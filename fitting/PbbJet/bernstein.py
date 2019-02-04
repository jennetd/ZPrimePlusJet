import math,array
import ROOT as r
from optparse import OptionParser,OptionGroup

def bern(x,v,n):
    normalization = 1. * math.factorial(n) / (math.factorial(v) * math.factorial(n - v))
    Bvn = normalization * (x**v) * (1-x)**(n-v)
    return float(Bvn)
def bern_str(x,v,n):
    normalization = 1. * math.factorial(n) / (math.factorial(v) * math.factorial(n - v))
    Bvn_str = "(%s x^%i (1-x)^%i) "%(normalization,v,n)
    return (Bvn_str)

### Returns Bernstein transfer factor of order n_rho and n_pT
### IsMsdPt = True   : Use for x=msd,y=pT domain 
### IsMsdPt = Faluse : Use for x=rho,y=pT domain
### rescale = True   : Domain =[MASS_LO(RHO_LO),MASS_HI(RHO_HI)][PT_LO,PT_HI]
### rescale = False  : Domain =[0,1][0,1]
### qcdeff           : Factor out QCD eff parameter 
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
    def fun2(x, par):
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
        iPar =0
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
    return fun2

def getParsfromMLfit(fml_path,pamNames,setTFto1=False):
    print "="*20+" "+fml_path+" "+"="*20
    fml = r.TFile(fml_path)
    rfr = r.RooFitResult(fml.Get("fit_s"))
    for p in lParams:
        if rfr.floatParsFinal().find(p):
            print p, "=", rfr.floatParsFinal().find(p).getVal(), "+/-", rfr.floatParsFinal().find(p).getError()
            if setTFto1 and 'qcdeff' not in p:
                print "Setting  %s to 1"%p
                pars.append(1)
            else:
                pars.append(rfr.floatParsFinal().find(p).getVal())
        else:
            pass
            #print p, "not found, skipping "

def getParsfromWS(ws_path,pamNames):
    ws_tf = r.TFile(ws_path)
    ws    = ws_tf.Get("w")
    pars = []
    print "="*20+" "+ws_path+" "+"="*20
    for pamName in pamNames:
        p = ws.var(pamName)
        try:
            print "%s =  %.3f +/- %.3f "%(p.GetName(), p.getVal(),  p.getError())
            pars.append(p.getVal())
        except:
            pass
            #print "%s is not present in ws"%pamName
    return pars


def makeTFs(pars,nrho,npT,odir):
        
    f2params = array.array('d', pars)
    npar = len(f2params)
    colz = False 

    boundaries={}
    boundaries['RHO_LO']=-6.
    boundaries['RHO_HI']=-2.1
    boundaries['PT_LO' ]= 450.
    boundaries['PT_HI' ]= 1000.

    c1 = r.TCanvas("c1","c1",800,800)

    # Pass-to-Fail ratio in mSD-pT plane
    fun_mass_pT =  genBernsteinTF(nrho,npT,boundaries,True,True,True)
    f2 = r.TF2("f2", fun_mass_pT, 40,201,450,1000,npar)
    f2.SetParameters(f2params)
    if colz:
        f2.Draw("colz")
    else:
        f2.Draw("surf1")
        f2.GetXaxis().SetTitle("m_{SD} [GeV]")
        f2.GetYaxis().SetTitle("p_{T} [GeV]")
        f2.GetZaxis().SetTitle("Pass-to-fail Ratio")
        f2.GetXaxis().SetTitleOffset(1.5)
        f2.GetYaxis().SetTitleOffset(2)
        f2.GetZaxis().SetTitleOffset(2)
        f2.SetTitle("")
    

    c1.SaveAs(odir+"f2.pdf")
    # Pass-to-Fail ratio in rho-pT plane
    fun_rho_pT =  genBernsteinTF(nrho,npT,boundaries,False,True,True)
    f2 = r.TF2("f2", fun_rho_pT, -6,-2.1,450,1000,npar)
    f2.SetParameters(f2params)
    if colz:
        f2.Draw("colz")
    else:
        f2.Draw("surf1")

    c1.SaveAs(odir+"f2_rho.pdf")

    # Transfer-factor in mSD-pT plane
    fun_mass_pT =  genBernsteinTF(nrho,npT,boundaries,True,False,True)
    f2 = r.TF2("f2", fun_mass_pT, 40,201,450,1000,npar)
    f2.SetParameters(f2params)
    print "Eval(f2)",f2.Eval(125,700)
    if colz:
        f2.Draw("colz")
    else:
        f2.Draw("surf1")

    c1.SaveAs(odir+"f2_noqcdeff.pdf")

    # Transfer-factor in rho-pT plane
    fun_rho_pT =  genBernsteinTF(nrho,npT,boundaries,False,False,True)
    f2 = r.TF2("f2", fun_rho_pT,  -6,-2.1,450,1000,npar)
    f2.SetParameters(f2params)
    if colz:
        f2.Draw("colz")
    else:
        f2.Draw("surf1")

    c1.SaveAs(odir+"f2_noqcdeff_rho.pdf")

    # Pass-to-Fail ratio in rho-pT unit plane
    fun2 =  genBernsteinTF(nrho,npT,boundaries,False,True,False)
    f2 = r.TF2("f_unit", fun2, 0,1,0,1,npar)
    f2.SetParameters(f2params)
    if colz:
        f2.Draw("colz")
    else:
        f2.Draw("surf1")
    c1.SaveAs(odir+"f_unit.pdf")   
        
