import numpy as np
import pandas as pd
import json
import pymysql

import nonlinear_capm_beta.config as config


class DataLoader:
    """DataLoader
    """

    def __init__(self, connect=True):

        self.connection = None

        if connect:
            self.connect()

    def connect(self):

        host = config.MYSQL_HOST
        port = config.MYSQL_PORT
        user = config.MYSQL_USER
        password = config.MYSQL_PASSWORD
        database = config.MYSQL_DATABASE

        print("")
        print("SQL Connection Info")
        print("- Host: {}".format(host))
        print("- Port: {}".format(port))
        print("- User: {}".format(user))
        print("- Database: {}".format(database))

        self.connection = pymysql.connect(host=host, port=port, user=user, password=password,
                                   db=database, charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)

    def close(self):
        self.connection.close()

    def load_market_returns(self, freq='daily', no_lags=20, date_from=None, date_to=None, log_returns=False):
        """load_market_returns
        """

        query = """
            select date, mktrf, rf
            from FamaFrench.3factors_{}
        """.format(freq)

        if (date_from is not None) & (date_to is not None):
            query = query + 'where date >= "{}" and date <= "{}"'.format(date_from, date_to)

        with self.connection.cursor() as cur:
            cur.execute(query)

            df = pd.DataFrame(cur.fetchall())

        if log_returns:
            df['rm'] = df['mktrf'] + df['rf']
            df['rf'] = np.log(1 + df['rf']/100) * 100
            df['mktrf'] = np.log(1 + df['rm']/100) * 100 - df['rf']
            del df['rm']

        for i in range(no_lags):
            df['L{}.mktrf'.format(i+1)] = df['mktrf'].shift(i+1)

        idx = np.isnan(df['L{}.mktrf'.format(no_lags)])

        return df.loc[~idx]

    def load_portfolio_returns(self, name, freq, log_returns=False):
        """load_market_returns
        """

        parts = name.split('_')

        if parts[0] == 'size':
            table = 'FamaFrench.portfolio_size'
        elif parts[0] == 'value':
            table = 'FamaFrench.portfolio_value'
        else:
            table = 'FamaFrench.3factors'

        if freq == 'daily':
            table = table + '_daily'
        elif (freq == 'monthly') & (len(parts) == 1):
            table = table + '_monthly'

        if len(parts) > 1:
            if parts[1] == 'lo':
                column = 'd1'
            elif parts[1] == 'hi':
                column = 'd10'
        else:
            column = parts[0]

        query = 'select date, {} from {}'.format(column, table)

        with self.connection.cursor() as cur:
            cur.execute(query)

            df = pd.DataFrame(cur.fetchall())
            df = df.rename(columns={column:'pfret'})

        if log_returns:
            df['pfret'] = np.log(1 + df['pfret']/100) * 100

        idx = np.isnan(df['pfret'])

        return df.loc[~idx]

    def load_portfolio_params(self, name, freq, lags=20, depth=2, width=1):
        """load_portfolio_params
        """

        query = """
            select parameters
            from beta_parameters_portfolios
            where freq = '{}' and name = '{}' and lags = {} and depth = {} and width = {}
        """.format(freq, name, lags, depth, width)

        with self.connection.cursor() as cur:
            cur.execute(query)
            result = cur.fetchall()

        assert len(result) <= 1

        if len(result) == 1:
            return json.loads(result[0]['parameters'])
        else:
            return None

    def save_portfolio_params(self, params, name, freq, lags=20, depth=2, width=1):
        """save_portfolio_params
        """

        check_if_exist = self.load_portfolio_params(name, freq, lags, depth, width)

        if check_if_exist is None:
            query = """
              insert into beta_parameters_portfolios
              (freq, name, lags, depth, width, parameters)
              values ('{}', '{}', {}, {}, {}, '{}')
            """.format(freq, name, lags, depth, width, json.dumps(params))

        else:
            query = """
              update beta_parameters_portfolios
              set parameters = '{}'
              where freq = '{}' and name = '{}' and lags = {} and depth = {} and width = {}
            """.format(json.dumps(params), freq, name, lags, depth, width)

        with self.connection.cursor() as cur:
            cur.execute(query)
            self.connection.commit()

    def load_target_permno_list(self, year, max_rank):
        """load_permno_list
        """

        query = """
            select year, rank, permno
            from beta_parameters_stocks
            where year = {} and rank <= {} and no_obs is null
            order by rank
        """.format(year, max_rank)

        with self.connection.cursor() as cur:
            cur.execute(query)
            results = cur.fetchall()

        if len(results) > 0:
            return pd.DataFrame(results)
        else:
            return None

    def check_if_still_empty(self, year, permno):
        """check_if_still_empty
        """

        query = """
            select parameters
            from beta_parameters_stocks
            where year = {} and permno = {}
        """.format(year, permno)

        with self.connection.cursor() as cur:
            cur.execute(query)
            results = cur.fetchall()

        return results[0]['parameters'] is None

    def load_stock_returns(self, permno, date_from, date_to):
        """load_stock_returns
        """

        query = """
            select date, ret
            from CRSP.stocks_daily
            where permno = {} and date >= '{}' and date <= '{}'
        """.format(permno, date_from, date_to)

        with self.connection.cursor() as cur:
            cur.execute(query)
            results = cur.fetchall()

        if len(results) > 0:
            return pd.DataFrame(results)
        else:
            return None

    def save_stock_params(self, year, permno, no_obs, date_from, date_to, params):
        """save_stock_params
        """

        query = """
          update beta_parameters_stocks
          set no_obs = {},
            sample_from = '{}',
            sample_to = '{}',
            parameters = '{}'
          where year = {} and permno = {}
        """.format(no_obs, date_from, date_to, json.dumps(params), year, permno)

        with self.connection.cursor() as cur:
            cur.execute(query)
            self.connection.commit()

    def save_stock_params_only_no_obs(self, year, permno, no_obs):
        """save_stock_params_only_no_obs
        """

        query = """
          update beta_parameters_stocks
          set no_obs = {}
          where year = {} and permno = {}
        """.format(no_obs, year, permno)

        with self.connection.cursor() as cur:
            cur.execute(query)
            self.connection.commit()
