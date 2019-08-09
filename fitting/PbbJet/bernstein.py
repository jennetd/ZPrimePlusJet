import math,array
import ROOT as r
import os
from optparse import OptionParser,OptionGroup

def bern(x,v,n):
    normalization = 1. * math.factorial(n) / (math.factorial(v) * math.factorial(n - v))
    Bvn = normalization * (x**v) * (1-x)**(n-v)
    return float(Bvn)
def bern_str(x,v,n):
    normalization = 1. * math.factorial(n) / (math.factorial(v) * math.factorial(n - v))
    if normalization ==1:
        Bvn_str = "(%s^%i(1-%s)^%i)"%(x,v,x,n-v)
    else:
        Bvn_str = "(%i %s^%i(1-%s)^%i)"%(normalization,x,v,x,n-v)
    return (Bvn_str)

### Returns Bernstein transfer factor of order n_rho and n_pT
### IsMsdPt = True   : Use for x=msd,y=pT domain 
### IsMsdPt = Faluse : Use for x=rho,y=pT domain
### rescale = True   : Domain =[MASS_LO(RHO_LO),MASS_HI(RHO_HI)][PT_LO,PT_HI]
### rescale = False  : Domain =[0,1][0,1]
### qcdeff           : Factor out QCD eff parameter if false 
### TO DO: add print string function to check results
def genBernsteinTF(n_rho,n_pT,boundaries,IsMsdPt,qcdeff=True,rescale=True,exp=False): 

    RHO_LO= boundaries['RHO_LO']
    RHO_HI= boundaries['RHO_HI']
    PT_LO = boundaries['PT_LO' ]
    PT_HI = boundaries['PT_HI' ]
   
    #assumes Par[0] = qcdeff
    #par[1:]  = [p0r1,p0r2...,
    #            p1r0,p1r1,..,
    #            ...]
    #function used to construct TF2
    def funbern(x, par):
        if IsMsdPt:
            rho   = r.TMath.Log((x[0] * x[0]) / (x[1] * x[1])) #convert mass to rho 
        else:
            rho   = x[0] 
        pT    = x[1]
        if rescale:
            rho_norm   = (rho - RHO_LO) /(RHO_HI - RHO_LO)
            pT_norm    = (pT  - PT_LO ) /(PT_HI  - PT_LO)
        else:
            rho_norm   = (rho)
            pT_norm    = (pT )

        # n_rho=2, n_pT=1      
        #poly0 = par[0] * bern(pT_norm,0,n_pT) * (          bern(rho_norm,0,n_rho)  + par[1] *  bern(rho_norm,1,n_rho) + par[2] *  bern(rho_norm,2,n_rho) )
        #poly1 = par[0] * bern(pT_norm,1,n_pT) * ( par[3] * bern(rho_norm,0,n_rho)  + par[4] *  bern(rho_norm,1,n_rho) + par[5] *  bern(rho_norm,2,n_rho) )
        poly = 0
        OLDTF = False # internal switch for old TF
        if OLDTF:
            iPar =0     # par[0] = normalization
            for i_pT in range(0,n_pT+1):
                for i_rho in range(0,n_rho+1):
                    if iPar==0: 
                        poly += par[0] *              bern(pT_norm,i_pT,n_pT) *  bern(rho_norm,i_rho,n_rho)
                    else:
                        poly += par[0] * par[iPar] *  bern(pT_norm,i_pT,n_pT) *  bern(rho_norm,i_rho,n_rho)
                    iPar+=1
        else:
            #NewTF:
            iPar =1     # par[0] = normalization
            for i_pT in range(0,n_pT+1):
                for i_rho in range(0,n_rho+1):
                    poly += par[0] * par[iPar] *  bern(pT_norm,i_pT,n_pT) *  bern(rho_norm,i_rho,n_rho)
                    iPar+=1

        if exp:
            if not qcdeff:
                poly = math.exp(poly)/par[0]  # remove overall qcd eff if not needed
            else:
                poly = par[0]*math.exp(poly/par[0])  # remove overall qcd eff if not needed
        elif not qcdeff:
            poly = poly/par[0]  # remove overall qcd eff if not needed
        return poly
    return funbern