if __name__ == '__main__':

    parser = OptionParser()
    parser.add_option('-o', '--odir', dest='odir', default='./', help='directory to write histograms/job output', metavar='odir')

    (options, args) = parser.parse_args()
    r.gStyle.SetPadTopMargin(0.1)
    r.gStyle.SetPadBottomMargin(0.2)
    r.gStyle.SetPadLeftMargin(0.15)
    r.gStyle.SetPadRightMargin(0.1)
    r.gStyle.SetPalette(1)
    r.gStyle.SetOptFit(0000)
    r.gROOT.SetBatch()
    lParams = []
    lParams.append("qcdeff")
    pt_max  = 2
    rho_max = 5
    # for r2p1 polynomial
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
      
    #pars = getParsfromWS("ddb_Jan31/MC/mcOnly/card_rhalphabet_all_floatZ.root",lParams) 
    #makeTFs(pars,2,1,"ddb_Jan31/MC/mcOnly/")

    pars = getParsfromWS("ddb_Jan17/MC/qcdMC_newTF21/ftest/cards_mc_r2p1/card_rhalphabet_all_r2p1_floatZ.root",lParams) 
    makeTFs(pars,2,1,"ddb_Jan17/MC/qcdMC_newTF21/ftest/cards_mc_r2p1/")
    #pars = getParsfromWS("ddb_Jan17/MC/qcdMC_newTF21/ftest/cards_mc_r2p2/card_rhalphabet_all_r2p2_floatZ.root",lParams) 
    #makeTFs(pars,2,2,"ddb_Jan17/MC/qcdMC_newTF21/ftest/cards_mc_r2p2/")
    #pars = getParsfromWS("ddb_Jan17/MC/qcdMC_newTF21/ftest/cards_mc_r3p1/card_rhalphabet_all_r3p1_floatZ.root",lParams) 
    #makeTFs(pars,3,1,"ddb_Jan17/MC/qcdMC_newTF21/ftest/cards_mc_r3p1/")
    #pars = getParsfromWS("ddb_Jan17/MC/qcdMC_newTF21/ftest/cards_mc_r4p1/card_rhalphabet_all_r4p1_floatZ.root",lParams) 
    #makeTFs(pars,4,1,"ddb_Jan17/MC/qcdMC_newTF21/ftest/cards_mc_r4p1/")
    #pars = getParsfromWS("ddb_Jan17/MC/qcdMC_newTF21/ftest/cards_mc_r3p2/card_rhalphabet_all_r3p2_floatZ.root",lParams) 
    #makeTFs(pars,3,2,"ddb_Jan17/MC/qcdMC_newTF21/ftest/cards_mc_r3p2/")
    #pars = getParsfromWS("ddb_Jan17/MC/qcdMC_newTF21/ftest/cards_mc_r5p1/card_rhalphabet_all_r5p1_floatZ.root",lParams) 
    #makeTFs(pars,5,1,"ddb_Jan17/MC/qcdMC_newTF21/ftest/cards_mc_r5p1/")

    #pars = getParsfromMLfit('ddb_Jan17/MC/qcdMC_r1/mlfit.root',lParams)
    #pars = getParsfromWS("ddb_Jan17/MC/qcdMC_r1/ftest/cards_mc_r2p1/card_rhalphabet_all_r2p1_floatZ.root",lParams) 
    #makeTFs(pars,2,1,"ddb_Jan17/MC/qcdMC_r1/ftest/cards_mc_r2p1/")
    #pars = getParsfromWS("ddb_Jan17/MC/qcdMC_r1/ftest/cards_mc_r2p2/card_rhalphabet_all_r2p2_floatZ.root",lParams) 
    #makeTFs(pars,2,2,"ddb_Jan17/MC/qcdMC_r1/ftest/cards_mc_r2p2/")
    #pars = getParsfromWS("ddb_Jan17/MC/qcdMC_r1/ftest/cards_mc_r3p1/card_rhalphabet_all_r3p1_floatZ.root",lParams) 
    #makeTFs(pars,3,1,"ddb_Jan17/MC/qcdMC_r1/ftest/cards_mc_r3p1/")


