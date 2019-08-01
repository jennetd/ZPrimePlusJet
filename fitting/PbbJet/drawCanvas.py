import ROOT as rt

rt.gROOT.SetBatch()
import tdrstyle

tdrstyle.setTDRStyle()
rt.gStyle.SetPadTopMargin(0.10)
rt.gStyle.SetPadLeftMargin(0.16)
rt.gStyle.SetPadRightMargin(0.10)
rt.gStyle.SetPalette(1)
rt.gStyle.SetPaintTextFormat("1.1f")
rt.gStyle.SetOptFit(0000)
rt.gROOT.SetBatch()


c = rt.TCanvas('c','c',500,400)
fd = rt.TFile.Open('fitDiagnostics.root')
for key in fd.GetListOfKeys():
    p = key.ReadObj()
    if p.InheritsFrom('RooPlot'):
        if 'cat1' in key.GetName():
            p.GetXaxis().SetRangeUser(47,201-5*7)
        elif 'cat2' in key.GetName():
            p.GetXaxis().SetRangeUser(47,201-3*7)
        else:
            p.GetXaxis().SetRangeUser(47,201)
        p.GetYaxis().SetRangeUser(0,p.GetMaximum()*1.5)
        p.GetXaxis().SetTitle('m_{SD} (GeV)')

        tag1 = rt.TLatex(0.67, 0.92, "41.5 fb^{-1} (13 TeV)")
        tag1.SetNDC()
        tag1.SetTextFont(42)
        tag1.SetTextSize(0.045)
        tag2 = rt.TLatex(0.2, 0.82, "CMS")
        tag2.SetNDC()
        tag2.SetTextFont(62)
        tag3 = rt.TLatex(0.3, 0.82, "Simulation Preliminary")
        
        ptRange = [450, 1200]
        if 'cat1' in key.GetName():
            ptRange = [450, 500]
        elif 'cat2' in key.GetName():
            ptRange = [500, 550]
        elif 'cat3' in key.GetName():
            ptRange = [550, 600]
        elif 'cat4' in key.GetName():
            ptRange = [600, 675]
        elif 'cat5' in key.GetName():
            ptRange = [675, 800]
        elif 'cat6' in key.GetName():
            ptRange = [800, 1200]
        
        passTag = 'Deep double-b tagger'
        passTag2 = 'Passing region'
        if 'fail' in key.GetName():
            passTag = 'Deep double-b tagger'
            passTag2 = 'Failing region'

        tag4 = rt.TLatex(0.25, 0.77, "%i < p_{T} < %i GeV"%(ptRange[0],ptRange[1]))
        tag4b = rt.TLatex(0.25, 0.72, "%s"%(passTag))
        tag4c = rt.TLatex(0.25, 0.67, "%s"%(passTag2))
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



        p.Draw()
        c.Draw()
        tag1.Draw()
        tag2.Draw()
        tag3.Draw()
        tag4.Draw()
        tag4b.Draw()
        tag4c.Draw()
        c.SaveAs(key.GetName()+'.pdf')
