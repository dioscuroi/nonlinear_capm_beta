* average_returns_of_every_stock

clear
set more off
graph drop _all
disp _newline(100)

local options = "stats(coef tstat) bdec(3) tdec(3)"

cd "/Users/dioscuroi/GitHub/nonlinear_capm_beta/stata"

!rm average_returns_of_every_stock*.txt


****************************************************
* Prepare data
****************************************************

* compute average stock returns
use "/Users/dioscuroi/Research Data/Stocks/CRSP stock returns/stocks_monthly_filtered.dta", clear

keep if date >= ym(1926,7)
keep if ret != .
keep date permno ret

merge m:1 date using "/Users/dioscuroi/Research Data/Stocks/Fama_French/ff3factors_monthly.dta", keep(match) nogen

gen exret = ret * 100 - rf

bysort permno: egen cnt = count(ret)
bysort permno: egen avg_exret = mean(exret)

drop if cnt < 5

keep permno cnt avg_exret
duplicates drop

* create a template to save results
gen avg_capm_alpha = .
gen avg_ff3_alpha = .

save average_returns_of_every_stock, replace


* iterate for each stock
use average_returns_of_every_stock, clear

describe

local no_obs = r(N)

forvalues i = 189/`no_obs' {
*forvalues i = 1/5 {

	use average_returns_of_every_stock, clear
	
	local permno = permno[`i']
	
	disp "permno: `permno' (`i'/`no_obs')
	
	use using "/Users/dioscuroi/Research Data/Stocks/CRSP stock returns/stocks_monthly_filtered.dta" if permno == `permno', clear
	
	capture {
		merge 1:1 date using "/Users/dioscuroi/Research Data/Stocks/Fama_French/ff3factors_monthly.dta", keep(match) nogen
		
		gen exret = ret * 100 - rf
		
		reg exret mktrf
		matrix capm = e(b)
		local capm_alpha = capm[1,2]
	
		reg exret mktrf smb hml
		matrix ff3 = e(b)
		local ff3_alpha = ff3[1,4]
	
		use average_returns_of_every_stock, clear
	
		replace avg_capm_alpha = `capm_alpha' if permno == `permno'
		replace avg_ff3_alpha  = `ff3_alpha'  if permno == `permno'
	
		save average_returns_of_every_stock, replace
	}
}
*/
