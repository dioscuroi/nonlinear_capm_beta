* fama_macbeth.do

clear
set more off
disp _newline(100)

local options = "stats(coef tstat) bdec(3) tdec(3)"

cd "/Users/dioscuroi/GitHub/nonlinear_capm_beta/stata"

!rm fama_macbeth*.txt


/*
****************************************************
* Compute annual returns
****************************************************

use "/Users/dioscuroi/OneDrive - UNSW/Research Data/Stocks/CRSP stock returns/stocks_monthly_filtered.dta", clear

keep date permno ret prc shrout
drop if ret == .

gen year = year(dofm(date))
gen month = month(dofm(date))
gen logret = log(1 + ret)
gen log_marcap = log(prc * shrout)

bysort permno year: egen sum_logret = sum(logret)

keep if month == 12
keep permno year sum_logret log_marcap

gen ret = exp(sum_logret) - 1

drop sum_logret

save fama_macbeth_temp.dta, replace


****************************************************
* Compute riskfree rates and excess returns
****************************************************

use "/Users/dioscuroi/OneDrive - UNSW/Research Data/Bonds/Bond Yields from FRB/Treasury Constant Maturity/Treasury Constant Maturity monthly.dta", clear

gen year  = year(dofm(date))
gen month = month(dofm(date))

keep if month == 12
keep year GS1

replace year = year + 1
rename GS1 rf

merge 1:m year using "fama_macbeth_temp.dta", keep(match) nogen

gen exret = ret - rf/100

order permno year ret rf exret

save fama_macbeth_temp.dta, replace
*/


****************************************************
* Merge with beta estimates
****************************************************

use fama_macbeth_temp.dta, clear

merge 1:1 permno year using "beta_stats_roll_lag20", keep(match) nogen
merge 1:1 permno year using "/Users/dioscuroi/OneDrive - UNSW/Research Data/Stocks/matched with Compustat/firm_characteristics.dta", keep(match) nogen

* need to choose optimal filtering conditions here
drop if no_obs < 100

* drop outliers
foreach beta of varlist beta_average beta_delay beta_convexity {

	bysort year: egen cut1 = pctile(`beta'), p(1)
	bysort year: egen cut2 = pctile(`beta'), p(99)
	
	replace `beta' = . if `beta' < cut1
	replace `beta' = . if `beta' > cut2
	
	drop cut1 cut2
}

drop if beta_average == .
drop if beta_delay == .
drop if beta_convexity == .

tsset permno year

reg F.exret beta_average beta_delay beta_convexity
reg F.exret beta_average beta_delay beta_convexity log_marcap
reg F.exret beta_average beta_delay beta_convexity log_marcap BM_equity


