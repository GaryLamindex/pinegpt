"""
class hierarchy suggestion:
abstract base class "algorithm"
And then for any other specify algorithms (e.g., rebalance margin with max drawdown), inhereits the algorithm class and build addtional features
Now put everything together for simplicity, but better separate the base class and the child class
"""
import math
import sys
import pathlib
from datetime import datetime

from dateutil.relativedelta import relativedelta
from engine.realtime_engine_ibkr.portfolio_data_engine import ibkr_portfolio_data_engine
from engine.realtime_engine_ibkr.stock_data_engine import ibkr_stock_data_io_engine
from engine.realtime_engine_ibkr.trade_engine import ibkr_trade_agent
from object.ibkr_acc_data import ibkr_acc_data

sys.path.append(str(pathlib.Path(__file__).parent.parent.parent.parent.resolve()))

from object.ibkr_acc_data import *
from engine.realtime_engine_ibkr.portfolio_data_engine import *
from engine.realtime_engine_ibkr.trade_engine import *
from engine.realtime_engine_ibkr.stock_data_engine import *

from ib_insync import *
from time import sleep
from object.action_data import IBAction, IBActionsTuple

class rebalance_margin_wif_max_drawdown:
    trade_agent = None
    portfolio_agent = None
    reg_exec = {}

    tickers = []
    number_of_stocks = 0

    max_drawdown_ratio = 0
    purchase_exliq = 0

    max_drawdown_dodge = {}  # a dictionary of boolean value, checking for each ticker

    max_stock_price = {}
    benchmark_drawdown_price = {}

    rebalance_margin = 0

    # however, different stock may have different maintenance margin, just don't consider it here
    maintain_margin = 0.01

    last_exec_price = {}
    liq_sold_qty_dict = {}
    liq_sold_price_dict = {}
    liquidate_sold_value = {}
    account_snapshot = {}
    action_msgs = []

    last_exec_datetime_obj = None
    last_max_drawdown_control_operation_datetime_obj = None
    loop = 0

    def __init__(self, trade_agent, portfolio_agent, tickers, max_drawdown_ratio, acceptance_range, rebalance_margin):

        self.trade_agent = trade_agent
        self.portfolio_agent = portfolio_agent
        self.tickers = tickers
        self.number_of_stocks = len(tickers)
        self.max_drawdown_ratio = max_drawdown_ratio

        self.acceptance_range = acceptance_range
        self.rebalance_margin = rebalance_margin
        self.maintain_margin = rebalance_margin

        for ticker in self.tickers:
            self.max_stock_price.update({ticker: 0})
            self.benchmark_drawdown_price.update({ticker: 0})
            self.max_drawdown_dodge.update({ticker: False})
            self.reg_exec.update({ticker: False})
            self.liq_sold_qty_dict.update({ticker: 0})
            self.liq_sold_price_dict.update({ticker: 0})

    # directly called to run the algorithm once
    def run(self, realtime_stock_data_dict, timestamp):
        # check if the market is opened, if not then do nothing and exit
        self.action_msgs = []
        datetime_obj = datetime.utcfromtimestamp(timestamp)

        if not self.trade_agent.market_opened():
            return

        timestamp = int(timestamp)
        print("timestamp:", timestamp, "; current_month:", datetime_obj.month)
        stock_data_dict = {}
        stock_data_dict.update({"timestamp": timestamp})

        # check if the data for the specified ticker exist, use temp_tickers instead of self.tickers for looping
        temp_ticker = []
        for ticker in self.tickers:
            if realtime_stock_data_dict.get(ticker) != None:
                temp_ticker.append(ticker)

        # update the portfolio data and get a snapshot of the account
        self.portfolio_agent.update_stock_price_and_portfolio_data(realtime_stock_data_dict)
        self.account_snapshot = self.portfolio_agent.get_account_snapshot()

        if self.check_exec(timestamp, freq="Daily", relative_delta=1):
            self.last_exec_datetime_obj = datetime_obj
            
            # portfolio is empty, initialize the portfolio by buying equal of stock
            if self.loop == 0:
                print("portfolio length is 0")

                capital_for_each_stock = float(self.account_snapshot.get(
                    "TotalCashValue")) / self.number_of_stocks  
                print("capital_for_each_stock", capital_for_each_stock)
                for ticker in temp_ticker:
                    ticker_price = realtime_stock_data_dict.get(ticker)['last']
                    share_purchase = math.floor(capital_for_each_stock / ticker_price) * 5  # 5x leverage
                    action_msg = IBActionsTuple(timestamp, IBAction.BUY_MKT_ORDER, {'ticker': ticker, 'position_purchase': share_purchase})
                    self.action_msgs.append(action_msg)
                self.last_max_drawdown_control_operation_datetime_obj = datetime_obj
            else:

                if self.check_max_drawdown_control_operation(timestamp):
                    self.last_max_drawdown_control_operation_datetime_obj = datetime_obj
                    for ticker in temp_ticker:

                        target_ex_liq = self.rebalance_margin * float(self.account_snapshot.get("GrossPositionValue"))
                        print("target_ex_liq:",target_ex_liq)

                        ticker_price = float(realtime_stock_data_dict.get(ticker)['last'])
                        

                        if self.max_drawdown_dodge[ticker]:  # the stock is dodged
                            print("self.max_drawdown_dodge[ticker]", self.max_drawdown_dodge[ticker])
                            buying_power = float(self.account_snapshot.get("BuyingPower"))
                            if self.check_buy_back(ticker, ticker_price):
                                action_msg = self.buy_back_position(ticker, ticker_price, buying_power, timestamp)  # the function handled writing of action message
                                self.action_msgs.append(action_msg)
                            else:
                                # self.time_avg_buy_back(ticker, ticker_price, buying_power, timestamp)
                                pass
                        else:  # didn't dodge
                            # see if it needs to dodge
                            print("check if dodge:  ticker_price:", ticker_price, "; benchmark_drawdown_price:",
                                    self.benchmark_drawdown_price.get(ticker))
                            # if self.is_max_drawdown_dodge(ticker, ticker_price):
                            if self.check_max_drawdown_dodge(ticker, ticker_price):  # needs to dodge
                                action_msg = self.liquidate_stock_position(ticker, ticker_price,timestamp)
                                self.action_msgs.append(action_msg)

                            else:  # doesn't need to dodge
                                if float(self.account_snapshot.get("ExcessLiquidity")) > target_ex_liq and ticker_price > self.last_exec_price.get(ticker, 0) * 1.005:
                                    ex_liq_diff = float(
                                        self.account_snapshot.get("ExcessLiquidity")) - target_ex_liq
                                    target_share_purchase = math.floor(ex_liq_diff / ticker_price)*4

                                    if target_share_purchase > 0:
                                        action_msg = IBActionsTuple(timestamp, IBAction.BUY_MKT_ORDER, {'ticker': ticker, 'position_purchase': target_share_purchase})
                                        self.action_msgs.append(action_msg)
                                        
                        self.last_exec_price[ticker] = ticker_price


                    self.last_exec_datetime_obj = datetime_obj

                    for ticker in temp_ticker:
                        real_time_ticker_price = float(realtime_stock_data_dict.get(ticker)['last'])
                        if self.max_drawdown_dodge.get(ticker):
                            self.update_benchmark_drawdown_price_after_dodge(ticker, real_time_ticker_price)
                        else:
                            self.update_max_and_benchmark_price_before_dodge(ticker, real_time_ticker_price)
                else:
                    ticker_price = float(realtime_stock_data_dict.get(ticker)['last'])
                    main_ex_liq = 0.005 * float(self.account_snapshot.get("GrossPositionValue"))
                    if float(self.account_snapshot.get("ExcessLiquidity")) < main_ex_liq:
                        ex_liq_diff = main_ex_liq - float(self.account_snapshot.get("ExcessLiquidity"))
                        target_share_sell = math.floor(ex_liq_diff / ticker_price) * 2
                        if target_share_sell > 0:
                            action_msg = IBActionsTuple(timestamp, IBAction.SELL_MKT_ORDER,{'ticker': ticker, 'position_sell': target_share_sell})
                            self.action_msgs.append(action_msg)
            self.loop += 1
            print(f"==========Finish running {self.loop} loop==========")
            return self.action_msgs.copy()
                    

    def update_max_and_benchmark_price_before_dodge(self, ticker, real_time_ticker_price):
        if (self.max_stock_price.get(ticker) == 0):  # if there is no data for the max and benchmark pric

            self.max_stock_price.update({ticker: real_time_ticker_price})
            benchmark_price = real_time_ticker_price * (1 - self.max_drawdown_ratio)
            self.benchmark_drawdown_price.update({ticker: benchmark_price})
        elif real_time_ticker_price > self.max_stock_price.get(ticker):
            self.max_stock_price.update({ticker: real_time_ticker_price})
            benchmark_price = real_time_ticker_price * (1 - self.max_drawdown_ratio)
            self.benchmark_drawdown_price.update({ticker: benchmark_price})

    def update_benchmark_drawdown_price_after_dodge(self, ticker, real_time_ticker_price):
        if real_time_ticker_price < self.benchmark_drawdown_price[ticker] * 0.7:
            target_update_benchmark_drawdown_price = real_time_ticker_price + (
                    (self.liq_sold_price_dict[ticker] - real_time_ticker_price) * 0.5)
            if target_update_benchmark_drawdown_price < self.benchmark_drawdown_price[ticker]:
                self.benchmark_drawdown_price[ticker] = target_update_benchmark_drawdown_price
        pass

    def check_max_drawdown_dodge(self, ticker, ticker_price):
        boo = ticker_price < self.benchmark_drawdown_price.get(ticker)
        return boo

    def check_buy_back(self, ticker, ticker_price):
        range_price = self.benchmark_drawdown_price.get(ticker) * (1 + 0.01)
        return ticker_price > range_price

    
    def buy_back_position(self, ticker, ticker_price, buying_power, timestamp):
        print(f"{ticker} ticker_price >= {ticker} benchmark_price")
        target_share_purchases = self.liq_sold_qty_dict.get(ticker)
        print("liq_sold_qty_dict")
        print(self.liq_sold_qty_dict.get(ticker))
        purchase_amount = target_share_purchases * ticker_price
        if buying_power >= purchase_amount:
            action_msg = IBActionsTuple(timestamp, IBAction.BUY_MKT_ORDER, 
                                        {'ticker': ticker, 'position_purchase': target_share_purchases})
        else:
            target_share_purchases = math.floor(buying_power / ticker_price)
            action_msg = IBActionsTuple(timestamp, IBAction.BUY_MKT_ORDER, 
                                        {'ticker': ticker, 'position_purchase': target_share_purchases})

        # update the benchmark price and the max price after buying back
        self.max_drawdown_dodge.update({ticker: False})
        self.max_stock_price[ticker] = ticker_price
        
        return action_msg


    def liquidate_stock_position(self, ticker, limit_price, timestamp):
        current_position = float(self.account_snapshot.get(f"position_{ticker}"))
        no_leverage_position = (float(
            self.account_snapshot.get("EquityWithLoanValue")) / self.number_of_stocks) / float(
            self.account_snapshot.get(f"marketPrice_{ticker}"))
        target_leverage_position_at_liquid_state = no_leverage_position
        print("liquidate_stock_position::current_position:", current_position)
        print("liquidate_stock_position::no_leverage_position:", no_leverage_position)  # corrected variable name
        target_sold_position = math.ceil(current_position - target_leverage_position_at_liquid_state)

        action_msg = IBActionsTuple(timestamp, IBAction.SELL_MKT_ORDER, 
                                    {'ticker': ticker, 'position_sell': target_sold_position})
        print(f"Added SELL_MKT_ORDER action for {ticker} with position_sell = {target_sold_position}")

        self.benchmark_drawdown_price.update({ticker: limit_price})
        self.liq_sold_qty_dict.update({ticker: action_msg.args_dict['position_sell']})
        self.liq_sold_price_dict.update({ticker: limit_price})
        self.liquidate_sold_value.update({ticker: limit_price * action_msg.args_dict['position_sell']})

        self.max_drawdown_dodge.update({ticker: True})

        return action_msg


    def check_exec(self, timestamp, **kwargs):
        datetime_obj = datetime.utcfromtimestamp(timestamp)
        if self.last_exec_datetime_obj == None:
            return True
        else:
            freq = kwargs.pop("freq")
            relative_delta = kwargs.pop("relative_delta")
            if freq == "Daily":
                # next_exec_datetime_obj = self.last_exec_datetime_obj + relativedelta(days=+relative_delta)
                if datetime_obj.day != self.last_exec_datetime_obj.day and datetime_obj > self.last_exec_datetime_obj:
                    print(
                        f"check_exec: True. last_exec_datetime_obj.day={self.last_exec_datetime_obj.day}; datetime_obj.day={datetime_obj.day}")
                    return True
                else:
                    print(
                        f"check_exec: False. last_exec_datetime_obj.day={self.last_exec_datetime_obj.day}; datetime_obj.day={datetime_obj.day}")
                    return False

            elif freq == "Monthly":
                next_exec_datetime_obj = self.last_exec_datetime_obj + relativedelta(months=+relative_delta)
                if datetime_obj.month >= next_exec_datetime_obj.month:
                    print(
                        f"check_exec: True. last_exec_datetime_obj.month={self.last_exec_datetime_obj.month}; datetime_obj.month={datetime_obj.month}")
                    return True
                else:
                    print(
                        f"check_exec: False. last_exec_datetime_obj.month={self.last_exec_datetime_obj.month}; datetime_obj.month={datetime_obj.month}")
                    return False

    def check_max_drawdown_control_operation(self, timestamp):
        datetime_obj = datetime.utcfromtimestamp(timestamp)
        # next_exec_datetime_obj = self.last_max_drawdown_control_operation_datetime_obj + relativedelta(months=+1)
        # if datetime_obj.month >= next_exec_datetime_obj.month and datetime_obj >= next_exec_datetime_obj:
        if datetime_obj.month != self.last_max_drawdown_control_operation_datetime_obj.month and datetime_obj > self.last_max_drawdown_control_operation_datetime_obj:
            print(
                f"check_exec: True. last_max_drawdown_control_operation_datetime_obj.month={self.last_max_drawdown_control_operation_datetime_obj.month}; datetime_obj.month={datetime_obj.month}")
            return True
        else:
            print(
                f"check_exec: False. last_max_drawdown_control_operation_datetime_obj.month={self.last_max_drawdown_control_operation_datetime_obj.month}; datetime_obj.month={datetime_obj.month}")
            return False

    # def check_fuse_liquidation(self, timestamp, realtime_stock_data_dict):
    #     exec_arr = []
    #     for ticker in self.tickers:
    #         print(self.max_stock_price[ticker])
    #         if realtime_stock_data_dict[ticker]['last'] > self.benchmark_drawdown_price[ticker] * 0.5:
    #             action_msg = self.liquidate_stock_position(ticker,realtime_stock_data_dict[ticker]['last'] * (1 + self.acceptance_range), timestamp)
    #             print("check_exec: False.  Liquidate_stock_position")
    #             exec_arr.append(True)
    #             self.reg_exec[ticker] = True
    #         else:
    #             exec_arr.append(False)
    #             print("check_exec: No fuse.")
    #     return action_msg, exec_arr

    # def time_avg_buy_back(self, ticker, ticker_price, buying_power, timestamp):
    #     # print(f"{ticker} ticker_price")
    #     # target_share_value_purchases = self.liquidate_sold_value[ticker] / 24
    #     # target_share_purchases = math.floor(target_share_value_purchases/ticker_price)
    #     target_share_purchases = math.floor(self.liq_sold_qty_dict[ticker] / 24)
    #     print("target_share_purchases:", target_share_purchases)
    #     purchase_amount = target_share_purchases * ticker_price
    #     if buying_power >= purchase_amount:
    #         action_msg = self.trade_agent.place_buy_stock_limit_order(ticker, target_share_purchases,
    #                                                                   ticker_price * (1 + self.acceptance_range),
    #                                                                   timestamp)
    #     else:
    #         target_share_purchases = math.floor(buying_power / ticker_price)
    #         action_msg = self.trade_agent.place_buy_stock_limit_order(ticker, target_share_purchases,
    #                                                                   ticker_price * (1 + self.acceptance_range),
    #                                                                   timestamp)

    #     self.action_msgs.append(action_msg)
    #     self.liq_sold_qty_dict[ticker] -= target_share_purchases

    #     pass


