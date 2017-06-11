* beta_full_periods

clear
set more off
graph drop _all
disp _newline(100)

local options = "stats(coef tstat) bdec(3) tdec(3)"

cd "/Users/dioscuroi/GitHub/nonlinear_capm_beta/stata"

!rm beta_full_periods*.txt


****************************************************
* Prepare data
****************************************************

use beta_stats_full, clear

* merge with beta stats
merge 1:1 permno using average_returns_of_every_stock, keep(matched) nogen

* need to choose optimal filtering conditions here
drop if no_obs < 500

* drop outliers
foreach beta of varlist beta_average beta_delay beta_convexity {
	
	_pctile `beta', p(1 99)
	
	replace `beta' = . if `beta' < r(r1)
	replace `beta' = . if `beta' > r(r2)
}

drop if beta_average == .
drop if beta_delay == .
drop if beta_convexity == .

*replace beta_average = beta_average - beta_delay

* print the summary of beta
summarize beta_*, detail

corr beta_*

reg avg_ret beta_*
reg avg_capm_alpha beta_*
reg avg_ff3_alpha beta_*

reg avg_capm_alpha beta_average
reg avg_capm_alpha beta_delay
reg avg_capm_alpha beta_average beta_delay
reg avg_capm_alpha beta_average beta_delay beta_convexity

