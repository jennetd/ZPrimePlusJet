from ROOT import *
import itertools
from optparse import OptionParser
import tdrstyle,CMS_lumi,os


def GetChain(h, f,xsec,lumi,branch,selection='',treeName='Events'):
    chain = TChain(treeName)
    chain.Add(f)
    if 'w12j' in f:
        #kfactor = "67.6/10.8/(10000.*(1094.))"
        kfactor = "67.6/10.8"
        if selection: 
            nevt = chain.Draw("%s>>%s"%(branch,h.GetName()),'fEvtWeight*%s*%s'%(kfactor,selection))
            print "pass selection = " ,nevt, ' all evt = ',chain.GetEntries(),' nNorm = ',(10000.*(1094.))
            h.Scale(lumi/(10000.*1094.*nevt/chain.GetEntries()))  #scaled down by fraction
        else:
            chain.Draw("%s>>%s"%(branch,h.GetName()),'fEvtWeight*%s'%kfactor)
            h.Scale(lumi/(10000.*(1094.)))
    elif 'z12j' in f:
        kfactor = "0.6991/0.2*3.0*(1./1.73)"
        if selection: 
            nevt = chain.Draw("%s>>%s"%(branch,h.GetName()),'fEvtWeight*%s*%s'%(kfactor,selection))
            print "pass selection = " ,nevt, ' all evt = ',chain.GetEntries()
            h.Scale(lumi/nevt)
        else:
            chain.Draw("%s>>%s"%(branch,h.GetName()),'fEvtWeight*%s'%kfactor)
            h.Scale(lumi/chain.GetEntries())
    elif 'skim' in f or 'Output' in f: 
        ##baconbits#
        if selection: 
            nevt = chain.Draw("%s>>%s"%(branch,h.GetName()),'scale1fb*%s'%selection)
            print "pass selection = " ,nevt, ' all evt = ',chain.GetEntries()
            h.Scale(lumi*xsec/nevt)
        else:
            chain.Draw("%s>>%s"%(branch,h.GetName()),'scale1fb')
            h.Scale(lumi*xsec/chain.GetEntries())
    else:
        ###Phil's LO files 
        if selection: 
            nevt = chain.Draw("%s>>%s"%(branch,h.GetName()),'fEvtWeight*%s'%selection)
            print "pass selection = " ,nevt, ' all evt = ',chain.GetEntries()
            h.Scale(lumi*xsec/nevt)
        else:
            chain.Draw("%s>>%s"%(branch,h.GetName()),'fEvtWeight')
            h.Scale(lumi*xsec/chain.GetEntries())

    print h.GetName(), h.Integral() 
    return h

def SetColor(h,color):
    h.SetLineColor(color)
    h.SetMarkerColor(color)
    return

def drawFromhist(hlist,texList,pname,options,drawOpt='',yr=(-1,-1),xr=(-1,-1),outf=''):
   
    colors = [kBlack,kBlue,kRed,kGreen,kMagenta,kViolet,kPink,kOrange] 
    CMS_lumi.lumi_13TeV = "59.9/fb"
    CMS_lumi.writeExtraText = 1
    CMS_lumi.extraText = "      Preliminary"
    CMS_lumi.lumi_sqrtS = "13 TeV" # used with iPeriod = 0, e.g. for simulation-only plots (default is an empty string)

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


    #CMS_lumi.CMS_lumi(pad1, iPeriod, iPos)
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
        h['hist'].SetLineStyle(h['style'])
        h['hist'].SetLineWidth(2)
        h['hist'].SetMarkerColor(h['colors'])

    if options.norm:
        for i,h in enumerate(hlist): h['hist'].Scale(1./h['hist'].Integral())
        

    if drawOpt=="":
        #hlist[0]['hist'].Draw("AP")
        #print "drawing with AP"
        #for h in hlist[1:]:
        #    h['hist'].Draw("APsame")
        for h in hlist:
            h['hist'].Draw("same")
    else:
        hlist[0]['hist'].Draw(drawOpt)
        for h in hlist[1:]:
            h['hist'].Draw(drawOpt+"same")
    leg.Draw("same") 
    if texList:
        tex=TLatex()
        for t in texList:
            tex.SetTextSize(  t['size'])
            tex.DrawLatexNDC( t['x'],t['y'],t['text'])
        tex.Draw()

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
        #hlist[0]['clone'].GetYaxis().SetRangeUser(0,2)
        hlist[0]['clone'].GetYaxis().SetRangeUser(0.6,1.3)
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
    #c1.SaveAs(options.odir+pname+".root")

def getControlPlot(tf_path,year,tag,plot):
    tf = TFile(tf_path)
    print "Getting from %s histgram with %s"%(tf_path,plot)
    h_V = tf.Get(plot)
    h_V.SetDirectory(0)
    h_V.SetName(h_V.GetName()+"_"+year+"_"+tag)

    pt450  = h_V.FindBin(450.0)
    pt500  = h_V.FindBin(500.0)
    pt550  = h_V.FindBin(550.0)
    pt600  = h_V.FindBin(600.0)
    pt675  = h_V.FindBin(675.0)
    pt800  = h_V.FindBin(800.0)
    pt1000 = h_V.FindBin(1000.0)


    if year=='2017':
        h_V.Scale(lumi/41.5)
    elif year=='2016':
        h_V.Scale(lumi/35.9)
    elif year=='2018':
        h_V.Scale(lumi/53.8)

    #print 'cat 1 = %s'%h_V.Integral(pt450,pt500)
    #print 'cat 2 = %s'%h_V.Integral(pt500,pt550)
    #print 'cat 3 = %s'%h_V.Integral(pt550,pt600)
    #print 'cat 4 = %s'%h_V.Integral(pt600,pt675)
    #print 'cat 5 = %s'%h_V.Integral(pt675,pt800)
    #print 'cat 6 = %s'%h_V.Integral(pt800,pt1000)

    return h_V


