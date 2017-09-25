create view beta_stocks_monthly_progress as
select a.year, a.count, b.success,
	cast(a.count / 500 as decimal(3,2)) as progress_rate,
	cast(b.success / a.count as decimal(3,2)) as success_rate
from (
	select year, count(permno) as count
	from `beta_stocks_monthly`
	where no_obs is not null
	group by year
) a
join (
	select year, count(permno) as success
	from `beta_stocks_monthly`
	where parameters is not null
	group by year
) b on a.year = b.year
;
