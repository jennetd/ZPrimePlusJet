import ROOT as rt
import os
from RootIterator import RootIterator

from optparse import OptionParser


poiMap = {'r':"#mu_{H}",
          'r_z':"#mu_{Z}"}
        
catDict = {}
catDict['muonCR','r'] = '#splitline{Combined}{   #scale[0.8]{#mu_{H} = %.1f_{#minus%.1f}^{+%.1f}}}'
catDict['r_cat1','r'] = '#splitline{[450, 500] GeV}{    #scale[0.8]{#mu_{H} = %.1f_{#minus%.1f}^{+%.1f}}}'
catDict['r_cat2','r'] = '#splitline{[500, 550] GeV}{    #scale[0.8]{#mu_{H} = %.1f_{#minus%.1f}^{+%.1f}}}'
catDict['r_cat3','r'] = '#splitline{[550, 600] GeV}{    #scale[0.8]{#mu_{H} = %.1f_{#minus%.1f}^{+%.1f}}}'
catDict['r_cat4','r'] = '#splitline{[600, 675] GeV}{    #scale[0.8]{#mu_{H} = %.1f_{#minus%.1f}^{+%.1f}}}'
catDict['r_cat5','r'] = '#splitline{[675, 800] GeV}{    #scale[0.8]{#mu_{H} = %.1f_{#minus%.1f}^{+%.1f}}}'
catDict['r_cat6','r'] = '#splitline{[800, 1200] GeV}{     #scale[0.8]{#mu_{H} = %.1f_{#minus%.1f}^{+%.1f}}}'
catDict['r_2016','r'] = '#splitline{2016}{     #scale[0.8]{#mu_{H} = %.1f_{#minus%.1f}^{+%.1f}}}'
catDict['r_2017','r'] = '#splitline{2017}{     #scale[0.8]{#mu_{H} = %.1f_{#minus%.1f}^{+%.1f}}}'
catDict['r_2018','r'] = '#splitline{2018}{     #scale[0.8]{#mu_{H} = %.1f_{#minus%.1f}^{+%.1f}}}'

catDict['muonCR','r_z'] = '#splitline{Combined}{   #scale[0.8]{#mu_{Z} = %.2f_{#minus%.2f}^{+%.2f}}}'
catDict['cat1','r_z'] = '#splitline{[450, 500] GeV}{    #scale[0.8]{#mu_{Z} = %.2f_{#minus%.2f}^{+%.2f}}}'
catDict['cat2','r_z'] = '#splitline{[500, 550] GeV}{    #scale[0.8]{#mu_{Z} = %.2f_{#minus%.2f}^{+%.2f}}}'
catDict['cat3','r_z'] = '#splitline{[550, 600] GeV}{    #scale[0.8]{#mu_{Z} = %.2f_{#minus%.2f}^{+%.2f}}}'
catDict['cat4','r_z'] = '#splitline{[600, 675] GeV}{    #scale[0.8]{#mu_{Z} = %.2f_{#minus%.2f}^{+%.2f}}}'
catDict['cat5','r_z'] = '#splitline{[675, 800] GeV}{    #scale[0.8]{#mu_{Z} = %.2f_{#minus%.2f}^{+%.2f}}}'
catDict['cat6','r_z'] = '#splitline{[800, 1200] GeV}{     #scale[0.8]{#mu_{Z} = %.2f_{#minus%.2f}^{+%.2f}}}'

def getRooFitResult(InputIsCCC=False,poi='r',poi_string='r_*'):
    if InputIsCCC:
        f = rt.TFile.Open(options.ifile)
        fit_nominal   = f.Get("fit_nominal")
        fit_alternate = f.Get("fit_alternate")
        if (fit_nominal == 0 or fit_alternate == 0):
            print"Input file ", gFile.GetName(), " does not contain fit_nominal or fit_alternate"
            sys.exit()
        rFit = fit_nominal.floatParsFinal().find(poi)
        rFitChannels = fit_alternate.floatParsFinal().selectByName(poi_string)
        if (rFit == 0):
            print "Nominal fit does not contain parameter ", poi
            sys.exit()
    else:
        f     = rt.TFile.Open(options.ifile)
        fnorm = rt.TFile.Open(options.inorm)
        rFit = fnorm.Get("fit_mdf").floatParsFinal().find(poi)
        rFitChannels = f.Get("fit_mdf").floatParsFinal().selectByName(poi_string)
    return rFit,rFitChannels

