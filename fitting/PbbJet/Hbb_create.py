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

def get2018files(isMuonCR):
    idir_temp = 'root://cmseos.fnal.gov//eos/uscms/store/user/lpchbb/zprimebits-v12.04/cvernier/'
    idir_1502 = 'root://cmseos.fnal.gov//eos/uscms/store/user/lpcbacon/dazsle/zprimebits-v15.02/'
    idir_1502skim = 'root://cmseos.fnal.gov//eos/uscms/store/user/lpcbacon/dazsle/zprimebits-v15.02/skim/'
    idir_1501skim = 'root://cmseos.fnal.gov//eos/uscms/store/user/lpcbacon/dazsle/zprimebits-v15.01/skim/'
    idir_1504     = 'root://cmseos.fnal.gov//eos/uscms/store/user/lpcbacon/dazsle/zprimebits-v15.04/'
    idir_1504skim = 'root://cmseos.fnal.gov//eos/uscms/store/user/lpcbacon/dazsle/zprimebits-v15.04/skim/'
    idir_1505     = 'root://cmseos.fnal.gov//eos/uscms/store/user/lpcbacon/dazsle/zprimebits-v15.05/'
    idir_1505skim = 'root://cmseos.fnal.gov//eos/uscms/store/user/lpcbacon/dazsle/zprimebits-v15.05/skim/'
    idir_1605     = 'root://cmseos.fnal.gov//eos/uscms/store/user/lpcbacon/dazsle/zprimebits-v16.05/'
    idir_1605skim = 'root://cmseos.fnal.gov//eos/uscms/store/user/lpcbacon/dazsle/zprimebits-v16.05/skim/'


    tfiles = {
	    'hqq125'     : { 'GluGluHToBB_M125_13TeV_powheg_pythia8':                      [idir_1505skim+'/GluGluHToBB_M125_13TeV_powheg_pythia8_*.root']},
	    'vbfhqq125'  : { 'VBFHToBB_M_125_13TeV_powheg_pythia8_weightfix':              [idir_1505skim+'/VBFHToBB_M_125_13TeV_powheg_pythia8_weightfix_*.root']},
        'zhqq125'    : { 
                           'ZH_HToBB_ZToQQ_M125_13TeV_powheg_pythia8':              [idir_1505skim+'/ZH_HToBB_ZToQQ_M125_13TeV_powheg_pythia8_*.root'],
                           'ggZH_HToBB_ZToQQ_M125_13TeV_powheg_pythia8':            [idir_1505skim+'/ggZH_HToBB_ZToQQ_M125_13TeV_powheg_pythia8_*.root'],
                           #'ZH_HToBB_ZToNuNu_M125_13TeV_powheg_pythia8':            [idir_1505+'/ZH_HToBB_ZToNuNu_M125_13TeV_powheg_pythia8/*.root'],
                           'ggZH_HToBB_ZToNuNu_M125_13TeV_powheg_pythia8':          [idir_1505skim+'/ggZH_HToBB_ZToNuNu_M125_13TeV_powheg_pythia8_*.root'],
                       },
        'whqq125'    : {
                           'WminusH_HToBB_WToQQ_M125_13TeV_powheg_pythia8':         [idir_1505skim+'/WminusH_HToBB_WToQQ_M125_13TeV_powheg_pythia8_*.root'],
                           'WplusH_HToBB_WToQQ_M125_13TeV_powheg_pythia8':          [idir_1505skim+'/WplusH_HToBB_WToQQ_M125_13TeV_powheg_pythia8_*.root'],
                       },
	    'tthqq125'   : { 'ttHTobb_M125_TuneCP5_13TeV_powheg_pythia8':           [idir_1505skim+'/ttHTobb_M125_TuneCP5_13TeV_powheg_pythia8_*.root']},
        'vvqq':        {
                             'WW_TuneCP5_13TeV-pythia8':[idir_1505skim+'WW_TuneCP5_13TeV_pythia8_*.root'],
                             'WZ_TuneCP5_13TeV-pythia8':[idir_1505skim+'WZ_TuneCP5_13TeV_pythia8_*.root'],
                             'ZZ_TuneCP5_13TeV-pythia8':[idir_1505skim+'ZZ_TuneCP5_13TeV_pythia8_*.root']
                       },
        'zqq':         {
                            'ZJetsToQQ_HT400to600_qc19_4j_TuneCP5_13TeV': [idir_1505skim + '/ZJetsToQQ_HT400to600_qc19_4j_TuneCP5_13TeV_*.root'],
                            'ZJetsToQQ_HT600to800_qc19_4j_TuneCP5_13TeV': [idir_1505skim + '/ZJetsToQQ_HT600to800_qc19_4j_TuneCP5_13TeV_*.root'],
                            'ZJetsToQQ_HT-800toInf_qc19_4j_TuneCP5_13TeV':[idir_1505skim + '/ZJetsToQQ_HT-800toInf_qc19_4j_TuneCP5_13TeV_*.root'],
                        },
        'zll':          {
                            'DYJetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8'  :[idir_1505skim+'/DYJetsToLL_M_50_TuneCP5_13TeV_*.root']
                        },
        'stqq':  {
                             'ST_s-channel_4f_hadronicDecays_TuneCP5_13TeV-madgraph-pythia8'                 :[idir_1505skim+'ST_s_channel_4f_hadronicDecays_TuneCP5_13TeV_madgraph_pythia8_*.root'],
                             'ST_t-channel_antitop_4f_inclusiveDecays_TuneCP5_13TeV-powhegV2-madspin-pythia8':[idir_1505skim+'ST_t_channel_antitop_4f_InclusiveDecays_TuneCP5_13TeV_powheg_madspin_pythia8_*.root'],
                             'ST_t-channel_top_4f_inclusiveDecays_TuneCP5_13TeV-powhegV2-madspin-pythia8'    :[idir_1505skim+'ST_t_channel_top_4f_InclusiveDecays_TuneCP5_13TeV_powheg_madspin_pythia8_*.root'],
                             'ST_tW_antitop_5f_inclusiveDecays_TuneCP5_13TeV-powheg-pythia8'                 :[idir_1505skim+'ST_tW_antitop_5f_inclusiveDecays_TuneCP5_13TeV_powheg_pythia8_*.root'],
                             'ST_tW_top_5f_inclusiveDecays_TuneCP5_13TeV-powheg-pythia8'                     :[idir_1505skim+'ST_tW_top_5f_inclusiveDecays_TuneCP5_13TeV_powheg_pythia8_*.root']
                            },
        'wqq'         : {
                              'WJetsToQQ_HT400to600_qc19_3j_TuneCP5_13TeV': [idir_1505skim + 'WJetsToQQ_HT400to600_qc19_3j_TuneCP5_13TeV_*.root'],
                              'WJetsToQQ_HT600to800_qc19_3j_TuneCP5_13TeV': [idir_1505skim + 'WJetsToQQ_HT600to800_qc19_3j_TuneCP5_13TeV_*.root'],
                              'WJetsToQQ_HT-800toInf_qc19_3j_TuneCP5_13TeV':[idir_1505skim + 'WJetsToQQ_HT-800toInf_qc19_3j_TuneCP5_13TeV_*.root'],
                             },
        'wlnu':         {
                              # "WJetsToLNu_TuneCP5_13TeV-madgraphMLM-pythia8"               :[ idir_1401skim+'WJetsToLNu_TuneCP5_13TeV*.root'],
                               "WJetsToLNu_HT-200To400_TuneCP5_13TeV-madgraphMLM-pythia8"   :[ idir_1504skim+'WJetsToLNu_HT_200To400_TuneCP5_13TeV_*.root'],
                               "WJetsToLNu_HT-400To600_TuneCP5_13TeV-madgraphMLM-pythia8"   :[ idir_1504skim+'WJetsToLNu_HT_400To600_TuneCP5_13TeV_*.root'],
                               "WJetsToLNu_HT-600To800_TuneCP5_13TeV-madgraphMLM-pythia8"   :[ idir_1504skim+'WJetsToLNu_HT_600To800_TuneCP5_13TeV_*.root'],
                               "WJetsToLNu_HT-800To1200_TuneCP5_13TeV-madgraphMLM-pythia8"  :[ idir_1504skim+'WJetsToLNu_HT_800To1200_TuneCP5_13TeV_*.root'],
                               "WJetsToLNu_HT-1200To2500_TuneCP5_13TeV-madgraphMLM-pythia8" :[ idir_1504skim+'WJetsToLNu_HT_1200To2500_TuneCP5_13TeV_*.root'],
                               "WJetsToLNu_HT-2500ToInf_TuneCP5_13TeV-madgraphMLM-pythia8"  :[ idir_1504skim+'WJetsToLNu_HT_2500ToInf_TuneCP5_13TeV_*.root'],
                            },
        'tqq':      {
                       'TTToHadronic_TuneCP5_13TeV_powheg_pythia8'    :[idir_1505skim+'TTToHadronic_TuneCP5_13TeV-powheg-pythia8_*.root'],
                       'TTToSemiLeptonic_TuneCP5_13TeV_powheg_pythia8':[idir_1505skim+'TTToSemiLeptonic_TuneCP5_13TeV_powheg_pythia8_*.root'],
                       'TTTo2L2Nu_TuneCP5_13TeV_powheg_pythia8'       :[idir_1505skim+'TTTo2L2Nu_TuneCP5_13TeV-powheg-pythia8_*.root'       ],
                      },
        'qcd':        {
                       'QCD_HT500to700_TuneCP5_13TeV-madgraphMLM-pythia8'  :[idir_1505skim+'/QCD_HT500to700_TuneCP5_13TeV-madgraphMLM-pythia8_*.root'  ],
                       'QCD_HT700to1000_TuneCP5_13TeV-madgraphMLM-pythia8' :[idir_1505skim+'/QCD_HT700to1000_TuneCP5_13TeV-madgraphMLM-pythia8_*.root' ],
                       'QCD_HT1000to1500_TuneCP5_13TeV-madgraphMLM-pythia8':[idir_1505skim+'/QCD_HT1000to1500_TuneCP5_13TeV-madgraphMLM-pythia8_*.root'],
                       'QCD_HT1500to2000_TuneCP5_13TeV-madgraphMLM-pythia8':[idir_1505skim+'/QCD_HT1500to2000_TuneCP5_13TeV-madgraphMLM-pythia8_*.root'],
                       'QCD_HT2000toInf_TuneCP5_13TeV-madgraphMLM-pythia8' :[idir_1505skim+'/QCD_HT2000toInf_TuneCP5_13TeV-madgraphMLM-pythia8_*.root' ]
                      },
        'data_obs_jet': [
                            #idir_1505 + 'JetHTRun2018A_17Sep2018_v1/*.root',
                            #idir_1505 + 'JetHTRun2018B_17Sep2018_v1/*.root',
                            #idir_1505 + 'JetHTRun2018C_PromptReco_v*/*.root',
                            #idir_1505 + 'JetHTRun2018D_PromptReco_v*/*.root',
                            idir_1505skim + 'JetHTRun2018A_17Sep2018_v1*.root',
                            idir_1505skim + 'JetHTRun2018B_17Sep2018_v1*.root',
                            idir_1505skim + 'JetHTRun2018C_PromptReco_v*.root',
                            #idir_1505skim + 'JetHTRun2018D_PromptReco_v*.root',  ## ~1/5 'polluted' with wrong training
                            idir_1605skim + 'JetHTRun2018D_PromptReco_v*.root',  
                      ],
        'data_obs_mu': [
                       #idir_1505+'/SingleMuonRun2018A_17Sep2018_v2/*.root',
                       #idir_1505+'/SingleMuonRun2018B_17Sep2018_v1/*.root',
                       #idir_1505+'/SingleMuonRun2018C_17Sep2018_v1/*.root',
                       #idir_1505+'/SingleMuonRun2018D_PromptReco_v2*/*.root',
                       idir_1605skim+'/SingleMuonRun2018A_17Sep2018_v2*.root',
                       idir_1505skim+'/SingleMuonRun2018B_17Sep2018_v1*.root',
                       idir_1505skim+'/SingleMuonRun2018C_17Sep2018_v1*.root',
                       idir_1505skim+'/SingleMuonRun2018D_PromptReco_v2*.root',
                    ]
    }
    return tfiles

