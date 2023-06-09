import json
import pathlib
import numpy as np

class backtest_acc_data(object):
    trading_funds = {}
    mkt_value = {}
    margin_acc = {}
    deposit_withdraw_cash_record = {}
    portfolio = []
    margin_info = []
    stock_transaction_record = []
    cashflow_record = []
    acc_data_json_file_path = ""
    table_name = ""

    def __init__(self, table_dir, table_name):
        self.table_name = table_name
        self.portfolio = []
        self.stock_transaction_record = []
        self.deposit_withdraw_cash_record = []
        # the above 4 are for the entire account
        self.acc_data = {"AccountCode": 0, "Currency": "HKD", "ExchangeRate": 0}
        self.margin_acc = {'FullInitMarginReq': 0, 'FullMaintMarginReq': 0}
        self.trading_funds = {'AvailableFunds': 0, "ExcessLiquidity": 0, "BuyingPower": 0, "Leverage": 0,
                              "EquityWithLoanValue": 0}
        self.mkt_value = {"TotalCashValue": 0, "NetDividend": 0, "NetLiquidation": 0, "UnrealizedPnL": 0,
                          "RealizedPnL": 0, "GrossPositionValue": 0}

        self.initialize_margin_info()
        self.acc_data_json_file_path = table_dir.joinpath("acc_data", f"{self.table_name}.json")
        
    # for stocks !
    def update_portfolio_item(self, ticker, position, marketPrice, averageCost, marketValue, realizedPNL, unrealizedPNL,
                              initMarginReq, maintMarginReq, costBasis):
        updating_portfolio_dict = {'ticker': ticker, 'position': position, "marketPrice": marketPrice,
                                   'averageCost': averageCost, "marketValue": marketValue,
                                   "realizedPNL": realizedPNL, "unrealizedPNL": unrealizedPNL,
                                   'initMarginReq': initMarginReq, 'maintMarginReq': maintMarginReq,
                                   "costBasis": costBasis}
        update = False
        if len(self.portfolio) == 0:
            self.portfolio.append(updating_portfolio_dict)
        else:
            for item in self.portfolio:
                if item.get("ticker") == ticker:
                    item.update((k, v) for k, v in updating_portfolio_dict.items() if v is not None)
                    update = True
                    break
            if not update:
                self.portfolio.append(updating_portfolio_dict)

    def append_stock_transaction_record(self, ticker, timestamp, transaction_type, position_purchase, ticker_open_price,
                                        transaction_amount,
                                        position):
        transaction_type_dict = {0: "Buy", 1: "Sell"}
        record = {'ticker': ticker, "timestamp": timestamp,
                  'transaction_type': transaction_type_dict.get(transaction_type),
                  "position_purchase": position_purchase, 'ticker_open_price': ticker_open_price,
                  'transaction_amount': transaction_amount,
                  'position': position}
        self.stock_transaction_record.append(record)

    def append_cashflow_record(self, timestamp, transaction_type, amount):
        transaction_type_dict = {0: "Deposit", 1: "Withdraw"}
        record = {'timestamp': timestamp, 'transaction_type': transaction_type_dict.get(transaction_type),
                  'amount': amount}
        self.cashflow_record.append(record)

    def update_acc_data(self, AccountCode, Currency, ExchangeRate):
        updating_acc_data_dict = {"AccountCode": AccountCode, "Currency": Currency, "ExchangeRate": ExchangeRate}
        self.acc_data.update((k, v) for k, v in updating_acc_data_dict.items() if v is not None)

    def update_margin_acc(self, FullInitMarginReq, FullMaintMarginReq):
        updating_margin_acc_dict = {'FullInitMarginReq': FullInitMarginReq, 'FullMaintMarginReq': FullMaintMarginReq}
        self.margin_acc.update((k, v) for k, v in updating_margin_acc_dict.items() if v is not None)

    def update_trading_funds(self, AvailableFunds, ExcessLiquidity, BuyingPower, Leverage, EquityWithLoanValue):
        updating_trading_funds_dict = {'AvailableFunds': AvailableFunds, 'ExcessLiquidity': ExcessLiquidity,
                                       'BuyingPower': BuyingPower,
                                       'Leverage': Leverage, 'EquityWithLoanValue': EquityWithLoanValue}
        self.trading_funds.update((k, v) for k, v in updating_trading_funds_dict.items() if v is not None)

    def update_mkt_value(self, TotalCashValue, NetDividend, NetLiquidation, UnrealizedPnL, RealizedPnL,
                         GrossPositionValue):
        updating_mkt_value_dict = {"TotalCashValue": TotalCashValue, "NetDividend": NetDividend,
                                   "NetLiquidation": NetLiquidation, "UnrealizedPnL": UnrealizedPnL,
                                   "RealizedPnL": RealizedPnL, "GrossPositionValue": GrossPositionValue}
        self.mkt_value.update((k, v) for k, v in updating_mkt_value_dict.items() if v is not None)

    def check_if_ticker_exist_in_portfolio(self, ticker):
        tickers = [d['ticker'] for d in self.portfolio]
        if ticker in tickers:
            return True
        else:
            return False

    def get_portfolio_ticker_item(self, ticker):
        ticker_item = next((item for item in self.portfolio if item['ticker'] == ticker), None)
        return ticker_item

    def update_portfolio_ticker_item(self, ticker_item):
        ticker = ticker_item.ticker
        for item in self.portfolio:
            if item.get("ticker") == ticker:
                ticker_dict = ticker_item.__getdict__()
                for k, v in ticker_dict.items():
                    if v is not None:
                        item.update({k: v})
                break

    def get_margin_info_ticker_item(self, ticker):
        margin_info_item = next((item for item in self.margin_info if item["ticker"] == ticker), None)
        return margin_info_item

    def return_acc_data(self):
        class CustomJSONEncoder(json.JSONEncoder):
            def default(self, obj):
                if isinstance(obj, np.int64):
                    return int(obj)
                return json.JSONEncoder.default(self, obj)

        portfolio_json = json.dumps(self.portfolio, cls=CustomJSONEncoder)
        stock_transaction_record_json = json.dumps(self.stock_transaction_record, cls=CustomJSONEncoder)
        deposit_withdraw_cash_record_json = json.dumps(self.deposit_withdraw_cash_record, cls=CustomJSONEncoder)

        acc_data_json = json.dumps(self.acc_data, cls=CustomJSONEncoder)
        mkt_value_json = json.dumps(self.mkt_value, cls=CustomJSONEncoder)
        margin_acc_json = json.dumps(self.margin_acc, cls=CustomJSONEncoder)
        trading_funds_json = json.dumps(self.trading_funds, cls=CustomJSONEncoder)

        data_dict = {"portfolio": portfolio_json, "stock_transaction_record": stock_transaction_record_json,
                    "deposit_withdraw_cash_record": deposit_withdraw_cash_record_json,
                    "acc_data": acc_data_json, "mkt_value": mkt_value_json, "margin_acc": margin_acc_json,
                    "trading_funds": trading_funds_json
                    }

        return data_dict


    def read_acc_data(self):
        acc_data_json_file = pathlib.Path(self.acc_data_json_file_path)
        if acc_data_json_file.is_file():
            data_dict = {}
            with open(self.acc_data_json_file_path, 'r') as f:
                data_dict = json.load(f)

            portfolio_json = data_dict.get("portfolio")
            stock_transaction_record_json = data_dict.get("stock_transaction_record")
            deposit_withdraw_cash_record_json = data_dict.get("deposit_withdraw_cash_record")

            acc_data_json = data_dict.get("acc_data")
            mkt_value_json = data_dict.get("mkt_value")
            margin_acc_json = data_dict.get("margin_acc")
            trading_funds_json = data_dict.get("trading_funds")

            self.portfolio = json.loads(portfolio_json)
            self.stock_transaction_record = json.loads(stock_transaction_record_json)
            self.deposit_withdraw_cash_record = json.loads(deposit_withdraw_cash_record_json)

            self.acc_data = json.loads(acc_data_json)
            self.mkt_value = json.loads(mkt_value_json)
            self.margin_acc = json.loads(margin_acc_json)
            self.trading_funds = json.loads(trading_funds_json)

        pass

    def get_portfolio(self):
        return self.portfolio

    def get_mkt_value(self):
        return self.mkt_value


    def initialize_margin_info(self):
        _3188 = {'ticker': '3188', 'initMarginReq': 0.2500, 'maintMarginReq': 0.2000}
        _spy = {'ticker': 'SPY', 'initMarginReq': 0.1091, 'maintMarginReq': 0.992}
        _govt = {'ticker': 'GOVT', 'initMarginReq': 0.099, 'maintMarginReq': 0.09}
        _shv = {'ticker': 'SHV', 'initMarginReq': 0.099, 'maintMarginReq': 0.09}
        _ivv = {'ticker': 'IVV', 'initMarginReq': 0.1071, 'maintMarginReq': 0.0974}
        _vti = {'ticker': 'VTI', 'initMarginReq': 0.1111, 'maintMarginReq': 0.1010}
        _voo = {'ticker': 'VOO', 'initMarginReq': 0.1068, 'maintMarginReq': 0.0971}
        _qqq = {'ticker': 'QQQ', 'initMarginReq': 0.1315, 'maintMarginReq': 0.1196}
        _vtv = {'ticker': 'VTV', 'initMarginReq': 0.1686, 'maintMarginReq': 0.1533}
        _agg = {'ticker': 'AGG', 'initMarginReq': 0.1652, 'maintMarginReq': 0.1502}
        _bnd = {'ticker': 'BND', 'initMarginReq': 0.1652, 'maintMarginReq': 0.1502}
        _vug = {'ticker': 'VUG', 'initMarginReq': 0.1696, 'maintMarginReq': 0.1542}
        _ijr = {'ticker': 'IJR', 'initMarginReq': 0.1420, 'maintMarginReq': 0.1291}
        _vig = {'ticker': 'VIG', 'initMarginReq': 0.1680, 'maintMarginReq': 0.1527}
        _ijh = {'ticker': 'IJH', 'initMarginReq': 0.1299, 'maintMarginReq': 0.1181}
        _iwf = {'ticker': 'IWF', 'initMarginReq': 0.1246, 'maintMarginReq': 0.1133}
        _iwd = {'ticker': 'IWD', 'initMarginReq': 0.1016, 'maintMarginReq': 0.0924}
        _iwm = {'ticker': 'IWM', 'initMarginReq': 0.1346, 'maintMarginReq': 0.1224}
        _vo = {'ticker': 'VO', 'initMarginReq': 0.1692, 'maintMarginReq': 0.1538}
        _vym = {'ticker': 'VYM', 'initMarginReq': 0.1684, 'maintMarginReq': 0.1531}
        _xle = {'ticker': 'XLE', 'initMarginReq': 0.1687, 'maintMarginReq': 0.1534}
        _vgt = {'ticker': 'VGT', 'initMarginReq': 0.1698, 'maintMarginReq': 0.1543}
        _vb = {'ticker': 'VB', 'initMarginReq': 0.1255, 'maintMarginReq': 0.1141}
        _vnq = {'ticker': 'VNQ', 'initMarginReq': 0.1690, 'maintMarginReq': 0.1536}
        _xlk = {'ticker': 'XLK', 'initMarginReq': 0.1695, 'maintMarginReq': 0.1541}
        _itot = {'ticker': 'ITOT', 'initMarginReq': 0.1110, 'maintMarginReq': 0.1009}
        _bsv = {'ticker': 'BSV', 'initMarginReq': 0.1652, 'maintMarginReq': 0.1502}
        _xlv = {'ticker': 'XLV', 'initMarginReq': 0.1688, 'maintMarginReq': 0.1535}
        _schd = {'ticker': 'SCHD', 'initMarginReq': 0.1681, 'maintMarginReq': 0.1528}
        _xlf = {'ticker': 'XLF', 'initMarginReq': 0.1693, 'maintMarginReq': 0.1539}
        _lqd = {'ticker': 'LQD', 'initMarginReq': 0.1661, 'maintMarginReq': 0.1510}
        _rsp = {'ticker': 'RSP', 'initMarginReq': 0.1148, 'maintMarginReq': 0.1043}
        _tip = {'ticker': 'TIP', 'initMarginReq': 0.0990, 'maintMarginReq': 0.0900}
        _ivw = {'ticker': 'IVW', 'initMarginReq': 0.1258, 'maintMarginReq': 0.1143}
        _schx = {'ticker': 'SCHX', 'initMarginReq': 0.1691, 'maintMarginReq': 0.1537}
        _iwr = {'ticker': 'IWR', 'initMarginReq': 0.1207, 'maintMarginReq': 0.1097}
        _mub = {'ticker': 'MUB', 'initMarginReq': 0.0994, 'maintMarginReq': 0.0904}
        _dia = {'ticker': 'DIA', 'initMarginReq': 0.1010, 'maintMarginReq': 0.0918}
        _iwb = {'ticker': 'IWB', 'initMarginReq': 0.1102, 'maintMarginReq': 0.1002}
        _usmv = {'ticker': 'USMV', 'initMarginReq': 0.25, 'maintMarginReq': 0.2}
        _vv = {'ticker': 'VV', 'initMarginReq': 0.1691, 'maintMarginReq': 0.1538}
        _ive = {'ticker': 'IVE', 'initMarginReq': 0.1069, 'maintMarginReq': 0.0972}
        _shy = {'ticker': 'SHY', 'initMarginReq': 0.0990, 'maintMarginReq': 0.0990}
        _vbr = {'ticker': 'VBR', 'initMarginReq': 0.1387, 'maintMarginReq': 0.1261}
        _dvy = {'ticker': 'DVY', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _dgro = {'ticker': 'DGRO', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _esgu = {'ticker': 'ESGU', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _sdy = {'ticker': 'SDY', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _igsb = {'ticker': 'IGSB', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _qual = {'ticker': 'QUAL', 'initMarginReq': 0.2500, 'maintMarginReq': 0.2000}
        _vtip = {'ticker': 'VTIP', 'initMarginReq': 0.0990, 'maintMarginReq': 0.0900}
        _mbb = {'ticker': 'MBB', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _schb = {'ticker': 'SCHB', 'initMarginReq': 0.1182, 'maintMarginReq': 0.1074}
        _tlt = {'ticker': 'TLT', 'initMarginReq': 0.0990, 'maintMarginReq': 0.0900}
        _mdy = {'ticker': 'MDY', 'initMarginReq': 0.1353, 'maintMarginReq': 0.1230}
        _jpst = {'ticker': 'JPST', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _shv = {'ticker': 'SHV', 'initMarginReq': 0.0990, 'maintMarginReq': 0.0900}
        _ief = {'ticker': 'IEF', 'initMarginReq': 0.0990, 'maintMarginReq': 0.0900}
        _govt = {'ticker': 'GOVT', 'initMarginReq': 0.0990, 'maintMarginReq': 0.0900}
        _iusb = {'ticker': 'IUSB', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _bil = {'ticker': 'BIL', 'initMarginReq': 0.0990, 'maintMarginReq': 0.0900}
        _voe = {'ticker': 'VOE', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _xlu = {'ticker': 'XLU', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _vteb = {'ticker': 'VTEB', 'initMarginReq': 0.0990, 'maintMarginReq': 0.0900}
        _pff = {'ticker': 'PFF', 'initMarginReq': 0.2750, 'maintMarginReq': 0.2500}
        _xly = {'ticker': 'XLY', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _schp = {'ticker': 'SCHP', 'initMarginReq': 0.0990, 'maintMarginReq': 0.0900}
        _vht = {'ticker': 'VHT', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _xlp = {'ticker': 'XLP', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _vgsh = {'ticker': 'VGSH', 'initMarginReq': 0.0990, 'maintMarginReq': 0.0900}
        _dfac = {'ticker': 'DFAC', 'initMarginReq': 0.2200, 'maintMarginReq': 0.2000}
        _vmbs = {'ticker': 'VMBS', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _scha = {'ticker': 'SCHA', 'initMarginReq': 0.1377, 'maintMarginReq': 0.1252}
        _schg = {'ticker': 'SCHG', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _xli = {'ticker': 'XLI', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _splg = {'ticker': 'SPLG', 'initMarginReq': 0.1074, 'maintMarginReq': 0.0977}
        _iws = {'ticker': 'IWS', 'initMarginReq': 0.1245, 'maintMarginReq': 0.1132}
        _vxf = {'ticker': 'VXF', 'initMarginReq': 0.1412, 'maintMarginReq': 0.1283}
        _tqqq = {'ticker': 'TQQQ', 'initMarginReq': 0.3953, 'maintMarginReq': 0.3594}
        _spyv = {'ticker': 'SPYV', 'initMarginReq': 0.1075, 'maintMarginReq': 0.0977}
        _hdv = {'ticker': 'HDV', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _hyg = {'ticker': 'HYG', 'initMarginReq': 0.2750, 'maintMarginReq': 0.2500}
        _iwn = {'ticker': 'IWN', 'initMarginReq': 0.1415, 'maintMarginReq': 0.1287}
        _vbk = {'ticker': 'VBK', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _spyg = {'ticker': 'SPYG', 'initMarginReq': 0.1329, 'maintMarginReq': 0.1208}
        _fvd = {'ticker': 'FVD', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _stip = {'ticker': 'STIP', 'initMarginReq': 0.0990, 'maintMarginReq': 0.0900}
        _biv = {'ticker': 'BIV', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _iwp = {'ticker': 'IWP', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _gslc = {'ticker': 'GSLC', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _iusv = {'ticker': 'IUSV', 'initMarginReq': 0.1065, 'maintMarginReq': 0.0968}
        _iusg = {'ticker': 'IUSG', 'initMarginReq': 0.1294, 'maintMarginReq': 0.1176}
        _mgk = {'ticker': 'MGK', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _iwv = {'ticker': 'IWV', 'initMarginReq': 0.1176, 'maintMarginReq': 0.1069}
        _mtum = {'ticker': 'MTUM', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _fndx = {'ticker': 'FNDX', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _iei = {'ticker': 'IEI', 'initMarginReq': 0.0990, 'maintMarginReq': 0.0900}
        _splv = {'ticker': 'SPLV', 'initMarginReq': 0.2200, 'maintMarginReq': 0.2000}
        _nobl = {'ticker': 'NOBL', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _vlue = {'ticker': 'VLUE', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _xlc = {'ticker': 'XLC', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _jepi = {'ticker': 'JEPI', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _schv = {'ticker': 'SCHV', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _vot = {'ticker': 'VOT', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _iwo = {'ticker': 'IWO', 'initMarginReq': 0.1398, 'maintMarginReq': 0.1270}
        _vfh = {'ticker': 'VFH', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _vde = {'ticker': 'VDE', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _schm = {'ticker': 'SCHM', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _vgit = {'ticker': 'VGIT', 'initMarginReq': 0.0990, 'maintMarginReq': 0.0900}
        _rdvy = {'ticker': 'RDVY', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _ijs = {'ticker': 'IJS', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _arkk = {'ticker': 'ARKK', 'initMarginReq': 0.2569, 'maintMarginReq': 0.2335}
        _scho = {'ticker': 'SCHO', 'initMarginReq': 0.0990, 'maintMarginReq': 0.0900}
        _spyd = {'ticker': 'SPYD', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _sub = {'ticker': 'SUB', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _jnk = {'ticker': 'JNK', 'initMarginReq': 0.2750, 'maintMarginReq': 0.2500}
        _ftcs = {'ticker': 'FTCS', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _oef = {'ticker': 'OEF', 'initMarginReq': 0.1099, 'maintMarginReq': 0.0999}
        _smh = {'ticker': 'SMH', 'initMarginReq': 0.1760, 'maintMarginReq': 0.1600}
        _soxx = {'ticker': 'SOXX', 'initMarginReq': 0.1807, 'maintMarginReq': 0.1643}
        _xlb = {'ticker': 'XLB', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _ushy = {'ticker': 'USHY', 'initMarginReq': 0.2750, 'maintMarginReq': 0.2500}
        _ijj = {'ticker': 'IJJ', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _schz = {'ticker': 'SCHZ', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _schr = {'ticker': 'SCHR', 'initMarginReq': 0.0990, 'maintMarginReq': 0.0900}
        _spsb = {'ticker': 'SPSB', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _ibb = {'ticker': 'IBB', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _amlp = {'ticker': 'AMLP', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _dfat = {'ticker': 'DFAT', 'initMarginReq': 0.2200, 'maintMarginReq': 0.2000}
        _iyw = {'ticker': 'IYW', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _ihi = {'ticker': 'IHI', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _ijk = {'ticker': 'IJK', 'initMarginReq': 0.1444, 'maintMarginReq': 0.1313}
        _fpe = {'ticker': 'FPE', 'initMarginReq': 0.2750, 'maintMarginReq': 0.2500}
        _vong = {'ticker': 'VONG', 'initMarginReq': 0.1290, 'maintMarginReq': 0.1173}
        _voog = {'ticker': 'VOOG', 'initMarginReq': 0.1266, 'maintMarginReq': 0.1151}
        _qyld = {'ticker': 'QYLD', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _moat = {'ticker': 'MOAT', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _cowz = {'ticker': 'COWZ', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _vonv = {'ticker': 'VONV', 'initMarginReq': 0.1101, 'maintMarginReq': 0.1001}
        _usig = {'ticker': 'USIG', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _dgrw = {'ticker': 'DGRW', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _vdc = {'ticker': 'VDC', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _icsh = {'ticker': 'ICSH', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _schh = {'ticker': 'SCHH', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _spab = {'ticker': 'SPAB', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _xbi = {'ticker': 'XBI', 'initMarginReq': 0.1832, 'maintMarginReq': 0.1665}
        _vpu = {'ticker': 'VPU', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _fnda = {'ticker': 'FNDA', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _esgv = {'ticker': 'ESGV', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _xop = {'ticker': 'XOP', 'initMarginReq': 0.2479, 'maintMarginReq': 0.2253}
        _prf = {'ticker': 'PRF', 'initMarginReq': 0.1136, 'maintMarginReq': 0.1033}
        _usfr = {'ticker': 'USFR', 'initMarginReq': 0.0990, 'maintMarginReq': 0.0900}
        _vtwo = {'ticker': 'VTWO', 'initMarginReq': 0.1373, 'maintMarginReq': 0.1248}
        _mgv = {'ticker': 'MGV', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _pgx = {'ticker': 'PGX', 'initMarginReq': 0.2750, 'maintMarginReq': 0.2500}
        _ftec = {'ticker': 'FTEC', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _dfus = {'ticker': 'DFUS', 'initMarginReq': 0.2200, 'maintMarginReq': 0.2000}
        _spib = {'ticker': 'SPIB', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _sptm = {'ticker': 'SPTM', 'initMarginReq': 0.1108, 'maintMarginReq': 0.1008}
        _istb = {'ticker': 'ISTB', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _cibr = {'ticker': 'CIBR', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _xlre = {'ticker': 'XLRE', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _sptl = {'ticker': 'SPTL', 'initMarginReq': 0.0990, 'maintMarginReq': 0.0900}
        _lmbs = {'ticker': 'LMBS', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _ijt = {'ticker': 'IJT', 'initMarginReq': 0.1365, 'maintMarginReq': 0.1241}
        _shyg = {'ticker': 'SHYG', 'initMarginReq': 0.2750, 'maintMarginReq': 0.2500}
        _spmd = {'ticker': 'SPMD', 'initMarginReq': 0.1371, 'maintMarginReq': 0.1246}
        _bkln = {'ticker': 'BKLN', 'initMarginReq': 0.2750, 'maintMarginReq': 0.2500}
        _shm = {'ticker': 'SHM', 'initMarginReq': 0.0990, 'maintMarginReq': 0.0900}
        _vcr = {'ticker': 'VCR', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _iyr = {'ticker': 'IYR', 'initMarginReq': 0.2932, 'maintMarginReq': 0.2665}
        _fdn = {'ticker': 'FDN', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _igv = {'ticker': 'IGV', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _ftsm = {'ticker': 'FTSM', 'initMarginReq': 0.2750, 'maintMarginReq': 0.2500}
        _iwy = {'ticker': 'IWY', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _pave = {'ticker': 'PAVE', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _near = {'ticker': 'NEAR', 'initMarginReq': 0.2750, 'maintMarginReq': 0.2500}
        _spsm = {'ticker': 'SPSM', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _hylb = {'ticker': 'HYLB', 'initMarginReq': 0.2750, 'maintMarginReq': 0.2500}
        _vclt = {'ticker': 'VCLT', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _dfas = {'ticker': 'DFAS', 'initMarginReq': 0.2200, 'maintMarginReq': 0.2000}
        _blv = {'ticker': 'BLV', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _qqqm = {'ticker': 'QQQM', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _slyv = {'ticker': 'SLYV', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _sphd = {'ticker': 'SPHD', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _cwb = {'ticker': 'CWB', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _fixd = {'ticker': 'FIXD', 'initMarginReq': 0.2750, 'maintMarginReq': 0.2500}
        _rpv = {'ticker': 'RPV', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _spmb = {'ticker': 'SPMB', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _tfi = {'ticker': 'TFI', 'initMarginReq': 0.0990, 'maintMarginReq': 0.0900}
        _ewu = {'ticker': 'EWU', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _sjnk = {'ticker': 'SJNK', 'initMarginReq': 0.2750, 'maintMarginReq': 0.2500}
        _oneq = {'ticker': 'ONEQ', 'initMarginReq': 0.1322, 'maintMarginReq': 0.1202}
        _igm = {'ticker': 'IGM', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _oih = {'ticker': 'OIH', 'initMarginReq': 0.3825, 'maintMarginReq': 0.3477}
        _skyy = {'ticker': 'SKYY', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _dsi = {'ticker': 'DSI', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _ita = {'ticker': 'ITA', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _mgc = {'ticker': 'MGC', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _kre = {'ticker': 'KRE', 'initMarginReq': 0.1714, 'maintMarginReq': 0.1518}
        _sphq = {'ticker': 'SPHQ', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _ftsl = {'ticker': 'FTSL', 'initMarginReq': 0.2750, 'maintMarginReq': 0.2500}
        _vaw = {'ticker': 'VAW', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _avuv = {'ticker': 'AVUV', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _qld = {'ticker': 'QLD', 'initMarginReq': 0.2744, 'maintMarginReq': 0.2494}
        _spti = {'ticker': 'SPTI', 'initMarginReq': 0.0990, 'maintMarginReq': 0.0900}
        _vglt = {'ticker': 'VGLT', 'initMarginReq': 0.0990, 'maintMarginReq': 0.0900}
        _vis = {'ticker': 'VIS', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1550}
        _susa = {'ticker': 'SUSA', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _ioo = {'ticker': 'IOO', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _ixj = {'ticker': 'IXJ', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _ixn = {'ticker': 'IXN', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _angl = {'ticker': 'ANGL', 'initMarginReq': 0.2750, 'maintMarginReq': 0.2500}
        _spts = {'ticker': 'SPTS', 'initMarginReq': 0.0990, 'maintMarginReq': 0.0900}
        _dln = {'ticker': 'DLN', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _sso = {'ticker': 'SSO', 'initMarginReq': 0.2252, 'maintMarginReq': 0.2047}
        _iye = {'ticker': 'IYE', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _bond = {'ticker': 'BOND', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _sqqq = {'ticker': 'SQQQ', 'initMarginReq': 0.4950, 'maintMarginReq': 0.4500}
        _hyd = {'ticker': 'HYD', 'initMarginReq': 0.2750, 'maintMarginReq': 0.2500}
        _susl = {'ticker': 'SUSL', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _don = {'ticker': 'DON', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _xt = {'ticker': 'XT', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _vox = {'ticker': 'VOX', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _reet = {'ticker': 'REET', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _fdl = {'ticker': 'FDL', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _xme = {'ticker': 'XME', 'initMarginReq': 0.1857, 'maintMarginReq': 0.1688}
        _jets = {'ticker': 'JETS', 'initMarginReq': 0.1935, 'maintMarginReq': 0.1759}
        _faln = {'ticker': 'FALN', 'initMarginReq': 0.2750, 'maintMarginReq': 0.2500}
        _voov = {'ticker': 'VOOV', 'initMarginReq': 0.1036, 'maintMarginReq': 0.0942}
        _sgov = {'ticker': 'SGOV', 'initMarginReq': 0.2750, 'maintMarginReq': 0.2500}
        _bsco = {'ticker': 'BSCO', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _ussg = {'ticker': 'USSG', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _spip = {'ticker': 'SPIP', 'initMarginReq': 0.0990, 'maintMarginReq': 0.0900}
        _nrgu = {'ticker': 'NRGU', 'initMarginReq': 0.7500, 'maintMarginReq': 0.9000}
        _iyh = {'ticker': 'IYH', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _fhlc = {'ticker': 'FHLC', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _vone = {'ticker': 'VONE', 'initMarginReq': 0.1127, 'maintMarginReq': 0.1025}
        _amj = {'ticker': 'AMJ', 'initMarginReq': 0.2500, 'maintMarginReq': 0.2500}
        _emlp = {'ticker': 'EMLP', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _vusb = {'ticker': 'VUSB', 'initMarginReq': 0.2750, 'maintMarginReq': 0.2500}
        _icf = {'ticker': 'ICF', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _upro = {'ticker': 'UPRO', 'initMarginReq': 0.3587, 'maintMarginReq': 0.3261}
        _spxl = {'ticker': 'SPXL', 'initMarginReq': 0.3528, 'maintMarginReq': 0.3207}
        _kbe = {'ticker': 'KBE', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _vnla = {'ticker': 'VNLA', 'initMarginReq': 0.2750, 'maintMarginReq': 0.2500}
        _ryt = {'ticker': 'RYT', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _jhmm = {'ticker': 'JHMM', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _arkg = {'ticker': 'ARKG', 'initMarginReq': 0.2268, 'maintMarginReq': 0.2061}
        _gvi = {'ticker': 'GVI', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _sh = {'ticker': 'SH', 'initMarginReq': 0.1163, 'maintMarginReq': 0.1053}
        _slqd = {'ticker': 'SLQD', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _rpg = {'ticker': 'RPG', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _totl = {'ticker': 'TOTL', 'initMarginReq': 0.2750, 'maintMarginReq': 0.2500}
        _pbus = {'ticker': 'PBUS', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _gbil = {'ticker': 'GBIL', 'initMarginReq': 0.0990, 'maintMarginReq': 0.0900}
        _fas = {'ticker': 'FAS', 'initMarginReq': 0.4950, 'maintMarginReq': 0.4500}
        _dfau = {'ticker': 'DFAU', 'initMarginReq': 0.2200, 'maintMarginReq': 0.2000}
        _avus = {'ticker': 'AVUS', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _tlh = {'ticker': 'TLH', 'initMarginReq': 0.0990, 'maintMarginReq': 0.0900}
        _usrt = {'ticker': 'USRT', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _slyg = {'ticker': 'SLYG', 'initMarginReq': 0.1369, 'maintMarginReq': 0.1245}
        _schk = {'ticker': 'SCHK', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _iyf = {'ticker': 'IYF', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _qcln = {'ticker': 'QCLN', 'initMarginReq': 0.1891, 'maintMarginReq': 0.1719}
        _omfl = {'ticker': 'OMFL', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _tdtt = {'ticker': 'TDTT', 'initMarginReq': 0.0990, 'maintMarginReq': 0.0900}
        _kbwb = {'ticker': 'KBWB', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _pffd = {'ticker': 'PFFD', 'initMarginReq': 0.2750, 'maintMarginReq': 0.2500}
        _xlg = {'ticker': 'XLG', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _fmb = {'ticker': 'FMB', 'initMarginReq': 0.0990, 'maintMarginReq': 0.0900}
        _icvt = {'ticker': 'ICVT', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _fxz = {'ticker': 'FXZ', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _bscm = {'ticker': 'BSCM', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _fxn = {'ticker': 'FXN', 'initMarginReq': 0.1727, 'maintMarginReq': 0.1570}
        _pza = {'ticker': 'PZA', 'initMarginReq': 0.0990, 'maintMarginReq': 0.0900}
        _aor = {'ticker': 'AOR', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _futy = {'ticker': 'FUTY', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _rwr = {'ticker': 'RWR', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _eagg = {'ticker': 'EAGG', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _cdc = {'ticker': 'CDC', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _vrp = {'ticker': 'VRP', 'initMarginReq': 0.2750, 'maintMarginReq': 0.2500}
        _prfz = {'ticker': 'PRFZ', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _tecl = {'ticker': 'TECL', 'initMarginReq': 0.4950, 'maintMarginReq': 0.4500}
        _ptlc = {'ticker': 'PTLC', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _qtec = {'ticker': 'QTEC', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _ifra = {'ticker': 'IFRA', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _cmf = {'ticker': 'CMF', 'initMarginReq': 0.0990, 'maintMarginReq': 0.0900}
        _des = {'ticker': 'DES', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _bab = {'ticker': 'BAB', 'initMarginReq': 0.0990, 'maintMarginReq': 0.0900}
        _hys = {'ticker': 'HYS', 'initMarginReq': 0.2750, 'maintMarginReq': 0.2500}
        _feny = {'ticker': 'FENY', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _hymb = {'ticker': 'HYMB', 'initMarginReq': 0.2750, 'maintMarginReq': 0.2500}
        _frel = {'ticker': 'FREL', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _iev = {'ticker': 'IEV', 'initMarginReq': 0.1092, 'maintMarginReq': 0.0992}
        _itm = {'ticker': 'ITM', 'initMarginReq': 0.0990, 'maintMarginReq': 0.0900}
        _tdiv = {'ticker': 'TDIV', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _vioo = {'ticker': 'VIOO', 'initMarginReq': 0.1379, 'maintMarginReq': 0.1254}
        _hyls = {'ticker': 'HYLS', 'initMarginReq': 0.2750, 'maintMarginReq': 0.2500}
        _sly = {'ticker': 'SLY', 'initMarginReq': 0.1343, 'maintMarginReq': 0.1221}
        _fez = {'ticker': 'FEZ', 'initMarginReq': 0.1233, 'maintMarginReq': 0.1121}
        _iyg = {'ticker': 'IYG', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1550}
        _hack = {'ticker': 'HACK', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _uup = {'ticker': 'UUP', 'initMarginReq': 0.2200, 'maintMarginReq': 0.2000}
        _komp = {'ticker': 'KOMP', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _ewg = {'ticker': 'EWG', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _ilcg = {'ticker': 'ILCG', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _pho = {'ticker': 'PHO', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _xyld = {'ticker': 'XYLD', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _qdf = {'ticker': 'QDF', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _fxr = {'ticker': 'FXR', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _ibdo = {'ticker': 'IBDO', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _fncl = {'ticker': 'FNCL', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _aom = {'ticker': 'AOM', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _ibdp = {'ticker': 'IBDP', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _stpz = {'ticker': 'STPZ', 'initMarginReq': 0.0990, 'maintMarginReq': 0.0900}
        _arkw = {'ticker': 'ARKW', 'initMarginReq': 0.2426, 'maintMarginReq': 0.2205}
        _ivol = {'ticker': 'IVOL', 'initMarginReq': 0.2750, 'maintMarginReq': 0.2500}
        _mdyg = {'ticker': 'MDYG', 'initMarginReq': 0.1407, 'maintMarginReq': 0.1279}
        _iyy = {'ticker': 'IYY', 'initMarginReq': 0.1169, 'maintMarginReq': 0.1063}
        _mdyv = {'ticker': 'MDYV', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _ihf = {'ticker': 'IHF', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _bbmc = {'ticker': 'BBMC', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _tilt = {'ticker': 'TILT', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _iwx = {'ticker': 'IWX', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500100100}
        _itb = {'ticker': 'ITB', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _bscp = {'ticker': 'BSCP', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _esml = {'ticker': 'ESML', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _ibdn = {'ticker': 'IBDN', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _iglb = {'ticker': 'IGLB', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _usmc = {'ticker': 'USMC', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _divo = {'ticker': 'DIVO', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _tipx = {'ticker': 'TIPX', 'initMarginReq': 0.0990, 'maintMarginReq': 0.0900}
        _nulv = {'ticker': 'NULV', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _ewl = {'ticker': 'EWL', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _ivoo = {'ticker': 'IVOO', 'initMarginReq': 0.1332, 'maintMarginReq': 0.1211}
        _hndl = {'ticker': 'HNDL', 'initMarginReq': 0.1640, 'maintMarginReq': 0.1491}
        _rwl = {'ticker': 'RWL', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _tbt = {'ticker': 'TBT', 'initMarginReq': 0.1980, 'maintMarginReq': 0.1800}
        _fxh = {'ticker': 'FXH', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _ldur = {'ticker': 'LDUR', 'initMarginReq': 0.2750, 'maintMarginReq': 0.2500}
        _ftxn = {'ticker': 'FTXN', 'initMarginReq': 0.1657, 'maintMarginReq': 0.1507}
        _xar = {'ticker': 'XAR', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _eufn = {'ticker': 'EUFN', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _iyk = {'ticker': 'IYK', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _iyj = {'ticker': 'IYJ', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _lctu = {'ticker': 'LCTU', 'initMarginReq': 0.2200, 'maintMarginReq': 0.2000}
        _ppa = {'ticker': 'PPA', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _pgf = {'ticker': 'PGF', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _pej = {'ticker': 'PEJ', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _pkw = {'ticker': 'PKW', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _mlpa = {'ticker': 'MLPA', 'initMarginReq': 0.2258, 'maintMarginReq': 0.2052}
        _tna = {'ticker': 'TNA', 'initMarginReq': 0.3964, 'maintMarginReq': 0.3603}
        _ksa = {'ticker': 'KSA', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _sdog = {'ticker': 'SDOG', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _pey = {'ticker': 'PEY', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _tflo = {'ticker': 'TFLO', 'initMarginReq': 0.0990, 'maintMarginReq': 0.0900}
        _fbt = {'ticker': 'FBT', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _viov = {'ticker': 'VIOV', 'initMarginReq': 0.1687, 'maintMarginReq': 0.1533}
        _fxo = {'ticker': 'FXO', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _ryld = {'ticker': 'RYLD', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _fdvv = {'ticker': 'FDVV', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _srvr = {'ticker': 'SRVR', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _pdp = {'ticker': 'PDP', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _spyx = {'ticker': 'SPYX', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _lqdh = {'ticker': 'LQDH', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _gush = {'ticker': 'GUSH', 'initMarginReq': 0.5651, 'maintMarginReq': 0.5137}
        _fta = {'ticker': 'FTA', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _arkq = {'ticker': 'ARKQ', 'initMarginReq': 0.1751, 'maintMarginReq': 0.1591}
        _uitb = {'ticker': 'UITB', 'initMarginReq': 0.2795, 'maintMarginReq': 0.2541}
        _xmlv = {'ticker': 'XMLV', 'initMarginReq': 0.1713, 'maintMarginReq': 0.1557}
        _dhs = {'ticker': 'DHS', 'initMarginReq': 0.1713, 'maintMarginReq': 0.1557}
        _ibdq = {'ticker': 'IBDQ', 'initMarginReq': 0.1663, 'maintMarginReq': 0.1009}
        _bbre = {'ticker': 'BBRE', 'initMarginReq': 0.1739, 'maintMarginReq': 0.1581}
        _fiw = {'ticker': 'FIW', 'initMarginReq': 0.1714, 'maintMarginReq': 0.1558}
        _qlta = {'ticker': 'QLTA', 'initMarginReq': 0.1684, 'maintMarginReq': 0.1531}
        _ige = {'ticker': 'IGE', 'initMarginReq': 0.1739, 'maintMarginReq': 0.1581}
        _vthr = {'ticker': 'VTHR', 'initMarginReq': 0.1317, 'maintMarginReq': 0.1198}
        _fxl = {'ticker': 'FXL', 'initMarginReq': 0.1735, 'maintMarginReq': 0.1578}
        _bug = {'ticker': 'BUG', 'initMarginReq': 0.1742, 'maintMarginReq': 0.1584}
        _ieo = {'ticker': 'IEO', 'initMarginReq': 0.1825, 'maintMarginReq': 0.1659}
        _edv = {'ticker': 'EDV', 'initMarginReq': 0.1031, 'maintMarginReq': 0.0937}
        _fpx = {'ticker': 'FPX', 'initMarginReq': 0.1748, 'maintMarginReq': 0.1589}
        _fdis = {'ticker': 'FDIS', 'initMarginReq': 0.1735, 'maintMarginReq': 0.1577}
        _sds = {'ticker': 'SDS', 'initMarginReq': 0.2222, 'maintMarginReq': 0.2020}
        _xsd = {'ticker': 'XSD', 'initMarginReq': 0.2133, 'maintMarginReq': 0.1939}
        _fex = {'ticker': 'FEX', 'initMarginReq': 0.1723, 'maintMarginReq': 0.1566}
        _psq = {'ticker': 'PSQ', 'initMarginReq': 0.1373, 'maintMarginReq': 0.1248}
        _xhb = {'ticker': 'XHB', 'initMarginReq': 0.1739, 'maintMarginReq': 0.1581}
        _lrgf = {'ticker': 'LRGF', 'initMarginReq': 0.1719, 'maintMarginReq': 0.1563}
        _bbus = {'ticker': 'BBUS', 'initMarginReq': 0.1718, 'maintMarginReq': 0.1561}
        _regl = {'ticker': 'REGL', 'initMarginReq': 0.1703, 'maintMarginReq': 0.1548}
        _iyt = {'ticker': 'IYT', 'initMarginReq': 0.1707, 'maintMarginReq': 0.1552}
        _fcg = {'ticker': 'FCG', 'initMarginReq': 0.1978, 'maintMarginReq': 0.1798}
        _dtd = {'ticker': 'DTD', 'initMarginReq': 0.1708, 'maintMarginReq': 0.1553}
        _hydw = {'ticker': 'HYDW', 'initMarginReq': 0.2833, 'maintMarginReq': 0.2575}
        _psk = {'ticker': 'PSK', 'initMarginReq': 0.2845, 'maintMarginReq': 0.2587}
        _fsta = {'ticker': 'FSTA', 'initMarginReq': 0.1689, 'maintMarginReq': 0.1536}
        _imcg = {'ticker': 'IMCG', 'initMarginReq': 0.1735, 'maintMarginReq': 0.1577}
        _mlpx = {'ticker': 'MLPX', 'initMarginReq': 0.1948, 'maintMarginReq': 0.1771}
        _qqew = {'ticker': 'QQEW', 'initMarginReq': 0.1472, 'maintMarginReq': 0.1338}
        _pbw = {'ticker': 'PBW', 'initMarginReq': 0.2175, 'maintMarginReq': 0.1977}
        _idu = {'ticker': 'IDU', 'initMarginReq': 0.1729, 'maintMarginReq': 0.1572}
        _bscq = {'ticker': 'BSCQ', 'initMarginReq': 0.1673, 'maintMarginReq': 0.1521}
        _aggy = {'ticker': 'AGGY', 'initMarginReq': 0.1682, 'maintMarginReq': 0.1529}
        _flql = {'ticker': 'FLQL', 'initMarginReq': 0.1714, 'maintMarginReq': 0.1558}
        _nusc = {'ticker': 'NUSC', 'initMarginReq': 0.1741, 'maintMarginReq': 0.1582}
        _smlf = {'ticker': 'SMLF', 'initMarginReq': 0.1726, 'maintMarginReq': 0.1569}
        _pfxf = {'ticker': 'PFXF', 'initMarginReq': 0.2854, 'maintMarginReq': 0.2594}
        _htrb = {'ticker': 'HTRB', 'initMarginReq': 0.1682, 'maintMarginReq': 0.1529}
        _fnx = {'ticker': 'FNX', 'initMarginReq': 0.1737, 'maintMarginReq': 0.1579}
        _kxi = {'ticker': 'KXI', 'initMarginReq': 0.1686, 'maintMarginReq': 0.1533}
        _iwc = {'ticker': 'IWC', 'initMarginReq': 0.1740, 'maintMarginReq': 0.1582}
        _ibdr = {'ticker': 'IBDR', 'initMarginReq': 0.1672, 'maintMarginReq': 0.1520}
        _rez = {'ticker': 'REZ', 'initMarginReq': 0.1731, 'maintMarginReq': 0.1574}
        _sect = {'ticker': 'SECT', 'initMarginReq': 0.1722, 'maintMarginReq': 0.1565}
        _cfo = {'ticker': 'CFO', 'initMarginReq': 0.1716, 'maintMarginReq': 0.1560}
        _iat = {'ticker': 'IAT', 'initMarginReq': 0.1754, 'maintMarginReq': 0.1594}
        _calf = {'ticker': 'CALF', 'initMarginReq': 0.1768, 'maintMarginReq': 0.1607}
        _iwl = {'ticker': 'IWL', 'initMarginReq': 0.1715, 'maintMarginReq': 0.1559}
        _spgp = {'ticker': 'SPGP', 'initMarginReq': 0.1710, 'maintMarginReq': 0.1554}
        _ftc = {'ticker': 'FTC', 'initMarginReq': 0.1726, 'maintMarginReq': 0.1569}
        _sdvy = {'ticker': 'SDVY', 'initMarginReq': 0.1724, 'maintMarginReq': 0.1568}
        _xmmo = {'ticker': 'XMMO', 'initMarginReq': 0.1729, 'maintMarginReq': 0.1572}
        _susc = {'ticker': 'SUSC', 'initMarginReq': 0.1683, 'maintMarginReq': 0.1530}
        _uvxy = {'ticker': 'UVXY', 'initMarginReq': 0.2242, 'maintMarginReq': 0.2038}
        _vtwv = {'ticker': 'VTWV', 'initMarginReq': 0.1502, 'maintMarginReq': 0.1365}
        _aok = {'ticker': 'AOK', 'initMarginReq': 0.1687, 'maintMarginReq': 0.1534}
        _ryh = {'ticker': 'RYH', 'initMarginReq': 0.1711, 'maintMarginReq': 0.1555}
        _hygv = {'ticker': 'HYGV', 'initMarginReq': 0.2837, 'maintMarginReq': 0.2579}
        _drsk = {'ticker': 'DRSK', 'initMarginReq': 0.1674, 'maintMarginReq': 0.1522}
        _qus = {'ticker': 'QUS', 'initMarginReq': 0.1710, 'maintMarginReq': 0.1554}
        _gto = {'ticker': 'GTO', 'initMarginReq': 0.1683, 'maintMarginReq': 0.1530}
        _smdv = {'ticker': 'SMDV', 'initMarginReq': 0.1701, 'maintMarginReq': 0.1546}
        _qqqj = {'ticker': 'QQQJ', 'initMarginReq': 0.2331, 'maintMarginReq': 0.2119}
        _fyx = {'ticker': 'FYX', 'initMarginReq': 0.1735, 'maintMarginReq': 0.1578}
        _ftxg = {'ticker': 'FTXG', 'initMarginReq': 0.1696, 'maintMarginReq': 0.1542}
        _rem = {'ticker': 'REM', 'initMarginReq': 0.1820, 'maintMarginReq': 0.1654}
        _vfva = {'ticker': 'VFVA', 'initMarginReq': 0.1732, 'maintMarginReq': 0.1574}
        _rdiv = {'ticker': 'RDIV', 'initMarginReq': 0.1706, 'maintMarginReq': 0.1551}
        _rwj = {'ticker': 'RWJ', 'initMarginReq': 0.1736, 'maintMarginReq': 0.1578}
        _phb = {'ticker': 'PHB', 'initMarginReq': 0.2828, 'maintMarginReq': 0.2570}
        _oney = {'ticker': 'ONEY', 'initMarginReq': 0.1716, 'maintMarginReq': 0.1560}
        _ivov = {'ticker': 'IVOV', 'initMarginReq': 0.1728, 'maintMarginReq': 0.1571}
        _eusb = {'ticker': 'EUSB', 'initMarginReq': 0.2800, 'maintMarginReq': 0.2546}
        _pwv = {'ticker': 'PWV', 'initMarginReq': 0.1708, 'maintMarginReq': 0.1553}
        _nulg = {'ticker': 'NULG', 'initMarginReq': 0.1727, 'maintMarginReq': 0.1570}
        _erx = {'ticker': 'ERX', 'initMarginReq': 0.5213, 'maintMarginReq': 0.4739}
        _ilcb = {'ticker': 'ILCB', 'initMarginReq': 0.1723, 'maintMarginReq': 0.1567}
        _tdtf = {'ticker': 'TDTF', 'initMarginReq': 0.1675, 'maintMarginReq': 0.1522}
        _ilcv = {'ticker': 'ILCV', 'initMarginReq': 0.1708, 'maintMarginReq': 0.1553}
        _snpe = {'ticker': 'SNPE', 'initMarginReq': 0.1265, 'maintMarginReq': 0.1150}
        _imcb = {'ticker': 'IMCB', 'initMarginReq': 0.1729, 'maintMarginReq': 0.1571}
        _muni = {'ticker': 'MUNI', 'initMarginReq': 0.1003, 'maintMarginReq': 0.0912}
        _labu = {'ticker': 'LABU', 'initMarginReq': 0.6920, 'maintMarginReq': 0.6291}
        _ezm = {'ticker': 'EZM', 'initMarginReq': 0.1729, 'maintMarginReq': 0.1572}
        _jhml = {'ticker': 'JHML', 'initMarginReq': 0.1719, 'maintMarginReq': 0.1562}
        _ousa = {'ticker': 'OUSA', 'initMarginReq': 0.1693, 'maintMarginReq': 0.1539}
        _fngu = {'ticker': 'FNGU', 'initMarginReq': 0.7500, 'maintMarginReq': 0.7500}
        _ntsx = {'ticker': 'NTSX', 'initMarginReq': 0.1746, 'maintMarginReq': 0.1587}
        _iyc = {'ticker': 'IYC', 'initMarginReq': 0.1729, 'maintMarginReq': 0.1572}
        _xslv = {'ticker': 'XSLV', 'initMarginReq': 0.1712, 'maintMarginReq': 0.1556}
        _jmbs = {'ticker': 'JMBS', 'initMarginReq': 0.1678, 'maintMarginReq': 0.1526}
        _pcef = {'ticker': 'PCEF', 'initMarginReq': 0.1716, 'maintMarginReq': 0.1560}
        _ewq = {'ticker': 'EWQ', 'initMarginReq': 0.1713, 'maintMarginReq': 0.1557}
        _cltl = {'ticker': 'CLTL', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _eqal = {'ticker': 'EQAL', 'initMarginReq': 0.1731, 'maintMarginReq': 0.1574}
        _qvml = {'ticker': 'QVML', 'initMarginReq': 0.2289, 'maintMarginReq': 0.2081}
        _dstl = {'ticker': 'DSTL', 'initMarginReq': 0.1712, 'maintMarginReq': 0.1557}
        _smmv = {'ticker': 'SMMV', 'initMarginReq': 0.1702, 'maintMarginReq': 0.1548}
        _dial = {'ticker': 'DIAL', 'initMarginReq': 0.2823, 'maintMarginReq': 0.2566}
        _ibds = {'ticker': 'IBDS', 'initMarginReq': 0.1675, 'maintMarginReq': 0.1522}
        _ivog = {'ticker': 'IVOG', 'initMarginReq': 0.1483, 'maintMarginReq': 0.1348}
        _qai = {'ticker': 'QAI', 'initMarginReq': 0.1688, 'maintMarginReq': 0.1534}
        _ptbd = {'ticker': 'PTBD', 'initMarginReq': 0.2835, 'maintMarginReq': 0.2577}
        _ipay = {'ticker': 'IPAY', 'initMarginReq': 0.1784, 'maintMarginReq': 0.1622}
        _qqqe = {'ticker': 'QQQE', 'initMarginReq': 0.1460, 'maintMarginReq': 0.1327}
        _spxu = {'ticker': 'SPXU', 'initMarginReq': 0.3950, 'maintMarginReq': 0.3591}
        _fidu = {'ticker': 'FIDU', 'initMarginReq': 0.1708, 'maintMarginReq': 0.1553}
        _div = {'ticker': 'DIV', 'initMarginReq': 0.1728, 'maintMarginReq': 0.1571}
        _rye = {'ticker': 'RYE', 'initMarginReq': 0.1780, 'maintMarginReq': 0.1618}
        _cmbs = {'ticker': 'CMBS', 'initMarginReq': 0.2802, 'maintMarginReq': 0.2547}
        _xsvm = {'ticker': 'XSVM', 'initMarginReq': 0.1742, 'maintMarginReq': 0.1584}
        _pfm = {'ticker': 'PFM', 'initMarginReq': 0.1700, 'maintMarginReq': 0.1546}
        _clou = {'ticker': 'CLOU', 'initMarginReq': 0.1763, 'maintMarginReq': 0.1603}
        _altl = {'ticker': 'ALTL', 'initMarginReq': 0.2266, 'maintMarginReq': 0.2060}
        _fxg = {'ticker': 'FXG', 'initMarginReq': 0.1693, 'maintMarginReq': 0.1539}
        _wcld = {'ticker': 'WCLD', 'initMarginReq': 0.2184, 'maintMarginReq': 0.1985}
        _bsjn = {'ticker': 'BSJN', 'initMarginReq': 0.2805, 'maintMarginReq': 0.2550}
        _ptnq = {'ticker': 'PTNQ', 'initMarginReq': 0.1689, 'maintMarginReq': 0.1535}
        _sphy = {'ticker': 'SPHY', 'initMarginReq': 0.2851, 'maintMarginReq': 0.2592}
        _bsjm = {'ticker': 'BSJM', 'initMarginReq': 0.2776, 'maintMarginReq': 0.2524}
        _psc = {'ticker': 'PSC', 'initMarginReq': 0.1736, 'maintMarginReq': 0.1579}
        _nusi = {'ticker': 'NUSI', 'initMarginReq': 0.1704, 'maintMarginReq': 0.1549}
        _vrig = {'ticker': 'VRIG', 'initMarginReq': 0.1653, 'maintMarginReq': 0.1502}
        _udow = {'ticker': 'UDOW', 'initMarginReq': 0.3616, 'maintMarginReq': 0.3287}
        _gsew = {'ticker': 'GSEW', 'initMarginReq': 0.1726, 'maintMarginReq': 0.1569}
        _gigb = {'ticker': 'GIGB', 'initMarginReq': 0.1684, 'maintMarginReq': 0.1531}
        _ighg = {'ticker': 'IGHG', 'initMarginReq': 0.1661, 'maintMarginReq': 0.1510}
        _uyg = {'ticker': 'UYG', 'initMarginReq': 0.3568, 'maintMarginReq': 0.3243}
        _lglv = {'ticker': 'LGLV', 'initMarginReq': 0.1699, 'maintMarginReq': 0.1544}
        _eps = {'ticker': 'EPS', 'initMarginReq': 0.1716, 'maintMarginReq': 0.1560}
        _ltpz = {'ticker': 'LTPZ', 'initMarginReq': 0.1029, 'maintMarginReq': 0.0935}
        _krma = {'ticker': 'KRMA', 'initMarginReq': 0.1720, 'maintMarginReq': 0.1564}
        _aces = {'ticker': 'ACES', 'initMarginReq': 0.1867, 'maintMarginReq': 0.1697}
        _tbf = {'ticker': 'TBF', 'initMarginReq': 0.0961, 'maintMarginReq': 0.0873}
        _fdrr = {'ticker': 'FDRR', 'initMarginReq': 0.1706, 'maintMarginReq': 0.1551}
        _psi = {'ticker': 'PSI', 'initMarginReq': 0.2019, 'maintMarginReq': 0.1835}
        _agz = {'ticker': 'AGZ', 'initMarginReq': 0.1670, 'maintMarginReq': 0.1519}
        _lvhd = {'ticker': 'LVHD', 'initMarginReq': 0.1706, 'maintMarginReq': 0.1551}
        _sphb = {'ticker': 'SPHB', 'initMarginReq': 0.1982, 'maintMarginReq': 0.1801}
        _ees = {'ticker': 'EES', 'initMarginReq': 0.1725, 'maintMarginReq': 0.1569}
        _jval = {'ticker': 'JVAL', 'initMarginReq': 0.1721, 'maintMarginReq': 0.1564}
        _gsus = {'ticker': 'GSUS', 'initMarginReq': 0.1717, 'maintMarginReq': 0.1561}
        _vtwg = {'ticker': 'VTWG', 'initMarginReq': 0.1604, 'maintMarginReq': 0.1458}
        _xtn = {'ticker': 'XTN', 'initMarginReq': 0.1740, 'maintMarginReq': 0.1582}
        _pwb = {'ticker': 'PWB', 'initMarginReq': 0.1730, 'maintMarginReq': 0.1572}
        _bizd = {'ticker': 'BIZD', 'initMarginReq': 0.1739, 'maintMarginReq': 0.1581}
        _corp = {'ticker': 'CORP', 'initMarginReq': 0.1681, 'maintMarginReq': 0.1528}
        _tpyp = {'ticker': 'TPYP', 'initMarginReq': 0.1733, 'maintMarginReq': 0.1575}
        _splb = {'ticker': 'SPLB', 'initMarginReq': 0.1704, 'maintMarginReq': 0.1549}
        _fcom = {'ticker': 'FCOM', 'initMarginReq': 0.1734, 'maintMarginReq': 0.1577}
        _rhs = {'ticker': 'RHS', 'initMarginReq': 0.1689, 'maintMarginReq': 0.1536}
        _cfa = {'ticker': 'CFA', 'initMarginReq': 0.1716, 'maintMarginReq': 0.1560}
        _usxf = {'ticker': 'USXF', 'initMarginReq': 0.1718, 'maintMarginReq': 0.1561}
        _onev = {'ticker': 'ONEV', 'initMarginReq': 0.1708, 'maintMarginReq': 0.1553}
        _tmv = {'ticker': 'TMV', 'initMarginReq': 0.2901, 'maintMarginReq': 0.2638}
        _pwz = {'ticker': 'PWZ', 'initMarginReq': 0.1689, 'maintMarginReq': 0.1535}
        _syld = {'ticker': 'SYLD', 'initMarginReq': 0.5000, 'maintMarginReq': 0.5000}
        _ihak = {'ticker': 'IHAK', 'initMarginReq': 0.1727, 'maintMarginReq': 0.1570}
        _pjan = {'ticker': 'PJAN', 'initMarginReq': 0.1690, 'maintMarginReq': 0.1536}
        _vtc = {'ticker': 'VTC', 'initMarginReq': 0.1683, 'maintMarginReq': 0.1530}
        _cath = {'ticker': 'CATH', 'initMarginReq': 0.1717, 'maintMarginReq': 0.1561}
        _ewd = {'ticker': 'EWD', 'initMarginReq': 0.1710, 'maintMarginReq': 0.1554}
        _pnqi = {'ticker': 'PNQI', 'initMarginReq': 0.1759, 'maintMarginReq': 0.1599}
        _pffa = {'ticker': 'PFFA', 'initMarginReq': 0.2882, 'maintMarginReq': 0.2820}
        _rtm = {'ticker': 'RTM', 'initMarginReq': 0.1719, 'maintMarginReq': 0.1563}
        _rom = {'ticker': 'ROM', 'initMarginReq': 0.3647, 'maintMarginReq': 0.3315}
        _fmat = {'ticker': 'FMAT', 'initMarginReq': 0.1723, 'maintMarginReq': 0.1567}
        _mna = {'ticker': 'MNA', 'initMarginReq': 0.1676, 'maintMarginReq': 0.1524}
        _smmu = {'ticker': 'SMMU', 'initMarginReq': 0.0995, 'maintMarginReq': 0.0904}
        _vxx = {'ticker': 'VXX', 'initMarginReq': 0.1624, 'maintMarginReq': 0.1476}
        _nyf = {'ticker': 'NYF', 'initMarginReq': 0.1011, 'maintMarginReq': 0.0919}
        _jpus = {'ticker': 'JPUS', 'initMarginReq': 0.1718, 'maintMarginReq': 0.1562}
        _dbeu = {'ticker': 'DBEU', 'initMarginReq': 0.1122, 'maintMarginReq': 0.1020}
        _kng = {'ticker': 'KNG', 'initMarginReq': 1.0000, 'maintMarginReq': 1.0000}
        _fval = {'ticker': 'FVAL', 'initMarginReq': 0.1724, 'maintMarginReq': 0.1567}
        _bbsc = {'ticker': 'BBSC', 'initMarginReq': 0.2319, 'maintMarginReq': 0.2108}
        _viog = {'ticker': 'VIOG', 'initMarginReq': 0.1517, 'maintMarginReq': 0.1379}
        _imcv = {'ticker': 'IMCV', 'initMarginReq': 0.1720, 'maintMarginReq': 0.1564}
        _ftls = {'ticker': 'FTLS', 'initMarginReq': 0.1688, 'maintMarginReq': 0.1534}
        _ewp = {'ticker': 'EWP', 'initMarginReq': 0.1704, 'maintMarginReq': 0.1549}
        _spxs = {'ticker': 'SPXS', 'initMarginReq': 0.4197, 'maintMarginReq': 0.3816}
        _vuse = {'ticker': 'VUSE', 'initMarginReq': 0.1729, 'maintMarginReq': 0.1572}
        _bsjo = {'ticker': 'BSJO', 'initMarginReq': 0.2825, 'maintMarginReq': 0.2568}
        _spd = {'ticker': 'SPD', 'initMarginReq': 0.2222, 'maintMarginReq': 0.2020}
        _ryf = {'ticker': 'RYF', 'initMarginReq': 0.1705, 'maintMarginReq': 0.1550}
        _bklc = {'ticker': 'BKLC', 'initMarginReq': 0.1719, 'maintMarginReq': 0.1563}
        _mdiv = {'ticker': 'MDIV', 'initMarginReq': 0.1729, 'maintMarginReq': 0.1572}
        _csm = {'ticker': 'CSM', 'initMarginReq': 1.0000, 'maintMarginReq': 1.0000}
        _efiv = {'ticker': 'EFIV', 'initMarginReq': 0.1714, 'maintMarginReq': 0.1558}
        _plw = {'ticker': 'PLW', 'initMarginReq': 0.1011, 'maintMarginReq': 0.0919}
        _swan = {'ticker': 'SWAN', 'initMarginReq': 0.1696, 'maintMarginReq': 0.1541}
        _gsst = {'ticker': 'GSST', 'initMarginReq': 0.2754, 'maintMarginReq': 0.2503}
        _ibdt = {'ticker': 'IBDT', 'initMarginReq': 0.1679, 'maintMarginReq': 0.1526}
        _kie = {'ticker': 'KIE', 'initMarginReq': 0.1702, 'maintMarginReq': 0.1547}
        _fxd = {'ticker': 'FXD', 'initMarginReq': 0.1740, 'maintMarginReq': 0.1581}
        _mj = {'ticker': 'MJ', 'initMarginReq': 0.2026, 'maintMarginReq': 0.1841}
        _ssus = {'ticker': 'SSUS', 'initMarginReq': 0.1680, 'maintMarginReq': 0.1527}
        _aivl = {'ticker': 'AIVL', 'initMarginReq': 0.1707, 'maintMarginReq': 0.1552}
        _acio = {'ticker': 'ACIO', 'initMarginReq': 0.1672, 'maintMarginReq': 0.1520}
        _bscr = {'ticker': 'BSCR', 'initMarginReq': 0.1675, 'maintMarginReq': 0.1523}
        _ptmc = {'ticker': 'PTMC', 'initMarginReq': 0.1649, 'maintMarginReq': 0.1499}
        _pmay = {'ticker': 'PMAY', 'initMarginReq': 0.1694, 'maintMarginReq': 0.1540}
        _cape = {'ticker': 'CAPE', 'initMarginReq': 0.2298, 'maintMarginReq': 0.2098}
        _tail = {'ticker': 'TAIL', 'initMarginReq': 0.2675, 'maintMarginReq': 0.2435}
        _fndb = {'ticker': 'FNDB', 'initMarginReq': 0.1717, 'maintMarginReq': 0.1560}
        _rwm = {'ticker': 'RWM', 'initMarginReq': 0.1427, 'maintMarginReq': 0.1298}
        _xntk = {'ticker': 'XNTK', 'initMarginReq': 0.1783, 'maintMarginReq': 0.1621}
        _iai = {'ticker': 'IAI', 'initMarginReq': 0.1700, 'maintMarginReq': 0.1545}
        _bufd = {'ticker': 'BUFD', 'initMarginReq': 0.2233, 'maintMarginReq': 0.2030}
        _svxy = {'ticker': 'SVXY', 'initMarginReq': 0.4139, 'maintMarginReq': 0.3763}
        _bbh = {'ticker': 'BBH', 'initMarginReq': 0.1723, 'maintMarginReq': 0.1566}
        _ihe = {'ticker': 'IHE', 'initMarginReq': 0.1703, 'maintMarginReq': 0.1548}
        _gssc = {'ticker': 'GSSC', 'initMarginReq': 0.1727, 'maintMarginReq': 0.1570}
        _eusa = {'ticker': 'EUSA', 'initMarginReq': 0.1730, 'maintMarginReq': 0.1573}
        _kbwd = {'ticker': 'KBWD', 'initMarginReq': 0.1771, 'maintMarginReq': 0.1610}
        _fdlo = {'ticker': 'FDLO', 'initMarginReq': 0.1706, 'maintMarginReq': 0.1551}
        _ibmk = {'ticker': 'IBMK', 'initMarginReq': 0.1653, 'maintMarginReq': 0.1502}
        _tmfc = {'ticker': 'TMFC', 'initMarginReq': 0.1721, 'maintMarginReq': 0.1564}
        _iqsu = {'ticker': 'IQSU', 'initMarginReq': 0.1717, 'maintMarginReq': 0.1561}
        _smmd = {'ticker': 'SMMD', 'initMarginReq': 0.1733, 'maintMarginReq': 0.1575}
        _zroz = {'ticker': 'ZROZ', 'initMarginReq': 0.1032, 'maintMarginReq': 0.0938}
        _ibml = {'ticker': 'IBML', 'initMarginReq': 0.2762, 'maintMarginReq': 0.2511}
        _gbf = {'ticker': 'GBF', 'initMarginReq': 0.1679, 'maintMarginReq': 0.1526}
        _shyd = {'ticker': 'SHYD', 'initMarginReq': 0.2800, 'maintMarginReq': 0.2545}
        _fctr = {'ticker': 'FCTR', 'initMarginReq': 0.1720, 'maintMarginReq': 0.1564}
        _xhe = {'ticker': 'XHE', 'initMarginReq': 0.1731, 'maintMarginReq': 0.1574}
        _ttt = {'ticker': 'TTT', 'initMarginReq': 0.2720, 'maintMarginReq': 0.2472}
        _psct = {'ticker': 'PSCT', 'initMarginReq': 0.1731, 'maintMarginReq': 0.1574}
        _schi = {'ticker': 'SCHI', 'initMarginReq': 0.2796, 'maintMarginReq': 0.2542}
        _iez = {'ticker': 'IEZ', 'initMarginReq': 0.2260, 'maintMarginReq': 0.2054}
        _iyz = {'ticker': 'IYZ', 'initMarginReq': 0.1715, 'maintMarginReq': 0.1559}
        _flgv = {'ticker': 'FLGV', 'initMarginReq': 0.1674, 'maintMarginReq': 0.1522}
        _ryu = {'ticker': 'RYU', 'initMarginReq': 0.1734, 'maintMarginReq': 0.1577}
        _rous = {'ticker': 'ROUS', 'initMarginReq': 0.1710, 'maintMarginReq': 0.1555}
        _fxu = {'ticker': 'FXU', 'initMarginReq': 0.1734, 'maintMarginReq': 0.1576}
        _dwas = {'ticker': 'DWAS', 'initMarginReq': 0.1787, 'maintMarginReq': 0.1624}
        _qdef = {'ticker': 'QDEF', 'initMarginReq': 0.1702, 'maintMarginReq': 0.1547}
        _ddm = {'ticker': 'DDM', 'initMarginReq': 0.2336, 'maintMarginReq': 0.2124}
        _iscv = {'ticker': 'ISCV', 'initMarginReq': 0.1732, 'maintMarginReq': 0.1574}
        _rgi = {'ticker': 'RGI', 'initMarginReq': 0.1712, 'maintMarginReq': 0.1556}
        _ig = {'ticker': 'IG', 'initMarginReq': 0.1687, 'maintMarginReq': 0.1533}
        _tza = {'ticker': 'TZA', 'initMarginReq': 0.4766, 'maintMarginReq': 0.4333}
        _pxe = {'ticker': 'PXE', 'initMarginReq': 0.1882, 'maintMarginReq': 0.1771}
        _qid = {'ticker': 'QID', 'initMarginReq': 0.3326, 'maintMarginReq': 0.3024}
        _jqua = {'ticker': 'JQUA', 'initMarginReq': 0.1712, 'maintMarginReq': 0.1556}
        _xes = {'ticker': 'XES', 'initMarginReq': 0.3868, 'maintMarginReq': 0.3516}
        _sfy = {'ticker': 'SFY', 'initMarginReq': 0.1725, 'maintMarginReq': 0.1568}
        _bsjp = {'ticker': 'BSJP', 'initMarginReq': 0.2821, 'maintMarginReq': 0.2565}
        _agzd = {'ticker': 'AGZD', 'initMarginReq': 0.2752, 'maintMarginReq': 0.2502}
        _smb = {'ticker': 'SMB', 'initMarginReq': 0.1671, 'maintMarginReq': 0.1519}
        _size = {'ticker': 'SIZE', 'initMarginReq': 0.1726, 'maintMarginReq': 0.1569}
        _rwk = {'ticker': 'RWK', 'initMarginReq': 0.1736, 'maintMarginReq': 0.1578}
        _jhsc = {'ticker': 'JHSC', 'initMarginReq': 0.1728, 'maintMarginReq': 0.1571}
        _ulst = {'ticker': 'ULST', 'initMarginReq': 0.1652, 'maintMarginReq': 0.1502}
        _schj = {'ticker': 'SCHJ', 'initMarginReq': 0.2776, 'maintMarginReq': 0.2523}
        _ustb = {'ticker': 'USTB', 'initMarginReq': 0.2767, 'maintMarginReq': 0.2516}
        _adme = {'ticker': 'ADME', 'initMarginReq': 0.1687, 'maintMarginReq': 0.1533}
        _eza = {'ticker': 'EZA', 'initMarginReq': 0.1712, 'maintMarginReq': 0.1556}
        _ibmm = {'ticker': 'IBMM', 'initMarginReq': 0.1659, 'maintMarginReq': 0.1508}
        _avlv = {'ticker': 'AVLV', 'initMarginReq': 0.2296, 'maintMarginReq': 0.2087}
        _pref = {'ticker': 'PREF', 'initMarginReq': 0.1677, 'maintMarginReq': 0.1525}
        _vbnd = {'ticker': 'VBND', 'initMarginReq': 0.2802, 'maintMarginReq': 0.2547}
        _sret = {'ticker': 'SRET', 'initMarginReq': 0.1749, 'maintMarginReq': 0.1590}
        _mear = {'ticker': 'MEAR', 'initMarginReq': 0.1653, 'maintMarginReq': 0.1503}
        _vote = {'ticker': 'VOTE', 'initMarginReq': 0.2290, 'maintMarginReq': 0.2082}
        _xrt = {'ticker': 'XRT', 'initMarginReq': 0.1728, 'maintMarginReq': 0.1571}
        _spdn = {'ticker': 'SPDN', 'initMarginReq': 0.1197, 'maintMarginReq': 0.1088}
        _sdow = {'ticker': 'SDOW', 'initMarginReq': 0.3444, 'maintMarginReq': 0.3131}
        _gnma = {'ticker': 'GNMA', 'initMarginReq': 0.1680, 'maintMarginReq': 0.1527}
        _yyy = {'ticker': 'YYY', 'initMarginReq': 0.1718, 'maintMarginReq': 0.1562}
        _dusa = {'ticker': 'DUSA', 'initMarginReq': 0.1716, 'maintMarginReq': 0.1560}
        _amza = {'ticker': 'AMZA', 'initMarginReq': 0.3392, 'maintMarginReq': 0.3084}
        _ujan = {'ticker': 'UJAN', 'initMarginReq': 0.1671, 'maintMarginReq': 0.1519}
        _psch = {'ticker': 'PSCH', 'initMarginReq': 0.1719, 'maintMarginReq': 0.1563}
        _numg = {'ticker': 'NUMG', 'initMarginReq': 0.1739, 'maintMarginReq': 0.1581}
        _mmin = {'ticker': 'MMIN', 'initMarginReq': 0.2810, 'maintMarginReq': 0.2554}
        _iscg = {'ticker': 'ISCG', 'initMarginReq': 0.1735, 'maintMarginReq': 0.1577}
        _sjb = {'ticker': 'SJB', 'initMarginReq': 0.2666, 'maintMarginReq': 0.2423}
        _clsc = {'ticker': 'CLSC', 'initMarginReq': 0.2216, 'maintMarginReq': 0.2015}
        _numv = {'ticker': 'NUMV', 'initMarginReq': 0.1727, 'maintMarginReq': 0.1570}
        _xmhq = {'ticker': 'XMHQ', 'initMarginReq': 0.1491, 'maintMarginReq': 0.1355}
        _onln = {'ticker': 'ONLN', 'initMarginReq': 0.1974, 'maintMarginReq': 0.1795}
        _ftsd = {'ticker': 'FTSD', 'initMarginReq': 0.2757, 'maintMarginReq': 0.2506}
        _soxs = {'ticker': 'SOXS', 'initMarginReq': 0.4877, 'maintMarginReq': 0.4434}
        _papr = {'ticker': 'PAPR', 'initMarginReq': 0.1686, 'maintMarginReq': 0.1532}
        _tecb = {'ticker': 'TECB', 'initMarginReq': 0.1741, 'maintMarginReq': 0.1583}
        _iak = {'ticker': 'IAK', 'initMarginReq': 0.1693, 'maintMarginReq': 0.1539}
        _pjp = {'ticker': 'PJP', 'initMarginReq': 0.1699, 'maintMarginReq': 0.1544}
        _inds = {'ticker': 'INDS', 'initMarginReq': 0.1720, 'maintMarginReq': 0.1563}
        _ffeb = {'ticker': 'FFEB', 'initMarginReq': 0.1702, 'maintMarginReq': 0.1547}
        _rzv = {'ticker': 'RZV', 'initMarginReq': 0.1744, 'maintMarginReq': 0.1586}
        _kbwy = {'ticker': 'KBWY', 'initMarginReq': 0.1745, 'maintMarginReq': 0.1587}
        _vixy = {'ticker': 'VIXY', 'initMarginReq': 0.1939, 'maintMarginReq': 0.1763}
        _vceb = {'ticker': 'VCEB', 'initMarginReq': 0.2803, 'maintMarginReq': 0.2548}
        _clrg = {'ticker': 'CLRG', 'initMarginReq': 0.1716, 'maintMarginReq': 0.1560}
        _usdu = {'ticker': 'USDU', 'initMarginReq': 0.1636, 'maintMarginReq': 0.1488}
        _pxi = {'ticker': 'PXI', 'initMarginReq': 0.2034, 'maintMarginReq': 0.1849}
        _fmhi = {'ticker': 'FMHI', 'initMarginReq': 0.2818, 'maintMarginReq': 0.2562}
        _cdl = {'ticker': 'CDL', 'initMarginReq': 0.1714, 'maintMarginReq': 0.1558}
        _ccor = {'ticker': 'CCOR', 'initMarginReq': 0.1634, 'maintMarginReq': 0.1486}
        _bkag = {'ticker': 'BKAG', 'initMarginReq': 0.2793, 'maintMarginReq': 0.2539}
        _nuag = {'ticker': 'NUAG', 'initMarginReq': 0.1676, 'maintMarginReq': 0.1524}
        _rcd = {'ticker': 'RCD', 'initMarginReq': 0.1735, 'maintMarginReq': 0.1578}
        _tmf = {'ticker': 'TMF', 'initMarginReq': 0.3281, 'maintMarginReq': 0.2983}
        _dfeb = {'ticker': 'DFEB', 'initMarginReq': 0.1685, 'maintMarginReq': 0.1532}
        _oneo = {'ticker': 'ONEO', 'initMarginReq': 0.1726, 'maintMarginReq': 0.1569}
        _dfnm = {'ticker': 'DFNM', 'initMarginReq': 0.2782, 'maintMarginReq': 0.2529}
        _vsda = {'ticker': 'VSDA', 'initMarginReq': 0.1698, 'maintMarginReq': 0.1543}
        _pbj = {'ticker': 'PBJ', 'initMarginReq': 0.1695, 'maintMarginReq': 0.1540}
        _ulvm = {'ticker': 'ULVM', 'initMarginReq': 0.1720, 'maintMarginReq': 0.1564}
        _fcpi = {'ticker': 'FCPI', 'initMarginReq': 0.1730, 'maintMarginReq': 0.1572}
        _lgh = {'ticker': 'LGH', 'initMarginReq': 0.1689, 'maintMarginReq': 0.1536}
        _pfix = {'ticker': 'PFIX', 'initMarginReq': 0.2040, 'maintMarginReq': 0.1855}
        _fny = {'ticker': 'FNY', 'initMarginReq': 0.1736, 'maintMarginReq': 0.1578}
        _csb = {'ticker': 'CSB', 'initMarginReq': 0.1709, 'maintMarginReq': 0.1554}
        _rfg = {'ticker': 'RFG', 'initMarginReq': 0.1743, 'maintMarginReq': 0.1584}
        _bibl = {'ticker': 'BIBL', 'initMarginReq': 0.1731, 'maintMarginReq': 0.1574}
        _sixh = {'ticker': 'SIXH', 'initMarginReq': 0.1707, 'maintMarginReq': 0.1552}
        _def = {'ticker': 'DEF', 'initMarginReq': 0.1701, 'maintMarginReq': 0.1546}
        _dpst = {'ticker': 'DPST', 'initMarginReq': 0.5777, 'maintMarginReq': 0.5252}
        _pio = {'ticker': 'PIO', 'initMarginReq': 0.1714, 'maintMarginReq': 0.1558}
        _bulz = {'ticker': 'BULZ', 'initMarginReq': 0.7500, 'maintMarginReq': 0.7500}
        _hmop = {'ticker': 'HMOP', 'initMarginReq': 0.1674, 'maintMarginReq': 0.1522}
        _usvm = {'ticker': 'USVM', 'initMarginReq': 0.1731, 'maintMarginReq': 0.1573}
        _pfeb = {'ticker': 'PFEB', 'initMarginReq': 0.1693, 'maintMarginReq': 0.1539}
        _qqh = {'ticker': 'QQH', 'initMarginReq': 0.1684, 'maintMarginReq': 0.1531}
        _fsmb = {'ticker': 'FSMB', 'initMarginReq': 0.2772, 'maintMarginReq': 0.2520}
        _just = {'ticker': 'JUST', 'initMarginReq': 0.1720, 'maintMarginReq': 0.1563}
        _dfe = {'ticker': 'DFE', 'initMarginReq': 0.1724, 'maintMarginReq': 0.1568}
        _ldsf = {'ticker': 'LDSF', 'initMarginReq': 0.2782, 'maintMarginReq': 0.2529}
        _mmit = {'ticker': 'MMIT', 'initMarginReq': 0.1672, 'maintMarginReq': 0.1520}
        _divb = {'ticker': 'DIVB', 'initMarginReq': 0.1710, 'maintMarginReq': 0.1554}
        _fqal = {'ticker': 'FQAL', 'initMarginReq': 0.1713, 'maintMarginReq': 0.1557}
        _urty = {'ticker': 'URTY', 'initMarginReq': 0.5091, 'maintMarginReq': 0.4628}
        _ovl = {'ticker': 'OVL', 'initMarginReq': 0.1731, 'maintMarginReq': 0.1574}
        _govz = {'ticker': 'GOVZ', 'initMarginReq': 0.2295, 'maintMarginReq': 0.2086}
        _ftxo = {'ticker': 'FTXO', 'initMarginReq': 0.1808, 'maintMarginReq': 0.1643}
        _gal = {'ticker': 'GAL', 'initMarginReq': 0.1700, 'maintMarginReq': 0.1546}
        _ibuy = {'ticker': 'IBUY', 'initMarginReq': 0.2091, 'maintMarginReq': 0.1901}
        _pjun = {'ticker': 'PJUN', 'initMarginReq': 0.1689, 'maintMarginReq': 0.1536}
        _ibmn = {'ticker': 'IBMN', 'initMarginReq': 0.1663, 'maintMarginReq': 0.1512}
        _dog = {'ticker': 'DOG', 'initMarginReq': 0.1084, 'maintMarginReq': 0.0985}
        _jpme = {'ticker': 'JPME', 'initMarginReq': 0.1728, 'maintMarginReq': 0.1571}
        _bscs = {'ticker': 'BSCS', 'initMarginReq': 0.1677, 'maintMarginReq': 0.1524}
        _xmvm = {'ticker': 'XMVM', 'initMarginReq': 0.1734, 'maintMarginReq': 0.1577}
        _nubd = {'ticker': 'NUBD', 'initMarginReq': 0.1680, 'maintMarginReq': 0.1527}
        _vlu = {'ticker': 'VLU', 'initMarginReq': 0.1718, 'maintMarginReq': 0.1562}
        _fvc = {'ticker': 'FVC', 'initMarginReq': 0.1696, 'maintMarginReq': 0.1542}
        _ibdu = {'ticker': 'IBDU', 'initMarginReq': 0.1681, 'maintMarginReq': 0.1528}
        _fdd = {'ticker': 'FDD', 'initMarginReq': 0.1719, 'maintMarginReq': 0.1562}
        _dig = {'ticker': 'DIG', 'initMarginReq': 0.4935, 'maintMarginReq': 0.4486}
        _tur = {'ticker': 'TUR', 'initMarginReq': 1.0000, 'maintMarginReq': 0.1523}
        _mlpb = {'ticker': 'MLPB', 'initMarginReq': 0.2500, 'maintMarginReq': 0.2500}
        _pmar = {'ticker': 'PMAR', 'initMarginReq': 0.1688, 'maintMarginReq': 0.1534}
        _skor = {'ticker': 'SKOR', 'initMarginReq': 0.1673, 'maintMarginReq': 0.1521}
        _pth = {'ticker': 'PTH', 'initMarginReq': 0.1728, 'maintMarginReq': 0.1571}
        _fyt = {'ticker': 'FYT', 'initMarginReq': 0.1781, 'maintMarginReq': 0.1600}
        _py = {'ticker': 'PY', 'initMarginReq': 0.1722, 'maintMarginReq': 0.1566}
        _usd = {'ticker': 'USD', 'initMarginReq': 0.4341, 'maintMarginReq': 0.3947}
        _fnk = {'ticker': 'FNK', 'initMarginReq': 0.1731, 'maintMarginReq': 0.1574}
        _jmom = {'ticker': 'JMOM', 'initMarginReq': 0.1724, 'maintMarginReq': 0.1567}
        _psep = {'ticker': 'PSEP', 'initMarginReq': 0.1683, 'maintMarginReq': 0.1530}
        _fapr = {'ticker': 'FAPR', 'initMarginReq': 0.2269, 'maintMarginReq': 0.2063}
        _tchp = {'ticker': 'TCHP', 'initMarginReq': 0.2316, 'maintMarginReq': 0.2105}
        _xsw = {'ticker': 'XSW', 'initMarginReq': 0.1756, 'maintMarginReq': 0.1596}
        _eql = {'ticker': 'EQL', 'initMarginReq': 0.1720, 'maintMarginReq': 0.1564}
        _iltb = {'ticker': 'ILTB', 'initMarginReq': 0.1703, 'maintMarginReq': 0.1548}
        _poct = {'ticker': 'POCT', 'initMarginReq': 0.1685, 'maintMarginReq': 0.1532}
        _palc = {'ticker': 'PALC', 'initMarginReq': 0.2282, 'maintMarginReq': 0.2075}
        _mstb = {'ticker': 'MSTB', 'initMarginReq': 0.2237, 'maintMarginReq': 0.2034}
        _taxf = {'ticker': 'TAXF', 'initMarginReq': 0.2797, 'maintMarginReq': 0.2543}
        _psj = {'ticker': 'PSJ', 'initMarginReq': 0.1742, 'maintMarginReq': 0.1584}
        _fumb = {'ticker': 'FUMB', 'initMarginReq': 0.2757, 'maintMarginReq': 0.2506}
        _atmp = {'ticker': 'ATMP', 'initMarginReq': 0.2500, 'maintMarginReq': 0.2500}
        _qval = {'ticker': 'QVAL', 'initMarginReq': 0.1748, 'maintMarginReq': 0.1589}
        _dgrs = {'ticker': 'DGRS', 'initMarginReq': 0.1722, 'maintMarginReq': 0.1566}
        _fdec = {'ticker': 'FDEC', 'initMarginReq': 0.2269, 'maintMarginReq': 0.2063}
        _dbmf = {'ticker': 'DBMF', 'initMarginReq': 0.1628, 'maintMarginReq': 0.1480}
        _cgcp = {'ticker': 'CGCP', 'initMarginReq': 0.2803, 'maintMarginReq': 0.2549}
        _ixp = {'ticker': 'IXP', 'initMarginReq': 0.1726, 'maintMarginReq': 0.1569}
        _ibd = {'ticker': 'IBD', 'initMarginReq': 0.1675, 'maintMarginReq': 0.1523}
        _flv = {'ticker': 'FLV', 'initMarginReq': 0.1699, 'maintMarginReq': 0.1544}
        _valq = {'ticker': 'VALQ', 'initMarginReq': 0.1720, 'maintMarginReq': 0.1563}
        _xlsr = {'ticker': 'XLSR', 'initMarginReq': 0.1718, 'maintMarginReq': 0.1562}
        _prnt = {'ticker': 'PRNT', 'initMarginReq': 0.1748, 'maintMarginReq': 0.1589}
        _she = {'ticker': 'SHE', 'initMarginReq': 0.1724, 'maintMarginReq': 0.1567}
        _djd = {'ticker': 'DJD', 'initMarginReq': 0.1689, 'maintMarginReq': 0.1535}
        _dapr = {'ticker': 'DAPR', 'initMarginReq': 0.2248, 'maintMarginReq': 0.2044}
        _pdec = {'ticker': 'PDEC', 'initMarginReq': 0.1689, 'maintMarginReq': 0.1535}
        _jpse = {'ticker': 'JPSE', 'initMarginReq': 0.1734, 'maintMarginReq': 0.1576}
        _pbe = {'ticker': 'PBE', 'initMarginReq': 0.1712, 'maintMarginReq': 0.1556}
        _fri = {'ticker': 'FRI', 'initMarginReq': 0.1740, 'maintMarginReq': 0.1582}
        _flbl = {'ticker': 'FLBL', 'initMarginReq': 0.2775, 'maintMarginReq': 0.2523}
        _usmf = {'ticker': 'USMF', 'initMarginReq': 0.1715, 'maintMarginReq': 0.1559}
        _dfen = {'ticker': 'DFEN', 'initMarginReq': 0.5569, 'maintMarginReq': 0.5062}
        _mln = {'ticker': 'MLN', 'initMarginReq': 0.1727, 'maintMarginReq': 0.1570}
        _cza = {'ticker': 'CZA', 'initMarginReq': 0.1724, 'maintMarginReq': 0.1567}
        _qgro = {'ticker': 'QGRO', 'initMarginReq': 0.1737, 'maintMarginReq': 0.1580}
        _hyzd = {'ticker': 'HYZD', 'initMarginReq': 0.2809, 'maintMarginReq': 0.2554}
        _mort = {'ticker': 'MORT', 'initMarginReq': 0.1820, 'maintMarginReq': 0.1655}
        _tdsb = {'ticker': 'TDSB', 'initMarginReq': 0.2220, 'maintMarginReq': 0.2018}
        _iscb = {'ticker': 'ISCB', 'initMarginReq': 0.1738, 'maintMarginReq': 0.1580}
        _xvv = {'ticker': 'XVV', 'initMarginReq': 0.2296, 'maintMarginReq': 0.2087}
        _ptf = {'ticker': 'PTF', 'initMarginReq': 0.1830, 'maintMarginReq': 0.1664}
        _fmar = {'ticker': 'FMAR', 'initMarginReq': 0.2267, 'maintMarginReq': 0.2061}
        _cure = {'ticker': 'CURE', 'initMarginReq': 0.5461, 'maintMarginReq': 0.4965}
        _fyc = {'ticker': 'FYC', 'initMarginReq': 0.1748, 'maintMarginReq': 0.1589}
        _yld = {'ticker': 'YLD', 'initMarginReq': 0.2820, 'maintMarginReq': 0.2564}
        _dfip = {'ticker': 'DFIP', 'initMarginReq': 0.2800, 'maintMarginReq': 0.2546}
        _ibte = {'ticker': 'IBTE', 'initMarginReq': 0.1660, 'maintMarginReq': 0.1509}
        _psce = {'ticker': 'PSCE', 'initMarginReq': 0.2290, 'maintMarginReq': 0.2082}
        _csml = {'ticker': 'CSML', 'initMarginReq': 0.1728, 'maintMarginReq': 0.1571}
        _vfmo = {'ticker': 'VFMO', 'initMarginReq': 0.1722, 'maintMarginReq': 0.1566}
        _pnov = {'ticker': 'PNOV', 'initMarginReq': 0.1691, 'maintMarginReq': 0.1537}
        _bjan = {'ticker': 'BJAN', 'initMarginReq': 0.1697, 'maintMarginReq': 0.1542}
        _must = {'ticker': 'MUST', 'initMarginReq': 0.1686, 'maintMarginReq': 0.1532}
        _spff = {'ticker': 'SPFF', 'initMarginReq': 0.2824, 'maintMarginReq': 0.2567}
        _smlv = {'ticker': 'SMLV', 'initMarginReq': 0.1704, 'maintMarginReq': 0.1549}
        _tipz = {'ticker': 'TIPZ', 'initMarginReq': 0.1009, 'maintMarginReq': 0.0917}
        _deed = {'ticker': 'DEED', 'initMarginReq': 0.2795, 'maintMarginReq': 0.2541}
        _psp = {'ticker': 'PSP', 'initMarginReq': 0.1746, 'maintMarginReq': 0.1587}
        _fcvt = {'ticker': 'FCVT', 'initMarginReq': 0.2858, 'maintMarginReq': 0.2598}
        _fab = {'ticker': 'FAB', 'initMarginReq': 0.1725, 'maintMarginReq': 0.1568}
        _oscv = {'ticker': 'OSCV', 'initMarginReq': 0.1731, 'maintMarginReq': 0.1573}
        _qvmm = {'ticker': 'QVMM', 'initMarginReq': 0.2307, 'maintMarginReq': 0.2097}
        _tbx = {'ticker': 'TBX', 'initMarginReq': 0.1622, 'maintMarginReq': 0.1475}
        _airr = {'ticker': 'AIRR', 'initMarginReq': 0.1727, 'maintMarginReq': 0.1570}
        _fad = {'ticker': 'FAD', 'initMarginReq': 0.1735, 'maintMarginReq': 0.1578}
        _igbh = {'ticker': 'IGBH', 'initMarginReq': 0.1666, 'maintMarginReq': 0.1514}
        _xph = {'ticker': 'XPH', 'initMarginReq': 0.1720, 'maintMarginReq': 0.1563}
        _nail = {'ticker': 'NAIL', 'initMarginReq': 0.5949, 'maintMarginReq': 0.5409}
        _idna = {'ticker': 'IDNA', 'initMarginReq': 0.1741, 'maintMarginReq': 0.1583}
        _vfqy = {'ticker': 'VFQY', 'initMarginReq': 0.1724, 'maintMarginReq': 0.1567}
        _slvo = {'ticker': 'SLVO', 'initMarginReq': 0.2500, 'maintMarginReq': 0.2500}
        _dfnl = {'ticker': 'DFNL', 'initMarginReq': 0.1709, 'maintMarginReq': 0.1554}
        _esg = {'ticker': 'ESG', 'initMarginReq': 0.5000, 'maintMarginReq': 0.5000}
        _pyz = {'ticker': 'PYZ', 'initMarginReq': 0.1868, 'maintMarginReq': 0.1698}
        _uwm = {'ticker': 'UWM', 'initMarginReq': 0.3153, 'maintMarginReq': 0.2867}
        _tphd = {'ticker': 'TPHD', 'initMarginReq': 0.1715, 'maintMarginReq': 0.1559}
        _epol = {'ticker': 'EPOL', 'initMarginReq': 0.1724, 'maintMarginReq': 0.1568}
        _wfhy = {'ticker': 'WFHY', 'initMarginReq': 0.2842, 'maintMarginReq': 0.2583}
        _ttac = {'ticker': 'TTAC', 'initMarginReq': 0.1719, 'maintMarginReq': 0.1562}
        _lrge = {'ticker': 'LRGE', 'initMarginReq': 0.1727, 'maintMarginReq': 0.1570}
        _emnt = {'ticker': 'EMNT', 'initMarginReq': 0.2753, 'maintMarginReq': 0.2503}
        _umi = {'ticker': 'UMI', 'initMarginReq': 0.2320, 'maintMarginReq': 0.2109}
        _ddec = {'ticker': 'DDEC', 'initMarginReq': 0.2235, 'maintMarginReq': 0.2032}
        _gnom = {'ticker': 'GNOM', 'initMarginReq': 0.1989, 'maintMarginReq': 0.1809}
        _spvu = {'ticker': 'SPVU', 'initMarginReq': 0.1720, 'maintMarginReq': 0.1564}
        _bmay = {'ticker': 'BMAY', 'initMarginReq': 0.1701, 'maintMarginReq': 0.1547}
        _tok = {'ticker': 'TOK', 'initMarginReq': 0.1719, 'maintMarginReq': 0.1563}
        _ausf = {'ticker': 'AUSF', 'initMarginReq': 0.1709, 'maintMarginReq': 0.1554}
        _ibmo = {'ticker': 'IBMO', 'initMarginReq': 0.1668, 'maintMarginReq': 0.1517}
        _tplc = {'ticker': 'TPLC', 'initMarginReq': 0.1720, 'maintMarginReq': 0.1564}
        _paug = {'ticker': 'PAUG', 'initMarginReq': 0.1675, 'maintMarginReq': 0.1523}
        _edoc = {'ticker': 'EDOC', 'initMarginReq': 0.2343, 'maintMarginReq': 0.2130}
        _pffv = {'ticker': 'PFFV', 'initMarginReq': 0.2811, 'maintMarginReq': 0.2555}
        _jsmd = {'ticker': 'JSMD', 'initMarginReq': 0.1722, 'maintMarginReq': 0.1566}
        _cacg = {'ticker': 'CACG', 'initMarginReq': 0.1728, 'maintMarginReq': 0.1571}
        _pawz = {'ticker': 'PAWZ', 'initMarginReq': 0.1675, 'maintMarginReq': 0.1523}
        _hlal = {'ticker': 'HLAL', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _qlv = {'ticker': 'QLV', 'initMarginReq': 0.1661, 'maintMarginReq': 0.1510}
        _fjan = {'ticker': 'FJAN', 'initMarginReq': 0.2206, 'maintMarginReq': 0.2006}
        _hegd = {'ticker': 'HEGD', 'initMarginReq': 0.2201, 'maintMarginReq': 0.2001}
        _hybb = {'ticker': 'HYBB', 'initMarginReq': 0.2735, 'maintMarginReq': 0.2486}
        _etho = {'ticker': 'ETHO', 'initMarginReq': 0.1656, 'maintMarginReq': 0.1506}
        _ghyb = {'ticker': 'GHYB', 'initMarginReq': 0.2730, 'maintMarginReq': 0.2481}
        _hygh = {'ticker': 'HYGH', 'initMarginReq': 0.2723, 'maintMarginReq': 0.2476}
        _sixa = {'ticker': 'SIXA', 'initMarginReq': 0.1659, 'maintMarginReq': 0.1508}
        _pjul = {'ticker': 'PJUL', 'initMarginReq': 0.1649, 'maintMarginReq': 0.1499}
        _gtip = {'ticker': 'GTIP', 'initMarginReq': 0.1672, 'maintMarginReq': 0.1520}
        _dali = {'ticker': 'DALI', 'initMarginReq': 0.1680, 'maintMarginReq': 0.1527}
        _xmpt = {'ticker': 'XMPT', 'initMarginReq': 0.1668, 'maintMarginReq': 0.1517}
        _ousm = {'ticker': 'OUSM', 'initMarginReq': 0.1656, 'maintMarginReq': 0.1506}
        _sval = {'ticker': 'SVAL', 'initMarginReq': 0.2192, 'maintMarginReq': 0.1993}
        _fdm = {'ticker': 'FDM', 'initMarginReq': 0.1640, 'maintMarginReq': 0.1491}
        _foct = {'ticker': 'FOCT', 'initMarginReq': 0.2199, 'maintMarginReq': 0.1999}
        _omfs = {'ticker': 'OMFS', 'initMarginReq': 0.1656, 'maintMarginReq': 0.1505}
        _rth = {'ticker': 'RTH', 'initMarginReq': 0.1653, 'maintMarginReq': 0.1503}
        _xsmo = {'ticker': 'XSMO', 'initMarginReq': 0.1639, 'maintMarginReq': 0.1490}
        _pfld = {'ticker': 'PFLD', 'initMarginReq': 0.2774, 'maintMarginReq': 0.2522}
        _lsat = {'ticker': 'LSAT', 'initMarginReq': 0.2205, 'maintMarginReq': 0.2005}
        _dmar = {'ticker': 'DMAR', 'initMarginReq': 0.2207, 'maintMarginReq': 0.2006}
        _deus = {'ticker': 'DEUS', 'initMarginReq': 0.1658, 'maintMarginReq': 0.1507}
        _igeb = {'ticker': 'IGEB', 'initMarginReq': 0.1653, 'maintMarginReq': 0.1503}
        _ibtd = {'ticker': 'IBTD', 'initMarginReq': 0.1653, 'maintMarginReq': 0.1502}
        _bndc = {'ticker': 'BNDC', 'initMarginReq': 0.1662, 'maintMarginReq': 0.1511}
        _aiq = {'ticker': 'AIQ', 'initMarginReq': 0.1634, 'maintMarginReq': 0.1486}
        _btal = {'ticker': 'BTAL', 'initMarginReq': 0.1649, 'maintMarginReq': 0.1499}
        _hyxf = {'ticker': 'HYXF', 'initMarginReq': 0.2729, 'maintMarginReq': 0.2481}
        _vfmf = {'ticker': 'VFMF', 'initMarginReq': 0.1649, 'maintMarginReq': 0.1499}
        _gvip = {'ticker': 'GVIP', 'initMarginReq': 0.1661, 'maintMarginReq': 0.1510}
        _eprf = {'ticker': 'EPRF', 'initMarginReq': 0.1654, 'maintMarginReq': 0.1504}
        _ffty = {'ticker': 'FFTY', 'initMarginReq': 0.1676, 'maintMarginReq': 0.1524}
        _faz = {'ticker': 'FAZ', 'initMarginReq': 0.5467, 'maintMarginReq': 0.4970}
        _rfv = {'ticker': 'RFV', 'initMarginReq': 0.1688, 'maintMarginReq': 0.1534}
        _spus = {'ticker': 'SPUS', 'initMarginReq': 0.1655, 'maintMarginReq': 0.1504}
        _eden = {'ticker': 'EDEN', 'initMarginReq': 0.1682, 'maintMarginReq': 0.1529}
        _fjul = {'ticker': 'FJUL', 'initMarginReq': 0.2199, 'maintMarginReq': 0.1999}
        _srty = {'ticker': 'SRTY', 'initMarginReq': 0.4895, 'maintMarginReq': 0.4450}
        _vsmv = {'ticker': 'VSMV', 'initMarginReq': 0.1655, 'maintMarginReq': 0.1504}
        _korp = {'ticker': 'KORP', 'initMarginReq': 0.2765, 'maintMarginReq': 0.2514}
        _wtmf = {'ticker': 'WTMF', 'initMarginReq': 0.1658, 'maintMarginReq': 0.1507}
        _sixl = {'ticker': 'SIXL', 'initMarginReq': 0.1665, 'maintMarginReq': 0.1513}
        _xitk = {'ticker': 'XITK', 'initMarginReq': 0.2042, 'maintMarginReq': 0.1857}
        _ewre = {'ticker': 'EWRE', 'initMarginReq': 0.1655, 'maintMarginReq': 0.1505}
        _vrai = {'ticker': 'VRAI', 'initMarginReq': 0.1655, 'maintMarginReq': 0.1505}
        _lsaf = {'ticker': 'LSAF', 'initMarginReq': 0.1649, 'maintMarginReq': 0.1499}
        _rvnu = {'ticker': 'RVNU', 'initMarginReq': 0.1648, 'maintMarginReq': 0.1498}
        _kbwp = {'ticker': 'KBWP', 'initMarginReq': 0.1648, 'maintMarginReq': 0.1498}
        _jmub = {'ticker': 'JMUB', 'initMarginReq': 0.2745, 'maintMarginReq': 0.2495}
        _ibdv = {'ticker': 'IBDV', 'initMarginReq': 0.2213, 'maintMarginReq': 0.2012}
        _bfor = {'ticker': 'BFOR', 'initMarginReq': 0.1646, 'maintMarginReq': 0.1497}
        _tdvg = {'ticker': 'TDVG', 'initMarginReq': 0.2217, 'maintMarginReq': 0.2016}
        _ppty = {'ticker': 'PPTY', 'initMarginReq': 0.1662, 'maintMarginReq': 0.1511}
        _pkb = {'ticker': 'PKB', 'initMarginReq': 0.1809, 'maintMarginReq': 0.1644}
        _ftxr = {'ticker': 'FTXR', 'initMarginReq': 0.1625, 'maintMarginReq': 0.1477}
        _hyhg = {'ticker': 'HYHG', 'initMarginReq': 0.2716, 'maintMarginReq': 0.2469}
        _psr = {'ticker': 'PSR', 'initMarginReq': 0.1670, 'maintMarginReq': 0.1518}
        _imtb = {'ticker': 'IMTB', 'initMarginReq': 0.2767, 'maintMarginReq': 0.2515}
        _fmf = {'ticker': 'FMF', 'initMarginReq': 0.1642, 'maintMarginReq': 0.1493}
        _hdge = {'ticker': 'HDGE', 'initMarginReq': 0.2869, 'maintMarginReq': 0.2608}
        _bsep = {'ticker': 'BSEP', 'initMarginReq': 0.1654, 'maintMarginReq': 0.1504}
        _stot = {'ticker': 'STOT', 'initMarginReq': 0.2755, 'maintMarginReq': 0.2504}
        _fdg = {'ticker': 'FDG', 'initMarginReq': 0.1649, 'maintMarginReq': 0.1499}
        _pst = {'ticker': 'PST', 'initMarginReq': 0.1950, 'maintMarginReq': 0.1772}
        _doct = {'ticker': 'DOCT', 'initMarginReq': 0.2201, 'maintMarginReq': 0.2001}
        _qlc = {'ticker': 'QLC', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _prn = {'ticker': 'PRN', 'initMarginReq': 0.1654, 'maintMarginReq': 0.1504}
        _pbtp = {'ticker': 'PBTP', 'initMarginReq': 0.1666, 'maintMarginReq': 0.1514}
        _pifi = {'ticker': 'PIFI', 'initMarginReq': 0.2761, 'maintMarginReq': 0.2510}
        _esga = {'ticker': 'ESGA', 'initMarginReq': 0.2207, 'maintMarginReq': 0.2006}
        _ius = {'ticker': 'IUS', 'initMarginReq': 0.1653, 'maintMarginReq': 0.1503}
        _edow = {'ticker': 'EDOW', 'initMarginReq': 0.1658, 'maintMarginReq': 0.1507}
        _fllv = {'ticker': 'FLLV', 'initMarginReq': 0.1657, 'maintMarginReq': 0.1597}
        _bsct = {'ticker': 'BSCT', 'initMarginReq': 0.1660, 'maintMarginReq': 0.1509}
        _rigs = {'ticker': 'RIGS', 'initMarginReq': 0.2733, 'maintMarginReq': 0.2485}
        _ocio = {'ticker': 'OCIO', 'initMarginReq': 0.1656, 'maintMarginReq': 0.1506}
        _fsep = {'ticker': 'FSEP', 'initMarginReq': 0.2196, 'maintMarginReq': 0.1997}
        _ieus = {'ticker': 'IEUS', 'initMarginReq': 0.1676, 'maintMarginReq': 0.1524}
        _pbp = {'ticker': 'PBP', 'initMarginReq': 0.1648, 'maintMarginReq': 0.1498}
        _mvv = {'ticker': 'MVV', 'initMarginReq': 0.3295, 'maintMarginReq': 0.2995}
        _psl = {'ticker': 'PSL', 'initMarginReq': 0.1649, 'maintMarginReq': 0.1499}
        _fbgx = {'ticker': 'FBGX', 'initMarginReq': 0.2500, 'maintMarginReq': 0.2500}
        _aieq = {'ticker': 'AIEQ', 'initMarginReq': 0.1656, 'maintMarginReq': 0.1505}
        _afif = {'ticker': 'AFIF', 'initMarginReq': 0.2763, 'maintMarginReq': 0.2512}
        _hydb = {'ticker': 'HYDB', 'initMarginReq': 0.2741, 'maintMarginReq': 0.2492}
        _aesr = {'ticker': 'AESR', 'initMarginReq': 0.1670, 'maintMarginReq': 0.1518}
        _nure = {'ticker': 'NURE', 'initMarginReq': 0.1652, 'maintMarginReq': 0.1501}
        _ffti = {'ticker': 'FFTI', 'initMarginReq': 0.2771, 'maintMarginReq': 0.2519}
        _ryj = {'ticker': 'RYJ', 'initMarginReq': 0.1662, 'maintMarginReq': 0.1511}
        _hybl = {'ticker': 'HYBL', 'initMarginReq': 0.2744, 'maintMarginReq': 0.2495}
        _ewmc = {'ticker': 'EWMC', 'initMarginReq': 0.1658, 'maintMarginReq': 0.1507}
        _miln = {'ticker': 'MILN', 'initMarginReq': 0.1693, 'maintMarginReq': 0.1539}
        _eqwl = {'ticker': 'EQWL', 'initMarginReq': 0.1655, 'maintMarginReq': 0.1505}
        _bapr = {'ticker': 'BAPR', 'initMarginReq': 0.1651, 'maintMarginReq': 0.1501}
        _fcal = {'ticker': 'FCAL', 'initMarginReq': 0.2743, 'maintMarginReq': 0.2494}
        _balt = {'ticker': 'BALT', 'initMarginReq': 0.2500, 'maintMarginReq': 0.2500}
        _twm = {'ticker': 'TWM', 'initMarginReq': 0.3911, 'maintMarginReq': 0.3555}
        _bfeb = {'ticker': 'BFEB', 'initMarginReq': 0.1651, 'maintMarginReq': 0.1501}
        _tecs = {'ticker': 'TECS', 'initMarginReq': 0.5046, 'maintMarginReq': 0.4587}
        _cvy = {'ticker': 'CVY', 'initMarginReq': 0.1655, 'maintMarginReq': 0.1504}
        _ibhc = {'ticker': 'IBHC', 'initMarginReq': 0.2742, 'maintMarginReq': 0.2493}
        _norw = {'ticker': 'NORW', 'initMarginReq': 0.1660, 'maintMarginReq': 0.1510}
        _htec = {'ticker': 'HTEC', 'initMarginReq': 0.1661, 'maintMarginReq': 0.1510}
        _ismd = {'ticker': 'ISMD', 'initMarginReq': 0.1657, 'maintMarginReq': 0.1506}
        _njan = {'ticker': 'NJAN', 'initMarginReq': 0.1647, 'maintMarginReq': 0.1497}
        _sqew = {'ticker': 'SQEW', 'initMarginReq': 0.1649, 'maintMarginReq': 0.1499}
        _shag = {'ticker': 'SHAG', 'initMarginReq': 0.2761, 'maintMarginReq': 0.2510}
        _baug = {'ticker': 'BAUG', 'initMarginReq': 0.1648, 'maintMarginReq': 0.1499}
        _risr = {'ticker': 'RISR', 'initMarginReq': 0.2711, 'maintMarginReq': 0.2464}
        _rxl = {'ticker': 'RXL', 'initMarginReq': 0.3366, 'maintMarginReq': 0.3060}
        _ibmp = {'ticker': 'IBMP', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _risn = {'ticker': 'RISN', 'initMarginReq': 0.2201, 'maintMarginReq': 0.2001}
        _rfda = {'ticker': 'RFDA', 'initMarginReq': 0.1661, 'maintMarginReq': 0.1510}
        _qqxt = {'ticker': 'QQXT', 'initMarginReq': 0.1646, 'maintMarginReq': 0.1497}
        _buff = {'ticker': 'BUFF', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _svol = {'ticker': 'SVOL', 'initMarginReq': 0.2204, 'maintMarginReq': 0.2004}
        _fbcv = {'ticker': 'FBCV', 'initMarginReq': 0.1669, 'maintMarginReq': 0.1517}
        _fngo = {'ticker': 'FNGO', 'initMarginReq': 0.5000, 'maintMarginReq': 0.5000}
        _eqrr = {'ticker': 'EQRR', 'initMarginReq': 0.1719, 'maintMarginReq': 0.1563}
        _rzg = {'ticker': 'RZG', 'initMarginReq': 0.1772, 'maintMarginReq': 0.1611}
        _qqqn = {'ticker': 'QQQN', 'initMarginReq': 0.2213, 'maintMarginReq': 0.2012}
        _ibnd = {'ticker': 'IBND', 'initMarginReq': 0.1665, 'maintMarginReq': 0.1514}
        _pzt = {'ticker': 'PZT', 'initMarginReq': 0.1648, 'maintMarginReq': 0.1498}
        _hknd = {'ticker': 'HKND', 'initMarginReq': 0.2221, 'maintMarginReq': 0.2019}
        _psff = {'ticker': 'PSFF', 'initMarginReq': 0.2200, 'maintMarginReq': 0.2000}
        _tdv = {'ticker': 'TDV', 'initMarginReq': 0.1638, 'maintMarginReq': 0.1489}
        _fdmo = {'ticker': 'FDMO', 'initMarginReq': 0.1659, 'maintMarginReq': 0.1508}
        _netl = {'ticker': 'NETL', 'initMarginReq': 0.1668, 'maintMarginReq': 0.1517}
        _bkmc = {'ticker': 'BKMC', 'initMarginReq': 0.1658, 'maintMarginReq': 0.1507}
        _ietc = {'ticker': 'IETC', 'initMarginReq': 0.1646, 'maintMarginReq': 0.1496}
        _fisr = {'ticker': 'FISR', 'initMarginReq': 0.2771, 'maintMarginReq': 0.2519}
        _chgx = {'ticker': 'CHGX', 'initMarginReq': 0.1655, 'maintMarginReq': 0.1504}
        _mbsd = {'ticker': 'MBSD', 'initMarginReq': 0.1660, 'maintMarginReq': 0.1509}
        _flmb = {'ticker': 'FLMB', 'initMarginReq': 0.2752, 'maintMarginReq': 0.2502}
        _ucrd = {'ticker': 'UCRD', 'initMarginReq': 0.2701, 'maintMarginReq': 0.2510}
        _kce = {'ticker': 'KCE', 'initMarginReq': 0.1651, 'maintMarginReq': 0.1501}
        _ign = {'ticker': 'IGN', 'initMarginReq': 0.1652, 'maintMarginReq': 0.1501}
        _pwc = {'ticker': 'PWC', 'initMarginReq': 0.1643, 'maintMarginReq': 0.1493}
        _dxd = {'ticker': 'DXD', 'initMarginReq': 0.2299, 'maintMarginReq': 0.2090}
        _dsep = {'ticker': 'DSEP', 'initMarginReq': 0.2201, 'maintMarginReq': 0.2001}
        _utrn = {'ticker': 'UTRN', 'initMarginReq': 0.1683, 'maintMarginReq': 0.1530}
        _ghyg = {'ticker': 'GHYG', 'initMarginReq': 0.2745, 'maintMarginReq': 0.2495}
        _putw = {'ticker': 'PUTW', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _qaba = {'ticker': 'QABA', 'initMarginReq': 0.1641, 'maintMarginReq': 0.1492}
        _webl = {'ticker': 'WEBL', 'initMarginReq': 0.5689, 'maintMarginReq': 0.5172}
        _inkm = {'ticker': 'INKM', 'initMarginReq': 0.1658, 'maintMarginReq': 0.1507}
        _dvol = {'ticker': 'DVOL', 'initMarginReq': 0.1660, 'maintMarginReq': 0.1509}
        _ure = {'ticker': 'URE', 'initMarginReq': 0.3356, 'maintMarginReq': 0.3051}
        _spbc = {'ticker': 'SPBC', 'initMarginReq': 0.2219, 'maintMarginReq': 0.2018}
        _xout = {'ticker': 'XOUT', 'initMarginReq': 0.1656, 'maintMarginReq': 0.1505}
        _bjul = {'ticker': 'BJUL', 'initMarginReq': 0.1652, 'maintMarginReq': 0.1502}
        _ibtg = {'ticker': 'IBTG', 'initMarginReq': 0.1656, 'maintMarginReq': 0.1505}
        _amub = {'ticker': 'AMUB', 'initMarginReq': 0.2500, 'maintMarginReq': 0.2500}
        _gmom = {'ticker': 'GMOM', 'initMarginReq': 0.1651, 'maintMarginReq': 0.1501}
        _boct = {'ticker': 'BOCT', 'initMarginReq': 0.1651, 'maintMarginReq': 0.1501}
        _sbio = {'ticker': 'SBIO', 'initMarginReq': 0.2082, 'maintMarginReq': 0.1893}
        _sspy = {'ticker': 'SSPY', 'initMarginReq': 0.1657, 'maintMarginReq': 0.1507}
        _nuhy = {'ticker': 'NUHY', 'initMarginReq': 0.2770, 'maintMarginReq': 0.2518}
        _qmom = {'ticker': 'QMOM', 'initMarginReq': 0.1737, 'maintMarginReq': 0.1580}
        _mfus = {'ticker': 'MFUS', 'initMarginReq': 0.1656, 'maintMarginReq': 0.1505}
        _drip = {'ticker': 'DRIP', 'initMarginReq': 0.4905, 'maintMarginReq': 0.4459}
        _dwaw = {'ticker': 'DWAW', 'initMarginReq': 0.1664, 'maintMarginReq': 0.1513}
        _phyl = {'ticker': 'PHYL', 'initMarginReq': 0.2762, 'maintMarginReq': 0.2511}
        _husv = {'ticker': 'HUSV', 'initMarginReq': 0.1668, 'maintMarginReq': 0.1517}
        _joet = {'ticker': 'JOET', 'initMarginReq': 0.2205, 'maintMarginReq': 0.2005}
        _flmi = {'ticker': 'FLMI', 'initMarginReq': 0.2754, 'maintMarginReq': 0.2503}
        _bib = {'ticker': 'BIB', 'initMarginReq': 0.3286, 'maintMarginReq': 0.2987}
        _xhs = {'ticker': 'XHS', 'initMarginReq': 0.1658, 'maintMarginReq': 0.1507}
        _bndd = {'ticker': 'BNDD', 'initMarginReq': 0.2773, 'maintMarginReq': 0.2521}
        _hyld = {'ticker': 'HYLD', 'initMarginReq': 0.2760, 'maintMarginReq': 0.2509}
        _fngd = {'ticker': 'FNGD', 'initMarginReq': 0.7500, 'maintMarginReq': 0.7500}
        _owns = {'ticker': 'OWNS', 'initMarginReq': 0.2762, 'maintMarginReq': 0.2511}
        _schq = {'ticker': 'SCHQ', 'initMarginReq': 0.2785, 'maintMarginReq': 0.2532}
        _dfnv = {'ticker': 'DFNV', 'initMarginReq': 0.2199, 'maintMarginReq': 0.2000}
        _teqi = {'ticker': 'TEQI', 'initMarginReq': 0.2207, 'maintMarginReq': 0.2007}
        _xvol = {'ticker': 'XVOL', 'initMarginReq': 0.2211, 'maintMarginReq': 0.2010}
        _minc = {'ticker': 'MINC', 'initMarginReq': 0.1648, 'maintMarginReq': 0.1499}
        _jsml = {'ticker': 'JSML', 'initMarginReq': 0.1641, 'maintMarginReq': 0.1492}
        _bdec = {'ticker': 'BDEC', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _bmar = {'ticker': 'BMAR', 'initMarginReq': 0.1652, 'maintMarginReq': 0.1502}
        _ftxl = {'ticker': 'FTXL', 'initMarginReq': 0.2036, 'maintMarginReq': 0.1851}
        _spmo = {'ticker': 'SPMO', 'initMarginReq': 0.1663, 'maintMarginReq': 0.1512}
        _cefs = {'ticker': 'CEFS', 'initMarginReq': 0.1648, 'maintMarginReq': 0.1498}
        _ibhb = {'ticker': 'IBHB', 'initMarginReq': 0.2748, 'maintMarginReq': 0.2498}
        _vixm = {'ticker': 'VIXM', 'initMarginReq': 0.2227, 'maintMarginReq': 0.2025}
        _shyl = {'ticker': 'SHYL', 'initMarginReq': 0.2742, 'maintMarginReq': 0.2493}
        _qdec = {'ticker': 'QDEC', 'initMarginReq': 0.2198, 'maintMarginReq': 0.1998}
        _fibr = {'ticker': 'FIBR', 'initMarginReq': 0.2759, 'maintMarginReq': 0.2509}
        _dwus = {'ticker': 'DWUS', 'initMarginReq': 0.1667, 'maintMarginReq': 0.1516}
        _cya = {'ticker': 'CYA', 'initMarginReq': 0.2263, 'maintMarginReq': 0.2058}
        _byld = {'ticker': 'BYLD', 'initMarginReq': 0.2759, 'maintMarginReq': 0.2509}
        _hsrt = {'ticker': 'HSRT', 'initMarginReq': 0.2753, 'maintMarginReq': 0.2503}
        _smig = {'ticker': 'SMIG', 'initMarginReq': 0.2219, 'maintMarginReq': 0.2017}
        _amna = {'ticker': 'AMNA', 'initMarginReq': 0.2500, 'maintMarginReq': 0.2500}
        _azbj = {'ticker': 'AZBJ', 'initMarginReq': 0.2205, 'maintMarginReq': 0.2004}
        _kbwr = {'ticker': 'KBWR', 'initMarginReq': 0.1661, 'maintMarginReq': 0.1510}
        _htab = {'ticker': 'HTAB', 'initMarginReq': 0.2771, 'maintMarginReq': 0.2519}
        _fsz = {'ticker': 'FSZ', 'initMarginReq': 0.1674, 'maintMarginReq': 0.1522}
        _bjun = {'ticker': 'BJUN', 'initMarginReq': 0.1654, 'maintMarginReq': 0.1504}
        _ibmq = {'ticker': 'IBMQ', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _ddiv = {'ticker': 'DDIV', 'initMarginReq': 0.1652, 'maintMarginReq': 0.1502}
        _onof = {'ticker': 'ONOF', 'initMarginReq': 0.2196, 'maintMarginReq': 0.1996}
        _drn = {'ticker': 'DRN', 'initMarginReq': 0.5071, 'maintMarginReq': 0.4610}
        _bnku = {'ticker': 'BNKU', 'initMarginReq': 0.7500, 'maintMarginReq': 0.7500}
        _psci = {'ticker': 'PSCI', 'initMarginReq': 0.1665, 'maintMarginReq': 0.1513}
        _mmtm = {'ticker': 'MMTM', 'initMarginReq': 0.1653, 'maintMarginReq': 0.1503}
        _ufo = {'ticker': 'UFO', 'initMarginReq': 0.1651, 'maintMarginReq': 0.1501}
        _szne = {'ticker': 'SZNE', 'initMarginReq': 0.1665, 'maintMarginReq': 0.1514}
        _djul = {'ticker': 'DJUL', 'initMarginReq': 0.2201, 'maintMarginReq': 0.2001}
        _ibtf = {'ticker': 'IBTF', 'initMarginReq': 0.1654, 'maintMarginReq': 0.1504}
        _pui = {'ticker': 'PUI', 'initMarginReq': 0.1702, 'maintMarginReq': 0.1548}
        _ibtk = {'ticker': 'IBTK', 'initMarginReq': 0.2217, 'maintMarginReq': 0.2015}
        _ibdw = {'ticker': 'IBDW', 'initMarginReq': 0.2217, 'maintMarginReq': 0.2016}
        _arb = {'ticker': 'ARB', 'initMarginReq': 0.1655, 'maintMarginReq': 0.1505}
        _fku = {'ticker': 'FKU', 'initMarginReq': 0.1678, 'maintMarginReq': 0.1526}
        _uapr = {'ticker': 'UAPR', 'initMarginReq': 0.1653, 'maintMarginReq': 0.1503}
        _rfci = {'ticker': 'RFCI', 'initMarginReq': 0.2755, 'maintMarginReq': 0.2505}
        _xjh = {'ticker': 'XJH', 'initMarginReq': 0.2206, 'maintMarginReq': 0.2005}
        _pxj = {'ticker': 'PXJ', 'initMarginReq': 0.2241, 'maintMarginReq': 0.2037}
        _ewo = {'ticker': 'EWO', 'initMarginReq': 0.1667, 'maintMarginReq': 0.1516}
        _ibtb = {'ticker': 'IBTB', 'initMarginReq': 0.2201, 'maintMarginReq': 0.2001}
        _fsmd = {'ticker': 'FSMD', 'initMarginReq': 0.1653, 'maintMarginReq': 0.1503}
        _dynf = {'ticker': 'DYNF', 'initMarginReq': 0.1654, 'maintMarginReq': 0.1504}
        _ibhd = {'ticker': 'IBHD', 'initMarginReq': 0.2730, 'maintMarginReq': 0.2481}
        _armr = {'ticker': 'ARMR', 'initMarginReq': 0.1662, 'maintMarginReq': 0.1511}
        _csf = {'ticker': 'CSF', 'initMarginReq': 0.1653, 'maintMarginReq': 0.1503}
        _labd = {'ticker': 'LABD', 'initMarginReq': 0.7945, 'maintMarginReq': 0.7223}
        _bils = {'ticker': 'BILS', 'initMarginReq': 0.2202, 'maintMarginReq': 0.2001}
        _buzz = {'ticker': 'BUZZ', 'initMarginReq': 0.2187, 'maintMarginReq': 0.1988}
        _dalt = {'ticker': 'DALT', 'initMarginReq': 0.1682, 'maintMarginReq': 0.1529}
        _pffr = {'ticker': 'PFFR', 'initMarginReq': 0.1673, 'maintMarginReq': 0.1521}
        _bsmm = {'ticker': 'BSMM', 'initMarginReq': 0.2755, 'maintMarginReq': 0.2505}
        _bnov = {'ticker': 'BNOV', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _dew = {'ticker': 'DEW', 'initMarginReq': 0.1662, 'maintMarginReq': 0.1510}
        _hips = {'ticker': 'HIPS', 'initMarginReq': 0.1668, 'maintMarginReq': 0.1517}
        _bscu = {'ticker': 'BSCU', 'initMarginReq': 0.2769, 'maintMarginReq': 0.2517}
        _resp = {'ticker': 'RESP', 'initMarginReq': 0.1657, 'maintMarginReq': 0.1506}
        _mrgr = {'ticker': 'MRGR', 'initMarginReq': 0.1649, 'maintMarginReq': 0.1499}
        _eudg = {'ticker': 'EUDG', 'initMarginReq': 0.1682, 'maintMarginReq': 0.1529}
        _spdv = {'ticker': 'SPDV', 'initMarginReq': 0.1659, 'maintMarginReq': 0.1508}
        _acsi = {'ticker': 'ACSI', 'initMarginReq': 0.1641, 'maintMarginReq': 0.1492}
        _spyc = {'ticker': 'SPYC', 'initMarginReq': 0.2221, 'maintMarginReq': 0.2019}
        _ffiu = {'ticker': 'FFIU', 'initMarginReq': 0.1656, 'maintMarginReq': 0.1505}
        _ibdd = {'ticker': 'IBDD', 'initMarginReq': 0.2750, 'maintMarginReq': 0.2500}
        _wbiy = {'ticker': 'WBIY', 'initMarginReq': 0.1646, 'maintMarginReq': 0.1496}
        _hibl = {'ticker': 'HIBL', 'initMarginReq': 0.5834, 'maintMarginReq': 0.5304}
        _jdiv = {'ticker': 'JDIV', 'initMarginReq': 0.1663, 'maintMarginReq': 0.1511}
        _mmlg = {'ticker': 'MMLG', 'initMarginReq': 0.2204, 'maintMarginReq': 0.2004}
        _ovb = {'ticker': 'OVB', 'initMarginReq': 0.2777, 'maintMarginReq': 0.2525}
        _tple = {'ticker': 'TPLE', 'initMarginReq': 0.2202, 'maintMarginReq': 0.2002}
        _evx = {'ticker': 'EVX', 'initMarginReq': 0.1676, 'maintMarginReq': 0.1523}
        _mgmt = {'ticker': 'MGMT', 'initMarginReq': 0.2200, 'maintMarginReq': 0.2000}
        _dura = {'ticker': 'DURA', 'initMarginReq': 0.1668, 'maintMarginReq': 0.1517}
        _vegn = {'ticker': 'VEGN', 'initMarginReq': 0.1648, 'maintMarginReq': 0.1498}
        _uym = {'ticker': 'UYM', 'initMarginReq': 0.3351, 'maintMarginReq': 0.3046}
        _rinf = {'ticker': 'RINF', 'initMarginReq': 0.1008, 'maintMarginReq': 0.0917}
        _noct = {'ticker': 'NOCT', 'initMarginReq': 0.1646, 'maintMarginReq': 0.1496}
        _usep = {'ticker': 'USEP', 'initMarginReq': 0.1651, 'maintMarginReq': 0.1501}
        _azaj = {'ticker': 'AZAJ', 'initMarginReq': 0.2204, 'maintMarginReq': 0.2004}
        _umay = {'ticker': 'UMAY', 'initMarginReq': 0.1656, 'maintMarginReq': 0.1505}
        _bitq = {'ticker': 'BITQ', 'initMarginReq': 0.2570, 'maintMarginReq': 0.2336}
        _sixs = {'ticker': 'SIXS', 'initMarginReq': 0.1647, 'maintMarginReq': 0.1497}
        _napr = {'ticker': 'NAPR', 'initMarginReq': 0.1645, 'maintMarginReq': 0.1496}
        _trnd = {'ticker': 'TRND', 'initMarginReq': 0.1652, 'maintMarginReq': 0.1501}
        _ewus = {'ticker': 'EWUS', 'initMarginReq': 0.1680, 'maintMarginReq': 0.1527}
        _pvi = {'ticker': 'PVI', 'initMarginReq': 0.1649, 'maintMarginReq': 0.1499}
        _soxq = {'ticker': 'SOXQ', 'initMarginReq': 0.2185, 'maintMarginReq': 0.1987}
        _vfmv = {'ticker': 'VFMV', 'initMarginReq': 0.1663, 'maintMarginReq': 0.1512}
        _spvm = {'ticker': 'SPVM', 'initMarginReq': 0.1651, 'maintMarginReq': 0.1501}
        _amtr = {'ticker': 'AMTR', 'initMarginReq': 0.2500, 'maintMarginReq': 0.2500}
        _iigd = {'ticker': 'IIGD', 'initMarginReq': 0.1659, 'maintMarginReq': 0.1508}
        _uoct = {'ticker': 'UOCT', 'initMarginReq': 0.1655, 'maintMarginReq': 0.1505}
        _bsmo = {'ticker': 'BSMO', 'initMarginReq': 0.2751, 'maintMarginReq': 0.2501}
        _iuss = {'ticker': 'IUSS', 'initMarginReq': 0.1655, 'maintMarginReq': 0.1504}
        _tphe = {'ticker': 'TPHE', 'initMarginReq': 0.2218, 'maintMarginReq': 0.2016}
        _csd = {'ticker': 'CSD', 'initMarginReq': 0.1728, 'maintMarginReq': 0.1570}
        _bkch = {'ticker': 'BKCH', 'initMarginReq': 0.2736, 'maintMarginReq': 0.2489}
        _bsmp = {'ticker': 'BSMP', 'initMarginReq': 0.2751, 'maintMarginReq': 0.2501}
        _qdiv = {'ticker': 'QDIV', 'initMarginReq': 0.1661, 'maintMarginReq': 0.1510}
        _flqm = {'ticker': 'FLQM', 'initMarginReq': 0.1658, 'maintMarginReq': 0.1508}
        _ewsc = {'ticker': 'EWSC', 'initMarginReq': 0.1655, 'maintMarginReq': 0.1505}
        _ovt = {'ticker': 'OVT', 'initMarginReq': 0.2213, 'maintMarginReq': 0.2013}
        _tyo = {'ticker': 'TYO', 'initMarginReq': 0.2913, 'maintMarginReq': 0.2648}
        _bsmn = {'ticker': 'BSMN', 'initMarginReq': 0.2746, 'maintMarginReq': 0.2496}
        _qylg = {'ticker': 'QYLG', 'initMarginReq': 0.2191, 'maintMarginReq': 0.1991}
        _recs = {'ticker': 'RECS', 'initMarginReq': 0.1648, 'maintMarginReq': 0.1498}
        _bkse = {'ticker': 'BKSE', 'initMarginReq': 0.1660, 'maintMarginReq': 0.1509}
        _xtl = {'ticker': 'XTL', 'initMarginReq': 0.1656, 'maintMarginReq': 0.1506}
        _midu = {'ticker': 'MIDU', 'initMarginReq': 0.4767, 'maintMarginReq': 0.4334}
        _sent = {'ticker': 'SENT', 'initMarginReq': 0.2188, 'maintMarginReq': 0.1989}
        _vxz = {'ticker': 'VXZ', 'initMarginReq': 0.1669, 'maintMarginReq': 0.1517}
        _lqdb = {'ticker': 'LQDB', 'initMarginReq': 0.2213, 'maintMarginReq': 0.2012}
        _drv = {'ticker': 'DRV', 'initMarginReq': 0.4815, 'maintMarginReq': 0.4377}
        _ifed = {'ticker': 'IFED', 'initMarginReq': 0.2500, 'maintMarginReq': 0.2500}
        _fngs = {'ticker': 'FNGS', 'initMarginReq': 0.2500, 'maintMarginReq': 0.2500}
        _xrlv = {'ticker': 'XRLV', 'initMarginReq': 0.1669, 'maintMarginReq': 0.1517}
        _btec = {'ticker': 'BTEC', 'initMarginReq': 0.1897, 'maintMarginReq': 0.1725}
        _qdpl = {'ticker': 'QDPL', 'initMarginReq': 0.2219, 'maintMarginReq': 0.2018}
        _lbay = {'ticker': 'LBAY', 'initMarginReq': 0.2220, 'maintMarginReq': 0.2018}
        _njul = {'ticker': 'NJUL', 'initMarginReq': 0.2198, 'maintMarginReq': 0.1998}
        _retl = {'ticker': 'RETL', 'initMarginReq': 0.5095, 'maintMarginReq': 0.4632}
        _tpsc = {'ticker': 'TPSC', 'initMarginReq': 0.1651, 'maintMarginReq': 0.1501}
        _bdcz = {'ticker': 'BDCZ', 'initMarginReq': 0.2500, 'maintMarginReq': 0.2500}
        _guru = {'ticker': 'GURU', 'initMarginReq': 0.1657, 'maintMarginReq': 0.1506}
        _wfh = {'ticker': 'WFH', 'initMarginReq': 0.2186, 'maintMarginReq': 0.1987}
        _qmar = {'ticker': 'QMAR', 'initMarginReq': 0.2198, 'maintMarginReq': 0.1998}
        _utes = {'ticker': 'UTES', 'initMarginReq': 0.1682, 'maintMarginReq': 0.1529}
        _jhmt = {'ticker': 'JHMT', 'initMarginReq': 0.1753, 'maintMarginReq': 0.1593}
        _romo = {'ticker': 'ROMO', 'initMarginReq': 0.1655, 'maintMarginReq': 0.1505}
        _dblv = {'ticker': 'DBLV', 'initMarginReq': 0.1660, 'maintMarginReq': 0.1509}
        _spuu = {'ticker': 'SPUU', 'initMarginReq': 0.2638, 'maintMarginReq': 0.2398}
        _pfi = {'ticker': 'PFI', 'initMarginReq': 0.1645, 'maintMarginReq': 0.1496}
        _arcm = {'ticker': 'ARCM', 'initMarginReq': 0.2754, 'maintMarginReq': 0.2504}
        _wiz = {'ticker': 'WIZ', 'initMarginReq': 0.1662, 'maintMarginReq': 0.1511}
        _sfyx = {'ticker': 'SFYX', 'initMarginReq': 0.1663, 'maintMarginReq': 0.1512}
        _sbnd = {'ticker': 'SBND', 'initMarginReq': 0.2760, 'maintMarginReq': 0.2509}
        _fthi = {'ticker': 'FTHI', 'initMarginReq': 0.1660, 'maintMarginReq': 0.1509}
        _pset = {'ticker': 'PSET', 'initMarginReq': 0.1660, 'maintMarginReq': 0.1509}
        _qpx = {'ticker': 'QPX', 'initMarginReq': 0.2194, 'maintMarginReq': 0.1995}
        _qvms = {'ticker': 'QVMS', 'initMarginReq': 0.2201, 'maintMarginReq': 0.2001}
        _vamo = {'ticker': 'VAMO', 'initMarginReq': 0.1643, 'maintMarginReq': 0.1494}
        _lead = {'ticker': 'LEAD', 'initMarginReq': 0.5000, 'maintMarginReq': 0.5000}
        _umar = {'ticker': 'UMAR', 'initMarginReq': 0.1656, 'maintMarginReq': 0.1505}
        _hdg = {'ticker': 'HDG', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _deep = {'ticker': 'DEEP', 'initMarginReq': 0.1635, 'maintMarginReq': 0.1486}
        _dweq = {'ticker': 'DWEQ', 'initMarginReq': 0.1656, 'maintMarginReq': 0.1505}
        _udec = {'ticker': 'UDEC', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _ufeb = {'ticker': 'UFEB', 'initMarginReq': 0.1653, 'maintMarginReq': 0.1503}
        _mmca = {'ticker': 'MMCA', 'initMarginReq': 0.2203, 'maintMarginReq': 0.2002}
        _koct = {'ticker': 'KOCT', 'initMarginReq': 0.1651, 'maintMarginReq': 0.1500}
        _lkor = {'ticker': 'LKOR', 'initMarginReq': 0.1660, 'maintMarginReq': 0.1510}
        _ery = {'ticker': 'ERY', 'initMarginReq': 0.4073, 'maintMarginReq': 0.3763}
        _pscc = {'ticker': 'PSCC', 'initMarginReq': 0.1643, 'maintMarginReq': 0.1494}
        _nrgd = {'ticker': 'NRGD', 'initMarginReq': 0.7500, 'maintMarginReq': 0.7500}
        _homz = {'ticker': 'HOMZ', 'initMarginReq': 0.1665, 'maintMarginReq': 0.1513}
        _oeur = {'ticker': 'OEUR', 'initMarginReq': 0.1686, 'maintMarginReq': 0.1532}
        _pteu = {'ticker': 'PTEU', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _vflq = {'ticker': 'VFLQ', 'initMarginReq': 0.1657, 'maintMarginReq': 0.1506}
        _hewg = {'ticker': 'HEWG', 'initMarginReq': 0.1665, 'maintMarginReq': 0.1514}
        _bsjr = {'ticker': 'BSJR', 'initMarginReq': 0.2733, 'maintMarginReq': 0.2485}
        _java = {'ticker': 'JAVA', 'initMarginReq': 0.2215, 'maintMarginReq': 0.2014}
        _feig = {'ticker': 'FEIG', 'initMarginReq': 0.2212, 'maintMarginReq': 0.2011}
        _wbif = {'ticker': 'WBIF', 'initMarginReq': 0.1651, 'maintMarginReq': 0.1500}
        _pab = {'ticker': 'PAB', 'initMarginReq': 0.2211, 'maintMarginReq': 0.2010}
        _bkhy = {'ticker': 'BKHY', 'initMarginReq': 0.2734, 'maintMarginReq': 0.2485}
        _hyrm = {'ticker': 'HYRM', 'initMarginReq': 0.2730, 'maintMarginReq': 0.2481}
        _zig = {'ticker': 'ZIG', 'initMarginReq': 0.1647, 'maintMarginReq': 0.1498}
        _aqgx = {'ticker': 'AQGX', 'initMarginReq': 0.2196, 'maintMarginReq': 0.1997}
        _shus = {'ticker': 'SHUS', 'initMarginReq': 0.2160, 'maintMarginReq': 0.1963}
        _pxq = {'ticker': 'PXQ', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _udn = {'ticker': 'UDN', 'initMarginReq': 0.2205, 'maintMarginReq': 0.2004}
        _sfig = {'ticker': 'SFIG', 'initMarginReq': 0.1657, 'maintMarginReq': 0.1507}
        _azbo = {'ticker': 'AZBO', 'initMarginReq': 0.2202, 'maintMarginReq': 0.2002}
        _igld = {'ticker': 'IGLD', 'initMarginReq': 1.0000, 'maintMarginReq': 1.0000}
        _mino = {'ticker': 'MINO', 'initMarginReq': 0.2760, 'maintMarginReq': 0.2509}
        _pscf = {'ticker': 'PSCF', 'initMarginReq': 0.1660, 'maintMarginReq': 0.1509}
        _jhms = {'ticker': 'JHMS', 'initMarginReq': 0.1664, 'maintMarginReq': 0.1513}
        _ibhe = {'ticker': 'IBHE', 'initMarginReq': 0.2741, 'maintMarginReq': 0.2492}
        _enor = {'ticker': 'ENOR', 'initMarginReq': 0.3750, 'maintMarginReq': 0.3000}
        _wbii = {'ticker': 'WBII', 'initMarginReq': 0.1658, 'maintMarginReq': 0.1507}
        _wfig = {'ticker': 'WFIG', 'initMarginReq': 0.1660, 'maintMarginReq': 0.1509}
        _mbox = {'ticker': 'MBOX', 'initMarginReq': 0.2214, 'maintMarginReq': 0.2012}
        _jhmh = {'ticker': 'JHMH', 'initMarginReq': 0.1666, 'maintMarginReq': 0.1514}
        _lsst = {'ticker': 'LSST', 'initMarginReq': 0.2755, 'maintMarginReq': 0.2505}
        _azao = {'ticker': 'AZAO', 'initMarginReq': 0.2203, 'maintMarginReq': 0.2003}
        _obnd = {'ticker': 'OBND', 'initMarginReq': 0.2760, 'maintMarginReq': 0.2509}
        _wbig = {'ticker': 'WBIG', 'initMarginReq': 0.1646, 'maintMarginReq': 0.1496}
        _vega = {'ticker': 'VEGA', 'initMarginReq': 0.1656, 'maintMarginReq': 0.1506}
        _tagg = {'ticker': 'TAGG', 'initMarginReq': 0.2213, 'maintMarginReq': 0.2012}
        _pink = {'ticker': 'PINK', 'initMarginReq': 0.2228, 'maintMarginReq': 0.2026}
        _tgrw = {'ticker': 'TGRW', 'initMarginReq': 0.2197, 'maintMarginReq': 0.1997}
        _jhme = {'ticker': 'JHME', 'initMarginReq': 0.1934, 'maintMarginReq': 0.1758}
        _tya = {'ticker': 'TYA', 'initMarginReq': 0.2809, 'maintMarginReq': 0.2554}
        _pbnd = {'ticker': 'PBND', 'initMarginReq': 0.1658, 'maintMarginReq': 0.1507}
        _pbs = {'ticker': 'PBS', 'initMarginReq': 0.1651, 'maintMarginReq': 0.1501}
        _stnc = {'ticker': 'STNC', 'initMarginReq': 0.2220, 'maintMarginReq': 0.2018}
        _nacp = {'ticker': 'NACP', 'initMarginReq': 0.1660, 'maintMarginReq': 0.1509}
        _bsmq = {'ticker': 'BSMQ', 'initMarginReq': 0.2749, 'maintMarginReq': 0.2499}
        _ibth = {'ticker': 'IBTH', 'initMarginReq': 0.1658, 'maintMarginReq': 0.1507}
        _iehs = {'ticker': 'IEHS', 'initMarginReq': 0.1674, 'maintMarginReq': 0.1522}
        _pbsm = {'ticker': 'PBSM', 'initMarginReq': 0.1656, 'maintMarginReq': 0.1506}
        _tbux = {'ticker': 'TBUX', 'initMarginReq': 0.2753, 'maintMarginReq': 0.2503}
        _alty = {'ticker': 'ALTY', 'initMarginReq': 0.1664, 'maintMarginReq': 0.1512}
        _ihyf = {'ticker': 'IHYF', 'initMarginReq': 0.2751, 'maintMarginReq': 0.2501}
        _tdsa = {'ticker': 'TDSA', 'initMarginReq': 0.2208, 'maintMarginReq': 0.2007}
        _roof = {'ticker': 'ROOF', 'initMarginReq': 0.1673, 'maintMarginReq': 0.1521}
        _sims = {'ticker': 'SIMS', 'initMarginReq': 0.1659, 'maintMarginReq': 0.1508}
        _sspx = {'ticker': 'SSPX', 'initMarginReq': 0.2204, 'maintMarginReq': 0.2004}
        _tpor = {'ticker': 'TPOR', 'initMarginReq': 0.4653, 'maintMarginReq': 0.4230}
        _mtgp = {'ticker': 'MTGP', 'initMarginReq': 0.2769, 'maintMarginReq': 0.2517}
        _scdl = {'ticker': 'SCDL', 'initMarginReq': 0.2500, 'maintMarginReq': 0.2500}
        _teng = {'ticker': 'TENG', 'initMarginReq': 0.3308, 'maintMarginReq': 0.3007}
        _pamc = {'ticker': 'PAMC', 'initMarginReq': 0.2211, 'maintMarginReq': 0.2010}
        _hold = {'ticker': 'HOLD', 'initMarginReq': 0.1652, 'maintMarginReq': 0.1501}
        _rffc = {'ticker': 'RFFC', 'initMarginReq': 0.1651, 'maintMarginReq': 0.1501}
        _lfeq = {'ticker': 'LFEQ', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _ieih = {'ticker': 'IEIH', 'initMarginReq': 0.1651, 'maintMarginReq': 0.1501}
        _ciz = {'ticker': 'CIZ', 'initMarginReq': 0.1676, 'maintMarginReq': 0.1524}
        _ubt = {'ticker': 'UBT', 'initMarginReq': 0.2037, 'maintMarginReq': 0.1852}
        _xylg = {'ticker': 'XYLG', 'initMarginReq': 0.2201, 'maintMarginReq': 0.2001}
        _tctl = {'ticker': 'TCTL', 'initMarginReq': 0.1656, 'maintMarginReq': 0.1505}
        _ujul = {'ticker': 'UJUL', 'initMarginReq': 0.1653, 'maintMarginReq': 0.1502}
        _fevr = {'ticker': 'FEVR', 'initMarginReq': 0.2197, 'maintMarginReq': 0.1998}
        _mbnd = {'ticker': 'MBND', 'initMarginReq': 0.2753, 'maintMarginReq': 0.2502}
        _klcd = {'ticker': 'KLCD', 'initMarginReq': 0.1656, 'maintMarginReq': 0.1505}
        _rrh = {'ticker': 'RRH', 'initMarginReq': 0.2693, 'maintMarginReq': 0.2448}
        _jib = {'ticker': 'JIB', 'initMarginReq': 0.2772, 'maintMarginReq': 0.2520}
        _fftg = {'ticker': 'FFTG', 'initMarginReq': 0.1669, 'maintMarginReq': 0.1518}
        _ewco = {'ticker': 'EWCO', 'initMarginReq': 0.1660, 'maintMarginReq': 0.1509}
        _bsce = {'ticker': 'BSCE', 'initMarginReq': 0.2748, 'maintMarginReq': 0.2498}
        _nusa = {'ticker': 'NUSA', 'initMarginReq': 0.2761, 'maintMarginReq': 0.2510}
        _lgov = {'ticker': 'LGOV', 'initMarginReq': 0.2776, 'maintMarginReq': 0.2523}
        _pfig = {'ticker': 'PFIG', 'initMarginReq': 0.1661, 'maintMarginReq': 0.1510}
        _saa = {'ticker': 'SAA', 'initMarginReq': 0.4033, 'maintMarginReq': 0.3667}
        _dfhy = {'ticker': 'DFHY', 'initMarginReq': 0.2758, 'maintMarginReq': 0.2507}
        _fhys = {'ticker': 'FHYS', 'initMarginReq': 0.2745, 'maintMarginReq': 0.2495}
        _scrd = {'ticker': 'SCRD', 'initMarginReq': 0.2767, 'maintMarginReq': 0.2515}
        _pws = {'ticker': 'PWS', 'initMarginReq': 0.1651, 'maintMarginReq': 0.1501}
        _mvrl = {'ticker': 'MVRL', 'initMarginReq': 0.3750, 'maintMarginReq': 0.3750}
        _entr = {'ticker': 'ENTR', 'initMarginReq': 0.1653, 'maintMarginReq': 0.1502}
        _gfgf = {'ticker': 'GFGF', 'initMarginReq': 0.2221, 'maintMarginReq': 0.2019}
        _pez = {'ticker': 'PEZ', 'initMarginReq': 0.1686, 'maintMarginReq': 0.1532}
        _ffsg = {'ticker': 'FFSG', 'initMarginReq': 0.1669, 'maintMarginReq': 0.1517}
        _ibce = {'ticker': 'IBCE', 'initMarginReq': 0.1652, 'maintMarginReq': 0.1502}
        _iwdl = {'ticker': 'IWDL', 'initMarginReq': 0.2500, 'maintMarginReq': 0.2500}
        _avmu = {'ticker': 'AVMU', 'initMarginReq': 0.2753, 'maintMarginReq': 0.2503}
        _womn = {'ticker': 'WOMN', 'initMarginReq': 0.1659, 'maintMarginReq': 0.1508}
        _pval = {'ticker': 'PVAL', 'initMarginReq': 0.2206, 'maintMarginReq': 0.2005}
        _acvf = {'ticker': 'ACVF', 'initMarginReq': 0.2212, 'maintMarginReq': 0.2011}
        _ffhg = {'ticker': 'FFHG', 'initMarginReq': 0.1662, 'maintMarginReq': 0.1511}
        _vpc = {'ticker': 'VPC', 'initMarginReq': 0.1643, 'maintMarginReq': 0.1494}
        _umdd = {'ticker': 'UMDD', 'initMarginReq': 0.4899, 'maintMarginReq': 0.4453}
        _aspy = {'ticker': 'ASPY', 'initMarginReq': 0.2203, 'maintMarginReq': 0.2003}
        _sihy = {'ticker': 'SIHY', 'initMarginReq': 0.2733, 'maintMarginReq': 0.2484}
        _dug = {'ticker': 'DUG', 'initMarginReq': 0.3567, 'maintMarginReq': 0.3243}
        _dbv = {'ticker': 'DBV', 'initMarginReq': 0.2219, 'maintMarginReq': 0.2017}
        _esgs = {'ticker': 'ESGS', 'initMarginReq': 0.1656, 'maintMarginReq': 0.1506}
        _qjun = {'ticker': 'QJUN', 'initMarginReq': 0.2199, 'maintMarginReq': 0.1999}
        _rafe = {'ticker': 'RAFE', 'initMarginReq': 0.1658, 'maintMarginReq': 0.1507}
        _revs = {'ticker': 'REVS', 'initMarginReq': 0.1652, 'maintMarginReq': 0.1502}
        _iigv = {'ticker': 'IIGV', 'initMarginReq': 0.1662, 'maintMarginReq': 0.1511}
        _idiv = {'ticker': 'IDIV', 'initMarginReq': 0.1600, 'maintMarginReq': 0.1454}
        _fedl = {'ticker': 'FEDL', 'initMarginReq': 0.2500, 'maintMarginReq': 0.2500}
        _ewgs = {'ticker': 'EWGS', 'initMarginReq': 0.1678, 'maintMarginReq': 0.1526}
        _fcef = {'ticker': 'FCEF', 'initMarginReq': 0.1668, 'maintMarginReq': 0.1516}
        _uaug = {'ticker': 'UAUG', 'initMarginReq': 0.1650, 'maintMarginReq': 0.1500}
        _mlpo = {'ticker': 'MLPO', 'initMarginReq': 0.2500, 'maintMarginReq': 0.2500}
        _fite = {'ticker': 'FITE', 'initMarginReq': 0.1662, 'maintMarginReq': 0.1511}
        _jmin = {'ticker': 'JMIN', 'initMarginReq': 0.1669, 'maintMarginReq': 0.1517}
        _cws = {'ticker': 'CWS', 'initMarginReq': 0.1669, 'maintMarginReq': 0.1517}
        _thy = {'ticker': 'THY', 'initMarginReq': 0.2205, 'maintMarginReq': 0.2005}
        _usml = {'ticker': 'USML', 'initMarginReq': 0.2500, 'maintMarginReq': 0.2500}
        _xshq = {'ticker': 'XSHQ', 'initMarginReq': 0.1637, 'maintMarginReq': 0.1489}
        _pscd = {'ticker': 'PSCD', 'initMarginReq': 0.1921, 'maintMarginReq': 0.1746}
        _frty = {'ticker': 'FRTY', 'initMarginReq': 0.2223, 'maintMarginReq': 0.2021}
        _tgif = {'ticker': 'TGIF', 'initMarginReq': 0.2763, 'maintMarginReq': 0.2512}
        _kvle = {'ticker': 'KVLE', 'initMarginReq': 0.2223, 'maintMarginReq': 0.2021}
        _marb = {'ticker': 'MARB', 'initMarginReq': 0.1663, 'maintMarginReq': 0.1612}
        _nflt = {'ticker': 'NFLT', 'initMarginReq': 0.1646, 'maintMarginReq': 0.1496}
        _srs = {'ticker': 'SRS', 'initMarginReq': 0.3147, 'maintMarginReq': 0.2863}
        _ujun = {'ticker': 'UJUN', 'initMarginReq': 0.1678, 'maintMarginReq': 0.1526}
        _qspt = {'ticker': 'QSPT', 'initMarginReq': 0.2282, 'maintMarginReq': 0.2075}
        _germ = {'ticker': 'GERM', 'initMarginReq': 0.1697, 'maintMarginReq': 0.1543}
        _fovl = {'ticker': 'FOVL', 'initMarginReq': 0.1722, 'maintMarginReq': 0.1566}
        _xshd = {'ticker': 'XSHD', 'initMarginReq': 0.1722, 'maintMarginReq': 0.1566}
        _qull = {'ticker': 'QULL', 'initMarginReq': 0.2500, 'maintMarginReq': 0.2500}
        _sxqg = {'ticker': 'SXQG', 'initMarginReq': 0.2277, 'maintMarginReq': 0.2077}
        _dfnd = {'ticker': 'DFND', 'initMarginReq': 0.1665, 'maintMarginReq': 0.1614}
        _xweb = {'ticker': 'XWEB', 'initMarginReq': 0.2185, 'maintMarginReq': 0.1986}
        _xjr = {'ticker': 'XJR', 'initMarginReq': 0.2318, 'maintMarginReq': 0.2107}
        _bkui = {'ticker': 'BKUI', 'initMarginReq': 0.2749, 'maintMarginReq': 0.2499}
        _cdx = {'ticker': 'CDX', 'initMarginReq': 0.2762, 'maintMarginReq': 0.2511}
        _want = {'ticker': 'WANT', 'initMarginReq': 0.5798, 'maintMarginReq': 0.5271}
        _glry = {'ticker': 'GLRY', 'initMarginReq': 0.2302, 'maintMarginReq': 0.2093}
        _rwvg = {'ticker': 'RWVG', 'initMarginReq': 0.1692, 'maintMarginReq': 0.1538}
        _dvlu = {'ticker': 'DVLU', 'initMarginReq': 0.1110, 'maintMarginReq': 0.1009}
        _rosc = {'ticker': 'ROSC', 'initMarginReq': 0.1729, 'maintMarginReq': 0.1572}
        _nulc = {'ticker': 'NULC', 'initMarginReq': 0.1708, 'maintMarginReq': 0.1553}
        _clse = {'ticker': 'CLSE', 'initMarginReq': 0.2273, 'maintMarginReq': 0.2066}
        _dxge = {'ticker': 'DXGE', 'initMarginReq': 0.1743, 'maintMarginReq': 0.1585}
        _spxe = {'ticker': 'SPXE', 'initMarginReq': 0.1706, 'maintMarginReq': 0.1551}
        _jusa = {'ticker': 'JUSA', 'initMarginReq': 0.2277, 'maintMarginReq': 0.2070}
        _qcon = {'ticker': 'QCON', 'initMarginReq': 0.2847, 'maintMarginReq': 0.2588}
        _dusl = {'ticker': 'DUSL', 'initMarginReq': 0.5545, 'maintMarginReq': 0.5041}
        _cpi = {'ticker': 'CPI', 'initMarginReq': 0.1668, 'maintMarginReq': 0.1516}
        _rdog = {'ticker': 'RDOG', 'initMarginReq': 0.1699, 'maintMarginReq': 0.1544}
        _sepz = {'ticker': 'SEPZ', 'initMarginReq': 0.2264, 'maintMarginReq': 0.2058}
        _kcca = {'ticker': 'KCCA', 'initMarginReq': 0.2245, 'maintMarginReq': 0.2041}
        _rnsc = {'ticker': 'RNSC', 'initMarginReq': 0.1733, 'maintMarginReq': 0.1575}
        _ovlh = {'ticker': 'OVLH', 'initMarginReq': 0.2236, 'maintMarginReq': 0.2033}
        _jhmf = {'ticker': 'JHMF', 'initMarginReq': 0.1710, 'maintMarginReq': 0.1554}
        _jhmb = {'ticker': 'JHMB', 'initMarginReq': 0.2737, 'maintMarginReq': 0.2488}
        _csa = {'ticker': 'CSA', 'initMarginReq': 0.1728, 'maintMarginReq': 0.1571}
        _alfa = {'ticker': 'ALFA', 'initMarginReq': 0.1784, 'maintMarginReq': 0.1621}
        _htus = {'ticker': 'HTUS', 'initMarginReq': 0.1676, 'maintMarginReq': 0.1523}
        _rbnd = {'ticker': 'RBND', 'initMarginReq': 0.2197, 'maintMarginReq': 0.1997}
        _utsl = {'ticker': 'UTSL', 'initMarginReq': 0.5278, 'maintMarginReq': 0.4798}
        _fcsh = {'ticker': 'FCSH', 'initMarginReq': 0.3297, 'maintMarginReq': 0.2997}
        _wbit = {'ticker': 'WBIT', 'initMarginReq': 0.1711, 'maintMarginReq': 0.1556}
        _pscu = {'ticker': 'PSCU', 'initMarginReq': 0.1692, 'maintMarginReq': 0.1538}
        _xbap = {'ticker': 'XBAP', 'initMarginReq': 0.2263, 'maintMarginReq': 0.2057}
        _egis = {'ticker': 'EGIS', 'initMarginReq': 0.2282, 'maintMarginReq': 0.2075}
        _inmu = {'ticker': 'INMU', 'initMarginReq': 0.2752, 'maintMarginReq': 0.2502}
        _hlge = {'ticker': 'HLGE', 'initMarginReq': 0.2282, 'maintMarginReq': 0.2075}
        _fgm = {'ticker': 'FGM', 'initMarginReq': 0.1707, 'maintMarginReq': 0.1552}
        _ibhf = {'ticker': 'IBHF', 'initMarginReq': 0.2791, 'maintMarginReq': 0.2537}
        _kscd = {'ticker': 'KSCD', 'initMarginReq': 0.1708, 'maintMarginReq': 0.1553}
        _riet = {'ticker': 'RIET', 'initMarginReq': 0.2288, 'maintMarginReq': 0.2080}
        _spax = {'ticker': 'SPAX', 'initMarginReq': 0.2201, 'maintMarginReq': 0.2000}
        _pype = {'ticker': 'PYPE', 'initMarginReq': 0.2500, 'maintMarginReq': 0.2500}
        _snug = {'ticker': 'SNUG', 'initMarginReq': 0.1662, 'maintMarginReq': 0.1511}
        _smcp = {'ticker': 'SMCP', 'initMarginReq': 0.1718, 'maintMarginReq': 0.1562}
        _hymu = {'ticker': 'HYMU', 'initMarginReq': 0.2813, 'maintMarginReq': 0.2557}
        _bscv = {'ticker': 'BSCV', 'initMarginReq': 0.2754, 'maintMarginReq': 0.2504}
        _upw = {'ticker': 'UPW', 'initMarginReq': 0.3488, 'maintMarginReq': 0.3171}
        _jctr = {'ticker': 'JCTR', 'initMarginReq': 0.2278, 'maintMarginReq': 0.2071}
        _ibbq = {'ticker': 'IBBQ', 'initMarginReq': 0.2256, 'maintMarginReq': 0.2051}
        _rnlc = {'ticker': 'RNLC', 'initMarginReq': 0.1714, 'maintMarginReq': 0.1558}
        _sogu = {'ticker': 'SOGU', 'initMarginReq': 0.2088, 'maintMarginReq': 0.1898}
        _clix = {'ticker': 'CLIX', 'initMarginReq': 0.1713, 'maintMarginReq': 0.1558}
        _iwfl = {'ticker': 'IWFL', 'initMarginReq': 0.2500, 'maintMarginReq': 0.2500}
        _tspa = {'ticker': 'TSPA', 'initMarginReq': 0.2280, 'maintMarginReq': 0.2072}
        _spmv = {'ticker': 'SPMV', 'initMarginReq': 0.1692, 'maintMarginReq': 0.1538}
        _qqd = {'ticker': 'QQD', 'initMarginReq': 0.2216, 'maintMarginReq': 0.2014}
        _pscm = {'ticker': 'PSCM', 'initMarginReq': 0.1930, 'maintMarginReq': 0.1755}
        _eshy = {'ticker': 'ESHY', 'initMarginReq': 0.2797, 'maintMarginReq': 0.2543}
        _xrmi = {'ticker': 'XRMI', 'initMarginReq': 0.2255, 'maintMarginReq': 0.2050}
        _bsmr = {'ticker': 'BSMR', 'initMarginReq': 0.2752, 'maintMarginReq': 0.2502}
        _ftxh = {'ticker': 'FTXH', 'initMarginReq': 0.1684, 'maintMarginReq': 0.1531}
        _bsms = {'ticker': 'BSMS', 'initMarginReq': 0.2748, 'maintMarginReq': 0.2498}
        _qdyn = {'ticker': 'QDYN', 'initMarginReq': 0.1725, 'maintMarginReq': 0.1568}
        _jhmu = {'ticker': 'JHMU', 'initMarginReq': 0.1685, 'maintMarginReq': 0.1532}
        _erm = {'ticker': 'ERM', 'initMarginReq': 0.1709, 'maintMarginReq': 0.1554}
        _rek = {'ticker': 'REK', 'initMarginReq': 0.1604, 'maintMarginReq': 0.1458}
        _ylde = {'ticker': 'YLDE', 'initMarginReq': 0.1693, 'maintMarginReq': 0.1539}
        _qls = {'ticker': 'QLS', 'initMarginReq': 0.1672, 'maintMarginReq': 0.1520}
        _psmm = {'ticker': 'PSMM', 'initMarginReq': 0.1676, 'maintMarginReq': 0.1523}
        _esus = {'ticker': 'ESUS', 'initMarginReq': 0.2500, 'maintMarginReq': 0.2500}
        _efnl = {'ticker': 'EFNL', 'initMarginReq': 0.3750, 'maintMarginReq': 0.3000}
        _ecln = {'ticker': 'ECLN', 'initMarginReq': 0.1701, 'maintMarginReq': 0.1546}
        _bsjs = {'ticker': 'BSJS', 'initMarginReq': 0.2806, 'maintMarginReq': 0.2551}
        _azbl = {'ticker': 'AZBL', 'initMarginReq': 0.2210, 'maintMarginReq': 0.2090}
        _totr = {'ticker': 'TOTR', 'initMarginReq': 0.2197, 'maintMarginReq': 0.1998}
        _ewk = {'ticker': 'EWK', 'initMarginReq': 0.1696, 'maintMarginReq': 0.1542}
        _mnm = {'ticker': 'MNM', 'initMarginReq': 0.3626, 'maintMarginReq': 0.3297}
        _ujb = {'ticker': 'UJB', 'initMarginReq': 0.5689, 'maintMarginReq': 0.5172}
        _rokt = {'ticker': 'ROKT', 'initMarginReq': 0.1724, 'maintMarginReq': 0.1567}
        _reit = {'ticker': 'REIT', 'initMarginReq': 0.2254, 'maintMarginReq': 0.2049}
        _spxb = {'ticker': 'SPXB', 'initMarginReq': 0.1648, 'maintMarginReq': 0.1498}
        _rndv = {'ticker': 'RNDV', 'initMarginReq': 0.1707, 'maintMarginReq': 0.1552}
        _oppx = {'ticker': 'OPPX', 'initMarginReq': 0.2274, 'maintMarginReq': 0.2068}
        _sdei = {'ticker': 'SDEI', 'initMarginReq': 0.2277, 'maintMarginReq': 0.2070}
        _lrnz = {'ticker': 'LRNZ', 'initMarginReq': 0.2373, 'maintMarginReq': 0.2157}
        _hylv = {'ticker': 'HYLV', 'initMarginReq': 0.2780, 'maintMarginReq': 0.2527}
        _ssly = {'ticker': 'SSLY', 'initMarginReq': 0.1739, 'maintMarginReq': 0.1581}
        _demz = {'ticker': 'DEMZ', 'initMarginReq': 0.2272, 'maintMarginReq': 0.2065}
        _jhma = {'ticker': 'JHMA', 'initMarginReq': 0.1725, 'maintMarginReq': 0.1568}
        _sqlv = {'ticker': 'SQLV', 'initMarginReq': 0.1734, 'maintMarginReq': 0.1577}
        _clds = {'ticker': 'CLDS', 'initMarginReq': 0.2998, 'maintMarginReq': 0.2725}
        _hewu = {'ticker': 'HEWU', 'initMarginReq': 0.1711, 'maintMarginReq': 0.1556}
        _gsig = {'ticker': 'GSIG', 'initMarginReq': 0.2201, 'maintMarginReq': 0.2001}
        _iwml = {'ticker': 'IWML', 'initMarginReq': 0.2500, 'maintMarginReq': 0.2500}
        _qqqa = {'ticker': 'QQQA', 'initMarginReq': 0.2291, 'maintMarginReq': 0.2083}
        _bsmt = {'ticker': 'BSMT', 'initMarginReq': 0.2747, 'maintMarginReq': 0.2498}
        _rnmc = {'ticker': 'RNMC', 'initMarginReq': 0.1731, 'maintMarginReq': 0.1573}
        _eaok = {'ticker': 'EAOK', 'initMarginReq': 0.1663, 'maintMarginReq': 0.1511}
        _ftds = {'ticker': 'FTDS', 'initMarginReq': 0.1724, 'maintMarginReq': 0.1568}
        _dboc = {'ticker': 'DBOC', 'initMarginReq': 0.2252, 'maintMarginReq': 0.2047}
        _jhcb = {'ticker': 'JHCB', 'initMarginReq': 0.2198, 'maintMarginReq': 0.1998}
        _sef = {'ticker': 'SEF', 'initMarginReq': 0.1603, 'maintMarginReq': 0.1457}
        _tyd = {'ticker': 'TYD', 'initMarginReq': 0.2919, 'maintMarginReq': 0.2654}
        _psmj = {'ticker': 'PSMJ', 'initMarginReq': 0.2224, 'maintMarginReq': 0.2021}
        _ibti = {'ticker': 'IBTI', 'initMarginReq': 0.1642, 'maintMarginReq': 0.1492}
        _rtai = {'ticker': 'RTAI', 'initMarginReq': 0.2817, 'maintMarginReq': 0.2561}
        _gk = {'ticker': 'GK', 'initMarginReq': 0.2314, 'maintMarginReq': 0.2104}
        _mtul = {'ticker': 'MTUL', 'initMarginReq': 0.2500, 'maintMarginReq': 0.2500}
        _fehy = {'ticker': 'FEHY', 'initMarginReq': 0.2796, 'maintMarginReq': 0.2542}
        _usbf = {'ticker': 'USBF', 'initMarginReq': 0.2195, 'maintMarginReq': 0.1996}
        _adfi = {'ticker': 'ADFI', 'initMarginReq': 0.2760, 'maintMarginReq': 0.2509}
        _uxi = {'ticker': 'UXI', 'initMarginReq': 0.3616, 'maintMarginReq': 0.3287}
        _ust = {'ticker': 'UST', 'initMarginReq': 0.1956, 'maintMarginReq': 0.1778}
        _bout = {'ticker': 'BOUT', 'initMarginReq': 0.1711, 'maintMarginReq': 0.1555}
        _iedi = {'ticker': 'IEDI', 'initMarginReq': 0.1710, 'maintMarginReq': 0.1555}
        _xpnd = {'ticker': 'XPND', 'initMarginReq': 0.2318, 'maintMarginReq': 0.2107}
        _ibtj = {'ticker': 'IBTJ', 'initMarginReq': 0.1642, 'maintMarginReq': 0.1493}
        _iecs = {'ticker': 'IECS', 'initMarginReq': 0.1675, 'maintMarginReq': 0.1523}
        _elqd = {'ticker': 'ELQD', 'initMarginReq': 0.3297, 'maintMarginReq': 0.2997}
        _psmo = {'ticker': 'PSMO', 'initMarginReq': 0.2237, 'maintMarginReq': 0.2033}
        _dbeh = {'ticker': 'DBEH', 'initMarginReq': 0.1680, 'maintMarginReq': 0.1527}
        _psmr = {'ticker': 'PSMR', 'initMarginReq': 0.2244, 'maintMarginReq': 0.2040}
        _sfyf = {'ticker': 'SFYF', 'initMarginReq': 0.1931, 'maintMarginReq': 0.1756}
        _hyup = {'ticker': 'HYUP', 'initMarginReq': 0.2805, 'maintMarginReq': 0.2550}
        _feus = {'ticker': 'FEUS', 'initMarginReq': 0.2281, 'maintMarginReq': 0.2073}
        _minn = {'ticker': 'MINN', 'initMarginReq': 0.6000, 'maintMarginReq': 0.5000}
        _maga = {'ticker': 'MAGA', 'initMarginReq': 0.1724, 'maintMarginReq': 0.1567}
        _lyfe = {'ticker': 'LYFE', 'initMarginReq': 0.2297, 'maintMarginReq': 0.2088}
        _hsmv = {'ticker': 'HSMV', 'initMarginReq': 0.1709, 'maintMarginReq': 0.1554}
        _skf = {'ticker': 'SKF', 'initMarginReq': 0.3113, 'maintMarginReq': 0.2830}
        _jhpi = {'ticker': 'JHPI', 'initMarginReq': 0.2769, 'maintMarginReq': 0.2517}
        _spak = {'ticker': 'SPAK', 'initMarginReq': 0.2264, 'maintMarginReq': 0.2058}
        _bbc = {'ticker': 'BBC', 'initMarginReq': 0.2134, 'maintMarginReq': 0.1940}
        _amom = {'ticker': 'AMOM', 'initMarginReq': 0.1727, 'maintMarginReq': 0.1570}
        _augz = {'ticker': 'AUGZ', 'initMarginReq': 0.2253, 'maintMarginReq': 0.2048}
        _xbjl = {'ticker': 'XBJL', 'initMarginReq': 0.2258, 'maintMarginReq': 0.2053}
        _vabs = {'ticker': 'VABS', 'initMarginReq': 0.2197, 'maintMarginReq': 0.1997}
        _flqs = {'ticker': 'FLQS', 'initMarginReq': 0.1727, 'maintMarginReq': 0.1570}
        _jhcs = {'ticker': 'JHCS', 'initMarginReq': 0.1722, 'maintMarginReq': 0.1565}
        _qmn = {'ticker': 'QMN', 'initMarginReq': 0.1657, 'maintMarginReq': 0.1506}
        _plrg = {'ticker': 'PLRG', 'initMarginReq': 0.2281, 'maintMarginReq': 0.2074}
        _pill = {'ticker': 'PILL', 'initMarginReq': 0.5276, 'maintMarginReq': 0.4796}
        _xtjl = {'ticker': 'XTJL', 'initMarginReq': 0.2279, 'maintMarginReq': 0.2072}
        _flrg = {'ticker': 'FLRG', 'initMarginReq': 0.2283, 'maintMarginReq': 0.2075}
        _qtjl = {'ticker': 'QTJL', 'initMarginReq': 0.2298, 'maintMarginReq': 0.2089}
        _rew = {'ticker': 'REW', 'initMarginReq': 0.3343, 'maintMarginReq': 0.3039}
        _gldb = {'ticker': 'GLDB', 'initMarginReq': 0.2170, 'maintMarginReq': 0.1973}
        _ovm = {'ticker': 'OVM', 'initMarginReq': 0.2756, 'maintMarginReq': 0.2505}
        _jhmc = {'ticker': 'JHMC', 'initMarginReq': 0.1737, 'maintMarginReq': 0.1579}
        _pex = {'ticker': 'PEX', 'initMarginReq': 1.0000, 'maintMarginReq': 1.0000}
        _psmc = {'ticker': 'PSMC', 'initMarginReq': 0.1669, 'maintMarginReq': 0.1517}
        _imlp = {'ticker': 'IMLP', 'initMarginReq': 0.2500, 'maintMarginReq': 0.2500}
        _ftqi = {'ticker': 'FTQI', 'initMarginReq': 0.1702, 'maintMarginReq': 0.1547}
        _avsc = {'ticker': 'AVSC', 'initMarginReq': 0.2310, 'maintMarginReq': 0.2100}
        _ucc = {'ticker': 'UCC', 'initMarginReq': 0.3579, 'maintMarginReq': 0.3253}
        _pscw = {'ticker': 'PSCW', 'initMarginReq': 0.2235, 'maintMarginReq': 0.2032}
        _zecp = {'ticker': 'ZECP', 'initMarginReq': 0.2256, 'maintMarginReq': 0.2051}
        _smi = {'ticker': 'SMI', 'initMarginReq': 0.2748, 'maintMarginReq': 0.2498}
        _jhmi = {'ticker': 'JHMI', 'initMarginReq': 0.1727, 'maintMarginReq': 0.1570}
        _bbp = {'ticker': 'BBP', 'initMarginReq': 0.1692, 'maintMarginReq': 0.1538}
        _julz = {'ticker': 'JULZ', 'initMarginReq': 0.2260, 'maintMarginReq': 0.2054}
        _bsmu = {'ticker': 'BSMU', 'initMarginReq': 0.2741, 'maintMarginReq': 0.2492}
        _lopp = {'ticker': 'LOPP', 'initMarginReq': 0.2292, 'maintMarginReq': 0.2084}
        _mig = {'ticker': 'MIG', 'initMarginReq': 0.2201, 'maintMarginReq': 0.2001}
        _bsmv = {'ticker': 'BSMV', 'initMarginReq': 0.2743, 'maintMarginReq': 0.2493}
        _psfm = {'ticker': 'PSFM', 'initMarginReq': 0.2259, 'maintMarginReq': 0.2054}
        _bnkd = {'ticker': 'BNKD', 'initMarginReq': 0.7500, 'maintMarginReq': 0.7500}
        _myy = {'ticker': 'MYY', 'initMarginReq': 0.1437, 'maintMarginReq': 0.1307}
        _tmdv = {'ticker': 'TMDV', 'initMarginReq': 0.1696, 'maintMarginReq': 0.1541}
        _xjun = {'ticker': 'XJUN', 'initMarginReq': 0.2230, 'maintMarginReq': 0.2027}
        _azal = {'ticker': 'AZAL', 'initMarginReq': 0.2252, 'maintMarginReq': 0.2047}
        _qarp = {'ticker': 'QARP', 'initMarginReq': 0.1705, 'maintMarginReq': 0.1550}
        _dbja = {'ticker': 'DBJA', 'initMarginReq': 0.2262, 'maintMarginReq': 0.2057}
        _mide = {'ticker': 'MIDE', 'initMarginReq': 0.2314, 'maintMarginReq': 0.2104}
        _fsig = {'ticker': 'FSIG', 'initMarginReq': 0.2201, 'maintMarginReq': 0.2001}
        _ibhg = {'ticker': 'IBHG', 'initMarginReq': 0.2795, 'maintMarginReq': 0.2541}
        _ieme = {'ticker': 'IEME', 'initMarginReq': 0.1724, 'maintMarginReq': 0.1567}
        _bis = {'ticker': 'BIS', 'initMarginReq': 0.3379, 'maintMarginReq': 0.2072}
        _spuc = {'ticker': 'SPUC', 'initMarginReq': 0.2278, 'maintMarginReq': 0.2071}
        _tsja = {'ticker': 'TSJA', 'initMarginReq': 0.2283, 'maintMarginReq': 0.2075}
        _qrmi = {'ticker': 'QRMI', 'initMarginReq': 0.2264, 'maintMarginReq': 0.2058}
        _qrft = {'ticker': 'QRFT', 'initMarginReq': 0.1712, 'maintMarginReq': 0.1556}
        _fmny = {'ticker': 'FMNY', 'initMarginReq': 0.2761, 'maintMarginReq': 0.2510}
        _roro = {'ticker': 'RORO', 'initMarginReq': 0.2180, 'maintMarginReq': 0.1981}
        _bsjt = {'ticker': 'BSJT', 'initMarginReq': 0.2814, 'maintMarginReq': 0.2558}
        _qtap = {'ticker': 'QTAP', 'initMarginReq': 0.2304, 'maintMarginReq': 0.2094}
        _dbgr = {'ticker': 'DBGR', 'initMarginReq': 0.1723, 'maintMarginReq': 0.1566}
        _spxn = {'ticker': 'SPXN', 'initMarginReq': 0.1710, 'maintMarginReq': 0.1555}
        _ffnd = {'ticker': 'FFND', 'initMarginReq': 0.2338, 'maintMarginReq': 0.2125}
        _smle = {'ticker': 'SMLE', 'initMarginReq': 0.2315, 'maintMarginReq': 0.2105}
        _gbdv = {'ticker': 'GBDV', 'initMarginReq': 0.1677, 'maintMarginReq': 0.1525}
        _scc = {'ticker': 'SCC', 'initMarginReq': 0.3059, 'maintMarginReq': 0.2781}
        _aaa = {'ticker': 'AAA', 'initMarginReq': 0.2199, 'maintMarginReq': 0.1999}
        _boss = {'ticker': 'BOSS', 'initMarginReq': 0.1741, 'maintMarginReq': 0.1583}
        _psfj = {'ticker': 'PSFJ', 'initMarginReq': 0.2217, 'maintMarginReq': 0.2015}
        _pgro = {'ticker': 'PGRO', 'initMarginReq': 0.2287, 'maintMarginReq': 0.2079}
        _spxt = {'ticker': 'SPXT', 'initMarginReq': 0.1702, 'maintMarginReq': 0.1547}
        _midf = {'ticker': 'MIDF', 'initMarginReq': 0.1728, 'maintMarginReq': 0.1571}
        _hytr = {'ticker': 'HYTR', 'initMarginReq': 0.2737, 'maintMarginReq': 0.2489}
        _heet = {'ticker': 'HEET', 'initMarginReq': 0.2275, 'maintMarginReq': 0.2068}
        _bul = {'ticker': 'BUL', 'initMarginReq': 0.1738, 'maintMarginReq': 0.1580}
        _smdy = {'ticker': 'SMDY', 'initMarginReq': 0.1732, 'maintMarginReq': 0.1574}
        _iefn = {'ticker': 'IEFN', 'initMarginReq': 0.1703, 'maintMarginReq': 0.1548}
        _dwpp = {'ticker': 'DWPP', 'initMarginReq': 0.1705, 'maintMarginReq': 0.1550}
        _eqop = {'ticker': 'EQOP', 'initMarginReq': 0.2299, 'maintMarginReq': 0.2090}
        _cldl = {'ticker': 'CLDL', 'initMarginReq': 0.3671, 'maintMarginReq': 0.3337}
        _tpay = {'ticker': 'TPAY', 'initMarginReq': 0.1771, 'maintMarginReq': 0.1610}
        _uslb = {'ticker': 'USLB', 'initMarginReq': 0.1709, 'maintMarginReq': 0.1554}
        _dwmc = {'ticker': 'DWMC', 'initMarginReq': 0.1741, 'maintMarginReq': 0.1583}
        _xdsq = {'ticker': 'XDSQ', 'initMarginReq': 0.2278, 'maintMarginReq': 0.2071}
        _tsoc = {'ticker': 'TSOC', 'initMarginReq': 0.2276, 'maintMarginReq': 0.2070}
        _berz = {'ticker': 'BERZ', 'initMarginReq': 0.7500, 'maintMarginReq': 0.7500}
        _bkus = {'ticker': 'BKUS', 'initMarginReq': 0.2277, 'maintMarginReq': 0.2070}
        _mbbb = {'ticker': 'MBBB', 'initMarginReq': 0.2201, 'maintMarginReq': 0.2001}
        _qed = {'ticker': 'QED', 'initMarginReq': 0.1670, 'maintMarginReq': 0.1518}
        _usi = {'ticker': 'USI', 'initMarginReq': 0.1649, 'maintMarginReq': 0.1499}
        _xdqq = {'ticker': 'XDQQ', 'initMarginReq': 0.2296, 'maintMarginReq': 0.2088}
        _uge = {'ticker': 'UGE', 'initMarginReq': 0.3559, 'maintMarginReq': 0.3236}
        _ovs = {'ticker': 'OVS', 'initMarginReq': 0.1740, 'maintMarginReq': 0.1582}
        _dsoc = {'ticker': 'DSOC', 'initMarginReq': 0.2280, 'maintMarginReq': 0.2073}
        _xtap = {'ticker': 'XTAP', 'initMarginReq': 0.2288, 'maintMarginReq': 0.2080}
        _fltn = {'ticker': 'FLTN', 'initMarginReq': 0.2708, 'maintMarginReq': 0.2462}
        _bad = {'ticker': 'BAD', 'initMarginReq': 0.2290, 'maintMarginReq': 0.2082}
        _vnmc = {'ticker': 'VNMC', 'initMarginReq': 0.2285, 'maintMarginReq': 0.2077}
        _lvol = {'ticker': 'LVOL', 'initMarginReq': 0.2260, 'maintMarginReq': 0.2055}
        _iqm = {'ticker': 'IQM', 'initMarginReq': 0.1743, 'maintMarginReq': 0.1584}
        _indf = {'ticker': 'INDF', 'initMarginReq': 0.2276, 'maintMarginReq': 0.2069}
        _decz = {'ticker': 'DECZ', 'initMarginReq': 0.2258, 'maintMarginReq': 0.2053}
        _ecoz = {'ticker': 'ECOZ', 'initMarginReq': 0.1717, 'maintMarginReq': 0.1561}
        _ibtl = {'ticker': 'IBTL', 'initMarginReq': 0.2733, 'maintMarginReq': 0.2485}
        _rspy = {'ticker': 'RSPY', 'initMarginReq': 0.2275, 'maintMarginReq': 0.2068}
        _qqc = {'ticker': 'QQC', 'initMarginReq': 0.2260, 'maintMarginReq': 0.2054}
        _syus = {'ticker': 'SYUS', 'initMarginReq': 0.2288, 'maintMarginReq': 0.2080}
        _bedz = {'ticker': 'BEDZ', 'initMarginReq': 0.2357, 'maintMarginReq': 0.2143}
        _jojo = {'ticker': 'JOJO', 'initMarginReq': 0.2238, 'maintMarginReq': 0.2035}
        _cbse = {'ticker': 'CBSE', 'initMarginReq': 0.2320, 'maintMarginReq': 0.2109}
        _stlv = {'ticker': 'STLV', 'initMarginReq': 0.1706, 'maintMarginReq': 0.1551}
        _rwgv = {'ticker': 'RWGV', 'initMarginReq': 0.1736, 'maintMarginReq': 0.1578}
        _smdd = {'ticker': 'SMDD', 'initMarginReq': 0.4582, 'maintMarginReq': 0.4165}
        _hval = {'ticker': 'HVAL', 'initMarginReq': 0.2284, 'maintMarginReq': 0.2077}
        _pfut = {'ticker': 'PFUT', 'initMarginReq': 0.2292, 'maintMarginReq': 0.2084}
        _sbb = {'ticker': 'SBB', 'initMarginReq': 0.1541, 'maintMarginReq': 0.1401}
        _spxz = {'ticker': 'SPXZ', 'initMarginReq': 0.2278, 'maintMarginReq': 0.2071}
        _xdap = {'ticker': 'XDAP', 'initMarginReq': 0.2289, 'maintMarginReq': 0.2081}
        _octz = {'ticker': 'OCTZ', 'initMarginReq': 0.2253, 'maintMarginReq': 0.2048}
        _escr = {'ticker': 'ESCR', 'initMarginReq': 0.1641, 'maintMarginReq': 0.1492}
        _hyin = {'ticker': 'HYIN', 'initMarginReq': 0.2316, 'maintMarginReq': 0.2106}
        _esgy = {'ticker': 'ESGY', 'initMarginReq': 0.2294, 'maintMarginReq': 0.2085}
        _eaom = {'ticker': 'EAOM', 'initMarginReq': 0.1668, 'maintMarginReq': 0.1517}
        _aprz = {'ticker': 'APRZ', 'initMarginReq': 0.2254, 'maintMarginReq': 0.2049}
        _mid = {'ticker': 'MID', 'initMarginReq': 0.2331, 'maintMarginReq': 0.2119}
        _pldr = {'ticker': 'PLDR', 'initMarginReq': 0.2273, 'maintMarginReq': 0.2066}
        _ivlc = {'ticker': 'IVLC', 'initMarginReq': 0.2278, 'maintMarginReq': 0.2071}
        _psfo = {'ticker': 'PSFO', 'initMarginReq': 0.2243, 'maintMarginReq': 0.2039}
        _pltl = {'ticker': 'PLTL', 'initMarginReq': 0.2316, 'maintMarginReq': 0.2105}
        _nvq = {'ticker': 'NVQ', 'initMarginReq': 0.2299, 'maintMarginReq': 0.2090}
        _sdga = {'ticker': 'SDGA', 'initMarginReq': 0.1684, 'maintMarginReq': 0.1531}
        _fsst = {'ticker': 'FSST', 'initMarginReq': 0.2292, 'maintMarginReq': 0.2083}
        _nscs = {'ticker': 'NSCS', 'initMarginReq': 0.2320, 'maintMarginReq': 0.2109}
        _marz = {'ticker': 'MARZ', 'initMarginReq': 0.2255, 'maintMarginReq': 0.2050}
        _virs = {'ticker': 'VIRS', 'initMarginReq': 0.2245, 'maintMarginReq': 0.2041}
        _jre = {'ticker': 'JRE', 'initMarginReq': 0.2251, 'maintMarginReq': 0.2046}
        _pscq = {'ticker': 'PSCQ', 'initMarginReq': 0.2226, 'maintMarginReq': 0.2023}
        _hdiv = {'ticker': 'HDIV', 'initMarginReq': 0.1686, 'maintMarginReq': 0.1532}
        _ssg = {'ticker': 'SSG', 'initMarginReq': 0.4137, 'maintMarginReq': 0.3760}
        _tfjl = {'ticker': 'TFJL', 'initMarginReq': 0.2744, 'maintMarginReq': 0.2494}
        _tbjl = {'ticker': 'TBJL', 'initMarginReq': 0.2730, 'maintMarginReq': 0.2482}
        _cbls = {'ticker': 'CBLS', 'initMarginReq': 0.2262, 'maintMarginReq': 0.2056}
        _aflg = {'ticker': 'AFLG', 'initMarginReq': 0.1709, 'maintMarginReq': 0.1554}
        _itan = {'ticker': 'ITAN', 'initMarginReq': 0.2288, 'maintMarginReq': 0.2080}
        _pscj = {'ticker': 'PSCJ', 'initMarginReq': 0.2205, 'maintMarginReq': 0.2005}
        _xdjl = {'ticker': 'XDJL', 'initMarginReq': 0.2278, 'maintMarginReq': 0.2071}
        _nwlg = {'ticker': 'NWLG', 'initMarginReq': 0.2289, 'maintMarginReq': 0.2081}
        _usvt = {'ticker': 'USVT', 'initMarginReq': 0.2319, 'maintMarginReq': 0.2108}
        _mayz = {'ticker': 'MAYZ', 'initMarginReq': 0.2254, 'maintMarginReq': 0.2049}
        _janz = {'ticker': 'JANZ', 'initMarginReq': 0.2266, 'maintMarginReq': 0.2060}
        _dsja = {'ticker': 'DSJA', 'initMarginReq': 0.2280, 'maintMarginReq': 0.2073}
        _sdd = {'ticker': 'SDD', 'initMarginReq': 0.3462, 'maintMarginReq': 0.3147}
        _amer = {'ticker': 'AMER', 'initMarginReq': 0.2282, 'maintMarginReq': 0.2074}
        _rec = {'ticker': 'REC', 'initMarginReq': 0.2202, 'maintMarginReq': 0.2001}
        _wwow = {'ticker': 'WWOW', 'initMarginReq': 0.2325, 'maintMarginReq': 0.2114}
        _pexl = {'ticker': 'PEXL', 'initMarginReq': 0.1741, 'maintMarginReq': 0.1583}
        _trdf = {'ticker': 'TRDF', 'initMarginReq': 0.2200, 'maintMarginReq': 0.2000}
        _qclr = {'ticker': 'QCLR', 'initMarginReq': 0.2201, 'maintMarginReq': 0.2001}
        _spxv = {'ticker': 'SPXV', 'initMarginReq': 0.1713, 'maintMarginReq': 0.1557}
        _wil = {'ticker': 'WIL', 'initMarginReq': 1.0000, 'maintMarginReq': 1.0000}
        _xclr = {'ticker': 'XCLR', 'initMarginReq': 0.2201, 'maintMarginReq': 0.2001}
        _vsl = {'ticker': 'VSL', 'initMarginReq': 0.1698, 'maintMarginReq': 0.1544}
        _dwat = {'ticker': 'DWAT', 'initMarginReq': 0.1678, 'maintMarginReq': 0.1526}
        _junz = {'ticker': 'JUNZ', 'initMarginReq': 0.2257, 'maintMarginReq': 0.2052}
        _cfcv = {'ticker': 'CFCV', 'initMarginReq': 0.1704, 'maintMarginReq': 0.1549}
        _lopx = {'ticker': 'LOPX', 'initMarginReq': 0.2319, 'maintMarginReq': 0.2109}
        _fldz = {'ticker': 'FLDZ', 'initMarginReq': 0.3439, 'maintMarginReq': 0.3127}
        _nife = {'ticker': 'NIFE', 'initMarginReq': 0.1763, 'maintMarginReq': 0.1603}
        _jfwd = {'ticker': 'JFWD', 'initMarginReq': 0.2338, 'maintMarginReq': 0.2126}
        _febz = {'ticker': 'FEBZ', 'initMarginReq': 0.2259, 'maintMarginReq': 0.2054}
        _rxd = {'ticker': 'RXD', 'initMarginReq': 0.3185, 'maintMarginReq': 0.2895}
        _fedx = {'ticker': 'FEDX', 'initMarginReq': 0.2273, 'maintMarginReq': 0.2067}
        _gblo = {'ticker': 'GBLO', 'initMarginReq': 0.2241, 'maintMarginReq': 0.2037}
        _wgro = {'ticker': 'WGRO', 'initMarginReq': 0.2296, 'maintMarginReq': 0.2087}
        _ooto = {'ticker': 'OOTO', 'initMarginReq': 0.3825, 'maintMarginReq': 0.3477}
        _xtr = {'ticker': 'XTR', 'initMarginReq': 0.2202, 'maintMarginReq': 0.2002}
        _mjus = {'ticker': 'MJUS', 'initMarginReq': 0.2264, 'maintMarginReq': 0.2058}
        _maax = {'ticker': 'MAAX', 'initMarginReq': 0.2763, 'maintMarginReq': 0.2512}
        _fivr = {'ticker': 'FIVR', 'initMarginReq': 0.2236, 'maintMarginReq': 0.2033}
        _ggrw = {'ticker': 'GGRW', 'initMarginReq': 0.2317, 'maintMarginReq': 0.2107}
        _mzz = {'ticker': 'MZZ', 'initMarginReq': 0.3009, 'maintMarginReq': 0.2735}
        _useq = {'ticker': 'USEQ', 'initMarginReq': 0.1717, 'maintMarginReq': 0.1560}
        _rodi = {'ticker': 'RODI', 'initMarginReq': 0.2500, 'maintMarginReq': 0.2500}
        _afsm = {'ticker': 'AFSM', 'initMarginReq': 0.1739, 'maintMarginReq': 0.1581}
        _weix = {'ticker': 'WEIX', 'initMarginReq': 0.2253, 'maintMarginReq': 0.2048}
        _afmc = {'ticker': 'AFMC', 'initMarginReq': 0.1739, 'maintMarginReq': 0.1581}
        _szk = {'ticker': 'SZK', 'initMarginReq': 0.3044, 'maintMarginReq': 0.2767}
        _liv = {'ticker': 'LIV', 'initMarginReq': 0.2300, 'maintMarginReq': 0.2091}
        _smn = {'ticker': 'SMN', 'initMarginReq': 0.3056, 'maintMarginReq': 0.2778}
        _sij = {'ticker': 'SIJ', 'initMarginReq': 0.3029, 'maintMarginReq': 0.2753}
        _sdp = {'ticker': 'SDP', 'initMarginReq': 0.3165, 'maintMarginReq': 0.2877}
        _qtr = {'ticker': 'QTR', 'initMarginReq': 0.2202, 'maintMarginReq': 0.2002}
        _ltl = {'ticker': 'LTL', 'initMarginReq': 0.3504, 'maintMarginReq': 0.3186}
        _skyu = {'ticker': 'SKYU', 'initMarginReq': 0.3671, 'maintMarginReq': 0.3338}
        _trpl = {'ticker': 'TRPL', 'initMarginReq': 0.2266, 'maintMarginReq': 0.2060}
        _stlg = {'ticker': 'STLG', 'initMarginReq': 0.1723, 'maintMarginReq': 0.1567}
        _eeh = {'ticker': 'EEH', 'initMarginReq': 0.2500, 'maintMarginReq': 0.2500}
        _hhh = {'ticker': 'HHH', 'initMarginReq': 0.2339, 'maintMarginReq': 0.2126}
        _aggh = {'ticker': 'AGGH', 'initMarginReq': 0.2184, 'maintMarginReq': 0.1986}
        _dspc = {'ticker': 'DSPC', 'initMarginReq': 0.2436, 'maintMarginReq': 0.2215}
        _gbgr = {'ticker': 'GBGR', 'initMarginReq': 0.2372, 'maintMarginReq': 0.2156}
        _epre = {'ticker': 'EPRE', 'initMarginReq': 0.2275, 'maintMarginReq': 0.2068}
        _ailv = {'ticker': 'AILV', 'initMarginReq': 0.2265, 'maintMarginReq': 0.2059}
        _ailg = {'ticker': 'AILG', 'initMarginReq': 0.2307, 'maintMarginReq': 0.2098}
        _xhyc = {'ticker': 'XHYC', 'initMarginReq': 0.2802, 'maintMarginReq': 0.2548}
        _xhyh = {'ticker': 'XHYH', 'initMarginReq': 0.2804, 'maintMarginReq': 0.2549}
        _xhyt = {'ticker': 'XHYT', 'initMarginReq': 0.2791, 'maintMarginReq': 0.2537}
        _m = {'ticker': 'M', 'initMarginReq': 0.2834, 'maintMarginReq': 0.2577}
        _msft = {'ticker': 'MSFT', 'initMarginReq': 0.1696, 'maintMarginReq': 0.1542}
        _xhyd = {'ticker': 'XHYD', 'initMarginReq': 0.2788, 'maintMarginReq': 0.2535}
        _dwx = {'ticker': 'DWX', 'initMarginReq': 1.0000, 'maintMarginReq': 1.0000}
        _eem = {'ticker': 'EEM', 'initMarginReq': 1.0000, 'maintMarginReq': 1.0000}
        _vgk = {'ticker': 'VGK', 'initMarginReq': 1.0000, 'maintMarginReq': 1.0000}
        _vpl = {'ticker': 'VPL', 'initMarginReq': 1.0000, 'maintMarginReq': 1.0000}
        _gltr = {'ticker': 'GLTR', 'initMarginReq': 1.0000, 'maintMarginReq': 1.0000}
        _vt = {'ticker': 'VT', 'initMarginReq': 1.0000, 'maintMarginReq': 1.0000}
        _bndx = {'ticker': 'BNDX', 'initMarginReq': 1.0000, 'maintMarginReq': 1.0000}
        _emb = {'ticker': 'EMB', 'initMarginReq': 1.0000, 'maintMarginReq': 1.0000}
        _dls = {'ticker': 'DLS', 'initMarginReq': 1.0000, 'maintMarginReq': 1.0000}
        _efv = {'ticker': 'EFV', 'initMarginReq': 1.0000, 'maintMarginReq': 1.0000}
        _gsg = {'ticker': 'GSG', 'initMarginReq': 1.0000, 'maintMarginReq': 1.0000}
        _efa = {'ticker': 'EFA', 'initMarginReq': 1.0000, 'maintMarginReq': 1.0000}
        _vea = {'ticker': 'VEA', 'initMarginReq': 1.0000, 'maintMarginReq': 1.0000}
        _veu = {'ticker': 'VEU', 'initMarginReq': 1.0000, 'maintMarginReq': 1.0000}
        _scz = {'ticker': 'SCZ', 'initMarginReq': 1.0000, 'maintMarginReq': 1.0000}
        _imtm = {'ticker': 'IMTM', 'initMarginReq': 1.0000, 'maintMarginReq': 1.0000}
        _dfusx = {'ticker': 'DFUSX', 'initMarginReq': 1.0000, 'maintMarginReq': 1.0000}
        _dfeox = {'ticker': 'DFEOX', 'initMarginReq': 1.0000, 'maintMarginReq': 1.0000}
        _dfalx = {'ticker': 'DFALX', 'initMarginReq': 1.0000, 'maintMarginReq': 1.0000}
        _dfcex = {'ticker': 'DFCEX', 'initMarginReq': 1.0000, 'maintMarginReq': 1.0000}
        _dfiex = {'ticker': 'DFIEX', 'initMarginReq': 1.0000, 'maintMarginReq': 1.0000}
        _dipsx = {'ticker': 'DIPSX', 'initMarginReq': 1.0000, 'maintMarginReq': 1.0000}
        _dfihx = {'ticker': 'DFIHX', 'initMarginReq': 1.0000, 'maintMarginReq': 1.0000}
        _gld = {'ticker': 'GLD', 'initMarginReq': 1.0000, 'maintMarginReq': 1.0000}
        _ugl = {'ticker': 'UGL', 'initMarginReq': 1.0000, 'maintMarginReq': 1.0000}
        _dbc = {'ticker': 'DBC', 'initMarginReq': 1.0000, 'maintMarginReq': 1.0000}
        _capd = {'ticker': 'CAPD', 'initMarginReq': 1.0000, 'maintMarginReq': 1.0000}

        self.margin_info = [_m, _msft, _3188, _spy, _ivv, _vti, _voo, _qqq, _vtv, _agg, _bnd, _vug, _ijr, _vig, _ijh,
                            _iwf, _iwd, _iwm, _vo, _vym, _xle, _vgt, _vb, _vnq, _xlk, _itot, _bsv, _xlv, _schd, _xlf,
                            _lqd, _rsp, _tip, _ivw, _schx, _iwr, _mub, _dia, _iwb, _usmv, _vv, _ive, _shy, _vbr, _dvy,
                            _dgro, _esgu, _sdy, _igsb, _qual, _vtip, _mbb, _schb, _tlt, _mdy, _jpst, _shv, _ief, _govt,
                            _iusb, _bil, _voe, _xlu, _vteb, _pff, _xly, _schp, _vht, _xlp, _vgsh, _dfac, _vmbs, _scha,
                            _schg, _xli, _splg, _iws, _vxf, _tqqq, _spyv, _hdv, _hyg, _iwn, _vbk, _spyg, _fvd, _stip,
                            _biv, _iwp, _gslc, _iusv, _iusg, _mgk, _iwv, _mtum, _fndx, _iei, _splv, _nobl, _vlue, _xlc,
                            _jepi, _schv, _vot, _iwo, _vfh, _vde, _schm, _vgit, _rdvy, _ijs, _arkk, _scho, _spyd, _sub,
                            _jnk, _ftcs, _oef, _smh, _soxx, _xlb, _ushy, _ijj, _schz, _schr, _spsb, _ibb, _amlp, _dfat,
                            _iyw, _ihi, _ijk, _fpe, _vong, _voog, _qyld, _moat, _cowz, _vonv, _usig, _dgrw, _vdc, _icsh,
                            _schh, _spab, _xbi, _vpu, _fnda, _esgv, _xop, _prf, _usfr, _vtwo, _mgv, _pgx, _ftec, _dfus,
                            _spib, _sptm, _istb, _cibr, _xlre, _sptl, _lmbs, _ijt, _shyg, _spmd, _bkln, _shm, _vcr,
                            _iyr, _fdn, _igv, _ftsm, _iwy, _pave, _near, _spsm, _hylb, _vclt, _dfas, _blv, _qqqm, _slyv,
                            _sphd, _cwb, _fixd, _rpv, _spmb, _tfi, _ewu, _sjnk, _oneq, _igm, _oih, _skyy, _dsi, _ita,
                            _mgc, _kre, _sphq, _ftsl, _vaw, _avuv, _qld, _spti, _vglt, _vis, _susa, _ioo, _ixj, _ixn,
                            _angl, _spts, _dln, _sso, _iye, _bond, _sqqq, _hyd, _susl, _don, _xt, _vox, _reet, _fdl,
                            _xme, _jets, _faln, _voov, _sgov, _bsco, _ussg, _spip, _nrgu, _iyh, _fhlc, _vone, _amj,
                            _emlp, _vusb, _icf, _upro, _spxl, _kbe, _vnla, _ryt, _jhmm, _arkg, _gvi, _sh, _slqd, _rpg,
                            _totl, _pbus, _gbil, _fas, _dfau, _avus, _tlh, _usrt, _slyg, _schk, _iyf, _qcln, _omfl,
                            _tdtt, _kbwb, _pffd, _xlg, _fmb, _icvt, _fxz, _bscm, _fxn, _pza, _aor, _futy, _rwr, _eagg,
                            _cdc, _vrp, _prfz, _tecl, _ptlc, _qtec, _ifra, _cmf, _des, _bab, _hys, _feny, _hymb, _frel,
                            _iev, _itm, _tdiv, _vioo, _hyls, _sly, _fez, _iyg, _hack, _uup, _komp, _ewg, _ilcg, _pho,
                            _xyld, _qdf, _fxr, _ibdo, _fncl, _aom, _ibdp, _stpz, _arkw, _ivol, _mdyg, _iyy, _mdyv, _ihf,
                            _bbmc, _tilt, _iwx, _itb, _bscp, _esml, _ibdn, _iglb, _usmc, _divo, _tipx, _nulv, _ewl,
                            _ivoo, _hndl, _rwl, _tbt, _fxh, _ldur, _ftxn, _xar, _eufn, _iyk, _iyj, _lctu, _ppa, _pgf,
                            _pej, _pkw, _mlpa, _tna, _ksa, _sdog, _pey, _tflo, _fbt, _viov, _fxo, _ryld, _fdvv, _srvr,
                            _pdp, _spyx, _lqdh, _gush, _fta, _arkq, _uitb, _xmlv, _dhs, _ibdq, _bbre, _fiw, _qlta, _ige,
                            _vthr, _fxl, _bug, _ieo, _edv, _fpx, _fdis, _sds, _xsd, _fex, _psq, _xhb, _lrgf, _bbus,
                            _regl, _iyt, _fcg, _dtd, _hydw, _psk, _fsta, _imcg, _mlpx, _qqew, _pbw, _idu, _bscq, _aggy,
                            _flql, _nusc, _smlf, _pfxf, _htrb, _fnx, _kxi, _iwc, _ibdr, _rez, _sect, _cfo, _iat, _calf,
                            _iwl, _spgp, _ftc, _sdvy, _xmmo, _susc, _uvxy, _vtwv, _aok, _ryh, _hygv, _drsk, _qus, _gto,
                            _smdv, _qqqj, _fyx, _ftxg, _rem, _vfva, _rdiv, _rwj, _phb, _oney, _ivov, _eusb, _pwv, _nulg,
                            _erx, _ilcb, _tdtf, _ilcv, _snpe, _imcb, _muni, _labu, _ezm, _jhml, _ousa, _fngu, _ntsx,
                            _iyc, _xslv, _jmbs, _pcef, _ewq, _cltl, _eqal, _qvml, _dstl, _smmv, _dial, _ibds, _ivog,
                            _qai, _ptbd, _ipay, _qqqe, _spxu, _fidu, _div, _rye, _cmbs, _xsvm, _pfm, _clou, _altl, _fxg,
                            _wcld, _bsjn, _ptnq, _sphy, _bsjm, _psc, _nusi, _vrig, _udow, _gsew, _gigb, _ighg, _uyg,
                            _lglv, _eps, _ltpz, _krma, _aces, _tbf, _fdrr, _psi, _agz, _lvhd, _sphb, _ees, _jval, _gsus,
                            _vtwg, _xtn, _pwb, _bizd, _corp, _tpyp, _splb, _fcom, _rhs, _cfa, _usxf, _onev, _tmv, _pwz,
                            _syld, _ihak, _pjan, _vtc, _cath, _ewd, _pnqi, _pffa, _rtm, _rom, _fmat, _mna, _smmu, _vxx,
                            _nyf, _jpus, _dbeu, _kng, _fval, _bbsc, _viog, _imcv, _ftls, _ewp, _spxs, _vuse, _bsjo,
                            _spd, _ryf, _bklc, _mdiv, _csm, _efiv, _plw, _swan, _gsst, _ibdt, _kie, _fxd, _mj, _ssus,
                            _aivl, _acio, _bscr, _ptmc, _pmay, _cape, _tail, _fndb, _rwm, _xntk, _iai, _bufd, _svxy,
                            _bbh, _ihe, _gssc, _eusa, _kbwd, _fdlo, _ibmk, _tmfc, _iqsu, _smmd, _zroz, _ibml, _gbf,
                            _shyd, _fctr, _xhe, _ttt, _psct, _schi, _iez, _iyz, _flgv, _ryu, _rous, _fxu, _dwas, _qdef,
                            _ddm, _iscv, _rgi, _ig, _tza, _pxe, _qid, _jqua, _xes, _sfy, _bsjp, _agzd, _smb, _size,
                            _rwk, _jhsc, _ulst, _schj, _ustb, _adme, _eza, _ibmm, _avlv, _pref, _vbnd, _sret, _mear,
                            _vote, _xrt, _spdn, _sdow, _gnma, _yyy, _dusa, _amza, _ujan, _psch, _numg, _mmin, _iscg,
                            _sjb, _clsc, _numv, _xmhq, _onln, _ftsd, _soxs, _papr, _tecb, _iak, _pjp, _inds, _ffeb,
                            _rzv, _kbwy, _vixy, _vceb, _clrg, _usdu, _pxi, _fmhi, _cdl, _ccor, _bkag, _nuag, _rcd, _tmf,
                            _dfeb, _oneo, _dfnm, _vsda, _pbj, _ulvm, _fcpi, _lgh, _pfix, _fny, _csb, _rfg, _bibl, _sixh,
                            _def, _dpst, _pio, _bulz, _hmop, _usvm, _pfeb, _qqh, _fsmb, _just, _dfe, _ldsf, _mmit,
                            _divb, _fqal, _urty, _ovl, _govz, _ftxo, _gal, _ibuy, _pjun, _ibmn, _dog, _jpme, _bscs,
                            _xmvm, _nubd, _vlu, _fvc, _ibdu, _fdd, _dig, _tur, _mlpb, _pmar, _skor, _pth, _fyt, _py,
                            _usd, _fnk, _jmom, _psep, _fapr, _tchp, _xsw, _eql, _iltb, _poct, _palc, _mstb, _taxf, _psj,
                            _fumb, _atmp, _qval, _dgrs, _fdec, _dbmf, _cgcp, _ixp, _ibd, _flv, _valq, _xlsr, _prnt,
                            _she, _djd, _dapr, _pdec, _jpse, _pbe, _fri, _flbl, _usmf, _dfen, _mln, _cza, _qgro, _hyzd,
                            _mort, _tdsb, _iscb, _xvv, _ptf, _fmar, _cure, _fyc, _yld, _dfip, _ibte, _psce, _csml,
                            _vfmo, _pnov, _bjan, _must, _spff, _smlv, _tipz, _deed, _psp, _fcvt, _fab, _oscv, _qvmm,
                            _tbx, _airr, _fad, _igbh, _xph, _nail, _idna, _vfqy, _slvo, _dfnl, _esg, _pyz, _uwm, _tphd,
                            _epol, _wfhy, _ttac, _lrge, _emnt, _umi, _ddec, _gnom, _spvu, _bmay, _tok, _ausf, _ibmo,
                            _tplc, _paug, _edoc, _pffv, _jsmd, _cacg, _pawz, _hlal, _qlv, _fjan, _hegd, _hybb, _etho,
                            _ghyb, _hygh, _sixa, _pjul, _gtip, _dali, _xmpt, _ousm, _sval, _fdm, _foct, _omfs, _rth,
                            _xsmo, _pfld, _lsat, _dmar, _deus, _igeb, _ibtd, _bndc, _aiq, _btal, _hyxf, _vfmf, _gvip,
                            _eprf, _ffty, _faz, _rfv, _spus, _eden, _fjul, _srty, _vsmv, _korp, _wtmf, _sixl, _xitk,
                            _ewre, _vrai, _lsaf, _rvnu, _kbwp, _jmub, _ibdv, _bfor, _tdvg, _ppty, _pkb, _ftxr, _hyhg,
                            _psr, _imtb, _fmf, _hdge, _bsep, _stot, _fdg, _pst, _doct, _qlc, _prn, _pbtp, _pifi, _esga,
                            _ius, _edow, _fllv, _bsct, _rigs, _ocio, _fsep, _ieus, _pbp, _mvv, _psl, _fbgx, _aieq,
                            _afif, _hydb, _aesr, _nure, _ffti, _ryj, _hybl, _ewmc, _miln, _eqwl, _bapr, _fcal, _balt,
                            _twm, _bfeb, _tecs, _cvy, _ibhc, _norw, _htec, _ismd, _njan, _sqew, _shag, _baug, _risr,
                            _rxl, _ibmp, _risn, _rfda, _qqxt, _buff, _svol, _fbcv, _fngo, _eqrr, _rzg, _qqqn, _ibnd,
                            _pzt, _hknd, _psff, _tdv, _fdmo, _netl, _bkmc, _ietc, _fisr, _chgx, _mbsd, _flmb, _ucrd,
                            _kce, _ign, _pwc, _dxd, _dsep, _utrn, _ghyg, _putw, _qaba, _webl, _inkm, _dvol, _ure, _spbc,
                            _xout, _bjul, _ibtg, _amub, _gmom, _boct, _sbio, _sspy, _nuhy, _qmom, _mfus, _drip, _dwaw,
                            _phyl, _husv, _joet, _flmi, _bib, _xhs, _bndd, _hyld, _fngd, _owns, _schq, _dfnv, _teqi,
                            _xvol, _minc, _jsml, _bdec, _bmar, _ftxl, _spmo, _cefs, _ibhb, _vixm, _shyl, _qdec, _fibr,
                            _dwus, _cya, _byld, _hsrt, _smig, _amna, _azbj, _kbwr, _htab, _fsz, _bjun, _ibmq, _ddiv,
                            _onof, _drn, _bnku, _psci, _mmtm, _ufo, _szne, _djul, _ibtf, _pui, _ibtk, _ibdw, _arb, _fku,
                            _uapr, _rfci, _xjh, _pxj, _ewo, _ibtb, _fsmd, _dynf, _ibhd, _armr, _csf, _labd, _bils,
                            _buzz, _dalt, _pffr, _bsmm, _bnov, _dew, _hips, _bscu, _resp, _mrgr, _eudg, _spdv, _acsi,
                            _spyc, _ffiu, _ibdd, _wbiy, _hibl, _jdiv, _mmlg, _ovb, _tple, _evx, _mgmt, _dura, _vegn,
                            _uym, _rinf, _noct, _usep, _azaj, _umay, _bitq, _sixs, _napr, _trnd, _ewus, _pvi, _soxq,
                            _vfmv, _spvm, _amtr, _iigd, _uoct, _bsmo, _iuss, _tphe, _csd, _bkch, _bsmp, _qdiv, _flqm,
                            _ewsc, _ovt, _tyo, _bsmn, _qylg, _recs, _bkse, _xtl, _midu, _sent, _vxz, _lqdb, _drv, _ifed,
                            _fngs, _xrlv, _btec, _qdpl, _lbay, _njul, _retl, _tpsc, _bdcz, _guru, _wfh, _qmar, _utes,
                            _jhmt, _romo, _dblv, _spuu, _pfi, _arcm, _wiz, _sfyx, _sbnd, _fthi, _pset, _qpx, _qvms,
                            _vamo, _lead, _umar, _hdg, _deep, _dweq, _udec, _ufeb, _mmca, _koct, _lkor, _ery, _pscc,
                            _nrgd, _homz, _oeur, _pteu, _vflq, _hewg, _bsjr, _java, _feig, _wbif, _pab, _bkhy, _hyrm,
                            _zig, _aqgx, _shus, _pxq, _udn, _sfig, _azbo, _igld, _mino, _pscf, _jhms, _ibhe, _enor,
                            _wbii, _wfig, _mbox, _jhmh, _lsst, _azao, _obnd, _wbig, _vega, _tagg, _pink, _tgrw, _jhme,
                            _tya, _pbnd, _pbs, _stnc, _nacp, _bsmq, _ibth, _iehs, _pbsm, _tbux, _alty, _ihyf, _tdsa,
                            _roof, _sims, _sspx, _tpor, _mtgp, _scdl, _teng, _pamc, _hold, _rffc, _lfeq, _ieih, _ciz,
                            _ubt, _xylg, _tctl, _ujul, _fevr, _mbnd, _klcd, _rrh, _jib, _fftg, _ewco, _bsce, _nusa,
                            _lgov, _pfig, _saa, _dfhy, _fhys, _scrd, _pws, _mvrl, _entr, _gfgf, _pez, _ffsg, _ibce,
                            _iwdl, _avmu, _womn, _pval, _acvf, _ffhg, _vpc, _umdd, _aspy, _sihy, _dug, _dbv, _esgs,
                            _qjun, _rafe, _revs, _iigv, _idiv, _fedl, _ewgs, _fcef, _uaug, _mlpo, _fite, _jmin, _cws,
                            _thy, _usml, _xshq, _pscd, _frty, _tgif, _kvle, _marb, _nflt, _srs, _ujun, _qspt, _germ,
                            _fovl, _xshd, _qull, _sxqg, _dfnd, _xweb, _xjr, _bkui, _cdx, _want, _glry, _rwvg, _dvlu,
                            _rosc, _nulc, _clse, _dxge, _spxe, _jusa, _qcon, _dusl, _cpi, _rdog, _sepz, _kcca, _rnsc,
                            _ovlh, _jhmf, _jhmb, _csa, _alfa, _htus, _rbnd, _utsl, _fcsh, _wbit, _pscu, _xbap, _egis,
                            _inmu, _hlge, _fgm, _ibhf, _kscd, _riet, _spax, _pype, _snug, _smcp, _hymu, _bscv, _upw,
                            _jctr, _ibbq, _rnlc, _sogu, _clix, _iwfl, _tspa, _spmv, _qqd, _pscm, _eshy, _xrmi, _bsmr,
                            _ftxh, _bsms, _qdyn, _jhmu, _erm, _rek, _ylde, _qls, _psmm, _esus, _efnl, _ecln, _bsjs,
                            _azbl, _totr, _ewk, _mnm, _ujb, _rokt, _reit, _spxb, _rndv, _oppx, _sdei, _lrnz, _hylv,
                            _ssly, _demz, _jhma, _sqlv, _clds, _hewu, _gsig, _iwml, _qqqa, _bsmt, _rnmc, _eaok, _ftds,
                            _dboc, _jhcb, _sef, _tyd, _psmj, _ibti, _rtai, _gk, _mtul, _fehy, _usbf, _adfi, _uxi, _ust,
                            _bout, _iedi, _xpnd, _ibtj, _iecs, _elqd, _psmo, _dbeh, _psmr, _sfyf, _hyup, _feus, _minn,
                            _maga, _lyfe, _hsmv, _skf, _jhpi, _jhpi, _spak, _bbc, _amom, _augz, _xbjl, _vabs, _flqs,
                            _jhcs, _qmn, _plrg, _pill, _xtjl, _flrg, _qtjl, _rew, _gldb, _ovm, _jhmc, _pex, _psmc,
                            _imlp, _ftqi, _avsc, _ucc, _pscw, _zecp, _smi, _jhmi, _bbp, _julz, _bsmu, _lopp, _mig,
                            _bsmv, _psfm, _bnkd, _myy, _tmdv, _xjun, _azal, _qarp, _dbja, _mide, _fsig, _ibhg, _ieme,
                            _bis, _spuc, _tsja, _qrmi, _qrft, _fmny, _roro, _bsjt, _qtap, _dbgr, _spxn, _ffnd, _smle,
                            _gbdv, _scc, _aaa, _boss, _psfj, _pgro, _spxt, _midf, _hytr, _heet, _bul, _smdy, _iefn,
                            _dwpp, _eqop, _cldl, _tpay, _uslb, _dwmc, _xdsq, _tsoc, _berz, _bkus, _mbbb, _qed, _usi,
                            _xdqq, _uge, _ovs, _dsoc, _xtap, _fltn, _bad, _vnmc, _lvol, _iqm, _indf, _decz, _ecoz,
                            _ibtl, _rspy, _qqc, _syus, _bedz, _jojo, _cbse, _stlv, _rwgv, _smdd, _hval, _pfut, _sbb,
                            _spxz, _xdap, _octz, _escr, _hyin, _esgy, _eaom, _aprz, _mid, _pldr, _ivlc, _psfo, _pltl,
                            _nvq, _sdga, _fsst, _nscs, _marz, _virs, _jre, _pscq, _hdiv, _ssg, _tfjl, _tbjl, _cbls,
                            _aflg, _itan, _pscj, _xdjl, _nwlg, _usvt, _mayz, _janz, _dsja, _sdd, _amer, _rec, _wwow,
                            _pexl, _trdf, _qclr, _spxv, _wil, _xclr, _vsl, _dwat, _junz, _cfcv, _lopx, _fldz, _nife,
                            _jfwd, _febz, _rxd, _fedx, _gblo, _wgro, _ooto, _xtr, _mjus, _maax, _fivr, _ggrw, _mzz,
                            _useq, _rodi, _afsm, _weix, _afmc, _szk, _liv, _smn, _sij, _sdp, _qtr, _ltl, _skyu, _trpl,
                            _stlg, _eeh, _hhh, _aggh, _dspc, _gbgr, _epre, _ailv, _ailg, _xhyc, _xhyh, _xhyt, _xhyd,
                            _dwx, _eem, _vgk, _vpl, _gltr, _vt, _bndx, _emb, _dls, _efv, _gsg, _efa, _vea, _veu, _scz,
                            _imtm, _dfusx, _dfeox, _dfalx, _dfcex, _dfiex, _dipsx, _dfihx, _gld, _ugl, _dbc, _capd]
