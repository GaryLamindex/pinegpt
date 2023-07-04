import os
import json
import pathlib
import glob
from datetime import datetime
from os import listdir
from pathlib import Path

import numpy as np
import pandas as pd

from algo.rebalance_margin_wif_max_drawdown_control.algorithm import rebalance_margin_wif_max_drawdown
from engine.backtest_engine.portfolio_data_engine import backtest_portfolio_data_engine
from engine.backtest_engine.stock_data_io_engine import local_engine
from engine.backtest_engine.trade_engine import backtest_trade_engine
from engine.simulation_engine import sim_data_io_engine
from engine.aws_engine.dynamo_db_engine import dynamo_db_engine
from engine.simulation_engine.simulation_agent import simulation_agent
from engine.stat_engine.statistic_engine import statistic_engine
from engine.mongoDB_engine.write_statistic_document_engine import Write_Mongodb
from object.backtest_acc_data import backtest_acc_data
from engine.backtest_engine.dividend_engine import dividend_engine
from object.action_data import IBAction
from application.realtime_statistic_application import realtime_statistic
from engine.visualisation_engine import graph_plotting_engine
import sys

def run():
    pass


class backtest(object):
    data_freq = ""
    table_dir = ""
    user_id = ""
    table_name = ""

    initial_amount = 0
    start_timestamp = None
    end_timestamp = None
    cal_stat = True
    wipe_previous_sim_data = False
    quick_test = False
    rabalance_dict = {}
    maintain_dict = {}
    max_drawdown_ratio_dict = {}
    purchase_exliq_ratio_dict = {}
    table_info = {}

    stock_data_engines = {}
    info_param = {}
    var_param = {}
    
    tickers = []
    bond = []
    options = []

    # maximum ONLY 2 tickers at a time !!!
    def __init__(self, basic_setting, fixed_param, var_param, info_param):

        # Basic info
        self.strategy_name = "rebalance_margin_wif_max_drawdown_control"

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


    def backtest_exec(self):
        
        print("Start backtest_exec: rebalance_margin_wif_max_drawdown_control")
        # Load up stock_data_engines and timestamps 


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

        
        print(f"backtest_exec:timestamps:{timestamps}")
        # Create acc_data, agents, and algorithm 
        print("Create acc_data, agents, and algorithm")

        
        self.acc_data = backtest_acc_data(self.table_dir,self.table_name)

        self.portfolio_data_engine = backtest_portfolio_data_engine(self.acc_data, self.options)
        self.sim_agent = simulation_agent(self.db_mode, self.portfolio_data_engine,self.tickers, self.table_dir, self.table_name, self.info_param)
        self.trade_agent = backtest_trade_engine(self.acc_data, self.stock_data_engines, self.portfolio_data_engine)
        self.dividend_agent = dividend_engine(self.tickers)
        

        #Initiate algorithm with var_param
        leverage = self.var_param.get("leverage")
        print(f"leverage:{leverage}")

        self.algorithm = rebalance_margin_wif_max_drawdown(self.trade_agent, self.portfolio_data_engine, self.tickers, leverage)

        self.portfolio_data_engine.deposit_cash(self.initial_amount, self.start_timestamp)

        for timestamp in timestamps:
            _date = datetime.utcfromtimestamp(int(timestamp)).strftime("%Y-%m-%d")
            _time = datetime.utcfromtimestamp(int(timestamp)).strftime("%H:%M:%S")
            print('#' * 20, _date, ":", _time, '#' * 20)

            if self.quick_test:
                if self.algorithm.check_exec(timestamp, freq="Daily", relative_delta=1):
                    self.run(timestamp)
            else:
                self.run(timestamp)

        print("Finished all timestamp loop...")
        self.realtime_stat_agent = realtime_statistic(self.table_name,self.sim_agent.run_file_dir, self.sim_agent.run_file_path, self.sim_agent.stats_data_dir)
        self.realtime_stat_agent.cal_stat_function()
        self.write_params_to_txt()
        # self.plot_all_file_graph()

        # if self.cal_stat == True:
        #     print("start backtest")
        #     self.cal_all_file_return()

    
    def run(self, timestamp):
        # Initialize dictionaries for stock data and simulation metadata
        stock_data_dict = {}
        sim_meta_data = {}

        # Fetching ticker data from the engine by timestamp
        for ticker in self.tickers:
            ticker_engine = self.stock_data_engines[ticker]
            ticker_items = ticker_engine.get_ticker_item_by_timestamp(timestamp)

            # If data exists, update stock data dictionary with open price
            if ticker_items is not None:
                ticker_open_price = ticker_items.get('open')
                stock_data_dict.update({ticker: {'last': ticker_open_price}})

            # Update simulation metadata with algorithm data
            sim_meta_data.update({ticker: {"max_stock_price": self.algorithm.max_stock_price[ticker],
                                        "benchmark_drawdown_price": self.algorithm.benchmark_drawdown_price[ticker],
                                        "liq_sold_qty_dict": self.algorithm.liq_sold_qty_dict[ticker],
                                        "reg_exec": self.algorithm.reg_exec[ticker]}})

        # Fetch original account snapshot
        orig_account_snapshot_dict = self.sim_agent.portfolio_data_engine.get_account_snapshot()
       
        # Running the algorithm with the updated stock data
        action_msgs = self.algorithm.run(stock_data_dict, timestamp)

        # Handling actions
        action_record = []
        if action_msgs is not None:
            for action_msg in action_msgs:
                action = action_msg.action_enum
                if action == IBAction.SELL_MKT_ORDER:
                    temp_action_record = self.trade_agent.place_sell_stock_mkt_order(action_msg.args_dict.get("ticker"),
                                                                                action_msg.args_dict.get("position_sell"),
                                                                                {"timestamp": action_msg.timestamp})
                    action_record.append(temp_action_record)
            for action_msg in action_msgs:
                action = action_msg.action_enum
                if action == IBAction.BUY_MKT_ORDER:
                    temp_action_record = self.trade_agent.place_buy_stock_mkt_order(action_msg.args_dict.get("ticker"),
                                                                            action_msg.args_dict.get("position_purchase"),
                                                                            {"timestamp": action_msg.timestamp})
                    action_record.append(temp_action_record)

        # Appending run data to the database
        self.sim_agent.append_run_data_to_db(timestamp, orig_account_snapshot_dict, action_record, sim_meta_data,
                                            stock_data_dict)

        # Writing account data and transaction record to a JSON file
        self.sim_agent.write_acc_data_json()
        self.sim_agent.write_transaction_record(action_record)

    def plot_all_file_graph(self):
        print("plot_graph")
        graph_plotting_engine.plot_all_file_graph_png(self.sim_agent.run_file_dir, "date", "NetLiquidation", self.sim_agent.graph_dir)

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

