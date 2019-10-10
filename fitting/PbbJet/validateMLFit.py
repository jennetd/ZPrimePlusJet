#!/usr/bin/env python

import ROOT as r, sys, math, array, os
from ROOT import TFile, TTree, TChain, gPad, gDirectory, SetOwnership
from multiprocessing import Process
from optparse import OptionParser
from operator import add
import math
import sys
import time
import array
import re,copy
import  bernstein 

# including other directories
# sys.path.insert(0, '../.')
from tools import *

msd_binBoundaries = []
#for i in range(0, 24): msd_binBoundaries.append(40 + i * 7)
for i in range(1, 24): msd_binBoundaries.append(40 + i * 7)
pt_binBoundaries = [450, 500, 550, 600, 675, 800, 1200]
#pt_binBoundaries = [450, 500, 550, 600, 1200]

from buildRhalphabetHbb import BLIND_LO, BLIND_HI, RHO_LO, RHO_HI
BIN_WIDTH = 7

##-------------------------------------------------------------------------------------
def main(options, args):
    mass = 125

    #fml = r.TFile.Open(options.idir + "/mlfit.root", 'read')
    fml = r.TFile.Open(options.idir + "/mlfit_%s.root"%options.suffix.replace(":","_"), 'read')
    fd = r.TFile.Open(options.idir + "/base.root", 'read')
    if 'minlo' in options.idir:
        fbkgUnc = r.TFile.Open('./correlations/bkgUncBands_minlo.root','read')
    else:
        fbkgUnc = r.TFile.Open('./correlations/bkgUncBands.root','read')
    histograms_pass_all = {}
    histograms_fail_all = {}


    #shapes = ['wqq', 'zqq', 'tqq', 'qcd', 'hqq125', 'zhqq125', 'whqq125', 'tthqq125', 'vbfhqq125', 'data']
    #bkgshapes=['wqq', 'zqq', 'tqq', 'qcd']
    #sigshapes=['hqq125', 'zhqq125', 'whqq125', 'tthqq125', 'vbfhqq125']

    shapes = ['wqq', 'zqq', 'tqq', 'qcd', 'ggH_hbb', 'ZH_hbb', 'WH_hbb', 'ttH_hbb', 'qqH_hbb', 'data']
    bkgshapes=['wqq', 'zqq', 'tqq', 'qcd']
    sigshapes=['ggH_hbb', 'ZH_hbb', 'WH_hbb', 'ttH_hbb', 'qqH_hbb']

  
    qcdTFpars_2017={'n_rho':2, 'n_pT':2,
                'pars':[ 0.0151 , -1.0359, 2.3953 , 0.7093 , 1.0947 , 1.6930 , -0.1745, 0.1980 , 1.4567 , -0.0427]}
    qcdTFpars_2016={'n_rho':2, 'n_pT':2,
                'pars':[ 0.0144,-1.0856,2.4440 ,0.6407 ,1.3394 ,1.8660 ,-0.4000,0.1670 ,1.7287 ,-0.1297]} ## v2
    qcdTFpars_2018={'n_rho':2, 'n_pT':2,
                'pars':[0.0139,-0.9680,2.3695 ,0.6775 ,1.0759 ,1.4427 ,0.1826 ,0.2077 ,1.8612 ,-0.8737]} 
    suffixes = options.suffix.split(":")

    for suffix in suffixes:
        #if suffix is '': suffix = 'default'
        histograms_pass_all[suffix] = {}
        histograms_fail_all[suffix] = {}

        for i in range(len(pt_binBoundaries) - 1):
            print i,suffix
            if suffix =='2016': qcdTFpars = qcdTFpars_2016
            elif suffix =='2017': qcdTFpars = qcdTFpars_2017
            elif suffix =='2018': qcdTFpars = qcdTFpars_2018
            ## FIXME: turning qcdTFpars on will spoil the summed cats of fail
            if not options.qcdTF:
                qcdTFpars = {} 
            (tmppass, tmpfail) = plotCategory(fml, fd, i + 1, options.fit,suffix,qcdTFpars,fbkgUnc)
            histograms_pass_all[suffix][i] = {}
            histograms_fail_all[suffix][i] = {}
            for shape in shapes:
                for hist in tmppass:
                    if hist != None and re.match(shape,hist.GetName()): histograms_pass_all[suffix][i][shape] = hist
                for hist in tmpfail:
                    if hist !=None and re.match(shape,hist.GetName()): histograms_fail_all[suffix][i][shape] = hist
    if options.qcdTF:
        sys.exit()

    pass_2d = {}
    fail_2d = {}
    for suffix in suffixes:
        for shape in shapes:
            pass_2d[shape] = r.TH2F('%s_pass_%s_2d' % (shape,suffix), '%s_pass_%s_2d' % (shape,suffix), len(msd_binBoundaries) - 1,
                                    array.array('d', msd_binBoundaries), len(pt_binBoundaries) - 1,
                                    array.array('d', pt_binBoundaries))
            fail_2d[shape] = r.TH2F('%s_fail_%s_2d' % (shape,suffix), '%s_fail_%s_2d' % (shape,suffix), len(msd_binBoundaries) - 1,
                                    array.array('d', msd_binBoundaries), len(pt_binBoundaries) - 1,
                                    array.array('d', pt_binBoundaries))
            for i in range(1, pass_2d[shape].GetNbinsX() + 1):
                for j in range(1, pass_2d[shape].GetNbinsY() + 1):
                    if shape =='data': #data is a TAsymErrorGraph:
                        binCenter = pass_2d[shape].GetXaxis().GetBinCenter(i)
                        pass_2d[shape].SetBinContent(i, j, histograms_pass_all[suffix][j - 1][shape].Eval(binCenter))
                        fail_2d[shape].SetBinContent(i, j, histograms_pass_all[suffix][j - 1][shape].Eval(binCenter))
                    else:
                        if shape in histograms_pass_all[suffix][j - 1].keys(): pass_2d[shape].SetBinContent(i, j, histograms_pass_all[suffix][j - 1][shape].GetBinContent(i))
                        if shape in histograms_fail_all[suffix][j - 1].keys(): fail_2d[shape].SetBinContent(i, j, histograms_fail_all[suffix][j - 1][shape].GetBinContent(i))

    pass_2d_data_subtract = pass_2d['data'].Clone('data_pass_2d_subtract')
    fail_2d_data_subtract = fail_2d['data'].Clone('data_fail_2d_subtract')
    for shape in shapes:
        if shape == 'qcd' or shape == 'data': continue
        pass_2d_data_subtract.Add(pass_2d[shape], -1)
        fail_2d_data_subtract.Add(fail_2d[shape], -1)
    ratio_2d_data_subtract = pass_2d_data_subtract.Clone('ratio_2d_subtract')
    ratio_2d_data_subtract.Divide(fail_2d_data_subtract)

    for i in range(1, ratio_2d_data_subtract.GetNbinsX() + 1):
        for j in range(1, ratio_2d_data_subtract.GetNbinsY() + 1):
            massVal = ratio_2d_data_subtract.GetXaxis().GetBinCenter(i)
            ptVal = ratio_2d_data_subtract.GetYaxis().GetBinLowEdge(j) + ratio_2d_data_subtract.GetYaxis().GetBinWidth(
                j) * 0.3
            rhoVal = r.TMath.Log(massVal * massVal / ptVal / ptVal)
            if rhoVal < RHO_LO or rhoVal > RHO_HI:
                ratio_2d_data_subtract.SetBinContent(i, j, 0)


    qcdeff = 0.015
    for suffix in suffixes:
        rBestFit,pars = getFitPars(fml,options.fit,suffix,qcdeff)

    if len(options.suffix.split(':'))>1:
        bkgUnc_pass        = fbkgUnc.Get('bkgUncBand_pass')
        bkgUnc_fail        = fbkgUnc.Get('bkgUncBand_fail')
    else:
        bkgUnc_pass        = fbkgUnc.Get('bkgUncBand_pass_'+options.suffix)
        bkgUnc_fail        = fbkgUnc.Get('bkgUncBand_fail_'+options.suffix)

    ptCats = range(len(pt_binBoundaries)-1)
    (histograms_pass_summed,histograms_fail_summed) =  sumShapes(shapes,suffixes,ptCats,histograms_pass_all,histograms_fail_all)
    plotSummedShapes(shapes,bkgshapes,sigshapes,rBestFit,'allcats_%s'%options.suffix.replace(":","_"),histograms_pass_summed,histograms_fail_summed,bkgUnc_pass,bkgUnc_fail)
    if len(suffixes)>1:
        for ipt in ptCats:
            bkgUnc_pass        = fbkgUnc.Get('bkgUncBand_pass_cat%s'%(ipt+1))
            bkgUnc_fail        = fbkgUnc.Get('bkgUncBand_fail_cat%s'%(ipt+1))
            (histograms_pass_summed,histograms_fail_summed) =  sumShapes(shapes,suffixes,[ipt],histograms_pass_all,histograms_fail_all)
            plotSummedShapes(shapes,bkgshapes,sigshapes,rBestFit,'sumcat%s'%(ipt+1),histograms_pass_summed,histograms_fail_summed,bkgUnc_pass,bkgUnc_fail)
        

    # Plot TF poly
    #includeQCDeff = True
    #makeTF(pars, ratio_2d_data_subtract,options.NR,options.NP,includeQCDeff)
    #includeQCDeff = False
    #makeTF(pars, ratio_2d_data_subtract,options.NR,options.NP,includeQCDeff)

    #print "sum ",histograms_pass_summed_list[0:4], histograms_pass_summed_list[9], histograms_pass_summed_list[4:9]
 
