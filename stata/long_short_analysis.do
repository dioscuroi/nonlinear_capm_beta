* long_short_analysis

clear
set more off

local options = "stats(coef tstat) bdec(3) tdec(3)"

cd "/Users/dioscuroi/GitHub/nonlinear_capm_beta/stata"

!rm long_short_analysis*.txt


* load beta statistics
insheet using "beta_stats.csv", clear

* drop outliers
foreach beta of varlist beta_average beta_delay beta_convexity {
	
	_pctile `beta', p(1 99)
	
	drop if `beta' < r(r1)
	drop if `beta' > r(r2)
}

* print the summary of beta
summarize beta_*, detail

* form portfolios
foreach beta of varlist beta_average beta_delay beta_convexity {

	bysort year: egen p33 = pctile(`beta'), p(33)
	bysort year: egen p67 = pctile(`beta'), p(67)
	
	gen pid_`beta' = .
	replace pid_`beta' = 1 if (`beta' < p33)
	replace pid_`beta' = 2 if (`beta' >= p33) & (`beta' < p67)
	replace pid_`beta' = 3 if (`beta' >= p67)
	
	drop p33 p67
}

*gen pid_beta_convexity = .
*replace pid_beta_convexity = 1 if beta_convexity < 0
*replace pid_beta_convexity = 2 if beta_convexity == 0
*replace pid_beta_convexity = 3 if beta_convexity > 0


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


* print regression results
use temp_portfolio_returns_combined, clear

merge 1:1 date using "/Users/dioscuroi/Research Data/Stocks/Fama_French/ff3factors_monthly.dta", nogen

foreach beta in beta_average beta_delay beta_convexity {

	foreach weight in ew vw {
	
		gen exret1 = `weight'r_`beta'1 * 100 - rf
		gen exret2 = `weight'r_`beta'2 * 100 - rf
		gen exret3 = `weight'r_`beta'3 * 100 - rf

		reg exret1 mktrf
		outreg2 using "long_short_analysis_`beta'_`weight'_CAPM.txt", `option'
		
		reg exret2 mktrf
		outreg2 using "long_short_analysis_`beta'_`weight'_CAPM.txt", `option'
		
		reg exret3 mktrf
		outreg2 using "long_short_analysis_`beta'_`weight'_CAPM.txt", `option'

		reg exret1 mktrf smb hml
		outreg2 using "long_short_analysis_`beta'_`weight'_FF3.txt", `option'

		reg exret2 mktrf smb hml
		outreg2 using "long_short_analysis_`beta'_`weight'_FF3.txt", `option'

		reg exret3 mktrf smb hml
		outreg2 using "long_short_analysis_`beta'_`weight'_FF3.txt", `option'
		
		drop exret1 exret2 exret3

	}
}




