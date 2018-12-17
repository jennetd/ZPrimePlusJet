import os
import math
from array import array
from optparse import OptionParser
import ROOT
import sys
sys.path.append(os.path.expandvars("$CMSSW_BASE/src/DAZSLE/ZPrimePlusJet/analysis"))

from sampleContainer import *
from normSampleContainer import *

def get2016files(isMuonCR):
    #from  commit: ed54500
    idir     = 'root://cmseos.fnal.gov//eos/uscms/store/user/lpchbb/zprimebits-v12.04/cvernier'
    idirData = 'root://cmseos.fnal.gov//eos/uscms/store/user/lpchbb/zprimebits-v12.05/'
    
    tfiles = {
        'hqq125': #[idir + '/GluGluHToBB_M125_13TeV_powheg_pythia8_all_1000pb_weighted_corrected.root'],
                  #[idir + '/GluGluHToBB_M125_13TeV_powheg_pythia8_all_1000pb_weighted.root'],
                  #[idirData + '/GluGluHToBB_M125_13TeV_powheg_pythia8_2Jet_1000pb_weighted.root'],
                  [idirData + '/GluGluHToBB_M125_13TeV_powheg_pythia8_CKKW_1000pb_weighted.root'],
                  #[idirData + '/GluGluHToBB_M125_13TeV_powheg_pythia8_YR4_1000pb_weighted.root'],
        # 'VBFHbb': [idir+'/VBFHToBB_M125_13TeV_amcatnlo_pythia8_1000pb_weighted.root'],
        'vbfhqq125': [idir + '/VBFHToBB_M_125_13TeV_powheg_pythia8_weightfix_all_1000pb_weighted.root'],
        'zhqq125': [idir + '/ZH_HToBB_ZToQQ_M125_13TeV_powheg_pythia8_1000pb_weighted.root',
                    idir + '/ggZH_HToBB_ZToNuNu_M125_13TeV_powheg_pythia8_1000pb_weighted.root',
                    idir + '/ZH_HToBB_ZToNuNu_M125_13TeV_powheg_pythia8_ext_1000pb_weighted.root',
                    idir + '/ggZH_HToBB_ZToQQ_M125_13TeV_powheg_pythia8_1000pb_weighted.root'],
        'whqq125': [idir + '/WminusH_HToBB_WToQQ_M125_13TeV_powheg_pythia8_1000pb_weighted.root',
                    idir + '/WplusH_HToBB_WToQQ_M125_13TeV_powheg_pythia8_1000pb_weighted.root'],
        'tthqq125': [idir + '/ttHTobb_M125_13TeV_powheg_pythia8_1000pb_weighted.root'],
        # ttHTobb_M125_TuneCUETP8M2_ttHtranche3_13TeV_powheg_pythia8_1000pb_weighted.root'],
        'vvqq': [idir + '/WWTo4Q_13TeV_powheg_1000pb_weighted.root',
                 idir + '/ZZ_13TeV_pythia8_1000pb_weighted.root',
                 idir + '/WZ_13TeV_pythia8_1000pb_weighted.root'],
        'zqq': [idir + '/DYJetsToQQ_HT180_13TeV_1000pb_weighted_v1204.root'],
        # ZJetsToQQ_HT600toInf_13TeV_madgraph_1000pb_weighted.root'],#DYJetsToQQ_HT180_13TeV_1000pb_weighted.root '],
        'stqq': [
            idir + '/ST_t_channel_antitop_4f_inclusiveDecays_TuneCUETP8M2T4_13TeV_powhegV2_madspin_1000pb_weighted.root',
            idir + '/ST_t_channel_top_4f_inclusiveDecays_TuneCUETP8M2T4_13TeV_powhegV2_madspin_1000pb_weighted.root',
            idir + '/ST_tW_antitop_5f_inclusiveDecays_13TeV_powheg_pythia8_TuneCUETP8M2T4_1000pb_weighted.root',
            idir + '/ST_tW_top_5f_inclusiveDecays_13TeV_powheg_pythia8_TuneCUETP8M2T4_1000pb_weighted.root'],
        # 'W':  [idir+'/WJetsToQQ_HT_600ToInf_13TeV_1000pb_weighted.root'],
        'wqq': [idir + '/WJetsToQQ_HT180_13TeV_1000pb_weighted_v1204.root'],
        'wlnu': [idir + '/WJetsToLNu_HT_100To200_13TeV_1000pb_weighted.root',
                 idir + '/WJetsToLNu_HT_200To400_13TeV_1000pb_weighted.root',
                 idir + '/WJetsToLNu_HT_400To600_13TeV_1000pb_weighted.root',
                 idir + '/WJetsToLNu_HT_600To800_13TeV_1000pb_weighted.root',
                 idir + '/WJetsToLNu_HT_800To1200_13TeV_1000pb_weighted.root',
                 idir + '/WJetsToLNu_HT_1200To2500_13TeV_1000pb_weighted.root'],
        'zll': [idir + '/DYJetsToLL_M_50_13TeV_ext_1000pb_weighted.root'],
        # 'TTbar':  [idir+'/TTJets_13TeV_1000pb_weighted.root'], #MadGraph is the old default
        'tqq': [idir + '/TT_powheg_1000pb_weighted_v1204.root'],  # Powheg is the new default
        'qcd': [idir + '/QCD_HT100to200_13TeV_1000pb_weighted.root',
                idir + '/QCD_HT200to300_13TeV_all_1000pb_weighted.root',
                idir + '/QCD_HT300to500_13TeV_all_1000pb_weighted.root',
                idir + '/QCD_HT500to700_13TeV_ext_1000pb_weighted.root',
                idir + '/QCD_HT700to1000_13TeV_ext_1000pb_weighted.root',
                idir + '/QCD_HT1000to1500_13TeV_all_1000pb_weighted.root',
                idir + '/QCD_HT1500to2000_13TeV_all_1000pb_weighted.root',
                idir + '/QCD_HT2000toInf_13TeV_1000pb_weighted.root'],
        'Phibb50': [idir + '/Spin0_ggPhi12j_g1_50_Scalar_13TeV_madgraph_1000pb_weighted.root'],
        'Phibb75': [idir + '/Spin0_ggPhi12j_g1_75_Scalar_13TeV_madgraph_1000pb_weighted.root'],
        'Phibb150': [idir + '/Spin0_ggPhi12j_g1_150_Scalar_13TeV_madgraph_1000pb_weighted.root'],
        'Phibb250': [idir + '/Spin0_ggPhi12j_g1_250_Scalar_13TeV_madgraph_1000pb_weighted.root'],
        'data_obs': [idirData+'JetHTRun2016B_03Feb2017_ver2_v2_v3.root',
                     idirData + 'JetHTRun2016B_03Feb2017_ver1_v1_v3.root',
                     idirData + 'JetHTRun2016C_03Feb2017_v1_v3_0.root',
                     idirData + 'JetHTRun2016C_03Feb2017_v1_v3_1.root',
                     idirData + 'JetHTRun2016C_03Feb2017_v1_v3_2.root',
                     idirData + 'JetHTRun2016C_03Feb2017_v1_v3_3.root',
                     idirData + 'JetHTRun2016C_03Feb2017_v1_v3_4.root',
                     idirData + 'JetHTRun2016C_03Feb2017_v1_v3_5.root',
                     idirData + 'JetHTRun2016C_03Feb2017_v1_v3_6.root',
                     idirData + 'JetHTRun2016C_03Feb2017_v1_v3_7.root',
                     idirData + 'JetHTRun2016C_03Feb2017_v1_v3_8.root',
                     idirData + 'JetHTRun2016C_03Feb2017_v1_v3_9.root',
                     idirData + 'JetHTRun2016D_03Feb2017_v1_v3_0.root',
                     idirData + 'JetHTRun2016D_03Feb2017_v1_v3_1.root',
                     idirData + 'JetHTRun2016D_03Feb2017_v1_v3_10.root',
                     idirData + 'JetHTRun2016D_03Feb2017_v1_v3_11.root',
                     idirData + 'JetHTRun2016D_03Feb2017_v1_v3_12.root',
                     idirData + 'JetHTRun2016D_03Feb2017_v1_v3_13.root',
                     idirData + 'JetHTRun2016D_03Feb2017_v1_v3_14.root',
                     idirData + 'JetHTRun2016D_03Feb2017_v1_v3_2.root',
                     idirData + 'JetHTRun2016D_03Feb2017_v1_v3_3.root',
                     idirData + 'JetHTRun2016D_03Feb2017_v1_v3_4.root',
                     idirData + 'JetHTRun2016D_03Feb2017_v1_v3_5.root',
                     idirData + 'JetHTRun2016D_03Feb2017_v1_v3_6.root',
                     idirData + 'JetHTRun2016D_03Feb2017_v1_v3_7.root',
                     idirData + 'JetHTRun2016D_03Feb2017_v1_v3_8.root',
                     idirData + 'JetHTRun2016D_03Feb2017_v1_v3_9.root',
                     idirData + 'JetHTRun2016E_03Feb2017_v1_v3_0.root',
                     idirData + 'JetHTRun2016E_03Feb2017_v1_v3_1.root',
                     idirData + 'JetHTRun2016E_03Feb2017_v1_v3_2.root',
                     idirData + 'JetHTRun2016E_03Feb2017_v1_v3_3.root',
                     idirData + 'JetHTRun2016E_03Feb2017_v1_v3_4.root',
                     idirData + 'JetHTRun2016E_03Feb2017_v1_v3_5.root',
                     idirData + 'JetHTRun2016E_03Feb2017_v1_v3_6.root',
                     idirData + 'JetHTRun2016E_03Feb2017_v1_v3_7.root',
                     idirData + 'JetHTRun2016E_03Feb2017_v1_v3_8.root',
                     idirData + 'JetHTRun2016E_03Feb2017_v1_v3_9.root',
                     idirData + 'JetHTRun2016E_03Feb2017_v1_v3_10.root',
                     idirData + 'JetHTRun2016E_03Feb2017_v1_v3_11.root',
                     idirData + 'JetHTRun2016E_03Feb2017_v1_v3_12.root',
                     idirData + 'JetHTRun2016E_03Feb2017_v1_v3_13.root',
                     idirData + 'JetHTRun2016E_03Feb2017_v1_v3_14.root',
                     idirData + 'JetHTRun2016F_03Feb2017_v1_v3_0.root',
                     idirData + 'JetHTRun2016F_03Feb2017_v1_v3_1.root',
                     idirData + 'JetHTRun2016F_03Feb2017_v1_v3_2.root',
                     idirData + 'JetHTRun2016F_03Feb2017_v1_v3_3.root',
                     idirData + 'JetHTRun2016F_03Feb2017_v1_v3_4.root',
                     idirData + 'JetHTRun2016F_03Feb2017_v1_v3_5.root',
                     idirData + 'JetHTRun2016F_03Feb2017_v1_v3_6.root',
                     idirData + 'JetHTRun2016F_03Feb2017_v1_v3_7.root',
                     idirData + 'JetHTRun2016F_03Feb2017_v1_v3_8.root',
                     idirData + 'JetHTRun2016F_03Feb2017_v1_v3_9.root',
                     idirData + 'JetHTRun2016F_03Feb2017_v1_v3_10.root',
                     idirData + 'JetHTRun2016G_03Feb2017_v1_v3_0.root',
                     idirData + 'JetHTRun2016G_03Feb2017_v1_v3_1.root',
                     idirData + 'JetHTRun2016G_03Feb2017_v1_v3_2.root',
                     idirData + 'JetHTRun2016G_03Feb2017_v1_v3_3.root',
                     idirData + 'JetHTRun2016G_03Feb2017_v1_v3_4.root',
                     idirData + 'JetHTRun2016G_03Feb2017_v1_v3_5.root',
                     idirData + 'JetHTRun2016G_03Feb2017_v1_v3_6.root',
                     idirData + 'JetHTRun2016G_03Feb2017_v1_v3_7.root',
                     idirData + 'JetHTRun2016G_03Feb2017_v1_v3_8.root',
                     idirData + 'JetHTRun2016G_03Feb2017_v1_v3_9.root',
                     idirData + 'JetHTRun2016G_03Feb2017_v1_v3_10.root',
                     idirData + 'JetHTRun2016G_03Feb2017_v1_v3_11.root',
                     idirData + 'JetHTRun2016G_03Feb2017_v1_v3_12.root',
                     idirData + 'JetHTRun2016G_03Feb2017_v1_v3_13.root',
                     idirData + 'JetHTRun2016G_03Feb2017_v1_v3_14.root',
                     idirData + 'JetHTRun2016G_03Feb2017_v1_v3_15.root',
                     idirData + 'JetHTRun2016G_03Feb2017_v1_v3_16.root',
                     idirData + 'JetHTRun2016G_03Feb2017_v1_v3_17.root',
                     idirData + 'JetHTRun2016G_03Feb2017_v1_v3_18.root',
                     idirData + 'JetHTRun2016G_03Feb2017_v1_v3_19.root',
                     idirData + 'JetHTRun2016G_03Feb2017_v1_v3_20.root',
                     idirData + 'JetHTRun2016G_03Feb2017_v1_v3_21.root',
                     idirData + 'JetHTRun2016G_03Feb2017_v1_v3_22.root',
                     idirData + 'JetHTRun2016G_03Feb2017_v1_v3_23.root',
                     idirData + 'JetHTRun2016G_03Feb2017_v1_v3_24.root',
                     idirData + 'JetHTRun2016G_03Feb2017_v1_v3_25.root',
                     idirData + 'JetHTRun2016H_03Feb2017_ver2_v1_v3_0.root',
                     idirData + 'JetHTRun2016H_03Feb2017_ver2_v1_v3_1.root',
                     idirData + 'JetHTRun2016H_03Feb2017_ver2_v1_v3_2.root',
                     idirData + 'JetHTRun2016H_03Feb2017_ver2_v1_v3_3.root',
                     idirData + 'JetHTRun2016H_03Feb2017_ver2_v1_v3_4.root',
                     idirData + 'JetHTRun2016H_03Feb2017_ver2_v1_v3_5.root',
                     idirData + 'JetHTRun2016H_03Feb2017_ver2_v1_v3_6.root',
                     idirData + 'JetHTRun2016H_03Feb2017_ver2_v1_v3_7.root',
                     idirData + 'JetHTRun2016H_03Feb2017_ver2_v1_v3_8.root',
                     idirData + 'JetHTRun2016H_03Feb2017_ver2_v1_v3_9.root',
                     idirData + 'JetHTRun2016H_03Feb2017_ver2_v1_v3_10.root',
                     idirData + 'JetHTRun2016H_03Feb2017_ver2_v1_v3_11.root',
                     idirData + 'JetHTRun2016H_03Feb2017_ver2_v1_v3_12.root',
                     idirData + 'JetHTRun2016H_03Feb2017_ver2_v1_v3_13.root',
                     idirData + 'JetHTRun2016H_03Feb2017_ver2_v1_v3_14.root',
                     idirData + 'JetHTRun2016H_03Feb2017_ver2_v1_v3_15.root',
                     idirData + 'JetHTRun2016H_03Feb2017_ver2_v1_v3_16.root',
                     idirData + 'JetHTRun2016H_03Feb2017_ver2_v1_v3_17.root',
                     idirData + 'JetHTRun2016H_03Feb2017_ver2_v1_v3_18.root',
                     idirData + 'JetHTRun2016H_03Feb2017_ver2_v1_v3_19.root',
                     idirData + 'JetHTRun2016H_03Feb2017_ver2_v1_v3_20.root',
                     idirData + 'JetHTRun2016H_03Feb2017_ver2_v1_v3_21.root',
                     idirData + 'JetHTRun2016H_03Feb2017_ver2_v1_v3_22.root',
                     idirData + 'JetHTRun2016H_03Feb2017_ver2_v1_v3_23.root',
                     idirData + 'JetHTRun2016H_03Feb2017_ver2_v1_v3_24.root',
                     idirData + 'JetHTRun2016H_03Feb2017_ver2_v1_v3_25.root',
                     idirData + 'JetHTRun2016H_03Feb2017_ver3_v1_v3.root']
    }

    if isMuonCR:
        tfiles['data_obs'] = [idir + '/SingleMuonRun2016B_03Feb2017_ver1_v1_fixtrig.root',
                              idir + '/SingleMuonRun2016B_03Feb2017_ver2_v2_fixtrig.root',
                              idir + '/SingleMuonRun2016C_03Feb2017_v1_fixtrig.root',
                              idir + '/SingleMuonRun2016D_03Feb2017_v1_fixtrig.root',
                              idir + '/SingleMuonRun2016E_03Feb2017_v1_fixtrig.root',
                              idir + '/SingleMuonRun2016F_03Feb2017_v1_fixtrig.root',
                              idir + '/SingleMuonRun2016G_03Feb2017_v1_fixtrig.root',
                              idir + '/SingleMuonRun2016H_03Feb2017_ver2_v1_fixtrig.root',
                              idir + '/SingleMuonRun2016H_03Feb2017_ver3_v1_fixtrig.root']
    return tfiles