##  returns g1 = g1+g2, There is no TGraph::Add. 
def AddGraphs(g1,g2):
    (x1,y1) = (r.Double(), r.Double())
    (x2,y2) = (r.Double(), r.Double())
    alpha = 1-0.6827
    for ipt in range(0,g1.GetN()):
        g1.GetPoint(ipt,x1,y1)
        g2.GetPoint(ipt,x2,y2)
        N = y1 +y2
        ey1h = g1.GetEYhigh()[ipt]
        ey2h = g2.GetEYhigh()[ipt]
        ey1l = g1.GetEYlow()[ipt]
        ey2l = g2.GetEYlow()[ipt]
        if options.isData:
            #g1.SetPointEYlow(ipt, (N-L))
            #g1.SetPointEYhigh(ipt, (U-N))
            g1.SetPointEYlow(ipt, (ey1l**2+ey2l**2)**0.5)     #Add errors from density
            g1.SetPointEYhigh(ipt, (ey1h**2+ey2h**2)**0.5)
        else:
            g1.SetPointEYlow( ipt, N**0.5)
            g1.SetPointEYhigh(ipt, N**0.5)
        g1.SetPoint(ipt,x1,N)
        g1.SetPointEXlow(ipt,0)
        g1.SetPointEXhigh(ipt,0)
 
### Sum all the shapes for all [suffixes] and [ptCats] in histograms_pass_all,histograms_fail_all
def sumShapes(shapes,suffixes,ptCats,histograms_pass_all,histograms_fail_all): 
    histograms_pass_summed = {}
    histograms_fail_summed = {}
    #Sum all cats for each shapes, for each suffix
    for shape in shapes:
        suffix0 = suffixes[0]
        pt0     = ptCats[0]
        if not shape in histograms_pass_all[suffix0][pt0].keys(): continue
        histograms_pass_summed[shape] = histograms_pass_all[suffix0][pt0][shape].Clone(shape + '_pass_sum')
        for suffix in suffixes:
            for i in  ptCats:
                if i==pt0 and suffix==suffix0:
                    print suffix,shape,i, histograms_pass_summed[shape].Integral()
                    continue
                if not shape in histograms_pass_all[suffix][i].keys(): continue
                print suffix,shape,i, histograms_pass_summed[shape].Integral(), " + ", histograms_pass_all[suffix][i][shape].Integral()
                if shape=='data':
                    #print "before add data:",histograms_pass_summed[shape].Print()
                    AddGraphs(histograms_pass_summed[shape], histograms_pass_all[suffix][i][shape])
                    #print "AFter add data:",histograms_pass_summed[shape].Print()
                else:
                    histograms_pass_summed[shape].Add(histograms_pass_all[suffix][i][shape])
                print "= ",histograms_pass_summed[shape].Integral()

        #    print suffix, shape, histograms_pass_summed[shape].Integral()
        #print 'total', shape, histograms_pass_summed[shape].Integral()

    for shape in shapes:
        suffix0 = suffixes[0]
        pt0     = ptCats[0]
        if not shape in histograms_fail_all[suffix0][pt0].keys(): continue
        histograms_fail_summed[shape] = histograms_fail_all[suffix0][pt0][shape].Clone(shape + '_fail_sum')
        for suffix in suffixes:
            for i in  ptCats:
                if i==pt0 and suffix==suffix0:                    continue ##Avoid double counting
                if not shape in histograms_fail_all[suffix][i].keys(): continue
                if shape=='data':
                    AddGraphs(histograms_fail_summed[shape], histograms_fail_all[suffix][i][shape])
                else:
                    histograms_fail_summed[shape].Add(histograms_fail_all[suffix][i][shape])

    return (histograms_pass_summed,histograms_fail_summed)

def plotSummedShapes(shapes,bkgshapes,sigshapes,rBestFit,tag,histograms_pass_summed,histograms_fail_summed,bkgUnc_pass,bkgUnc_fail):
    ## sort histograms into bkg sig and data
    histograms_pass_summed_list = {"bkg":[],"sig":[]}
    histograms_fail_summed_list = {"bkg":[],"sig":[]}
    for shape in shapes:
        if shape in histograms_pass_summed.keys():
            if shape in bkgshapes:
                histograms_pass_summed_list['bkg'].append(histograms_pass_summed[shape])
            if shape in sigshapes:
                histograms_pass_summed_list['sig'].append(histograms_pass_summed[shape])
            if shape in ['data']:
                histograms_pass_summed_list['data']=histograms_pass_summed[shape]
            
        if shape in histograms_fail_summed.keys():
            if shape in bkgshapes:
                histograms_fail_summed_list['bkg'].append(histograms_fail_summed[shape])
            if shape in sigshapes:
                histograms_fail_summed_list['sig'].append(histograms_fail_summed[shape])
            if shape in ['data']:
                histograms_fail_summed_list['data']=histograms_fail_summed[shape]
 
    [histograms_pass_summed_list] = makeMLFitCanvas(histograms_pass_summed_list['bkg'], histograms_pass_summed_list['data'],
                                                    histograms_pass_summed_list['sig'], shapes,
                                                    "pass_%s_"%tag + options.fit, options.odir, rBestFit,
                                                    options.sOverSb, options.splitS, options.ratio,bkgUnc_pass)
    [histograms_fail_summed_list] = makeMLFitCanvas(histograms_fail_summed_list['bkg'], histograms_fail_summed_list['data'],
                                                    histograms_fail_summed_list['sig'], shapes,
                                                    "fail_%s_"%tag + options.fit, options.odir, rBestFit,
                                                    options.sOverSb, options.splitS, options.ratio,bkgUnc_fail)

def getFitPars(fml,fitType,suffix,qcdeff=0.01):
    rBestFit = 1
    # print out fit results
    if fitType == "fit_b" or fitType == "fit_s":
        rfr = r.RooFitResult(fml.Get(fitType))
        lParams = []
        #lParams.append("qcdeff")
        # for r2p1 polynomial
        if suffix is not "":
            lParams.append("p0r0_"+suffix)
            lParams.append("p0r1_"+suffix)  
            lParams.append("p0r2_"+suffix)  
            lParams.append("p1r0_"+suffix)  
            lParams.append("p1r1_"+suffix)  
            lParams.append("p1r2_"+suffix)
            lParams.append("p2r0_"+suffix)  
            lParams.append("p2r1_"+suffix)  
            lParams.append("p2r2_"+suffix)
        else:
            lParams.append("p0r0")
            lParams.append("p0r1")  
            lParams.append("p0r2")  
            lParams.append("p1r0")  
            lParams.append("p1r1")  
            lParams.append("p1r2")


        pars = [qcdeff]
        for p in lParams:
            if rfr.floatParsFinal().find(p):
                print p, "=", rfr.floatParsFinal().find(p).getVal(), "+/-", rfr.floatParsFinal().find(p).getError()
                pars.append(rfr.floatParsFinal().find(p).getVal())
            else:
                print p, "not found"
                pars.append(0)
        if fitType == 'fit_s':
            rBestFit = rfr.floatParsFinal().find('r').getVal()
        else:
            rBestFit = 0

    return (rBestFit,pars)

