drop table if exists beta_stocks_full_periods;

create table beta_stocks_full_periods as
select permno, count(ret) as obs, min(date) as sample_from, max(date) as sample_to
from CRSP_stocks_daily
group by permno
;

alter table beta_stocks_full_periods
add primary key (permno),
add touched datetime,
add parameters text,
add beta_average float,
add beta_delay float,
add beta_convexity float
;


select count(permno), min(permno), max(permno)
from beta_stocks_full_periods
;

