create view year_end_marcap as
select permno, year(date) as year, prc*shrout as marcap
from CRSP_stocks_monthly
where month(date) = 12;


create table year_end_marcap_ranked as
select t.year, t.permno, t.marcap, t.rank
from
	(select @rank := 0) init,
	(
	select year, permno, marcap,
		@rank := if(@current_year = year, @rank+1, 1) as rank,
		@current_year := year
	from year_end_marcap
	order by year, marcap desc
) t;


drop table if exists beta_stocks_rolling;

create table beta_stocks_rolling as
select year, rank, permno
from year_end_marcap_ranked
where year >= 1930
order by year, rank;

alter table beta_stocks_rolling
add primary key(year, rank);

alter table beta_stocks_rolling
add column no_obs int,
add column sample_from date,
add column sample_to date,
add column parameters text,
add column beta_average float,
add column beta_delay float,
add column beta_convexity float;

drop view if exists year_end_marcap;
drop table if exists year_end_marcap_ranked;



