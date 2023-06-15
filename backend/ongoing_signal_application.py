from algo.accelerating_dual_momentum.backtest import backtest as AccelDualMomentumBacktest
from algo.rebalance_margin_wif_max_drawdown_control.backtest import backtest as RebalanceMarginWithMaxDrawdownControlBacktest
from threading import Thread, Lock
from datetime import datetime as dt
import os
from pathlib import Path
import shutil
import json
import datetime


class OngoingSignalApplication:
    def __init__(self):
        self.table_ids = []
        self.table_list_dir = Path(__file__).parent.parent / "user_id_0" / "ongoing"

    def get_next_table_id(self):
        next_table_id = len(self.table_ids)
        self.table_ids.append(next_table_id)
        return next_table_id

    def run_rebalance_margin_with_max_drawdown_control(self, user_id, var_param, display_name, table_id):

        strategy_name = "rebalance_margin_with_max_drawdown_control"
        table_name = str(table_id) + "__" + strategy_name
        table_dir = self.table_list_dir / table_name
        table_dir.mkdir(parents=True, exist_ok=True)

        # Define your parameter maps
        basic_setting = {
            'table_dir': table_dir,
            'user_id': user_id,
            'table_name': table_name,
            'cal_stat': True,
            'data_freq': "one_day",
            'db_mode': {"dynamo_db": False, "local": True},
            'restart': True,
            'quick_test': True
        }

        fixed_param = {
            'initial_amount': 1000000,
            'start_date': dt(2015, 6, 3),
            'end_date': dt(2016, 6, 3)
        }

        info_param = {
            'store_mongoDB': False,
            'strategy_initial': 'rebalance_margin_with_max_drawdown_control',
            'video_link': None,
            'documents_link': None,
            'tags_array': None,
            'subscribers_num': None,
            'rating_dict': None,
            'margin_ratio': 3.24,
            'trader_name': None
        }

        # Initialize the backtest object
        # replace 'RebalanceMarginWithMaxDrawdownControlBacktest' with your actual backtest class
        backtest = RebalanceMarginWithMaxDrawdownControlBacktest(basic_setting, fixed_param, var_param, info_param)

        backtest.backtest_exec()
        # Update database.json
        self.update_database_json(table_id, strategy_name, display_name, table_name)

    def run_accelerating_dual_momentum(self, user_id, var_param, display_name, table_id):

        strategy_name = "accelerating_dual_momentum"
        table_name = str(table_id) + "__" + strategy_name
        table_dir = self.table_list_dir / table_name
        table_dir.mkdir(parents=True, exist_ok=True)

        start_date = dt(2015, 1, 1)
        end_date = dt(2020, 1, 1)
        # Define your parameter maps
        basic_setting = {
            'table_dir': table_dir,  # assuming self.table_list_dir and table_name are defined
            'user_id': user_id,  # replace 'user_id_value' with actual value
            'table_name': table_name,
            'cal_stat': True,
            'data_freq': "one_day",
            'db_mode': {"dynamo_db": False, "local": True},
            'restart': True,  
            'quick_test': True  
        }

        fixed_param = {
            'initial_amount': 1000000,
            'start_date': start_date,
            'end_date': end_date  # replace 'end_date_value' with actual value
        }

        info_param = {
            'store_mongoDB': False,  # replace 'store_mongoDB_value' with actual value


            'strategy_initial': 'accelerating_dual_momentum',
            'video_link': None,  # replace 'video_link_value' with actual value
            'documents_link': None,  # replace 'documents_link_value' with actual value
            'tags_array': None,  # replace 'tags_array_value' with actual value
            'subscribers_num': None,  # replace 'subscribers_num_value' with actual value
            'rating_dict': None,  # replace 'rating_dict_value' with actual value
            'margin_ratio': 3.24,
            'trader_name': None  # replace 'trader_name_value' with actual value
        }

        var_param['start_date'] = start_date
        # Initialize the backtest object

        accelDualMomentumBacktest = AccelDualMomentumBacktest(basic_setting, fixed_param, var_param, info_param)
        print(f"Starting {display_name}...")
        print(f"User ID: {user_id}, strategy_name:{strategy_name}, var_param: {var_param}")

        accelDualMomentumBacktest.backtest_exec()
        # Update database.json
        



    def restart(self):
        # delete everything under self.table_list_dir
        shutil.rmtree(self.table_list_dir, ignore_errors=True)  # add ignore_errors=True to avoid FileNotFoundError
        # create the directory again
        os.makedirs(self.table_list_dir, exist_ok=True)
        threads = []
        # remove the database.json file if it exists
        database_path = self.table_list_dir / 'database.json'
        if database_path.exists():
            database_path.unlink()

        # define var_params for accelerating daul momentum backtest_exec 
        user_ids = [0, 0]  # define the user_ids here
        var_params = [
            {
                'tickers': ["SPY", "QQQ"],
                'bond': ["TIP"],
            }, 
            {
                'tickers': ["SPY", "ARKK"],
                'bond': ["TIP"]
            }
        ]

        display_names = ["SPY QQQ Accel Dual Momentum", "SPY ARKK Accel Dual Momentum"]  # user-defined display names
        
        # # define var_params for accelerating daul momentum backtest_exec 
        # user_ids = [0]  # define the user_ids here
        # var_params = [
        #     {
        #         'tickers': ["SPY", "QQQ"],
        #         'bond': ["TIP"],
        #     }
        # ]

        # display_names = ["SPY QQQ Accel Dual Momentum"]  # user-defined display names


        for user_id, var_param, display_name in zip(user_ids, var_params, display_names):
            table_id = self.get_next_table_id()
            strategy_name = "accelerating_dual_momentum"
            table_name = str(table_id) + "__" + strategy_name
            self.update_database_json(table_id, strategy_name, display_name, table_name)

            t = Thread(target=self.run_accelerating_dual_momentum, args=(user_id, var_param, display_name, table_id))
            threads.append(t)


        #loop thorugh params for rebalance_margin_wif_max_drawdown_control 
        rabalance_dict = {"start":80, "end":100, "step":10}
        maintain_dict = {"start":1, "end":2, "step":1}
        purchase_exliq_ratio_dict = {"start":500, "end":502, "step":2}
        max_drawdown_ratio_dict = {"start": 5, "end": 7, "step": 2}

        # Append threads and pre-generate table IDs for run_rebalance_margin_with_max_drawdown_control
        for rebalance in range(rabalance_dict.get("start"), rabalance_dict.get("end"), rabalance_dict.get("step")):
            for max_drawdown in range(max_drawdown_ratio_dict.get("start"), max_drawdown_ratio_dict.get("end"), max_drawdown_ratio_dict.get("step")):
                for purchase_exliq_ratio in range(purchase_exliq_ratio_dict.get("start"), purchase_exliq_ratio_dict.get("end"), purchase_exliq_ratio_dict.get("step")):



                    rebalance_margin = rebalance / 1000
                    maintain_margin = 0.01
                    max_drawdown_ratio = max_drawdown / 1000
                    purchase_exliq = purchase_exliq_ratio / 100
                    acceptance_range = 0

                    var_param = {
                        'rebalance_margin': rebalance_margin,
                        "maintain_margin": maintain_margin,
                        'max_drawdown_ratio': max_drawdown_ratio,
                        'purchase_exliq': purchase_exliq,
                        "tickers": ["QQQ"],
                        "acceptance_range": acceptance_range
                    }
                    
                    table_id = self.get_next_table_id()
                    strategy_name = "rebalance_margin_with_max_drawdown_control"
                    table_name = str(table_id) + "__" + strategy_name
                    display_name = f"Rebalance Margin {rebalance_margin}, Max Drawdown Ratio {max_drawdown_ratio}, Purchase Exliq {purchase_exliq}"

                    user_id = 0
                    self.update_database_json(table_id, strategy_name, display_name, table_name)
                    
                    t = Thread(target=self.run_rebalance_margin_with_max_drawdown_control, args=(user_id, var_param, display_name, table_id))
                    threads.append(t)


        #loop thorugh params for rebalance_margin_wif_max_drawdown_control 
        rabalance_dict = {"start":80, "end":100, "step":10}
        maintain_dict = {"start":1, "end":2, "step":1}
        purchase_exliq_ratio_dict = {"start":500, "end":502, "step":2}
        max_drawdown_ratio_dict = {"start": 5, "end": 7, "step": 2}

        # Append threads and pre-generate table IDs for run_rebalance_margin_with_max_drawdown_control
        for rebalance in range(rabalance_dict.get("start"), rabalance_dict.get("end"), rabalance_dict.get("step")):
            for max_drawdown in range(max_drawdown_ratio_dict.get("start"), max_drawdown_ratio_dict.get("end"), max_drawdown_ratio_dict.get("step")):
                for purchase_exliq_ratio in range(purchase_exliq_ratio_dict.get("start"), purchase_exliq_ratio_dict.get("end"), purchase_exliq_ratio_dict.get("step")):

                    table_id = self.get_next_table_id()
                    user_id = 0

                    rebalance_margin = rebalance / 1000
                    maintain_margin = 0.01
                    max_drawdown_ratio = max_drawdown / 1000
                    purchase_exliq = purchase_exliq_ratio / 100
                    acceptance_range = 0

                    var_param = {
                        'rebalance_margin': rebalance_margin,
                        "maintain_margin": maintain_margin,
                        'max_drawdown_ratio': max_drawdown_ratio,
                        'purchase_exliq': purchase_exliq,
                        "tickers": ["SPY"],
                        "acceptance_range": acceptance_range
                    }

                    display_name = f"Rebalance Margin {rebalance_margin}, Max Drawdown Ratio {max_drawdown_ratio}, Purchase Exliq {purchase_exliq}"
                    t = Thread(target=self.run_rebalance_margin_with_max_drawdown_control, args=(user_id, var_param, display_name, table_id))
                    threads.append(t)

        # Start all threads
        for thread in threads:
            thread.start()
            
        # Wait for all threads to finish
        for thread in threads:
            thread.join()

    def update_database_json(self, table_id, strategy_name, display_name, table_name):
        # Path to the database.json file
        database_path = self.table_list_dir / 'database.json'

        # Load the existing data
        try:
            with open(database_path, 'r') as file:
                data = json.load(file)
        except FileNotFoundError:
            data = []

        # Append the new item
        data.append({
            "table_id": table_id,
            "strategy_name": strategy_name,
            "display_name": display_name,
            "folder_name": table_name
        })

        # Write the data back out
        with open(database_path, 'w') as file:
            json.dump(data, file)

def main():
    app = OngoingSignalApplication()
    app.restart()


if __name__ == "__main__":
    main()