def applyCorr(h_NLO,h_EWK):
    for i in range(0,h_NLO.GetNbinsX()+1):
        x     = h_NLO.GetBinCenter(i)
        y,ey  = h_NLO.GetBinContent(i), h_NLO.GetBinError(i)

        i_ewk = h_EWK.FindBin(x)
        ewk_corr     = h_EWK.GetBinContent(i_ewk)
        ewk_corr_err = h_EWK.GetBinError(i_ewk)
        
        h_NLO.SetBinContent(i, y * ewk_corr)
        h_NLO.SetBinError(i, (ey*ey + ewk_corr_err*ewk_corr_err)**0.5)
    

def getEWK(proc='W'):
    f_kfactors = TFile.Open(os.path.expandvars("$ZPRIMEPLUSJET_BASE/analysis/ggH/kfactors.root"), "read")
    hQCD_Z = f_kfactors.Get('ZJets_012j_NLO/nominal')
    hQCD_W = f_kfactors.Get('WJets_012j_NLO/nominal')
    hLO_Z = f_kfactors.Get('ZJets_LO/inv_pt')
    hLO_W = f_kfactors.Get('WJets_LO/inv_pt')
    hEWK_Z = f_kfactors.Get('EWKcorr/Z')
    hEWK_W = f_kfactors.Get('EWKcorr/W')
    hQCD_Z.SetDirectory(0)
    hQCD_W.SetDirectory(0)
    hLO_Z.SetDirectory(0)
    hLO_W.SetDirectory(0)
    hEWK_Z.SetDirectory(0)
    hEWK_W.SetDirectory(0)
    
    hEWK_Z.Divide(hQCD_Z);
    hEWK_W.Divide(hQCD_W);
    hQCD_Z.Divide(hLO_Z);
    hQCD_W.Divide(hLO_W);

    if proc=='W':
        return hEWK_W
    elif proc=='Z':
        return hEWK_Z
    else:
        print "invalid proc"
        return 1
        sys.exit()

def LOcomparison():
    ## LO comparisions
    ymax = h_W_2017.GetBinContent(h_W_2017.FindBin(400))*1.2
    hlist = [
         {"hist":h_wraw_2017,'colors':kGreen,'style':1, 'ytitle':"",  'label':'W 2017(no kfactor)','denom':False},
         {"hist":h_w_lo_400,'colors':kGreen,'style':3, 'ytitle':"",  'label':'W LO','denom':True},
    ]
    drawFromhist(hlist,[],"W_LO",options,"hist",(0,ymax),(400,1000))
    hlist = [
         {"hist":h_W_2017,'colors':kBlue ,'style':1, 'ytitle':"",  'label':'W 2017(w/ kfactor)','denom':False},
         {"hist":h_w_nlo_qcd,'colors':kBlue ,'style':3, 'ytitle':"",  'label':'W NLO','denom':True},
    ]
    drawFromhist(hlist,[],"W_NLO",options,"hist",(0,ymax),(400,1000))

    ymax = h_z_2017.GetBinContent(h_z_2017.FindBin(400))*1.2
    hlist = [
         {"hist":h_zraw_400_2017,'colors':kGreen,'style':1, 'ytitle':"",  'label':'Z 2017(no kfactor)','denom':True},
         {"hist":h_z_lo_400,'colors':kGreen,'style':3, 'ytitle':"",  'label':'Z LO','denom':False},
    ]
    drawFromhist(hlist,[],"Z_LO",options,"hist",(0,ymax),(400,1000))
    hlist = [
         {"hist":h_z_2017,  'colors':kBlue ,'style':1, 'ytitle':"",  'label':'Z 2017(w/ kfactor)','denom':True},
         {"hist":h_z_nlo_qcd,   'colors':kBlue,'style':3, 'ytitle':"",  'label':'Z NLO','denom':False},
    ]
    drawFromhist(hlist,[],"Z_NLO",options,"hist",(0,ymax),(400,1000))

def reweight():
    
    f_z_nlo = TFile("./ggH/ZJets_QCD_NLO.root","RECREATE")
    f_w_nlo = TFile("./ggH/WJets_QCD_NLO.root","RECREATE")
    ### Reweighting
    h_wraw_400_2017.Rebin(4)  ## courser binning => 40GeV 
    h_wraw_2016.Rebin(4)  ## courser binning => 40GeV 
    h_zraw_400_2017.Rebin(4)  ## courser binning => 40GeV 
    h_zraw_2016.Rebin(4)  ## courser binning => 40GeV 
    h_w_nlo_qcd.Rebin(4)  ## courser binning => 40GeV 
    h_z_nlo_qcd.Rebin(4)  ## courser binning => 40GeV 

    ptMin = 200
    ymax = h_wraw_400_2017.GetBinContent(h_wraw_400_2017.FindBin(ptMin))*1.2
    hlist = [
         {"hist":h_wraw_400_2017,'colors':kGreen,'style':1, 'ytitle':"",  'label':'W 2017(no kfactor)','denom':True},
         {"hist":h_w_nlo_qcd,'colors':kBlue ,'style':1, 'ytitle':"",  'label':'W NLO','denom':False},
    ]
    drawFromhist(hlist,[],"W_NLO_QCD_2017",options,"hist",(0,ymax),(ptMin,1000),f_w_nlo)
    hlist = [
         {"hist":h_wraw_2016,'colors':kGreen,'style':1, 'ytitle':"",  'label':'W 2016(no kfactor)','denom':True},
         {"hist":h_w_nlo_qcd,'colors':kBlue ,'style':1, 'ytitle':"",  'label':'W NLO','denom':False},
    ]
    drawFromhist(hlist,[],"W_NLO_QCD_2016",options,"hist",(0,ymax),(ptMin,1000),f_w_nlo)

    ymax = h_zraw_400_2017.GetBinContent(h_zraw_400_2017.FindBin(ptMin))*1.2
    hlist = [
         {"hist":h_zraw_400_2017,'colors':kGreen,'style':1, 'ytitle':"",  'label':'Z 2017(no kfactor)','denom':True},
         {"hist":h_z_nlo_qcd,'colors':kBlue ,'style':1, 'ytitle':"",  'label':'Z NLO','denom':False},
    ]
    drawFromhist(hlist,[],"Z_NLO_QCD_2017",options,"hist",(0,ymax),(ptMin,1000),f_z_nlo)
    hlist = [
         {"hist":h_zraw_2016,'colors':kGreen,'style':1, 'ytitle':"",  'label':'Z 2016(no kfactor)','denom':True},
         {"hist":h_z_nlo_qcd,'colors':kBlue ,'style':1, 'ytitle':"",  'label':'Z NLO','denom':False},
    ]
    drawFromhist(hlist,[],"Z_NLO_QCD_2016",options,"hist",(0,ymax),(ptMin,1000),f_z_nlo)