def get2017files(isMuonCR):
    idir = 'root://cmseos.fnal.gov//eos/uscms/store/user/lpchbb/zprimebits-v12.04/cvernier'
    idir_temp = 'root://cmseos.fnal.gov//eos/uscms/store/user/lpchbb/zprimebits-v12.04/cvernier/'
    idir_1207 = 'root://cmseos.fnal.gov//eos/uscms/store/user/lpcbacon/dazsle/zprimebits-v12.07-puWeight/norm'
    idir_1208 = 'root://cmseos.fnal.gov//eos/uscms/store/user/lpcbacon/dazsle/zprimebits-v12.08/norm'
    idirData = 'root://cmseos.fnal.gov//eos/uscms/store/user/lpcbacon/dazsle/zprimebits-v12.07/sklim'
    idir_1401 = 'root://cmseos.fnal.gov//eos/uscms/store/user/lpcbacon/dazsle/zprimebits-v14.01/'
    idir_1401skim = 'root://cmseos.fnal.gov//eos/uscms/store/user/lpcbacon/dazsle/zprimebits-v14.01/skim/'

    tfiles = {
        'hqq125': #[idir_temp + '/GluGluHToBB_M125_13TeV_powheg_pythia8_all_1000pb_weighted_corrected.root'],
                  #[idir_temp + '/GluGluHToBB_M125_13TeV_powheg_pythia8_all_1000pb_weighted.root'],
                  [idir_1207 + '/GluGluHToBB_M125_13TeV_powheg_pythia8_1000pb_weighted.root'],
                  #[idirData + '/GluGluHToBB_M125_13TeV_powheg_pythia8_YR4_1000pb_weighted.root'],
	    #'hqq125' :    { 'GluGluHToBB_M125_LHEHpT_250_Inf_13TeV_amcatnloFXFX_pythia8' :[idir_1401+'GluGluHToBB_M125_LHEHpT_250_Inf_13TeV_amcatnloFXFX_pythia8/*.root']},
        # 'VBFHbb': [idir_temp+'/VBFHToBB_M125_13TeV_amcatnlo_pythia8_1000pb_weighted.root'],
        'vbfhqq125': [idir_1207 + '/VBFHToBB_M_125_13TeV_powheg_pythia8_weightfix_1000pb_weighted.root'],
        'zhqq125': [idir_1207 + '/ZH_HToBB_ZToNuNu_M125_13TeV_powheg_pythia8_1000pb_weighted.root',
                    idir_1207 + '/ggZH_HToBB_ZToNuNu_M125_13TeV_powheg_herwigpp_1000pb_weighted.root',
                    idir_1207 + '/ZH_HToBB_ZToQQ_M125_13TeV_powheg_pythia8_1000pb_weighted.root',
                    idir_1207 + '/ggZH_HToBB_ZToQQ_M125_13TeV_powheg_pythia8_1000pb_weighted.root'],
        'whqq125': [idir_1207 + '/WminusH_HToBB_WToQQ_M125_13TeV_powheg_pythia8_1000pb_weighted.root',
                    idir_1207 + '/WplusH_HToBB_WToQQ_M125_13TeV_powheg_pythia8_1000pb_weighted.root'],
        'tthqq125': [idir_1207 + '/ttHTobb_M125_TuneCP5_13TeV_powheg_pythia8_1000pb_weighted.root'],
        # ttHTobb_M125_TuneCUETP8M2_ttHtranche3_13TeV_powheg_pythia8_1000pb_weighted.root'],
        'vvqq': [idir_1207 + '/WW_TuneCP5_13TeV_pythia8_1000pb_weighted.root',
                 idir_1207 + '/ZZ_TuneCP5_13TeV_pythia8_1000pb_weighted.root',
                 idir_1207 + '/WZ_TuneCP5_13TeV_pythia8_1000pb_weighted.root'],
        'zqq':   {
                            'ZJetsToQQ_HT400to600_qc19_4j_TuneCP5_13TeV': [idir_1401skim + 'ZJetsToQQ_HT400to600_qc19_4j_TuneCP5_13TeV*.root'],
                            'ZJetsToQQ_HT600to800_qc19_4j_TuneCP5_13TeV': [idir_1401skim + 'ZJetsToQQ_HT600to800_qc19_4j_TuneCP5_13TeV*.root'],
                            'ZJetsToQQ_HT-800toInf_qc19_4j_TuneCP5_13TeV':[idir_1401skim + 'ZJetsToQQ_HT_800toInf_qc19_4j_TuneCP5_13TeV*.root'],
                  },
        'zll': [idir + '/DYJetsToLL_M_50_13TeV_ext_1000pb_weighted.root'],
        # ZJetsToQQ_HT600toInf_13TeV_madgraph_1000pb_weighted.root'],#DYJetsToQQ_HT180_13TeV_1000pb_weighted.root '],
        'stqq': [idir_1207 + '/ST_s_channel_4f_leptonDecays_TuneCP5_13TeV_amcatnlo_pythia8_noPF_1000pb_weighted.root',
                 idir_1207 + '/ST_tW_antitop_5f_inclusiveDecays_TuneCP5_13TeV_powheg_pythia8_1000pb_weighted.root',
                 idir_1207 + '/ST_tW_top_5f_inclusiveDecays_TuneCP5_13TeV_powheg_pythia8_1000pb_weighted.root',
                 idir_1207 + '/ST_t_channel_antitop_4f_inclusiveDecays_TuneCP5_13TeV_powhegV2_madspin_pythia8_1000pb_weighted.root',
                 idir_1207 + '/ST_t_channel_top_4f_inclusiveDecays_TuneCP5_13TeV_powhegV2_madspin_pythia8_1000pb_weighted.root'],
        'wqq'         : {
                              'WJetsToQQ_HT400to600_qc19_3j_TuneCP5_13TeV': [idir_1401skim + 'WJetsToQQ_HT400to600_qc19_3j_TuneCP5_13TeV*.root'],
                              'WJetsToQQ_HT600to800_qc19_3j_TuneCP5_13TeV': [idir_1401skim + 'WJetsToQQ_HT600to800_qc19_3j_TuneCP5_13TeV*.root'],
                              'WJetsToQQ_HT-800toInf_qc19_3j_TuneCP5_13TeV':[idir_1401skim + 'WJetsToQQ_HT_800toInf_qc19_3j_TuneCP5_13TeV*.root'],
                         },
        'wlnu':         {
                              # "WJetsToLNu_TuneCP5_13TeV-madgraphMLM-pythia8"               :[ idir_1401skim+'WJetsToLNu_TuneCP5_13TeV*.root'],
                               "WJetsToLNu_HT-200To400_TuneCP5_13TeV-madgraphMLM-pythia8"   :[ idir_1401skim+'WJetsToLNu_HT_200To400_*.root'],
                               "WJetsToLNu_HT-400To600_TuneCP5_13TeV-madgraphMLM-pythia8"   :[ idir_1401skim+'WJetsToLNu_HT_400To600_*.root'],
                               "WJetsToLNu_HT-600To800_TuneCP5_13TeV-madgraphMLM-pythia8"   :[ idir_1401skim+'WJetsToLNu_HT_600To800_*.root'],
                               "WJetsToLNu_HT-800To1200_TuneCP5_13TeV-madgraphMLM-pythia8"  :[ idir_1401skim+'WJetsToLNu_HT_800To1200_*.root'],
                               "WJetsToLNu_HT-1200To2500_TuneCP5_13TeV-madgraphMLM-pythia8" :[ idir_1401skim+'WJetsToLNu_HT_1200To2500_*.root'],
                              # "WJetsToLNu_HT-2500ToInf_TuneCP5_13TeV-madgraphMLM-pythia8" :[ idir_1401skim+'WJetsToLNu_HT_2500ToInf*.root'],
                            },
        # 'TTbar':  [idir+'/TTJets_13TeV_1000pb_weighted.root'], #MadGraph is the old default
        'tqq': [idir_1207 + '/TTToHadronic_TuneCP5_13TeV_powheg_pythia8_byLumi_1000pb_weighted.root',
		        idir_1207 + '/TTToSemiLeptonic_TuneCP5_13TeV_powheg_pythia8_byLumi_1000pb_weighted.root'],  # Powheg is the new default
        'qcd': [#idir_1207 + '/QCD_HT100to200_13TeV_1000pb_weighted.root',
                #idir_1207 + '/QCD_HT200to300_13TeV_all_1000pb_weighted.root',
                idir_1207 + '/QCD_HT300to500_TuneCP5_13TeV_madgraph_pythia8_noPF_byLumi_1000pb_weighted.root',
                idir_1207 + '/QCD_HT500to700_TuneCP5_13TeV_madgraph_pythia8_noPF_byLumi_1000pb_weighted.root',
                idir_1207 + '/QCD_HT700to1000_TuneCP5_13TeV_madgraph_pythia8_noPF_byLumi_1000pb_weighted.root',
                idir_1207 + '/QCD_HT1000to1500_TuneCP5_13TeV_madgraph_pythia8_1000pb_weighted.root',
                idir_1207 + '/QCD_HT1500to2000_TuneCP5_13TeV_madgraph_pythia8_1000pb_weighted.root',
                idir_1207 + '/QCD_HT2000toInf_TuneCP5_13TeV_madgraph_pythia8_1000pb_weighted.root'],
        'data_obs': [idirData + '/JetHTRun2017C_17Nov2017_v1_noPF.root',
                     idirData + '/JetHTRun2017D_17Nov2017_v1_noPF.root',
                     idirData + '/JetHTRun2017E_17Nov2017_v1_noPF.root',
                     idirData + '/JetHTRun2017F_17Nov2017_v1_noPF.root'],
    }

    if isMuonCR:
        tfiles['data_obs'] = [
                       #idirData+'/SingleMuonRun2017B_17Nov2017_v1_noPF.root',
                       idirData+'/SingleMuonRun2017C_17Nov2017_v1_noPF.root',
                       idirData+'/SingleMuonRun2017D_17Nov2017_v1_noPF.root',
                       idirData+'/SingleMuonRun2017E_17Nov2017_v1_noPF.root',
                       idirData+'/SingleMuonRun2017F_17Nov2017_v1_noPF.root'
                              ]
    return tfiles


    

