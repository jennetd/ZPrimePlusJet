import ROOT as rt
rt.gROOT.SetBatch()
from RootIterator import RootIterator
from optparse import OptionParser
import os
import sys
import numpy as np
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import bernstein, array
from buildRhalphabetHbb import MASS_BINS,MASS_LO,MASS_HI,BLIND_LO,BLIND_HI,RHO_LO,RHO_HI,SF2018,SF2017,SF2016,MASS_HIST_HI,MASS_HIST_LO


def parseFile(f,ipt):
    arr_x  = np.array([])
    arr_ex = np.array([])
    arr_y  = np.array([])
    arr_ey = np.array([])
    data = [] 
    with  open(f,'r') as qcdcov_txt:
        for l in qcdcov_txt:
            name = l.split()[0]
            ratio = float(l.split()[2])
            ratioErr = float(l.split()[3])
            mass = 40+7*float(name.split("_")[3].replace("Bin",""))-3.5
            if   ipt ==1: pt = 465.0
            elif ipt ==2: pt = 515.0
            elif ipt ==3: pt = 565.0
            elif ipt ==4: pt = 622.5 
            elif ipt ==5: pt = 712.5
            elif ipt ==6: pt = 920.0
            arr_x  = np.append(arr_x, mass)
            arr_ex = np.append(arr_ex, 0)
            arr_y  = np.append(arr_y,ratio )
            arr_ey = np.append(arr_ey, ratioErr)
            data.append((mass,0,ratio,ratioErr))
    #data = np.sort(zip(arr_x,arr_y,arr_ex,arr_ey))
    data.sort()
    p_arr_x=  np.array([i[0] for i in data] )
    p_arr_ex= np.array([i[1] for i in data] )
    p_arr_y=  np.array([i[2] for i in data] )
    p_arr_ey= np.array([i[3] for i in data])
    return p_arr_x,p_arr_y,p_arr_ex,p_arr_ey