def plotCategory(fml, fd, index, fittype,suffix="",qcdTFpars={},fbkgUnc=None):
    shapes = ['wqq', 'zqq', 'tqq', 'qcd', 'ggH_hbb', 'ZH_hbb', 'WH_hbb', 'ttH_hbb', 'qqH_hbb']
    bkgshapes=['wqq', 'zqq', 'tqq', 'qcd']
    sigshapes=['ggH_hbb', 'ZH_hbb', 'WH_hbb', 'ttH_hbb', 'qqH_hbb']

    histograms_fail = []
    histograms_pass = []

    rBestFit = 1
    if fittype == "fit_b" or fittype == "fit_s":
        rfr = r.RooFitResult(fml.Get(options.fit))
        if options.fit == 'fit_s':
            rBestFit = rfr.floatParsFinal().find('r').getVal()
        else:
            rBestFit = 0
       
    pass_cat_name = "_".join(filter(None,["cat%i"%index,suffix,"pass","cat%i"%index]))
    fail_cat_name = "_".join(filter(None,["cat%i"%index,suffix,"fail","cat%i"%index]))
    if fbkgUnc is not None:
        bkgUnc_pass        = fbkgUnc.Get('bkgUncBand_pass_'+suffix+'_cat%i'%index)
        bkgUnc_fail        = fbkgUnc.Get('bkgUncBand_fail_'+suffix+'_cat%i'%index)
    else:
        bkgUnc_pass        = None 
        bkgUnc_fail        = None 

    for i, ish in enumerate(bkgshapes+sigshapes):
        if i < 4:
            fitdir = fittype
        else:
            # fitdir = "prefit"
            fitdir = fittype
        # print fitdir+"/cat%i_fail_cat%i/%s" % (index,index,ish)

        histograms_fail.append(fml.Get("shapes_" + fitdir + "/%s/%s" % (fail_cat_name, ish)))
        histograms_pass.append(fml.Get("shapes_" + fitdir + "/%s/%s" % (pass_cat_name, ish)))
        # print fitdir
        rags = fml.Get("norm_" + fitdir)
        # rags.Print()


        print "finding rrv with name = %s/%s, %s/%s" % (pass_cat_name, ish,fail_cat_name,ish)
        if rags.find("%s/%s" % (fail_cat_name, ish)) != None:
          rrv_fail = r.RooRealVar(rags.find("%s/%s" % (fail_cat_name, ish)))
          curnorm_fail = rrv_fail.getVal()
        else:
            print " rrv with name = %s/%s is null" % (fail_cat_name, ish)
            curnorm_fail = 0
        if  rags.find("%s/%s" % (pass_cat_name, ish)) != None:
          rrv_pass = r.RooRealVar(rags.find("%s/%s" % (pass_cat_name, ish)))
          curnorm_pass = rrv_pass.getVal()
        else:
            curnorm_pass = 0
            print " rrv with name = %s/%s is null" % (pass_cat_name, ish)
	
        if curnorm_fail > 0.: histograms_fail[i].Scale(curnorm_fail / histograms_fail[i].Integral())
        if curnorm_pass > 0.: histograms_pass[i].Scale(curnorm_pass / histograms_pass[i].Integral())

   # wp = fd.Get("w_pass_cat%i" % (index))
   # wf = fd.Get("w_fail_cat%i" % (index))
   # rdhp = wp.data("data_obs_pass_cat%i" % (index))
   # rdhf = wf.data("data_obs_fail_cat%i" % (index))
   # rrv = wp.var("x")

   # data_fail = rdhf.createHistogram("data_fail_cat" + str(index) + "_" + fittype, rrv,
   #                                  r.RooFit.Binning(histograms_pass[0].GetNbinsX()))
   # data_pass = rdhp.createHistogram("data_pass_cat" + str(index) + "_" + fittype, rrv,
   #                                  r.RooFit.Binning(histograms_pass[0].GetNbinsX()))
    data_density_pass =fml.Get("shapes_" + fitdir + "/%s/data" % (pass_cat_name))
    data_density_fail =fml.Get("shapes_" + fitdir + "/%s/data" % (fail_cat_name))

    def getGraphFromDensity(g):
        gClone = g.Clone(g.GetName()+"_copy")
        alpha = 1-0.6827
        for i in range(0,gClone.GetN()):
            N = gClone.GetY()[i]*BIN_WIDTH
            L = 0
            if N!=0:
                L = r.Math.gamma_quantile(alpha/2,N,1.)
            U = r.Math.gamma_quantile_c(alpha/2,N+1,1)

            eyh = gClone.GetErrorYhigh(i)
            eyl = gClone.GetErrorYlow(i)
            gClone.SetPoint(i,gClone.GetX()[i], N)
            if options.isData:
                gClone.SetPointEYhigh(i, (N-L))
                gClone.SetPointEYlow(i, (U-N))  
            else:
                gClone.SetPointEYhigh(i, eyh*BIN_WIDTH)
                gClone.SetPointEYlow(i, eyl*BIN_WIDTH)
            gClone.SetPointEXhigh(i,0) 
            gClone.SetPointEXlow(i, 0)
        return gClone
    
    data_pass = getGraphFromDensity(data_density_pass)
    data_fail = getGraphFromDensity(data_density_fail)


    # if index==4:
    #    data_fail.SetBinContent(13,(data_fail.GetBinContent(12)+data_fail.GetBinContent(14))/2.)
    histograms_fail.append(data_fail)
    histograms_pass.append(data_pass)

    (bkg_fail,sig_fail) = ([],[])
    (bkg_pass,sig_pass) = ([],[])

    for i,ish in enumerate(bkgshapes+sigshapes):
        if ish in bkgshapes:
            if histograms_fail[i] !=None: bkg_fail.append(histograms_fail[i])
            if histograms_pass[i] !=None: bkg_pass.append(histograms_pass[i])
        if ish in sigshapes:
            if histograms_fail[i] !=None: sig_fail.append(histograms_fail[i])
            if histograms_pass[i] !=None: sig_pass.append(histograms_pass[i])

    [histograms_fail] = makeMLFitCanvas(bkg_fail, data_fail, sig_fail, shapes,
                                        "fail_cat" + str(index) + "_%s_"%suffix + fittype, options.odir, rBestFit,
                                        options.sOverSb, options.splitS, options.ratio,bkgUnc_fail)
    [histograms_pass] = makeMLFitCanvas(bkg_pass, data_pass, sig_pass, shapes,
                                        "pass_cat" + str(index) + "_%s_"%suffix + fittype, options.odir, rBestFit,
                                        options.sOverSb, options.splitS, options.ratio,bkgUnc_pass)
    if qcdTFpars!={}:
        bkg_pass_qcdfail    = copy.deepcopy(bkg_pass)
        ## qcd position is 3
        hqcd = bkg_fail[3]
        f2params    = array.array('d', qcdTFpars['pars'])
        npar        = len(f2params)
        boundaries={}
        boundaries['RHO_LO']=-6.
        boundaries['RHO_HI']=-2.1
        boundaries['PT_LO' ]= 450.
        boundaries['PT_HI' ]= 1200.
        if   index == 1 : pt = 465.0
        elif index == 2 : pt = 515.0
        elif index == 3 : pt = 565.0
        elif index == 4 : pt = 622.5 
        elif index == 5 : pt = 712.5
        elif index == 6 : pt = 920.0

        f_bernstein = bernstein.genBernsteinTF1D(qcdTFpars['n_rho'],qcdTFpars['n_pT'],pt,boundaries,IsMsdPt=True,qcdeff=True,rescale=True)
        tf2   = r.TF1("f2", f_bernstein, 40,201,npar)
        tf2.SetParameters(f2params)
        for ibin in range(1,hqcd.GetNbinsX()+1):
            mass   = hqcd.GetBinCenter(ibin)
            qcdeff = tf2.Eval(mass)
            hqcd.SetBinContent(ibin,  qcdeff * hqcd.GetBinContent(ibin))
            hqcd.SetBinError(ibin,  qcdeff * hqcd.GetBinContent(ibin)**0.5)
            #hqcd.SetBinContent(ibin,  f2params[0] * hqcd.GetBinContent(ibin))
            #hqcd.SetBinError(ibin,  f2params[0] * hqcd.GetBinContent(ibin)**0.5
        
        bkg_pass_qcdfail[3] = hqcd
        makeMLFitCanvas(bkg_pass_qcdfail, data_pass, sig_pass, shapes,
                                        "failTF_cat" + str(index) + "_%s_"%suffix + fittype, options.odir, rBestFit,
                                        options.sOverSb, options.splitS, options.ratio)


    return (histograms_pass, histograms_fail)


