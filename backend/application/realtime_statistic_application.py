import pathlib
from datetime import datetime

import pandas as pd

from engine.stat_engine.statistic_engine import realtime_statistic_engine


class realtime_statistic:
    def __init__(self, table_name, run_file_dir, run_file_csv_dir, stats_data_dir):
        store_mongoDB = False,
        strategy_initial = '',
        video_link = 'https://www.youtube.com',
        documents_link = 'https://google.com',
        tags_array = None,
        subscribers_num = 3,
        rating_dict = None,
        trader_name = 'Fai'
        self.run_file_csv_dir = run_file_csv_dir
        df = pd.read_csv(self.run_file_csv_dir)
        last_day = df["date"].iloc[-1]
        last_day_object = datetime.strptime(last_day, '%Y-%m-%d')
        end_timestamp = datetime.timestamp(last_day_object)
        first_day = df["date"].iloc[0]
        first_day_object = datetime.strptime(first_day, '%Y-%m-%d')
        start_timestamp = datetime.timestamp(first_day_object)
        self.realtime_stat_engine = realtime_statistic_engine(table_name, run_file_dir, stats_data_dir,start_timestamp, end_timestamp,
                                                              store_mongoDB, strategy_initial, video_link, documents_link, tags_array,
                                                              rating_dict, subscribers_num, trader_name)

    def cal_stat_function(self):
        print("realtime_statistic:cal_stat_function")
        df = pd.read_csv(self.run_file_csv_dir)
        last_day = df["date"].iloc[-1]
        last_day_object = datetime.strptime(last_day, '%Y-%m-%d')
        end_timestamp = datetime.timestamp(last_day_object)
        self.realtime_stat_engine.update_timestamp(end_timestamp)
        self.realtime_stat_engine.cal_file_return()


if __name__ == "__main__":
    realtime_stat = realtime_statistic(0, "50_SPY_50_MSFT_")
    realtime_stat.cal_stat_function()
