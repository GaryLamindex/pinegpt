import pandas as pd
from datetime import *


#
class Indicator:

    def __init__(self, stock_data_engines, tickers, start_date):
        self.stock_data_engines = stock_data_engines
        self.evaluated_dict = {}  
        self.pct_change_dict = {}
        self.ticker_df = {}
        self.delta_timestamps = []
        self.tickers = tickers
        self.start_date = start_date

        for month in range(1, 7):
            delta = timedelta(weeks=(4 * month))
            date_before = start_date - delta
            date_before_timestamp = datetime.timestamp(date_before)
            self.delta_timestamps.append(date_before_timestamp)

        for ticker in self.tickers:
            for month in range(5, -1, -1):
                timestamp = self.delta_timestamps[month]
                ticker_item = self.stock_data_engines[ticker].get_ticker_item_by_timestamp(timestamp)
                while ticker_item is None:
                    timestamp = timestamp + 3600
                    ticker_item = self.stock_data_engines[ticker].get_ticker_item_by_timestamp(timestamp)

                self.append_into_ticker_df(ticker, ticker_item)

    def get_pct_change(self, option, periods, col_name, timestamp):
        pct_change_col_name = f'pct_change_{col_name}'
        self.ticker_df[option][pct_change_col_name] = self.ticker_df[option][col_name].pct_change(periods=periods)
        
        
        row_at_timestamp = self.ticker_df[option]['timestamp'] == timestamp
        pct_change_at_timestamp = self.ticker_df[option].loc[row_at_timestamp, pct_change_col_name]

        if pct_change_at_timestamp.shape[0] != 0:
            pct_change_value = pct_change_at_timestamp.item()
            return pct_change_value



    def append_into_ticker_df(self, option, option_item):

        temp = pd.DataFrame([option_item])

        if option not in self.ticker_df or self.ticker_df[option].empty:
            self.ticker_df[option] = temp
        else:
            self.ticker_df[option] = pd.concat([self.ticker_df[option], temp], ignore_index=True)




    def getPctChangeDict(self, options, timestamp):
        for option in options:
            if option not in self.pct_change_dict:
                self.pct_change_dict[option] = {}
            self.pct_change_dict[option].update({1: self.get_pct_change(option, 1, 'open', timestamp)})
            self.pct_change_dict[option].update({3: self.get_pct_change(option, 3, 'open', timestamp)})
            self.pct_change_dict[option].update({6: self.get_pct_change(option, 6, 'open', timestamp)})
        return self.pct_change_dict

