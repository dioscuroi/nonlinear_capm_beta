drop table if exists beta_portfolios;

create table beta_portfolios (
  `filename` varchar(255) NOT NULL,
  `portfolio` varchar(255) NOT NULL,
  `lags` int(11) NOT NULL,
  `no_obs` int not null,
  `id` int NOT NULL,
  `touched` datetime,
  `parameters` text,
  `beta_average` float,
  `beta_delay` float,
  `beta_convexity` float,
  PRIMARY KEY (`filename`, `portfolio`, `lags`, `id`)
);


