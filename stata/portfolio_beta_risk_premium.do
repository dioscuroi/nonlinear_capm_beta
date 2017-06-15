* portfolio_beta_risk_premium

clear
set more off
graph drop _all
disp _newline(100)

local options = "stats(coef tstat) bdec(3) tdec(3)"

cd "/Users/dioscuroi/GitHub/nonlinear_capm_beta/stata"

!rm portfolio_beta_risk_premium*.txt



****************************************************
* Compute portfolio average excess returns
****************************************************

* portfolio_49industry
use "/Users/dioscuroi/OneDrive - UNSW/Research Data/Stocks/Fama_French/portfolio_49industry.dta", clear

merge 1:1 date using "/Users/dioscuroi/OneDrive - UNSW/Research Data/Stocks/Fama_French/ff3factors_monthly.dta", nogen keep(match)

foreach col of var agric-other {
	replace `col' = . if `col' < -99
	gen exret_`col' = `col' - rf
	egen avg_exr_`col' = mean(exret_`col')
}

keep avg_exr_*
duplicates drop

gen filename = "portfolio_49industry_daily"

reshape long avg_exr_, i(filename) j(portfolio) string

save portfolio_beta_risk_premium, replace


* ff25portfolios
use "/Users/dioscuroi/OneDrive - UNSW/Research Data/Stocks/Fama_French/ff25portfolios", clear

merge 1:1 date using "/Users/dioscuroi/OneDrive - UNSW/Research Data/Stocks/Fama_French/ff3factors_monthly.dta", nogen keep(match)

foreach col of var p11-p55 {
	replace `col' = . if `col' < -99
	gen exret_`col' = `col' - rf
	egen avg_exr_`col' = mean(exret_`col')
}

keep avg_exr_*
duplicates drop

gen filename = "ff25portfolios_daily"

reshape long avg_exr_, i(filename) j(portfolio) string

append using portfolio_beta_risk_premium

rename avg_exr_ avg_exr

save portfolio_beta_risk_premium, replace



****************************************************
* Merge with portfolio betas
****************************************************

use portfolio_beta_risk_premium, clear

merge 1:1 filename portfolio using beta_portfolios, nogen

drop if beta_average > 6

summarize beta*, detail

corr beta*

reg avg_exr beta_average
reg avg_exr beta_delay
reg avg_exr beta_convexity
reg avg_exr beta_average beta_delay beta_convexity

reg avg_exr beta_average if filename == "portfolio_49industry_daily"
reg avg_exr beta_delay if filename == "portfolio_49industry_daily"
reg avg_exr beta_convexity if filename == "portfolio_49industry_daily"
reg avg_exr beta_average beta_delay beta_convexity if filename == "portfolio_49industry_daily"

reg avg_exr beta_average if filename == "ff25portfolios_daily"
reg avg_exr beta_delay if filename == "ff25portfolios_daily"
reg avg_exr beta_convexity if filename == "ff25portfolios_daily"
reg avg_exr beta_average beta_delay beta_convexity if filename == "ff25portfolios_daily"