##----##----##----##----##----##----##
def main(options, args):
#    idir = options.idir
    odir = options.odir
    lumi = options.lumi
    muonCR = options.muonCR
    dbtagmin = options.dbtagmin
    dbtagcut = options.dbtagcut
    is2017   = options.is2017
    sfData   = options.sfData

    fileName = 'hist_1DZbb_pt_scalesmear_%s.root'%options.iSplit
    if options.skipQCD:
    	fileName = 'hist_1DZbb_pt_scalesmear_looserWZ_%s.root'%options.iSplit
    if options.bb:
        fileName = 'hist_1DZbb_sortByBB_%s.root'%options.iSplit
    elif muonCR:
        fileName = 'hist_1DZbb_muonCR_%s.root'%options.iSplit

    outfile = ROOT.TFile(options.odir + "/" + fileName, "recreate")
    
    if is2017:
        #tfiles = get2017files(muonCR)
        samplefiles   = open(os.path.expandvars("$ZPRIMEPLUSJET_BASE/analysis/ggH/samplefiles.json"),"r")
        if muonCR:
            tfiles  = json.load(samplefiles)['Hbb_create_2017_muCR']
        else:
            tfiles  = json.load(samplefiles)['Hbb_create_2017']
        puOpt  = "2017"
    else:
        tfiles = get2016files(muonCR)
        puOpt  = "2016"

    passfail    = ['pass','fail']
    systematics = ['JESUp','JESDown','JERUp','JERDown','triggerUp','triggerDown','PuUp','PuDown','matched','unmatched']
    plots = []
    region  = options.region
    print "Selecting doubleB pass/fail plots for this region   =  %s"% region
    for pf in passfail:
        hname  ="h_msd_v_pt_ak8_%s_%s"%(region,pf)
        plots.append(hname)
        for sys in systematics:
            hname_sys  = "h_msd_v_pt_ak8_%s_%s_%s"%(region,pf,sys)
            plots.append(hname_sys)

    #plots = ['h_msd_v_pt_ak8_topR6_N2_pass', 'h_msd_v_pt_ak8_topR6_N2_fail',
    #         # SR with N2DDT @ 26% && db > 0.9, msd corrected
    #         'h_msd_v_pt_ak8_topR6_N2_pass_matched', 'h_msd_v_pt_ak8_topR6_N2_pass_unmatched',
    #         # matched and unmatached for mass up/down
    #         'h_msd_v_pt_ak8_topR6_N2_fail_matched', 'h_msd_v_pt_ak8_topR6_N2_fail_unmatched',
    #         # matched and unmatached for mass up/down
    #         'h_msd_v_pt_ak8_topR6_N2_pass_JESUp', 'h_msd_v_pt_ak8_topR6_N2_pass_JESDown',  # JES up/down
    #         'h_msd_v_pt_ak8_topR6_N2_fail_JESUp', 'h_msd_v_pt_ak8_topR6_N2_fail_JESDown',  # JES up/down
    #         'h_msd_v_pt_ak8_topR6_N2_pass_JERUp', 'h_msd_v_pt_ak8_topR6_N2_pass_JERDown',  # JER up/down
    #         'h_msd_v_pt_ak8_topR6_N2_fail_JERUp', 'h_msd_v_pt_ak8_topR6_N2_fail_JERDown',  # JER up/down
    #         'h_msd_v_pt_ak8_topR6_N2_pass_triggerUp', 'h_msd_v_pt_ak8_topR6_N2_pass_triggerDown',  # trigger up/down
    #         'h_msd_v_pt_ak8_topR6_N2_fail_triggerUp', 'h_msd_v_pt_ak8_topR6_N2_fail_triggerDown',  # trigger up/down
    #         'h_msd_v_pt_ak8_topR6_N2_pass_PuUp', 'h_msd_v_pt_ak8_topR6_N2_pass_PuDown',  # Pu up/downxf
    #         'h_msd_v_pt_ak8_topR6_N2_fail_PuUp', 'h_msd_v_pt_ak8_topR6_N2_fail_PuDown',  # trigger up/down
    #         ]
    print "N plots = %s "%(len(plots))
    print "plots =  ",plots

    if options.bb:
        plots = ['h_msd_v_pt_ak8_bbleading_topR6_pass', 'h_msd_v_pt_ak8_bbleading_topR6_fail']
    elif muonCR:
        plots = ['h_msd_ak8_muCR4_N2_pass', 'h_msd_ak8_muCR4_N2_fail',
                 'h_msd_ak8_muCR4_N2_pass_JESUp', 'h_msd_ak8_muCR4_N2_pass_JESDown',
                 'h_msd_ak8_muCR4_N2_fail_JESUp', 'h_msd_ak8_muCR4_N2_fail_JESDown',
                 'h_msd_ak8_muCR4_N2_pass_JERUp', 'h_msd_ak8_muCR4_N2_pass_JERDown',
                 'h_msd_ak8_muCR4_N2_fail_JERUp', 'h_msd_ak8_muCR4_N2_fail_JERDown',
                 'h_msd_ak8_muCR4_N2_pass_mutriggerUp', 'h_msd_ak8_muCR4_N2_pass_mutriggerDown',
                 'h_msd_ak8_muCR4_N2_fail_mutriggerUp', 'h_msd_ak8_muCR4_N2_fail_mutriggerDown',
                 'h_msd_ak8_muCR4_N2_pass_muidUp', 'h_msd_ak8_muCR4_N2_pass_muidDown',
                 'h_msd_ak8_muCR4_N2_fail_muidUp', 'h_msd_ak8_muCR4_N2_fail_muidDown',
                 'h_msd_ak8_muCR4_N2_pass_muisoUp', 'h_msd_ak8_muCR4_N2_pass_muisoDown',
                 'h_msd_ak8_muCR4_N2_fail_muisoUp', 'h_msd_ak8_muCR4_N2_fail_muisoDown',
                 'h_msd_ak8_muCR4_N2_pass_PuUp', 'h_msd_ak8_muCR4_N2_pass_PuDown',
                 'h_msd_ak8_muCR4_N2_fail_PuUp', 'h_msd_ak8_muCR4_N2_fail_PuDown',
                 ]

    print "Signals... "
    sigSamples = {}
    sigSamples['hqq125'] = sampleContainer('hqq125', tfiles['hqq125'], 1, dbtagmin, lumi, False, False, '1', True, iSplit = options.iSplit, maxSplit = options.maxSplit,doublebCut=dbtagcut,puOpt=puOpt)
    #sigSamples['hqq125'] = normSampleContainer('hqq125',tfiles['hqq125'], 1, dbtagmin,lumi,False,False,'1',False, iSplit = options.iSplit, maxSplit = options.maxSplit,treeName='Events',puOpt="default").addPlots(plots)
    sigSamples['tthqq125'] = sampleContainer('tthqq125', tfiles['tthqq125'], 1, dbtagmin, lumi, False, False, '1', True, iSplit = options.iSplit, maxSplit = options.maxSplit,doublebCut=dbtagcut,puOpt=puOpt)
    sigSamples['vbfhqq125'] = sampleContainer('vbfhqq125', tfiles['vbfhqq125'], 1, dbtagmin, lumi, False, False, '1',True, iSplit = options.iSplit, maxSplit = options.maxSplit,doublebCut=dbtagcut,puOpt=puOpt)
    sigSamples['whqq125'] = sampleContainer('whqq125', tfiles['whqq125'], 1, dbtagmin, lumi, False, False, '1', True, iSplit = options.iSplit, maxSplit = options.maxSplit,doublebCut=dbtagcut,puOpt=puOpt)
    sigSamples['zhqq125'] = sampleContainer('zhqq125', tfiles['zhqq125'], 1, dbtagmin, lumi, False, False, '1', True, iSplit = options.iSplit, maxSplit = options.maxSplit,doublebCut=dbtagcut,puOpt=puOpt)
    print "Backgrounds..."
    bkgSamples = {}

    if options.is2017:
        bkgSamples['wqq']  = normSampleContainer('wqq',tfiles['wqq'], 1, dbtagmin,lumi,False,False,'1',True, iSplit = options.iSplit, maxSplit = options.maxSplit,puOpt="default").addPlots(plots)
        bkgSamples['zqq']  = normSampleContainer('zqq',tfiles['zqq'], 1, dbtagmin,lumi,False,False,'1',True, iSplit = options.iSplit, maxSplit = options.maxSplit,puOpt="default").addPlots(plots)
        bkgSamples['wlnu'] = normSampleContainer('wlnu',tfiles['wlnu'], 1, dbtagmin,lumi,False,False,'1',True, iSplit = options.iSplit, maxSplit = options.maxSplit,puOpt="default").addPlots(plots)
    else:
        bkgSamples['wqq']  = sampleContainer('wqq',tfiles['wqq'], 1, dbtagmin,lumi,False,False,'1',True, iSplit = options.iSplit, maxSplit = options.maxSplit,puOpt="2016")
        bkgSamples['zqq']  = sampleContainer('zqq',tfiles['zqq'], 1, dbtagmin,lumi,False,False,'1',True, iSplit = options.iSplit, maxSplit = options.maxSplit,puOpt="2016")
        bkgSamples['wlnu'] = sampleContainer('wlnu', tfiles['wlnu'], 1, dbtagmin, lumi, False, False, '1', True, iSplit = options.iSplit, maxSplit = options.maxSplit,doublebCut=dbtagcut,puOpt="2016")
    if not options.skipQCD:
        bkgSamples['qcd'] = sampleContainer('qcd', tfiles['qcd'], 1, dbtagmin, lumi, False, False, '1', True, iSplit = options.iSplit, maxSplit = options.maxSplit,doublebCut=dbtagcut,puOpt=puOpt)
    bkgSamples['tqq'] = sampleContainer('tqq', tfiles['tqq'], 1, dbtagmin, lumi, False, False, '1', True, iSplit = options.iSplit, maxSplit = options.maxSplit,doublebCut=dbtagcut,puOpt=puOpt)
    bkgSamples['stqq'] = sampleContainer('stqq', tfiles['stqq'], 1, dbtagmin, lumi, False, False, '1', True, iSplit = options.iSplit, maxSplit = options.maxSplit,doublebCut=dbtagcut,puOpt=puOpt)
    bkgSamples['zll'] = sampleContainer('zll', tfiles['zll'], 1, dbtagmin, lumi, False, False, '1', True, iSplit = options.iSplit, maxSplit = options.maxSplit,doublebCut=dbtagcut,puOpt="2016")
    bkgSamples['vvqq'] = sampleContainer('vvqq', tfiles['vvqq'], 1, dbtagmin, lumi, False, False, '1', True, iSplit = options.iSplit, maxSplit = options.maxSplit,doublebCut=dbtagcut,puOpt=puOpt)
    print "Data..."
    if not options.skipData:
        if muonCR:
            dataSample = sampleContainer('data_obs', tfiles['data_obs'], sfData, dbtagmin, lumi, True, False,
                                     '((triggerBits&4)&&passJson)', True, iSplit = options.iSplit, maxSplit = options.maxSplit,doublebCut=dbtagcut,puOpt=puOpt)
        else:
            # 2017 triggerBits
            triggerNames={"version":"zprimebit-12.07-triggerBits","branchName":"triggerBits",
                          "names":[
                               "HLT_AK8PFJet330_PFAK8BTagCSV_p17_v*",
                               "HLT_PFHT1050_v*",
                               "HLT_AK8PFJet400_TrimMass30_v*",
                               "HLT_AK8PFHT800_TrimMass50_v*",
                               "HLT_PFJet500_v*",
                               "HLT_AK8PFJet360_TrimMass30_v*",
                               "HLT_AK8PFJet380_TrimMass30_v*",
                               "HLT_AK8PFJet500_v*"]
                      }
            if is2017:
                dataSample = sampleContainer('data_obs', tfiles['data_obs'], sfData, dbtagmin, lumi, True, False,
                                       'passJson', True, iSplit = options.iSplit, maxSplit = options.maxSplit,doublebCut=dbtagcut,triggerNames=triggerNames)
            else:
                dataSample = sampleContainer('data_obs', tfiles['data_obs'], sfData, dbtagmin, lumi, True, False,
                                       '((triggerBits&2)&&passJson)', True, iSplit = options.iSplit, maxSplit = options.maxSplit,doublebCut=dbtagcut,puOpt=puOpt)

    hall = {}

    #normSamples =['wqq','zqq','wlnu','hqq125']
    normSamples =['wqq','zqq','wlnu']
    for plot in plots:
        tag = plot.split('_')[-1]  # 'pass' or 'fail' or systematicName
        if tag not in ['pass', 'fail']:
            tag = plot.split('_')[-2] + '_' + plot.split('_')[-1]  # 'pass_systematicName', 'pass_systmaticName', etc.

        for process, s in sigSamples.iteritems():
            if options.is2017 and process in normSamples:
                hall['%s_%s' % (process, tag)] = sigSamples[process][plot]   #get plot from normSampleContainer
            else:
                hall['%s_%s' % (process, tag)] = getattr(s, plot)           #get plot from SampleContainer
            hall['%s_%s' % (process, tag)].SetName('%s_%s' % (process, tag))

        for process, s in bkgSamples.iteritems():
            if options.is2017 and process in normSamples:
                hall['%s_%s' % (process, tag)] = bkgSamples[process][plot]     #get plot from normSampleContainer
            else:
                hall['%s_%s' % (process, tag)] = getattr(s, plot)           #get plot from SampleContainer
            hall['%s_%s' % (process, tag)].SetName('%s_%s' % (process, tag))

        if not options.skipData:
            hall['%s_%s' % ('data_obs', tag)] = getattr(dataSample, plot)
            hall['%s_%s' % ('data_obs', tag)].SetName('%s_%s' % ('data_obs', tag))

    outfile.cd()

    for key, h in hall.iteritems():
        h.Write()

    outfile.Write()
    outfile.Close()


