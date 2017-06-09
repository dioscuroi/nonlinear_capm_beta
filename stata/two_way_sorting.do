* two_way_sorting

clear
set more off
disp _newline(100)

local options = "stats(coef tstat) bdec(3) tdec(3)"

cd "/Users/dioscuroi/GitHub/nonlinear_capm_beta/stata"

!rm two_way_sorting*.txt


****************************************************
* Prepare data
****************************************************

* load beta statistics
insheet using "beta_stats_lag5.csv", clear

* drop outliers
foreach beta of varlist beta_average beta_delay beta_convexity {
	
	_pctile `beta', p(1 99)
	
	replace `beta' = . if `beta' < r(r1)
	replace `beta' = . if `beta' > r(r2)
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

* form portfolios by beta_average first
bysort year: egen p33 = pctile(beta_average), p(33)
bysort year: egen p67 = pctile(beta_average), p(67)

gen pid_beta_average = .
replace pid_beta_average = 1 if (beta_average < p33)
replace pid_beta_average = 2 if (beta_average >= p33) & (beta_average < p67)
replace pid_beta_average = 3 if (beta_average >= p67)
	
drop p33 p67

* form sub-portfolios by beta_convexity/beta_delay next
foreach beta of varlist beta_convexity beta_delay {

	bysort year pid_beta_average: egen p33 = pctile(`beta'), p(33)
	bysort year pid_beta_average: egen p67 = pctile(`beta'), p(67)
	
	gen pid_`beta' = .
	replace pid_`beta' = pid_beta_average*10 + 1 if (`beta' < p33)
	replace pid_`beta' = pid_beta_average*10 + 2 if (`beta' >= p33) & (`beta' < p67)
	replace pid_`beta' = pid_beta_average*10 + 3 if (`beta' >= p67)
	
	drop p33 p67
}

* print summary statistics for each portfolio
table pid_beta_convexity, c(mean beta_average mean beta_convexity)
table pid_beta_delay, c(mean beta_average mean beta_delay)



****************************************************
* Compute portfolio returns
****************************************************

* merge with stock returns
gen date = ym(year, 12)
format %tm date

merge 1:1 permno date using "/Users/dioscuroi/Research Data/Stocks/CRSP stock returns/stocks_monthly_filtered.dta", nogen

gen marcap = prc * shrout

keep  date permno ret marcap pid_*
order date permno ret marcap pid_*

tsset permno date

gen Fret = F.ret
gen month = month(dofm(date))

forvalues i = 1/11 {
	foreach pid of varlist pid_* {
		quietly replace `pid' = L`i'.`pid' if month == `i'
	}
}

drop if pid_beta_average == .
drop month

save temp_portfolio_formation, replace


* compute portfolio returns
foreach beta in beta_delay beta_convexity {

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

use temp_portfolio_returns_beta_delay, clear
merge 1:1 date using temp_portfolio_returns_beta_convexity, nogen

save temp_portfolio_returns_combined, replace


* print regression results
use temp_portfolio_returns_combined, clear

merge 1:1 date using "/Users/dioscuroi/Research Data/Stocks/Fama_French/ff3factors_monthly.dta", nogen

foreach beta in beta_convexity beta_delay {

	foreach weight in ew vw {
	
		disp ""
		disp ""
		disp "****************************************************************"
		disp " `beta', `weight' "
		disp "****************************************************************"
	
		matrix raw_exret 		= (0,0,0 \ 0,0,0 \ 0,0,0)
		matrix raw_exret_tstat  = raw_exret
		matrix capm_alpha_coef  = raw_exret
		matrix capm_alpha_tstat = raw_exret
		matrix ff3_alpha_coef   = raw_exret
		matrix ff3_alpha_tstat  = raw_exret
	
		forvalues i = 1/3 {
		forvalues j = 1/3 {
			quietly gen exret = `weight'r_`beta'`i'`j' * 100 - rf
			
			* raw excess returns
			quietly summarize exret
			matrix raw_exret[`i',`j'] = r(mean)
			matrix raw_exret_tstat[`i',`j'] = r(mean) / r(sd) * sqrt(r(N))
			
			* CAPM alpha
			quietly reg exret mktrf
			matrix coef = e(b)
			matrix cov = e(V)
			
			matrix capm_alpha_coef[`i',`j'] = coef[1,2]
			matrix capm_alpha_tstat[`i',`j'] = coef[1,2] / sqrt(cov[2,2])
			
			* FF3 alpha
			quietly reg exret mktrf smb hml
			matrix coef = e(b)
			matrix cov = e(V)
			
			matrix ff3_alpha_coef[`i',`j'] = coef[1,4]
			matrix ff3_alpha_tstat[`i',`j'] = coef[1,4] / sqrt(cov[4,4])
			
			drop exret
		}
		}
		
		matrix list raw_exret
		matrix list raw_exret_tstat
		matrix list capm_alpha_coef
		matrix list capm_alpha_tstat
		matrix list ff3_alpha_coef
		matrix list ff3_alpha_tstat
	}
}

