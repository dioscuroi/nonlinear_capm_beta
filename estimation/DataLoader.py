import numpy as np
import pandas as pd
import json
import pymysql

from collections import OrderedDict
from pymysql.cursors import DictCursorMixin, Cursor

import nonlinear_capm_beta.config as config


class OrderedDictCursor(DictCursorMixin, Cursor):
    dict_type = OrderedDict


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

    def sql_query_select(self, query):
        """sql_query_select
        """

        with self.connection.cursor(OrderedDictCursor) as cur:
            cur.execute(query)
            results = cur.fetchall()

        if results is None:
            return None

        if len(results) == 0:
            return None

        return pd.DataFrame(results)

    def sql_query_commit(self, query):
        """sql_query_commit
        """

        with self.connection.cursor() as cur:
            cur.execute(query)
            self.connection.commit()

    def load_market_returns(self, freq='daily', no_lags=20, date_from=None, date_to=None, log_returns=False):
        """load_market_returns
        """

        query = 'select date, mktrf, rf from FamaFrench_3factors'

        if freq == 'daily':
            query += '_daily'

        if (date_from is not None) & (date_to is not None):
            query += ' where date >= "{}" and date <= "{}"'.format(date_from, date_to)

        df = self.sql_query_select(query)

        if log_returns:
            df['rm'] = df['mktrf'] + df['rf']
            df['rf'] = np.log(1 + df['rf']/100) * 100
            df['mktrf'] = np.log(1 + df['rm']/100) * 100 - df['rf']
            del df['rm']

        for i in range(no_lags):
            df['L{}.mktrf'.format(i+1)] = df['mktrf'].shift(i+1)

        idx = np.isnan(df['L{}.mktrf'.format(no_lags)])

        return df.loc[~idx]

    def load_portfolio_returns(self, freq, name, log_returns=False):
        """load_market_returns
        """

        switcher = {
            'small': 'select date, d1 from FamaFrench_portfolio_size',
            'large': 'select date, d10 from FamaFrench_portfolio_size',
            'growth': 'select date, d1 from FamaFrench_portfolio_value',
            'value': 'select date, d10 from FamaFrench_portfolio_value',
            'smb': 'select date, smb from FamaFrench_3factors',
            'hml': 'select date, hml from FamaFrench_3factors',
            'small-growth': 'select date, p11 from FamaFrench_portfolio_size_value',
            'small-value': 'select date, p15 from FamaFrench_portfolio_size_value',
            'large-growth': 'select date, p51 from FamaFrench_portfolio_size_value',
            'large-value': 'select date, p55 from FamaFrench_portfolio_size_value'
        }

        query = switcher[name]

        if freq == 'daily':
            query += '_daily'

        with self.connection.cursor() as cur:
            cur.execute(query)

            df = pd.DataFrame(cur.fetchall())
            df = df.rename(columns={cur._fields[1]:'pfret'})

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

        if len(result) < 1:
            return None

        params = result[0]['parameters']

        if params is not None:
            return json.loads(params)
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

    def load_permno_list_with_parameters(self, year, max_rank):
        """load_permno_list_with_parameters
        """

        query = """
            select permno
            from beta_parameters_stocks
            where year = {} and rank <= {} and parameters is not null
            order by rank
        """.format(year, max_rank)

        with self.connection.cursor() as cur:
            cur.execute(query)
            results = cur.fetchall()

        if len(results) > 0:
            return pd.DataFrame(results)
        else:
            return None

    def load_permno_list_with_parameters_but_no_beta(self, year):
        """load_permno_list_with_parameters_but_no_beta
        """

        query = """
            select permno
            from beta_parameters_stocks
            where year = {} and parameters is not null and beta_average is null
            order by rank
        """.format(year)

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

    def load_stock_returns(self, permno, date_from=None, date_to=None):
        """load_stock_returns
        """

        query = """
            select date, ret
            from CRSP_stocks_daily
            where permno = {} and ret is not null
        """.format(permno).strip()

        if date_from is not None:
            query = query + " and date >= {}".format(date_from)

        if date_to is not None:
            query = query + " and date <= {}".format(date_to)

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

    def load_stock_params(self, year, permno):
        """load_stock_params
        """

        query = """
          select parameters
          from beta_parameters_stocks
          where year = {} and permno = {}
        """.format(year, permno)

        with self.connection.cursor() as cur:
            cur.execute(query)
            result = cur.fetchall()

            if len(result) < 1:
                return None

            params = result[0]['parameters']

            if params is not None:
                return json.loads(params)
            else:
                return None

    def move_portfolio_params_to_the_repeated(self, freq, name, id):
        """move_portfolio_params_to_the_repeated
        """

        with self.connection.cursor() as cur:

            query = """
              select parameters
              from beta_parameters_portfolios
              where freq = '{}' and name = '{}'""".format(freq, name)

            cur.execute(query)
            result = cur.fetchall()

            assert len(result) == 1

            params = result[0]['parameters']

            query = """
              delete from beta_parameters_portfolios
              where freq = '{}' and name = '{}'""".format(freq, name)

            cur.execute(query)

            query = """
              insert into beta_parameters_portfolios_repeated
              (freq, name, id, parameters)
              value
              ('{}', '{}', {}, '{}')""".format(freq, name, id, params)

            cur.execute(query)

            self.connection.commit()

    def save_beta_stats(self, year, permno, beta_average, beta_delay, beta_convexity):
        """save_beta_stats
        """

        query = """
            update beta_parameters_stocks
            set beta_average = {}, beta_delay = {}, beta_convexity = {}
            where year = {} and permno = {}
        """.format(beta_average, beta_delay, beta_convexity, year, permno)

        self.sql_query_commit(query)

