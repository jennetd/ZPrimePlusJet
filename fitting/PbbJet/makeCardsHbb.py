#!/usr/bin/env python

import ROOT as r,sys,math,array,os
from ROOT import TFile, TTree, TChain, gPad, gDirectory
from multiprocessing import Process
from optparse import OptionParser
from operator import add
import math
import sys
import time
import array

# including other directories
sys.path.insert(0, '../.')
from tools import *

from buildRhalphabetHbb import MASS_BINS,MASS_LO,MASS_HI,BLIND_LO,BLIND_HI,RHO_LO,RHO_HI,SF2018,SF2017,SF2016,MASS_HIST_HI,MASS_HIST_LO

##-------------------------------------------------------------------------------------
def main(options,args):
	
    if options.year=='2018':
        SF       =SF2018
        BB_SF    =SF2018['BB_SF'] 
        BB_SF_ERR=SF2018['BB_SF_ERR']
        V_SF     =SF2018['V_SF']
        V_SF_ERR =SF2018['V_SF_ERR']
        LUMI_ERR = 1.025
    elif options.year=='2017':
        SF       =SF2017
        BB_SF    =SF2017['BB_SF'] 
        BB_SF_ERR=SF2017['BB_SF_ERR']
        V_SF     =SF2017['V_SF']
        V_SF_ERR =SF2017['V_SF_ERR']
        LUMI_ERR = 1.023
    elif options.year =='2016':
        SF       =SF2016
        BB_SF     =SF2016['BB_SF']
        BB_SF_ERR =SF2016['BB_SF_ERR']
        V_SF      =SF2016['V_SF']
        V_SF_ERR  =SF2016['V_SF_ERR']
        LUMI_ERR = 1.025
  
    print "using BB_SF    ", BB_SF    
    print "using BB_SF_ERR", BB_SF_ERR
    print "using V_SF     ", V_SF     
    print "using V_SF_ERR ", V_SF_ERR  
    print "using LUMI_ERR ", LUMI_ERR
     

    tfile = r.TFile.Open(options.ifile)
    tfile_loose = None
    if options.ifile_loose is not None:
        tfile_loose = r.TFile.Open(options.ifile_loose)
        
    boxes = ['pass', 'fail']
    #Has to follow the ordering in template datacard
    sigs = ['tthqq125','whqq125','hqq125','zhqq125','vbfhqq125']
    bkgs = ['zqq','wqq','qcd','tqq']
    systs = ['JER','JES','Pu']

    removeUnmatched = options.removeUnmatched

    nBkgd = len(bkgs)
    nSig = len(sigs)
    #Change the list of bins to do integral for proc removal
    binwidth = 7
    massbins = range(MASS_LO,MASS_HI,binwidth)
    masshistbins = []
    for ibin,mass in enumerate(massbins):
        if( mass>=MASS_HIST_LO and mass<=MASS_HIST_HI):
            masshistbins.append(ibin+1)
    print "Integrating over these mass bins:",masshistbins
    print "                 read  mass bins:",massbins
    numberOfPtBins = 6
    procsToRemove = []

    histoDict = {}
    histoDictLoose = {}

    for proc in (sigs+bkgs):
        for box in boxes:
            print 'getting histogram for process: %s_%s'%(proc,box)
            histoDict['%s_%s'%(proc,box)] = tfile.Get('%s_%s'%(proc,box))
            if tfile_loose is not None:
                histoDictLoose['%s_%s'%(proc,box)] = tfile_loose.Get('%s_%s'%(proc,box))
                
            if removeUnmatched and (proc =='wqq' or proc=='zqq' or 'hqq' in proc):
                histoDict['%s_%s_matched'%(proc,box)] = tfile.Get('%s_%s_matched'%(proc,box))
                histoDict['%s_%s_unmatched'%(proc,box)] = tfile.Get('%s_%s_unmatched'%(proc,box))
                if tfile_loose is not None:
                    histoDictLoose['%s_%s_matched'%(proc,box)] = tfile_loose.Get('%s_%s_matched'%(proc,box))
                    histoDictLoose['%s_%s_unmatched'%(proc,box)] = tfile_loose.Get('%s_%s_unmatched'%(proc,box))
                    
                
            for syst in systs:
                print 'getting histogram for process: %s_%s_%sUp'%(proc,box,syst)
                histoDict['%s_%s_%sUp'%(proc,box,syst)] = tfile.Get('%s_%s_%sUp'%(proc,box,syst))
                print 'getting histogram for process: %s_%s_%sDown'%(proc,box,syst)
                histoDict['%s_%s_%sDown'%(proc,box,syst)] = tfile.Get('%s_%s_%sDown'%(proc,box,syst))

    #for hname,h in histoDict.iteritems():
    #    h.RebinX(7)
    #    print 'rebinning %s by 7...'
    dctpl = open("datacard.tpl")
    #dctpl = open("datacardZbb.tpl")
    #dctpl = open("datacardZonly.tpl")

    linel = []
    for line in dctpl: 
        print line.strip().split()
        linel.append(line.strip())

    for i in range(1,numberOfPtBins+1):

        jesErrs = {}
        jerErrs = {}
        puErrs = {}
        bbErrs = {}
        weffErrs = {}
        vErrs = {}
        mcstatErrs = {}
        scaleErrs = {}
        scaleptErrs = {}
        for box in boxes:
            for proc in (sigs+bkgs):
                if options.blind:
                    rate1  = histoDict['%s_%s'%(proc,box)].Integral(masshistbins[0], masshistbins[9], i, i)
                    rate2  = histoDict['%s_%s'%(proc,box)].Integral(masshistbins[13], masshistbins[-1], i, i)
                    rateall= histoDict['%s_%s'%(proc,box)].Integral(masshistbins[0], masshistbins[-1], i, i)
                    rate = rate1+rate2
                    print "ignore bins: mass (%s,%s)"%(massbins[11],massbins[13])
                    print 'rate1 = %.3f rate2 = %.3f, rateall= %.3f'%(rate1,rate2,rateall)
                else:
                    rate = histoDict['%s_%s'%(proc,box)].Integral(masshistbins[0], masshistbins[-1], i, i)
                print " proc, cat, box, rate =", proc, "cat%i"%i, box, rate
                if rate>0.1:
                    rateJESUp   = histoDict['%s_%s_JESUp'  %(proc,box)].Integral(masshistbins[0], masshistbins[-1], i, i)
                    rateJESDown = histoDict['%s_%s_JESDown'%(proc,box)].Integral(masshistbins[0], masshistbins[-1], i, i)
                    rateJERUp   = histoDict['%s_%s_JERUp'  %(proc,box)].Integral(masshistbins[0], masshistbins[-1], i, i)
                    rateJERDown = histoDict['%s_%s_JERDown'%(proc,box)].Integral(masshistbins[0], masshistbins[-1], i, i)
                    ratePuUp    = histoDict['%s_%s_PuUp'   %(proc,box)].Integral(masshistbins[0], masshistbins[-1], i, i)
                    ratePuDown  = histoDict['%s_%s_PuDown' %(proc,box)].Integral(masshistbins[0], masshistbins[-1], i, i)
                    jesErrs['%s_%s'%(proc,box)] =  1.0+(abs(rateJESUp-rate)+abs(rateJESDown-rate))/(2.*rate)   
                    jerErrs['%s_%s'%(proc,box)] =  1.0+(abs(rateJERUp-rate)+abs(rateJERDown-rate))/(2.*rate) 
                    puErrs['%s_%s'%(proc,box)] =  1.0+(abs(ratePuUp-rate)+abs(ratePuDown-rate))/(2.*rate)
                else:
                    jesErrs['%s_%s'%(proc,box)] =  1.0
                    jerErrs['%s_%s'%(proc,box)] =  1.0
                    puErrs['%s_%s'%(proc,box)] =  1.0
                    print "to remove: proc, cat, box, rate =", proc, "cat%i"%i, box, rate
                    procsToRemove.append((proc, "cat%i"%i, box))
               
                if proc == 'wqq':
                    mass = 80.4
                elif proc == 'zqq':
                    mass = 91.
                elif 'hqq' in proc:
                    mass = float(proc[-3:])  # hqq125 -> 125 
                
                # Assume template is shifted by 1 bin, require:
                # 7 GeV (1binshift) * scaleErr = (scaleSigma); 
                #          scaleSigma = mass * massShift * massShiftUnc
                #    ==>   scaleErr   = scaleSigma/7GeV
                scaleSigma                    = mass * SF['shift_SF'] *  SF['shift_SF_ERR']
                scaleErrs['%s_%s'%(proc,box)] =  scaleSigma/7.0
                #print proc, mass, scaleSigma, "%.3f"%( scaleSigma/7.0)

                ##### old scheme
                #scaleErrs['%s_%s'%(proc,box)] =  0.1 
                #if i == 2:
                #    scaleptErrs['%s_%s'%(proc,box)] =  0.05
                #elif i == 3:
                #    scaleptErrs['%s_%s'%(proc,box)] =  0.1
                #elif i == 4:
                #    scaleptErrs['%s_%s'%(proc,box)] =  0.2
                #elif i == 5:
                #    scaleptErrs['%s_%s'%(proc,box)] =  0.3
                #elif i == 6:
                #    scaleptErrs['%s_%s'%(proc,box)] =  0.4
                
                if i == 2:
                    scaleptErrs['%s_%s'%(proc,box)] = scaleErrs['%s_%s'%(proc,box)]*(500-450)/100
                elif i == 3:
                    scaleptErrs['%s_%s'%(proc,box)] = scaleErrs['%s_%s'%(proc,box)]*(550-450)/100
                elif i == 4:
                    scaleptErrs['%s_%s'%(proc,box)] = scaleErrs['%s_%s'%(proc,box)]*(600-450)/100
                elif i == 5:
                    scaleptErrs['%s_%s'%(proc,box)] = scaleErrs['%s_%s'%(proc,box)]*(675-450)/100
                elif i == 6:
                    scaleptErrs['%s_%s'%(proc,box)] = scaleErrs['%s_%s'%(proc,box)]*(800-450)/100
                
                
                vErrs['%s_%s'%(proc,box)] = 1.0+V_SF_ERR/V_SF
                if box=='pass':
                    bbErrs['%s_%s'%(proc,box)] = 1.0+BB_SF_ERR/BB_SF
                else:
                    ratePass = histoDict['%s_%s'%(proc,'pass')].Integral()
                    rateFail = histoDict['%s_%s'%(proc,'fail')].Integral()
                    if rateFail>0:
                        bbErrs['%s_%s'%(proc,box)] = 1.0-BB_SF_ERR*(ratePass/rateFail)
                    else:
                        bbErrs['%s_%s'%(proc,box)] = 1.0

                WEFF_SF_ERR = 0.3
                WEFF_SF     = 1.0   # if differ from 1, need to update rhalphabet builder
                if box=='pass':
                    weffErrs['%s_%s'%(proc,box)] = 1.0+WEFF_SF_ERR/WEFF_SF
                else:
                    ratePass = histoDict['%s_%s'%(proc,'pass')].Integral()
                    rateFail = histoDict['%s_%s'%(proc,'fail')].Integral()
                    if rateFail>0:
                        weffErrs['%s_%s'%(proc,box)] = 1.0-WEFF_SF_ERR*(ratePass/rateFail)
                    else:
                        weffErrs['%s_%s'%(proc,box)] = 1.0

                        
                    
                #for j in range(1,numberOfMassBins+1):                    
                for j in masshistbins:                    
                    if options.noMcStatShape:                 
                        matchString = ''
                        if removeUnmatched and (proc =='wqq' or proc=='zqq'):
                            matchString = '_matched'
                        if (tfile_loose is not None) and (proc =='wqq' or proc=='zqq') and 'pass' in box:
                            histo = histoDictLoose['%s_%s%s'%(proc,box,matchString)]
                        else:
                            histo = histoDict['%s_%s%s'%(proc,box,matchString)]
                            
                        error = array.array('d',[0.0])
                        rate = histo.IntegralAndError(1,histo.GetNbinsX(),i,i,error)                 
                        if rate>0:
                            mcstatErrs['%s_%s'%(proc,box),i,j] = 1.0+(error[0]/rate)
                        else:
                            mcstatErrs['%s_%s'%(proc,box),i,j] = 1.0
                            if (proc, "cat%i"%i, box) not in procsToRemove:
                                procsToRemove.append((proc, "cat%i"%i, box))
                    else:
                        mcstatErrs['%s_%s'%(proc,box),i,j] = 1.0
                        

        jesString = 'CMS_scale_j%s lnN'%options.suffix
        jerString = 'CMS_res_j%s lnN'%options.suffix
        puString = 'CMS_PU%s lnN'%options.suffix
        bbString = 'CMS_eff_bb%s lnN'%options.suffix
        hqq125ptString = 'CMS_gghbb_hqq125pt lnN'
        weffString = 'weff%s lnN'%options.suffix            ### this is not used ##
        vString = 'CMS_gghbb_veff%s lnN'%options.suffix
        ### Normal scale/scale pt
        scaleptString = 'CMS_gghbb_scalept%s shape'%options.suffix
        scaleString   = 'CMS_gghbb_scale%s shape'%options.suffix
        ### scale(pt) pass/fail 
        #scalepassptString = 'scalepasspt%s shape'%options.suffix
        #scalefailptString = 'scalefailpt%s shape'%options.suffix
        #scalepassString   = 'scalepass%s shape'%options.suffix
        #scalefailString   = 'scalefail%s shape'%options.suffix
        #scalepassString   = 'scalepass_cat%i%s shape'%(i,options.suffix)
        #scalefailString   = 'scalefail_cat%i%s shape'%(i,options.suffix)
        ### scale cat i 
        #if i >=2:
        #    scaleString   = 'scale_cat%i%s shape'%(i,options.suffix)
        #else:
        #    scaleString   = 'scale%s shape'%(options.suffix)
        mcStatStrings = {}
        if options.year in ['2017','2018']:
            lumiString = 'lumi_13TeV%s lnN'%options.suffix
        else:
            lumiString = 'lumi%s lnN'%options.suffix
        mcStatGroupString = 'mcstat group ='
        mcstatsuffix  = options.suffix.lower().strip("_")
        qcdGroupString = 'qcd group = '
        qcdeffGroupString = 'qcdeff group = '
        for box in boxes:
            for proc in sigs+bkgs:
                #for j in range(1,numberOfMassBins+1):
                for j in masshistbins:
                    if options.noMcStatShape:
                        mcStatStrings['%s_%s'%(proc,box),i,j] = '%s%scat%i%smcstat%i lnN'%(proc,box,i,mcstatsuffix,j)
                    else:
                        mcStatStrings['%s_%s'%(proc,box),i,j] = '%s%scat%i%smcstat%i shape'%(proc,box,i,mcstatsuffix,j)
                    
        for box in boxes:
            for proc in sigs+bkgs:
                if proc=='qcd' :
                    jesString += ' -'
                    jerString += ' -'
                    puString += ' -'
                    lumiString += ' -'
                else:
                    jesString += ' %.3f'%jesErrs['%s_%s'%(proc,box)]
                    jerString += ' %.3f'%jerErrs['%s_%s'%(proc,box)]
                    puString += ' %.3f'%puErrs['%s_%s'%(proc,box)]                        
                    lumiString += ' %.3f'%LUMI_ERR
                if proc in ['qcd','tqq']:
                    scaleString += ' -'
                    #scalepassString += ' -'
                    #scalefailString += ' -'
                    if i > 1:
                        scaleptString += ' -'
                        #scalepassptString += ' -'
                        #scalefailptString += ' -'
                else:
                    scaleString += ' %.3f'%scaleErrs['%s_%s'%(proc,box)]
                    if i > 1:
                        scaleptString += ' %.3f'%scaleptErrs['%s_%s'%(proc,box)]
                    #if box =='pass':
                    #    scalepassString += ' %.3f'%scaleErrs['%s_%s'%(proc,box)]
                    #    scalefailString += ' -'
                    #    if i > 1:
                    #        scalepassptString += ' %.3f'%scaleptErrs['%s_%s'%(proc,box)]
                    #        scalefailptString += ' -'
                    #else:
                    #    scalepassString += ' -'
                    #    scalefailString += ' %.3f'%scaleErrs['%s_%s'%(proc,box)]
                    #    if i > 1:
                    #        scalepassptString += ' -'
                    #        scalefailptString += ' %.3f'%scaleptErrs['%s_%s'%(proc,box)]

                if proc in ['qcd','tqq','wqq']:
                    bbString += ' -'
                else:
                    bbString += ' %.3f'%bbErrs['%s_%s'%(proc,box)]
                if proc in ['hqq125']:
                    if not options.addHptShape:
                        hqq125ptString += ' 1.20'
                    else:
                        hqq125ptString += ' 1.30'
                else:
                    hqq125ptString += ' -'

                if proc in ['wqq']:
                    weffString += ' %.3f'%weffErrs['%s_%s'%(proc,box)]
                else:
                    weffString += ' -'

                if proc in ['qcd','tqq']:
                    vString += ' -'
                else:
                    vString += ' %.3f'%vErrs['%s_%s'%(proc,box)]
                #for j in range(1,numberOfMassBins+1):
                for j in masshistbins:
                    for box1 in boxes:                    
                        for proc1 in sigs+bkgs:                            
                            if proc1==proc and box1==box and proc!='qcd' :
                                mcStatStrings['%s_%s'%(proc1,box1),i,j] += '\t%.3f'% mcstatErrs['%s_%s'%(proc,box),i,j]
                            else:                        
                                mcStatStrings['%s_%s'%(proc1,box1),i,j] += '\t-'

        tag = "cat"+str(i)
        dctmp = open(options.odir+"/card_rhalphabet_%s.txt" % tag, 'w')
        for j,l in enumerate(linel):
            #if '#' == l[0]:continue
            if 'shapes qcd' in l:
                if options.addqcdCovMat:
                    l = l.replace("rhalphabase","qcdfit_decorrelated")
                    l = l.replace("w_fail_CATX","qcdfit_deco%s"%options.suffix)
                    l = l.replace("w_pass_CATX","qcdfit_deco%s"%options.suffix)
                newline = l+options.suffix
                if options.multi:
                    newline = newline.replace('qcd','qcd_multi')
            elif 'qcd' in l:
                if options.multi:
                    newline = l.replace('qcd','qcd_multi')
                else:
                    newline = l
            elif 'lumi' in l:
                newline = lumiString
            elif 'CMS_scale_j' in l:
                newline = jesString
            elif 'CMS_res_j' in l:
                newline = jerString
            elif 'CMS_PU' in l:
                newline = puString
            elif 'CMS_eff_bb' in l:
                newline = bbString
            #elif 'weff' in l:
            #    newline = weffString
            #    pass
            elif 'hqq125pt' in l and not 'hqq125ptShape' in l:
                newline = hqq125ptString
            elif 'hqq125ptShape' in l:
                if options.addHptShape:
                    newline = l
                else:
                    newline = l.replace("hqq125ptShape","#hqq125ptShape")
            elif 'veff' in l:
                newline = vString
            elif 'CMS_gghbb_scale' in l  and 'pt' in l and i>1:
                #newline = scaleptString.replace("scalept","scalept_cat%i"%i)
                newline = scaleptString
                #if 'pass' in l:
                #    newline = scalepassptString
                #elif 'fail' in l:
                #    newline = scalefailptString
                pass
            elif 'smear' in l:
                newline = l.replace('smear','smear'+options.suffix)
            elif 'trigger' in l:
                newline = l.replace('trigger','trigger'+options.suffix)
            elif 'CMS_gghbb_scale' in l and not 'pt' in l:
                newline = scaleString
                #if 'pass' in l:
                #    newline = scalepassString
                #elif 'fail' in l:
                #    newline = scalefailString
            elif 'TQQEFF' in l or 'tqqnormSF' in l or 'tqqeffSF' in l:
                tqqeff = histoDict['tqq_pass'].Integral() / (
                histoDict['tqq_pass'].Integral() + histoDict['tqq_fail'].Integral())
                newline = l.replace('TQQEFF','%.4f'%tqqeff)
                newline = newline.replace('CATXnorm','CATX%snorm'%options.suffix)
                newline = newline.replace('tqqnormSF','tqqnormSF%s'%options.suffix)
                newline = newline.replace('tqqeffSF','tqqeffSF%s'%options.suffix)
            elif "wznormEW" in l:
                if i==4:                    newline = l.replace('1.02','1.06')
                elif i==5:                    newline = l.replace('1.02','1.06')
                elif i==6:                    newline = l.replace('1.02','1.06')
                else:                    newline = l
            elif "znormEW" in l:
                if i==3:                    newline = l.replace('1.05','1.07')
                elif i==4:                    newline = l.replace('1.05','1.07')
                elif i==5:                    newline = l.replace('1.05','1.07')
                elif i==6:                    newline = l.replace('1.05','1.07')      
                else:                    newline = l              
            else:
                newline = l
            if "CATX" in l:
                newline = newline.replace('CATX',tag)
            dctmp.write(newline + "\n")
        for box in boxes:
            for proc in sigs+bkgs:
                if options.noMcStatShape and proc!='qcd' :
                    if (proc, 'cat%i'%i, box) not in procsToRemove:
                        print 'include %s%scat%i%smcstat'%(proc,box,i,mcstatsuffix)
                        firstmassbin = masshistbins[0]
                        dctmp.write(mcStatStrings['%s_%s'%(proc,box),i,firstmassbin].replace('mcstat%s'%str(firstmassbin),'mcstat') + "\n")
                        mcStatGroupString += ' %s%scat%i%smcstat'%(proc,box,i,mcstatsuffix)
                        continue
                    else:
                        continue
                #for j in range(1,numberOfMassBins+1):                    
                for j in masshistbins:                    
                    # if stat. unc. is greater than 50% 
                    matchString = ''
                    if removeUnmatched and (proc =='wqq' or proc=='zqq'):
                        matchString = '_matched'
                    if (tfile_loose is not None) and (proc =='wqq' or proc=='zqq') and 'pass' in box:
                        histo = histoDictLoose['%s_%s%s'%(proc,box,matchString)]
                    else:
                        histo = histoDict['%s_%s%s'%(proc,box,matchString)]
                    if abs(histo.GetBinContent(j,i)) > 0. and histo.GetBinError(j,i) > 0.5*histo.GetBinContent(j,i) and proc!='qcd':
                        massVal = histo.GetXaxis().GetBinCenter(j)
                        ptVal = histo.GetYaxis().GetBinLowEdge(i) + 0.3*(histo.GetYaxis().GetBinWidth(i))
                        rhoVal = r.TMath.Log(massVal*massVal/ptVal/ptVal)
                        if not( options.blind and massVal > BLIND_LO and massVal < BLIND_HI) and not (rhoVal < RHO_LO or rhoVal > RHO_HI):
                            dctmp.write(mcStatStrings['%s_%s'%(proc,box),i,j] + "\n")
                            print 'include %s%scat%i%smcstat%i'%(proc,box,i,mcstatsuffix,j)
                            mcStatGroupString += ' %s%scat%i%smcstat%i'%(proc,box,i,mcstatsuffix,j)
                        else:
                            print 'do not include %s%scat%i%smcstat%i'%(proc,box,i,mcstatsuffix,j)
                    else:
                        print 'do not include %s%scat%i%smcstat%i'%(proc,box,i,mcstatsuffix,j)
                        
        #for im in range(numberOfMassBins):
        for im in masshistbins:
            dctmp.write("qcd_fail_%s_Bin%i%s flatParam \n" % (tag,im,options.suffix))
            qcdGroupString += ' qcd_fail_%s_Bin%i%s'%(tag,im,options.suffix)
            flatPars = ['p0r0','p0r1', 'p0r2', 'p1r0', 'p1r1', 'p1r2']
        for flatPar in flatPars:
            dctmp.write('%s%s flatParam \n'%(flatPar,options.suffix))
        if options.addqcdCovMat:
            qcdfit_deco = r.TFile.Open(options.odir+'qcdfit_decorrelated.root')
            ws          = qcdfit_deco.Get("qcdfit_deco_%s"%options.year)
            decoVars    = ws.allVars().selectByName("qcdfit_tf_%s_deco*"%options.year)
            #decoVars.Print()
            for i in range(0,decoVars.getSize()):
                qcdeffGroupString += "qcdfit_tf_%s_deco%s "%(options.year,i)
                dctmp.write("qcdfit_tf_%s_deco%s param 0 1"%(options.year,i)+'\n')

        dctmp.write(mcStatGroupString + "\n")
        dctmp.write(qcdGroupString + "\n")
        dctmp.write(qcdeffGroupString + "\n")
        dctmp.close()
    def removeProc(proc, tag, box):
        dctmp = open(options.odir+"/card_rhalphabet_%s.txt" % tag, 'r')
        linel = []
        firstProcessLine = True
        for iline, line in enumerate(dctmp):
            l = line.strip().split()
            linel.append(l)
        for iline, l in enumerate(linel):
            if l[0]=='process' and firstProcessLine: 
                totalProcs = len(l)-1
                #procIndex = l.index(proc)
                procIndex = [il for il, nl in enumerate(l) if nl == proc][0] # first instance of process (pass category)
                if linel[iline-1][procIndex]!='%s_%s'%(box,tag):
                    procIndex = [il for il, nl in enumerate(l) if nl == proc][1] # second instance of process (fail category)
                if linel[iline-1][procIndex]=='%s_%s'%(box,tag):
                    print "REMOVING", proc, tag, box                    
                else:
                    print "NOT REMOVING; NO MATCH", proc, tag, box                    
                l.pop(procIndex)
                linel[iline] = l
                linel[iline-1].pop(procIndex)
                firstProcessLine = False
            elif not firstProcessLine and len(l) > 1 and l[1]=='group':
                continue
            elif not firstProcessLine and len(l)==totalProcs+1:
                l.pop(procIndex)
                linel[iline] = l
            elif not firstProcessLine and len(l)==totalProcs+2:
                l.pop(procIndex+1)     
                linel[iline]= l
        dctmp.close()
        dctmp_w = open(options.odir+"/card_rhalphabet_%s.txt" % tag, 'w')
        for l in linel: dctmp_w.write(' '.join(l)+'\n')

    for proc, tag, box in procsToRemove: 
        removeProc(proc, tag, box)
