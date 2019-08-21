#!/usr/bin/env python
import ROOT as r, sys, math, os
from ROOT import TFile, TTree, TChain, gPad, gDirectory
from multiprocessing import Process
from optparse import OptionParser
from operator import add
import math
import sys
import time
import array

#r.gSystem.Load("~/Dropbox/RazorAnalyzer/python/lib/libRazorRun2.so")
r.gSystem.Load(os.getenv('CMSSW_BASE') + '/lib/' + os.getenv('SCRAM_ARCH') + '/libHiggsAnalysisCombinedLimit.so')

# including other directories
# sys.path.insert(0, '../.')
from tools import *
from hist import *

MASS_BINS = 23
MASS_LO = 40       # mass range for RooVar
MASS_HI = 201
MASS_HIST_LO = 47   # mass range for histograms
MASS_HIST_HI = 201
BLIND_LO = 110
BLIND_HI = 131
RHO_LO = -6
RHO_HI = -2.1

SF2018={
            #cristina July8
            'shift_SF'  : 0.970,           'shift_SF_ERR' : 0.012,
            'smear_SF'  : 0.9076,          'smear_SF_ERR' : 0.0146,
            'V_SF'      : 0.953,           'V_SF_ERR'     : 0.016,  
            #'smear_SF'  : 0.952,            'smear_SF_ERR' : 0.0495  , # prelim SF @26% N2ddt 
            #'V_SF'      : 0.845,            'V_SF_ERR'     : 0.031   , # prelim SF @26% N2ddt
            #'BB_SF'     : 0.7,              'BB_SF_ERR' : 0.065,      #2018 prelim ddb SF
            #'BB_SF'     : 0.77,             'BB_SF_ERR' : 0.07,     ## M2 SF
            'BB_SF'     : 1.0,             'BB_SF_ERR' : 0.3,     ## M2 SF
}
SF2017={
            #cristina July8
            'shift_SF'  : 0.978,           'shift_SF_ERR' : 0.012,
            'smear_SF'  : 0.9045,          'smear_SF_ERR' : 0.048,
            'V_SF'      : 0.924,           'V_SF_ERR'  : 0.018,  
            #cristina Jun25
            #'shift_SF'  : 0.979,           'shift_SF_ERR' : 0.012,
            #'smear_SF'  : 0.911,           'smear_SF_ERR' : 0.0476,
            #'V_SF'      : 0.92,            'V_SF_ERR'     : 0.018,  
            #'smear_SF'  : 1.037,            'smear_SF_ERR' : 0.049   , # prelim SF @26% N2ddt 

            #'shift_SF'  : 1.001,            'shift_SF_ERR' : 0.0044   , # 2016 shift SF 
            #'smear_SF'  : 1.084,            'smear_SF_ERR' : 0.0905  , #  2016 smear SF 
            #'V_SF'      : 0.993,            'V_SF_ERR'  : 0.043,       # 2016 VSF
            #'shift_SF'  : 1.00,            'shift_SF_ERR' : 0.01   , # prelim SF @26% N2ddt 
            #'shift_SF'  : 1.00,             'shift_SF_ERR' : 0.03   , # prelim SF @26% N2ddt 
            #'V_SF'      : 0.95 ,            'V_SF_ERR'     : 0.02   , # prelim SF @26% N2ddt
            #'BB_SF'     : 0.68,             'BB_SF_ERR' : 0.06       , # prelim ddb SF
            'BB_SF'     : 1.0,             'BB_SF_ERR' : 0.3        , # prelim ddb SF
            #'BB_SF'     : 0.77,             'BB_SF_ERR' : 0.07,     ## M2 SF
}
SF2016={
            #'m_data'    : 82.657,           'm_data_err': 0.313,
            #'m_mc'      : 82.548,           'm_mc_err'  : 0.191,
            #'s_data'    : 8.701,            's_data_err': 0.433,
            #'s_mc'      : 8.027,            's_mc_err'  : 0.607,
            #'BB_SF'     : 0.68,             'BB_SF_ERR' : 0.15,     ## T2 SF
            #'BB_SF'     : 0.77,             'BB_SF_ERR' : 0.07,     ## M2 SF
            'BB_SF'     : 1.0,             'BB_SF_ERR' : 0.23,     ## M2 SF
            'V_SF'      : 0.993,            'V_SF_ERR'  : 0.043,
            'shift_SF'  : 1.001,            'shift_SF_ERR' : 0.012   , # m_data/m_mc, sqrt((m_data_err/m_data)**2+(m_mc_err/m_mc)**2)
            #'shift_SF'  : 1.001,            'shift_SF_ERR' : 0.044   , # m_data/m_mc, sqrt((m_data_err/m_data)**2+(m_mc_err/m_mc)**2)
            'smear_SF'  : 1.084,            'smear_SF_ERR' : 0.0905  , # s_data/s_mc, sqrt((s_data_err/s_data)**2+(s_mc_err/s_mc)**2)
        }
