import pandas as pd

from nonlinear_capm_beta.estimation.DataLoader import DataLoader

loader = DataLoader(connect=True)

# query = "select year, rank, permno, beta_average, beta_delay, beta_convexity \
#   from beta_parameters_stocks where rank <= 500 and beta_average is not null"

query = "select year, rank, permno, beta_average, beta_delay, beta_convexity \
  from beta_parameters_stocks where beta_average is not null"

beta_stats = loader.sql_query_select(query)

loader.close()

beta_stats.to_csv('beta_stats.csv', index=False)