def get2016legacyfiles():
    idir_temp = 'root://cmseos.fnal.gov//eos/uscms/store/user/lpchbb/zprimebits-v12.04/cvernier/'
    idir_1504     = 'root://cmseos.fnal.gov//eos/uscms/store/user/lpcbacon/dazsle/zprimebits-v15.04/'
    idir_1504skim = 'root://cmseos.fnal.gov//eos/uscms/store/user/lpcbacon/dazsle/zprimebits-v15.04/skim/'
    idir_1503     = 'root://cmseos.fnal.gov//eos/uscms/store/user/lpcbacon/dazsle/zprimebits-v15.03/'
    idir_1503skim = 'root://cmseos.fnal.gov//eos/uscms/store/user/lpcbacon/dazsle/zprimebits-v15.03/skim/'
    idir_1603     = 'root://cmseos.fnal.gov//eos/uscms/store/user/lpcbacon/dazsle/zprimebits-v16.03/'
    idir_1603skim = 'root://cmseos.fnal.gov//eos/uscms/store/user/lpcbacon/dazsle/zprimebits-v16.03/skim/'
    idir_16031skim = 'root://cmseos.fnal.gov//eos/uscms/store/user/lpcbacon/dazsle/zprimebits-v16.031/skim/'
    tfiles = {
	          'hqq125'     :          { 'GluGluHToBB_M125_13TeV_powheg_pythia8':                      [idir_1603skim+'/GluGluHToBB_M125_13TeV_powheg_pythia8_*.root']},
	          'vbfhqq125'    :          { 'VBFHToBB_M_125_13TeV_powheg_pythia8_weightfix':            [idir_1603skim+'/VBFHToBB_M_125_13TeV_powheg_pythia8_weightfix_*.root']},
	          'zhqq125'      :          { 
                                    'ZH_HToBB_ZToQQ_M125_13TeV_powheg_pythia8':              [idir_1603skim+'/ZH_HToBB_ZToQQ_M125_13TeV_powheg_pythia8_*.root'],
                                    'ggZH_HToBB_ZToQQ_M125_13TeV_powheg_pythia8':            [idir_1603skim+'/ggZH_HToBB_ZToQQ_M125_13TeV_powheg_pythia8_*.root'],
                                    'ggZH_HToBB_ZToNuNu_M125_13TeV_powheg_pythia8':          [idir_1603skim+'/ggZH_HToBB_ZToNuNu_M125_13TeV_powheg_pythia8_*.root'],
                                    },
               'whqq125':          {
                                    'WminusH_HToBB_WToQQ_M125_13TeV_powheg_pythia8':         [idir_1603skim+'/WminusH_HToBB_WToQQ_M125_13TeV_powheg_pythia8_*.root'],
                                    'WplusH_HToBB_WToQQ_M125_13TeV_powheg_pythia8':          [idir_1603skim+'/WplusH_HToBB_WToQQ_M125_13TeV_powheg_pythia8_*.root']
                                    },
	          'tthqq125'    :        { 'ttHTobb_M125_TuneCP5_13TeV_powheg_pythia8':           [idir_1503skim+'/ttHTobb_M125_13TeV_powheg_pythia8*.root']},
              'vvqq':    {
                             'WW_TuneCUETP8M1_13TeV-pythia8':[idir_1603skim+'WW_13TeV_pythia8*.root'],
                             'WZ_TuneCUETP8M1_13TeV-pythia8':[idir_1603skim+'WZ_13TeV_pythia8*.root'],
                             'ZZ_TuneCUETP8M1_13TeV-pythia8':[idir_1603skim+'ZZ_13TeV_pythia8*.root'] 

                            },
              'zqq':         {
                            #'DYJetsToQQ_HT180_13TeV-madgraphMLM-pythia8' : [idir_1503skim + '/DYJetsToQQ_HT180_13TeV_*.root'],
                            'DYJetsToQQ_HT180_13TeV-madgraphMLM-pythia8' : [idir_1603skim + '/DYJetsToQQ_HT180_13TeV_*.root'],
                            },
              'zll':       {
                             'DYJetsToLL_Pt_250To400_13TeV_amcatnloFXFX_pythia8'  :[idir_1503skim+'/DYJetsToLL_Pt_250To400_13TeV_amcatnloFXFX_pythia8*.root'] , 
                             'DYJetsToLL_Pt_400To650_13TeV_amcatnloFXFX_pythia8'  :[idir_1503skim+'/DYJetsToLL_Pt_400To650_13TeV_amcatnloFXFX_pythia8*.root'] , 
                             'DYJetsToLL_Pt_650ToInf_13TeV_amcatnloFXFX_pythia8'  :[idir_1503skim+'/DYJetsToLL_Pt_650ToInf_13TeV_amcatnloFXFX_pythia8*.root'] , 
                            },
              'stqq':  {
                             'ST_s-channel_4f_leptonDecays_13TeV-amcatnlo-pythia8_TuneCUETP8M1'              :[idir_1603skim+'ST_s_channel_4f_leptonDecays_13TeV_amcatnlo_pythia8_TuneCUETP8M1_*.root'              ],            
                             'ST_t-channel_antitop_4f_inclusiveDecays_13TeV-powhegV2-madspin-pythia8_TuneCUETP8M1' :[idir_1603skim+'ST_t_channel_antitop_4f_inclusiveDecays_TuneCUETP8M2T4_13TeV_powhegV2_madspin_*.root' ],
                             'ST_t-channel_top_4f_inclusiveDecays_13TeV-powhegV2-madspin-pythia8_TuneCUETP8M1'     :[idir_1603skim+'ST_t_channel_top_4f_inclusiveDecays_TuneCUETP8M2T4_13TeV_powhegV2_madspin_*.root'     ],    
                             'ST_tW_antitop_5f_inclusiveDecays_13TeV-powheg-pythia8_TuneCUETP8M1'          :[idir_1603skim+'ST_tW_antitop_5f_inclusiveDecays_13TeV_powheg_pythia8_TuneCUETP8M2T4*.root'          ],         
                             'ST_tW_top_5f_inclusiveDecays_13TeV-powheg-pythia8_TuneCUETP8M1'              :[idir_1603skim+'ST_tW_top_5f_inclusiveDecays_13TeV_powheg_pythia8_TuneCUETP8M2T4_*.root'              ],             

                            },
              'wqq'         : {
                              #'WJetsToQQ_HT180_13TeV-madgraphMLM-pythia8': [idir_1503skim + 'WJetsToQQ_HT180_13TeV_*.root'],
                              'WJetsToQQ_HT180_13TeV-madgraphMLM-pythia8': [idir_1603skim + 'WJetsToQQ_HT180_13TeV_*.root'],
                            },
              'wlnu':       {
                             "WJetsToLNu_HT-100To200_TuneCUETP8M1_13TeV-madgraphMLM-pythia8"     :[ idir_1503skim+'WJetsToLNu_HT_100To200_*.root'],
                             "WJetsToLNu_HT-200To400_TuneCUETP8M1_13TeV-madgraphMLM-pythia8"     :[ idir_1503skim+'WJetsToLNu_HT_200To400_*.root'],
                             "WJetsToLNu_HT-400To600_TuneCUETP8M1_13TeV-madgraphMLM-pythia8"     :[ idir_1503skim+'WJetsToLNu_HT_400To600_*.root'],
                             "WJetsToLNu_HT-600To800_TuneCUETP8M1_13TeV-madgraphMLM-pythia8"     :[ idir_1503skim+'WJetsToLNu_HT_600To800_*.root'],
                             "WJetsToLNu_HT-800To1200_TuneCUETP8M1_13TeV-madgraphMLM-pythia8"    :[ idir_1503skim+'WJetsToLNu_HT_800To1200_*.root'],
                             "WJetsToLNu_HT-1200To2500_TuneCUETP8M1_13TeV-madgraphMLM-pythia8"   :[ idir_1503skim+'WJetsToLNu_HT_1200To2500_*.root'],
                             "WJetsToLNu_HT-2500ToInf_TuneCUETP8M1_13TeV-madgraphMLM-pythia8"    :[ idir_1503skim+'WJetsToLNu_HT_2500ToInf_*.root'],
                            },
              'tqq':      {
                             'TT_TuneCUETP8M2T4_13TeV_powheg_pythia8'    :[idir_1603skim+'TT_TuneCUETP8M2T4_13TeV_powheg_pythia8_*.root'],
                            },
              'qcd':        {
                             #'QCD_HT300to500_TuneCUETP8M1_13TeV-madgraphMLM-pythia8'  :[idir_1503skim+'/QCD_HT300to500_*.root'  ],
                             'QCD_HT500to700_TuneCUETP8M1_13TeV-madgraphMLM-pythia8'  :[idir_16031skim+'/QCD_HT500to700_*.root'  ],
                             'QCD_HT700to1000_TuneCUETP8M1_13TeV-madgraphMLM-pythia8' :[idir_16031skim+'/QCD_HT700to1000_*.root' ],
                             'QCD_HT1000to1500_TuneCUETP8M1_13TeV-madgraphMLM-pythia8':[idir_16031skim+'/QCD_HT1000to1500_*.root'],
                             'QCD_HT1500to2000_TuneCUETP8M1_13TeV-madgraphMLM-pythia8':[idir_16031skim+'/QCD_HT1500to2000_*.root'],
                             'QCD_HT2000toInf_TuneCUETP8M1_13TeV-madgraphMLM-pythia8' :[idir_16031skim+'/QCD_HT2000toInf_*.root' ]
                            },
              'data_obs_jet': [
                            #idir_1503skim + 'JetHTRun2016B_07Aug17_v*_ddb8X*.root',
                            #idir_1503skim + 'JetHTRun2016C_07Aug17_v*_ddb8X*.root',
                            #idir_1503skim + 'JetHTRun2016D_07Aug17_v*_ddb8X*.root',
                            #idir_1503skim + 'JetHTRun2016E_07Aug17_v*_ddb8X*.root',
                            #idir_1503skim + 'JetHTRun2016F_07Aug17_v*_ddb8X*.root',
                            #idir_1503skim + 'JetHTRun2016G_07Aug17_v*_ddb8X*.root',
                            idir_1503skim  + 'JetHTRun2016B_07Aug17_v*_withPF*.root',
                            idir_1503skim  + 'JetHTRun2016C_07Aug17_v1_withPF*.root',    
                            idir_1503skim  + 'JetHTRun2016D_07Aug17_v1_withPF*.root',    
                            idir_1503skim  + 'JetHTRun2016E_07Aug17_v1_withPF*.root',   
                            idir_1503skim  + 'JetHTRun2016F_07Aug17_v1_withPF*.root',  
                            idir_1503skim  + 'JetHTRun2016G_07Aug17_v1_withPF*.root',
                            idir_1503skim  + 'JetHTRun2016H_07Aug17_v1_withPF*.root',
                      ],
           'data_obs_mu' :[
                       idir_1603skim+'/SingleMuonRun2016B_07Aug17_v*.root',
                       idir_1603skim+'/SingleMuonRun2016C_07Aug17_v*.root',
                       idir_1603skim+'/SingleMuonRun2016D_07Aug17_v*.root',
                       idir_1603skim+'/SingleMuonRun2016E_07Aug17_v*.root',
                       idir_1603skim+'/SingleMuonRun2016F_07Aug17_v*.root',
                       idir_1603skim+'/SingleMuonRun2016G_07Aug17_v*.root',
                       idir_1603skim+'/SingleMuonRun2016H_07Aug17_v*.root',
                    ]
    }
    return tfiles


