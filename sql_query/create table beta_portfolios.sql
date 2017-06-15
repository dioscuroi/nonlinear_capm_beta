drop table if exists beta_portfolios;

create table beta_portfolios (
  `group` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `lags` int(11) NOT NULL,
  `id` int NOT NULL,
  `touched` datetime,
  `parameters` text,
  `beta_average` float,
  `beta_delay` float,
  `beta_convexity` float,
  PRIMARY KEY (`group`, `name`, `lags`, `id`)
);


