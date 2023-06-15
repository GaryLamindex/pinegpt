import json
from datetime import datetime

import sys
import pathlib

import numpy as np
import pandas as pd

sys.path.append(str(pathlib.Path(__file__).parent.parent.parent.parent.resolve()))
import os
import csv
import datetime as dt

from engine.realtime_engine_ibkr.portfolio_data_engine import *
from engine.simulation_engine.sim_data_io_engine import *
from pathlib import Path
from object.backtest_acc_data import backtest_acc_data

from object.action_data import IBAction, IBActionsTuple, IBActionMessage, IBActionState

class simulation_agent(object):
    spec = {}
    spec_str = ""
    run_file_path = ""
    run_file_path_temp = ""
    graph_file_path = ""
    tickers = []
    table_name = ""
    table_dir = ""

    sim_data_engine = None
    portfolio_data_engine = None
    acc_data = None
    list_header = []
    header_update = False

    # example
    # spec:{"rebalance_margin":rebalance_margin,"maintain_margin":maintain_margin,"max_drawdown_ratio":max_drawdown_ratio,"purchase_exliq":purchase_exliq}
    # table_info:{"mode":"backtest","strategy_name":"rebalance_margin_wif_max_drawdown_control","user_id":0}
    # ??? portfolio agent: should be an initialized instance which is connect to TWS with an initialized ibkr acc object
    def __init__(self, db_mode, portfolio_data_engine, tickers, table_dir, table_name, info_param):
        
        self.table_name = table_name
        self.list_header = []

        if db_mode.get("local"):
            self.sim_data_engine = offline_engine(table_dir)
            self.table_dir = table_dir
            
        else:
            self.sim_data_engine = online_engine()

        self.portfolio_data_engine = portfolio_data_engine
        self.acc_data = portfolio_data_engine.acc_data
        self.tickers = tickers

        if db_mode.get("local"):
            
            self.run_file_dir = f"{self.table_dir}/run_data/"
            self.stats_data_dir = f"{self.table_dir}/stats_data/"
            self.acc_data_dir = f"{self.table_dir}/acc_data/"
            self.transact_data_dir = f"{self.table_dir}/transaction_data/"
            self.graph_dir = f"{self.table_dir}/graph"

            self.run_file_path = os.path.join(str(self.run_file_dir), self.table_name + '.csv')
            self.run_file_path_temp = self.run_file_path.replace(".csv", "temp.csv")
            self.graph_file_path = str(self.graph_dir) + self.table_name + '.png'

            if os.path.exists(self.run_file_path):
                df = pd.read_csv(self.run_file_path)
                first_day = df["date"].iloc[0]
                last_day = df["date"].iloc[-1]
                if abs((self.start_date - datetime.strptime(first_day, "%Y-%m-%d")).days) > 10 or \
                        abs((self.end_date - datetime.strptime(last_day, "%Y-%m-%d")).days) > 10:
                    os.remove(Path(self.run_file_path))
                else:
                    if os.path.exists(self.graph_file_path):
                        os.remove(Path(self.graph_file_path))
                    # self.load_run_data(spec_str)
                    return
            if os.path.exists(self.graph_file_path):
                os.remove(Path(self.graph_file_path))

            if not os.path.exists(self.run_file_dir):
                Path(self.run_file_dir).mkdir(parents=True, exist_ok=True)
            if not os.path.exists(self.stats_data_dir):
                Path(self.stats_data_dir).mkdir(parents=True, exist_ok=True)
            if not os.path.exists(self.acc_data_dir):
                Path(self.acc_data_dir).mkdir(parents=True, exist_ok=True)
            if not os.path.exists(self.transact_data_dir):
                Path(self.transact_data_dir).mkdir(parents=True, exist_ok=True)
            if not os.path.exists(self.graph_dir):
                Path(self.graph_dir).mkdir(parents=True, exist_ok=True)


            self.strategy_initial = info_param.get('strategy_initial', 'None')
            self.video_link = info_param.get('video_link', 'None')
            self.documents_link = info_param.get('documents_link', 'None')
            self.tags_array = info_param.get('tags_array', list())
            self.subscribers_num = info_param.get('subscribers_num', 0)
            self.rating_dict = info_param.get('rating_dict', {})
            self.margin_ratio = info_param.get('margin_ratio', np.NaN)
            self.trader_name = info_param.get('trader_name', "None")

        # # initialize the attribute (column name) of the csv file
        # self.data_attribute = ['date', 'time' ,'timestamp','TotalCashValue','NetDividend','NetLiquidation','UnrealizedPnL','RealizedPnL','GrossPositionValue','AvailableFunds','ExcessLiquidity','BuyingPower','Leverage','EquityWithLoanValue']
        # for ticker in tickers:
        #     # overall position
        #     self.data_attribute += [f'{ticker} state',f'{ticker} position',f'{ticker} marketPrice',f'{ticker} averageCost',f'{ticker} marketValue',f'{ticker} realizedPNL',f'{ticker} unrealizedPNL',f'{ticker} initMarginReq',f'{ticker} maintMarginReq',f'{ticker} costBasis']
        # for ticker in tickers:
        #     # instance action
        #     self.data_attribute += [f'{ticker} action',f'{ticker} totalQuantity',f'{ticker} avgPrice',f'{ticker} commission', f'{ticker} transaction_amount']

    # no clear usage
    def get_net_action_dicts(self, action_msgs):
       # print("action_msgs:", action_msgs)
        net_action_dicts = []
        for action_msg in action_msgs:
            action_ticker = action_msg.get('ticker')
            # if ticker not exist in net action
            if (net_action_dicts == None):
                action_type = action_msg.get('action')
                if (action_type == "BUY"):
                    action_ticker = action_msg.get('ticker')
                    action_amount = action_msg.get('avgPrice') * action_msg.get('totalQuantity')
                    net_action_dicts.append(
                        {action_ticker + ' action': action_type, action_ticker + " action amount": action_amount})

                elif (action_type == "SELL"):
                    action_ticker = action_msg.get('ticker')
                    action_amount = action_msg.get('transaction_amount')
                    net_action_dicts.append(
                        {action_ticker + ' action': action_type, action_ticker + " action amount": action_amount})

            elif any(action_ticker + ' action' in action_dict for action_dict in net_action_dicts):
                action_type = action_msg.get('action')
               # print("action_type:", action_type)
               # print("action_msg:", action_msg)
                action_amount = action_msg.get('transaction_amount')
                if action_type == "SELL":
                    action_amount = action_amount * -1
                    #print("action_amount:", action_amount)
                previous_action_type = [action_dict[action_ticker + ' action'] for action_dict in net_action_dicts if
                                        action_ticker + ' action' in action_dict][0]
                previous_action_amount = \
                [action_dict[action_ticker + " action amount"] for action_dict in net_action_dicts if
                 action_ticker + ' action amount' in action_dict][0]
                if previous_action_type == 'SELL':
                    previous_action_amount = previous_action_amount * -1
                    #print("previous_action_amount:", previous_action_amount)
                net_action_amount = action_amount + previous_action_amount
                if net_action_amount > 0:
                    net_action_dict = {action_ticker + ' action': "buy",
                                       action_ticker + " action amount": net_action_amount}
                else:
                    net_action_dict = {action_ticker + ' action': "sell",
                                       action_ticker + " action amount": net_action_amount * -1}

                net_action_dicts = [net_action_dict for net_action_dict in net_action_dicts if
                                    not action_ticker + ' action' in net_action_dict.keys()]
                net_action_dicts.append(net_action_dict)

            # if ticker already exist in net action, calculate the net action (buy+sell)
            else:
                action_type = action_msg.get('action')
                if (action_type == "buy"):
                    action_ticker = action_msg.get('ticker')
                    action_amount = action_msg.get('transaction_amount')
                    net_action_dicts.append(
                        {action_ticker + ' action': action_type, action_ticker + " action amount": action_amount})

                elif (action_type == "sell"):
                    action_ticker = action_msg.get('ticker')
                    action_amount = action_msg.get('transaction_amount')
                    net_action_dicts.append(
                        {action_ticker + ' action': action_type, action_ticker + " action amount": action_amount})

            #print("net_action_dicts:", net_action_dicts)

        return net_action_dicts


    def append_run_data_to_db(self, timestamp, orig_account_snapshot_dict, action_msgs, sim_meta_data, ticker_data):
        
        _date = datetime.utcfromtimestamp(int(timestamp)).strftime("%Y-%m-%d")
        _time = datetime.utcfromtimestamp(int(timestamp)).strftime("%H:%M:%S")
        timestamp_dict = {"timestamp": timestamp, "date": _date, "time": _time}
        if os.path.exists(self.run_file_path):
            with open(self.run_file_path, 'r', newline='') as f:
                reader = csv.reader(f)
                for row in reader:
                    # adding the first row
                    self.list_header = row
                    # breaking the loop after the
                    # first iteration itself
                    break


        # store the header information to self.list_header field
        # using a for-loop function like the below example
        # timestamp, date and time first
        for key in timestamp_dict.keys():
            if key not in self.list_header:
                self.list_header.append(key)
                self.header_update = True

        action_dicts = {}
        sim_data_res = {}
        ticker_data_res = {}

        # Handle case where action_msgs is None
        if action_msgs is None:
            action_msgs = []

        for action_msg in action_msgs:
            action_msg_dict = action_msg.__getdict__()
            print(f"action_msg_dict:{action_msg_dict}")
            if not action_msg_dict['action'] == 'rejected': #accpeted the then do
                #print("temp_list:", temp_list)
                action_ticker = action_msg_dict["ticker"]
                try:
                    del action_msg_dict['ticker']  # get rid of the "ticker" column, since the csv does NOT contain this attribute
                    del action_msg_dict['orderId']
                    del action_msg_dict['lmtPrice']
                    del action_msg_dict['exchange']
                    del action_msg_dict['timestamp']
                except KeyError:
                    pass

                # Mark, change the code here as you like, so that giving a better representations in tickers snapshots
                #The action_msg has a null val so the output has 4 collumns of (key)_null BUG
                action_res = {f"{str(key)}_{action_ticker}": val for key, val in action_msg_dict.items()}
                action_dicts.update(action_res)  # action_dicts|action_res

                # then action_dicts
                for key in action_res.keys():
                    if key not in self.list_header:
                        self.list_header.append(key)
                        self.header_update = True

        # print(action_dicts)

        try:
            del ticker_data['timestamp']
        except KeyError:
            pass
        sim_data_res = {}
        #Mark, change the code here as you like, so that giving a better representations in tickers snapshots
        for ticker in self.tickers:
            temp_key = ""
            if len(sim_meta_data) > 0 and ticker in sim_meta_data:
                for key, val in sim_meta_data[ticker].items():
                    sim_data_res.update({f"{str(key)}_{ticker} ": val })
                    temp_key = f"{str(key)}_{ticker} "
                    
            if temp_key not in self.list_header:
                self.list_header.append(temp_key)
                self.header_update = True

            ticker_data_res.update({f"mktPrice_{ticker} ": ticker_data[ticker]['last']})

            if f"mktPrice_{ticker} " not in self.list_header:
                self.list_header.append(f"mktPrice_{ticker} ")
                self.header_update = True

        for key in orig_account_snapshot_dict.keys():
            if key not in self.list_header:
                self.list_header.append(key)
                self.header_update = True

        run_dict = timestamp_dict | orig_account_snapshot_dict | ticker_data_res | sim_data_res | action_dicts
        self.data_attribute = run_dict.keys()

        if not os.path.exists(self.run_file_path):
            print("File doesn't exist, creating a new one...")  # printing when the file doesn't exist and a new one is created
            print(f"Header: {self.list_header}")  # Debug line
            print(f"Data: {run_dict}")  # Debug line
            
            with open(self.run_file_path, 'w+', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(self.list_header)
                temp_row = []
                for item in self.list_header:
                    temp_row.append(run_dict.get(item, None))
                writer.writerow(temp_row)
                print("write header")
        
        else:
            print("File exists...")  # printing when the file already exists
            if self.header_update:
                #if exist then copy first
                print("Header needs to be updated...")  # printing when the header needs to be updated
                with open(self.run_file_path, 'r') as f_input,\
                        open(self.run_file_path_temp, 'w+', newline='') as f_output:
                    writer = csv.writer(f_output)
                    writer.writerow(self.list_header)
                    print("updated write header")
                    next(f_input)
                    #try
                    input_csv = csv.reader(f_input)
                    for row in input_csv:
                        writer.writerow(row)

                    #then write data we need
                    temp_row = []
                    for item in self.list_header:
                        temp_row.append(run_dict.get(item, None))
                    writer.writerow(temp_row)

                self.header_update = False
                os.remove(self.run_file_path)
                os.rename(self.run_file_path_temp, self.run_file_path)

            else:
                print("Appending to existing file...")  # printing when appending to an existing file
                with open(self.run_file_path, 'a+', newline='') as f:
                    writer = csv.writer(f)
                    temp_row = []
                    for item in self.list_header:
                        temp_row.append(run_dict.get(item, None))
                    print(f"Writing row: {temp_row}")  # print the row being written
                    writer.writerow(temp_row)


        # thoughts:
        # generate a file, leave the first line for header which place after running all the code
        # first get the header list
        # if header in header list:
        #   iterate through the data which get the value corresponding to the header if it exists
        #   else leave a blank space" "
        # else:
        #   add a new header to the header list
        # place header list to the first row

    
    def write_transaction_record(self, action_records):

        if not all(isinstance(record, IBActionMessage) for record in action_records):
            raise TypeError("All action records must be instances of IBActionMessage.")


        transaction_field_name = ["state", "timestamp", "orderId", "ticker", "action", "lmtPrice", "totalQuantity",
                                  "avgPrice", "exchange", "commission"]

        # Ensure the directory exists
        os.makedirs(os.path.join(self.transact_data_dir, self.table_name), exist_ok=True)
        
        for action_record in action_records:

            action_record_dict = action_record.to_dict()

            if f"{self.table_name}.csv" not in os.listdir(self.transact_data_dir):
                with open(os.path.join(self.transact_data_dir, f'{self.table_name}.csv'), 'a+', newline='') as f:
                    writer = csv.DictWriter(f, transaction_field_name)
                    writer.writeheader()
                    writer.writerow(action_record_dict)
            else:
                with open(os.path.join(self.transact_data_dir, f'{self.table_name}.csv'), 'a+', newline='') as f:
                    writer = csv.DictWriter(f, transaction_field_name)
                    writer.writerow(action_record_dict)
    
    # def write_acc_data(self):
    #     data_dict = self.acc_data.return_acc_data()
    #     acc_field_name = list(data_dict.keys())
    #     if f"{self.table_name}.csv" not in os.listdir(f"{self.table_path}/acc_data/"):
    #         with open(self.acc_data_file_path, 'a+', newline='') as f:
    #             writer = csv.DictWriter(f, acc_field_name)
    #             writer.writeheader()
    #             writer.writerow(data_dict)
    #     else:
    #         with open(self.acc_data_file_path, 'a+', newline='') as f:
    #             print(f"Writing acc data in {self.acc_data_file_path}")
    #             writer = csv.DictWriter(f, acc_field_name)
    #             writer.writerow(data_dict)
    #     pass



    def write_acc_data_json(self):
        class CustomJSONEncoder(json.JSONEncoder):
            def default(self, obj):
                if isinstance(obj, np.int64):
                    return int(obj)
                return json.JSONEncoder.default(self, obj)
        
        data_dict = self.acc_data.return_acc_data()
        print("data_dict:",data_dict)
        self.acc_data_file_path_json = os.path.join(self.acc_data_dir, f"{self.table_name}.json")

        with open(self.acc_data_file_path_json, 'w') as f:
            json.dump(data_dict, f, cls=CustomJSONEncoder)

def main():
    pass


if __name__ == "__main__":
    main()
