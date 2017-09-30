* univariate_risk_premium

clear
set more off
disp _newline(100)

local options = "stats(coef tstat) bdec(3) tdec(3)"

cd "/Users/dioscuroi/GitHub/nonlinear_capm_beta/stata"

!rm univariate_risk_premium*.txt


****************************************************
* Prepare data
****************************************************

* load beta statistics
use beta_stats_roll_lag20, clear

* need to choose optimal filtering conditions here
keep if rank <= 1000

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

* print the summary of beta
summarize beta_*, detail

corr beta_*


****************************************************
* Portfolio formation
****************************************************

* form portfolios
foreach beta of varlist beta_average beta_delay beta_convexity {

	bysort year: egen p33 = pctile(`beta'), p(33)
	bysort year: egen p67 = pctile(`beta'), p(67)
	
	gen pid_`beta' = .
	replace pid_`beta' = 1 if (`beta' < p33)
	replace pid_`beta' = 2 if (`beta' >= p33) & (`beta' <= p67)
	replace pid_`beta' = 3 if (`beta' > p67)
	
	drop p33 p67
}


****************************************************
* Compute portfolio returns
****************************************************

* merge with stock returns
gen date = ym(year, 12)
format %tm date

merge 1:1 permno date using "/Users/dioscuroi/OneDrive - UNSW/Research Data/Stocks/CRSP stock returns/stocks_monthly_filtered.dta", nogen

gen marcap = prc * shrout

keep  date permno ret marcap pid_*
order date permno ret marcap pid_*

tsset permno date

gen Fret = F.ret
gen month = month(dofm(date))

forvalues i = 1/11 {
	foreach pid of varlist pid_* {
		replace `pid' = L`i'.`pid' if month == `i'
	}
}

drop if pid_beta_average == .
drop month

save temp_portfolio_formation, replace


* compute portfolio returns
foreach beta in beta_average beta_delay beta_convexity {

	use temp_portfolio_formation, clear

	* equal-weighted portfolio return
	bysort date pid_`beta': egen `beta'_ewFret = mean(Fret)

	* value-weighted portfolio return
	bysort date pid_`beta': egen total_marcap = sum(marcap)

	gen weight = marcap / total_marcap
	gen weight_Fret = weight * Fret

	bysort date pid_`beta': egen `beta'_vwFret = sum(weight_Fret)
	
	keep date pid_`beta' `beta'_ewFret `beta'_vwFret 
	duplicates drop
	
	* move date by one month and get rid of "F" label
	replace date = date + 1
	rename `beta'_ewFret ewr_`beta'
	rename `beta'_vwFret vwr_`beta'
	
	reshape wide ewr_`beta' vwr_`beta', i(date) j(pid_`beta')
	
	save temp_portfolio_returns_`beta', replace
}

use temp_portfolio_returns_beta_average, clear
merge 1:1 date using temp_portfolio_returns_beta_delay, nogen
merge 1:1 date using temp_portfolio_returns_beta_convexity, nogen

save temp_portfolio_returns_combined, replace


****************************************************
* print regression results
****************************************************

use temp_portfolio_returns_combined, clear

merge 1:1 date using "/Users/dioscuroi/OneDrive - UNSW/Research Data/Stocks/Fama_French/ff3factors_monthly.dta", nogen

tsset date

foreach beta in beta_average beta_delay beta_convexity {

*	foreach weight in ew vw {
	foreach weight in vw {
	
		gen exret1 = `weight'r_`beta'1 * 100 - rf
		gen exret2 = `weight'r_`beta'2 * 100 - rf
		gen exret3 = `weight'r_`beta'3 * 100 - rf

		forvalues i = 1/3 {
			reg exret`i'
			outreg2 using "univariate_risk_premium_`beta'_`weight'_raw.txt", `options' drop(exret`i')
			
			reg exret`i' mktrf L.mktrf
			outreg2 using "univariate_risk_premium_`beta'_`weight'_CAPM.txt", `options' drop(exret`i')
		}
	
		drop exret1 exret2 exret3
	}
}




