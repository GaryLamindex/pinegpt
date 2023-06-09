import time

import numpy as np
import pandas as pd
from datetime import datetime
from algo.accelerating_dual_momentum.backtest import backtest as accelerating_dual_momentum_backtest
from algo.accelerating_dual_momentum.indicator import Indicator
from object.action_data import IBAction, IBActionsTuple
from engine.backtest_engine.stock_data_io_engine import local_engine
from engine.visualisation_engine import graph_plotting_engine
import os
import pathlib
from pathlib import Path
from engine.mongoDB_engine.write_run_data_document_engine import Write_Mongodb
from application.realtime_statistic_application import realtime_statistic
from engine.simulation_engine.simulation_agent import simulation_agent

class realtime:
    def __init__(self, tickers, bond, initial_amount, margin_ratio, start_date, cal_stat, data_freq, user_id,
                 db_mode, execute_period, table_id, table_name, table_dir, mode):
        self.tickers_and_bonds_list = None
        self.stat_agent = None
        self.margin_ratio = margin_ratio
        self.rebalance_dict = None
        self.trader_name = None
        self.rating_dict = None
        self.subscribers_num = None
        self.tags_array = None
        self.documents_link = None
        self.video_link = None
        self.strategy_initial = None
        self.store_mongoDB = None
        self.stock_data_engines = {}
        self.algorithm = None
        self.dividend_agent = None
        self.sim_agent = None
        self.trade_agent = None
        self.portfolio_data_engine = None
        self.acc_data = None
        self.bond = bond
        self.indicators = {}
        self.table_dir = table_dir
        self.table_id = table_id
        self.table_info = {"mode": mode, "strategy_name": "accelerating_dual_momentum", "user_id": user_id}
        self.table_name = table_name
        self.user_id = user_id
        self.tickers = tickers
        self.bond = bond
        self.initial_amount = initial_amount
        self.start_timestamp = datetime.timestamp(start_date)
        self.cal_stat = cal_stat
        self.data_freq = data_freq
        self.db_mode = db_mode
        self.start_date = start_date
        self.backtest = None
        self.now = datetime.now()
        self.execute_period = execute_period
        self.init_backtest_flag = False
        self.ongoing = False
        
        if mode == "ongoing":
            self.ongoing = True

        if db_mode.get("local"):
            self.sim_agent = simulation_agent(False, self.portfolio_data_engine,self.tickers, self.table_dir, self.table_name)


    def init_backtest(self, user_id, store_mongoDB, strategy_initial, video_link,
                      documents_link, tags_array, subscribers_num,
                      rating_dict, margin_ratio, trader_name):
        self.now = datetime.now()
        params = None
        if store_mongoDB:
            params = {
                "strategy_initial": strategy_initial,
                "video_link": video_link,
                "documents_link": documents_link,
                "tags_array": tags_array,
                "subscribers_num": subscribers_num,
                "rating_dict": rating_dict,
                "margin_ratio": margin_ratio,
                "trader_name": trader_name,
                # add other parameters as needed
            }


        self.backtest = accelerating_dual_momentum_backtest(self.tickers, self.bond, self.initial_amount,
                                                            self.start_date, self.now, True, self.data_freq,
                                                            user_id, self.db_mode, store_mongoDB,params,
                                                            self.table_name, self.table_dir )
        self.backtest.loop_through_param()
        

    def cal_stat_function(self):
        df = pd.read_csv(self.run_file_dir)
        last_day = df["date"].iloc[-1]
        last_day_object = datetime.strptime(last_day, '%Y-%m-%d')
        end_timestamp = datetime.timestamp(last_day_object)
        self.realtime_stat_engine.update_timestamp(end_timestamp)
        self.realtime_stat_engine.cal_file_return(f"{self.sim_agent.stats_data_dir}/{self.table_name}.csv")    

    def realtime_exec(self):
        if not self.init_backtest_flag:
            self.init_backtest(self.user_id,
                               store_mongoDB=False,
                               strategy_initial='SPY_MSFT_TIP_accelerating_dual_momentum',
                               video_link='https://www.youtube.com',
                               documents_link='https://google.com',
                               tags_array=None,
                               subscribers_num=3,
                               rating_dict=None,
                               margin_ratio=None,
                               trader_name='Fai'
                               )

            self.init_backtest_flag = True
        else:
            self.acc_data = self.backtest.acc_data
            self.portfolio_data_engine = self.backtest.portfolio_data_engine
            self.trade_agent = self.backtest.trade_agent
            self.sim_agent = self.backtest.sim_agent
            self.dividend_agent = self.backtest.dividend_agent
            self.algorithm = self.backtest.algorithm
            self.tickers_and_bonds_list = self.tickers.copy()
            self.tickers_and_bonds_list.append(self.bond)
            df = pd.read_csv(self.backtest.run_file)
            last_date_str = df["date"].iloc[-1]
            last_date = datetime.strptime(last_date_str, '%Y-%m-%d')
            delta_timestamps = self.backtest.cal_deltas_timestamps(last_date)
            for ticker in self.tickers:
                # get current ticker data
                self.stock_data_engines[ticker] = local_engine(ticker, self.data_freq)
                self.indicators[ticker] = Indicator(pd.DataFrame())
                self.backtest.get_indicator_ticker_items(ticker, delta_timestamps)
            self.stock_data_engines[self.bond] = local_engine(self.bond, self.data_freq)  # update bond price
            last_excute_timestamp = df["timestamp"].iloc[-1]
            last_excute_timestamp = int(last_excute_timestamp)
            last_excute_timestamp = last_excute_timestamp + 1
            current_date = datetime.now()
            current_timestamp = datetime.timestamp(current_date)
            _date = datetime.utcfromtimestamp(int(current_timestamp)).strftime("%Y-%m-%d")
            _time = datetime.utcfromtimestamp(int(current_timestamp)).strftime("%H:%M:%S")
            print('#' * 20, _date, ":", _time, " " * 5, self.tickers, '#' * 20)
            if self.stock_data_engines[self.tickers[0]].get_data_by_range(
                    [last_excute_timestamp, current_timestamp]) is None:
                print("No new data")
            else:
                print("Have new data")
                timestamps = \
                    self.stock_data_engines[self.tickers[0]].get_data_by_range(
                        [last_excute_timestamp, current_timestamp])[
                        'timestamp']
                for x in range(1, len(self.tickers)):
                    temp = self.stock_data_engines[self.tickers[x]].get_data_by_range(
                        [last_excute_timestamp, current_timestamp])['timestamp']
                    timestamps = np.intersect1d(timestamps, temp)
                for timestamp in timestamps:
                    self.run(timestamp)
                self.backtest.end_date = current_date
                # self.plot_all_file_graph()
        self.realtime_stat_agent = realtime_statistic(self.table_name,f"{self.run_file_dir}", f"{self.run_file_dir}/{self.table_name}.csv", self.stats_data_dir )
        self.realtime_stat_agent.cal_stat_function()

    def run(self, timestamp):  # run realtime
        _date = datetime.utcfromtimestamp(int(timestamp)).strftime("%Y-%m-%d")
        _time = datetime.utcfromtimestamp(int(timestamp)).strftime("%H:%M:%S")
        print('#' * 20, _date, ":", _time, " " * 5, self.tickers, '#' * 20)
        if self.dividend_agent.check_div(timestamp):
            portfolio = self.portfolio_data_engine.get_portfolio()
            total_dividend = self.dividend_agent.distribute_div(timestamp, portfolio)
            if total_dividend != 0:
                self.portfolio_data_engine.deposit_dividend(total_dividend, timestamp)

        stock_data_dict = {}
        sim_meta_data = {}
        pct_change_dict = {}
        for ticker in self.tickers:
            pct_change_dict.update({ticker: {}})
        for ticker in self.tickers:
            ticker_data = self.stock_data_engines[ticker].get_ticker_item_by_timestamp(timestamp)
            if ticker_data is not None:
                ticker_engine = self.stock_data_engines[ticker]
                ticker_items = ticker_engine.get_ticker_item_by_timestamp(timestamp)
                self.indicators[ticker].append_into_df(ticker_items)
                pct_change_dict[ticker].update({1: self.indicators[ticker].get_pct_change(1, 'open', timestamp)})
                pct_change_dict[ticker].update({3: self.indicators[ticker].get_pct_change(3, 'open', timestamp)})
                pct_change_dict[ticker].update({6: self.indicators[ticker].get_pct_change(6, 'open', timestamp)})
                sim_meta_data.update({ticker: ticker_data})
                price = ticker_items.get('open')
                if price is None:
                    stock_data_dict.update({ticker: {'last': None}})
                    continue
                else:
                    stock_data_dict.update({ticker: {'last': price}})

        bond_engine = self.stock_data_engines[self.bond]  # update bond price
        ticker_items = bond_engine.get_ticker_item_by_timestamp(timestamp)
        sim_meta_data.update({self.bond: bond_engine.get_ticker_item_by_timestamp(timestamp)})
        price = ticker_items.get('open')
        if price is None:
            stock_data_dict.update({self.bond: {'last': None}})
        else:
            stock_data_dict.update({self.bond: {'last': price}})

        action_msgs = self.algorithm.run(pct_change_dict, stock_data_dict, self.bond, timestamp)
        action_record = []
        if action_msgs is None:
            self.sim_agent.append_run_data_to_db(timestamp, self.sim_agent.portfolio_data_engine.get_account_snapshot(),
                                                 action_record, sim_meta_data,
                                                 stock_data_dict)
            if self.store_mongoDB:
                p = Write_Mongodb()
                for file in os.listdir(self.backtest_data_directory):
                    if file.decode().endswith("csv"):
                        csv_path = Path(self.run_file_dir, file.decode())
                        a = pd.read_csv(csv_path)
                        spec = file.decode().split('.csv')
                        p.write_new_backtest_result(strategy_name=self.table_name + '_' + spec[0],
                                                    run_df=a)
            return
        for action_msg in action_msgs:
            action = action_msg.action_enum
            if action == IBAction.SELL_MKT_ORDER:
                temp_action_record = self.trade_agent.place_sell_stock_mkt_order(action_msg.args_dict.get("ticker"),
                                                                                 action_msg.args_dict.get(
                                                                                     "position_sell"),
                                                                                 {"timestamp": action_msg.timestamp})
                action_record.append(temp_action_record)
        for action_msg in action_msgs:
            action = action_msg.action_enum
            if action == IBAction.BUY_MKT_ORDER:
                temp_action_record = self.trade_agent.place_buy_stock_mkt_order(action_msg.args_dict.get("ticker"),
                                                                                action_msg.args_dict.get(
                                                                                    "position_purchase"),
                                                                                {"timestamp": action_msg.timestamp})
                action_record.append(temp_action_record)
        self.sim_agent.append_run_data_to_db(timestamp, self.sim_agent.portfolio_data_engine.get_account_snapshot(),
                                             action_record, sim_meta_data,
                                             stock_data_dict)
        if self.store_mongoDB:
            p = Write_Mongodb()
            for file in os.listdir(self.backtest_data_directory):
                if file.decode().endswith("csv"):
                    csv_path = Path(self.run_file_dir, file.decode())
                    a = pd.read_csv(csv_path)
                    spec = file.decode().split('.csv')
                    p.write_new_backtest_result(strategy_name=self.table_name + '_' + spec[0],
                                                run_df=a)

    def plot_all_file_graph(self):
        print("plot_graph")
        graph_plotting_engine.plot_all_file_graph_png(f"{self.backtest.run_file_dir}", "date", "NetLiquidation",
                                                      f"{self.backtest.tabledir}/graph")


def main():
    tickers = ["SPY", "MSFT"]
    initial_amount = 10000
    start_date = datetime(2020, 1, 1)  # YYMMDD
    data_freq = "one_day"
    user_id = 0
    cal_stat = True
    db_mode = {"dynamo_db": False, "local": True}
    bond = "TIP"
    execute_period = "Monthly"

    realtime_backtest = realtime(tickers, bond, initial_amount, start_date, cal_stat,
                                 data_freq, user_id, db_mode, execute_period)
    while True:
        realtime_backtest.run()
        time.sleep(60)


if __name__ == "__main__":
    main()