def plotRatio(options,args):
    for ipt in range(1,7): 
        c1 = rt.TCanvas('c1','c1',800,600)
        leg = rt.TLegend(0.7,0.7,0.9,0.9)
        arr_x,arr_y,arr_ex,arr_ey = parseFile(options.idir+"../TF22_MC_muonCR_SFJul8/"+'qcdTF_MCstat_cat%s.txt'%ipt,ipt)
        g = rt.TGraphErrors(len(arr_x), arr_x, arr_y, arr_ex, arr_ey)
        arr_x2,arr_y2,arr_ex2,arr_ey2 = parseFile(options.idir+"../TF22_MC_muonCR_SFJul8/"+'qcdTF_MC_cov_cat%s.txt'%ipt,ipt)
        g2 = rt.TGraphErrors(len(arr_x2), arr_x2, arr_y2, arr_ex2, arr_ey2)
        arr_x,arr_y,arr_ex,arr_ey = parseFile(options.idir+'qcdTF_MC_cov_cat%s.txt'%ipt,ipt)
        g3 = rt.TGraphErrors(len(arr_x), arr_x, arr_y, arr_ex, arr_ey)
        leg.AddEntry(g,'mcstat Unc','lf')
        leg.AddEntry(g2,'cov Unc','lf')
        leg.AddEntry(g3,'cov weighted Unc','lf')
        g.SetFillStyle(3004)
        g2.SetFillStyle(3004)
        g3.SetFillStyle(3004)
        g.SetFillColor(rt.kBlue)
        g2.SetFillColor(rt.kRed)
        g3.SetFillColor(rt.kGreen)
        g.SetMarkerColor(rt.kBlue)
        g2.SetMarkerColor(rt.kRed)
        g3.SetMarkerColor(rt.kGreen)
        g.Draw('Al3*')
        g3.Draw("same lp3*")
        g2.Draw("same lp3*")
        g.SetTitle("")
        g.GetYaxis().SetTitle("Pass/Fail")
        g.GetYaxis().SetTitleOffset(0.3)
        g.GetXaxis().SetTitle("mSD[GeV]")
        leg.Draw('same')
        c1.SaveAs(options.idir+"qcdTFerr_cat%s.pdf"%ipt)
        c1.SaveAs(options.idir+"qcdTFerr_cat%s.png"%ipt)
    Merge(options.idir,'qcdTFerr_cat*','qcdTFerr_all')


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

        
def QCDratio(options,args):

    fhist = rt.TFile(options.idir+"../data/hist_1DZbb_pt_scalesmear.root")

    qcdMCpass_2d  = fhist.Get("qcd_pass")
    qcdMCfail_2d  = fhist.Get("qcd_fail")
    for ipt in range(1,7): 
        qcdcov_txt = open(options.idir+'qcdTF_MCstat_cat%s.txt'%ipt,'w')

        qcdMCpass      = qcdMCpass_2d.ProjectionX( "px_" + qcdMCpass_2d.GetName() + str(ipt), ipt, ipt );
        qcdMCfail      = qcdMCfail_2d.ProjectionX( "px_" + qcdMCfail_2d.GetName() + str(ipt), ipt, ipt );
        qcdMCpass.Divide(qcdMCfail)
        qcdTFpars_2017={'n_rho':2, 'n_pT':2,
                    'pars':[  0.0151 ,-1.0404,2.3977 ,0.7081 ,1.1165 ,1.6787 ,-0.1655,0.1460 ,1.5137 ,-0.0976]}
        qcdTFpars_2016={'n_rho':2, 'n_pT':2,
                    'pars':[  0.0145 ,-1.0210,2.3459 ,0.6978 ,0.9232 ,2.3925 ,-0.7023,0.5732 ,1.2283 ,0.1019 ]}
        qcdTFpars_2018={'n_rho':2, 'n_pT':2,
                    'pars':[ 0.0139 ,-0.9751 ,2.3730 ,0.6757 ,1.0980 ,1.4290 ,0.1947 ,0.1500 ,1.9308 ,-0.9522]}
        if options.year =='2017':   qcdTFpars = qcdTFpars_2017
        elif options.year =='2018':   qcdTFpars = qcdTFpars_2018
        elif options.year =='2016':   qcdTFpars = qcdTFpars_2016

        f2params    = array.array('d', qcdTFpars['pars'])
        npar        = len(f2params)
        boundaries={}
        boundaries['RHO_LO']=-6.
        boundaries['RHO_HI']=-2.1
        boundaries['PT_LO' ]= 450.
        boundaries['PT_HI' ]= 1200.
        if   ipt ==1: pt = 465.0
        elif ipt ==2: pt = 515.0
        elif ipt ==3: pt = 565.0
        elif ipt ==4: pt = 622.5 
        elif ipt ==5: pt = 712.5
        elif ipt ==6: pt = 920.0

        f_bernstein = bernstein.genBernsteinTF1D(qcdTFpars['n_rho'],qcdTFpars['n_pT'],pt,boundaries,IsMsdPt=True,qcdeff=True,rescale=True)
        tf2   = rt.TF1("f2", f_bernstein, 40,201,npar)
        tf2.SetParameters(f2params)

        for ibin in range(1,qcdMCpass.GetNbinsX()+1):
            mass       = qcdMCpass.GetBinCenter(ibin)
            rho        = rt.TMath.Log(mass * mass / pt / pt)
            if (rho>-6.0 and rho <-2.1) and (mass>MASS_HIST_LO and mass<MASS_HIST_HI):
                qcdeff_err =  qcdMCpass.GetBinError(ibin)
                qcdeff     = tf2.Eval( qcdMCpass.GetBinCenter(ibin))
                print 'qcdeff_cat%i_%s_Bin%i_%s param %.6f %.6f'%(ipt,options.year,ibin,options.year,qcdeff,qcdeff_err)  
                qcdcov_txt.write('qcdeff_cat%i_%s_Bin%i_%s param %.6f %.6f\n'%(ipt,options.year,ibin,options.year,qcdeff,qcdeff_err)  )
            else:
                print 'skipping ibin = %s (mass=%.3f, pt = %.3f, rho =%.3f)'%(ibin,mass, pt,rho)
        qcdcov_txt.close()
    