def genBernsteinTFstring(n_rho,n_pT,f2,qcdeff=True,forWolfram=False): 
        if forWolfram:
            rho_norm = 'x'
            pT_norm = 'y'
        else:
            rho_norm = 'rho'
            pT_norm = 'pT'

        nPar = f2.GetNpar()
        f2params = array.array('d',[1]*nPar)
        f2.GetParameters(f2params)
        par  = list(f2params)
        iPar =1# par[0] = normalization
        poly_pT = []
        for i_pT in range(0,n_pT+1):
            poly_rho = []
            for i_rho in range(0,n_rho+1):
                poly_rho.append( "*".join([ "%.3f"%float(par[iPar]) , bern_str(pT_norm,i_pT,n_pT) , bern_str(rho_norm,i_rho,n_rho)]))
                iPar+=1
            poly_pT.append( "[ "+ " + ".join(poly_rho) +" ]")
        if not qcdeff:
            poly = " + ".join(poly_pT)
        else:
            poly = "%.3f *{"%(float(par[0])) + " + ".join(poly_pT) + "}"

        return poly

#Return 1D TF evaluated at pT 
def genBernsteinTF1D(n_rho,n_pT,pT,boundaries,IsMsdPt,qcdeff=True,rescale=True): 
    RHO_LO= boundaries['RHO_LO']
    RHO_HI= boundaries['RHO_HI']
    PT_LO = boundaries['PT_LO' ]
    PT_HI = boundaries['PT_HI' ]
   
    def fun1(x, par):
        if IsMsdPt:
            rho   = r.TMath.Log((x[0] * x[0]) / (pT * pT)) #convert mass to rho 
        else:
            rho   = x[0] 
        if rescale:
            rho_norm   = (rho - RHO_LO) /(RHO_HI - RHO_LO)
            pT_norm    = (pT  - PT_LO ) /(PT_HI  - PT_LO)
        else:
            rho_norm   = (rho)
            pT_norm    = (pT )

        # n_rho=2, n_pT=1      
        #poly0 = par[0] * bern(pT_norm,0,n_pT) * (          bern(rho_norm,0,n_rho)  + par[1] *  bern(rho_norm,1,n_rho) + par[2] *  bern(rho_norm,2,n_rho) )
        #poly1 = par[0] * bern(pT_norm,1,n_pT) * ( par[3] * bern(rho_norm,0,n_rho)  + par[4] *  bern(rho_norm,1,n_rho) + par[5] *  bern(rho_norm,2,n_rho) )
        poly = 0
        iPar =1
        for i_pT in range(0,n_pT+1):
            for i_rho in range(0,n_rho+1):
                #if iPar==0: 
                #    poly += par[0] *              bern(pT_norm,i_pT,n_pT) *  bern(rho_norm,i_rho,n_rho)
                #else:
                poly += par[0] * par[iPar] *  bern(pT_norm,i_pT,n_pT) *  bern(rho_norm,i_rho,n_rho)
                iPar+=1
        if not qcdeff:
            poly = poly/par[0]  # remove overall qcd eff if not needed
        return poly
    return fun1

def getParsfromMLfit(ws_path,fml_path,pamNames,qcdeff=0,setTFto1=False,fit_type = "fit_s"):
    print "="*20+" "+fml_path+" "+"="*20
    fml = r.TFile(fml_path)
    rfr = r.RooFitResult(fml.Get(fit_type))

    try:
        ws_tf = r.TFile(ws_path)
        ws    = ws_tf.Get("w")
        qcdeff = ws.var('qcdeff').getVal()
    except:
        ## for per-bin-eff where no qcdeff is in the ws
        qcdeff = -999
        print "cannot qcdeff in  workspace %s"%ws_path
        
    print "Using qcd eff = %.4f"%qcdeff
    
    # {pName:Value,'arr':[]}, initialize with input value
    pars    = {'qcdeff':qcdeff}
    parsArr = [qcdeff]
    ## generic way to find many parameters, not sure how to enforce orders
    fitpams = rfr.floatParsFinal().selectByName("p*r*")
    ## sort the fitparameters in accending x and y, where pam = pxry
    fitpamNames = sorted([ fitpams[i].GetName() for i in range(0,len(fitpams))])
    for p in fitpamNames:
        print p, "= %.3f"%rfr.floatParsFinal().find(p).getVal(), "+/-  %.3f"%rfr.floatParsFinal().find(p).getError()
        pars[p] = rfr.floatParsFinal().find(p).getVal()
        parsArr.append( rfr.floatParsFinal().find(p).getVal())
    pars['arr'] = parsArr
    print pars
    return pars

