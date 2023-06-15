import os
import json
from datetime import datetime
from datetime import timedelta
import pandas as pd
from os import listdir
from pathlib import Path
from .algorithm import accelerating_dual_momentum
from .indicator import Indicator
from engine.backtest_engine.dividend_engine import dividend_engine
from engine.backtest_engine.portfolio_data_engine import backtest_portfolio_data_engine
from engine.backtest_engine.stock_data_io_engine import local_engine
from engine.backtest_engine.trade_engine import backtest_trade_engine
from engine.simulation_engine.simulation_agent import simulation_agent
from engine.stat_engine.statistic_engine import *
# from engine.mongoDB_engine.write_document_engine import Write_Mongodb
from engine.visualisation_engine.graph_plotting_engine import *
from object.action_data import IBAction
from object.backtest_acc_data import backtest_acc_data
import numpy as np
from application.realtime_statistic_application import realtime_statistic

class  backtest:
    table_dir = ""
    table_info = {}
    table_name = ""
    start_timestamp = 0
    end_timestamp = 0
    cal_stat = True
    data_freq = "one_min"
    db_mode = "local"
    tickers = []
    bond = ""
    initial_amount = 0
    stock_data_engines = {}
    store_mongoDB = False
    strategy_initial = 'None'
    video_link = 'None'
    documents_link = 'None'
    tags_array = list()
    subscribers_num = 0
    rating_dict = {}
    margin_ratio = np.NaN
    trader_name = "None"
    info_param = {}
    indicator_param = {}

    def __init__(self, basic_setting, fixed_param, var_param, info_param):

        # Basic info
        self.strategy_name = "accelerating_dual_momentum"
        
        # Basic settings
        self.table_dir = basic_setting.get('table_dir')
        self.user_id = basic_setting.get('user_id')
        self.table_name = basic_setting.get('table_name')
        self.cal_stat = basic_setting.get('cal_stat')
        self.data_freq = basic_setting.get('data_freq')
        self.db_mode = basic_setting.get('db_mode')
        self.restart = basic_setting.get('restart')
        self.quick_test = basic_setting.get('quick_test')

        # Fixed params
        self.initial_amount = fixed_param.get('initial_amount')
        self.start_date = fixed_param.get('start_date')
        self.end_date = fixed_param.get('end_date')
        self.start_timestamp = datetime.timestamp(self.start_date)
        self.end_timestamp = datetime.timestamp(self.end_date)

        self.info_param = info_param
        self.var_param = var_param

        self.tickers = var_param.get("tickers", [])
        self.bond = var_param.get("bond", [])
        self.options = self.tickers + self.bond
        print(f"tickers::{self.tickers}")
        print(f"bond::{self.bond}")
        print(f"options::{self.options}")

    #Call by whatever application after init all the basic settings, fixed params, and info_params
    def backtest_exec(self):
        # Load up stock_data_engines and get timestamp
        print('Fetch data')

        timestamps = []
        for option in self.options:
            # get current ticker data
            print(f"ticker:{option}")
            self.stock_data_engines[option] = local_engine(option, self.data_freq)
            
            # get timestamps from current ticker
            current_timestamps = self.stock_data_engines[option].get_data_by_range([self.start_timestamp, self.end_timestamp])['timestamp']

            # initialize timestamps if empty, otherwise intersect with current timestamps
            if len(timestamps) == 0:
                timestamps = current_timestamps
            else:
                timestamps = np.intersect1d(timestamps, current_timestamps)

        # Create acc_data, agents, and algorithm 
        print("Create acc_data, agents, and algorithm")
        print("self.var_param",self.var_param)
        
        self.acc_data = backtest_acc_data(self.table_dir,self.table_name)

        self.portfolio_data_engine = backtest_portfolio_data_engine(self.acc_data, self.options)
        self.sim_agent = simulation_agent(self.db_mode, self.portfolio_data_engine,self.tickers, self.table_dir, self.table_name, self.info_param)
        self.trade_agent = backtest_trade_engine(self.acc_data, self.stock_data_engines, self.portfolio_data_engine)
        self.dividend_agent = dividend_engine(self.tickers)
        self.algorithm = accelerating_dual_momentum(self.trade_agent, self.portfolio_data_engine, self.stock_data_engines, self.var_param)
        
        if len(self.tickers) != 2:
            print('This strategy only works for two tickers')
            exit(0)

        
        print('start backtest')
        self.portfolio_data_engine.deposit_cash(self.initial_amount, self.start_timestamp)
 
        # After collect timestamp from stock_data_engine, backtest by looping through timestamps 
        print('Backtest by looping through timestamps')
        for timestamp in timestamps:
            _date = datetime.utcfromtimestamp(int(timestamp)).strftime("%Y-%m-%d")
            _time = datetime.utcfromtimestamp(int(timestamp)).strftime("%H:%M:%S")
            print('#' * 20, _date, ":", _time, " " * 5, self.tickers, '#' * 20)
            # if self.dividend_agent.check_div(timestamp):
            #     portfolio = self.portfolio_data_engine.get_portfolio()
            #     total_dividend = self.dividend_agent.distribute_div(timestamp, portfolio)
            #     if total_dividend != 0:
            #         self.portfolio_data_engine.deposit_dividend(total_dividend, timestamp)

            if self.quick_test:
                if self.algorithm.check_exec(timestamp, freq="Daily", relative_delta=1):
                    self.run(timestamp)
            else:
                self.run(timestamp)

        print("Finished all timestamp loop...")
        self.realtime_stat_agent = realtime_statistic(self.table_name,self.sim_agent.run_file_dir, self.sim_agent.run_file_path, self.sim_agent.stats_data_dir)
        self.realtime_stat_agent.cal_stat_function()
        self.write_params_to_txt()

    #only take timestamp as input, use global varaibale for all the other agent and engines
    def run(self, timestamp):
        # Initializing metadata for the simulation and dictionary to hold stock data
        sim_meta_data = {}
        stock_data_dict = {}

        # Iterating over options to update stock and bond prices
        for option in self.options:
            # Fetching option data from the engine by timestamp
            option_engine = self.stock_data_engines[option]
            option_items = option_engine.get_ticker_item_by_timestamp(timestamp)

            # Updating simulation metadata with option items
            sim_meta_data.update({option: option_items})

            # Fetching price and updating the stock data dictionary
            price = option_items.get('open')
            if price is None:
                stock_data_dict.update({option: {'last': None}})
            else:
                stock_data_dict.update({option: {'last': price}})


        # Running the algorithm with the updated stock and bond data
        action_msgs = self.algorithm.run(stock_data_dict, self.bond, timestamp)
        action_record = []

        # If no action messages, append run data to the database and return
        if action_msgs is None:
            self.sim_agent.append_run_data_to_db(timestamp, self.sim_agent.portfolio_data_engine.get_account_snapshot(),
                                                action_record, sim_meta_data,
                                                stock_data_dict)
            return

        # Processing sell market order actions
        for action_msg in action_msgs:
            action = action_msg.action_enum
            if action == IBAction.SELL_MKT_ORDER:
                temp_action_record = self.trade_agent.place_sell_stock_mkt_order(action_msg.args_dict.get("ticker"),
                                                                                action_msg.args_dict.get("position_sell"),
                                                                                {"timestamp": action_msg.timestamp})
                action_record.append(temp_action_record)

        # Processing buy market order actions
        for action_msg in action_msgs:
            action = action_msg.action_enum
            if action == IBAction.BUY_MKT_ORDER:
                temp_action_record = self.trade_agent.place_buy_stock_mkt_order(action_msg.args_dict.get("ticker"),
                                                                            action_msg.args_dict.get("position_purchase"),
                                                                            {"timestamp": action_msg.timestamp})
                action_record.append(temp_action_record)

        # Appending run data to the database
        self.sim_agent.append_run_data_to_db(timestamp, self.sim_agent.portfolio_data_engine.get_account_snapshot(),
                                            action_record, sim_meta_data,
                                            stock_data_dict)

        # Writing account data and transaction record to a JSON file
        self.sim_agent.write_acc_data_json()
        self.sim_agent.write_transaction_record(action_record)




    def plot_all_file_graph(self):
        print("plot_graph")
        self.graph_plotting_engine.plot_all_file_graph_png(self.run_file_dir, "date", "NetLiquidation",self.graph_dir)
        
    def load_run_data(self, spec_str):
        run_file = self.run_file_dir + spec_str + '.csv'
        self.acc_data = backtest_acc_data(self.table_info.get("user_id"), self.table_info.get("strategy_name"),
                                          self.table_name, spec_str)
        self.portfolio_data_engine = backtest_portfolio_data_engine(self.acc_data, self.tickers)
        self.trade_agent = backtest_trade_engine(self.acc_data, self.stock_data_engines,
                                                 self.portfolio_data_engine)
        self.sim_agent = simulation_agent(self.backtest_spec, self.table_info, False, self.portfolio_data_engine,
                                          self.tickers)
        self.dividend_agent = dividend_engine(self.tickers)
        self.stat_agent = realtime_statistic_engine(self.run_file_dir, self.start_timestamp, self.end_timestamp,
                                                    self.path, self.table_name, self.store_mongoDB,
                                                    self.stats_data_dir, self.strategy_initial, self.video_link,
                                                    self.documents_link, self.tags_array, self.rating_dict,
                                                    self.margin_ratio, self.subscribers_num, self.trader_name)
        self.algorithm = accelerating_dual_momentum(self.trade_agent, self.portfolio_data_engine)
        df = pd.read_csv(run_file)
        row = df.iloc[-1]
        last_day = df["date"].iloc[-1]
        availablefunds = row.get("AvailableFunds")
        excessliquidity = row.get("ExcessLiquidity")
        buyingpower = row.get("BuyingPower")
        leverage = row.get("Leverage")
        equitywithloanvalue = row.get("EquityWithLoanValue")
        totalcashvalue = row.get("TotalCashValue")
        netdividend = row.get("NetDividend")
        netliquidation = row.get("NetLiquidation")
        unrealizedpnL = row.get("UnrealizedPnL")
        realizedpnL = row.get("RealizedPnL")
        grosspositionvalue = row.get("GrossPositionValue")

        self.acc_data.update_trading_funds(availablefunds, excessliquidity, buyingpower, leverage, equitywithloanvalue)
        self.acc_data.update_mkt_value(totalcashvalue, netdividend, netliquidation, unrealizedpnL, realizedpnL,
                                       grosspositionvalue)
        for ticker in self.tickers:
            mktprice = row.get(f"marketPrice_{ticker}")
            position = row.get(f"position_{ticker}")
            averagecost = row.get(f"averageCost_{ticker}")
            marketvalue = row.get(f"marketValue_{ticker}")
            ticker_realizedpnl = row.get(f"realizedPNL_{ticker}")
            ticker_unrealizedpnl = row.get(f"unrealizedPNL_{ticker}")
            initmarginreq = row.get(f"initMarginReq_{ticker}")
            maintmarginreq = row.get(f"maintMarginReq_{ticker}")
            costbasis = row.get(f"costBasis_{ticker}")
            self.acc_data.update_portfolio_item(ticker, position, mktprice, averagecost, marketvalue,
                                                ticker_realizedpnl, ticker_unrealizedpnl, initmarginreq, maintmarginreq,
                                                costbasis)
        self.portfolio_data_engine.acc_data = self.acc_data
        self.trade_agent.backtest_acc_data = self.acc_data


    def write_params_to_txt(self):
        
        def serializer(obj):
            if isinstance(obj, Path):
                return str(obj)
            if isinstance(obj, datetime):
                return obj.isoformat()
            raise TypeError(f"Type {type(obj)} not serializable")
        
        params = {
            "strategy_name": self.strategy_name,
            "user_id": self.user_id,
            "table_name": self.table_name,
            "cal_stat": self.cal_stat,
            "data_freq": self.data_freq,
            "db_mode": self.db_mode,
            "restart": self.restart,
            "quick_test": self.quick_test,
            "initial_amount": self.initial_amount,
            "start_date": str(self.start_date),
            "end_date": str(self.end_date),
            "start_timestamp": self.start_timestamp,
            "end_timestamp": self.end_timestamp,
            "info_param": self.info_param,
            "var_param": self.var_param,
            "tickers": self.tickers,
            "bond": self.bond
        }
        with open(f"{self.table_dir}/info_data.json", "w") as f:
            f.write(json.dumps(params, indent=4, default=serializer))  # Pass serializer to json.dumps