#==================== ddb_Apr17/ddb_M2/msd47_TF21/card_rhalphabet_all_floatZ.root ====================
#qcdeff =  0.0153 +/- 0.0000 
#p0r0 =  -0.7085  +/- 0.0529 
#p0r1 =  2.2649   +/- 0.0350 
#p0r2 =  0.7067   +/- 0.0155 
#p1r0 =  1.1266   +/- 0.0919 
#p1r1 =  1.7097   +/- 0.1284 
#p1r2 =  -0.8651  +/- 0.0997 

#==================== ddb_Jun24_v2/ddb_M2_full/TF22_MC_w2Fit/card_rhalphabet_all_2017_floatZ.root ====================
#qcdeff_2017 =  0.0151  +/- 0.0000 
#p0r0_2017   =  -1.0359 +/- 0.1669 
#p0r1_2017   =  2.3953  +/- 0.1000 
#p0r2_2017   =  0.7093  +/- 0.0362 
#p1r0_2017   =  1.0947  +/- 0.3854 
#p1r1_2017   =  1.6930  +/- 0.3269 
#p1r2_2017   =  -0.1745 +/- 0.1725 
#p2r0_2017   =  0.1980  +/- 0.4379 
#p2r1_2017   =  1.4567  +/- 0.5200 
#p2r2_2017   =  -0.0427 +/- 0.4857 

#==================== ddb2016_Jun24_v2/ddb_M2_full/TF22_MC_w2Fit/card_rhalphabet_all_2016_floatZ.root ====================
#qcdeff_2016 =  0.0145 +/- 0.0000 
#p0r0_2016   =  -1.0136 +/- 0.3498 
#p0r1_2016   =  2.3427 +/- 0.2129 
#p0r2_2016   =  0.6987 +/- 0.0783 
#p1r0_2016   =  0.8998 +/- 0.7414 
#p1r1_2016   =  2.4030 +/- 0.6171 
#p1r2_2016   =  -0.7088 +/- 0.3288 
#p2r0_2016   =  0.6278 +/- 0.8229 
#p2r1_2016   =  1.1812 +/- 0.9868 
#p2r2_2016   =  0.1521 +/- 0.9433 
#==================== ddb2016_Jun24_v3/ddb_M2_full/TF22_MC_w2Fit/card_rhalphabet_all_2016_floatZ.root ====================
#qcdeff_2016 =  0.0145 +/- 0.0000 
#p0r0_2016 =  -1.1068 +/- 0.1544 
#p0r1_2016 =  2.4223 +/- 0.0937 
#p0r2_2016 =  0.6320 +/- 0.0323 
#p1r0_2016 =  1.3960 +/- 0.3358 
#p1r1_2016 =  2.1129 +/- 0.2936 
#p1r2_2016 =  -0.3538 +/- 0.1520 
#p2r0_2016 =  0.0473 +/- 0.3804 
#p2r1_2016 =  1.3758 +/- 0.4746 
#p2r2_2016 =  -0.1053 +/- 0.4365 
#==================== ddb2018_Jun24_v3/ddb_M2_full/TF22_MC_w2Fit/card_rhalphabet_all_2018_floatZ.root ====================
#qcdeff_2018 =  0.0139 +/- 0.0000 
#p0r0_2018 =  -0.9680 +/- 0.1666 
#p0r1_2018 =  2.3695 +/- 0.1017 
#p0r2_2018 =  0.6775 +/- 0.0382 
#p1r0_2018 =  1.0759 +/- 0.3846 
#p1r1_2018 =  1.4427 +/- 0.3313 
#p1r2_2018 =  0.1826 +/- 0.1843 
#p2r0_2018 =  0.2077 +/- 0.4334 
#p2r1_2018 =  1.8612 +/- 0.5152 
#p2r2_2018 =  -0.8737 +/- 0.4928 


