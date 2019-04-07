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

##############################################################################
def main(options,args):
    lumi = options.lumi
    odir = options.odir
    i_split = options.iSplit
    max_split = options.maxSplit
    idir_1501skim = '/eos/uscms/store/user/lpcbacon/dazsle/zprimebits-v15.01/skim/'
        
    legname = {
	       'ggHbb': 'ggH(b#bar{b})',
               'ggHbb_amc': 'ggH(b#bar{b}) aMC@NLO',
               'VBFHbb':'VBF H(b#bar{b})',
	       'ZHbb': ' Z(q#bar{q})H(b#bar{b})',
	       'ZnnHbb': ' Z(#nu#nu)H(b#bar{b})',
	       'WHbb': 'W(q#bar{q})H(b#bar{b})',
	       'ttHbb': 'ttH(b#bar{b})'
               }
    
    tfiles = {'ggHbb_amc' :  { 'GluGluHToBB_M125_13TeV_amcatnloFXFX_pythia8':                glob.glob(idir_1501skim+'GluGluHToBB_M125_13TeV_amcatnloFXFX_pythia8_*.root')},
        'ggHbb_amcHpT250' :  { 'GluGluHToBB_M125_LHEHpT_250_Inf_13TeV_amcatnloFXFX_pythia8' : glob.glob(idir_1501skim+'GluGluHToBB_M125_LHEHpT_250_Inf_13TeV_amcatnloFXFX_pythia8_*.root')},
              'ggHbb'     :          { 'GluGluHToBB_M125_13TeV_powheg_pythia8':                      glob.glob(idir_1501skim+'/GluGluHToBB_M125_13TeV_powheg_pythia8_*.root')},
              'VBFHbb'    :          { 'VBFHToBB_M_125_13TeV_powheg_pythia8_weightfix':              glob.glob(idir_1501skim+'/VBFHToBB_M_125_13TeV_powheg_pythia8_weightfix_*.root')},
              'ZnnHbb'      :          { 
            'ZH_HToBB_ZToNuNu_M125_13TeV_powheg_pythia8':            glob.glob(idir_1501skim+'/ZH_HToBB_ZToQQ_M125_13TeV_powheg_pythia8_*.root'),
            },
              'ZHbb' : {
            'ZH_HToBB_ZToQQ_M125_13TeV_powheg_pythia8':              glob.glob(idir_1501skim+'/ZH_HToBB_ZToQQ_M125_13TeV_powheg_pythia8_*.root'),
            'ggZH_HToBB_ZToQQ_M125_13TeV_powheg_pythia8':            glob.glob(idir_1501skim+'/ggZH_HToBB_ZToQQ_M125_13TeV_powheg_pythia8_*.root'),
            },
              'WHbb' : {
            'WminusH_HToBB_WToQQ_M125_13TeV_powheg_pythia8':         glob.glob(idir_1501skim+'/WminusH_HToBB_WToQQ_M125_13TeV_powheg_pythia8_*.root'),
            'WplusH_HToBB_WToQQ_M125_13TeV_powheg_pythia8':          glob.glob(idir_1501skim+'/WplusH_HToBB_WToQQ_M125_13TeV_powheg_pythia8_*.root'),
            },
              'ttHbb'    :          { 'ttHTobb_M125_TuneCP5_13TeV_powheg_pythia8':           glob.glob(idir_1501skim+'/ttHTobb_M125_TuneCP5_13TeV_powheg_pythia8_*.root')},
              }
    
    color = {
             'ggHbb': ROOT.kBlue+2,
             'ggHbb_amc': ROOT.kGreen+2,
             'VBFHbb': ROOT.kAzure+3,
             'ZnnHbb': ROOT.kPink+5,
	     'ZHbb': ROOT.kPink+1,
	     'WHbb': ROOT.kAzure+1,	
	     'ttHbb': ROOT.kOrange+1,
               }

    style = {
	     'ggHbb': 1,
             'ggHbb_amc': 1,
             'VBFHbb': 2,
	     'ZHbb': 1,
	     'WHbb':1,
             'ZnnHbb': 1,
	     'ttHbb':1,		
             }
    
    plots = [
        'h_n_ak4'           ,
        'h_met'             ,
        'h_pt_ak8'          ,
        'h_pt_ak8_dbtagCut' ,
        'h_msd_ak8'         ,
        'h_msd_ak8_dbtagCut',
        'h_msd_ak8_t21ddtCut'  ,
        'h_msd_ak8_N2Cut'   ,
        'h_dbtag_ak8'       ,
        'h_t21ddt_ak8'      ,
        'h_t32_ak8'         ,
        'h_t32_ak8_t21ddtCut'  ,
        'h_n2b1sd_ak8'      ,
        'h_n2b1sdddt_ak8'   ,
        'h_pt_bbleading' ,
        'h_bb_bbleading' ,
        'h_msd_bbleading',
        'h_msd_ak8_inc',
        'h_msd_ak8_raw',
        'h_msd_ak8_topR6_N2_pass',
        'h_msd_ak8_topR6_N2_fail',
        'h_rho_ak8',
        'h_maxAK4_dcsvb',
        'h_n_ak4M'
        ]

        
    print("Signals... ")
    sigSamples = {}
    pu_Opt  = {'data':"2017"}
    sigSamples['ggHbb']  = normSampleContainer('ggHbb',tfiles['ggHbb']  , 1, DBTMIN,lumi,False,False,'1',False, iSplit = i_split, maxSplit = max_split,puOpt=pu_Opt,doublebName='AK8Puppijet0_deepdoubleb').addPlots(plots)
    #sigSamples['ggHbb_amc']  = normSampleContainer('ggHbb_amc',tfiles['ggHbb_amc']  , 1, DBTMIN,lumi,False,False,'1',False, iSplit = i_split, maxSplit = max_split,puOpt=pu_Opt,doublebName='AK8Puppijet0_deepdoubleb').addPlots(plots)
    sigSamples['VBFHbb']  = normSampleContainer('VBFHbb',tfiles['VBFHbb']  , 1, DBTMIN,lumi,False,False,'1',False, iSplit = i_split, maxSplit = max_split,puOpt=pu_Opt,doublebName='AK8Puppijet0_deepdoubleb').addPlots(plots)
    sigSamples['ZHbb']  = normSampleContainer('ZHbb',tfiles['ZHbb']  , 1, DBTMIN,lumi,False,False,'1',False, iSplit = i_split, maxSplit = max_split,puOpt=pu_Opt,doublebName='AK8Puppijet0_deepdoubleb').addPlots(plots)
    sigSamples['WHbb']  = normSampleContainer('WHbb',tfiles['WHbb']  , 1, DBTMIN,lumi,False,False,'1',False, iSplit = i_split, maxSplit = max_split,puOpt=pu_Opt,doublebName='AK8Puppijet0_deepdoubleb').addPlots(plots)
    sigSamples['ttHbb']  = normSampleContainer('ttHbb',tfiles['ttHbb']  , 1, DBTMIN,lumi,False,False,'1',False, iSplit = i_split, maxSplit = max_split,puOpt=pu_Opt,doublebName='AK8Puppijet0_deepdoubleb').addPlots(plots)
    sigSamples['ZnnHbb']  = normSampleContainer('ZnnHbb',tfiles['ZnnHbb']  , 1, DBTMIN,lumi,False,False,'1',False, iSplit = i_split, maxSplit = max_split,puOpt=pu_Opt,doublebName='AK8Puppijet0_deepdoubleb').addPlots(plots)

    ofile = ROOT.TFile.Open(odir+'/Plots_1000pb_weighted.root','recreate')
    
    for plot in plots:
        hs = {}
        for process in sigSamples.keys():
            hs[process] = sigSamples[process][plot]
        c = makeCanvasComparison(hs,legname,color,style,plot.replace('h_','signalcomparison_'),odir,lumi)
        ofile.cd()
        for process, h in hs.iteritems():
            h.Write()        
        c.Write()

    ofile.Close()