def getParsfromWS(ws_path,pamNames):
    ws_tf = r.TFile(ws_path)
    ws    = ws_tf.Get("w")
    pars   = {}
    parsArr = [] 
    print "="*20+" "+ws_path+" "+"="*20
    for pamName in pamNames:
        p = ws.var(pamName)
        try:
            print "%s =  %.4f +/- %.4f "%(p.GetName(), p.getVal(),  p.getError())
            parsArr.append(p.getVal())
            if 'qcdeff' in pamName:
                pars['qcdeff'] = p.getVal()
            else:
                pars[pamName] = p.getVal()
        except:
            if 'qcdeff' in pamName:
                pars['qcdeff'] =-999. 
                parsArr.append(-999.)
            else:
                pars[pamName] = -999. 
            #print "%s is not present in ws"%pamName
            pass
    pars['arr'] = parsArr
    return pars

def getPaveText(MsdOrRho):
    if MsdOrRho=='msd':
        pave_param = r.TPaveText(0.18,0.65,0.27,0.85,"NDC")
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
        
        pave_param2 = r.TPaveText(0.64,0.21,0.74,0.31,"NDC")
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
    else:
        pave_param = r.TPaveText(0.23,0.36,0.33,0.46,"NDC")
        pave_param.SetTextFont(42)
        pave_param.SetFillColor(0)
        pave_param.SetBorderSize(0)
        pave_param.SetFillStyle(0)
        pave_param.SetTextAlign(11)
        pave_param.SetTextSize(0.045)
        text = pave_param.AddText("m_{SD} = 47 GeV")
        text.SetTextAngle(-68)
        text.SetTextAlign(22)
        text.SetTextSize(0.045)
        
        pave_param2 = r.TPaveText(0.57,0.55,0.67,0.65,"NDC")
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
    return pave_param,pave_param2


def drawOpt(f2,colz,MsdOrRho,ofname):
    c1 = r.TCanvas("c1","c1",800,800)
    c1.SetBottomMargin(0.15)
    #fun_mass_pT_str =  genBernsteinTFstring(nrho,npT,f2)
    #print "TF string = ",fun_mass_pT_str
   
    (rho_low,rho_up) = (-6,-2.1)
    (msd_low,msd_up) = (47,201)
    if colz:
        text1,text2 = getPaveText(MsdOrRho)
        if MsdOrRho=='msd':
            rhoxy =  r.TF2("rhoxy","log(x*x/y/y)",30,221,400,1300)
            contours = array.array('d',[rho_low ,rho_up])
            rhoxy.SetContour(2,contours)
            rhoxy.Draw("CONT Z LIST")
            r.gPad.Update()
            f2.Draw("colz")
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
            rhocurv1.Draw("same")
            rhocurv2.Draw("same")
        else:
            mxy = r.TF2("mxy", "sqrt(exp(x))*y",-6.5, -1.5, 400, 1300)
            contours = array.array('d',[msd_low ,msd_up])
            mxy.SetContour(2,contours)
            mxy.Draw("CONT Z LIST")
            r.gPad.Update()
            conts = r.gROOT.GetListOfSpecials().FindObject("contours")
            f2.Draw("colz")
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
            mcurv1.Draw("same")
            mcurv2.Draw("same")
        text1.Draw("same")
        text2.Draw("same")
        f2.GetXaxis().SetTitleOffset(1.5)
        f2.GetYaxis().SetTitleOffset(2)
    else:
        c1.SetRightMargin(0.1)
        c1.SetLeftMargin(0.15)
        f2.GetXaxis().SetTitleOffset(2)
        f2.GetYaxis().SetTitleOffset(2.2)
        f2.Draw("surf1")

    if MsdOrRho=='msd':
        f2.GetXaxis().SetTitle("m_{SD} [GeV]")
    else:
        f2.GetXaxis().SetTitle("#rho = log(m_{SD}^{2}/p_{T}^{2})")

    f2.GetYaxis().SetTitle("p_{T} [GeV]")
    f2.GetZaxis().SetTitle("Pass-to-fail Ratio")
    f2.GetZaxis().SetTitleOffset(2)
    f2.SetMaximum(1.0)
    f2.SetMinimum(0.0)
    f2.SetTitle("")

    #drawCMS()
    lumi = 41.5
    tag1 = r.TLatex(0.67,0.92,"%.1f fb^{-1} (13 TeV)"%lumi)
    tag1.SetNDC(); tag1.SetTextFont(42)
    tag1.SetTextSize(0.045)
    tag2 = r.TLatex(0.15,0.92,"CMS")
    tag2.SetNDC()
    tag2.SetTextFont(62)
    tag3 = r.TLatex(0.28,0.92,"Preliminary")
    tag3.SetNDC()
    tag3.SetTextFont(52)
    tag2.SetTextSize(0.055)
    tag3.SetTextSize(0.045)
    tag1.Draw()
    tag2.Draw()
    tag3.Draw()

    if colz:
        c1.SaveAs(ofname.replace(".pdf","_colz.pdf"))
    else:
        c1.SaveAs(ofname)