############## TF21s#######################
#==================== ddb2016_Jun24_v3/ddb_M2_full/TF21_MC_w2Fit/card_rhalphabet_all_2016_floatZ.root ====================
#qcdeff_2016 = 0.0144 +/- 0.0000 
#p0r0_2016 =  -0.7777 +/- 0.1012 
#p0r1_2016 =  2.3120  +/- 0.0676 
#p0r2_2016 =  0.6491  +/- 0.0265 
#p1r0_2016 =  1.3179  +/- 0.1327 
#p1r1_2016 =  2.1454  +/- 0.1989 
#p1r2_2016 =  -1.2233 +/- 0.1560 
#==================== ddb_Jun24_v2/ddb_M2_full/TF21_MC_w2Fit/card_rhalphabet_all_2017_floatZ.root ====================
#qcdeff_2017 =  0.0151 +/- 0.0000 
#p0r0_2017 =  -0.7472 +/- 0.1019 
#p0r1_2017 =  2.2678 +/- 0.0672 
#p0r2_2017 =  0.7198 +/- 0.0283 
#p1r0_2017 =  1.1505 +/- 0.1126 
#p1r1_2017 =  1.7452 +/- 0.1785 
#p1r2_2017 =  -0.9013 +/- 0.1570 
#==================== ddb2018_Jun24_v3/ddb_M2_full/TF21_MC_w2Fit/card_rhalphabet_all_2018_floatZ.root ====================
#qcdeff_2018 =  0.0139 +/- 0.0000 
#p0r0_2018 =  -0.7232 +/- 0.1037 
#p0r1_2018 =  2.2527 +/- 0.0704 
#p0r2_2018 =  0.7066 +/- 0.0306 
#p1r0_2018 =  1.2450 +/- 0.1200 
#p1r1_2018 =  1.4251 +/- 0.1879 
#p1r2_2018 =  -0.6247 +/- 0.1706 

#qcdTFpars_2017={'n_rho':2, 'n_pT':2,
#            'pars':[ 0.0151 , -1.0359, 2.3953 , 0.7093 , 1.0947 , 1.6930 , -0.1745, 0.1980 , 1.4567 , -0.0427]}
#qcdTFpars_2016={'n_rho':2, 'n_pT':2,
#            'pars':[ 0.0144,-1.0856,2.4440 ,0.6407 ,1.3394 ,1.8660 ,-0.4000,0.1670 ,1.7287 ,-0.1297]} ## v2
#qcdTFpars_2018={'n_rho':2, 'n_pT':2,
#            'pars':[0.0139,-0.9680,2.3695 ,0.6775 ,1.0759 ,1.4427 ,0.1826 ,0.2077 ,1.8612 ,-0.8737]}

qcdTFpars_2016={'n_rho':2, 'n_pT':1,
            'pars':[ 0.0144, -0.7777, 2.3120 , 0.6491 , 1.3179 , 2.1454 , -1.2233]}
qcdTFpars_2017={'n_rho':2, 'n_pT':1,
            'pars':[ 0.0151 ,-0.7472,2.2678 ,0.7198 ,1.1505 ,1.7452 ,-0.9013 ]}
qcdTFpars_2018={'n_rho':2, 'n_pT':1,
            'pars':[0.0139,-0.7232,2.2527 ,0.7066 ,1.2450 ,1.4251 ,-0.6247]}

#2016  T2pt350to2000, WPcut=0.92, SF= 0.68  +0.20/-0.10
#2016  M2pt350to2000, WPcut=0.89, SF= 0.77  +0.11/-0.04

#2017  M2pt350to2000, WPcut=0.89, SF= 0.68  +0.05/-0.07
#2018  M2pt350to2000, WPcut=0.89, SF= 0.70  +0.07/-0.06
def main(options, args):
    ifile = options.ifile
    odir = options.odir

    print "loading default rhalphabet_builder"
    from rhalphabet_builder import RhalphabetBuilder, LoadHistograms, GetSF
    # Load the input histograms
    # 	- 2D histograms of pass and fail mass,pT distributions
    # 	- for each MC sample and the data
    f = r.TFile.Open(ifile)    
    fLoose = None
    qcdTFpars = {}
    if options.ifile_loose is not None:
        fLoose = r.TFile.Open(options.ifile_loose)
    if   options.year =='2018':
          sf=SF2018
          if not options.pseudo:    qcdTFpars = qcdTFpars_2018 
    elif options.year =='2017':
          sf=SF2017
          if not options.pseudo:    qcdTFpars = qcdTFpars_2017
    elif options.year =='2016':
          sf=SF2016
          if not options.pseudo:    qcdTFpars = qcdTFpars_2016

    #(hpass, hfail) = loadHistograms(f, options.pseudo, options.blind, options.useQCD, options.scale, options.r)
    (pass_hists,fail_hists) = LoadHistograms(f, options.pseudo, options.blind, options.useQCD, scale=options.scale, r_signal=options.r, mass_range=[MASS_HIST_LO, MASS_HIST_HI], blind_range=[BLIND_LO, BLIND_HI], rho_range=[RHO_LO,RHO_HI], fLoose=fLoose,sf_dict=sf,createPassFromFail=options.createPassFromFail,skipQCD=options.skipQCD)
    #f.Close()

    # Build the workspacees
    #dazsleRhalphabetBuilder(hpass, hfail, f, odir, options.NR, options.NP)

    rhalphabuilder = RhalphabetBuilder(pass_hists, fail_hists, f, options.odir, nr=options.NR, np=options.NP, mass_nbins=MASS_BINS, mass_lo=MASS_LO, mass_hi=MASS_HI, blind_lo=BLIND_LO, blind_hi=BLIND_HI, rho_lo=RHO_LO, rho_hi=RHO_HI, blind=options.blind, mass_fit=options.massfit, freeze_poly=options.freeze, remove_unmatched=options.removeUnmatched, input_file_loose=fLoose,suffix=options.suffix,sf_dict=sf,mass_hist_lo=MASS_HIST_LO,mass_hist_hi=MASS_HIST_HI,qcdTFpars=qcdTFpars,exp=options.exp,multi=options.multi,pseudo=options.pseudo)
    rhalphabuilder.run()
    if options.addHptShape:
        rhalphabuilder.addHptShape()	
    if options.prefit:
        rhalphabuilder.prefit()
    elif options.loadfit is not None:
        rhalphabuilder.loadfit(options.loadfit)
        

