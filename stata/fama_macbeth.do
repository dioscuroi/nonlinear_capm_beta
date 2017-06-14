* fama_macbeth.do

clear
set more off
disp _newline(100)

local options = "stats(coef tstat) bdec(3) tdec(3)"

cd "/Users/dioscuroi/GitHub/nonlinear_capm_beta/stata"

!rm fama_macbeth*.txt


