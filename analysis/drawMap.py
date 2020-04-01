from ROOT import *
import tdrstyle,CMS_lumi,os
from array import array

def drawMap(h,year):
    gStyle.SetPadLeftMargin(0.15)
    gStyle.SetPadRightMargin(0.18)

    gStyle.SetPaintTextFormat("1.2f")
    gStyle.SetOptStat(0)
    #gStyle.SetPalette(55)

    c1 = TCanvas("c1","c1",800,600)

    h.GetXaxis().SetTitleSize(0.05)
    h.GetYaxis().SetTitleSize(0.05)
    h.GetXaxis().SetTitleOffset(1)
    h.GetYaxis().SetTitleOffset(1.2)
    h.GetXaxis().SetLabelSize(0.045)
    h.GetYaxis().SetLabelSize(0.045)
    h.GetZaxis().SetLabelSize(0.045)
    h.GetZaxis().SetTitleSize(0.05)
    h.GetZaxis().SetTitleOffset(1.2)

    h.GetXaxis().SetTitle("#rho")
    h.GetYaxis().SetTitle("p_{T} (GeV)")
    h.GetZaxis().SetTitle("X_{26%}")
    h.GetZaxis().SetTitleOffset(1.2)
    h.GetZaxis().SetRangeUser(0.15,0.35)
    h.GetXaxis().SetRangeUser(-6,-2.1)
    h.GetYaxis().SetRangeUser(400,1000)
    h.SetTitle("")
    h.Draw("colz same")

    tag1 = TLatex(0.67,0.92,"%s (13 TeV)"%year)
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

    c1.SaveAs("n2ddtmap_%s.pdf"%year)

gStyle.SetPadTopMargin(0.10)
gStyle.SetPadLeftMargin(0.16)
gStyle.SetPadRightMargin(0.22)
gStyle.SetPaintTextFormat("1.1f")
gStyle.SetOptStat(0000)
gStyle.SetOptFit(0000)
gROOT.SetBatch()

#ROOT.gStyle.SetPalette(ROOT.kBlackBody)
#ROOT.gStyle.SetPalette(ROOT.kBird)    
stops = [ 0.0, 1.0]
red =   [ 1.0, 0.3]
green = [ 1.0, 0.3]
blue =  [ 1.0, 1.0]

s = array('d', stops)
r = array('d', red)
g = array('d', green)
b = array('d', blue)

npoints = len(s)
TColor.CreateGradientColorTable(npoints, s, r, g, b, 999)

gStyle.SetNumberContours(999)


gROOT.SetBatch()
f = TFile('ggH/n2ddtmap_2018bits_GaussianSmoothing1Sigma_CorrectVersion.root')
h = f.Get('Rho2D')
drawMap(h,'2018')


f = TFile('ggH/Output_smooth_2017MC.root')
h = f.Get('Rho2D')
drawMap(h,'2017')


f = TFile('GridOutput_v13_WP026.root')
h = f.Get('Rho2D')
drawMap(h,'2016')