##-------------------------------------------------------------------------------------
if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option('-b', action='store_true', dest='noX', default=False, help='no X11 windows')
    parser.add_option('-i', '--ifile', dest='ifile', default='hist_1DZbb.root', help='file with histogram inputs',
                      metavar='ifile')
    parser.add_option('--ifile-loose', dest='ifile_loose', default=None, help='second file with histogram inputs (looser b-tag cut to take W/Z/H templates)',
                      metavar='ifile_loose')
    parser.add_option('-o', '--odir', dest='odir', default='./', help='directory to write plots', metavar='odir')
    parser.add_option('--pseudo', action='store_true', dest='pseudo', default=False, help='use MC', metavar='pseudo')
    parser.add_option('--blind', action='store_true', dest='blind', default=False, help='blind signal region',
                      metavar='blind')
    parser.add_option('--use-qcd', type='int', dest='useQCD', default=1, help='use real QCD MC',
                      metavar='useQCD')
    parser.add_option('--massfit', action='store_true', dest='massfit', default=False, help='mass fit or rho',
                      metavar='massfit')
    parser.add_option('--exp', action='store_true', dest='exp', default=False, help='use exp(bernstein poly) transfer function',
                      metavar='exp')
    parser.add_option('--multi', action='store_true', dest='multi', default=False, help='define RooMultiPdf',
                      metavar='multi')
    parser.add_option('--freeze', action='store_true', dest='freeze', default=False, help='freeze pol values',
                      metavar='freeze')
    parser.add_option('--scale', dest='scale', default=1, type='float',
                      help='scale factor to scale MC (assuming only using a fraction of the data)')
    parser.add_option('--nr', dest='NR', default=2, type='int', help='order of rho (or mass) polynomial')
    parser.add_option('--np', dest='NP', default=1, type='int', help='order of pt polynomial')
    parser.add_option('-r', dest='r', default=1, type='float', help='signal strength for MC pseudodataset')
    parser.add_option('--remove-unmatched', action='store_true', dest='removeUnmatched', default =False,help='remove unmatched', metavar='removeUnmatched')
    parser.add_option('--prefit', action='store_true', dest='prefit', default =False,help='do prefit', metavar='prefit')
    parser.add_option('--addHptShape',action='store_true',dest='addHptShape',default =False,help='add H pt shape unc', metavar='addHptShape')
    parser.add_option('--loadfit', dest='loadfit', default=None, help='load qcd polynomial parameters from alternative rhalphabase.root',metavar='loadfit')
    parser.add_option('-y' ,'--year', type='choice', dest='year', default ='2016',choices=['2016','2017','2018'],help='switch to use different year ', metavar='year')
    parser.add_option('--suffix', dest='suffix', default='', help='suffix for conflict variables',metavar='suffix')
    parser.add_option('--createPassFromFail', action='store_true', dest='createPassFromFail', default=False, help='Creating data_obs pass from data_obs fail', metavar='createPassFromFail')
    parser.add_option('--skipQCD', action='store_true', dest='skipQCD', default=False, help='skipQCD MC template', metavar='skipQCD')

    (options, args) = parser.parse_args()

    import tdrstyle

    tdrstyle.setTDRStyle()
    r.gStyle.SetPadTopMargin(0.10)
    r.gStyle.SetPadLeftMargin(0.16)
    r.gStyle.SetPadRightMargin(0.10)
    r.gStyle.SetPalette(1)
    r.gStyle.SetPaintTextFormat("1.1f")
    r.gStyle.SetOptFit(0000)
    r.gROOT.SetBatch()

    main(options, args)
##-------------------------------------------------------------------------------------
