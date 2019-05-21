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
from controlPlotsGGH import get2017files

DBTMIN=-99
#

##############################################################################
def main(options,args):
    lumi = options.lumi
    odir = options.odir
    i_split = options.iSplit
    max_split = options.maxSplit
        
    legname = {'ggHbb': 'ggH(b#bar{b})',
               'ggHbb_amc': 'ggH(b#bar{b}) aMC@NLO',
	       'ZHbb': ' Z(q#bar{q})H(b#bar{b})',
	       'ZnnHbb': ' Z(#nu#nu)H(b#bar{b})',
	       'WHbb': 'W(q#bar{q})H(b#bar{b})',
	       'ttHbb': 't#bar{t}H(b#bar{b})',
               'Hbb': 'H(b#bar{b})',
               'VBFHbb':'VBF H(b#bar{b})',
               'VHbb': 'VH(b#bar{b})',
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
               }
    
    color = {
             'ggHbb': ROOT.kBlue+2,
             'ggHbb_amc': ROOT.kGreen+2,
             'VBFHbb': ROOT.kAzure+3,
             'ZnnHbb': ROOT.kPink+5,
	     'ZHbb': ROOT.kPink+1,
	     'WHbb': ROOT.kAzure+1,	
	     'ttHbb': ROOT.kOrange+1,
             'Hbb': ROOT.kRed,
             'VHbb': ROOT.kTeal+1,
             'VBFHbb': ROOT.kBlue-10,
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

    style = {
	     'ggHbb': 1,
             'ggHbb_amc': 1,
             'VBFHbb': 2,
	     'ZHbb': 1,
	     'WHbb':1,
             'ZnnHbb': 1,
	     'ttHbb':1,		
             'Hbb': 1,
             'VHbb': 4,
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
        
    
    plots = [
        'h_Cuts',
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
        ]


    year = "2017"       
    if year=="2017":
        samplefiles   = open(os.path.expandvars("$ZPRIMEPLUSJET_BASE/analysis/ggH/samplefiles.json"),"r")
        tfiles  = json.load(samplefiles)['controlPlotsGGH_2017']
        normfile      = os.path.expandvars("$ZPRIMEPLUSJET_BASE/analysis/ggH/norm_controlPlotsGGH_2017.root")
        pu_Opt  = {'data':"2017",'norm':normfile}
    elif year=='2016':
        tfiles = get2016files()
        pu_Opt  = {'data':"2016",'MC':"12.04"}
    elif year=='2018':
        samplefiles   = open(os.path.expandvars("$ZPRIMEPLUSJET_BASE/analysis/ggH/samplefiles.json"),"r")
        #tfiles  = json.load(samplefiles)['controlPlotsGGH_2018']
        pu_Opt  = {'data':"2018"}
    else:
        print "Invalid choice of year. Aborting"            
        sys.exit()

    #idir_1501skim = '/eos/uscms/store/user/lpcbacon/dazsle/zprimebits-v15.04-vbf/skim/'
    #eos_prefix = 'root://cmseos.fnal.gov/'
    #tfiles_update = {'ggHbb_amc' :  { 'GluGluHToBB_M125_13TeV_amcatnloFXFX_pythia8':                [ eos_prefix+a for a in glob.glob(idir_1501skim+'GluGluHToBB_M125_13TeV_amcatnloFXFX_pythia8_*.root')]},
    #                 'ggHbb_amcHpT250' :  { 'GluGluHToBB_M125_LHEHpT_250_Inf_13TeV_amcatnloFXFX_pythia8' : [eos_prefix+a for a in glob.glob(idir_1501skim+'GluGluHToBB_M125_LHEHpT_250_Inf_13TeV_amcatnloFXFX_pythia8_*.root')]},
    #                 'ggHbb'     :          { 'GluGluHToBB_M125_13TeV_powheg_pythia8':                      [eos_prefix+a for a in glob.glob(idir_1501skim+'/GluGluHToBB_M125_13TeV_powheg_pythia8_*.root')]},
    #                 'VBFHbb'    :          { 'VBFHToBB_M_125_13TeV_powheg_pythia8_weightfix':              [eos_prefix+a for a in glob.glob(idir_1501skim+'/VBFHToBB_M_125_13TeV_powheg_pythia8_weightfix_*.root')]},
    #                 'ZnnHbb'      :          { 
    #        'ZH_HToBB_ZToNuNu_M125_13TeV_powheg_pythia8':            [eos_prefix+a for a in glob.glob(idir_1501skim+'/ZH_HToBB_ZToQQ_M125_13TeV_powheg_pythia8_*.root')],
    #        },
    #                 'ZHbb' : {
    #        'ZH_HToBB_ZToQQ_M125_13TeV_powheg_pythia8':              [eos_prefix+a for a in glob.glob(idir_1501skim+'/ZH_HToBB_ZToQQ_M125_13TeV_powheg_pythia8_*.root')],
    #        'ggZH_HToBB_ZToQQ_M125_13TeV_powheg_pythia8':            [eos_prefix+a for a in glob.glob(idir_1501skim+'/ggZH_HToBB_ZToQQ_M125_13TeV_powheg_pythia8_*.root')],
    #        },
    #                 'WHbb' : {
    #        'WminusH_HToBB_WToQQ_M125_13TeV_powheg_pythia8':         [eos_prefix+a for a in glob.glob(idir_1501skim+'/WminusH_HToBB_WToQQ_M125_13TeV_powheg_pythia8_*.root')],
    #        'WplusH_HToBB_WToQQ_M125_13TeV_powheg_pythia8':          [eos_prefix+a for a in glob.glob(idir_1501skim+'/WplusH_HToBB_WToQQ_M125_13TeV_powheg_pythia8_*.root')],
    #        },
    #                 'ttHbb'    :          { 'ttHTobb_M125_TuneCP5_13TeV_powheg_pythia8':           [eos_prefix+a for a in glob.glob(idir_1501skim+'/ttHTobb_M125_TuneCP5_13TeV_powheg_pythia8_*.root')]},
    #                 })

    print("Signals... ")
    sigSamples = {}
    sigSamples['ggHbb']  = normSampleContainer('ggHbb',tfiles['ggHbb']  , 1, DBTMIN,lumi,False,False,'1',False, iSplit = i_split, maxSplit = max_split,puOpt=pu_Opt,doublebName='AK8Puppijet0_deepdoubleb').addPlots(plots)
    #sigSamples['ggHbb_amc']  = normSampleContainer('ggHbb_amc',tfiles['ggHbb_amc']  , 1, DBTMIN,lumi,False,False,'1',False, iSplit = i_split, maxSplit = max_split,puOpt=pu_Opt,doublebName='AK8Puppijet0_deepdoubleb').addPlots(plots)
    sigSamples['VBFHbb']  = normSampleContainer('VBFHbb',tfiles['VBFHbb']  , 1, DBTMIN,lumi,False,False,'1',False, iSplit = i_split, maxSplit = max_split,puOpt=pu_Opt,doublebName='AK8Puppijet0_deepdoubleb').addPlots(plots)
    sigSamples['VHbb']  = normSampleContainer('VHbb',tfiles['VHbb']  , 1, DBTMIN,lumi,False,False,'1',False, iSplit = i_split, maxSplit = max_split,puOpt=pu_Opt,doublebName='AK8Puppijet0_deepdoubleb').addPlots(plots)
    #sigSamples['ZHbb']  = normSampleContainer('ZHbb',tfiles['ZHbb']  , 1, DBTMIN,lumi,False,False,'1',False, iSplit = i_split, maxSplit = max_split,puOpt=pu_Opt,doublebName='AK8Puppijet0_deepdoubleb').addPlots(plots)
    #sigSamples['WHbb']  = normSampleContainer('WHbb',tfiles['WHbb']  , 1, DBTMIN,lumi,False,False,'1',False, iSplit = i_split, maxSplit = max_split,puOpt=pu_Opt,doublebName='AK8Puppijet0_deepdoubleb').addPlots(plots)
    sigSamples['ttHbb']  = normSampleContainer('ttHbb',tfiles['ttHbb']  , 1, DBTMIN,lumi,False,False,'1',False, iSplit = i_split, maxSplit = max_split,puOpt=pu_Opt,doublebName='AK8Puppijet0_deepdoubleb').addPlots(plots)
    #sigSamples['ZnnHbb']  = normSampleContainer('ZnnHbb',tfiles['ZnnHbb']  , 1, DBTMIN,lumi,False,False,'1',False, iSplit = i_split, maxSplit = max_split,puOpt=pu_Opt,doublebName='AK8Puppijet0_deepdoubleb').addPlots(plots)
    sigSamples['W']         = normSampleContainer('W',tfiles['W'], 1, DBTMIN,lumi,False,False,'1',False, iSplit = i_split, maxSplit = max_split,   puOpt=pu_Opt,doublebName='AK8Puppijet0_deepdoubleb').addPlots(plots)
    sigSamples['DY']        = normSampleContainer('DY',tfiles['DY'], 1, DBTMIN,lumi,False,False,'1',False, iSplit = i_split, maxSplit = max_split, puOpt=pu_Opt,doublebName='AK8Puppijet0_deepdoubleb').addPlots(plots)
    sigSamples['TTbar']     = normSampleContainer('TTbar',tfiles['TTbar'], 1, DBTMIN,lumi,False,False,'1',False, iSplit = i_split, maxSplit = max_split, puOpt=pu_Opt,doublebName='AK8Puppijet0_deepdoubleb').addPlots(plots)
    sigSamples['SingleTop'] = normSampleContainer('SingleTop',tfiles['SingleTop'], 1, DBTMIN,lumi,False,False,'1',False, iSplit = i_split, maxSplit = max_split, puOpt=pu_Opt,doublebName='AK8Puppijet0_deepdoubleb').addPlots(plots)
    sigSamples['Diboson']   = normSampleContainer('Diboson',tfiles['Diboson'], 1, DBTMIN,lumi,False,False,'1',False, iSplit = i_split, maxSplit = max_split, puOpt=pu_Opt,doublebName='AK8Puppijet0_deepdoubleb').addPlots(plots)
    sigSamples['QCD']       = normSampleContainer('QCD',tfiles['QCD'], 1, DBTMIN,lumi,False,False,'1',False, iSplit = i_split, maxSplit = max_split, puOpt=pu_Opt,doublebName='AK8Puppijet0_deepdoubleb').addPlots(plots)


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
    parser.add_option("--lumi", dest="lumi", type=float,default = 41,help="luminosity", metavar="lumi")
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

    os.system('mkdir -p %s'%options.odir)
    
    main(options,args)
##----##----##----##----##----##----##




