import ROOT as rt
rt.gROOT.SetBatch()
from RootIterator import RootIterator
import os
import sys
import numpy as np
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt


if __name__ == '__main__':
    
    output_path = 'ddb_Jun24_v2/ddb_M2_full/TF22_MC_muonCR_SFJul8/base.root'
    rhalphabet_output_path = 'ddb_Jun24_v2/ddb_M2_full/TF22_MC_muonCR_SFJul8/rhalphabase.root'

    fbase = rt.TFile.Open(output_path, 'read')
    fralphabase = rt.TFile.Open(rhalphabet_output_path, 'read')
    wbase = {}
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
        wbase[cat] = fbase.Get('w_%s' % cat)
        wralphabase[cat] = fralphabase.Get('w_%s' % cat)

    nToys = 100
    fr = wralphabase['pass_cat1'].obj("nll_simPdf_s_data_obs")
    for cat in categories:
        w =  wralphabase[cat]
        for m in range(1,nmassbins+1):
            name = 'qcd_%s_2017_Bin%s'%(cat,m)
            fail_name = 'qcd_%s_2017_Bin%s_func'%(cat.replace('pass','fail'),m)
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
                name = 'qcd_%s_2017_Bin%s'%(cat,m)
                fail_name = 'qcd_%s_2017_Bin%s_func'%(cat.replace('pass','fail'),m)
                                       
                if w.function(name):
                    #print 'set %s = %e'%(name,w.function(name).getVal())
                    np_lists[name].append(w.function(name).getVal()/w.function(fail_name).getVal())
                    

    os.system('mkdir -p covMatrixToyHists')
    os.system('cp ddb_Jun24_v2/ddb_M2_full/TF22_qcdTF22_muonCR_SFJul8/card_rhalphabet_cat*.txt  ddb_Jun24_v2/ddb_M2_full/TF22_qcdTF22_muonCR_SFJul8/*base.root ddb_Jun24_v2/ddb_M2_full/TF22_qcdTF22_muonCR_SFJul8/*muonCR*.* covMatrixToyHists/')
    for name, np_list in np_lists.iteritems():
        if name not in bf_values: continue
        eff_name = '_'.join(['qcdeff']+name.split('_')[2:]+['2017'])
        np_arrays[name] = np.array(np_list)
        plt.figure()
        counts, bins = np.histogram(np.array(np_list))
        plt.hist(np.array(np_list),bins=bins,histtype='step',label=r'$%.5f\pm%.5f$'%(bf_values[name],np.std(np_arrays[name])))
        plt.plot([bf_values[name], bf_values[name]], [0, np.max(counts)])
        plt.legend(title=eff_name,loc='best')
        plt.savefig('covMatrixToyHists/'+name+'.pdf')
        plt.close()

        print "%s param %s %s"%(eff_name, bf_values[name], np.std(np_arrays[name]))
        cat = name.split('_')[2]
        os.system('echo %s param %s %s >> covMatrixToyHists/card_rhalphabet_%s.txt'%(eff_name, bf_values[name], np.std(np_arrays[name]),cat))
