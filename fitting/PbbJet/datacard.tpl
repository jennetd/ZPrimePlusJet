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
bin pass_CATX pass_CATX pass_CATX pass_CATX pass_CATX pass_CATX pass_CATX pass_CATX pass_CATX pass_CATX pass_CATX pass_CATX fail_CATX fail_CATX fail_CATX fail_CATX fail_CATX fail_CATX fail_CATX fail_CATX fail_CATX fail_CATX fail_CATX fail_CATX
process ttH_hbb WH_hbb ggH_hbbGenpt1 ggH_hbbGenpt2 ggH_hbbGenpt3 ggH_hbbGenpt4 ZH_hbb qqH_hbb zqq wqq qcd tqq ttH_hbb WH_hbb ggH_hbbGenpt1 ggH_hbbGenpt2 ggH_hbbGenpt3 ggH_hbbGenpt4 ZH_hbb qqH_hbb zqq wqq qcd tqq 
process -4 -3 -2 -1 -5 -6 -7 0 1 2 3 4 -4 -3 -2 -1 -5 -6 -7 0 1 2 3 4 
rate -1 -1 -1 -1 -1 -1 -1 -1 -1 -1 1.0 -1 -1 -1 -1 -1 -1 -1 -1 -1 -1 -1 1.0 -1 
----------------------------------------------------------------------------------------------------------------------------------
lumi_13TeV lnN 1.025 1.025 1.025 1.025 1.025 1.025 1.025 1.025 1.025 1.025 - - 1.025 1.025 1.025 1.025 1.025 1.025 1.025 1.025 1.025 1.025 - -
#CMS_gghbb_ggHpt lnN - - 1.30 - - - - - - - - 1.30 - - - - - -
#CMS_gghbb_ggHptShape shape - - 1 - - - - - - - - 1 - - - - - -
CMS_gghbb_veff lnN 1.2 1.2 1.2 1.2 1.2 1.2 1.2 1.2 1.2 1.2 - - 1.2 1.2 1.2 1.2 1.2 1.2 1.2 1.2 1.2 1.2 - -
CMS_eff_bb lnN 1.1 1.1 1.1 1.1 1.1 1.1 1.1 1.1 - - - - 1.1 1.1 1.1 1.1 1.1 1.1 1.1 1.1 - - - -
CMS_gghbb_znormQ lnN - - - - - - - - 1.1 1.1 - - - - - - - - - - 1.1 1.1 - -
CMS_gghbb_znormEW lnN - - - - - - - - 1.05 1.05 - - - - - - - - - - 1.05 1.05 - -
CMS_gghbb_wznormEW lnN - - - - - - - - - 1.02 - - - - - - - - - - - 1.02 - -
#weff lnN - - - - - - 1.00 - - - - - - - - 1.00 - -
CMS_res_j lnN 1 1 1 1 1 1 1 1 1 1 - 1 1 1 1 1 1 1 1 1 1 1 - 1
CMS_scale_j lnN 1 1 1 1 1 1 1 1 1 1 - 1 1 1 1 1 1 1 1 1 1 1 - 1
CMS_PU lnN 1 1 1 1 1 1 1 1 1 1 - 1 1 1 1 1 1 1 1 1 1 1 - 1
CMS_gghbb_trigger lnN 1.02 1.02 1.02 1.02 1.02 1.02 1.02 1.02 1.02 1.02 - 1.02 1.02 1.02 1.02 1.02 1.02 1.02 1.02 1.02 1.02 1.02 - 1.02
CMS_gghbb_m_veto lnN 1.005 1.005 1.005 1.005 1.005 1.005 1.005 1.005 1.005 1.005 - 1.005 1.005 1.005 1.005 1.005 1.005 1.005 1.005 1.005 1.005 1.005 - 1.005
CMS_gghbb_e_veto lnN 1.005 1.005 1.005 1.005 1.005 1.005 1.005 1.005 1.005 1.005 - 1.005 1.005 1.005 1.005 1.005 1.005 1.005 1.005 1.005 1.005 1.005 - 1.005
CMS_gghbb_scale shape 0.1 0.1 0.1 0.1 0.1 0.1 0.1 0.1 0.1 0.1 - - 0.1 0.1 0.1 0.1 0.1 0.1 0.1 0.1 0.1 0.1 - -
#CMS_gghbb_scalept shape 0.1 0.1 0.1 0.1 0.1 0.1 0.1 0.1 0.1 0.1 - - 0.1 0.1 0.1 0.1 0.1 0.1 0.1 0.1 0.1 0.1 - -
CMS_gghbb_smear shape 0.25 0.25 0.25 0.25 0.25 0.25 0.25 0.25 0.25 0.25 - - 0.25 0.25 0.25 0.25 0.25 0.25 0.25 0.25 0.25 0.25- -
tqqpassCATXnorm rateParam pass_CATX tqq (@0*@1) CMS_gghbb_tqqnormSF,CMS_gghbb_tqqeffSF
tqqfailCATXnorm rateParam fail_CATX tqq (@0*(1.0-@1*TQQEFF)/(1.0-TQQEFF)) CMS_gghbb_tqqnormSF,CMS_gghbb_tqqeffSF
CMS_gghbb_tqqnormSF extArg 1.0 [0.0,10.0]
CMS_gghbb_tqqeffSF extArg 1.0 [0.0,10.0]