def main():
    tickers = ["QQQ", "SPY"]
    acceptance_range = 0.02  # for placing limit order
    max_drawdown_ratio = 0  # to be modified
    rebalance_margin = 0  # to be modified

    # create ibkr_acc_data object
    user_id = 0
    table_info = {"mode": "realtime", "strategy_name": "test", "user_id": user_id}
    # strategy_name = "rebalance_margin_wif_max_drawdown_control"
    table_name = table_info.get("mode") + "_" + table_info.get("strategy_name") + "_" + str(table_info.get("user_id"))
    spec_str = "test"
    ibkr_acc = ibkr_acc_data(table_info.get("user_id"), table_info.get("strategy_name"), table_name, spec_str)

    # instantiate the ib object and connection
    ib = IB()
    ib.connect('127.0.0.1', 7497, clientId=1)

    ibkr_portfolio_engine = ibkr_portfolio_data_engine(ibkr_acc, ib)
    ibkr_trade_engine = ibkr_trade_agent(ib)
    ibkr_stock_data_engine = ibkr_stock_data_io_engine(ib)

    algo = rebalance_margin_wif_max_drawdown(ibkr_trade_engine, ibkr_stock_data_engine, ibkr_portfolio_engine, tickers,
                                             max_drawdown_ratio, acceptance_range, rebalance_margin)

    while True:
        algo.run()
        sleep(60)


if __name__ == "__main__":
    main()