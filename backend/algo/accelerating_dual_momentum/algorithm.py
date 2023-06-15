from object.backtest_acc_data import backtest_acc_data
from engine.backtest_engine.trade_engine import backtest_trade_engine
from engine.backtest_engine.portfolio_data_engine import backtest_portfolio_data_engine
from datetime import datetime
from dateutil.relativedelta import relativedelta
from object.action_data import IBAction, IBActionsTuple
from .indicator import Indicator
import pandas as pd

class accelerating_dual_momentum:

    def __init__(self, trade_agent, portfolio_agent, stock_data_engines, var_param):
        self.account_snapshot = {}
        self.portfolio = []
        self.trade_agent = trade_agent

        self.portfolio_agent = portfolio_agent
        self.pct_change_dict = {}
        self.last_exec_datetime_obj = None
        self.portfolio = self.account_snapshot.get("portfolio")
        self.total_market_value = self.account_snapshot.get("NetLiquidation")
        self.action_msgs = []

        self.stock_data_engines = stock_data_engines
        self.tickers = var_param["tickers"]
        self.bond = var_param.get("bond", [])
        self.options = self.tickers + self.bond

        self.start_date = var_param["start_date"]

        self.indicator = Indicator(stock_data_engines, self.tickers, self.start_date)
        self.last_momentum_operation_datetime_obj = None
        self.loop = 0

    def run(self, price_dict, bond, timestamp):
    
        # Append the price data to ticker data frame and calculate the percentage change for each ticker
        print("run:append_into_ticker_df")
        datetime_obj = datetime.utcfromtimestamp(timestamp)

        for option in self.options:
            # Fetching option data from the engine by timestamp
            option_engine = self.stock_data_engines[option]
            option_items = option_engine.get_ticker_item_by_timestamp(timestamp)
            self.indicator.append_into_ticker_df(option, option_items)

        print("Appended")
        self.pct_change_dict = self.indicator.getPctChangeDict([*price_dict], timestamp)
        print("pct_change_dict:",self.pct_change_dict)

        # Update the portfolio based on the new price data and get the current state of the account
        self.portfolio_agent.update_stock_price_and_portfolio_data(price_dict)
        self.account_snapshot = self.portfolio_agent.get_account_snapshot()
        # If it's time to execute the trades (once per month)
        if self.check_exec(timestamp, freq="Daily", relative_delta=1):

            # Clear out any previous action messages
            self.action_msgs = []
            
            # If the market isn't open, there's nothing to do
            if not self.trade_agent.market_opened():
                return

            if self.check_momentum_operation(timestamp):    
                self.last_momentum_operation_datetime_obj = datetime_obj
            # Get the current portfolio and the total value of the account
                self.portfolio = self.portfolio_agent.get_portfolio()
                
                # Create empty list to hold the momentum signals for each ticker
                momentum_signals = []
                buy = ""
                
                # Calculate the momentum signal for each ticker based on the pct change over 1, 3, and 6 months
                for ticker in self.tickers:
                    one_month_pct_change = self.pct_change_dict[ticker][1]
                    three_month_pct_change = self.pct_change_dict[ticker][3]
                    six_month_pct_change = self.pct_change_dict[ticker][6]
                    
                    print("One month pct change for {}: {}".format(ticker, one_month_pct_change))
                    print("Three month pct change for {}: {}".format(ticker, three_month_pct_change))
                    print("Six month pct change for {}: {}".format(ticker, six_month_pct_change))

                    momentum_signal = one_month_pct_change * 0.33 + three_month_pct_change * 0.33 + six_month_pct_change * 0.34
                    print("Momentum signal for {}: {}".format(ticker, momentum_signal))
                    
                    momentum_signals.append(momentum_signal)

                # If the momentum signals for all tickers are negative, buy bonds instead
                if momentum_signals[0] < 0 and momentum_signals[1] < 0:
                    buy = bond[0]
                # Otherwise, buy the ticker with the highest momentum signal
                elif momentum_signals[0] > momentum_signals[1]:
                    buy = self.tickers[0]
                elif momentum_signals[0] < momentum_signals[1]:
                    buy = self.tickers[1]

                print("Selected to buy:", buy)
                
                # Go through each ticker in the portfolio
                for ticker_data in self.portfolio:
                    ticker_name = ticker_data["ticker"]
                    ticker_pos = ticker_data["position"]

                    print("Ticker in portfolio:", ticker_name)
                    print("Position in this ticker:", ticker_pos)

                    # If the ticker is the one we want to buy
                    if ticker_name == buy:
                        print("Ticker we want to buy:",ticker_name)
                        # If we already hold some of this ticker, calculate how much more we need to buy
                        if ticker_pos > 0:  
                            print("We already hold some of this ticker.")
                            price = price_dict[buy]["last"]
                            print("NetLiquidation:", self.account_snapshot.get("NetLiquidation"))
                            target_pos = self.account_snapshot.get("NetLiquidation") / price
                            print("target_pos:", target_pos)
                            buy_pos = target_pos - ticker_pos
                            print("Calculated position to buy:", buy_pos)
                            if buy_pos > 0.0:
                                print("Placing an order to buy more of this ticker.")
                                # Generate a buy order for the additional shares needed
                                action_msg = IBActionsTuple(timestamp, IBAction.BUY_MKT_ORDER, {'ticker': buy, 'position_purchase': buy_pos})
                                self.action_msgs.append(action_msg)
                        # If we don't currently hold any of this ticker, generate a buy order for the full amount
                        elif ticker_pos == 0: 
                            print("We do not hold this ticker yet.")
                            price = price_dict[buy]["last"]
                            target_pos = self.account_snapshot.get("NetLiquidation") / price
                            print("Placing an order to buy this ticker.")
                            action_msg = IBActionsTuple(timestamp, IBAction.BUY_MKT_ORDER, {'ticker': buy, 'position_purchase': target_pos})
                            self.action_msgs.append(action_msg)
                    # If we are holding a ticker that we don't want to buy, we sell it
                    elif ticker_pos > 0:  
                        print("Ticker we want to sell:",ticker_name)
                        sell = ticker_name
                        sell_pos = ticker_pos
                        print("Calculated position to sell:", sell_pos)
                        # Generate a sell order to get rid of all shares of this ticker
                        action_msg = IBActionsTuple(timestamp, IBAction.SELL_MKT_ORDER, {'ticker': sell, 'position_sell': sell_pos})
                        self.action_msgs.append(action_msg)
        else:
            print("check_exec: False")    
        # Return the list of action messages, which are the orders that will be executed
        self.loop += 1
        return self.action_msgs.copy()



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

    def check_momentum_operation(self, timestamp):

        datetime_obj = datetime.utcfromtimestamp(timestamp)
        if  self.loop == 0:
            return True
        else:
            if datetime_obj.month != self.last_momentum_operation_datetime_obj.month and datetime_obj > self.last_momentum_operation_datetime_obj:
                print(
                    f"check_exec: True. last_momentum_operation_datetime_obj.month={self.last_momentum_operation_datetime_obj.month}; datetime_obj.month={datetime_obj.month}")
                return True
            else:
                print(
                    f"check_exec: False. last_momentum_operation_datetime_obj.month={self.last_momentum_operation_datetime_obj.month}; datetime_obj.month={datetime_obj.month}")
                return False