##----##----##----##----##----##----##
if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option('-b', action='store_true', dest='noX', default=False, help='no X11 windows')
    parser.add_option("--lumi", dest="lumi", default=41.3, type="float", help="luminosity", metavar="lumi")
    parser.add_option("--bb", action='store_true', dest="bb", default=False, help="sort by double b-tag")
    parser.add_option('-i', '--idir', dest='idir', default='data/', help='directory with data', metavar='idir')
    parser.add_option('-o', '--odir', dest='odir', default='./', help='directory to write histograms', metavar='odir')
    parser.add_option('-m', '--muonCR', action='store_true', dest='muonCR', default=False, help='for muon CR',
                      metavar='muonCR')
    parser.add_option('--dbtagmin', dest='dbtagmin', default=-99., type="float",
                      help='left bound to btag selection(fail region lower bound)', metavar='dbtagmin')
    parser.add_option('--dbtagcut', dest='dbtagcut', default=0.9, type="float",
                      help='btag selection for cut value(pass region lower bound)', metavar='dbtagcut')
    parser.add_option('--skip-qcd', action='store_true', dest='skipQCD', default=False, help='skip QCD', metavar='skipQCD')
    parser.add_option('--skip-data', action='store_true', dest='skipData', default=False, help='skip Data', metavar='skipData')
    parser.add_option("--max-split", dest="maxSplit", default=1, type="int", help="max number of jobs", metavar="maxSplit")
    parser.add_option("--i-split"  , dest="iSplit", default=0, type="int", help="job number", metavar="iSplit")
    parser.add_option("--is2017"  , dest="is2017", action='store_true', default=False, help="use 2017 files", metavar="is2017")
    parser.add_option("--sfData" , dest="sfData", default=1, type="int", help="process 1/sf of data", metavar="sfData")
    parser.add_option("--region" , dest="region", default='topR6_N2',choices=['topR6_N2','QGquark','QGgluon'], help="region for pass/fail doubleB tag", metavar="region")

    (options, args) = parser.parse_args()

    main(options, args)

    print "All done."
