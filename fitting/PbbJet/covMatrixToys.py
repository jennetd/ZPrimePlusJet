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
    fr = wralphabase['pass_cat1'].obj("nll_simPdf_s_data_obs")
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
    parser.add_option('-p','--plot', dest='plot', default='./', help='make pdf plots',metavar='plot')
    parser.add_option('-y' ,'--year', type='choice', dest='year', default ='2016',choices=['2016','2017','2018'],help='switch to use different year ', metavar='year')

    (options, args) = parser.parse_args()
    main(options,args)