def drawBasisMaps(nrho,npT,odir,exp=False):
    boundaries={}
    boundaries['RHO_LO']=-6.
    boundaries['RHO_HI']=-2.1
    boundaries['PT_LO' ]= 450.
    boundaries['PT_HI' ]= 1200.

    arr=[1.0] ##qcdeff
    #initialize parameters  npar = (nrho+1)*(npT+1)
    for i_pT in range(0,(npT+1)*(nrho+1)):            arr.append(0)
    npar = len(arr)
    ipos=1
    colz=True
    for i_pT in range(0,npT+1):
        for i_rho in range(0,nrho+1):
            arr[ipos] =1.0          # turn on this basis
            print "Generating basis map for : p%sr%s"%(i_pT,i_rho)
            print arr
            f2params = array.array('d', arr)
            fun_mass_pT =  genBernsteinTF(nrho,npT,boundaries,IsMsdPt=True,qcdeff=False,rescale=True,exp=exp)
            f2 = r.TF2("f2", fun_mass_pT, 40,201,450,1200,npar)
            f2.SetParameters(f2params)
            #drawOpt(f2,colz,'msd',odir+"bern_msd_p%sr%s.pdf"%(i_pT,i_rho))
            drawOpt(f2,colz,'msd',odir+"bern_msd_p%sr%s.png"%(i_pT,i_rho))

            fun_rho_pT =  genBernsteinTF(nrho,npT,boundaries,IsMsdPt=False,qcdeff=False,rescale=True,exp=exp)
            f2 = r.TF2("f2", fun_rho_pT, -6,-2.1,450,1200,npar)
            f2.SetParameters(f2params)
            #drawOpt(f2,colz,'rho',odir+"bern_rho_p%sr%s.pdf"%(i_pT,i_rho))
            drawOpt(f2,colz,'rho',odir+"bern_rho_p%sr%s.png"%(i_pT,i_rho))

            arr[ipos] =0.0          # reset arr
            ipos +=1 
   