if __name__ == '__main__':

    gROOT.SetBatch()
    gStyle.SetPalette(1)
    gStyle.SetOptFit(0000)
    tdrstyle.setTDRStyle()
    gStyle.SetPadTopMargin(0.20)
    gStyle.SetPadLeftMargin(0.13)
    gStyle.SetPadRightMargin(0.10)
    gStyle.SetPaintTextFormat("1.1f")
    gStyle.SetOptFit(0000)


    parser = OptionParser()
    parser.add_option('-o','--odir', dest='odir', default = 'checkVqq/May28/',help='directory to write plots', metavar='odir')
    parser.add_option("--lumi", dest="lumi", default = 35.9,type=float,help="luminosity", metavar="lumi")

    (options, args) = parser.parse_args()

    colors = [kRed,kBlue,kYellow,kGreen,kMagenta,kOrange]

    options.norm=False
    options.ratio=True
 
    gStyle.SetHistLineWidth(2)
    hsumw =TH1D("sumw", "", 1, 0, 1)

    #lumi = 35.9
    lumi =1.0 

    h_w_nlo_qcd = TH1D('h_w_nlo_qcd','h_w_nlo_qcd',100,0,1000)
    h_z_nlo_qcd = TH1D('h_z_nlo_qcd','h_z_nlo_qcd',100,0,1000)
    h_w_lo_400 = TH1D('h_w_lo_400','h_w_lo_400',100,0,1000)
    h_w_lo_600 = TH1D('h_w_lo_600','h_w_lo_600',100,0,1000)
    h_w_lo_800 = TH1D('h_w_lo_800','h_w_lo_800',100,0,1000)
    h_z_lo_400 = TH1D('h_z_lo_400','h_z_lo_400',100,0,1000)
    h_z_lo_600 = TH1D('h_z_lo_600','h_z_lo_600',100,0,1000)
    h_z_lo_800 = TH1D('h_z_lo_800','h_z_lo_800',100,0,1000)

    h_wraw_2016    = TH1D('h_wraw_2016'    ,'h_wraw_2016'    ,100,0,1000)
    h_zraw_2016    = TH1D('h_zraw_2016'    ,'h_zraw_2016'    ,100,0,1000)
    h_wraw_400_2017= TH1D('h_wraw_400_2017','h_wraw_400_2017',100,0,1000)
    h_zraw_400_2017= TH1D('h_zraw_400_2017','h_zraw_400_2017',100,0,1000)
    h_wraw_600_2017= TH1D('h_wraw_600_2017','h_wraw_600_2017',100,0,1000)
    h_zraw_600_2017= TH1D('h_zraw_600_2017','h_zraw_600_2017',100,0,1000)
    h_wraw_800_2017= TH1D('h_wraw_800_2017','h_wraw_800_2017',100,0,1000)
    h_zraw_800_2017= TH1D('h_zraw_800_2017','h_zraw_800_2017',100,0,1000)
    
    ##### Phil's NLO files
    #h_w_nlo_qcd  = GetChain(h_w_nlo_qcd,'ggH/Comb_w12j.root',56.3582,lumi*1000,'fVPt','(v_m>40)' )
    #h_z_nlo_qcd  = GetChain(h_z_nlo_qcd,'ggH/z12j_v2.root'  ,22.2833,lumi*1000,'fVPt','(v_m>40)' )
    #h_w_nlo_ewk = h_w_nlo_qcd.Clone('h_w_nlo_ewk') 
    #h_z_nlo_ewk = h_z_nlo_qcd.Clone('h_z_nlo_ewk')
    #hEWK_W             = getEWK('W')
    #hEWK_Z             = getEWK('Z')
    #applyCorr(h_w_nlo_ewk,hEWK_W)
    #applyCorr(h_z_nlo_ewk,hEWK_Z)
   
    #### Phil's LO files 
    #h_w_lo_400  = GetChain(h_w_lo_400,'ggH/wqq_ht400.root',315.6,lumi*1000,'fVPt','(v_m>40)')
    #h_w_lo_600  = GetChain(h_w_lo_600,'ggH/wqq_ht600.root',68.57,lumi*1000,'fVPt','(v_m>40)')
    #h_w_lo_800  = GetChain(h_w_lo_800,'ggH/wqq_ht800.root',34.9,lumi*1000,'fVPt' ,'(v_m>40)')
    #
    #h_z_lo_400  = GetChain(h_z_lo_400,'ggH/zqq_ht400.root',145.4,lumi*1000,'fVPt','(v_m>40)')
    #h_z_lo_600  = GetChain(h_z_lo_600,'ggH/zqq_ht600.root',34.0 ,lumi*1000,'fVPt','(v_m>40)')
    #h_z_lo_800  = GetChain(h_z_lo_800,'ggH/zqq_ht800.root',18.67,lumi*1000,'fVPt','(v_m>40)')

    h_w_lo_400.Add(h_w_lo_600)
    h_w_lo_400.Add(h_w_lo_800)
    h_z_lo_400.Add(h_z_lo_600)
    h_z_lo_400.Add(h_z_lo_800)

  
    # from checkVqqMay20  baconbit 13,14,15
    #tf_raw = TFile("checkVqq/May28/Vpt.root")

    #Baconbits
    tf2016zqq         ='/eos/uscms/store/user/lpcbacon/dazsle/zprimebits-v15.03/skim/oldDYJets/DYJetsToQQ_HT180_13TeV_*.root'
    tf2016wqq         ='/eos/uscms/store/user/lpcbacon/dazsle/zprimebits-v15.03/skim/oldWJets/WJetsToQQ_HT180_13TeV_*.root'
    tf2017wqq_400_600 ='/eos/uscms/store/user/lpcbacon/dazsle/zprimebits-v15.04/skim/WJetsToQQ_HT400to600_qc19_3j_TuneCP5_13TeV_*.root'
    tf2017wqq_600_800 ='/eos/uscms/store/user/lpcbacon/dazsle/zprimebits-v15.04/skim/WJetsToQQ_HT600to800_qc19_3j_TuneCP5_13TeV_*.root'
    tf2017wqq_800     ='/eos/uscms/store/user/lpcbacon/dazsle/zprimebits-v15.04/skim/WJetsToQQ_HT-800toInf_qc19_3j_TuneCP5_13TeV_0.root'
    tf2017zqq_600_800 ='/eos/uscms/store/user/lpcbacon/dazsle/zprimebits-v15.04/skim/ZJetsToQQ_HT600to800_qc19_4j_TuneCP5_13TeV_*.root'
    tf2017zqq_400_600 ='/eos/uscms/store/user/lpcbacon/dazsle/zprimebits-v15.04/skim/ZJetsToQQ_HT400to600_qc19_4j_TuneCP5_13TeV_*.root'
    tf2017zqq_800     ='/eos/uscms/store/user/lpcbacon/dazsle/zprimebits-v15.04/skim/ZJetsToQQ_HT-800toInf_qc19_4j_TuneCP5_13TeV_0.root'

    #tf2016zqq         ='/eos/uscms/store/user/lpcbacon/dazsle/zprimebits-v15.03/DYJetsToQQ_HT180_13TeV/Output_job*.root'
    #tf2016wqq         ='/eos/uscms/store/user/lpcbacon/dazsle/zprimebits-v15.03/WJetsToQQ_HT180_13TeV/Output_job*.root'
    #tf2017wqq_400_600 ='/eos/uscms/store/user/lpcbacon/dazsle/zprimebits-v15.04/WJetsToQQ_HT400to600_qc19_3j_TuneCP5_13TeV/Output_job*.root'
    #tf2017wqq_600_800 ='/eos/uscms/store/user/lpcbacon/dazsle/zprimebits-v15.04/WJetsToQQ_HT600to800_qc19_3j_TuneCP5_13TeV/Output_job*.root'
    #tf2017wqq_800     ='/eos/uscms/store/user/lpcbacon/dazsle/zprimebits-v15.04/WJetsToQQ_HT-800toInf_qc19_3j_TuneCP5_13TeV/Output_job*.root'
    #tf2017zqq_600_800 ='/eos/uscms/store/user/lpcbacon/dazsle/zprimebits-v15.04/ZJetsToQQ_HT600to800_qc19_4j_TuneCP5_13TeV/Output_job*.root'
    #tf2017zqq_400_600 ='/eos/uscms/store/user/lpcbacon/dazsle/zprimebits-v15.04/ZJetsToQQ_HT400to600_qc19_4j_TuneCP5_13TeV/Output_job*.root'
    #tf2017zqq_800     ='/eos/uscms/store/user/lpcbacon/dazsle/zprimebits-v15.04/ZJetsToQQ_HT-800toInf_qc19_4j_TuneCP5_13TeV/Output_job*.root'


    Reweight = False 
    #h_wraw_2016     = GetChain(h_wraw_2016,tf2016wqq        ,2778 ,lumi*1000.0,'genVPt','(genVMass>40)','otree')
    #h_zraw_2016     = GetChain(h_zraw_2016,tf2016zqq        ,1187 ,lumi*1000.0,'genVPt','(genVMass>40)','otree')

    #h_wraw_400_2017  = GetChain(h_wraw_400_2017,tf2017wqq_400_600,315.6,lumi*1000.0,'genVPt','(genVMass>40)','otree')
    #h_wraw_600_2017  = GetChain(h_wraw_600_2017,tf2017wqq_600_800,68.57,lumi*1000.0,'genVPt','(genVMass>40)','otree')
    #h_wraw_800_2017  = GetChain(h_wraw_800_2017,tf2017wqq_800    ,34.9 ,lumi*1000.0,'genVPt','(genVMass>40)','otree')
    #                            
    #h_zraw_400_2017  = GetChain(h_zraw_400_2017,tf2017zqq_400_600,145.4,lumi*1000.0,'genVPt','(genVMass>40)','otree')
    #h_zraw_600_2017  = GetChain(h_zraw_600_2017,tf2017zqq_600_800,34.0 ,lumi*1000.0,'genVPt','(genVMass>40)','otree')
    #h_zraw_800_2017  = GetChain(h_zraw_800_2017,tf2017zqq_800    ,18.67,lumi*1000.0,'genVPt','(genVMass>40)','otree')

    #h_wraw_400_2017.Add(h_wraw_600_2017)
    #h_wraw_400_2017.Add(h_wraw_800_2017)
    #h_zraw_400_2017.Add(h_zraw_600_2017)
    #h_zraw_400_2017.Add(h_zraw_800_2017)

    #f_z_nlo = TFile("./ggH/ZJets_QCD_NLO.root")
    #f_w_nlo = TFile("./ggH/WJets_QCD_NLO.root")
    #h_wraw_2016_ewk = h_wraw_2016.Clone('h_wraw_2016_ewk')
    #h_zraw_2016_ewk = h_zraw_2016.Clone('h_zraw_2016_ewk')
    #h_wraw_2016_qcd = h_wraw_2016.Clone('h_wraw_2016_qcd')
    #h_zraw_2016_qcd = h_zraw_2016.Clone('h_zraw_2016_qcd')
    #applyCorr(h_wraw_2016_ewk,hEWK_W)
    #applyCorr(h_zraw_2016_ewk,hEWK_Z)
    #applyCorr(h_wraw_2016_qcd,f_w_nlo.Get("W_NLO_QCD_2016"))
    #applyCorr(h_zraw_2016_qcd,f_z_nlo.Get("Z_NLO_QCD_2016"))

    #h_wraw_400_2017_ewk = h_wraw_400_2017.Clone('h_wraw_400_2017_ewk')
    #h_zraw_400_2017_ewk = h_zraw_400_2017.Clone('h_zraw_400_2017_ewk')
    #h_wraw_400_2017_qcd = h_wraw_400_2017.Clone('h_wraw_400_2017_qcd')
    #h_zraw_400_2017_qcd = h_zraw_400_2017.Clone('h_zraw_400_2017_qcd')
    ##
    #applyCorr(h_wraw_400_2017_ewk,hEWK_W)
    #applyCorr(h_zraw_400_2017_ewk,hEWK_Z)
    #applyCorr(h_wraw_400_2017_qcd,f_w_nlo.Get("W_NLO_QCD_2017"))
    #applyCorr(h_zraw_400_2017_qcd,f_z_nlo.Get("Z_NLO_QCD_2017"))
    #f_z_nlo.Close()
    #f_w_nlo.Close()

    ## Jun10 = Zprime2017 reweighting
    #tf2017 = TFile("ddb_Jun10/MC/Plots_1000pb_weighted.root")
    ## May21 = 2016 preApp reweighting
    #tf2016 = TFile("ddb2016_May21_v2/MC/Plots_1000pb_weighted.root")
    ## 400-1000 reweight
    #tf2017 = TFile("ddb_Jun12/MC/Plots_1000pb_weighted.root")
    #tf2016 = TFile("ddb2016_Jun12/MC/Plots_1000pb_weighted.root")
    ## correct reweighting

    tfs = [
      {'tf' :'ddb_Jun10/MC/Plots_1000pb_weighted.root'    , 'year':'2017','tag':'zprime'},
      {'tf' :'ddb_Apr17/MC/Plots_1000pb_weighted.root'    , 'year':'2017','tag':'preApp'},
      {'tf' :'ddb2016_Jun16/MC/Plots_1000pb_weighted.root', 'year':'2016','tag':'preApp'},
      {'tf' :"ddb_Jun16/MC/Plots_1000pb_weighted.root"    , 'year':'2017','tag':'new'},
      {'tf' :"ddb2016_Jun16/MC/Plots_1000pb_weighted.root", 'year':'2016','tag':'new'},
    ]
    
    Z_kfactor ="h_DY_fBosonPt_weight"         ;
    Z_PUweight ="h_DY_fBosonPt_PUweight"      ;
    Z_trigweight ="h_DY_fBosonPt_trigWeight"  ;
    W_kfactor    ="h_W_fBosonPt_weight"
    W_PUweight   ="h_W_fBosonPt_PUweight"
    W_trigweight ="h_W_fBosonPt_trigWeight" 

    h_W_2017_zprime  =getControlPlot( 'ddb_Jun10/MC/Plots_1000pb_weighted.root', '2017', 'zprime' ,W_kfactor)
    h_Z_2017_zprime  =getControlPlot( 'ddb_Jun10/MC/Plots_1000pb_weighted.root', '2017', 'zprime' ,Z_kfactor)
    h_W_2017_preApp  =getControlPlot( 'ddb_Apr17/MC/Plots_1000pb_weighted.root', '2017', 'preApp' ,W_kfactor)
    h_Z_2017_preApp  =getControlPlot( 'ddb_Apr17/MC/Plots_1000pb_weighted.root', '2017', 'preApp' ,Z_kfactor)
    h_W_2016_preApp  =getControlPlot( 'ddb2016_May21_v2/MC/Plots_1000pb_weighted.root', '2016', 'preApp' ,W_kfactor)
    h_Z_2016_preApp  =getControlPlot( 'ddb2016_May21_v2/MC/Plots_1000pb_weighted.root', '2016', 'preApp' ,Z_kfactor)

    h_W_2016_fix  =getControlPlot( 'ddb2016_Jun16/MC/Plots_1000pb_weighted.root', '2016', tag='new' ,plot=W_kfactor)
    h_Z_2016_fix  =getControlPlot( 'ddb2016_Jun16/MC/Plots_1000pb_weighted.root', '2016', tag='new' ,plot=Z_kfactor)
    
    h_W_2016_PU =getControlPlot( 'ddb2016_Jun24/MC/Plots_1000pb_weighted.root', '2016', tag='Jun24' ,plot=W_PUweight)
    h_W_2017_PU =getControlPlot( 'ddb_Jun24/MC/Plots_1000pb_weighted.root', '2017', tag='Jun24' ,plot=W_PUweight)
    h_Z_2016_PU =getControlPlot( 'ddb2016_Jun24/MC/Plots_1000pb_weighted.root', '2016', tag='Jun24' ,plot=Z_PUweight)
    h_Z_2017_PU =getControlPlot( 'ddb_Jun24/MC/Plots_1000pb_weighted.root', '2017', tag='Jun24' ,plot=Z_PUweight)

    #h_W_2016_trig =getControlPlot( 'ddb2016_Jun24/MC/Plots_1000pb_weighted.root', '2016', tag='Jun24' ,plot=W_trigweight)
    #h_W_2017_trig =getControlPlot( 'ddb_Jun24/MC/Plots_1000pb_weighted.root', '2017', tag='Jun24' ,plot=W_trigweight)
    #h_Z_2016_trig =getControlPlot( 'ddb2016_Jun24/MC/Plots_1000pb_weighted.root', '2016', tag='Jun24' ,plot=Z_trigweight)
    #h_Z_2017_trig =getControlPlot( 'ddb_Jun24/MC/Plots_1000pb_weighted.root', '2017', tag='Jun24' ,plot=Z_trigweight)
    
    #h_W_2017_fix  =getControlPlot( 'ddb_Jun16/MC/Plots_1000pb_weighted.root', '2017', tag='new' ,plot=W_kfactor)
    #h_Z_2017_fix  =getControlPlot( 'ddb_Jun16/MC/Plots_1000pb_weighted.root', '2017', tag='new' ,plot=Z_kfactor)

    h_ddb2017 = TH1D("h_ddb_2017",'h_ddb_2017',100,0,1)
    h_ddb2016 = TH1D("h_ddb_2016",'h_ddb_2016',100,0,1)
    h_zraw_2016     = GetChain(h_ddb2016,tf2016zqq        ,1187 ,lumi*1000.0,'AK8Puppijet0_deepdoubleb','(AK8Puppijet0_deepdoubleb>=0&&AK8Puppijet0_pt>450)','otree')
    h_zraw_800_2017  = GetChain(h_ddb2017,tf2017zqq_800   ,18.67,lumi*1000.0,'AK8Puppijet0_deepdoubleb','(AK8Puppijet0_deepdoubleb>=0&&AK8Puppijet0_pt>450)','otree')
    hlist = [
         {"hist":h_ddb_2016   ,'colors':kBlack    ,'style':1, 'ytitle':"",  'label':'Z 2016'   ,'denom':False},
         {"hist":h_ddb_2017   ,'colors':kRed    ,'style':1, 'ytitle':""  ,  'label':'Z 2017'   ,'denom':True},
    ]
    drawFromhist(hlist,[],"Z_dbtag_baconbit",options,"hist")


    #p = 'h_DY_dbtag_ak8_aftercut'
    #h_2016 =getControlPlot( 'ddb2016_Jun24/MC/Plots_1000pb_weighted.root', '2016', tag='Jun24' ,plot=p)
    #h_2017 =getControlPlot( 'ddb_Jun24/MC/Plots_1000pb_weighted.root'    , '2017', tag='Jun24' ,plot=p)
    #hlist = [
    #     {"hist":h_2016   ,'colors':kBlack    ,'style':1, 'ytitle':"",  'label':'Z 2016'   ,'denom':False},
    #     {"hist":h_2017   ,'colors':kRed    ,'style':1, 'ytitle':""  ,  'label':'Z 2017'   ,'denom':True},
    #]
    #drawFromhist(hlist,[],"Z_dbtag_aftercut",options,"hist")
    #p = 'h_DY_dbtag_ak8'
    #h_2016 =getControlPlot( 'ddb2016_Jun24/MC/Plots_1000pb_weighted.root', '2016', tag='Jun24' ,plot=p)
    #h_2017 =getControlPlot( 'ddb_Jun24/MC/Plots_1000pb_weighted.root'    , '2017', tag='Jun24' ,plot=p)
    #hlist = [
    #     {"hist":h_2016   ,'colors':kBlack    ,'style':1, 'ytitle':"",  'label':'Z 2016'   ,'denom':False},
    #     {"hist":h_2017   ,'colors':kRed    ,'style':1, 'ytitle':""  ,  'label':'Z 2017'   ,'denom':True},
    #]
    #drawFromhist(hlist,[],"Z_dbtag_beforecut",options,"hist")
    #p = 'h_DY_pt_ak8'
    #h_2016 =getControlPlot( 'ddb2016_Jun24/MC/Plots_1000pb_weighted.root', '2016', tag='Jun24' ,plot=p)
    #h_2017 =getControlPlot( 'ddb_Jun24/MC/Plots_1000pb_weighted.root'    , '2017', tag='Jun24' ,plot=p)
    #h_2018 =getControlPlot( 'ddb2018_Jun24/MC/Plots_1000pb_weighted.root', '2018', tag='Jun24' ,plot=p)
    #hlist = [
    #     {"hist":h_2016   ,'colors':kBlack    ,'style':1, 'ytitle':"",  'label':'Z 2016'   ,'denom':False},
    #     {"hist":h_2017   ,'colors':kRed    ,'style':1, 'ytitle':""  ,  'label':'Z 2017'   ,'denom':True},
    #     {"hist":h_2018   ,'colors':kBlue    ,'style':1, 'ytitle':""  ,  'label':'Z 2018'   ,'denom':False},
    #]
    #drawFromhist(hlist,[],"Z_pt_ak8",options,"hist")



    ### Gen pT with different weights
    #xmin = 450.0
    #hlist = [
    #     {"hist":h_W_2016_PU    ,'colors':kGreen    ,'style':1, 'ytitle':"",  'label':'W 2016 (PU)'   ,'denom':False},
    #     {"hist":h_W_2017_PU    ,'colors':kGreen    ,'style':2, 'ytitle':"",  'label':'W 2017(PU)'   ,'denom':False},
    #     {"hist":h_W_2016_trig    ,'colors':kRed    ,'style':1, 'ytitle':"",  'label':'W 2016(trig)'   ,'denom':False},
    #     {"hist":h_W_2017_trig    ,'colors':kRed    ,'style':2, 'ytitle':"",  'label':'W 2017(trig)'   ,'denom':False},
    #     {"hist":h_w_nlo_ewk    ,'colors':kBlue   ,'style':1, 'ytitle':"",  'label':'W NLO(qcd+ewk)'    ,'denom':True},
    #]
    #ymax = h_w_nlo_ewk.GetBinContent(h_w_nlo_ewk.FindBin(xmin))*1.5
    #drawFromhist(hlist,[],"W_PU_compare",options,"hist",(0,ymax),(xmin,1000))
    #hlist = [
    #     {"hist":h_Z_2016_fix   ,'colors':kBlack    ,'style':1, 'ytitle':"",  'label':'Z (fixed)'   ,'denom':False},
    #     {"hist":h_Z_2016_PU   ,'colors':kGreen    ,'style':1, 'ytitle':"",  'label':'Z 2016(PU)'   ,'denom':False},
    #     {"hist":h_Z_2017_PU   ,'colors':kGreen    ,'style':2, 'ytitle':"",  'label':'Z 2017(PU)'   ,'denom':False},
    #     {"hist":h_Z_2016_trig   ,'colors':kRed    ,'style':1, 'ytitle':"",  'label':'Z 2016(trig)'   ,'denom':False},
    #     {"hist":h_Z_2017_trig   ,'colors':kRed    ,'style':2, 'ytitle':"",  'label':'Z 2017(trig)'   ,'denom':False},
    #     {"hist":h_z_nlo_ewk    ,'colors':kBlue   ,'style':1, 'ytitle':"",  'label':'Z NLO(qcd+ewk)'    ,'denom':True},
    #]
    #ymax = h_w_nlo_ewk.GetBinContent(h_w_nlo_ewk.FindBin(xmin))*1.5
    #drawFromhist(hlist,[],"Z_PU_compare",options,"hist",(0,ymax),(xmin,1000))


    #xmin = 450.0
    #hlist = [
    #     {"hist":h_W_2016_fix   ,'colors':kRed    ,'style':1, 'ytitle':"",  'label':'W (fixed)'   ,'denom':False},
    #     {"hist":h_W_2016_preApp,'colors':kBlack  ,'style':1, 'ytitle':"",  'label':'W 2016(preApp)'   ,'denom':False},
    #     {"hist":h_W_2017_preApp,'colors':kBlack  ,'style':2, 'ytitle':"",  'label':'W 2017(preApp)'   ,'denom':False},
    #     {"hist":h_W_2017_zprime,'colors':kGreen  ,'style':2, 'ytitle':"",  'label':'W 2017(Zprime)'   ,'denom':False},
    #     {"hist":h_w_nlo_ewk    ,'colors':kBlue   ,'style':1, 'ytitle':"",  'label':'W NLO(qcd+ewk)'    ,'denom':True},
    #]
    #ymax = h_w_nlo_ewk.GetBinContent(h_w_nlo_ewk.FindBin(xmin))*1.5
    #drawFromhist(hlist,[],"W_compare",options,"hist",(0,ymax),(xmin,1000))
    #hlist = [
    #     {"hist":h_Z_2016_fix   ,'colors':kRed    ,'style':1, 'ytitle':"",  'label':'Z (fixed)'   ,'denom':False},
    #     {"hist":h_Z_2016_preApp,'colors':kBlack  ,'style':1, 'ytitle':"",  'label':'Z 2016(preApp)'   ,'denom':False},
    #     {"hist":h_Z_2017_preApp,'colors':kBlack  ,'style':2, 'ytitle':"",  'label':'Z 2017(preApp)'   ,'denom':False},
    #     {"hist":h_Z_2017_zprime,'colors':kGreen  ,'style':2, 'ytitle':"",  'label':'Z 2017(Zprime)'   ,'denom':False},
    #     {"hist":h_z_nlo_ewk    ,'colors':kBlue   ,'style':1, 'ytitle':"",  'label':'Z NLO(qcd+ewk)'    ,'denom':True},
    #]
    #ymax = h_w_nlo_ewk.GetBinContent(h_w_nlo_ewk.FindBin(xmin))*1.5
    #drawFromhist(hlist,[],"Z_compare",options,"hist",(0,ymax),(xmin,1000))



    #hlist = [
    #     {"hist":h_W_2017       ,'colors':kGreen,'style':1, 'ytitle':"",  'label':'W 2017'            ,'denom':False},
    #     {"hist":h_W_2016       ,'colors':kRed  ,'style':1, 'ytitle':"",  'label':'W 2016'            ,'denom':False},
    #     {"hist":h_w_nlo_ewk    ,'colors':kBlue ,'style':1, 'ytitle':"",  'label':'W NLO(qcd+ewk)'    ,'denom':True},
    #]
    #xmin = 350.0
    #ymax = h_W_2016.GetBinContent(h_W_2016.FindBin(xmin))*1.5
    #drawFromhist(hlist,[],"Validate_W",options,"hist",(0,ymax),(xmin,1000))

    #hlist = [
    #     {"hist":h_Z_2017       ,'colors':kGreen,'style':1, 'ytitle':"",  'label':'Z 2017'            ,'denom':False},
    #     {"hist":h_Z_2016       ,'colors':kRed  ,'style':1, 'ytitle':"",  'label':'Z 2016'            ,'denom':False},
    #     {"hist":h_z_nlo_ewk    ,'colors':kBlue ,'style':1, 'ytitle':"",  'label':'Z NLO(qcd+ewk)'    ,'denom':True},
    #]
    #ymax = h_Z_2016.GetBinContent(h_Z_2016.FindBin(xmin))*1.5
    #drawFromhist(hlist,[],"Validate_Z",options,"hist",(0,ymax),(xmin,1000))


    #xmin = 450.0
    #hlist = [
    #     {"hist":h_W_2016_fix       ,'colors':kRed    ,'style':1, 'ytitle':"",  'label':'W 2016(qcd+ewk)'   ,'denom':False},
    #     {"hist":h_wraw_2016_ewk,'colors':kBlack  ,'style':2, 'ytitle':"",  'label':'W 2016(ewk)'       ,'denom':False},
    #     {"hist":h_wraw_2016_qcd,'colors':kBlack  ,'style':3, 'ytitle':"",  'label':'W 2016(qcd)'       ,'denom':False},
    #     {"hist":h_wraw_2016    ,'colors':kBlack  ,'style':1, 'ytitle':"",  'label':'W 2016(no kfactor)','denom':False},
    #     {"hist":h_w_nlo_ewk    ,'colors':kBlue   ,'style':1, 'ytitle':"",  'label':'W NLO(qcd+ewk)'    ,'denom':True},
    #]
    #ymax = h_w_nlo_ewk.GetBinContent(h_w_nlo_ewk.FindBin(xmin))*1.5
    #drawFromhist(hlist,[],"W_2016",options,"hist",(0,ymax),(xmin,1000))
    #hlist = [
    #     {"hist":h_Z_2016_fix       ,'colors':kRed    ,'style':1, 'ytitle':"",  'label':'Z 2016(qcd+ewk)'   ,'denom':False},
    #     {"hist":h_zraw_2016_ewk,'colors':kBlack  ,'style':2, 'ytitle':"",  'label':'Z 2016(ewk)'       ,'denom':False},
    #     {"hist":h_zraw_2016_qcd,'colors':kBlack  ,'style':3, 'ytitle':"",  'label':'Z 2016(qcd)'       ,'denom':False},
    #     {"hist":h_zraw_2016    ,'colors':kBlack  ,'style':1, 'ytitle':"",  'label':'Z 2016(no kfactor)','denom':False},
    #     {"hist":h_z_nlo_ewk    ,'colors':kBlue ,'style':1, 'ytitle':"",  'label':'Z NLO(qcd+ewk)'    ,'denom':True},
    #]
    #ymax = h_Z_2016.GetBinContent(h_Z_2016.FindBin(xmin))*1.5
    #drawFromhist(hlist,[],"Z_2016",options,"hist",(0,ymax),(xmin,1000))
    #hlist = [
    #     {"hist":h_W_2017_fix           ,'colors':kGreen  ,'style':1, 'ytitle':"",  'label':'W 2017(qcd+ewk)'   ,'denom':False},
    #     {"hist":h_wraw_400_2017_ewk,'colors':kBlack  ,'style':2, 'ytitle':"",  'label':'W 2017(ewk)'       ,'denom':False},
    #     {"hist":h_wraw_400_2017_qcd,'colors':kBlack  ,'style':3, 'ytitle':"",  'label':'W 2017(qcd)'       ,'denom':False},
    #     {"hist":h_wraw_400_2017    ,'colors':kBlack  ,'style':1, 'ytitle':"",  'label':'W 2017(no kfactor)','denom':False},
    #     {"hist":h_w_nlo_ewk        ,'colors':kBlue   ,'style':1, 'ytitle':"",  'label':'W NLO(qcd+ewk)'    ,'denom':True},
    #]
    #ymax = h_W_2017.GetBinContent(h_W_2017.FindBin(xmin))*1.5
    #drawFromhist(hlist,[],"W_2017",options,"hist",(0,ymax),(xmin,1000))
    #hlist = [
    #     {"hist":h_Z_2017_fix           ,'colors':kGreen  ,'style':1, 'ytitle':"",  'label':'Z 2017(qcd+ewk)'   ,'denom':False},
    #     {"hist":h_zraw_400_2017    ,'colors':kBlack  ,'style':1, 'ytitle':"",  'label':'Z 2017(no kfactor)','denom':False},
    #     {"hist":h_zraw_400_2017_ewk,'colors':kBlack  ,'style':2, 'ytitle':"",  'label':'Z 2017(ewk)'       ,'denom':False},
    #     {"hist":h_zraw_400_2017_qcd,'colors':kBlack  ,'style':3, 'ytitle':"",  'label':'Z 2017(qcd)'       ,'denom':False},
    #     {"hist":h_z_nlo_ewk        ,'colors':kBlue   ,'style':1, 'ytitle':"",  'label':'Z NLO(qcd+ewk)'    ,'denom':True},
    #]
    #ymax = h_Z_2017.GetBinContent(h_Z_2017.FindBin(xmin))*1.5
    #drawFromhist(hlist,[],"Z_2017",options,"hist",(0,ymax),(xmin,1000))
    #LOcomparison()
    #reweight()


