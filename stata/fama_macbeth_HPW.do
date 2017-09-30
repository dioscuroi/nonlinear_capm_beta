* fama_macbeth_HPW.do

clear
set more off
disp _newline(100)
 
local options = "stats(coef tstat) bdec(3) tdec(3)"

cd "/Users/dioscuroi/GitHub/nonlinear_capm_beta/stata"

!rm fama_macbeth_HPW.do*.txt


****************************************************
* Fama-MacBeth as in Hu, Pan, and Wang (2013)
****************************************************

use "/Users/dioscuroi/OneDrive - UNSW/Research Data/Stocks/CRSP stock returns/stocks_monthly_filtered.dta", clear

tsset permno date

gen marcap = prc * shrout
gen Lmarcap = L.marcap

keep date permno ret Lmarcap
keep if ret != .

merge m:1 date using "/Users/dioscuroi/OneDrive - UNSW/Research Data/Stocks/Fama_French/ff3factors_monthly.dta", keep(match) nogen

gen exret = ret * 100 - rf
keep date permno exret Lmarcap

merge m:1 permno using beta_stats_full, keep(match) nogen

drop if no_obs < 1000

tsset permno date

save fama_macbeth_HPW_temp, replace


****************************************************
* Create a template file to save the output
****************************************************

clear

gen date = .
gen coef_avg = .
gen coef_delay = .
gen coef_convx = .

save fama_macbeth_HPW, replace


****************************************************
* Regress returns on characteristics every month
****************************************************

use fama_macbeth_HPW_temp, clear

summarize date

local date_min = r(min) + 1
local date_max = r(max)

forvalues i = `date_min'/`date_max' {

	disp "***************************************************"
	disp " date: `i' (min: `date_min', max: `date_max')"
	disp "***************************************************"
	
	use fama_macbeth_HPW_temp if date == `i', clear
	
	reg exret beta_average beta_delay beta_convexity
	
	matrix coef = e(b)
	
	use fama_macbeth_HPW, clear
	
	set obs `= _N + 1'
	
	replace date = `i' in `=_N'
	replace coef_avg   = coef[1,1] in `=_N'
	replace coef_delay = coef[1,2] in `=_N'
	replace coef_convx = coef[1,3] in `=_N'
	
	save fama_macbeth_HPW, replace
}



****************************************************
* t-test on the estimated coefficients
****************************************************

use fama_macbeth_HPW, clear

reg coef_avg
reg coef_delay
reg coef_convx