def get2017files(isMuonCR):
    idir = 'root://cmseos.fnal.gov//eos/uscms/store/user/lpchbb/zprimebits-v12.04/cvernier'
    idir_temp = 'root://cmseos.fnal.gov//eos/uscms/store/user/lpchbb/zprimebits-v12.04/cvernier/'
    idir_1207 = 'root://cmseos.fnal.gov//eos/uscms/store/user/lpcbacon/dazsle/zprimebits-v12.07-puWeight/norm'
    idir_1208 = 'root://cmseos.fnal.gov//eos/uscms/store/user/lpcbacon/dazsle/zprimebits-v12.08/norm'
    idirData = 'root://cmseos.fnal.gov//eos/uscms/store/user/lpcbacon/dazsle/zprimebits-v12.07/sklim'
    idir_1401 = 'root://cmseos.fnal.gov//eos/uscms/store/user/lpcbacon/dazsle/zprimebits-v14.01/'
    idir_1401skim = 'root://cmseos.fnal.gov//eos/uscms/store/user/lpcbacon/dazsle/zprimebits-v14.01/skim/'
    idir_1501 = 'root://cmseos.fnal.gov//eos/uscms/store/user/lpcbacon/dazsle/zprimebits-v15.01/'
    idir_1501skim = 'root://cmseos.fnal.gov//eos/uscms/store/user/lpcbacon/dazsle/zprimebits-v15.01/skim/'
    idir_1504 = 'root://cmseos.fnal.gov//eos/uscms/store/user/lpcbacon/dazsle/zprimebits-v15.04/'
    idir_1504skim_vbf = 'root://cmseos.fnal.gov//eos/uscms/store/user/lpcbacon/dazsle/zprimebits-v15.04-vbf/skim/'
    idir_1504skim = 'root://cmseos.fnal.gov//eos/uscms/store/user/lpcbacon/dazsle/zprimebits-v15.04/skim/'
    idir_1604skim = 'root://cmseos.fnal.gov//eos/uscms/store/user/lpcbacon/dazsle/zprimebits-v16.04/skim/'

    tfiles = {
	    'hqq125'     : { 'GluGluHToBB_M125_13TeV_powheg_pythia8':                      [idir_1504skim_vbf+'/GluGluHToBB_M125_13TeV_powheg_pythia8_*.root']},
	    'vbfhqq125'  : { 'VBFHToBB_M_125_13TeV_powheg_pythia8_weightfix':              [idir_1504skim_vbf+'/VBFHToBB_M_125_13TeV_powheg_pythia8_weightfix_*.root']},
        'zhqq125'    : { 
                           'ZH_HToBB_ZToQQ_M125_13TeV_powheg_pythia8':              [idir_1504skim_vbf+'/ZH_HToBB_ZToQQ_M125_13TeV_powheg_pythia8_*.root'],
                           'ggZH_HToBB_ZToQQ_M125_13TeV_powheg_pythia8':            [idir_1504skim_vbf+'/ggZH_HToBB_ZToQQ_M125_13TeV_powheg_pythia8_*.root'],
                           #'ZH_HToBB_ZToNuNu_M125_13TeV_powheg_pythia8':            [idir_1504skim_vbf+'/ZH_HToBB_ZToNuNu_M125_13TeV_powheg_pythia8_*.root'],
                           'ggZH_HToBB_ZToNuNu_M125_13TeV_powheg_pythia8':          [idir_1504skim_vbf+'/ggZH_HToBB_ZToNuNu_M125_13TeV_powheg_pythia8*.root'],
                       },
        'whqq125'    : {
                           'WminusH_HToBB_WToQQ_M125_13TeV_powheg_pythia8':         [idir_1504skim_vbf+'/WminusH_HToBB_WToQQ_M125_13TeV_powheg_pythia8_*.root'],
                           'WplusH_HToBB_WToQQ_M125_13TeV_powheg_pythia8':          [idir_1504skim_vbf+'/WplusH_HToBB_WToQQ_M125_13TeV_powheg_pythia8_*.root'],
                       },
	    'tthqq125'   : { 'ttHTobb_M125_TuneCP5_13TeV_powheg_pythia8':           [idir_1504skim_vbf+'/ttHTobb_M125_TuneCP5_13TeV_powheg_pythia8_*.root']},
        'vvqq':        {
                             'WW_TuneCP5_13TeV-pythia8':[idir_1504skim_vbf+'WW_TuneCP5_13TeV_pythia8_*.root'],
                             'WZ_TuneCP5_13TeV-pythia8':[idir_1504skim_vbf+'WZ_TuneCP5_13TeV_pythia8_*.root'],
                             'ZZ_TuneCP5_13TeV-pythia8':[idir_1504skim_vbf+'ZZ_TuneCP5_13TeV_pythia8_*.root']
                       },
        'zqq':         {
                            'ZJetsToQQ_HT400to600_qc19_4j_TuneCP5_13TeV': [idir_1504skim_vbf + '/ZJetsToQQ_HT400to600_qc19_4j_TuneCP5_13TeV_*.root'],
                            'ZJetsToQQ_HT600to800_qc19_4j_TuneCP5_13TeV': [idir_1504skim_vbf + '/ZJetsToQQ_HT600to800_qc19_4j_TuneCP5_13TeV_*.root'],
                            'ZJetsToQQ_HT-800toInf_qc19_4j_TuneCP5_13TeV':[idir_1504skim_vbf + '/ZJetsToQQ_HT-800toInf_qc19_4j_TuneCP5_13TeV_*.root'],
                        },
        'zll':         {
                             'DYJetsToLL_M_50_HT_400to600_TuneCP5_13TeV'  :[idir_1504skim_vbf+'/DYJetsToLL_M_50_HT_400to600_TuneCP5_13TeV_*.root'] , 
                             'DYJetsToLL_M_50_HT_600to800_TuneCP5_13TeV'  :[idir_1504skim_vbf+'/DYJetsToLL_M_50_HT_600to800_TuneCP5_13TeV_*.root'] , 
                             'DYJetsToLL_M_50_HT_800to1200_TuneCP5_13TeV' :[idir_1504skim_vbf+'/DYJetsToLL_M_50_HT_800to1200_TuneCP5_13TeV_*.root'],                                     
                             'DYJetsToLL_M_50_HT_1200to2500_TuneCP5_13TeV':[idir_1504skim_vbf+'/DYJetsToLL_M_50_HT_1200to2500_TuneCP5_13TeV_*.root'], 
                             'DYJetsToLL_M_50_HT_2500toInf_TuneCP5_13TeV' :[idir_1504skim_vbf+'/DYJetsToLL_M_50_HT_2500toInf_TuneCP5_13TeV_*.root' ] 
                       },
        # ZJetsToQQ_HT600toInf_13TeV_madgraph_1000pb_weighted.root'],#DYJetsToQQ_HT180_13TeV_1000pb_weighted.root '],
        'stqq':  {
                             'ST_t-channel_antitop_4f_inclusiveDecays_TuneCP5_13TeV-powhegV2-madspin-pythia8':[idir_1504skim_vbf+'ST_t_channel_antitop_4f_inclusiveDecays_TuneCP5_13TeV_powhegV2_madspin_pythia8_*.root'],
                             'ST_t-channel_top_4f_inclusiveDecays_TuneCP5_13TeV-powhegV2-madspin-pythia8'    :[idir_1504skim_vbf+'ST_t_channel_top_4f_inclusiveDecays_TuneCP5_13TeV_powhegV2_madspin_pythia8_*.root'],
                             'ST_tW_antitop_5f_inclusiveDecays_TuneCP5_13TeV-powheg-pythia8'                 :[idir_1504skim_vbf+'ST_tW_antitop_5f_inclusiveDecays_TuneCP5_13TeV_powheg_pythia8_*.root'],
                             'ST_tW_top_5f_inclusiveDecays_TuneCP5_13TeV-powheg-pythia8'                     :[idir_1504skim_vbf+'ST_tW_top_5f_inclusiveDecays_TuneCP5_13TeV_powheg_pythia8_*.root']
                            },
        'wqq'         : {
                              'WJetsToQQ_HT400to600_qc19_3j_TuneCP5_13TeV': [idir_1504skim_vbf + 'WJetsToQQ_HT400to600_qc19_3j_TuneCP5_13TeV_*.root'],
                              'WJetsToQQ_HT600to800_qc19_3j_TuneCP5_13TeV': [idir_1504skim_vbf + 'WJetsToQQ_HT600to800_qc19_3j_TuneCP5_13TeV_*.root'],
                              'WJetsToQQ_HT-800toInf_qc19_3j_TuneCP5_13TeV':[idir_1504skim_vbf + 'WJetsToQQ_HT-800toInf_qc19_3j_TuneCP5_13TeV_*.root'],
                             },
        'wlnu':         {
                              # "WJetsToLNu_TuneCP5_13TeV-madgraphMLM-pythia8"               :[ idir_1401skim+'WJetsToLNu_TuneCP5_13TeV*.root'],
                               "WJetsToLNu_HT-200To400_TuneCP5_13TeV-madgraphMLM-pythia8"   :[ idir_1504skim_vbf+'WJetsToLNu_HT_200To400_TuneCP5_13TeV_*.root'],
                               "WJetsToLNu_HT-400To600_TuneCP5_13TeV-madgraphMLM-pythia8"   :[ idir_1504skim_vbf+'WJetsToLNu_HT_400To600_TuneCP5_13TeV_*.root'],
                               "WJetsToLNu_HT-600To800_TuneCP5_13TeV-madgraphMLM-pythia8"   :[ idir_1504skim_vbf+'WJetsToLNu_HT_600To800_TuneCP5_13TeV_*.root'],
                               "WJetsToLNu_HT-800To1200_TuneCP5_13TeV-madgraphMLM-pythia8"  :[ idir_1504skim_vbf+'WJetsToLNu_HT_800To1200_TuneCP5_13TeV_*.root'],
                               "WJetsToLNu_HT-1200To2500_TuneCP5_13TeV-madgraphMLM-pythia8" :[ idir_1504skim_vbf+'WJetsToLNu_HT_1200To2500_TuneCP5_13TeV_*.root'],
                               "WJetsToLNu_HT-2500ToInf_TuneCP5_13TeV-madgraphMLM-pythia8"  :[ idir_1504skim_vbf+'WJetsToLNu_HT_2500ToInf_TuneCP5_13TeV_*.root'],
                            },
        'tqq':      {
                       'TTToHadronic_TuneCP5_13TeV_powheg_pythia8'    :[idir_1504skim_vbf+'TTToHadronic_TuneCP5_13TeV_powheg_pythia8_*.root'],
                       'TTToSemiLeptonic_TuneCP5_13TeV_powheg_pythia8':[idir_1504skim_vbf+'TTToSemiLeptonic_TuneCP5_13TeV_powheg_pythia8_*.root'],
                       'TTTo2L2Nu_TuneCP5_13TeV_powheg_pythia8'       :[idir_1504skim_vbf+'TTTo2L2Nu_TuneCP5_13TeV_powheg_pythia8_*.root'       ],
                      },
        'qcd':        {
                       'QCD_HT500to700_TuneCP5_13TeV-madgraphMLM-pythia8'  :[idir_1504skim_vbf+'/QCD_HT500to700_TuneCP5_13TeV-madgraphMLM-pythia8_*.root'  ],
                       'QCD_HT700to1000_TuneCP5_13TeV-madgraphMLM-pythia8' :[idir_1504skim_vbf+'/QCD_HT700to1000_TuneCP5_13TeV-madgraphMLM-pythia8_*.root' ],
                       'QCD_HT1000to1500_TuneCP5_13TeV-madgraphMLM-pythia8':[idir_1504skim_vbf+'/QCD_HT1000to1500_TuneCP5_13TeV-madgraphMLM-pythia8_*.root'],
                       'QCD_HT1500to2000_TuneCP5_13TeV-madgraphMLM-pythia8':[idir_1504skim_vbf+'/QCD_HT1500to2000_TuneCP5_13TeV-madgraphMLM-pythia8_*.root'],
                       'QCD_HT2000toInf_TuneCP5_13TeV-madgraphMLM-pythia8' :[idir_1504skim_vbf+'/QCD_HT2000toInf_TuneCP5_13TeV-madgraphMLM-pythia8_*.root' ]
                      },
        'data_obs_jet': [
        	        	     idir_1604skim + 'JetHTRun2017B_17Nov2017_v1_*.root',
                             idir_1604skim + 'JetHTRun2017C_17Nov2017_v1_*.root',
                             idir_1604skim + 'JetHTRun2017D_17Nov2017_v1_*.root',
                             idir_1604skim + 'JetHTRun2017E_17Nov2017_v1_*.root',
                             idir_1604skim + 'JetHTRun2017F_17Nov2017_v1_*.root',
                             #idir_1504skim_vbf + 'JetHTRun2017F_17Nov2017_v1_*.root',
                             #idir_1501 + 'JetHTRun2017F_17Nov2017_v1/*.rootnodupl.root'
                      ],
        'data_obs_mu' :[
                       idir_1604skim+'/SingleMuonRun2017B_17Nov2017_v1_*.root',
                       idir_1604skim+'/SingleMuonRun2017C_17Nov2017_v1_*.root',
                       idir_1604skim+'/SingleMuonRun2017D_17Nov2017_v1_*.root',
                       idir_1604skim+'/SingleMuonRun2017E_17Nov2017_v1_*.root',
                       idir_1604skim+'/SingleMuonRun2017F_17Nov2017_v1_*.root'
                    ]
    }
    return tfiles


    