###############################################################
def weightBySOverSpB(bkgs, data, hsigs, tag):
    wB = 0.
    wS = 0.
    for i in range(10, 14):  # 110-131 H mass window; #1,data.GetNbinsX()+1):
        for b in bkgs:
            wB += b.GetBinContent(i)
        for s in hsigs:
            wS += s.GetBinContent(i)
    if ('allcats' or 'sumcat') in tag:
        Z = 1
    else:
        Z = wS / (wS + wB)  # math.sqrt(wS+wB)
        print(Z, wS, wB)
    for h in bkgs + hsigs:
        h.Scale(Z)
    for i in range(0,data.GetN()):
        data.SetPoint(i , data.GetX()[i], (data.GetY()[i])*Z)
        eyh = data.GetErrorYhigh(i)
        eyl = data.GetErrorYlow(i)
        data.SetPointEYhigh(i, eyh * Z)
        data.SetPointEYlow(i, eyl * Z)

    weight = wS / (wS + wB)  # math.sqrt(wS+wB)
    return [bkgs, data, hsigs, weight]


def makeMLFitCanvas(bkgs, data, hsigs, leg, tag, odir='cards', rBestFit=1, sOverSb=False, splitS=True, ratio=False,bkgUnc=None):
    weight = 1
    if sOverSb:
        [bkgs, data, hsigs, weight] = weightBySOverSpB(bkgs, data, hsigs, tag)

    c = r.TCanvas("c%s" % tag, "c%s" % tag, 800, 800)
    SetOwnership(c, False)
    p12 = r.TPad("p12%s" % tag, "p12%s" % tag, 0.0, 0.3, 1.0, 1.0)
    p22 = r.TPad("p22%s" % tag, "p22%s" % tag, 0.0, 0.0, 1.0, 0.3)
    p12.SetBottomMargin(0.02)
    p22.SetTopMargin(0.05)
    p22.SetBottomMargin(0.3)

    c.cd()
    p12.Draw()
    p12.cd()

    h = r.TH1F("h", "AK8 m_{SD} (GeV);", 23, 40, 201)
    htot = bkgs[0].Clone("htot%s" % tag)
    hqcd = bkgs[3].Clone("hqcd%s" % tag)

    if options.showWZinRatio: 
        hqcd.Add(bkgs[2])       #subtract ttbar only
    else:
        hqcd.Add(bkgs[0])       #subtract ttbar 
        hqcd.Add(bkgs[1])       #subtract zqq 
        hqcd.Add(bkgs[2])       #subtract wqq 
    htotsig = bkgs[0].Clone("htotsig%s" % tag)
    htotsig.SetLineColor(r.kBlack)
    htotsig.SetFillStyle(3001)
    htotsig.SetFillColor(r.kPink + 3)
    htotsig.SetLineColor(r.kPink + 3)
    htotsig.SetLineWidth(2)
    # htotsig.Draw("")
    for ih in range(1, len(bkgs)):
        htot.Add(bkgs[ih])
        htotsig.Add(bkgs[ih])
    hsig = hsigs[0].Clone("hsig%s" % tag)
    for ih in range(1, len(hsigs)):
        if hsigs[ih] !=None:
            hsig.Add(hsigs[ih])
            htotsig.Add(hsigs[ih])

    colors = [r.kGreen + 2, r.kRed + 1, r.kMagenta + 3, r.kGray + 2, r.kPink + 7]
    sigcolor = [r.kPink + 7, r.kPink + 1, r.kAzure + 1, r.kOrange + 1, r.kAzure + 3]
    sleg = ['GF H(b#bar{b})', 'Z(q#bar{q})H(b#bar{b})', 'W(q#bar{q})H(b#bar{b})', 'ttH(b#bar{b})', 'VBF H(b#bar{b})']
    style = [2, 3, 4, 2, 2]
    for i, b in enumerate(bkgs):
        #	b.SetFillColor(colors[i])
        b.SetLineColor(colors[i])
        b.SetLineStyle(style[i])
        b.SetLineWidth(2)

    if 'fit_b' not in tag:
        l = r.TLegend(0.6, 0.55, 0.75, 0.85)
    elif splitS:
        l = r.TLegend(0.6, 0.4, 0.75, 0.85)
    else:
        l = r.TLegend(0.6, 0.5, 0.75, 0.85)
    l.SetFillStyle(0)
    l.SetBorderSize(0)
    l.SetTextFont(42)
    l.SetTextSize(0.037)
    legnames = {'wqq': 'W', 'zqq': 'Z', 'qcd': 'Multijet', 'tqq': 't#bar{t}'}
    for i in range(len(bkgs)):
        l.AddEntry(bkgs[i], legnames[leg[i]], "l")
    if bkgUnc is not None:
        l.AddEntry(bkgUnc, "Total background", "lf")
    else:
        l.AddEntry(htot, "Total background", "lf")
    # l.AddEntry(htotsig,"Total Bkg. + Sig.","lf")
    if 'fit_b' not in tag:
        if splitS:
            for ih in range(0, len(hsigs)):
                hsigs[ih].SetLineColor(sigcolor[ih])
                l.AddEntry(hsigs[ih], sleg[ih], "lf")
        else:
            l.AddEntry(hsig, "H(b#bar{b})", "lf")


    l.AddEntry(data, "Data", "pe")

    htot.SetLineColor(r.kBlack)
    htot.SetFillStyle(3001)
    htot.SetFillColor(r.kAzure - 5)
    htot.SetLineColor(r.kAzure - 5)
    htotsig.SetLineColor(r.kPink + 3)
    # htotsig.SetFillStyle(3001)
    htotsig.SetFillColor(r.kPink+3)
    htotsig.SetLineColor(r.kPink + 3)
    htotsig.SetLineWidth(2)

    data.SetMinimum(0)
    htot.SetMarkerSize(0)
    htot.SetMarkerColor(r.kGray + 2)
    htot.SetLineWidth(2)
    data.SetMarkerStyle(r.kFullDotLarge)
    
    def getDataGraphFromHist(h_data):    
        g_data = r.TGraphAsymmErrors(h_data)    
        alpha = 1-0.6827
        for i in range(0,g_data.GetN()):
            N = g_data.GetY()[i]
            L = 0
            if N!=0:
                L = r.Math.gamma_quantile(alpha/2,N,1.)
            U = r.Math.gamma_quantile_c(alpha/2,N+1,1)
            if options.isData:
                g_data.SetPointEYlow(i, (N-L))
                g_data.SetPointEYhigh(i, (U-N))
            else:
                g_data.SetPointEYlow( i, h_data.GetBinError(i+1))
                g_data.SetPointEYhigh(i, h_data.GetBinError(i+1))
            g_data.SetPointEXlow( i, 0)
            g_data.SetPointEXhigh(i, 0)
            g_data.SetPoint(i, g_data.GetX()[i], N)
        return g_data
 
    #g_data = getDataGraphFromHist(data)
    #g_data = data.Clone("g_data")
    g_data = data

    maximum = htot.GetMaximum()    
    htot.GetXaxis().SetTitle('m_{SD} (GeV)')
    htot.GetYaxis().SetTitle('Events / 7 GeV')
    htot.GetYaxis().SetTitleSize(0.06)
    htot.GetYaxis().SetLabelSize(0.05)
    htot.GetYaxis().SetTitleOffset(1.25)

    htot.SetFillStyle(0)
    htot.SetLineStyle(1)
    htot.Draw('hist')
    if 'cat1' in tag:
        htot.GetXaxis().SetRangeUser(min(msd_binBoundaries),max(msd_binBoundaries) - 7*5)
    elif 'cat2' in tag:
        htot.GetXaxis().SetRangeUser(min(msd_binBoundaries),max(msd_binBoundaries) - 7*3)
    else:
        htot.GetXaxis().SetRangeUser(min(msd_binBoundaries),max(msd_binBoundaries))
        
    htot_line = htot.Clone('htot_line%s' % tag)
    htot_line.SetFillStyle(0)
    #htot_line.Draw('histsame')
    htotsig_line = htotsig.Clone('htotsig_line%s' % tag)
    htotsig_line.SetFillStyle(0)
    # htotsig_line.Draw('histsame')
    hstackMC = r.THStack("hstackMC","hstackMC")

    def mysort(v):
        name = v.GetName()
        if 'tqq' in name:
            return 0
        elif 'qcd' in name:
            return 1
        elif 'wqq' in name: 
            return 2
        elif 'zqq' in name:
            return 3
        elif 'ggH' in name:
            return 4
        elif 'Sbb' in name:
            return 5
        else:
            return 6

    for b in sorted(bkgs,key=mysort):
        if 'qcd' in b.GetName():
            b.Draw('hist sames')
            #hstackMC.Add(b)
        else:
            hstackMC.Add(b)
    hsig.SetLineColor(r.kPink + 7)
    hsig.SetFillColor(r.kPink + 7)
    # hsig.SetLineStyle(2)
    #hsig.SetLineWidth(1)
    if not splitS:
        hstackMC.Add(hsig)
        #hsig.Draw('hist sames')
    else:
        for ih in range(0, len(hsigs)):
            hstackMC.Add(hsigs[ih])	
            #hsigs[ih].Draw('hist sames')
    if bkgUnc is not None:
        bkgUnc.Draw("E2 same")
        pass
    else:
        htot.Draw('E2same')
    hstackMC.Draw("hist sames")
    g_data.Draw('pezsame')
    l.Draw()
    tag1 = r.TLatex(0.67, 0.92, "%.1f fb^{-1} (13 TeV)" % options.lumi)
    tag1.SetNDC()
    tag1.SetTextFont(42)
    tag1.SetTextSize(0.045)
    tag2 = r.TLatex(0.2, 0.82, "CMS")
    tag2.SetNDC()
    tag2.SetTextFont(62)
    if options.isData:
        tag3 = r.TLatex(0.2, 0.77, "Preliminary")
    else:
        tag3 = r.TLatex(0.2, 0.77, "Simulation Preliminary")

        
    ptRange = [450, 1200]
    if 'cat1' in tag:
        ptRange = [450, 500]
    elif 'cat2' in tag:
        ptRange = [500, 550]
    elif 'cat3' in tag:
        ptRange = [550, 600]
    elif 'cat3' in tag:
        ptRange = [550, 600]
    elif 'cat4' in tag:
        ptRange = [600, 675]
        if "vbf" in options.suffix:
            ptRange = [600, 1200]
    elif 'cat5' in tag:
        ptRange = [675, 800]
    elif 'cat6' in tag:
        ptRange = [800, 1200]
        
    passTag = 'Deep double-b tagger'
    passTag2 = 'Passing region'
    if 'fail' in tag:
        passTag = 'Deep double-b tagger'
        passTag2 = 'Failing region'

    tag4 = r.TLatex(0.25, 0.77, "%i < p_{T} < %i GeV"%(ptRange[0],ptRange[1]))
    tag4b = r.TLatex(0.25, 0.72, "%s"%(passTag))
    tag4c = r.TLatex(0.25, 0.67, "%s"%(passTag2))
    #tag4 = r.TLatex(0.36, 0.81, "%i < p_{T} < %i GeV"%(ptRange[0],ptRange[1]))
    #tag4b = r.TLatex(0.36, 0.75, "%s"%(passTag))
    #tag4c = r.TLatex(0.36, 0.69, "%s"%(passTag2))
    tag4.SetNDC()
    tag4.SetTextFont(42)
    tag4b.SetNDC()
    tag4b.SetTextFont(42)
    tag4c.SetNDC()
    tag4c.SetTextFont(42)
    tag3.SetNDC()
    tag3.SetTextFont(52)
    tag2.SetTextSize(0.055)
    tag3.SetTextSize(0.045)
    tag4.SetTextSize(0.038)
    tag4b.SetTextSize(0.038)
    tag4c.SetTextSize(0.038)
    tag1.Draw()
    tag2.Draw()
    #tag3.Draw()
    tag4.Draw()
    tag4b.Draw()
    tag4c.Draw()
    htot.SetMaximum(maximum * 1.5)


    c.cd()
    p22.Draw()
    p22.cd()
    # p22.SetGrid()

    iRatio = h.Clone('iRatio%s' % tag)
    maxdata=1	
    mindata=10	
    if ratio:
        iRatioGraph = r.TGraphAsymmErrors(iRatio)
        alpha = 1 - 0.6827
        print iRatio.GetNbinsX()
        for i in range(0, iRatio.GetNbinsX()):
            N = g_data.GetY()[i] 
            L = 0
            if N != 0:
                L = r.Math.gamma_quantile(alpha / 2, N, 1.)
            U = r.Math.gamma_quantile_c(alpha / 2, N + 1, 1)
            iRatioGraph.SetPointEYlow(i, (N - L) / htot.GetBinContent(i + 1) * weight)
            iRatioGraph.SetPointEYhigh(i, (U - N) / htot.GetBinContent(i + 1) * weight)
            iRatioGraph.SetPointEXlow(i, 0)
            iRatioGraph.SetPointEXhigh(i, 0)
            iRatioGraph.SetPoint(i, iRatioGraph.GetX()[i], N / htot.GetBinContent(i + 1) * weight)
    else:	
        for i in range(iRatio.GetNbinsX()):
            #if hqcd.GetBinContent(i + 1) > 0:
            if g_data.GetY()[i] > 0:
                x,y = (r.Double(),r.Double())
                #value_data = data.GetBinContent(i + 1)
                g_data.GetPoint(i,x,y)
                value_data = y  
                value_fit = hqcd.GetBinContent(i + 1)                
                err_low_data = g_data.GetEYlow()[i]
                err_high_data = g_data.GetEYhigh()[i]
                err_tot_data = 0
                if (value_fit > value_data):
                    err_tot_data = err_high_data  
                else:
                    err_tot_data = err_low_data
                iRatio.SetBinContent(i + 1, (value_data - value_fit) / err_tot_data)
		if (value_data - value_fit) / err_tot_data > maxdata : maxdata = (value_data - value_fit) / err_tot_data
		if (value_data - value_fit) / err_tot_data < mindata : mindata = (value_data - value_fit) / err_tot_data
		
                iRatio.SetBinError(i + 1, 1)  # data.GetBinError(i+1)+hqcd.GetBinError(i+1) )
        iRatioGraph = r.TGraphAsymmErrors(iRatio)
        for i in range(iRatio.GetNbinsX()):
            iRatioGraph.SetPointEXlow(i, 0)
            iRatioGraph.SetPointEXhigh(i, 0)

    iOneWithErrors = htot.Clone('iOneWithErrors%s' % tag)
    htot.GetXaxis().SetTitleOffset(100)
    htot.GetXaxis().SetLabelOffset(100)    
    if ratio:
        iOneWithErrors.SetTitle("; m_{SD} (GeV); Data/Prediction")
    else:
        if options.showWZinRatio:
            iOneWithErrors.SetTitle("; m_{SD} (GeV); #frac{Data #minus (Multijet + t#bar{t})}{#sigma_{Data}}")
        else:
            iOneWithErrors.SetTitle("; m_{SD} (GeV); #frac{Data #minus Bkg}{#sigma_{Data}}")
    iOneWithErrors.SetMaximum(1.5)
    iOneWithErrors.SetMinimum(0.)
    iOneWithErrors.GetYaxis().SetTitleSize(0.1)
    iOneWithErrors.GetYaxis().SetNdivisions(6)
    iOneWithErrors.GetYaxis().SetLabelSize(0.12)
    iOneWithErrors.GetYaxis().SetTitleOffset(0.7)
    iOneWithErrors.GetXaxis().SetTitleSize(0.13)
    iOneWithErrors.GetXaxis().SetLabelSize(0.12)
    iOneWithErrors.GetXaxis().SetTitleOffset(0.9)

    if ratio:
        iOneWithErrors.Divide(htot.Clone())
        for i in range(iOneWithErrors.GetNbinsX()):
            # print i+1, htot.GetBinContent(i+1)
            if htot.GetBinContent(i + 1) > 0. and g_data.GetY()[i] > 0.:
                #iOneWithErrors.SetBinError(i + 1, htot.GetBinError(i + 1) / htot.GetBinContent(i + 1))
                iOneWithErrors.SetBinError(i + 1,  bkgUnc.GetBinError(i+1) / htot.GetBinContent(i + 1))
            else:
                iOneWithErrors.SetBinError(i + 1, 0)
    else:
        iOneWithErrors.Add((-1) * htot.Clone())
        for i in range(iOneWithErrors.GetNbinsX()):
            err_tot_data =  (g_data.GetEYlow()[i]+g_data.GetEYhigh()[i])/2
            iOneWithErrors.SetBinError(i+1, bkgUnc.GetBinError(i+1)/err_tot_data )
    iOneWithErrors.SetFillStyle(3001)
    if ratio: 
        iOneWithErrors.SetFillColor(r.kAzure - 5)
        iOneWithErrors.SetLineColor(r.kAzure - 5)
    else :
        iOneWithErrors.SetLineColor(r.kAzure -5 )
        iOneWithErrors.SetFillColor(r.kAzure -5 )
    iOneWithErrors.SetMarkerSize(0)
    iOneWithErrors.SetLineWidth(2)
    iOneWithErrors.Draw('')
    if 'cat1' in tag:
        iOneWithErrors.GetXaxis().SetRangeUser(min(msd_binBoundaries),max(msd_binBoundaries) - 7*5)
    elif 'cat2' in tag:                                                                     
        iOneWithErrors.GetXaxis().SetRangeUser(min(msd_binBoundaries),max(msd_binBoundaries) - 7*3)
    else:                                                                                   
        iOneWithErrors.GetXaxis().SetRangeUser(min(msd_binBoundaries),max(msd_binBoundaries))
    iOneWithErrorsLine = iOneWithErrors.Clone('iOneWithErrorsLine%s' % tag)
    iOneWithErrorsLine.SetFillStyle(0)

    if ratio: 
        iOneWithErrors.Draw("e2 sames")
        iOneWithErrors.GetYaxis().SetRangeUser(0.8, 1.2)
    else:
        iOneWithErrors.Draw("e2 sames")
        iOneWithErrors.GetYaxis().SetRangeUser((mindata-1)*1.5, (maxdata+1)*1.5)
    
    sigHistResiduals = []
    if splitS:
        sigHists = list(hsigs)
    else:
        sigHists = [hsig]
    if options.showWZinRatio:
        [sigHists.append(bkg) for bkg in bkgs if 'zqq' in bkg.GetName()]
        [sigHists.append(bkg) for bkg in bkgs if 'wqq' in bkg.GetName()]
   
    #print sigHists
    #sys.exit()
    for sigHist in sigHists:
        sigHistResidual = sigHist.Clone('sigHistResidual%s%s' % (sigHist.GetName(),tag))
        for bin in range (0,g_data.GetN()):
            value_data = g_data.GetY()[bin]
            err_tot_data = g_data.GetEYhigh()[bin]
            value_signal = sigHist.GetBinContent(bin+1)
            if options.ratio:
                if htot.GetBinContent(bin+1)>0:
                    sig_residual = (value_signal) / htot.GetBinContent(bin+1) 
                else:
                    sig_residual = 0
            else:
                ## Signal residuals
                if err_tot_data>0:                
                    sig_residual = (value_signal) / err_tot_data
                else:
                    sig_residual = 0                                
            ## Fill histo with residuals
            sigHistResidual.SetBinContent(bin+1,sig_residual)
        sigHistResiduals.append(sigHistResidual)
    hstack = r.THStack("hstack","hstack")
    for sigHistResidual in sorted(sigHistResiduals,key=mysort):
	hstack.Add(sigHistResidual) 	
    #    sigHistResidual.Draw("hist sames")
    hstack.Draw("hist sames")	
    iOneWithErrorsLine.Draw("hist sames")
    iRatioGraph.Draw("pezsame")

    if sOverSb:
        tag += '_sOverSb'

    p12.RedrawAxis()
    p22.RedrawAxis()
    htot.SetMinimum(0)
    c.SaveAs(odir + "/mlfit_" + tag + ".pdf")
    c.SaveAs(odir + "/mlfit_" + tag + ".png")
    c.SaveAs(odir + "/mlfit_" + tag + ".C")

    #p12.SetLogy()
    #htot.SetMinimum(0.5)
    #htot.SetMaximum(htot.GetMaximum() * 2)
    #p12.RedrawAxis()
    #p22.RedrawAxis()
    #c.SaveAs(odir + "/mlfit_" + tag + "-log.pdf")
    #c.SaveAs(odir + "/mlfit_" + tag + "-log.C")

    #raw_input("test")

    #return [bkgs + hsigs + [data]]
    return [bkgs + hsigs + [data]]


