#!/usr/bin/env python

import ROOT as r,sys,math,array,os
from ROOT import TFile, TTree, TChain, gPad, gDirectory
from ROOT import *
from multiprocessing import Process
from optparse import OptionParser
from operator import add
import math
import sys
import time
import array


def drawFromhist(hlist,texList,pname,options,drawOpt='',yr=(-1,-1),xr=(-1,-1),outf=''):
   
    colors = [kBlack,kBlue,kRed,kGreen,kMagenta,kViolet,kPink,kOrange] 

    iPos = 0
    iPeriod = 4

    c1 = TCanvas("c1","c1",800,800)
    pad1 = TPad("pad1", "pad1", 0, 0.3, 1, 1.0)
    pad2 = TPad("pad2", "pad2", 0, 0.05, 1, 0.3)
    pad1.SetTopMargin(0.1)
    pad1.SetBottomMargin(0)
    pad2.SetTopMargin(0)
    pad2.SetBottomMargin(0.25)
    pad1.Draw()
    pad2.Draw()
    leg= TLegend(0.6,0.7,0.9,0.9)

    gStyle.SetPaintTextFormat("1.2f")
    gStyle.SetOptStat(0)
    gStyle.SetPalette(55)

    pad1.cd()
    pad1.SetGrid()


    ymaxs = []
    for h in hlist:
        ymaxs.append(h['hist'].GetMaximum())
        leg.AddEntry(h['hist'],h['label'],"lp")
   
    if not hlist[0]['ytitle']=="":    
        hlist[0]['hist'].GetYaxis().SetTitle(hlist[0]['ytitle'])
        print hlist[0]['ytitle']
    hlist[0]['hist'].GetYaxis().SetTitleOffset(0.9)
    hlist[0]['hist'].GetYaxis().SetTitleSize(0.04)
    hlist[0]['hist'].GetXaxis().SetTitleOffset(1.1)
    hlist[0]['hist'].GetXaxis().SetTitleSize(0.1)

    if not yr==(-1,-1):
        ymin,ymax = yr
        hlist[0]['hist'].GetYaxis().SetRangeUser(ymin,ymax)
    else:
        hlist[0]['hist'].GetYaxis().SetRangeUser(1E-1,1.2*max(ymaxs))
        #pad1.SetLogy()
    if not xr==(-1,-1):
        xmin,xmax = xr
        hlist[0]['hist'].GetXaxis().SetRangeUser(xmin,xmax)

    for i,h in enumerate(hlist):
        h['hist'].SetLineColor(h['colors'])
        #h['hist'].SetLineStyle(h['style'])
        h['hist'].SetLineWidth(2)
        h['hist'].SetMarkerColor(h['colors'])

    if options.norm:
        for i,h in enumerate(hlist): h['hist'].Scale(1./h['hist'].Integral())
        

    if drawOpt=="":
        for h in hlist:
            h['hist'].Draw("same")
    else:
        hlist[0]['hist'].Draw('ep')
        for h in hlist[1:]:
            h['hist'].Draw(drawOpt+"same")
    leg.Draw("same") 
    if texList:
        tex=TLatex()
        for t in texList:
            tex.SetTextSize(  t['size'])
            tex.DrawLatexNDC( t['x'],t['y'],t['text'])
        tex.Draw()

    lumi = 41.1
    tag1 = TLatex(0.67,0.92,"%.1f fb^{-1} (13 TeV)"%lumi)
    tag1.SetNDC(); tag1.SetTextFont(42)
    tag1.SetTextSize(0.045)
    tag2 = TLatex(0.15,0.92,"CMS")
    tag2.SetNDC()
    tag2.SetTextFont(62)
    tag3 = TLatex(0.25,0.92,"Simulation Preliminary")
    tag3.SetNDC()
    tag3.SetTextFont(52)
    tag2.SetTextSize(0.055)
    tag3.SetTextSize(0.045)
    tag1.Draw()
    tag2.Draw()
    tag3.Draw()
    pad1.Update()

    if options.ratio:
        pad2.cd()
        ymaxsPad2 = 0
        denomPos = 0
        for i,h in enumerate(hlist):
            h['clone'] = h['hist'].Clone(h['hist'].GetName()+"_ratio")
            if h['denom']:  denomPos =i 
        for i,h in enumerate(hlist):
            h['clone'].Divide(hlist[denomPos]['hist'])
            h['clone'].SetLineColor(h['colors'])
            h['clone'].SetMarkerColor(h['colors'])
        if not hlist[denomPos]['hist'].GetMaximum()==0:
            ymaxsPad2 =  max(ymaxs)/hlist[denomPos]['hist'].GetMaximum()
        hlist[0]['clone'].GetYaxis().SetRangeUser(0,2)
        hlist[0]['clone'].GetYaxis().SetTitle("Ratio")
        hlist[0]['clone'].GetYaxis().SetTitleSize(0.08)
        hlist[0]['clone'].GetYaxis().SetTitleOffset(0.5)
        hlist[0]['clone'].GetYaxis().SetLabelSize(0.07)
        hlist[0]['clone'].GetXaxis().SetLabelOffset(0.03)
        hlist[0]['clone'].GetXaxis().SetLabelSize(0.09)
        for i,h in enumerate(hlist):
            if drawOpt:
                h['clone'].Draw(drawOpt+"same")
            else:
                h['clone'].Draw("same")
            if outf and i != denomPos:
                outf.cd()
                h['clone'].Write(pname)


    c1.Update()
    c1.SaveAs(options.odir+pname+".pdf")
    c1.SaveAs(options.odir+pname+".png")
    #c1.SaveAs(options.odir+pname+".root")