def cccPlot(poi = "r", rMin =-10, rMax=15, filename="ccc_r.pdf"):
    c1 = rt.TCanvas("c1")
    c1.SetLeftMargin(0.4)
    c1.SetBottomMargin(0.12)
    c1.SetGridx(1)
    if (rt.gFile == 0):
        print "No input file open"
        sys.exit()

    rFit, rFitChannels = getRooFitResult(InputIsCCC=False,poi='r',poi_string='r_*')

    nChann = len(rFitChannels)

    frame = rt.TH2F("frame",";%s;"%poiMap[poi],1,rMin,rMax,nChann,0,nChann)

    iChann = 0
    points = rt.TGraphAsymmErrors(nChann)
    
    for i in range(0,len(rFitChannels)):
            ri = rFitChannels[i]
            channel = ri.GetName()
            if channel=='muonCR':
                # put at some dummy value
                points.SetPoint(iChann,       100, iChann+0.5)
                points.SetPointError(iChann, -1, 1, 0, 0)
            else:
                points.SetPoint(iChann,       ri.getVal(), iChann+0.5)
                points.SetPointError(iChann, -ri.getAsymErrorLo(), ri.getAsymErrorHi(), 0, 0)
            iChann+=1
            if channel=='muonCR':
                frame.GetYaxis().SetBinLabel(iChann, (catDict[channel,options.poi]%(rFit.getVal(),-rFit.getAsymErrorLo(), rFit.getAsymErrorHi())).replace('-','#minus'))
            else:
                frame.GetYaxis().SetBinLabel(iChann, (catDict[channel,options.poi]%(ri.getVal(),-ri.getAsymErrorLo(), ri.getAsymErrorHi())).replace('-','#minus'))
    points.SetLineColor(rt.kRed)
    points.SetLineWidth(3)
    points.SetMarkerStyle(21)
    frame.GetXaxis().SetTitleSize(0.05)
    frame.GetXaxis().SetLabelSize(0.04)
    frame.GetYaxis().SetLabelSize(0.06)
    frame.Draw()
    rt.gStyle.SetOptStat(0)
    globalFitBand = rt.TBox(rFit.getVal()+rFit.getAsymErrorLo(), 0, rFit.getVal()+rFit.getAsymErrorHi(), nChann)
    globalFitBand.SetFillColor(rt.kGreen)
    globalFitBand.SetLineStyle(0)
    globalFitBand.Draw('')
    globalFitLine = rt.TLine(rFit.getVal(), 0, rFit.getVal(), nChann)
    globalFitLine.SetLineWidth(4)
    globalFitLine.SetLineColor(214)
    globalFitLine.Draw('')
    points.Draw("PZ SAME")
    
    l = rt.TLatex()
    l.SetTextAlign(11)
    l.SetTextSize(0.045)
    l.SetNDC()
    l.SetTextFont(62)
    l.DrawLatex(0.41,0.85,"CMS")
    l.SetTextFont(52)
    l.DrawLatex(0.41,0.8,"Preliminary")
    tag1 = rt.TLatex(0.67,0.92,"%.1f fb^{-1} (13 TeV)"%(options.lumi))
    tag1.SetNDC()
    tag1.SetTextFont(42)
    tag1.SetTextSize(0.045)
    tag1.Draw()
    
    c1.RedrawAxis()
    c1.Print(filename)
    c1.Print(filename.replace('.pdf','.C'))
    c1.Print(filename.replace('.pdf','.png'))

if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option('-b', action='store_true', dest='noX', default=False, help='no X11 windows')
    parser.add_option('--rMin',dest='rMin', default=-10 ,type='float',help='minimum of r (signal strength) in profile likelihood plot')
    parser.add_option('--rMax',dest='rMax', default=15,type='float',help='maximum of r (signal strength) in profile likelihood plot')  
    parser.add_option('--lumi',dest='lumi', default=136.2,type='float',help='lumi')  
    parser.add_option('-i','--ifile',dest='ifile', default='multidimfit.root',type='string',help='multidimfit result')  
    parser.add_option('--inorm',dest='inorm', default='multidimfit_norm.root',type='string',help='norminal multidimfit result')  
    parser.add_option('--tag',dest='tag', default='',type='string',help='tag')  
    
    parser.add_option('-P','--poi'   ,action='store',type='string',dest='poi'   ,default='r', help='poi name')  

    
    (options, args) = parser.parse_args()
    rt.gROOT.SetBatch()
    odir = os.path.dirname(options.ifile)+"/"
    fname = "_".join(filter(None,["ccc",options.poi,options.tag]))
    #cccPlot(options.poi, options.rMin, options.rMax, odir+"ccc_"+options.poi+".pdf")
    cccPlot(options.poi, options.rMin, options.rMax, odir+fname+".pdf")