#     def cal_additional_data(self, file_name):
#         file_path = f"{self.sim_agent.run_file_dir}/{file_name}/.csv"
#         df = pd.read_csv(file_path, low_memory=False)
#         _exmk = df['ExcessLiquidity/ GrossPositionValue(Day End)'].min()
#         _additional_data = {"min(ExcessLiquidity/ GrossPositionValue(Day End))": _exmk}
#         return _additional_data



# # def main():
# #     run_dir = "C:\\Users\\user\\Documents\\GitHub\\user_id_0\\backtest\\backtest_rebalance_margin_wif_max_drawdown_control_0\\"
# #     graph_plotting_engine.plot_all_file_graph_png(f"{run_dir}\\run_data", "date", "NetLiquidation", f"{run_dir}/graph")

# #
# def main():
#     run_file_dir = "C:\\Users\\lam\\Documents\\GitHub\\test_graph_data"
#     sim_data_offline_engine = sim_data_io_engine.offline_engine(run_file_dir)
#     backtest_data_directory = os.fsencode(run_file_dir)
#     data_list = []
#     for file in os.listdir(backtest_data_directory):
#         if file.decode().endswith("csv"):
#             file_name = file.decode().split(".csv")[0]
#             stat_engine = statistic_engine(sim_data_offline_engine)
#             print("stat_engine")
#             sharpe_dict = stat_engine.get_sharpe_data(file_name)
#             print("sharpe_dict")
#             inception_sharpe = sharpe_dict.get("inception")
#             _1_yr_sharpe = sharpe_dict.get("1y")
#             _3_yr_sharpe = sharpe_dict.get("3y")
#             _5_yr_sharpe = sharpe_dict.get("5y")
#             _ytd_sharpe = sharpe_dict.get("ytd")

#             return_dict = stat_engine.get_return_data(file_name)
#             inception_return = return_dict.get("inception")
#             _1_yr_return = return_dict.get("1y")
#             _3_yr_return = return_dict.get("3y")
#             _5_yr_return = return_dict.get("5y")
#             _ytd_return = return_dict.get("ytd")

#             all_file_stats_row = {
#                 "Backtest Spec": file_name, 'YTD Return': _ytd_return, '1 Yr Return': _1_yr_return,
#                 "3 Yr Return": _3_yr_return, "5 Yr Return": _5_yr_return,
#                 "Since Inception Return": inception_return, "Since Inception Sharpe": inception_sharpe,
#                 "YTD Sharpe": _ytd_sharpe,
#                 "1 Yr Sharpe": _1_yr_sharpe, "3 Yr Sharpe": _3_yr_sharpe, "5 Yr Sharpe": _5_yr_sharpe
#             }
#             # _additional_data = self.cal_additional_data(file_name)
#             _additional_data = {}
#             data_list.append(all_file_stats_row | _additional_data)

#     col = ['Backtest Spec', 'YTD Return', '1 Yr Return', "3 Yr Return", "5 Yr Return",
#            "Since Inception Return", "Since Inception Sharpe", "YTD Sharpe", "1 Yr Sharpe", "3 Yr Sharpe",
#            "5 Yr Sharpe", "min(exliq/mkt value)"]
#     df = pd.DataFrame(data_list, columns=col)
#     df.fillna(0)
#     df.to_csv(f"{run_file_dir}/test.csv")
#     # print(f"{self.path}/stats_data/{self.table_name}.csv")
#     # df.to_csv(f"{self.path}/stats_data/{self.table_name}.csv")
#     pass


# if __name__ == "__main__":
#     main()
