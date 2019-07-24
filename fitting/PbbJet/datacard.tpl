Combination of datacard.tpl
imax 2 number of bins
jmax * number of processes minus 1
kmax * number of nuisance parameters
----------------------------------------------------------------------------------------------------------------------------------
shapes * fail_CATX base.root w_fail_CATX:$PROCESS_fail_CATX w_fail_CATX:$PROCESS_fail_CATX_$SYSTEMATIC
shapes qcd fail_CATX rhalphabase.root w_fail_CATX:$PROCESS_fail_CATX
shapes * pass_CATX base.root w_pass_CATX:$PROCESS_pass_CATX w_pass_CATX:$PROCESS_pass_CATX_$SYSTEMATIC
shapes qcd pass_CATX rhalphabase.root w_pass_CATX:$PROCESS_pass_CATX
----------------------------------------------------------------------------------------------------------------------------------
bin pass_CATX fail_CATX
observation -1.0 -1.0 
----------------------------------------------------------------------------------------------------------------------------------
bin pass_CATX pass_CATX pass_CATX pass_CATX pass_CATX pass_CATX pass_CATX pass_CATX pass_CATX fail_CATX fail_CATX fail_CATX fail_CATX fail_CATX fail_CATX fail_CATX fail_CATX fail_CATX
process tthqq125 whqq125 hqq125 zhqq125 vbfhqq125 zqq wqq qcd tqq tthqq125 whqq125 hqq125 zhqq125 vbfhqq125 zqq wqq qcd tqq 
process -4 -3 -2 -1 0 1 2 3 4 -4 -3 -2 -1 0 1 2 3 4 
rate -1 -1 -1 -1 -1 -1 -1 1.0 -1 -1 -1 -1 -1 -1 -1 -1 1.0 -1 
----------------------------------------------------------------------------------------------------------------------------------
lumi lnN 1.025 1.025 1.025 1.025 1.025 1.025 1.025 - - 1.025 1.025 1.025 1.025 1.025 1.025 1.025 - -
hqq125pt lnN - - 1.30 - - - - - - - - 1.30 - - - - - -
hqq125ptShape shape - - 1 - - - - - - - - 1 - - - - - -
veff lnN 1.2 1.2 1.2 1.2 1.2 1.2 1.2 - - 1.2 1.2 1.2 1.2 1.2 1.2 1.2 - -
bbeff lnN 1.1 1.1 1.1 1.1 1.1 - - - - 1.1 1.1 1.1 1.1 1.1 - - - -
znormQ lnN - - - - - 1.1 1.1 - - - - - - - 1.1 1.1 - -
znormEW lnN - - - - - 1.05 1.05 - - - - - - - 1.05 1.05 - -
wznormEW lnN - - - - - - 1.02 - - - - - - - - 1.02 - -
#weff lnN - - - - - - 1.00 - - - - - - - - 1.00 - -
JER lnN 1 1 1 1 1 1 1 - 1 1 1 1 1 1 1 1 - 1
JES lnN 1 1 1 1 1 1 1 - 1 1 1 1 1 1 1 1 - 1
Pu lnN 1 1 1 1 1 1 1 - 1 1 1 1 1 1 1 1 - 1
trigger lnN 1.02 1.02 1.02 1.02 1.02 1.02 1.02 - 1.02 1.02 1.02 1.02 1.02 1.02 1.02 1.02 - 1.02
muveto lnN 1.005 1.005 1.005 1.005 1.005 1.005 1.005 - 1.005 1.005 1.005 1.005 1.005 1.005 1.005 1.005 - 1.005
eleveto lnN 1.005 1.005 1.005 1.005 1.005 1.005 1.005 - 1.005 1.005 1.005 1.005 1.005 1.005 1.005 1.005 - 1.005
scale shape 0.1 0.1 0.1 0.1 0.1 0.1 0.1 - - 0.1 0.1 0.1 0.1 0.1 0.1 0.1 - -
#scalept shape 0.1 0.1 0.1 0.1 0.1 0.1 0.1 - - 0.1 0.1 0.1 0.1 0.1 0.1 0.1 - -
smear shape 0.25 0.25 0.25 0.25 0.25 0.25 0.25 - - 0.25 0.25 0.25 0.25 0.25 0.25 0.25 - -
tqqpassCATXnorm rateParam pass_CATX tqq (@0*@1) tqqnormSF,tqqeffSF
tqqfailCATXnorm rateParam fail_CATX tqq (@0*(1.0-@1*TQQEFF)/(1.0-TQQEFF)) tqqnormSF,tqqeffSF
tqqnormSF extArg 1.0 [0.0,10.0]
tqqeffSF extArg 1.0 [0.0,10.0]
