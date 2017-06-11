import pandas as pd

from nonlinear_capm_beta.estimation.DataLoader import DataLoader

loader = DataLoader(connect=True)

######################################################
# Load and write beta_parameters_stocks table
######################################################

query = "select year, rank, permno, no_obs, beta_average, beta_delay, beta_convexity \
  from beta_parameters_stocks where beta_average is not null"

beta_stats = loader.sql_query_select(query)

beta_stats.to_stata('beta_stats_roll.dta', write_index=False)


######################################################
# Load and write beta_stocks_full_periods table
######################################################

query = "select permno, no_obs, beta_average, beta_delay, beta_convexity \
  from beta_stocks_full_periods where beta_average is not null"

beta_stats = loader.sql_query_select(query)

beta_stats.to_stata('beta_stats_full.dta', write_index=False)


loader.close()

