import ROOT
from ROOT import TFile, TTree, TChain, gPad, gDirectory
from multiprocessing import Process
from optparse import OptionParser
from operator import add
import math
import sys
import time
import array
import glob
import os,json
from plotHelpers import *
from sampleContainer import *
from normSampleContainer import *
DBTMIN=-99
#
def makePlots(plot,hs,hb,hd,hall,legname,color,style,isData,muonCR,odir,lumi,ofile,canvases):
    if isData:
        c = makeCanvasComparisonStackWData(hd,hs,hb,legname,color,style,plot.replace('h_','stack_'),odir,lumi,ofile,True,True,muonCR)
        canvases.append(c)	
    else:
        c = makeCanvasComparisonStack(hs,hb,legname,color,style,'ggHbb',plot.replace('h_','stack_'),odir,lumi,False,ofile)
        c1 = makeCanvasComparison(hall,legname,color,style,plot.replace('h_','signalcomparison_'),odir,lumi,ofile,True)
#        canvases.append(c)	
        canvases.append(c1)

def get2016files():
    #from  commit: ed54500
    idir     = 'root://cmseos.fnal.gov//eos/uscms/store/user/lpchbb/zprimebits-v12.04/cvernier'
    idirData = 'root://cmseos.fnal.gov//eos/uscms/store/user/lpchbb/zprimebits-v12.05/'
    
    tfiles = {
        'Hbb'   :    [idirData + '/GluGluHToBB_M125_13TeV_powheg_pythia8_CKKW_1000pb_weighted.root',
                      idir + '/VBFHToBB_M_125_13TeV_powheg_pythia8_weightfix_all_1000pb_weighted.root',
                      idir + '/ZH_HToBB_ZToQQ_M125_13TeV_powheg_pythia8_1000pb_weighted.root',
                      idir + '/ggZH_HToBB_ZToNuNu_M125_13TeV_powheg_pythia8_1000pb_weighted.root',
                      idir + '/ZH_HToBB_ZToNuNu_M125_13TeV_powheg_pythia8_ext_1000pb_weighted.root',
                      idir + '/ggZH_HToBB_ZToQQ_M125_13TeV_powheg_pythia8_1000pb_weighted.root',
                      idir + '/WminusH_HToBB_WToQQ_M125_13TeV_powheg_pythia8_1000pb_weighted.root',
                      idir + '/WplusH_HToBB_WToQQ_M125_13TeV_powheg_pythia8_1000pb_weighted.root',
                      idir + '/ttHTobb_M125_13TeV_powheg_pythia8_1000pb_weighted.root'],
        'ggHbb'  :  [idirData + '/GluGluHToBB_M125_13TeV_powheg_pythia8_CKKW_1000pb_weighted.root'],
        'VBFHbb' :  [idir + '/VBFHToBB_M_125_13TeV_powheg_pythia8_weightfix_all_1000pb_weighted.root'],
        'VHbb':     [idir + '/ZH_HToBB_ZToQQ_M125_13TeV_powheg_pythia8_1000pb_weighted.root',
                    idir + '/ggZH_HToBB_ZToNuNu_M125_13TeV_powheg_pythia8_1000pb_weighted.root',
                    idir + '/ZH_HToBB_ZToNuNu_M125_13TeV_powheg_pythia8_ext_1000pb_weighted.root',
                    idir + '/ggZH_HToBB_ZToQQ_M125_13TeV_powheg_pythia8_1000pb_weighted.root',
                    idir + '/WminusH_HToBB_WToQQ_M125_13TeV_powheg_pythia8_1000pb_weighted.root',
                    idir + '/WplusH_HToBB_WToQQ_M125_13TeV_powheg_pythia8_1000pb_weighted.root'],
        'ttHbb'  : [idir + '/ttHTobb_M125_13TeV_powheg_pythia8_1000pb_weighted.root'],

        'Diboson': [idir + '/WWTo4Q_13TeV_powheg_1000pb_weighted.root',
                    idir + '/ZZ_13TeV_pythia8_1000pb_weighted.root',
                    idir + '/WZ_13TeV_pythia8_1000pb_weighted.root'],
        'DY':      [idir + '/DYJetsToQQ_HT180_13TeV_1000pb_weighted_v1204.root'],
        'DYll':    [idir + '/DYJetsToLL_M_50_13TeV_ext_1000pb_weighted.root'],
        'SingleTop': [
                    idir + '/ST_t_channel_antitop_4f_inclusiveDecays_TuneCUETP8M2T4_13TeV_powhegV2_madspin_1000pb_weighted.root',
                    idir + '/ST_t_channel_top_4f_inclusiveDecays_TuneCUETP8M2T4_13TeV_powhegV2_madspin_1000pb_weighted.root',
                    idir + '/ST_tW_antitop_5f_inclusiveDecays_13TeV_powheg_pythia8_TuneCUETP8M2T4_1000pb_weighted.root',
                    idir + '/ST_tW_top_5f_inclusiveDecays_13TeV_powheg_pythia8_TuneCUETP8M2T4_1000pb_weighted.root'],
        'W'      : [idir + '/WJetsToQQ_HT180_13TeV_1000pb_weighted_v1204.root'],
        'Wlnu'   : [idir + '/WJetsToLNu_HT_100To200_13TeV_1000pb_weighted.root',
                    idir + '/WJetsToLNu_HT_200To400_13TeV_1000pb_weighted.root',
                    idir + '/WJetsToLNu_HT_400To600_13TeV_1000pb_weighted.root',
                    idir + '/WJetsToLNu_HT_600To800_13TeV_1000pb_weighted.root',
                    idir + '/WJetsToLNu_HT_800To1200_13TeV_1000pb_weighted.root',
                    idir + '/WJetsToLNu_HT_1200To2500_13TeV_1000pb_weighted.root'],
        'TTbar'  : [idir + '/TT_powheg_1000pb_weighted_v1204.root'],  # Powheg is the new default
        'QCD': [    idir + '/QCD_HT100to200_13TeV_1000pb_weighted.root',
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
        'data':     [idirData+'JetHTRun2016B_03Feb2017_ver2_v2_v3.root',
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
                     idirData + 'JetHTRun2016H_03Feb2017_ver3_v1_v3.root'],

        'muon':     [idir + '/SingleMuonRun2016B_03Feb2017_ver1_v1_fixtrig.root',
                     idir + '/SingleMuonRun2016B_03Feb2017_ver2_v2_fixtrig.root',
                     idir + '/SingleMuonRun2016C_03Feb2017_v1_fixtrig.root',
                     idir + '/SingleMuonRun2016D_03Feb2017_v1_fixtrig.root',
                     idir + '/SingleMuonRun2016E_03Feb2017_v1_fixtrig.root',
                     idir + '/SingleMuonRun2016F_03Feb2017_v1_fixtrig.root',
                     idir + '/SingleMuonRun2016G_03Feb2017_v1_fixtrig.root',
                     idir + '/SingleMuonRun2016H_03Feb2017_ver2_v1_fixtrig.root',
                     idir + '/SingleMuonRun2016H_03Feb2017_ver3_v1_fixtrig.root']
        }
    return tfiles


def get2018files():
    idir_temp = 'root://cmseos.fnal.gov//eos/uscms/store/user/lpchbb/zprimebits-v12.04/cvernier/'
    idir_1502 = 'root://cmseos.fnal.gov//eos/uscms/store/user/lpcbacon/dazsle/zprimebits-v15.02/'
    idir_1501 = 'root://cmseos.fnal.gov//eos/uscms/store/user/lpcbacon/dazsle/zprimebits-v15.01/'
    idir_1501skim = 'root://cmseos.fnal.gov//eos/uscms/store/user/lpcbacon/dazsle/zprimebits-v15.01/skim/'
    idir_1502skim = 'root://cmseos.fnal.gov//eos/uscms/store/user/lpcbacon/dazsle/zprimebits-v15.02/skim/'
    tfiles = {
	          'ggHbb_amc' :          { 'GluGluHToBB_M125_13TeV_amcatnloFXFX_pythia8':                [idir_1502skim+'GluGluHToBB_M125_13TeV_amcatnloFXFX_pythia8_*.root']},
	          'ggHbb_amcHpT250' :    { 'GluGluHToBB_M125_LHEHpT_250_Inf_13TeV_amcatnloFXFX_pythia8' :[idir_1502skim+'GluGluHToBB_M125_LHEHpT_250_Inf_13TeV_amcatnloFXFX_pythia8_*.root']},
	          'ggHbb_NNLOPS'    :    { 'GluGluHToBB_M-125_13TeV_powheg_MINLO_NNLOPS_pythia8'        :[idir_1502+'GluGluHToBB_M_125_13TeV_powheg_MINLO_NNLOPS_pythia8/*.root']},
	          #'ggHbb_NNLOPS'    :    { 'GluGluHToBB_M-125_13TeV_powheg_MINLO_NNLOPS_pythia8'        :[idir_1502skim+'GluGluHToBB_M_125_13TeV_powheg_MINLO_NNLOPS_pythia8*.root']},
	          'ggHbb'     :          { 'GluGluHToBB_M125_13TeV_powheg_pythia8':                      [idir_1502skim+'/GluGluHToBB_M125_13TeV_powheg_pythia8_*.root']},
	          'VBFHbb'    :          { 'VBFHToBB_M_125_13TeV_powheg_pythia8_weightfix':              [idir_1502skim+'/VBFHToBB_M_125_13TeV_powheg_pythia8_weightfix_*.root']},
	          'VHbb'      :          { 
                                    'ZH_HToBB_ZToQQ_M125_13TeV_powheg_pythia8':              [idir_1502skim+'/ZH_HToBB_ZToQQ_M125_13TeV_powheg_pythia8_*.root'],
                                    'ZH_HToBB_ZToNuNu_M125_13TeV_powheg_pythia8':            [idir_1502skim+'/ZH_HToBB_ZToQQ_M125_13TeV_powheg_pythia8_*.root'],
                                    'WminusH_HToBB_WToQQ_M125_13TeV_powheg_pythia8':         [idir_1502skim+'/WminusH_HToBB_WToQQ_M125_13TeV_powheg_pythia8_*.root'],
                                    'WplusH_HToBB_WToQQ_M125_13TeV_powheg_pythia8':          [idir_1502skim+'/WplusH_HToBB_WToQQ_M125_13TeV_powheg_pythia8_*.root'],
                                    #'ggZH_HToBB_ZToNuNu_M125_13TeV_powheg_herwigpp':         [idir_1502skim+'/ggZH_HToBB_ZToNuNu_M125_13TeV_powheg_herwigpp_*.root'],
                                    'ggZH_HToBB_ZToQQ_M125_13TeV_powheg_pythia8':            [idir_1502skim+'/ggZH_HToBB_ZToQQ_M125_13TeV_powheg_pythia8_*.root'],
                                    },
	          'ttHbb'    :          { 'ttHTobb_M125_TuneCP5_13TeV_powheg_pythia8':           [idir_1502skim+'/ttHTobb_M125_TuneCP5_13TeV_powheg_pythia8_*.root']},
              'Diboson':    {
                             'WW_TuneCP5_13TeV-pythia8':[idir_1501skim+'WW_TuneCP5_13TeV_pythia8_*.root'],
                             'WZ_TuneCP5_13TeV-pythia8':[idir_1501skim+'WZ_TuneCP5_13TeV_pythia8_*.root'],
                             'ZZ_TuneCP5_13TeV-pythia8':[idir_1501skim+'ZZ_TuneCP5_13TeV_pythia8_*.root']
                            },
              'DY':         {
                            'ZJetsToQQ_HT400to600_qc19_4j_TuneCP5_13TeV': [idir_1502skim + '/ZJetsToQQ_HT400to600_qc19_4j_TuneCP5_13TeV_*.root'],
                            'ZJetsToQQ_HT600to800_qc19_4j_TuneCP5_13TeV': [idir_1502skim + '/ZJetsToQQ_HT600to800_qc19_4j_TuneCP5_13TeV_*.root'],
                            'ZJetsToQQ_HT-800toInf_qc19_4j_TuneCP5_13TeV':[idir_1502skim + '/ZJetsToQQ_HT-800toInf_qc19_4j_TuneCP5_13TeV_*.root'],
                            },
              'DYll':       {
                             'DYJetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8'  :[idir_1502skim+'/DYJetsToLL_M_50_TuneCP5_13TeV_*.root'] , 
                            },
              'SingleTop':  {
                            # 'ST_t-channel_antitop_4f_inclusiveDecays_TuneCP5_13TeV-powhegV2-madspin-pythia8':[idir_1502skim+'ST_t_channel_antitop_4f_inclusiveDecays_TuneCP5_13TeV_powhegV2_madspin_pythia8_*.root'],
                            # 'ST_t-channel_top_4f_inclusiveDecays_TuneCP5_13TeV-powhegV2-madspin-pythia8'    :[idir_1502skim+'ST_t_channel_top_4f_inclusiveDecays_TuneCP5_13TeV_powhegV2_madspin_pythia8_*.root'],
                             'ST_t-channel_antitop_4f_inclusiveDecays_TuneCP5_13TeV-powhegV2-madspin-pythia8':[idir_1502skim+'ST_t_channel_antitop_4f_InclusiveDecays_TuneCP5_13TeV_powheg_madspin_pythia8_*.root'],
                             'ST_t-channel_top_4f_inclusiveDecays_TuneCP5_13TeV-powhegV2-madspin-pythia8'    :[idir_1502skim+'ST_t_channel_top_4f_InclusiveDecays_TuneCP5_13TeV_powheg_madspin_pythia8_*.root'],
                             'ST_tW_antitop_5f_inclusiveDecays_TuneCP5_13TeV-powheg-pythia8'                 :[idir_1502skim+'ST_tW_antitop_5f_inclusiveDecays_TuneCP5_13TeV_powheg_pythia8_*.root'],
                             'ST_tW_top_5f_inclusiveDecays_TuneCP5_13TeV-powheg-pythia8'                     :[idir_1502skim+'ST_tW_top_5f_inclusiveDecays_TuneCP5_13TeV_powheg_pythia8_*.root']
                            },
              'W'         : {
                              'WJetsToQQ_HT400to600_qc19_3j_TuneCP5_13TeV': [idir_1502skim + 'WJetsToQQ_HT400to600_qc19_3j_TuneCP5_13TeV_*.root'],
                              'WJetsToQQ_HT600to800_qc19_3j_TuneCP5_13TeV': [idir_1502skim + 'WJetsToQQ_HT600to800_qc19_3j_TuneCP5_13TeV_*.root'],
                              'WJetsToQQ_HT-800toInf_qc19_3j_TuneCP5_13TeV':[idir_1502skim + 'WJetsToQQ_HT-800toInf_qc19_3j_TuneCP5_13TeV_*.root'],
                             },
              'Wlnu':       {
                              # "WJetsToLNu_TuneCP5_13TeV-madgraphMLM-pythia8"               :[ idir_1401skim+'WJetsToLNu_TuneCP5_13TeV*.root'],
                               "WJetsToLNu_HT-200To400_TuneCP5_13TeV-madgraphMLM-pythia8"   :[ idir_1501skim+'WJetsToLNu_HT_200To400_*.root'],
                               "WJetsToLNu_HT-400To600_TuneCP5_13TeV-madgraphMLM-pythia8"   :[ idir_1501skim+'WJetsToLNu_HT_400To600_*.root'],
                               "WJetsToLNu_HT-600To800_TuneCP5_13TeV-madgraphMLM-pythia8"   :[ idir_1501skim+'WJetsToLNu_HT_600To800_*.root'],
                               "WJetsToLNu_HT-800To1200_TuneCP5_13TeV-madgraphMLM-pythia8"  :[ idir_1501skim+'WJetsToLNu_HT_800To1200_*.root'],
                               "WJetsToLNu_HT-1200To2500_TuneCP5_13TeV-madgraphMLM-pythia8" :[ idir_1501skim+'WJetsToLNu_HT_1200To2500_*.root'],
                               "WJetsToLNu_HT-2500ToInf_TuneCP5_13TeV-madgraphMLM-pythia8"  :[ idir_1501skim+'WJetsToLNu_HT_2500ToInf*.root'],
                            },
              'TTbar':      {
                             'TTToHadronic_TuneCP5_13TeV_powheg_pythia8'    :[idir_1502skim+'TTToHadronic_TuneCP5_13TeV-powheg-pythia8_*.root'],
                             'TTToSemiLeptonic_TuneCP5_13TeV_powheg_pythia8':[idir_1502skim+'TTToSemiLeptonic_TuneCP5_13TeV-powheg-pythia8_*.root'],
                             'TTTo2L2Nu_TuneCP5_13TeV_powheg_pythia8'       :[idir_1502skim+'TTTo2L2Nu_TuneCP5_13TeV-powheg-pythia8_*.root'       ],
                            },
              'QCD':        {
                             'QCD_HT500to700_TuneCP5_13TeV-madgraphMLM-pythia8'  :[idir_1502skim+'/QCD_HT500to700_TuneCP5_13TeV-madgraphMLM-pythia8_*.root'  ],
                             'QCD_HT700to1000_TuneCP5_13TeV-madgraphMLM-pythia8' :[idir_1502skim+'/QCD_HT700to1000_TuneCP5_13TeV-madgraphMLM-pythia8_*.root' ],
                             'QCD_HT1000to1500_TuneCP5_13TeV-madgraphMLM-pythia8':[idir_1502skim+'/QCD_HT1000to1500_TuneCP5_13TeV-madgraphMLM-pythia8_*.root'],
                             'QCD_HT1500to2000_TuneCP5_13TeV-madgraphMLM-pythia8':[idir_1502skim+'/QCD_HT1500to2000_TuneCP5_13TeV-madgraphMLM-pythia8_*.root'],
                             'QCD_HT2000toInf_TuneCP5_13TeV-madgraphMLM-pythia8' :[idir_1502skim+'/QCD_HT2000toInf_TuneCP5_13TeV-madgraphMLM-pythia8_*.root' ]
                            },
              'data': [
                            idir_1502skim + 'JetHTRun2018A_17Sep2018_v1*.root',
                            idir_1502skim + 'JetHTRun2018B_17Sep2018_v1*.root',
                            idir_1502skim + 'JetHTRun2018C_PromptReco_v*.root',
                            idir_1502skim + 'JetHTRun2018D_PromptReco_v*.root',
                      ],
              'muon': [
                       idir_1502skim+'/SingleMuonRun2018A_17Sep2018_v2*.root',
                       idir_1502skim+'/SingleMuonRun2018B_17Sep2018_v1*.root',
                       idir_1502skim+'/SingleMuonRun2018C_17Sep2018_v1*.root',
                       idir_1502skim+'/SingleMuonRun2018D_PromptReco_v2*.root',
                    ]
            }
    return tfiles

def get2017files():
    idir_temp = 'root://cmseos.fnal.gov//eos/uscms/store/user/lpchbb/zprimebits-v12.04/cvernier/'
    idir = 'root://cmseos.fnal.gov//eos/uscms/store/user/lpcbacon/dazsle/zprimebits-v12.07-puWeight/norm/'
    idir_1208 = 'root://cmseos.fnal.gov//eos/uscms/store/user/lpcbacon/dazsle/zprimebits-v12.08/norm'
    #idir_1401 = '/eos/uscms/store/user/lpcbacon/dazsle/zprimebits-v14.01/'
    idir_1401 = 'root://cmseos.fnal.gov//eos/uscms/store/user/lpcbacon/dazsle/zprimebits-v14.01/'
    idir_1401skim = 'root://cmseos.fnal.gov//eos/uscms/store/user/lpcbacon/dazsle/zprimebits-v14.01/skim/'
    idir_1501 = 'root://cmseos.fnal.gov//eos/uscms/store/user/lpcbacon/dazsle/zprimebits-v15.01/'
    idir_1501skim = 'root://cmseos.fnal.gov//eos/uscms/store/user/lpcbacon/dazsle/zprimebits-v15.01/skim/'
    idirData = 'root://cmseos.fnal.gov//eos/uscms/store/user/lpcbacon/dazsle/zprimebits-v12.07/sklim/'

    tfiles = {'Hbb':        [idir+'/GluGluHToBB_M125_13TeV_powheg_pythia8_all_1000pb_weighted.root',
			                idir+'/VBFHToBB_M_125_13TeV_powheg_pythia8_weightfix_all_1000pb_weighted.root',
			                idir+'/ZH_HToBB_ZToQQ_M125_13TeV_powheg_pythia8_1000pb_weighted.root',
			                idir+'/WminusH_HToBB_WToQQ_M125_13TeV_powheg_pythia8_1000pb_weighted.root',
			                idir+'/WplusH_HToBB_WToQQ_M125_13TeV_powheg_pythia8_1000pb_weighted.root',  
			                idir+'/ttHTobb_M125_TuneCP5_13TeV_powheg_pythia8_1000pb_weighted.root',
			                idir+'/ggZH_HToBB_ZToNuNu_M125_13TeV_powheg_herwigpp_1000pb_weighted.root',
			                idir+'/ggZH_HToBB_ZToQQ_M125_13TeV_powheg_pythia8_1000pb_weighted.root',
			                idir+'/ZH_HToBB_ZToNuNu_M125_13TeV_powheg_pythia8_1000pb_weighted.root'],	
	          'ggHbb_amc' :          { 'GluGluHToBB_M125_13TeV_amcatnloFXFX_pythia8':                [idir_1501skim+'GluGluHToBB_M125_13TeV_amcatnloFXFX_pythia8_*.root']},
	          'ggHbb_amcHpT250' :    { 'GluGluHToBB_M125_LHEHpT_250_Inf_13TeV_amcatnloFXFX_pythia8' :[idir_1501skim+'GluGluHToBB_M125_LHEHpT_250_Inf_13TeV_amcatnloFXFX_pythia8_*.root']},
	          'ggHbb'     :          { 'GluGluHToBB_M125_13TeV_powheg_pythia8':                      [idir_1501skim+'/GluGluHToBB_M125_13TeV_powheg_pythia8_*.root']},
	          'VBFHbb'    :          { 'VBFHToBB_M_125_13TeV_powheg_pythia8_weightfix':              [idir_1501skim+'/VBFHToBB_M_125_13TeV_powheg_pythia8_weightfix_*.root']},
	          'VHbb'      :          { 
                                    'ZH_HToBB_ZToQQ_M125_13TeV_powheg_pythia8':              [idir_1501skim+'/ZH_HToBB_ZToQQ_M125_13TeV_powheg_pythia8_*.root'],
                                    'ZH_HToBB_ZToNuNu_M125_13TeV_powheg_pythia8':            [idir_1501skim+'/ZH_HToBB_ZToQQ_M125_13TeV_powheg_pythia8_*.root'],
                                    'WminusH_HToBB_WToQQ_M125_13TeV_powheg_pythia8':         [idir_1501skim+'/WminusH_HToBB_WToQQ_M125_13TeV_powheg_pythia8_*.root'],
                                    'WplusH_HToBB_WToQQ_M125_13TeV_powheg_pythia8':          [idir_1501skim+'/WplusH_HToBB_WToQQ_M125_13TeV_powheg_pythia8_*.root'],
                                    #'ggZH_HToBB_ZToNuNu_M125_13TeV_powheg_herwigpp':         [idir_1501skim+'/ggZH_HToBB_ZToNuNu_M125_13TeV_powheg_herwigpp_*.root'],
                                    'ggZH_HToBB_ZToQQ_M125_13TeV_powheg_pythia8':            [idir_1501skim+'/ggZH_HToBB_ZToQQ_M125_13TeV_powheg_pythia8_*.root'],
                                    },
	          'ttHbb'    :          { 'ttHTobb_M125_TuneCP5_13TeV_powheg_pythia8':           [idir_1501skim+'/ttHTobb_M125_TuneCP5_13TeV_powheg_pythia8_*.root']},
              'Diboson':    {
                             'WW_TuneCP5_13TeV-pythia8':[idir_1501skim+'WW_TuneCP5_13TeV_pythia8_*.root'],
                             'WZ_TuneCP5_13TeV-pythia8':[idir_1501skim+'WZ_TuneCP5_13TeV_pythia8_*.root'],
                             'ZZ_TuneCP5_13TeV-pythia8':[idir_1501skim+'ZZ_TuneCP5_13TeV_pythia8_*.root']
                            },
              'DY':         {
                            'ZJetsToQQ_HT400to600_qc19_4j_TuneCP5_13TeV': [idir_1501skim + '/ZJetsToQQ_HT400to600_qc19_4j_TuneCP5_13TeV_*.root'],
                            'ZJetsToQQ_HT600to800_qc19_4j_TuneCP5_13TeV': [idir_1501skim + '/ZJetsToQQ_HT600to800_qc19_4j_TuneCP5_13TeV_*.root'],
                            'ZJetsToQQ_HT-800toInf_qc19_4j_TuneCP5_13TeV':[idir_1501skim + '/ZJetsToQQ_HT-800toInf_qc19_4j_TuneCP5_13TeV_*.root'],
                            },
              #'DYll':       [idir_temp+'/DYJetsToLL_M_50_13TeV_ext_1000pb_weighted.root'],
              'DYll':       {
                             'DYJetsToLL_M_50_HT_400to600_TuneCP5_13TeV'  :[idir_1501skim+'/DYJetsToLL_M_50_HT_400to600_TuneCP5_13TeV*.root'] , 
                             'DYJetsToLL_M_50_HT_600to800_TuneCP5_13TeV'  :[idir_1501skim+'/DYJetsToLL_M_50_HT_600to800_TuneCP5_13TeV*.root'] , 
                             'DYJetsToLL_M_50_HT_800to1200_TuneCP5_13TeV' :[idir_1501skim+'/DYJetsToLL_M_50_HT_800to1200_TuneCP5_13TeV*.root'],                                     
                             'DYJetsToLL_M_50_HT_1200to2500_TuneCP5_13TeV':[idir_1501skim+'/DYJetsToLL_M_50_HT_1200to2500_TuneCP5_13TeV*.root'], 
                             'DYJetsToLL_M_50_HT_2500toInf_TuneCP5_13TeV' :[idir_1501skim+'/DYJetsToLL_M_50_HT_2500toInf_TuneCP5_13TeV*.root' ] 
                            },

              'SingleTop':  {
                             'ST_t-channel_antitop_4f_inclusiveDecays_TuneCP5_13TeV-powhegV2-madspin-pythia8':[idir_1501skim+'ST_t_channel_antitop_4f_inclusiveDecays_TuneCP5_13TeV_powhegV2_madspin_pythia8_*.root'],
                             'ST_t-channel_top_4f_inclusiveDecays_TuneCP5_13TeV-powhegV2-madspin-pythia8'    :[idir_1501skim+'ST_t_channel_top_4f_inclusiveDecays_TuneCP5_13TeV_powhegV2_madspin_pythia8_*.root'],
                             'ST_tW_antitop_5f_inclusiveDecays_TuneCP5_13TeV-powheg-pythia8'                 :[idir_1501skim+'ST_tW_antitop_5f_inclusiveDecays_TuneCP5_13TeV_powheg_pythia8_*.root'],
                             'ST_tW_top_5f_inclusiveDecays_TuneCP5_13TeV-powheg-pythia8'                     :[idir_1501skim+'ST_tW_top_5f_inclusiveDecays_TuneCP5_13TeV_powheg_pythia8_*.root']
                            },
              'W'         : {
                              'WJetsToQQ_HT400to600_qc19_3j_TuneCP5_13TeV': [idir_1501skim + 'WJetsToQQ_HT400to600_qc19_3j_TuneCP5_13TeV_*.root'],
                              'WJetsToQQ_HT600to800_qc19_3j_TuneCP5_13TeV': [idir_1501skim + 'WJetsToQQ_HT600to800_qc19_3j_TuneCP5_13TeV_*.root'],
                              'WJetsToQQ_HT-800toInf_qc19_3j_TuneCP5_13TeV':[idir_1501skim + 'WJetsToQQ_HT-800toInf_qc19_3j_TuneCP5_13TeV_*.root'],
                             },
              'Wlnu':       {
                              # "WJetsToLNu_TuneCP5_13TeV-madgraphMLM-pythia8"               :[ idir_1401skim+'WJetsToLNu_TuneCP5_13TeV*.root'],
                               "WJetsToLNu_HT-200To400_TuneCP5_13TeV-madgraphMLM-pythia8"   :[ idir_1501skim+'WJetsToLNu_HT_200To400_*.root'],
                               "WJetsToLNu_HT-400To600_TuneCP5_13TeV-madgraphMLM-pythia8"   :[ idir_1501skim+'WJetsToLNu_HT_400To600_*.root'],
                               "WJetsToLNu_HT-600To800_TuneCP5_13TeV-madgraphMLM-pythia8"   :[ idir_1501skim+'WJetsToLNu_HT_600To800_*.root'],
                               "WJetsToLNu_HT-800To1200_TuneCP5_13TeV-madgraphMLM-pythia8"  :[ idir_1501skim+'WJetsToLNu_HT_800To1200_*.root'],
                               "WJetsToLNu_HT-1200To2500_TuneCP5_13TeV-madgraphMLM-pythia8" :[ idir_1501skim+'WJetsToLNu_HT_1200To2500_*.root'],
                               "WJetsToLNu_HT-2500ToInf_TuneCP5_13TeV-madgraphMLM-pythia8" :[ idir_1501skim+'WJetsToLNu_HT_2500ToInf*.root'],
                            },
              'TTbar':      {
                             'TTToHadronic_TuneCP5_13TeV_powheg_pythia8'    :[idir_1501skim+'TTToHadronic_TuneCP5_13TeV_powheg_pythia8_*.root'],
                             'TTToSemiLeptonic_TuneCP5_13TeV_powheg_pythia8':[idir_1501skim+'TTToSemiLeptonic_TuneCP5_13TeV_powheg_pythia8_*.root'],
                             'TTTo2L2Nu_TuneCP5_13TeV_powheg_pythia8'       :[idir_1501skim+'TTTo2L2Nu_TuneCP5_13TeV_powheg_pythia8_*.root'       ],
                            },
              'QCD':        {
                             'QCD_HT500to700_TuneCP5_13TeV-madgraphMLM-pythia8'  :[idir_1501skim+'/QCD_HT500to700_TuneCP5_13TeV-madgraphMLM-pythia8_*.root'  ],
                             'QCD_HT700to1000_TuneCP5_13TeV-madgraphMLM-pythia8' :[idir_1501skim+'/QCD_HT700to1000_TuneCP5_13TeV-madgraphMLM-pythia8_*.root' ],
                             'QCD_HT1000to1500_TuneCP5_13TeV-madgraphMLM-pythia8':[idir_1501skim+'/QCD_HT1000to1500_TuneCP5_13TeV-madgraphMLM-pythia8_*.root'],
                             'QCD_HT1500to2000_TuneCP5_13TeV-madgraphMLM-pythia8':[idir_1501skim+'/QCD_HT1500to2000_TuneCP5_13TeV-madgraphMLM-pythia8_*.root'],
                             'QCD_HT2000toInf_TuneCP5_13TeV-madgraphMLM-pythia8' :[idir_1501skim+'/QCD_HT2000toInf_TuneCP5_13TeV-madgraphMLM-pythia8_*.root' ]
                            },
              'data': [
        	        	     idir_1501skim + 'JetHTRun2017B_17Nov2017_v1_*.root',
                             idir_1501skim + 'JetHTRun2017C_17Nov2017_v1_*.root',
                             idir_1501skim + 'JetHTRun2017D_17Nov2017_v1_*.root',
                             idir_1501skim + 'JetHTRun2017E_17Nov2017_v1_*.root',
                             #idir_1501skim + 'JetHTRun2017F_17Nov2017_v1_*.root'
                             idir_1501skim + 'JetHTRun2017F_17Nov2017_v1_*.rootnodupl.root',
                      ],
              'muon': [
                       idir_1501skim+'/SingleMuonRun2017B_17Nov2017_v1_*.root',
                       idir_1501skim+'/SingleMuonRun2017C_17Nov2017_v1_*.root',
                       idir_1501skim+'/SingleMuonRun2017D_17Nov2017_v1_*.root',
                       idir_1501skim+'/SingleMuonRun2017E_17Nov2017_v1_*.root',
                       idir_1501skim+'/SingleMuonRun2017F_17Nov2017_v1_*.root'
                    ]
            }
    return tfiles

##############################################################################
def main(options,args,outputExists):
    #idir = "/eos/uscms/store/user/lpchbb/ggHsample_V11/sklim-v0-28Oct/"
    #odir = "plots_2016_10_31/"
#    idir = options.idir

    #TODO: update to new samples
    odir = options.odir
    lumi = options.lumi
    isData = options.isData
    muonCR = options.muonCR
    year = options.year
    i_split = options.iSplit
    max_split = options.maxSplit
    
    legname = {'ggHbb': 'ggH(b#bar{b})',
               'Hbb': 'H(b#bar{b})',
               'VBFHbb':'VBF H(b#bar{b})',
               'VHbb': 'VH(b#bar{b})',
	           'ttHbb': 't#bar{t}H(b#bar{b})',
               'Diboson': 'VV(4q)',
               'SingleTop': 'single-t',
               'DY': 'Z(qq)+jets',
               'W': 'W(qq)+jets',
               'DYll': 'Z(ll)+jets',
               'Wlnu': 'W(l#nu)+jets',
               'TTbar': 't#bar{t}+jets',        
               'TTbar1Mu': 't#bar{t}+jets, 1#mu',  
               'TTbar1Ele': 't#bar{t}+jets, 1e',        
               'TTbar1Tau': 't#bar{t}+jets, 1#tau',        
               'TTbar0Lep': 't#bar{t}+jets, 0l',        
               'TTbar2Lep': 't#bar{t}+jets, 2l',        
               'QCD': 'QCD',
	           'data': 'JetHT data',
               'muon': 'SingleMuon data',
               'Phibb50': '#Phi(b#bar{b}), 50 GeV',
               'Phibb75': '#Phi(b#bar{b}), 75 GeV',
               'Phibb150': '#Phi(b#bar{b}), 150 GeV',
               'Phibb250': '#Phi(b#bar{b}), 250 GeV'               
               }


    if isData and muonCR:
        legname['data'] = 'SingleMuon data'

    if year=="2017":
        samplefiles   = open(os.path.expandvars("$ZPRIMEPLUSJET_BASE/analysis/ggH/samplefiles.json"),"r")
        tfiles  = json.load(samplefiles)['controlPlotsGGH_2017']
        pu_Opt  = {'data':"2017"}
    elif year=='2016':
        tfiles = get2016files()
        pu_Opt  = {'data':"2016",'MC':"12.04"}
    elif year=='2018':
        samplefiles   = open(os.path.expandvars("$ZPRIMEPLUSJET_BASE/analysis/ggH/samplefiles.json"),"r")
        tfiles  = json.load(samplefiles)['controlPlotsGGH_2018']
        pu_Opt  = {'data':"2018"}
    else:
        print "Invalid choice of year. Aborting"            
        sys.exit()
       

    color = {'ggHbb': ROOT.kAzure+1,
             'Hbb': ROOT.kRed,
             'VHbb': ROOT.kTeal+1,
             'VBFHbb': ROOT.kBlue-10,
		     'Phibb50': ROOT.kBlue-1,
             'Phibb75': ROOT.kAzure+1,
		     'Phibb150': ROOT.kTeal+1,
		     'Phibb250': ROOT.kMagenta+1,
		     'ttHbb': ROOT.kBlue-1,
             'Diboson': ROOT.kOrange,
             'SingleTop': ROOT.kRed-2,
             'DY':  ROOT.kRed,
             'DYll':  ROOT.kRed-3,
             'W':  ROOT.kGreen+3,
             'Wlnu':  ROOT.kGreen+2,
             'TTbar':  ROOT.kGray,
             'TTbar1Mu':  ROOT.kViolet,
             'TTbar1Ele':  ROOT.kSpring,
             'TTbar1Tau':  ROOT.kOrange+2,
             'TTbar0Lep':  ROOT.kGray,
             'TTbar2Lep':  ROOT.kMagenta-9,
             'QCD': ROOT.kBlue+2,
		     'data':ROOT.kBlack,
		     'muon':ROOT.kBlack
            }

    style = {'Hbb': 1,
             'ggHbb': 2,             
		     'Phibb50': 2,
             'Phibb75': 3,
		     'Phibb150': 4,
		     'Phibb250': 5,
             'VBFHbb': 3,
		     'VHbb': 4,
		     'ttHbb': 5,
             'Diboson': 1,
             'SingleTop': 1,
             'DY': 1,
             'DYll': 1,
             'W': 1,
             'Wlnu': 1,
             'TTbar': 1,
             'TTbar1Mu': 1,
             'TTbar1Ele': 1,
             'TTbar1Tau': 1,
             'TTbar0Lep': 1,
             'TTbar2Lep': 1,
             'QCD': 1,
             'data': 1,
		     'muon':1
            }
        

    canvases = []
    if isData and muonCR:
        plots = []
        testSample = sampleContainer('test',[], 1, DBTMIN,lumi)
        for attr in dir(testSample):
            try:
                if 'h_' in attr and getattr(testSample,attr).InheritsFrom('TH1') and not getattr(testSample,attr).InheritsFrom('TH2'):
                    plots.append(attr)
            except:
                pass
    elif isData:
        plots = ['h_pt_ak8','h_eta_ak8','h_rho_ak8','h_msd_ak8','h_msd_ak8_raw',
                 'h_dbtag_ak8','h_dbtag_ak8_aftercut',
                 'h_n_ak4','h_n_ak4_dR0p8','h_t21_ak8',
                 'h_t32_ak8','h_t21ddt_ak8',
                 'h_maxAK4_dcsvb','h_n_OppHem_AK4',
                 'h_npv', 'h_met','h_ht',
                 'h_n2b1sdddt_ak8','h_n2b1sdddt_ak8_aftercut','h_Cuts']
    else:
        plots = []
        testSample = sampleContainer('test',[], 1, DBTMIN,lumi)
        for attr in dir(testSample):
            try:
                if 'h_' in attr and getattr(testSample,attr).InheritsFrom('TH1') and not getattr(testSample,attr).InheritsFrom('TH2'):
                    plots.append(attr)
            except:
                pass
    if not outputExists: 
        samples = ['ggHbb','VBFHbb','VHbb','ttHbb','QCD','SingleTop','Diboson','TTbar']                      
        #samples = ['ggHbb','VBFHbb','VHbb','ttHbb','QCD','SingleTop','Diboson','W','DY','TTbar']                      
        pudir="root://cmseos.fnal.gov//eos/uscms/store/user/lpcbacon/dazsle/zprimebits-v12.08-Pu/hadd/"
        for s in samples:
            if type(tfiles[s])==type({}): continue
            for tfile in tfiles[s]:
                if not "root://" in tfile and not os.path.isfile(tfile):
                    print 'ControlplotGGH:: error: %s does not exist'%tfile                 
                    sys.exit()
        print "Signals... "
        sigSamples = {}

        if  year=='2017' or year=='2018':
            sigSamples['ggHbb_amc']       = normSampleContainer('ggHbb_amc',tfiles['ggHbb_amc']  , 1, DBTMIN,lumi,False,False,'1',False, iSplit = i_split, maxSplit = max_split, puOpt=pu_Opt,doublebName='AK8Puppijet0_deepdoubleb').addPlots(plots)
            sigSamples['ggHbb_amcHpT250'] = normSampleContainer('ggHbb_amcHpT250',tfiles['ggHbb_amcHpT250'], 1, DBTMIN,lumi,False,False,'1',False, iSplit = i_split, maxSplit = max_split, puOpt=pu_Opt,doublebName='AK8Puppijet0_deepdoubleb').addPlots(plots)
            sigSamples['ggHbb']           = normSampleContainer('ggHbb',tfiles['ggHbb']  , 1, DBTMIN,lumi,False,False,'1',False, iSplit = i_split, maxSplit = max_split, puOpt=pu_Opt,doublebName='AK8Puppijet0_deepdoubleb').addPlots(plots) 
            sigSamples['VHbb']           = normSampleContainer('VHbb',tfiles['VHbb']  , 1, DBTMIN,lumi,False,False,'1',False, iSplit = i_split, maxSplit = max_split, puOpt=pu_Opt,doublebName='AK8Puppijet0_deepdoubleb').addPlots(plots) 
            sigSamples['VBFHbb']         = normSampleContainer('VBFHbb',tfiles['VBFHbb']  , 1, DBTMIN,lumi,False,False,'1',False, iSplit = i_split, maxSplit = max_split, puOpt=pu_Opt,doublebName='AK8Puppijet0_deepdoubleb').addPlots(plots) 
            sigSamples['ttHbb']          = normSampleContainer('ttHbb',tfiles['ttHbb']  , 1, DBTMIN,lumi,False,False,'1',False, iSplit = i_split, maxSplit = max_split, puOpt=pu_Opt,doublebName='AK8Puppijet0_deepdoubleb').addPlots(plots) 
            if year == '2018':
                sigSamples['ggHbb_NNLOPS'] = normSampleContainer('ggHbb_NNLOPS',tfiles['ggHbb_NNLOPS'], 1, DBTMIN,lumi,False,False,'1',False, iSplit = i_split, maxSplit = max_split, treeName="Events",puOpt=pu_Opt,doublebName='AK8Puppijet0_deepdoubleb').addPlots(plots)
        elif year=='2016':
            sigSamples['ggHbb']  = sampleContainer('ggHbb',tfiles['ggHbb']  , 1, DBTMIN,lumi,False,False,'1',False, iSplit = i_split, maxSplit = max_split,puOpt=pu_Opt) 
            sigSamples['VBFHbb'] = sampleContainer('VBFHbb',tfiles['VBFHbb'], 1, DBTMIN,lumi ,False,False,'1',False, iSplit = i_split, maxSplit = max_split,puOpt=pu_Opt) 
            sigSamples['VHbb'] = sampleContainer('VHbb',tfiles['VHbb'], 1, DBTMIN,lumi ,False,False,'1',False, iSplit = i_split, maxSplit = max_split,puOpt=pu_Opt) 	
            sigSamples['ttHbb'] = sampleContainer('ttHbb',tfiles['ttHbb'], 1, DBTMIN,lumi ,False,False,'1',False, iSplit = i_split, maxSplit = max_split,puOpt=pu_Opt)    
        print "Backgrounds..."
        bkgSamples = {}    
        subwqqSamples={}
        subzqqSamples={}
        if  year=='2017' or year=='2018':
            bkgSamples['W']         = normSampleContainer('W',tfiles['W'], 1, DBTMIN,lumi,False,False,'1',False, iSplit = i_split, maxSplit = max_split,   puOpt=pu_Opt,doublebName='AK8Puppijet0_deepdoubleb').addPlots(plots)
            bkgSamples['DY']        = normSampleContainer('DY',tfiles['DY'], 1, DBTMIN,lumi,False,False,'1',False, iSplit = i_split, maxSplit = max_split, puOpt=pu_Opt,doublebName='AK8Puppijet0_deepdoubleb').addPlots(plots)
            bkgSamples['TTbar']     = normSampleContainer('TTbar',tfiles['TTbar'], 1, DBTMIN,lumi,False,False,'1',False, iSplit = i_split, maxSplit = max_split, puOpt=pu_Opt,doublebName='AK8Puppijet0_deepdoubleb').addPlots(plots)
            bkgSamples['SingleTop'] = normSampleContainer('SingleTop',tfiles['SingleTop'], 1, DBTMIN,lumi,False,False,'1',False, iSplit = i_split, maxSplit = max_split, puOpt=pu_Opt,doublebName='AK8Puppijet0_deepdoubleb').addPlots(plots)
            bkgSamples['Diboson']   = normSampleContainer('Diboson',tfiles['Diboson'], 1, DBTMIN,lumi,False,False,'1',False, iSplit = i_split, maxSplit = max_split, puOpt=pu_Opt,doublebName='AK8Puppijet0_deepdoubleb').addPlots(plots)
            bkgSamples['QCD']       = normSampleContainer('QCD',tfiles['QCD'], 1, DBTMIN,lumi,False,False,'1',False, iSplit = i_split, maxSplit = max_split, puOpt=pu_Opt,doublebName='AK8Puppijet0_deepdoubleb').addPlots(plots)
        elif year=='2016':
            bkgSamples['W']  = sampleContainer('W',tfiles['W'], 1, DBTMIN,lumi,False,False,'1',False, iSplit = i_split, maxSplit = max_split,puOpt=pu_Opt)
            bkgSamples['DY']  = sampleContainer('DY',tfiles['DY'], 1, DBTMIN,lumi,False,False,'1',False, iSplit = i_split, maxSplit = max_split,puOpt=pu_Opt)
            bkgSamples['TTbar']  = sampleContainer('TTbar',tfiles['TTbar'], 1, DBTMIN,lumi,False,False,'1',False, iSplit = i_split, maxSplit = max_split,puOpt=pu_Opt)
            bkgSamples['SingleTop'] = sampleContainer('SingleTop',tfiles['SingleTop'], 1, DBTMIN,lumi,False,False,'1',False, iSplit = i_split, maxSplit = max_split,puOpt=pu_Opt)
            bkgSamples['Diboson'] = sampleContainer('Diboson',tfiles['Diboson'], 1, DBTMIN,lumi,False,False,'1',False, iSplit = i_split, maxSplit = max_split,puOpt=pu_Opt)
            bkgSamples['QCD'] = sampleContainer('QCD',tfiles['QCD'], 1, DBTMIN,lumi,False,False,'1',False, iSplit = options.iSplit, maxSplit = options.maxSplit,puOpt=pu_Opt)

        if isData and muonCR:
            if year=='2017' or year=='2018':
                bkgSamples['Wlnu']  = normSampleContainer('Wlnu',tfiles['Wlnu'], 1, DBTMIN,lumi,False,False,'1',False, iSplit = i_split, maxSplit = max_split, puOpt=pu_Opt,doublebName='AK8Puppijet0_deepdoubleb').addPlots(plots)
                bkgSamples['DYll']  = normSampleContainer('DYll',tfiles['DYll'], 1, DBTMIN,lumi,False,False,'1',False, iSplit = i_split, maxSplit = max_split, puOpt=pu_Opt,doublebName='AK8Puppijet0_deepdoubleb').addPlots(plots) 
            elif year =='2016':
                bkgSamples['Wlnu']  = sampleContainer('Wlnu',tfiles['Wlnu'], 1, DBTMIN,lumi,False,False,'1',False, iSplit = i_split, maxSplit = max_split,puOpt=pu_Opt)
                bkgSamples['DYll']  = sampleContainer('DYll',tfiles['DYll'], 1, DBTMIN,lumi,False,False,'1',False, iSplit = i_split, maxSplit = max_split,puOpt=pu_Opt)

        if isData:
            print "Data..."
        if isData and muonCR:
            #Muon CR
            if year=='2017' or year=='2018':
                dataSample = sampleContainer('muon',tfiles['muon'], 1, DBTMIN,lumi, isData, False, '((triggerBits&1)&&passJson)',False, iSplit = i_split, maxSplit = max_split,puOpt=pu_Opt,doublebName='AK8Puppijet0_deepdoubleb')
            elif year=='2016':
                dataSample = sampleContainer('muon',tfiles['muon'], 1, DBTMIN,lumi, isData, False, '((triggerBits&4)&&passJson)',False, iSplit = i_split, maxSplit = max_split,puOpt=pu_Opt)
        elif isData:
            if year=='2017':
                triggerNames={"version":"zprimebit-15.01","branchName":"triggerBits",
                          "names":[
                               "HLT_AK8PFJet330_PFAK8BTagCSV_p17_v*",
                               "HLT_PFHT1050_v*",
                               "HLT_AK8PFJet400_TrimMass30_v*",
                               "HLT_AK8PFJet420_TrimMass30_v*",
                               "HLT_AK8PFHT800_TrimMass50_v*",
                               "HLT_PFJet500_v*",
                               "HLT_AK8PFJet500_v*"],
                      }
                dataSample = sampleContainer('data',tfiles['data'], 1, DBTMIN,lumi, isData, False, "passJson", False, iSplit = i_split, maxSplit = max_split,puOpt=pu_Opt, triggerNames=triggerNames,doublebName='AK8Puppijet0_deepdoubleb')
            elif year=='2018':
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
                dataSample = sampleContainer('data',tfiles['data'], 1, DBTMIN,lumi, isData, False, "passJson", False, iSplit = i_split, maxSplit = max_split,puOpt=pu_Opt,triggerNames=triggerNames,doublebName='AK8Puppijet0_deepdoubleb')
            elif year=='2016':
                dataSample = sampleContainer('data',tfiles['data'], 1, DBTMIN,lumi, isData, False, '((triggerBits&2)&&passJson)',False, iSplit = i_split, maxSplit = max_split,puOpt=pu_Opt)
        
        ofile = ROOT.TFile.Open(odir+'/Plots_1000pb_weighted_%s.root '%i_split,'recreate')

        normSamples =['QCD','DY','W','Wlnu','ggHbb','ggHbb_amc','ggHbb_amcHpT250','ggHbb_NNLOPS','VHbb','VBFHbb','ttHbb','TTbar','SingleTop','Diboson','DYll']
        hall_byproc = {}
        for process, s in sigSamples.iteritems():
            hall_byproc[process] = {}
        for process, s in bkgSamples.iteritems():
            hall_byproc[process] = {}
        if isData:
            if muonCR:
                hall_byproc['muon'] = {}
            else:
                hall_byproc['data'] = {}

        for plot in plots:
            for process, s in sigSamples.iteritems():
                if (year=='2017' or year=='2018') and process in normSamples:
                    hall_byproc[process][plot] = sigSamples[process][plot]   #get plot from normSampleContainer
                else:
                    hall_byproc[process][plot] = getattr(s,plot)
            for process, s in bkgSamples.iteritems():
                if (year=='2017' or year=='2018') and process in normSamples:
                    hall_byproc[process][plot] = bkgSamples[process][plot]   #get plot from normSampleContainer
                else:
                    hall_byproc[process][plot] = getattr(s,plot)
            if isData:
                if muonCR:      
                    hall_byproc['muon'][plot] = getattr(dataSample,plot)
                else:
                    hall_byproc['data'][plot] = getattr(dataSample,plot)
            
        ofile.cd()
        for proc, hDict in hall_byproc.iteritems():
            for plot, h in hDict.iteritems():
                print proc, plot
                h.Write()
        
        for plot in plots:
            hs = {}
            hb = {}
            hall={}
            hd = None
            for process, s in sigSamples.iteritems():
                if (year=='2017' or year=='2018') and process in normSamples:
                    hs[process]  =sigSamples[process][plot]   #get plot from normSampleContainer
                    hall[process]=sigSamples[process][plot]   #get plot from normSampleContainer
                else:
                    hs[process]   = getattr(s,plot)
                    hall[process] = getattr(s,plot)
            for process, s in bkgSamples.iteritems():
                if (year=='2017' or year=='2018') and process in normSamples:
                    hb[process]   =bkgSamples[process][plot]   #get plot from normSampleContainer 
                    hall[process] =bkgSamples[process][plot]   #get plot from normSampleContainer 
                else:
                    hb[process] = getattr(s,plot)
                    hall[process] = getattr(s,plot)
            if isData:
                hd = getattr(dataSample,plot)
            #makePlots(plot,hs,hb,hd,hall,legname,color,style,isData,odir,lumi,ofile,canvases)
    
        ofile.Close()
    else:        
        sigSamples = ['ggHbb','VBFHbb','VHbb','ttHbb']        
        bkgSamples = ['QCD','SingleTop','Diboson','W','DY']                      
        if isData and muonCR:
#            bkgSamples.extend(['Wlnu','DYll','TTbar1Mu','TTbar1Ele','TTbar1Tau','TTbar0Lep','TTbar2Lep'])
            bkgSamples.extend(['Wlnu','DYll','TTbar'])
        else:        
            bkgSamples.extend(['TTbar'])
            
        ofile = ROOT.TFile.Open(odir+'/Plots_1000pb_weighted.root','read')
        for plot in plots:
            hb = {}
            hs = {}
            hall = {}
            hd = None
            for process in bkgSamples:
                hb[process] = ofile.Get(plot.replace('h_','h_%s_'%process))
                hall[process] = ofile.Get(plot.replace('h_','h_%s_'%process))
            for process in sigSamples:
                hs[process] = ofile.Get(plot.replace('h_','h_%s_'%process))
                hall[process] = ofile.Get(plot.replace('h_','h_%s_'%process))
            if isData and muonCR:
                hd = ofile.Get(plot.replace('h_','h_muon_'))
            elif isData:
                hd = ofile.Get(plot.replace('h_','h_data_'))
            print plot
            makePlots(plot,hs,hb,hd,hall,legname,color,style,isData,muonCR,odir,lumi,ofile,canvases)
        


##----##----##----##----##----##----##
if __name__ == '__main__':

    parser = OptionParser()
    parser.add_option('-b', action='store_true', dest='noX', default=False, help='no X11 windows')
    parser.add_option("--lumi", dest="lumi", default = 35.9,type=float,help="luminosity", metavar="lumi")
    parser.add_option('-i','--idir', dest='idir', default = 'data/',help='directory with data', metavar='idir')
    parser.add_option('-o','--odir', dest='odir', default = 'plots/',help='directory to write plots', metavar='odir')
    parser.add_option('-s','--isData', action='store_true', dest='isData', default =False,help='signal comparison', metavar='isData')
    parser.add_option('-m','--muonCR', action='store_true', dest='muonCR', default =False,help='for muon CR', metavar='muonCR')
    parser.add_option('-y' ,'--year', type='choice', dest='year', default ='2017',choices=['2016','2017','2018'],help='switch to use different year ', metavar='year')
    parser.add_option("--max-split", dest="maxSplit", default=1, type="int", help="max number of jobs", metavar="maxSplit")
    parser.add_option("--i-split"  , dest="iSplit", default=0, type="int", help="job number", metavar="iSplit")

    (options, args) = parser.parse_args()

     
    import tdrstyle
    tdrstyle.setTDRStyle()
    ROOT.gStyle.SetPadTopMargin(0.10)
    ROOT.gStyle.SetPadLeftMargin(0.16)
    ROOT.gStyle.SetPadRightMargin(0.10)
    #ROOT.gStyle.SetPalette(1)
    ROOT.gStyle.SetPaintTextFormat("1.1f")
    ROOT.gStyle.SetOptFit(0000)
    ROOT.gROOT.SetBatch()

    
    outputExists = False
    if glob.glob(options.odir+'/Plots_1000pb_weighted.root'):
        outputExists = True
        
    main(options,args,outputExists)
    print "All done"
##----##----##----##----##----##----##