# Exp = exponential function
def makeTFs(pars,nrho,npT,odir,exp=False):
    if not pars['qcdeff'] ==-999:
        f2params = array.array('d', pars['arr'])
    else:
        print " Cannot find qcdeff, assume it's 1"
        f2params = array.array('d', [1.0]+pars['arr'][1:])
    npar = len(f2params)
    #print f2params, npar
    colz = False 

    boundaries={}
    boundaries['RHO_LO']=-6.
    boundaries['RHO_HI']=-2.1
    boundaries['PT_LO' ]= 450.
    boundaries['PT_HI' ]= 1200.

    for colz in [True,False]:
        # Pass-to-Fail ratio in mSD-pT plane
        fun_mass_pT =  genBernsteinTF(nrho,npT,boundaries,IsMsdPt=True,qcdeff=True,rescale=True,exp=exp)
        f2 = r.TF2("f2", fun_mass_pT, 40,201,450,1200,npar)
        f2.SetParameters(f2params)
        drawOpt(f2,colz,'msd',odir+"f2.pdf")
        fun_rho_pT =  genBernsteinTF(nrho,npT,boundaries,IsMsdPt=False,qcdeff=True,rescale=True,exp=exp)
        f2 = r.TF2("f2", fun_rho_pT, -6,-2.1,450,1200,npar)
        f2.SetParameters(f2params)
        drawOpt(f2,colz,'rho',odir+"f2_rho.pdf")
        # Transfer-factor in mSD-pT plane
        fun_mass_pT =  genBernsteinTF(nrho,npT,boundaries,IsMsdPt=True,qcdeff=False,rescale=True,exp=exp)
        f2 = r.TF2("f2", fun_mass_pT, 40,201,450,1200,npar)
        f2.SetParameters(f2params)
        #for pT in [500,700,800]:
        #    arr = []
        #    for msd in range(120,130):
        #        arr.append("%.3f"%f2.Eval(msd,pT))
        #    print arr

        drawOpt(f2,colz,'msd',odir+"f2_noqcdeff.pdf")
        # Transfer-factor in rho-pT plane
        fun_rho_pT =  genBernsteinTF(nrho,npT,boundaries,IsMsdPt=False,qcdeff=False,rescale=True,exp=exp)
        f2 = r.TF2("f2", fun_rho_pT,  -6,-2.1,450,1200,npar)
        f2.SetParameters(f2params)
        drawOpt(f2,colz,'rho',odir+"f2_noqcdeff_rho.pdf")
        # Pass-to-Fail ratio in rho-pT unit plane
        fun2 =  genBernsteinTF(nrho,npT,boundaries,IsMsdPt=False,qcdeff=True,rescale=False,exp=exp)
        f2 = r.TF2("f_unit", fun2, 0,1,0,1,npar)
        f2.SetParameters(f2params)
        drawOpt(f2,colz,'rho',odir+"f2_unit.pdf")
        
if __name__ == '__main__':

    parser = OptionParser()
    parser.add_option('-o', '--odir', dest='odir', default='./', help='directory to write histograms/job output', metavar='odir')

    (options, args) = parser.parse_args()
    r.gStyle.SetPadTopMargin(0.1)
    r.gStyle.SetPadBottomMargin(0.02)
    r.gStyle.SetPadLeftMargin(0.15)
    r.gStyle.SetPadRightMargin(0.2)
    r.gStyle.SetPalette(1)
    r.gStyle.SetOptFit(0000)
    r.gStyle.SetPaintTextFormat("1.1f")
    r.gROOT.SetBatch()
    lParams = []
    lParams.append("qcdeff")
    pt_max  = 2
    rho_max = 5
    # for r2p1 polynomial
    print ("Will look for these parameters:")  
    for i_pt in range(0,pt_max+1):
        for i_rho in range(0,rho_max+1):
            print ("p%ir%i"%(i_pt,i_rho))  
            lParams.append("p%ir%i"%(i_pt,i_rho))  

   
    setTFto1 = False 
    pars = []

    cards =[
        #{'card':'ddb_Apr17/ddb_M2_full/msd47_TF21_muonCR_blind/card_rhalphabet_all_floatZ.root','n_rho':2,'n_pT':1},
        {'card':'ddb_Apr17/ddb_M2_full/msd47_TF21_pbeff_blind/card_rhalphabet_all_floatZ.root','n_rho':2,'n_pT':1}
    ]
    for card in cards:
        card_path = card['card']
        (nr,npT)  = (card['n_rho'],card['n_pT'])
        pars = getParsfromWS(card_path,lParams)
        makeTFs(pars,nr,npT,  card_path.replace(card_path.split("/")[-1],""))

        mlfit_path = card_path.replace(card_path.split("/")[-1],"")+"mlfit.root"
        if os.path.exists(mlfit_path):
            pars = getParsfromMLfit(card_path,mlfit_path,lParams)
            makeTFs(pars,nr,npT,  card_path.replace(card_path.split("/")[-1],"mlfit/"))