##-------------------------------------------------------------------------------------
def main(options,args):
    #procs    = ['tthqq125','hqq125','whqq125','zhqq125','vbfhqq125']
    procs    = ['wqq','zqq']
    cats     = [ "cat"+str(i+1) for i in range(6)]
    passfail = ['pass','fail']
    upDown   = ['Up']
    allsys      = ['scale']
    colors      = [kRed, kBlue,kGreen,kYellow,kMagenta,kOrange]
   
    #idir1 = 'ddb_Apr17/ddb_M2/TF22_SFJun4/'
    idirs = [
        #{'path':'ddb2016_Jun16/ddb_M2_full/TF22_blind_muonCR_SF2016/', 'suffix':'2016','scale':41.1/35.9},
        #{'path':'ddb_Jun16/ddb_M2_full/TF22_blind_muonCR_SF2016/'    , 'suffix':'2017','scale':1.0},
        #{'path':'ddb2018_Jun16/ddb_M2_full/TF22_blind_muonCR_SF2016/', 'suffix':'2018','scale':41.1/59.2},
       # {'path':'ddb2016_Jun16/ddb_T3_full/TF22_blind_muonCR_config7/', 'suffix':'2016','scale':41.5/35.9},
       # {'path':'ddb_Jun16/ddb_T3_full/TF22_blind_muonCR_config7/'    , 'suffix':'2017','scale':1.0},
        #{'path':'ddb2016_Jun20_v2/ddb_M2_full/TF22_blind_SF2016/', 'suffix':'2016','scale':41.1/35.9},
        #{'path':'ddb_Jun20_v2/ddb_M2_full/TF22_blind_SF2016/'    , 'suffix':'2017','scale':1.0},
        #{'path':'ddb2018_Jun20_v2/ddb_M2_full/TF22_blind_SF2016/', 'suffix':'2018','scale':41.1/59.2},
       # {'path':'ddb2016_Jun20/ddb_M2_full/TF22_blind_muonCR_SF2016/', 'suffix':'2016','scale':41.1/35.9},
       # {'path':'ddb_Jun20/ddb_M2_full/TF22_blind_muonCR_SF2016/'    , 'suffix':'2017','scale':1.0},
       # {'path':'ddb2018_Jun20/ddb_M2_full/TF22_blind_muonCR_SF2016/', 'suffix':'2018','scale':41.1/59.2},
       # {'path':'ddb_Jun21/ddb_M2_full/TF22_blind_muonCR_bbSF1/'    , 'suffix':'2017_BtoF','scale':1.0},
       # {'path':'ddb_Jun24/ddb_M2_full/TF22_blind_muonCR_bbSF1/'    , 'suffix':'2017','scale':1.0},
        {'path':'ddb2016_Jun24_v2/ddb_M2_full/TF22_MC_bbSF1_v6_ewk/'       , 'suffix':'2016 p89','scale':1.0},
        {'path':'ddb2016_Jun24_v2/ddb_M2_full/TF22_MC_muonCR_looserWZ_p80/', 'suffix':'2016 p80','scale':1.0},
        {'path':'ddb_Jun24_v2/ddb_M2_full/TF22_muonCR_bbSF1_v6_ewk/'       , 'suffix':'2017 ','scale':35.9/41.0},
    ]
    tag = 'reg'
    options.norm = False
    options.ratio = True
    tfs = []
    for idir in idirs:
        idir['tf'] =  r.TFile(idir['path']+"validation.root")
    #    tf2 = r.TFile(idir2+"validation.root")
    c1 = TCanvas("c1","c1",800,600)
    c2 = TCanvas("c2","c2",800,600)
    for proc in procs:
        for cat in cats:
            for pf in passfail:
                hlist = []
                tlist = []
                norm = "_".join([proc,pf,cat])
                print "getting histogram with name", norm
                for i,idir in enumerate(idirs):
                    h_norm = idir['tf'].Get(norm)
                    h_norm.SetDirectory(0)
                    if 'scale' in idir.keys():  
                        h_norm.Scale(idir['scale'])
                    if i ==0: denom = True
                    else    : denom = False
                    d = {'hist':h_norm,'colors':colors[i],'ytitle':'','label':h_norm.GetName()+"_"+idir['suffix'],'denom':denom}
                    hlist.append(d)
                    tlist.append( {'text':"mean =%.3f, integral= %.1f"%(h_norm.GetMean(),h_norm.Integral()),'x':0.5,'y':0.6-i*0.04,'size':0.04})
                #h_norm2 = tf2.Get(norm)
                ##d = {'hist':h_norm2,'colors':kRed,'ytitle':'','label':h_norm.GetName()+"_shifted",'denom':True}
                #d = {'hist':h_norm2,'colors':kRed,'ytitle':'','label':h_norm.GetName()+"_2017",'denom':True}
                #tlist.append( {'text':"shifted mean=%.3f, integral= %.1f"%(h_norm2.GetMean(),h_norm2.Integral()),'x':0.5,'y':0.6-0.05,'size':0.04})
                #hlist.append(d)
                name = "_".join(filter(None,[h_norm.GetName(),tag]))
                drawFromhist(hlist,tlist,name,options,"hist",(-1,-1),(-1,-1))
            hsum = []
            tlist = []
            for i,idir in enumerate(idirs):
                norm = "_".join([proc,'pass',cat])
                h_pass = idir['tf'].Get(norm).Clone(norm.replace("pass",'sum'))
                h_fail = idir['tf'].Get(norm.replace("pass","fail"))
                print h_pass.GetName(),h_fail.GetName()
                h_pass.Add(h_fail)
                if 'scale' in idir.keys():  
                    h_pass.Scale(idir['scale'])
                d = {'hist':h_pass,'colors':colors[i],'ytitle':'','label':h_pass.GetName()+"_"+idir['suffix'],'denom':denom}
                hsum.append(d)
                name = "_".join(filter(None,[h_pass.GetName(),tag]))
                tlist.append( {'text':"mean =%.3f, integral= %.1f"%(h_pass.GetMean(),h_pass.Integral()),'x':0.5,'y':0.6-i*0.04,'size':0.04})
                drawFromhist(hsum,tlist,name,options,"hist",(-1,-1),(-1,-1))

    for proc in procs:
        for pf in passfail+['sum']:
            name = "_".join(filter(None,[proc,pf,'*',tag]))
            merge(name)

def merge(tag):
    cmd = ' montage -density 500 -tile 3x0 -geometry 800x800 -border 10'
    cmd += " %s%s.png"%(options.odir, tag)
    cmd += " %s%s.pdf"%(options.odir, tag.replace('_*',''))
    print cmd
    os.system(cmd)
    cmd = "rm %s%s*.png"%(options.odir, tag)
    print cmd
    os.system(cmd)

##-------------------------------------------------------------------------------------
if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option('-b', action='store_true', dest='noX', default=False, help='no X11 windows')
    parser.add_option("--lumi", dest="lumi", type=float, default = 30,help="luminosity", metavar="lumi")
    parser.add_option('-i','--idir', dest='idir', default = 'data/',help='directory with data', metavar='idir')
    parser.add_option('-o','--odir', dest='odir', default = 'plots/',help='directory to write plots', metavar='odir')
    parser.add_option('-s','--suffix', dest='suffix', default = '',help='directory to write plots', metavar='suffix')

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
    
    main(options,args)
##-------------------------------------------------------------------------------------