def makeTF(pars, ratio,n_rho,n_pT,Include_qcdeff):
    ratio.GetXaxis().SetTitle('m_{SD}^{PUPPI} (GeV)')
    ratio.GetYaxis().SetTitle('p_{T} (GeV)')

    ratio.GetXaxis().SetTitleOffset(1.5)
    ratio.GetYaxis().SetTitleOffset(1.5)
    if Include_qcdeff:
        ratio.GetZaxis().SetTitle('Pass-fail Ratio')
    else:
        ratio.GetZaxis().SetTitle('Transfer Factor')
    ratio.GetXaxis().SetNdivisions(504)
    ratio.GetYaxis().SetNdivisions(504)
    ratio.GetZaxis().SetNdivisions(504)

    f2params = array.array('d', pars)
    npar = len(f2params)

    PT_LO =  ratio.GetYaxis().GetXmin() 
    PT_HI =  ratio.GetYaxis().GetXmax() 
    boundaries={'RHO_LO':RHO_LO,'RHO_HI':RHO_HI,'PT_LO':PT_LO,'PT_HI':PT_HI}
    print boundaries
  
    msd_pT = True 
    fun_mass_pT =  bernstein.genBernsteinTF(n_rho,n_pT,boundaries,msd_pT,Include_qcdeff) 
    f2 = r.TF2("f2", fun_mass_pT,  ratio.GetXaxis().GetXmin(),ratio.GetXaxis().GetXmax(),
                                   ratio.GetYaxis().GetXmin(),ratio.GetYaxis().GetXmax(),npar)
    f2.SetParameters(f2params)

    c = r.TCanvas("cTF", "cTF", 1000, 800)
    SetOwnership(c, False)
    c.SetFillStyle(4000)
    c.SetFrameFillStyle(1000)
    c.SetFrameFillColor(0)
    ratio.Draw('surf1')
    # f2.FixParameter(0,0.00265721471909)
    # f2.FixParameter(1,0.000107581411605)
    # f2.FixParameter(2,0)
    # f2.FixParameter(3,-0.0106388614502)
    # f2.FixParameter(4,-0.670514254909 )
    # f2.FixParameter(5,0)
    # f2.FixParameter(6,-4.91702552097)
    # f2.FixParameter(7,0.000234083688387)
    # f2.FixParameter(8,0)
    # ratio.Fit('f2','RN')
    f2.Draw("surf fb bb same")
    #f2.Draw("surf1")

    r.gPad.SetTheta(30)
    r.gPad.SetPhi(30 + 270)
    r.gPad.Modified()
    r.gPad.Update()

    tag1 = r.TLatex(0.67, 0.92, "%.1f fb^{-1} (13 TeV)" % options.lumi)
    tag1.SetNDC();
    tag1.SetTextFont(42)
    tag1.SetTextSize(0.045)
    tag2 = r.TLatex(0.17, 0.92, "CMS")
    tag2.SetNDC()
    tag2.SetTextFont(62)
    if options.isData:
        tag3 = r.TLatex(0.25, 0.92, "Preliminary")
    else:
        tag3 = r.TLatex(0.25, 0.92, "Simulation Preliminary")
    tag3.SetNDC()
    tag3.SetTextFont(52)
    tag2.SetTextSize(0.055)
    tag3.SetTextSize(0.045)
    tag1.Draw()
    tag2.Draw()
    tag3.Draw()

    if Include_qcdeff:
        c.SaveAs(options.odir + "/tf.pdf")
        c.SaveAs(options.odir + "/tf.C")
    else:
        c.SaveAs(options.odir + "/tf_noeff.pdf")
        c.SaveAs(options.odir + "/tf_noeff.C")

    # raw_input("Press Enter to continue...")

    # for i in range(0,360):
    #    r.gPad.SetPhi(30+270+i)
    #    r.gPad.Modified()
    #    r.gPad.Update()
    #    c.SaveAs(options.odir+"/mlfit/tf_%03d.png"%i)

    
    c.SetLogz(0)
    Npoints = 10
    f2graph = r.TGraph2D()
    N = -1
    for i in range(Npoints+1):
        for j in range(Npoints+1):
            N+=1
            x = ratio.GetXaxis().GetXmin() + i*(ratio.GetXaxis().GetXmax()-ratio.GetXaxis().GetXmin())/Npoints
            y = ratio.GetYaxis().GetXmin() + j*(ratio.GetYaxis().GetXmax()-ratio.GetYaxis().GetXmin())/Npoints
            z = f2.Eval(x,y)
            #if math.log(x*x/(y*y)) < -6 or math.log(x*x/(y*y)) > -2.1:
            #    z = 0
            #print x, y, z
            f2graph.SetPoint(N,x,y,z)

    rhoxy =  r.TF2("rhoxy","log(x*x/y/y)",30,221,400,1100)
    contours = array.array('d',[-6 ,-2.1])
    rhoxy.SetContour(2,contours)
    rhoxy.Draw("CONT Z LIST")
    r.gPad.Update()
    conts = r.gROOT.GetListOfSpecials().FindObject("contours")
    contour0 = conts.At(0)
    rhocurv1 = contour0.First().Clone()
    rhocurv1.SetLineWidth(-503)
    rhocurv1.SetFillStyle(3004)
    rhocurv1.SetFillColor(r.kBlack)
    rhocurv1.SetLineColor(r.kBlack)
    contour0 = conts.At(1)
    rhocurv2 = contour0.First().Clone()
    rhocurv2.SetLineWidth(503)
    rhocurv2.SetFillStyle(3004)
    rhocurv2.SetFillColor(r.kBlack)
    rhocurv2.SetLineColor(r.kBlack)
    
    mxy = r.TF2("mxy", "sqrt(exp(x))*y",-6.5, -1.5, 400, 1100)
    contours = array.array('d',[40 ,201])
    mxy.SetContour(2,contours)
    mxy.Draw("CONT Z LIST")
    r.gPad.Update()
    conts = r.gROOT.GetListOfSpecials().FindObject("contours")
    contour0 = conts.At(0)
    mcurv1 = contour0.First().Clone()    
    mcurv1.SetLineWidth(503)
    mcurv1.SetFillStyle(3004)
    mcurv1.SetFillColor(r.kBlack)
    mcurv1.SetLineColor(r.kBlack)
    contour0 = conts.At(1)
    mcurv2 = contour0.First().Clone()    
    mcurv2.SetLineWidth(-503)
    mcurv2.SetFillStyle(3004)
    mcurv2.SetFillColor(r.kBlack)
    mcurv2.SetLineColor(r.kBlack)
    
    r.gStyle.SetNumberContours(999)
            
    ratiorho = r.TH2D('ratiorho','ratiorho',Npoints,-6,-2.1,Npoints,ratio.GetYaxis().GetXmin(),ratio.GetYaxis().GetXmax())
    ratiorho.GetYaxis().SetTitle(ratio.GetYaxis().GetTitle())    
    ratiorho.GetXaxis().SetTitle('#rho')
    ratiorho.GetZaxis().SetTitle(ratio.GetZaxis().GetTitle())
    ratiorhograph = r.TGraph2D()
    N = -1
    for i in range(1,ratio.GetNbinsX()+1):
        for j in range(1,ratio.GetNbinsY()+1):
            N+=1
            m = ratio.GetXaxis().GetBinCenter(i)
            y = ratio.GetYaxis().GetBinCenter(j)
            x = math.log(m*m/(y*y))
            z = ratio.GetBinContent(i,j)
            #print N, x, y, z
            ratiorhograph.SetPoint(N,x,y,z)

    msd_pT = False  #switch to use msd-pT /rho-pT
    fun_rho_pT =  bernstein.genBernsteinTF(n_rho,n_pT,boundaries,msd_pT,Include_qcdeff) 
    f2rho = r.TF2("f2",fun_rho_pT,-6,-2.1,ratio.GetYaxis().GetXmin(),ratio.GetYaxis().GetXmax(),npar)
    f2rho.SetParameters(f2params)
    f2rhograph = r.TGraph2D()
    N = -1
    for i in range(Npoints+1):
        for j in range(Npoints+1):
            N+=1
            x = -6 + i*(-2.1+6)/Npoints
            y = ratio.GetYaxis().GetXmin() + j*(ratio.GetYaxis().GetXmax()-ratio.GetYaxis().GetXmin())/Npoints
            z = f2rho.Eval(x,y)
            m = math.sqrt(math.exp(x))*y
            #if m < 40 or m > 201:
            #    z = 0
            #print x, y, z
            f2rhograph.SetPoint(N,x,y,z)
    #ratiorho.Draw('surf1')    
    ratiorhograph.GetHistogram().GetYaxis().SetTitle(ratio.GetYaxis().GetTitle())    
    ratiorhograph.GetHistogram().GetXaxis().SetTitle('#rho')
    ratiorhograph.GetHistogram().GetZaxis().SetTitle(ratio.GetZaxis().GetTitle())
    ratiorhograph.GetHistogram().GetYaxis().SetNdivisions(505)
    ratiorhograph.GetHistogram().GetXaxis().SetNdivisions(505)
    ratiorhograph.GetHistogram().GetXaxis().SetTitleOffset(1.5)
    ratiorhograph.GetHistogram().GetYaxis().SetTitleOffset(1.5)
    ratiorhograph.Draw("surf1")
    f2rho.Draw("surf fb bb same")
    #f2rhograph.SetLineColor(r.kRed)
    #f2rhograph.Draw("surf fb bb same")
    tag1 = r.TLatex(0.55,0.92,"%.1f fb^{-1} (13 TeV)"%options.lumi)
    tag1.SetNDC(); tag1.SetTextFont(42)
    tag1.SetTextSize(0.045)
    tag2 = r.TLatex(0.15,0.92,"CMS")
    tag2.SetNDC()
    tag2.SetTextFont(62)
    tag3 = r.TLatex(0.25,0.92,"Preliminary")
    tag3.SetNDC()
    tag3.SetTextFont(52)
    tag2.SetTextSize(0.055)
    tag3.SetTextSize(0.045)
    tag1.Draw()
    tag2.Draw()
    tag3.Draw()
   
    if Include_qcdeff: 
        c.SaveAs(options.odir + "/tf_rho.pdf")
        c.SaveAs(options.odir + "/tf_rho.C")
    else:
        c.SaveAs(options.odir + "/tf_rho_noeff.pdf")
        c.SaveAs(options.odir + "/tf_rho_noeff.C")
    
    # to plot TF2
    #f2.Draw("colz")
    c.SetRightMargin(0.20)
    # to plot TGraph:
    f2graph.Draw("colz")
    rhocurv1.Draw('same')
    rhocurv2.Draw('same')
    
    f2graph.GetHistogram().GetXaxis().SetTitle(ratio.GetXaxis().GetTitle())
    f2graph.GetHistogram().GetYaxis().SetTitle(ratio.GetYaxis().GetTitle())
    f2graph.GetHistogram().GetZaxis().SetTitle(ratio.GetZaxis().GetTitle())
    f2graph.GetHistogram().GetZaxis().SetTitleOffset(1.3)
    tag1 = r.TLatex(0.55,0.92,"%.1f fb^{-1} (13 TeV)"%options.lumi)
    tag1.SetNDC(); tag1.SetTextFont(42)
    tag1.SetTextSize(0.045)
    tag2 = r.TLatex(0.2,0.82,"CMS")
    tag2.SetNDC()
    tag2.SetTextFont(62)
    tag3 = r.TLatex(0.25,0.92,"Preliminary")
    tag3.SetNDC()
    tag3.SetTextFont(52)
    tag2.SetTextSize(0.055)
    tag3.SetTextSize(0.045)
    tag1.Draw()
    tag2.Draw()
    tag3.Draw()
    
    pave_param = r.TPaveText(0.17,0.72,0.27,0.82,"NDC")
    pave_param.SetTextFont(42)
    pave_param.SetFillColor(0)
    pave_param.SetBorderSize(0)
    pave_param.SetFillStyle(0)
    pave_param.SetTextAlign(11)
    pave_param.SetTextSize(0.045)
    text = pave_param.AddText("#rho = #minus6")
    text.SetTextAngle(75)
    text.SetTextAlign(22)
    text.SetTextSize(0.045)
    pave_param.Draw()
    
    pave_param2 = r.TPaveText(0.62,0.18,0.72,0.28,"NDC")
    pave_param2.SetTextFont(42)
    pave_param2.SetFillColor(0)
    pave_param2.SetBorderSize(0)
    pave_param2.SetFillStyle(0)
    pave_param2.SetTextAlign(11)
    pave_param2.SetTextSize(0.045)
    text2 = pave_param2.AddText("#rho = #minus2.1")
    text2.SetTextAngle(40)
    text2.SetTextAlign(22)
    text2.SetTextSize(0.045)
    pave_param2.Draw()
    

    if Include_qcdeff: 
        c.SaveAs(options.odir + "/tf_msdcolz.pdf")
        c.SaveAs(options.odir + "/tf_msdcolz.C")
    else:
        c.SaveAs(options.odir + "/tf_msdcolz_noeff.pdf")
        c.SaveAs(options.odir + "/tf_msdcolz_noeff.C")

    # to plot TF2
    #f2rho.Draw("colz")
    # to plot TGraph:
    #f2rhograph.SetContours(999)
    f2rhograph.Draw("colz")
    mcurv1.Draw('same')
    mcurv2.Draw('same')
    f2rhograph.GetHistogram().GetXaxis().SetTitle('#rho')
    f2rhograph.GetHistogram().GetYaxis().SetTitle(ratio.GetYaxis().GetTitle())
    f2rhograph.GetHistogram().GetZaxis().SetTitle(ratio.GetZaxis().GetTitle())
    f2rhograph.GetHistogram().GetZaxis().SetTitleOffset(1.3)
    Tag1 = r.TLatex(0.67,0.92,"%.1f fb^{-1} (13 TeV)"%options.lumi)
    tag1.SetNDC(); tag1.SetTextFont(42)
    tag1.SetTextSize(0.045)
    tag2 = r.TLatex(0.15,0.92,"CMS")
    tag2.SetNDC()
    tag2.SetTextFont(62)
    tag3 = r.TLatex(0.25,0.92,"Preliminary")
    tag3.SetNDC()
    tag3.SetTextFont(52)
    tag2.SetTextSize(0.055)
    tag3.SetTextSize(0.045)
    tag1.Draw()
    tag2.Draw()
    tag3.Draw()

    
    pave_param = r.TPaveText(0.18,0.5,0.28,0.6,"NDC")
    pave_param.SetTextFont(42)
    pave_param.SetFillColor(0)
    pave_param.SetBorderSize(0)
    pave_param.SetFillStyle(0)
    pave_param.SetTextAlign(11)
    pave_param.SetTextSize(0.045)
    text = pave_param.AddText("m_{SD} = 40 GeV")
    text.SetTextAngle(-70)
    text.SetTextAlign(22)
    text.SetTextSize(0.045)
    pave_param.Draw()
    
    pave_param2 = r.TPaveText(0.57,0.65,0.67,0.75,"NDC")
    pave_param2.SetTextFont(42)
    pave_param2.SetFillColor(0)
    pave_param2.SetBorderSize(0)
    pave_param2.SetFillStyle(0)
    pave_param2.SetTextAlign(11)
    pave_param2.SetTextSize(0.045)
    text2 = pave_param2.AddText("m_{SD} = 201 GeV")
    text2.SetTextAngle(-72)
    text2.SetTextAlign(22)
    text2.SetTextSize(0.045)
    pave_param2.Draw()
   
    if Include_qcdeff: 
        c.SaveAs(options.odir + "/tf_rhocolz.pdf")
        c.SaveAs(options.odir + "/tf_rhocolz.C")
    else:
        c.SaveAs(options.odir + "/tf_rhocolz_noeff.pdf")
        c.SaveAs(options.odir + "/tf_rhocolz_noeff.C")
    

