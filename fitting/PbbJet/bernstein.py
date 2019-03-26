import math,array
import ROOT as r
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
def genBernsteinTF(n_rho,n_pT,boundaries,IsMsdPt,qcdeff=True,rescale=True): 

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

        if not qcdeff:
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

def getParsfromMLfit(fml_path,pamNames,qcdeff=0,setTFto1=False):
    print "="*20+" "+fml_path+" "+"="*20
    fml = r.TFile(fml_path)
    rfr = r.RooFitResult(fml.Get("fit_s"))
    print "Using qcd eff = %.4f"%qcdeff
    pars = [qcdeff]
    for p in pamNames:
        if rfr.floatParsFinal().find(p):
            print p, "= %.3f"%rfr.floatParsFinal().find(p).getVal(), "+/-  %.3f"%rfr.floatParsFinal().find(p).getError()
            if setTFto1 and 'qcdeff' not in p:
                print "Setting  %s to 1"%p
                pars.append(1)
            else:
                pars.append(rfr.floatParsFinal().find(p).getVal())
        else:
            #print p, "not found, skipping "
            pass
    return pars

def getParsfromWS(ws_path,pamNames):
    ws_tf = r.TFile(ws_path)
    ws    = ws_tf.Get("w")
    pars = []
    print "="*20+" "+ws_path+" "+"="*20
    for pamName in pamNames:
        p = ws.var(pamName)
        try:
            print "%s =  %.4f +/- %.4f "%(p.GetName(), p.getVal(),  p.getError())
            pars.append(p.getVal())
        except:
            pass
            #print "%s is not present in ws"%pamName
    return pars

def drawOpt(f2,colz,MsdOrRho,ofname):
    c1 = r.TCanvas("c1","c1",800,800)
    #fun_mass_pT_str =  genBernsteinTFstring(nrho,npT,f2)
    #print "TF string = ",fun_mass_pT_str
    if colz:
        f2.Draw("colz")
    else:
        f2.Draw("surf1")

    if MsdOrRho=='msd':
        f2.GetXaxis().SetTitle("m_{SD} [GeV]")
    else:
        f2.GetXaxis().SetTitle("#rho")
    f2.GetYaxis().SetTitle("p_{T} [GeV]")
    f2.GetZaxis().SetTitle("Pass-to-fail Ratio")
    f2.GetXaxis().SetTitleOffset(1.5)
    f2.GetYaxis().SetTitleOffset(2)
    f2.GetZaxis().SetTitleOffset(2)
    f2.SetTitle("")
    if colz:
        c1.SaveAs(ofname.replace(".pdf","_colz.pdf"))
    else:
        c1.SaveAs(ofname)

    
def makeTFs(pars,nrho,npT,odir):
        
    f2params = array.array('d', pars)
    npar = len(f2params)
    colz = False 

    boundaries={}
    boundaries['RHO_LO']=-6.
    boundaries['RHO_HI']=-2.1
    boundaries['PT_LO' ]= 450.
    boundaries['PT_HI' ]= 1000.


    for colz in [True,False]:
        # Pass-to-Fail ratio in mSD-pT plane
        fun_mass_pT =  genBernsteinTF(nrho,npT,boundaries,True,True,True)
        f2 = r.TF2("f2", fun_mass_pT, 40,201,450,1000,npar)
        f2.SetParameters(f2params)
        drawOpt(f2,colz,'msd',odir+"f2.pdf")
        fun_rho_pT =  genBernsteinTF(nrho,npT,boundaries,False,True,True)
        f2 = r.TF2("f2", fun_rho_pT, -6,-2.1,450,1000,npar)
        f2.SetParameters(f2params)
        drawOpt(f2,colz,'rho',odir+"f2_rho.pdf")
        # Transfer-factor in mSD-pT plane
        fun_mass_pT =  genBernsteinTF(nrho,npT,boundaries,True,False,True)
        f2 = r.TF2("f2", fun_mass_pT, 40,201,450,1000,npar)
        f2.SetParameters(f2params)
        #for pT in [500,700,800]:
        #    arr = []
        #    for msd in range(120,130):
        #        arr.append("%.3f"%f2.Eval(msd,pT))
        #    print arr

        drawOpt(f2,colz,'msd',odir+"f2_noqcdeff.pdf")
        # Transfer-factor in rho-pT plane
        fun_rho_pT =  genBernsteinTF(nrho,npT,boundaries,False,False,True)
        f2 = r.TF2("f2", fun_rho_pT,  -6,-2.1,450,1000,npar)
        f2.SetParameters(f2params)
        drawOpt(f2,colz,'rho',odir+"f2_noqcdeff_rho.pdf")
        # Pass-to-Fail ratio in rho-pT unit plane
        fun2 =  genBernsteinTF(nrho,npT,boundaries,False,True,False)
        f2 = r.TF2("f_unit", fun2, 0,1,0,1,npar)
        f2.SetParameters(f2params)
        drawOpt(f2,colz,'rho',odir+"f2_unit.pdf")
        
if __name__ == '__main__':

    parser = OptionParser()
    parser.add_option('-o', '--odir', dest='odir', default='./', help='directory to write histograms/job output', metavar='odir')

    (options, args) = parser.parse_args()
    r.gStyle.SetPadTopMargin(0.1)
    r.gStyle.SetPadBottomMargin(0.2)
    r.gStyle.SetPadLeftMargin(0.15)
    r.gStyle.SetPadRightMargin(0.2)
    r.gStyle.SetPalette(1)
    r.gStyle.SetOptFit(0000)
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

    #rfr = r.RooFitResult(fml.Get("fit_s"))
    ### generic way to find many parameters, not sure how to enforce orders
    #fitpams = rfr.floatParsFinal().selectByName("p*r*")
    #for i in range(0,len(fitpams)):
    #    p =  fitpams[i]
    #    print p.GetName()," = ", p.getVal(), "+/-", p.getError()
   
    setTFto1 = False 
    pars = []

    pars = getParsfromWS("ddb_Mar7/ddb_M2/msd47_TF21_rescaled/card_rhalphabet_all_floatZ.root",lParams)
    makeTFs(pars,2,1,    "ddb_Mar7/ddb_M2/msd47_TF21_rescaled/")

    qcdeff = 0.0121
    #pars = getParsfromMLfit("ddb_Jan17/MC/qcdMC_newTF21/mlfit.root",lParams,qcdeff) 
    #makeTFs(pars,2,1,    "ddb_Jan17/MC/qcdMC_newTF21/ftest/cards_mc_r2p1/")

