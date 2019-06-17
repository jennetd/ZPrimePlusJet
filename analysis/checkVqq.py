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
    return h,chain

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
    #c1.SaveAs(options.odir+pname+".root")

def applyEWK(h_NLO,h_EWK):
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
    h_w_nlo_qcd ,chain_tmp = GetChain(h_w_nlo_qcd,'ggH/Comb_w12j.root',56.3582,lumi*1000,'fVPt','(v_m>40)' )
    h_z_nlo_qcd ,chain_tmp = GetChain(h_z_nlo_qcd,'ggH/z12j_v2.root'  ,22.2833,lumi*1000,'fVPt','(v_m>40)' )
    h_w_nlo_ewk = h_w_nlo_qcd.Clone('h_w_nlo_ewk') 
    h_z_nlo_ewk = h_z_nlo_qcd.Clone('h_z_nlo_ewk')
    hEWK_W             = getEWK('W')
    hEWK_Z             = getEWK('Z')
    applyEWK(h_w_nlo_ewk,hEWK_W)
    applyEWK(h_z_nlo_ewk,hEWK_Z)
   
    #### Phil's LO files 
    h_w_lo_400 ,chain_tmp = GetChain(h_w_lo_400,'ggH/wqq_ht400.root',315.6,lumi*1000,'fVPt','(v_m>40)')
    h_w_lo_600 ,chain_tmp = GetChain(h_w_lo_600,'ggH/wqq_ht600.root',68.57,lumi*1000,'fVPt','(v_m>40)')
    h_w_lo_800 ,chain_tmp = GetChain(h_w_lo_800,'ggH/wqq_ht800.root',34.9,lumi*1000,'fVPt' ,'(v_m>40)')
    
    h_z_lo_400 ,chain_tmp = GetChain(h_z_lo_400,'ggH/zqq_ht400.root',145.4,lumi*1000,'fVPt','(v_m>40)')
    h_z_lo_600 ,chain_tmp = GetChain(h_z_lo_600,'ggH/zqq_ht600.root',34.0 ,lumi*1000,'fVPt','(v_m>40)')
    h_z_lo_800 ,chain_tmp = GetChain(h_z_lo_800,'ggH/zqq_ht800.root',18.67,lumi*1000,'fVPt','(v_m>40)')

    h_w_lo_400.Add(h_w_lo_600)
    h_w_lo_400.Add(h_w_lo_800)
    h_z_lo_400.Add(h_z_lo_600)
    h_z_lo_400.Add(h_z_lo_800)

  
    # from checkVqqMay20  baconbit 13,14,15
    #tf_raw = TFile("checkVqq/May28/Vpt.root")

    #tf2016zqq         ='/eos/uscms/store/user/lpcbacon/dazsle/zprimebits-v15.03/skim/oldDYJets/DYJetsToQQ_HT180_13TeV_*.root'
    #tf2016wqq         ='/eos/uscms/store/user/lpcbacon/dazsle/zprimebits-v15.03/skim/oldWJets/WJetsToQQ_HT180_13TeV_*.root'
    #tf2017wqq_400_600 ='/eos/uscms/store/user/lpcbacon/dazsle/zprimebits-v15.04/skim/WJetsToQQ_HT400to600_qc19_3j_TuneCP5_13TeV_*.root'
    #tf2017wqq_600_800 ='/eos/uscms/store/user/lpcbacon/dazsle/zprimebits-v15.04/skim/WJetsToQQ_HT600to800_qc19_3j_TuneCP5_13TeV_*.root'
    #tf2017wqq_800     ='/eos/uscms/store/user/lpcbacon/dazsle/zprimebits-v15.04/skim/WJetsToQQ_HT-800toInf_qc19_3j_TuneCP5_13TeV_0.root'
    #tf2017zqq_600_800 ='/eos/uscms/store/user/lpcbacon/dazsle/zprimebits-v15.04/skim/ZJetsToQQ_HT600to800_qc19_4j_TuneCP5_13TeV_*.root'
    #tf2017zqq_400_600 ='/eos/uscms/store/user/lpcbacon/dazsle/zprimebits-v15.04/skim/ZJetsToQQ_HT400to600_qc19_4j_TuneCP5_13TeV_*.root'
    #tf2017zqq_800     ='/eos/uscms/store/user/lpcbacon/dazsle/zprimebits-v15.04/skim/ZJetsToQQ_HT-800toInf_qc19_4j_TuneCP5_13TeV_0.root'

    tf2016zqq         ='/eos/uscms/store/user/lpcbacon/dazsle/zprimebits-v15.03/DYJetsToQQ_HT180_13TeV/Output_job1*.root'
    tf2016wqq         ='/eos/uscms/store/user/lpcbacon/dazsle/zprimebits-v15.03/WJetsToQQ_HT180_13TeV/Output_job1*.root'
    tf2017wqq_400_600 ='/eos/uscms/store/user/lpcbacon/dazsle/zprimebits-v15.04/WJetsToQQ_HT400to600_qc19_3j_TuneCP5_13TeV//Output_job1*.root'
    tf2017wqq_600_800 ='/eos/uscms/store/user/lpcbacon/dazsle/zprimebits-v15.04/WJetsToQQ_HT600to800_qc19_3j_TuneCP5_13TeV//Output_job1*.root'
    tf2017wqq_800     ='/eos/uscms/store/user/lpcbacon/dazsle/zprimebits-v15.04/WJetsToQQ_HT-800toInf_qc19_3j_TuneCP5_13TeV//Output_job1*.root'
    tf2017zqq_600_800 ='/eos/uscms/store/user/lpcbacon/dazsle/zprimebits-v15.04/ZJetsToQQ_HT600to800_qc19_4j_TuneCP5_13TeV//Output_job1*.root'
    tf2017zqq_400_600 ='/eos/uscms/store/user/lpcbacon/dazsle/zprimebits-v15.04/ZJetsToQQ_HT400to600_qc19_4j_TuneCP5_13TeV//Output_job1*.root'
    tf2017zqq_800     ='/eos/uscms/store/user/lpcbacon/dazsle/zprimebits-v15.04/ZJetsToQQ_HT-800toInf_qc19_4j_TuneCP5_13TeV/Output_job1*.root'


    Reweight = False
    if Reweight:
        h_wraw_2016 ,chain_tmp = GetChain(h_wraw_2016,tf2016wqq        ,2778 ,lumi*1000,'genVPt','(genVMass>40)','Events')
        h_zraw_2016 ,chain_tmp = GetChain(h_zraw_2016,tf2016zqq        ,1187 ,lumi*1000,'genVPt','(genVMass>40)','Events')

        h_wraw_400_2017 ,chain_tmp = GetChain(h_wraw_400_2017,tf2017wqq_400_600,315.6,lumi*1000,'genVPt','(genVMass>40)','Events')
        h_wraw_600_2017 ,chain_tmp = GetChain(h_wraw_600_2017,tf2017wqq_600_800,68.57,lumi*1000,'genVPt','(genVMass>40)','Events')
        h_wraw_800_2017 ,chain_tmp = GetChain(h_wraw_800_2017,tf2017wqq_800    ,34.9 ,lumi*1000,'genVPt','(genVMass>40)','Events')
                                              
        h_zraw_400_2017 ,chain_tmp = GetChain(h_zraw_400_2017,tf2017zqq_400_600,145.4,lumi*1000,'genVPt','(genVMass>40)','Events')
        h_zraw_600_2017 ,chain_tmp = GetChain(h_zraw_600_2017,tf2017zqq_600_800,34.0 ,lumi*1000,'genVPt','(genVMass>40)','Events')
        h_zraw_800_2017 ,chain_tmp = GetChain(h_zraw_800_2017,tf2017zqq_800    ,18.67,lumi*1000,'genVPt','(genVMass>40)','Events')

        print h_zraw_400_2017.GetName() ,   h_zraw_400_2017.Integral(40,50)
        print h_zraw_600_2017.GetName() ,   h_zraw_600_2017.Integral(40,50) 
        print h_zraw_800_2017.GetName() ,   h_zraw_800_2017.Integral(40,50)

        h_wraw_400_2017.Add(h_wraw_600_2017)
        h_wraw_400_2017.Add(h_wraw_800_2017)
        h_zraw_400_2017.Add(h_zraw_600_2017)
        h_zraw_400_2017.Add(h_zraw_800_2017)

    #tf2017 = TFile("ddb_Jun10/MC/Plots_1000pb_weighted.root")
    #tf2016 = TFile("ddb2016_May21_v2/MC/Plots_1000pb_weighted.root")
    ## 400-1000 reweight
    #tf2017 = TFile("ddb_Jun12/MC/Plots_1000pb_weighted.root")
    #tf2016 = TFile("ddb2016_Jun12/MC/Plots_1000pb_weighted.root")
    tf2017 = TFile("ddb_Jun16/MC/Plots_1000pb_weighted.root")
    tf2016 = TFile("ddb2016_Jun16/MC/Plots_1000pb_weighted.root")
    h_W_2017 = tf2017.Get("h_W_fBosonPt_weight")
    h_Z_2017 = tf2017.Get("h_DY_fBosonPt_weight")
    h_W_2016 = tf2016.Get("h_W_fBosonPt_weight")
    h_Z_2016 = tf2016.Get("h_DY_fBosonPt_weight")
    h_W_2017.Scale(lumi/41.5)
    h_Z_2017.Scale(lumi/41.5)
    h_W_2016.Scale(lumi/35.9)
    h_Z_2016.Scale(lumi/35.9)

    hlist = [
         #{"hist":h_wraw_400_2017,'colors':kGreen,'style':3, 'ytitle':"",  'label':'W 2017(no kfactor)','denom':True},
         #{"hist":h_wraw_2016,'colors':kRed  ,'style':3, 'ytitle':"",  'label':'W 2016(no kfactor)','denom':False},
         {"hist":h_W_2017       ,'colors':kGreen,'style':1, 'ytitle':"",  'label':'W 2017'            ,'denom':False},
         {"hist":h_W_2016       ,'colors':kRed  ,'style':1, 'ytitle':"",  'label':'W 2016'            ,'denom':False},
         #{"hist":h_w_nlo_qcd    ,'colors':kBlue ,'style':2, 'ytitle':"",  'label':'W NLO(qcd)  '      ,'denom':False},
         {"hist":h_w_nlo_ewk    ,'colors':kBlue ,'style':1, 'ytitle':"",  'label':'W NLO(qcd+ewk)'    ,'denom':True},
         #{"hist":h_w_lo_400 ,'colors':kBlue ,'style':3, 'ytitle':"",  'label':'W LO'              ,'denom':False},
    ]
    xmin = 350.0
    ymax = h_W_2016.GetBinContent(h_W_2016.FindBin(xmin))*1.5
    drawFromhist(hlist,[],"Validate_W",options,"hist",(0,ymax),(xmin,1000))

    hlist = [
         #{"hist":h_zraw_400_2017,'colors':kGreen,'style':3, 'ytitle':"",  'label':'Z 2017(no kfactor)','denom':True},
         #{"hist":h_zraw_2016,'colors':kRed  ,'style':3, 'ytitle':"",  'label':'Z 2016(no kfactor)','denom':False},
         {"hist":h_Z_2017       ,'colors':kGreen,'style':1, 'ytitle':"",  'label':'Z 2017'            ,'denom':False},
         {"hist":h_Z_2016       ,'colors':kRed  ,'style':1, 'ytitle':"",  'label':'Z 2016'            ,'denom':False},
         #{"hist":h_z_nlo_qcd    ,'colors':kBlue ,'style':2, 'ytitle':"",  'label':'Z NLO(qcd)'        ,'denom':False},
         {"hist":h_z_nlo_ewk    ,'colors':kBlue ,'style':1, 'ytitle':"",  'label':'Z NLO(qcd+ewk)'    ,'denom':True},
         #{"hist":h_z_lo_400 ,'colors':kBlue ,'style':3, 'ytitle':"",  'label':'Z LO'              ,'denom':False},
    ]
    ymax = h_Z_2016.GetBinContent(h_Z_2016.FindBin(xmin))*1.5
    drawFromhist(hlist,[],"Validate_Z",options,"hist",(0,ymax),(xmin,1000))
    #LOcomparison()
    #reweight()


