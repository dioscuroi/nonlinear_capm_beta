import pandas as pd

from nonlinear_capm_beta.estimation.DataLoader import DataLoader

loader = DataLoader(connect=True)

######################################################
# beta_stocks_rolling
######################################################

# query = "select year, rank, permno, no_obs, beta_average, beta_delay, beta_convexity \
#   from beta_stocks_rolling where beta_average is not null"
#
# beta_stats = loader.sql_query_select(query)
#
# beta_stats.to_stata('beta_stats_roll_lag20.dta', write_index=False)


######################################################
# beta_portfolios
######################################################

query = "select filename, portfolio, no_obs, beta_average, beta_delay, beta_convexity from beta_portfolios"

beta_stats = loader.sql_query_select(query)

beta_stats.to_stata('beta_portfolios.dta', write_index=False)


######################################################
# beta_stocks_full_periods
######################################################

# query = "select permno, no_obs, beta_average, beta_delay, beta_convexity \
#   from beta_stocks_full_periods where beta_average is not null"
#
# beta_stats = loader.sql_query_select(query)
#
# beta_stats.to_stata('beta_stats_full.dta', write_index=False)


loader.close()

