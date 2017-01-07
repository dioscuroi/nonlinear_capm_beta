* histogram

clear
set more off
graph drop _all

local options = "stats(coef tstat) bdec(3) tdec(2) adec(4)"

cd "/Users/dioscuroi/GitHub/nonlinear-capm-beta/figures"


use "/Users/dioscuroi/Research Data/Stocks/Fama_French/ff3factors_daily.dta", clear

* demean factor returns
foreach factor in "smb" "hml" {
	summarize `factor'
	replace `factor' = `factor' - r(mean)
}


* compute forward returns
sort date

gen n = _n
tsset n

foreach factor in "smb" "hml" {
	gen `factor'0 = `factor'

	forvalues i = 1/20 {
		local j = `i' - 1
		gen `factor'`i' = `factor'`j' + F`i'.`factor'
	}

	drop `factor'1-`factor'4
	drop `factor'6-`factor'19
}


* estimate average current/forward returns for each market return quintile
xtile qnt = mktrf, n(5)

foreach factor in "smb" "hml" {
	foreach hor of numlist 0 5 20 {
		bysort qnt: egen avg_`factor'`hor' = mean(`factor'`hor')
	}
}

keep qnt avg_*

renpfix avg_

duplicates drop