##----##----##----##----##----##----##
def main(options, args):
#    idir = options.idir
    odir = options.odir
    lumi = options.lumi
    muonCR = options.muonCR
    dbtagmin = options.dbtagmin
    dbtagcut = options.dbtagcut
    year   = options.year
    sfData   = options.sfData
    i_split  = options.iSplit
    max_split  = options.maxSplit
    doublebName = options.doublebName

    fileName = 'hist_1DZbb_pt_scalesmear_%s.root'%options.iSplit
    if options.skipQCD:
    	fileName = 'hist_1DZbb_pt_scalesmear_looserWZ_%s.root'%options.iSplit
    if options.bb:
        fileName = 'hist_1DZbb_sortByBB_%s.root'%options.iSplit
    elif muonCR:
        fileName = 'hist_1DZbb_muonCR_%s.root'%options.iSplit

    outfile = ROOT.TFile(options.odir + "/" + fileName, "recreate")
    
    if year=='2017':
        #tfiles = get2017files(muonCR)
        samplefiles   = open(os.path.expandvars("$ZPRIMEPLUSJET_BASE/analysis/ggH/samplefiles.json"),"r")
        tfiles  = json.load(samplefiles)['Hbb_create_2017']
        normfile      = os.path.expandvars("$ZPRIMEPLUSJET_BASE/analysis/ggH/norm_Hbb_create_2017.root")
        if muonCR:
            tfiles['data_obs']  = tfiles['data_obs_mu'] 
        else:
            tfiles['data_obs']  = tfiles['data_obs_jet'] 

        pu_Opt  = {'data':"2017",'norm':normfile}
    elif year=='2018':
        samplefiles   = open(os.path.expandvars("$ZPRIMEPLUSJET_BASE/analysis/ggH/samplefiles.json"),"r")
        tfiles  = json.load(samplefiles)['Hbb_create_2018']
        normfile      = os.path.expandvars("$ZPRIMEPLUSJET_BASE/analysis/ggH/norm_Hbb_create_2018.root")
        if muonCR:
            tfiles['data_obs']  = tfiles['data_obs_mu'] 
        else:
            tfiles['data_obs']  = tfiles['data_obs_jet'] 
        pu_Opt  = {'data':"2018",'norm':normfile}
    elif year=='2016legacy':
        samplefiles   = open(os.path.expandvars("$ZPRIMEPLUSJET_BASE/analysis/ggH/samplefiles.json"),"r")
        tfiles  = json.load(samplefiles)['Hbb_create_2016legacy']
        normfile      = os.path.expandvars("$ZPRIMEPLUSJET_BASE/analysis/ggH/norm_Hbb_create_2016legacy.root")
        if muonCR:
            tfiles['data_obs']  = tfiles['data_obs_mu'] 
        else:
            tfiles['data_obs']  = tfiles['data_obs_jet'] 
        pu_Opt  = {'data':"2016legacy",'norm':normfile}
    elif year=='2016':
        tfiles = get2016files(muonCR)
        pu_Opt  = {'data':"2016",'MC':"12.04"}


    passfail    = ['pass','fail']
    systematics = ['JESUp','JESDown','JERUp','JERDown','triggerUp','triggerDown','PuUp','PuDown','matched','unmatched']
    plots = []
    region  = options.region
    print "Selecting doubleB pass/fail plots for this region   =  %s"% region
    for pf in passfail:
        #hname  ="h_msd_v_pt_ak8_%s_%s"%(region,pf)
        hname ="h_msd_v_recoPt_v_genPt_ak8_%s_%s"%(region,pf)
        plots.append(hname)
        for sys in systematics:
            hname_sys ="h_msd_v_recoPt_v_genPt_ak8_%s_%s_%s"%(region,pf,sys)
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
        systematics = ['JESUp','JESDown','JERUp','JERDown','mutriggerUp','mutriggerDown','muidUp','muidDown','muisoUp','muisoDown','PuUp','PuDown']
        region = 'muCR4_N2'
        plots = []
        for pf in passfail:
                hname ="h_msd_v_recoPt_v_genPt_ak8_%s_%s"%(region,pf)
                plots.append(hname)
                for sys in systematics:
                    hname_sys ="h_msd_v_recoPt_v_genPt_ak8_%s_%s_%s"%(region,pf,sys)
                    plots.append(hname_sys)    
        #plots = ['h_msd_ak8_muCR4_N2_pass', 'h_msd_ak8_muCR4_N2_fail',
        #         'h_msd_ak8_muCR4_N2_pass_JESUp', 'h_msd_ak8_muCR4_N2_pass_JESDown',
        #         'h_msd_ak8_muCR4_N2_fail_JESUp', 'h_msd_ak8_muCR4_N2_fail_JESDown',
        #         'h_msd_ak8_muCR4_N2_pass_JERUp', 'h_msd_ak8_muCR4_N2_pass_JERDown',
        #         'h_msd_ak8_muCR4_N2_fail_JERUp', 'h_msd_ak8_muCR4_N2_fail_JERDown',
        #         'h_msd_ak8_muCR4_N2_pass_mutriggerUp', 'h_msd_ak8_muCR4_N2_pass_mutriggerDown',
        #         'h_msd_ak8_muCR4_N2_fail_mutriggerUp', 'h_msd_ak8_muCR4_N2_fail_mutriggerDown',
        #         'h_msd_ak8_muCR4_N2_pass_muidUp', 'h_msd_ak8_muCR4_N2_pass_muidDown',
        #         'h_msd_ak8_muCR4_N2_fail_muidUp', 'h_msd_ak8_muCR4_N2_fail_muidDown',
        #         'h_msd_ak8_muCR4_N2_pass_muisoUp', 'h_msd_ak8_muCR4_N2_pass_muisoDown',
        #         'h_msd_ak8_muCR4_N2_fail_muisoUp', 'h_msd_ak8_muCR4_N2_fail_muisoDown',
        #         'h_msd_ak8_muCR4_N2_pass_PuUp', 'h_msd_ak8_muCR4_N2_pass_PuDown',
        #         'h_msd_ak8_muCR4_N2_fail_PuUp', 'h_msd_ak8_muCR4_N2_fail_PuDown',
        #         ]

    print "Signals... "

    sigSamples = {}
    if year in ['2017','2018','2016legacy'] :
        sigSamples['hqq125']   = normSampleContainer('hqq125',tfiles['hqq125']       , 1, dbtagmin,lumi,False,False,'1',False, iSplit = i_split, maxSplit = max_split, doublebCut=dbtagcut,puOpt=pu_Opt,doublebName=doublebName).addPlots(plots)
        sigSamples['tthqq125'] = normSampleContainer('tthqq125', tfiles['tthqq125']  , 1, dbtagmin,lumi,False,False,'1',False, iSplit = i_split, maxSplit = max_split, doublebCut=dbtagcut,puOpt=pu_Opt,doublebName=doublebName).addPlots(plots) 
        sigSamples['vbfhqq125']= normSampleContainer('vbfhqq125', tfiles['vbfhqq125'], 1, dbtagmin,lumi,False,False,'1',False, iSplit = i_split, maxSplit = max_split, doublebCut=dbtagcut,puOpt=pu_Opt,doublebName=doublebName).addPlots(plots) 
        sigSamples['whqq125']  = normSampleContainer('whqq125', tfiles['whqq125']    , 1, dbtagmin,lumi,False,False,'1',False, iSplit = i_split, maxSplit = max_split, doublebCut=dbtagcut,puOpt=pu_Opt,doublebName=doublebName).addPlots(plots) 
        sigSamples['zhqq125']  = normSampleContainer('zhqq125', tfiles['zhqq125']    , 1, dbtagmin,lumi,False,False,'1',False, iSplit = i_split, maxSplit = max_split, doublebCut=dbtagcut,puOpt=pu_Opt,doublebName=doublebName).addPlots(plots) 
    elif year=='2016':
        sigSamples['hqq125'] = sampleContainer('hqq125', tfiles['hqq125'], 1, dbtagmin, lumi, False, False, '1', True, iSplit = i_split, maxSplit = max_split,doublebCut=dbtagcut,puOpt=pu_Opt)
        #sigSamples['hqq125'] = normSampleContainer('hqq125',tfiles['hqq125'], 1, dbtagmin,lumi,False,False,'1',False, iSplit = i_split, maxSplit = max_split,treeName='Events',puOpt="default").addPlots(plots)
        sigSamples['tthqq125'] = sampleContainer('tthqq125', tfiles['tthqq125'], 1, dbtagmin, lumi, False, False, '1', True, iSplit = i_split, maxSplit = max_split,doublebCut=dbtagcut,puOpt=pu_Opt)
        sigSamples['vbfhqq125'] = sampleContainer('vbfhqq125', tfiles['vbfhqq125'], 1, dbtagmin, lumi, False, False, '1',True, iSplit = i_split, maxSplit = max_split,doublebCut=dbtagcut,puOpt=pu_Opt)
        sigSamples['whqq125'] = sampleContainer('whqq125', tfiles['whqq125'], 1, dbtagmin, lumi, False, False, '1', True, iSplit = i_split, maxSplit = max_split,doublebCut=dbtagcut,puOpt=pu_Opt)
        sigSamples['zhqq125'] = sampleContainer('zhqq125', tfiles['zhqq125'], 1, dbtagmin, lumi, False, False, '1', True, iSplit = i_split, maxSplit = max_split,doublebCut=dbtagcut,puOpt=pu_Opt)

    print "Backgrounds..."
    bkgSamples = {}

    if year in ['2017','2018'] :
        bkgSamples['wqq']  = normSampleContainer('wqq',tfiles['wqq']  ,  1, dbtagmin,lumi,False,False,'1',False, iSplit = i_split, maxSplit = max_split, doublebCut=dbtagcut,puOpt=pu_Opt,doublebName=doublebName).addPlots(plots)
        bkgSamples['zqq']  = normSampleContainer('zqq',tfiles['zqq']  ,  1, dbtagmin,lumi,False,False,'1',False, iSplit = i_split, maxSplit = max_split, doublebCut=dbtagcut,puOpt=pu_Opt,doublebName=doublebName).addPlots(plots)
        bkgSamples['vvqq'] = normSampleContainer('vvqq', tfiles['vvqq'], 1, dbtagmin,lumi,False,False,'1',False, iSplit = i_split, maxSplit = max_split, doublebCut=dbtagcut,puOpt=pu_Opt,doublebName=doublebName).addPlots(plots)
        bkgSamples['tqq']  = normSampleContainer('tqq', tfiles['tqq'] ,  1, dbtagmin,lumi,False,False,'1',False, iSplit = i_split, maxSplit = max_split, doublebCut=dbtagcut,puOpt=pu_Opt,doublebName=doublebName).addPlots(plots)
        bkgSamples['stqq'] = normSampleContainer('stqq', tfiles['stqq'], 1, dbtagmin,lumi,False,False,'1',False, iSplit = i_split, maxSplit = max_split, doublebCut=dbtagcut,puOpt=pu_Opt,doublebName=doublebName).addPlots(plots)
        bkgSamples['zll']  = normSampleContainer('zll', tfiles['zll']  , 1, dbtagmin,lumi,False,False,'1',False ,iSplit = i_split, maxSplit = max_split, doublebCut=dbtagcut,puOpt=pu_Opt,doublebName=doublebName).addPlots(plots)
        if muonCR:
            bkgSamples['wlnu'] = normSampleContainer('wlnu',tfiles['wlnu'],  1, dbtagmin,lumi,False,False,'1',True, iSplit = i_split, maxSplit = max_split, doublebCut=dbtagcut,puOpt=pu_Opt,doublebName=doublebName).addPlots(plots)
        if not options.skipQCD:
            bkgSamples['qcd'] = normSampleContainer('qcd', tfiles['qcd'], 1, dbtagmin,lumi,False,False,'1',False, iSplit = i_split, maxSplit = max_split, doublebCut=dbtagcut,puOpt=pu_Opt,doublebName=doublebName).addPlots(plots)
        pass
    elif year=='2016':
        bkgSamples['wqq']  = sampleContainer('wqq',tfiles['wqq'], 1, dbtagmin,lumi,False,False,'1',True, iSplit = i_split, maxSplit = max_split,doublebCut=dbtagcut,puOpt=pu_Opt)
        bkgSamples['zqq']  = sampleContainer('zqq',tfiles['zqq'], 1, dbtagmin,lumi,False,False,'1',True, iSplit = i_split, maxSplit = max_split,doublebCut=dbtagcut,puOpt=pu_Opt)
        bkgSamples['vvqq'] = sampleContainer('vvqq', tfiles['vvqq'], 1, dbtagmin, lumi, False, False, '1', True, iSplit = i_split, maxSplit = max_split,doublebCut=dbtagcut,puOpt=pu_Opt)
        bkgSamples['tqq'] = sampleContainer('tqq', tfiles['tqq'], 1, dbtagmin, lumi, False, False, '1', True, iSplit = i_split, maxSplit = max_split,doublebCut=dbtagcut,puOpt=pu_Opt)
        bkgSamples['stqq'] = sampleContainer('stqq', tfiles['stqq'], 1, dbtagmin, lumi, False, False, '1', True, iSplit = i_split, maxSplit = max_split,doublebCut=dbtagcut,puOpt=pu_Opt)
        if muonCR:
            bkgSamples['wlnu'] = sampleContainer('wlnu', tfiles['wlnu'], 1, dbtagmin, lumi, False, False, '1', True, iSplit = i_split, maxSplit = max_split,doublebCut=dbtagcut,puOpt=pu_Opt)
        if not options.skipQCD:
            bkgSamples['qcd'] = sampleContainer('qcd', tfiles['qcd'], 1, dbtagmin, lumi, False, False, '1', True, iSplit = i_split, maxSplit = max_split,doublebCut=dbtagcut,puOpt=pu_Opt)
        bkgSamples['zll'] = sampleContainer('zll', tfiles['zll'], 1, dbtagmin, lumi, False, False, '1', True, iSplit = i_split, maxSplit = max_split,doublebCut=dbtagcut,puOpt=pu_Opt)
    elif year=='2016legacy':
        #### reduced set of 2016 bkg samples
        bkgSamples['wqq']  = normSampleContainer('wqq',tfiles['wqq']  ,  1, dbtagmin,lumi,False,False,'1',False, iSplit = i_split, maxSplit = max_split, doublebCut=dbtagcut,puOpt=pu_Opt,doublebName=doublebName).addPlots(plots)
        bkgSamples['zqq']  = normSampleContainer('zqq',tfiles['zqq']  ,  1, dbtagmin,lumi,False,False,'1',False, iSplit = i_split, maxSplit = max_split, doublebCut=dbtagcut,puOpt=pu_Opt,doublebName=doublebName).addPlots(plots)
        bkgSamples['vvqq'] = normSampleContainer('vvqq', tfiles['vvqq'], 1, dbtagmin,lumi,False,False,'1',False, iSplit = i_split, maxSplit = max_split, doublebCut=dbtagcut,puOpt=pu_Opt,doublebName=doublebName).addPlots(plots)
        bkgSamples['tqq']  = normSampleContainer('tqq', tfiles['tqq'] ,  1, dbtagmin,lumi,False,False,'1',False, iSplit = i_split, maxSplit = max_split, doublebCut=dbtagcut,puOpt=pu_Opt,doublebName=doublebName).addPlots(plots)
        if muonCR:
            bkgSamples['wlnu'] = normSampleContainer('wlnu',tfiles['wlnu'],  1, dbtagmin,lumi,False,False,'1',True, iSplit = i_split, maxSplit = max_split, doublebCut=dbtagcut,puOpt=pu_Opt,doublebName=doublebName).addPlots(plots)
        if not options.skipQCD:
            bkgSamples['qcd'] = normSampleContainer('qcd', tfiles['qcd'], 1, dbtagmin,lumi,False,False,'1',False, iSplit = i_split, maxSplit = max_split, doublebCut=dbtagcut,puOpt=pu_Opt,doublebName=doublebName).addPlots(plots)
        bkgSamples['stqq'] = normSampleContainer('stqq', tfiles['stqq'], 1, dbtagmin,lumi,False,False,'1',False, iSplit = i_split, maxSplit = max_split, doublebCut=dbtagcut,puOpt=pu_Opt,doublebName=doublebName).addPlots(plots)
        bkgSamples['zll']  = normSampleContainer('zll', tfiles['zll']  , 1, dbtagmin,lumi,False,False,'1',False ,iSplit = i_split, maxSplit = max_split, doublebCut=dbtagcut,puOpt=pu_Opt,doublebName=doublebName).addPlots(plots)


    print "Data..."
    if not options.skipData:
        if 'skim' in tfiles['data_obs'][0]: dataTree = 'otree'
        else:                               dataTree = 'Events'
        if muonCR:
            if year=='2017'or year=='2018':
                dataSample = sampleContainer('data_obs',tfiles['data_obs'], 1, dbtagmin,lumi, True, False, '((triggerBits&1)&&passJson)',False, iSplit = i_split, maxSplit = max_split,doublebCut=dbtagcut,puOpt=pu_Opt,doublebName=doublebName,treeName = dataTree)
            elif year=='2016':
                dataSample = sampleContainer('data_obs',tfiles['data_obs'], 1, dbtagmin,lumi, True, False, '((triggerBits&4)&&passJson)',False, iSplit = i_split, maxSplit = max_split,doublebCut=dbtagcut,puOpt=pu_Opt)
            elif year=='2016legacy':
                dataSample = sampleContainer('data_obs',tfiles['data_obs'], 1, dbtagmin,lumi, True, False, '(((triggerBits&1)||(triggerBits&2))&&passJson)',False, iSplit = i_split, maxSplit = max_split,doublebCut=dbtagcut,puOpt=pu_Opt,doublebName=doublebName,treeName=dataTree)
        else:
            if year=='2017':
                # 2017 triggerBits
                triggerNames={"version":"zprimebit-15.01","branchName":"triggerBits",
                          "names":[
                               "HLT_AK8PFJet330_PFAK8BTagCSV_p17_v*",
                               "HLT_PFHT1050_v*",
                               "HLT_AK8PFJet400_TrimMass30_v*",
                               "HLT_AK8PFJet420_TrimMass30_v*",
                               "HLT_AK8PFHT800_TrimMass50_v*",
                               "HLT_PFJet500_v*",
                               "HLT_AK8PFJet500_v*"]
                      }
                dataSample = sampleContainer('data_obs', tfiles['data_obs'], sfData, dbtagmin, lumi, True, False,'passJson', True, iSplit = i_split, maxSplit = max_split,doublebCut=dbtagcut,triggerNames=triggerNames,puOpt=pu_Opt,doublebName=doublebName,treeName = dataTree)
            elif year=='2018':
                # 2018 triggerBits
                triggerNames={"version":"zprimebit-15.01","branchName":"triggerBits",
                          "names":[
                               'HLT_AK8PFJet400_TrimMass30_v*',
                               'HLT_AK8PFJet420_TrimMass30_v*',
                               'HLT_AK8PFHT800_TrimMass50_v*',
                               'HLT_PFHT1050_v*',
                               'HLT_PFJet500_v*',
                               'HLT_AK8PFJet500_v*',
                               'HLT_AK8PFJet330_PFAK8BTagCSV_p17_v*',
                               "HLT_AK8PFJet330_TrimMass30_PFAK8BoostedDoubleB_np4_v*",
                        ],
                      }
                dataSample = sampleContainer('data_obs', tfiles['data_obs'], sfData, dbtagmin, lumi, True, False,'passJson', True, iSplit = i_split, maxSplit = max_split,doublebCut=dbtagcut,triggerNames=triggerNames,puOpt=pu_Opt,doublebName=doublebName,treeName = dataTree)
            elif year=='2016legacy':
                triggerNames={"version":"zprimebit-15.01","branchName":"triggerBits",
                          "names":[
                               "HLT_PFHT800_v*",
                               "HLT_PFHT900_v*",
                               "HLT_AK8PFJet360_TrimMass30_v*",
                               'HLT_AK8PFHT700_TrimR0p1PT0p03Mass50_v*',
                               "HLT_PFHT650_WideJetMJJ950DEtaJJ1p5_v*",
                               "HLT_PFHT650_WideJetMJJ900DEtaJJ1p5_v*",
                               "HLT_AK8DiPFJet280_200_TrimMass30_BTagCSV_p20_v*" ,
                               "HLT_PFJet450_v*",
                               ],
                      }
                dataSample = sampleContainer('data_obs', tfiles['data_obs'], sfData, dbtagmin, lumi, True, False,'passJson', True, iSplit = i_split, maxSplit = max_split,doublebCut=dbtagcut,triggerNames=triggerNames,puOpt=pu_Opt,doublebName=doublebName,treeName = dataTree)
            elif year=='2016':
                dataSample = sampleContainer('data_obs', tfiles['data_obs'], sfData, dbtagmin, lumi, True, False,'((triggerBits&2)&&passJson)', True, iSplit = i_split, maxSplit = max_split,doublebCut=dbtagcut,puOpt=pu_Opt)
    hall = {}

    #normSamples =['wqq','zqq','wlnu','hqq125']
    normSamples =['wqq','zqq','wlnu','zll','vvqq','tqq','stqq','qcd','hqq125','tthqq125','vbfhqq125','whqq125','zhqq125']
    for plot in plots:
        tag = plot.split('_')[-1]  # 'pass' or 'fail' or systematicName
        if tag not in ['pass', 'fail']:
            tag = plot.split('_')[-2] + '_' + plot.split('_')[-1]  # 'pass_systematicName', 'pass_systmaticName', etc.

        for process, s in sigSamples.iteritems():
            if (options.year in ['2017','2018','2016legacy']) and process in normSamples:
                hall['%s_%s' % (process, tag)] = sigSamples[process][plot]   #get plot from normSampleContainer
            else:
                hall['%s_%s' % (process, tag)] = getattr(s, plot)           #get plot from SampleContainer
            hall['%s_%s' % (process, tag)].SetName('%s_%s' % (process, tag))

        for process, s in bkgSamples.iteritems():
            if (options.year in ['2017','2018','2016legacy']) and process in normSamples:
                hall['%s_%s' % (process, tag)] = bkgSamples[process][plot]     #get plot from normSampleContainer
            else:
                hall['%s_%s' % (process, tag)] = getattr(s, plot)           #get plot from SampleContainer
            hall['%s_%s' % (process, tag)].SetName('%s_%s' % (process, tag))

        if not options.skipData:
            hall['%s_%s' % ('data_obs', tag)] = getattr(dataSample, plot)
            hall['%s_%s' % ('data_obs', tag)].SetName('%s_%s' % ('data_obs', tag))

    outfile.cd()

    for key, h in hall.iteritems():
        if type(h)==type(ROOT.TH3F()):
            if h.GetName().split("_")[0] == 'hqq125':
                hname = h.GetName()
                nGenPt = h.GetNbinsZ()
                for i in range(1,nGenPt+1):
                    h.GetZaxis().SetRange(i,i+1)
                    if options.muonCR:
                        h2d = h.Project3D("x")             # project to msd for each gen bins for hqq125
                    else:
                        h2d = h.Project3D("yx")             # project to msd v reco_pt for individual gen bins for hqq125
                    h2d.SetName(hname.replace("hqq125","hqq125Genpt%i"%i))
                    print h2d.GetName(),h2d.Integral()
                    h2d.Write()
            else:
                hname = h.GetName()
                if options.muonCR:
                    h2d = h.Project3D("x") #project to normal msd  for muonCR process
                else:
                    h2d = h.Project3D("yx") #project to normal msd v reco_pt for normal process
                h2d.SetName(hname)
                h2d.Write()
        else:
            h.Write()

    outfile.Write()
    outfile.Close()
    return


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
    parser.add_option('-y' ,'--year', type='choice', dest='year', default ='2016',choices=['2016legacy','2016','2017','2018'],help='switch to use different year ', metavar='year')
    parser.add_option("--sfData" , dest="sfData", default=1, type="int", help="process 1/sf of data", metavar="sfData")
    parser.add_option("--region" , dest="region", default='topR6_N2',choices=['topR6_N2','QGquark','QGgluon'], help="region for pass/fail doubleB tag", metavar="region")
    parser.add_option("--doublebName"  , dest="doublebName", default="AK8Puppijet0_deepdoubleb", help="double-b name", metavar="doublebName")

    (options, args) = parser.parse_args()

    main(options, args)
    
    print "All done."