##-------------------------------------------------------------------------------------
if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option('-b', action='store_true', dest='noX', default=False, help='no X11 windows')
    parser.add_option("--lumi", dest="lumi", type=float, default=35.9, help="luminosity", metavar="lumi")
    parser.add_option('-i', '--idir', dest='idir', default='cards/', help='directory with data', metavar='idir')
    parser.add_option('-o', '--odir', dest='odir', default='cards/', help='directory for plots', metavar='odir')
    parser.add_option('--fit', dest='fit', default='prefit', help='choice is either prefit, fit_s or fit_b',
                      metavar='fit')
    parser.add_option('--data', action='store_true', dest='isData', default=False, help='is data', metavar='isData')
    parser.add_option('--s-over-sb', action='store_true', dest='sOverSb', default=False,
                      help='weight entries by sOverSb', metavar='sOverSb')
    parser.add_option('--splitS', action='store_true', dest='splitS', default=False, help='split signal contribution',
                      metavar='splitS')
    parser.add_option('--ratio', action='store_true', dest='ratio', default=False, help='ratio or data-mc',
                      metavar='ratio')
    parser.add_option('--nr','--NR' ,action='store',type='int',dest='NR'   ,default=2, help='order of rho polynomial')
    parser.add_option('--np','--NP' ,action='store',type='int',dest='NP'   ,default=1, help='order of pt polynomial')
    parser.add_option('--suffix', dest='suffix', default='', help='list of suffix  separated by :',metavar='suffix')
    parser.add_option('--qcdTF', dest='qcdTF', action='store_true',default=False, help='make fail x TF plot',metavar='qcdTF')
    parser.add_option('--showWZinRatio', dest='showWZinRatio', action='store_true',default=False, help='showWZ in Ratio plot',metavar='showWZinRatio')

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
    #r.gStyle.SetPalette(r.kBird)
    #r.gStyle.SetPalette(r.kBlackBody)
    stops = [ 0.0, 1.0]
    red =   [ 1.0, 0.0]
    green = [ 1.0, 0.0]
    blue =  [ 1.0, 0.6]

    s = array.array('d', stops)
    rs = array.array('d', red)
    g = array.array('d', green)
    b = array.array('d', blue)

    npoints = len(s)
    r.TColor.CreateGradientColorTable(npoints, s, rs, g, b, 999)

    r.gStyle.SetNumberContours(999)

    main(options, args)
##-------------------------------------------------------------------------------------