def main(options, args):
    #rhalphabet_output_path = 'ddb_Jun24_v2/ddb_M2_full/TF22_MC_muonCR_SFJul8/rhalphabase.root'
    rhalphabet_output_path = options.idir + "rhalphabase.root" 

    fralphabase = rt.TFile.Open(rhalphabet_output_path, 'read')
    wralphabase = {}
    hist = {}
    nptbins = 6
    nmassbins = 23
    bf_values = {}
    np_lists = {}
    np_arrays = {}
    categories = []
    for ipt in range(1,nptbins+1):
        categories.append('pass_cat%s'%ipt)    
    for cat in categories:
        wralphabase[cat] = fralphabase.Get('w_%s' % cat)

    year = options.year

    nToys = 1000
    #fr = wralphabase['pass_cat1'].obj("nll_simPdf_s_data_obs")
    fr = wralphabase['pass_cat1'].obj("fitresult_simPdf_s_data_obs")
    for cat in categories:
        w =  wralphabase[cat]
        for m in range(1,nmassbins+1):
            name = 'qcd_%s_%s_Bin%s'%(cat,year,m)
            fail_name = 'qcd_%s_%s_Bin%s_func'%(cat.replace('pass','fail'),year,m)
            np_lists[name] = []
            if w.function(name):
                bf_values[name] = w.function(name).getVal()/w.function(fail_name).getVal()

    for i in xrange(nToys):
        randPars = fr.randomizePars()
        for cat in categories:
            w =  wralphabase[cat]
            #w.Print()
            for p in RootIterator(randPars):
                if w.var(p.GetName()):
                    #print 'randomize %s = %e +/- %e' % (p.GetName(), p.getVal(), p.getError())
                    w.var(p.GetName()).setVal(p.getVal())
                    w.var(p.GetName()).setError(p.getError())
            for m in range(1,nmassbins+1):
                name = 'qcd_%s_%s_Bin%s'%(cat,year,m)
                fail_name = 'qcd_%s_%s_Bin%s_func'%(cat.replace('pass','fail'),year,m)
                                       
                if w.function(name):
                    #print 'set %s = %e'%(name,w.function(name).getVal())
                    np_lists[name].append(w.function(name).getVal()/w.function(fail_name).getVal())
                    

    os.system('mkdir -p %s/covMatrixToyHists'%options.idir)
    #for i in range(1,7):
    #    cat = str(i)
    #    os.system('rm  %s/qcdTF_MC_cov_%s.txt'%(options.idir,cat))

    for name, np_list in np_lists.iteritems():
        if options.plot:
           if name not in bf_values: continue
           eff_name = '_'.join(['qcdeff']+name.split('_')[2:]+[year])
           np_arrays[name] = np.array(np_list)
           plt.figure()
           counts, bins = np.histogram(np.array(np_list))
           plt.hist(np.array(np_list),bins=bins,histtype='step',label=r'$%.5f\pm%.5f$'%(bf_values[name],np.std(np_arrays[name])))
           plt.plot([bf_values[name], bf_values[name]], [0, np.max(counts)])
           plt.legend(title=eff_name,loc='best')
           plt.savefig('%s/covMatrixToyHists/'%options.idir+name+'.pdf')
           plt.close()
        print "%s param %s %s"%(eff_name, bf_values[name], np.std(np_arrays[name]))
        cat = name.split('_')[2]
        os.system('echo %s param %s %s >> %s/qcdTF_MC_cov_%s.txt'%(eff_name, bf_values[name], np.std(np_arrays[name]),options.idir,cat))


if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option('-i','--idir', dest='idir', default='./', help='file qcd MC rhalphabet',metavar='idir')
    parser.add_option('-p','--plot', dest='plot', default=True, action='store_true', help='make pdf plots',metavar='plot')
    parser.add_option('-y' ,'--year', type='choice', dest='year', default ='2016',choices=['2016','2017','2018'],help='switch to use different year ', metavar='year')

    (options, args) = parser.parse_args()
    #main(options,args)
    #QCDratio(options,args)
    plotRatio(options,args)     ##plot data from QCDratio and main
