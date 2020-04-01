from bernstein import *
from optparse import OptionParser,OptionGroup
from array import array
import ROOT as r
import os

def getListOfPams(card):
    lParams = []
    if 'suffix' in card.keys():
        lParams.append("qcdeff_"+card['suffix'])
    else:
        lParams.append("qcdeff")
    pt_max  = 4
    rho_max = 5
    # for r2p1 polynomial
    for i_pt in range(0,pt_max+1):
        for i_rho in range(0,rho_max+1):
            if 'suffix' in card.keys():
                #print ("p%ir%i_%s"%(i_pt,i_rho,card['suffix']))  
                lParams.append("p%ir%i_%s"%(i_pt,i_rho,card['suffix'])) 
            else: 
                #print ("p%ir%i"%(i_pt,i_rho))  
                lParams.append("p%ir%i"%(i_pt,i_rho)) 
    print ("Will look for these parameters:",lParams)  
    return lParams

def Merge(idir,sub_plotNames, plotname):
    cmd = ' montage -density 750 -tile 3x0 -geometry 1600x1600 -border 5 '
    plotName = idir+sub_plotNames
    plotpdf  = idir+plotname

    cmd += plotName+".png"
    cmd += ' '
    cmd += plotpdf+".pdf"
    print cmd
    os.system(cmd)
    print 'rm '+plotName+".png"
    os.system('rm '+plotName+'.png')



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

    stops = [ 0.0, 1.0]
    red =   [ 1.0, 0.3]
    green = [ 1.0, 0.3]
    blue =  [ 1.0, 1.0]
    
    s = array('d', stops)
    red = array('d', red)
    g = array('d', green)
    b = array('d', blue)
    
    npoints = len(s)
    r.TColor.CreateGradientColorTable(npoints, s, red, g, b, 999)
    
    r.gStyle.SetNumberContours(100)


    cards =[
        {'card':'cards/fdeco_minlo//2016/card_rhalphabet_all_2016_floatZ.root' ,
         'mc'  :'ddb2016_Jun24_v3/ddb_M2_full/TF22_MC_w2Fitv2/card_rhalphabet_all_2016_floatZ.root',
         'n_rho':2   ,'n_pT':1    ,'suffix':'2016',
         'n_rho_mc':2,'n_pT_mc':2
        }, 
        {'card':'cards/fdeco_minlo/2017/card_rhalphabet_all_2017_floatZ.root' , 
          'mc':'ddb_Jun24_v2/ddb_M2_full/TF22_MC_w2Fit/card_rhalphabet_all_2017_floatZ.root',
         'n_rho':1,'n_pT':1,'suffix':'2017',
         'n_rho_mc':2,'n_pT_mc':2
         },
        {'card':'cards/fdeco_minlo//2018/card_rhalphabet_all_2018_floatZ.root',
         'mc'  :'ddb2018_Jun24_v3/ddb_M2_full/TF22_MC_w2Fit/card_rhalphabet_all_2018_floatZ.root',
          'n_rho':1,'n_pT':1,'suffix':'2018',
         'n_rho_mc':2,'n_pT_mc':2
         }
     ]
    for card in cards:
        pars = []
        card_path = card['card']
        mccard_path = card['mc']
        mlfit_path = card_path.replace(card_path.split("/")[-1],"")+"mlfit_%s.root"%card['suffix']

        (nr,npT)  = (card['n_rho'],card['n_pT'])
        (nr_mc,npT_mc)  = (card['n_rho_mc'],card['n_pT_mc'])
        lParams = getListOfPams(card)
        print lParams
        (zmaxMC,zminMC) = (0.02,0.0)
        (zmaxTF,zminTF) = (1.2,0.75)
        #pars    = getParsfromWS(card_path,lParams)
        pars    = getParsfromMLfit(card_path,mlfit_path,lParams)
        pars_mc = getParsfromWS(mccard_path,lParams)
        if 'exp' in card.keys():    exp=card['exp']
        else:                       exp=False
        if 'MC'  in card_path:      (zmax,zmin) = (zmaxMC,zminMC)
        else:                       (zmax,zmin) = (zmaxTF,zminTF)  
        print  (zmax,zmin)
        year = card['suffix'] 
        makeTFs(pars,nr,npT                          , "./PAS_plots/data_"+year+"_",exp=exp,zmax=zmax  ,zmin=zmin  ,Ztitle="Data residual correction R_{p/f} / #varepsilon^{QCD}")
        #makeTFs(pars_mc,nr_mc,npT_mc                 , "./PAS_plots/mc_"  +year+"_",exp=exp,zmax=zmaxMC,zmin=zminMC,Ztitle='Expected pass-fail ratio #varepsilon^{QCD}')
        #makeTFprod(pars,nr,npT, pars_mc, nr_mc,npT_mc, "./PAS_plots/Rpf_" +year+"_",exp=exp,zmax=zmaxMC,zmin=zminMC,Ztitle='Observed pass-fail ratio R_{p/f}')