##----##----##----##----##----##----##
if __name__ == '__main__':

    parser = OptionParser()
    parser.add_option('-b', action='store_true', dest='noX', default=False, help='no X11 windows')
    parser.add_option("--lumi", dest="lumi", type=float,default = 41.1,help="luminosity", metavar="lumi")
    parser.add_option('-i','--idir', dest='idir', default = 'data/',help='directory with data', metavar='idir')
    parser.add_option('-o','--odir', dest='odir', default = 'plots/',help='directory to write plots', metavar='odir')
    parser.add_option("--max-split", dest="maxSplit", default=1, type="int", help="max number of jobs", metavar="maxSplit")
    parser.add_option("--i-split"  , dest="iSplit", default=0, type="int", help="job number", metavar="iSplit")
    parser.add_option("--double-b-name"  , dest="doublebName", default="AK8Puppijet0_deepdoubleb", help="double-b name", metavar="doublebName")
    parser.add_option("--double-b-cut"  , dest="doublebCut", default=0.89, type="float", help="double-b cut", metavar="doublebCut")

    (options, args) = parser.parse_args()

     
    import tdrstyle
    tdrstyle.setTDRStyle()
    ROOT.gStyle.SetPadTopMargin(0.10)
    ROOT.gStyle.SetPadLeftMargin(0.16)
    ROOT.gStyle.SetPadRightMargin(0.10)
    ROOT.gStyle.SetPalette(1)
    ROOT.gStyle.SetPaintTextFormat("1.1f")
    ROOT.gStyle.SetOptFit(0000)
    ROOT.gROOT.SetBatch()
    
    main(options,args)
##----##----##----##----##----##----##