###############################################################


	
##-------------------------------------------------------------------------------------
if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option('-b', action='store_true', dest='noX', default=False, help='no X11 windows')
    parser.add_option("--lumi", dest="lumi", type=float, default = 30,help="luminosity", metavar="lumi")
    parser.add_option('-i','--ifile', dest='ifile', default = 'hist_1DZbb.root',help='file with histogram inputs', metavar='ifile')
    parser.add_option('--ifile-loose', dest='ifile_loose', default=None, help='second file with histogram inputs (looser b-tag cut to take W/Z/H templates)', metavar='ifile_loose')
    parser.add_option('-o','--odir', dest='odir', default = 'cards/',help='directory to write cards', metavar='odir')
    parser.add_option('--pseudo', action='store_true', dest='pseudo', default =False,help='signal comparison', metavar='isData')
    parser.add_option('--blind', action='store_true', dest='blind', default =False,help='blind signal region', metavar='blind')
    parser.add_option('-y' ,'--year', type='choice', dest='year', default ='2016',choices=['2016','2017','2018'],help='switch to use different year ', metavar='year')
    parser.add_option('--remove-unmatched', action='store_true', dest='removeUnmatched', default =False,help='remove unmatched', metavar='removeUnmatched')
    parser.add_option('--addHptShape', action='store_true', dest='addHptShape', default =False,help='add higgspt shape', metavar='addHptShape')
    parser.add_option('--addqcdCovMat', action='store_true', dest='addqcdCovMat', default =False,help='add qcdCovMat', metavar='addqcdCovMat')
    parser.add_option('--qcdfitdir',  dest='qcdfitdir', default ='',help='add qcdfit dir', metavar='qcdfitdir')
    parser.add_option('--no-mcstat-shape', action='store_true', dest='noMcStatShape', default =False,help='change mcstat uncertainties to lnN', metavar='noMcStatShape')
    parser.add_option('--suffix', dest='suffix', default='', help='suffix for conflict variables',metavar='suffix')
    parser.add_option('--multi', action='store_true', dest='multi', default=False, help='define RooMultiPdf',
                      metavar='multi')


    (options, args) = parser.parse_args()

    if options.suffix!='':
        options.suffix='_'+options.suffix
    import tdrstyle
    tdrstyle.setTDRStyle()
    r.gStyle.SetPadTopMargin(0.10)
    r.gStyle.SetPadLeftMargin(0.16)
    r.gStyle.SetPadRightMargin(0.10)
    r.gStyle.SetPalette(1)
    r.gStyle.SetPaintTextFormat("1.1f")
    r.gStyle.SetOptFit(0000)
    r.gROOT.SetBatch()

    main(options,args)
##-------------------------------------------------------------------------------------
