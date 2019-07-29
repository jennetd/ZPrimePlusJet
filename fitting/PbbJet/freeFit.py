import ROOT as rt
from optparse import OptionParser
from RootIterator import RootIterator
import os
import sys


class FreeFit():
    def __init__(self,nm):
        self._poly_degree_mass = {}
        if nm < 0:
            self._poly_degree_mass['pass_cat1'] = 4
            self._poly_degree_mass['pass_cat2'] = 3
            self._poly_degree_mass['pass_cat3'] = 3
            self._poly_degree_mass['pass_cat4'] = 3
            self._poly_degree_mass['pass_cat5'] = 2
            self._poly_degree_mass['pass_cat6'] = 2
        else:
            self._poly_degree_mass['pass_cat1'] = nm
            self._poly_degree_mass['pass_cat2'] = nm
            self._poly_degree_mass['pass_cat3'] = nm
            self._poly_degree_mass['pass_cat4'] = nm
            self._poly_degree_mass['pass_cat5'] = nm
            self._poly_degree_mass['pass_cat6'] = nm
        self._outdir = 'freeFitTest_%s'%nm
        os.system('mkdir -p %s'%(self._outdir))
        os.system('cp freeFitTest/card_rhalphabet_cat*.txt %s/'%(self._outdir))
        os.system('cp freeFitTest/base.root %s/'%(self._outdir))
        os.system('cp freeFitTest/rhalphabase.root %s/'%(self._outdir))
        self._output_path = '%s/base.root'%self._outdir
        self._rhalphabet_output_path = '%s/rhalphabase.root'%(self._outdir)
        self._nptbins = 6
        self._categories=[]
        for ipt in range(1,self._nptbins+1):
            self._categories.append('pass_cat%s'%ipt)
            #self._categories.append('fail_cat%s'%ipt)
        #self._categories=['pass_cat1']
        self._multi = False
        self._exp = False
        self._poly_degree_rho = 2
        self._poly_degree_pt = 2
        self._poly_degree_rho_exp = 3
        self._poly_degree_pt_exp = 1
        self._suffix = '_2017'

        self._background_names = ["wqq", "zqq", "qcd", "tqq"]
        self._signal_names = []
        for mass in [125]:
            for sig in ["hqq", "zhqq", "whqq", "vbfhqq", "tthqq"]:
                self._signal_names.append(sig + str(mass))
            
        self.prefit()

    def prefit(self):
        
        os.system('cp %s %s'%(self._output_path,self._output_path.replace('.root','_update.root')))
        os.system('cp %s %s'%(self._rhalphabet_output_path,self._rhalphabet_output_path.replace('.root','_update.root')))
        fbase = rt.TFile.Open(self._output_path.replace('.root','_update.root'), 'update')
        fralphabase = rt.TFile.Open(self._rhalphabet_output_path.replace('.root','_update.root'), 'update')

        bkgs = self._background_names
        sigs = self._signal_names

        wbase = {}
        wralphabase = {}
        for cat in self._categories:
            wbase[cat] = fbase.Get('w_%s' % cat)
            wralphabase[cat] = fralphabase.Get('w_%s' % cat)

        w = rt.RooWorkspace('w')
        w.factory('mu[1.,0.,20.]')
        x = wralphabase[self._categories[0]].var('x')
        rooCat = rt.RooCategory('cat', 'cat')

        mu = w.var('mu')
        epdf_b = {}
        epdf_s = {}
        datahist = {}
        histpdf = {}
        histpdfnorm = {}
        data = {}
        signorm = {}
        qcd_norms = {}
        qcd_pdfs = {}
        qcd_binpdfs = {}
        blist = []
        for cat in self._categories:
            rooCat.defineType(cat)

        empty_hists = []

        for cat in self._categories:

            empty_hist = rt.TH1D('hist','hist', 23, 40, 201)
            for i in range(1,empty_hist.GetNbinsX()+1):
                empty_hist.SetBinContent(i,1)
            empty_hist.SetBinContent(1,0)
            if 'cat1' in cat:
                empty_hist.SetBinContent(19,0)
                empty_hist.SetBinContent(20,0)
                empty_hist.SetBinContent(21,0)
                empty_hist.SetBinContent(22,0)
                empty_hist.SetBinContent(23,0)
            elif 'cat2' in cat:
                empty_hist.SetBinContent(21,0)
                empty_hist.SetBinContent(22,0)
                empty_hist.SetBinContent(23,0)
            empty_hists.append(empty_hist)

            roolist = rt.RooArgList()
            for i in range(0, self._poly_degree_mass[cat]+1):
                b = rt.RooRealVar('b%i_%s%s'%(i,cat,self._suffix),'b%i_%s%s'%(i,cat,self._suffix),0.1,0,1)
                roolist.add(b)
                blist.append(b)
            qcd = rt.RooBernstein('qcd_free_%s%s'%(cat,self._suffix),'qcd_free_%s%s'%(cat,self._suffix),x,roolist)
            qcd_binpdf = rt.RooParametricShapeBinPdf('qcd_free_bin_%s%s'%(cat,self._suffix), 'qcd_free_bin_%s%s'%(cat,self._suffix), qcd, x, roolist, empty_hist)
            qcd_norm = rt.RooRealVar('qcd_free_bin_%s%s_norm' % (cat, self._suffix),'qcd_free_bin_%s%s_norm' % (cat, self._suffix),1e3,0,1e5)
            qcd_norms['qcd_%s'%cat] = qcd_norm
            qcd_pdfs['qcd_%s'%cat] = qcd
            qcd_binpdfs['qcd_%s'%cat] = qcd_binpdf

            
            norms_b = rt.RooArgList()
            norms_s = rt.RooArgList()
            #norms_b.add(wralphabase[cat].function('qcd_%s%s_norm' % (cat, self._suffix)))
            #norms_s.add(wralphabase[cat].function('qcd_%s%s_norm' % (cat, self._suffix)))
            norms_b.add(qcd_norm)
            norms_s.add(qcd_norm)
            pdfs_b = rt.RooArgList()
            pdfs_s = rt.RooArgList()
            #pdfs_b.add(wralphabase[cat].pdf('qcd_%s%s' % (cat, self._suffix)))
            #pdfs_s.add(wralphabase[cat].pdf('qcd_%s%s' % (cat, self._suffix)))
            pdfs_b.add(qcd_binpdf)
            pdfs_s.add(qcd_binpdf)
            getattr(w, 'import')(qcd, rt.RooFit.RecycleConflictNodes())
            getattr(w, 'import')(qcd_binpdf, rt.RooFit.RecycleConflictNodes())
            getattr(w, 'import')(qcd_norm, rt.RooFit.RecycleConflictNodes())


            data[cat] = wbase[cat].data('data_obs_%s' % cat)
            getattr(w, 'import')(data[cat], rt.RooFit.RecycleConflictNodes())
            for proc in (bkgs + sigs):
                if proc == 'qcd': continue

                datahist['%s_%s' % (proc, cat)] = wbase[cat].data('%s_%s' % (proc, cat))
                histpdf['%s_%s' % (proc, cat)] = rt.RooHistPdf('histpdf_%s_%s' % (proc, cat),
                                                              'histpdf_%s_%s' % (proc, cat),
                                                              rt.RooArgSet(x),
                                                              datahist['%s_%s' % (proc, cat)])
                getattr(w, 'import')(datahist['%s_%s' % (proc, cat)], rt.RooFit.RecycleConflictNodes())
                getattr(w, 'import')(histpdf['%s_%s' % (proc, cat)], rt.RooFit.RecycleConflictNodes())
                #getattr(w, 'import')(datahist['%s_%s' % (proc, cat)], rt.RooFit.RenameConflictNodes(self._suffix))
                #getattr(w, 'import')(histpdf['%s_%s' % (proc, cat)] , rt.RooFit.RenameConflictNodes(self._suffix))
                if 'hqq125' in proc:
                    # signal
                    signorm['%s_%s' % (proc, cat)] = rt.RooRealVar('signorm_%s_%s' % (proc, cat),
                                                                  'signorm_%s_%s' % (proc, cat),
                                                                  datahist['%s_%s' % (proc, cat)].sumEntries(),
                                                                  0, 10. * datahist['%s_%s' % (proc, cat)].sumEntries())
                    signorm['%s_%s' % (proc, cat)].setConstant(True)
                    getattr(w, 'import')(signorm['%s_%s' % (proc, cat)], rt.RooFit.RecycleConflictNodes())
                    histpdfnorm['%s_%s' % (proc, cat)] = rt.RooFormulaVar('histpdfnorm_%s_%s' % (proc, cat),
                                                                         '@0*@1', rt.RooArgList(mu, signorm[
                            '%s_%s' % (proc, cat)]))
                    pdfs_s.add(histpdf['%s_%s' % (proc, cat)])
                    norms_s.add(histpdfnorm['%s_%s' % (proc, cat)])
                else:
                    # background
                    histpdfnorm['%s_%s' % (proc, cat)] = rt.RooRealVar('histpdfnorm_%s_%s' % (proc, cat),
                                                                      'histpdfnorm_%s_%s' % (proc, cat),
                                                                      datahist['%s_%s' % (proc, cat)].sumEntries(),
                                                                      0, 10. * datahist[
                                                                          '%s_%s' % (proc, cat)].sumEntries())
                    histpdfnorm['%s_%s' % (proc, cat)].setConstant(True)
                    getattr(w, 'import')(histpdfnorm['%s_%s' % (proc, cat)], rt.RooFit.RecycleConflictNodes())
                    pdfs_b.add(histpdf['%s_%s' % (proc, cat)])
                    pdfs_s.add(histpdf['%s_%s' % (proc, cat)])
                    norms_b.add(histpdfnorm['%s_%s' % (proc, cat)])
                    norms_s.add(histpdfnorm['%s_%s' % (proc, cat)])
            for proc in ['wqq','zqq']+sigs:
                for syst in ['smear','scale','scalept']:
                    getattr(w, 'import')(wbase[cat].data('%s_%s_%s%sUp' % (proc, cat, syst, self._suffix)), rt.RooFit.RecycleConflictNodes())
                    getattr(w, 'import')(wbase[cat].data('%s_%s_%s%sDown' % (proc, cat, syst, self._suffix)), rt.RooFit.RecycleConflictNodes())
            getattr(w, 'import')(wbase[cat].data('%s_%s_%sUp' % ('hqq125', cat, 'hqq125ptShape')), rt.RooFit.RecycleConflictNodes())
            getattr(w, 'import')(wbase[cat].data('%s_%s_%sDown' % ('hqq125', cat, 'hqq125ptShape')), rt.RooFit.RecycleConflictNodes())

            epdf_b[cat] = rt.RooAddPdf('epdf_b_' + cat, 'epdf_b_' + cat, pdfs_b, norms_b)
            epdf_s[cat] = rt.RooAddPdf('epdf_s_' + cat, 'epdf_s_' + cat, pdfs_s, norms_s)

            #getattr(w, 'import')(epdf_b[cat], rt.RooFit.RecycleConflictNodes())
            #getattr(w, 'import')(epdf_s[cat], rt.RooFit.RecycleConflictNodes())
            getattr(w, 'import')(epdf_b[cat], rt.RooFit.RenameConflictNodes(self._suffix))
            getattr(w, 'import')(epdf_s[cat], rt.RooFit.RenameConflictNodes(self._suffix))

        ## arguments = ["data_obs","data_obs",rt.RooArgList(x),rooCat]

        ## m = rt.std.map('string, RooDataHist*')()
        ## for cat in categories:
        ##    m.insert(rt.std.pair('string, RooDataHist*')(cat, data[cat]))
        ## arguments.append(m)

        ## combData = getattr(r,'RooDataHist')(*arguments)

        cat = self._categories[0]
        args = data[cat].get(0)

        combiner = rt.CombDataSetFactory(args, rooCat)

        for cat in self._categories:
            combiner.addSetBin(cat, data[cat])
        combData = combiner.done('data_obs', 'data_obs')

        simPdf_b = rt.RooSimultaneous('simPdf_b', 'simPdf_b', rooCat)
        simPdf_s = rt.RooSimultaneous('simPdf_s', 'simPdf_s', rooCat)
        for cat in self._categories:
            simPdf_b.addPdf(epdf_b[cat], cat)
            simPdf_s.addPdf(epdf_s[cat], cat)

        mu.setVal(1.)

        getattr(w, 'import')(simPdf_b, rt.RooFit.RecycleConflictNodes())
        getattr(w, 'import')(simPdf_s, rt.RooFit.RecycleConflictNodes())
        getattr(w, 'import')(combData, rt.RooFit.RecycleConflictNodes())

        w.Print('v')
        simPdf_b = w.pdf('simPdf_b')
        simPdf_s = w.pdf('simPdf_s')
        combData = w.data('data_obs')
        #x = w.var('x')
        rooCat = w.cat('cat')
        mu = w.var('mu')
        CMS_set = rt.RooArgSet()
        CMS_set.add(rooCat)
        CMS_set.add(x) 
        print x.getMax('qcd_free_bin_pass_cat1_2017_x_range_bin16')
        

        opt = rt.RooLinkedList()
        opt.Add(rt.RooFit.CloneData(False))
        allParams = simPdf_b.getParameters(combData)
        rt.RooStats.RemoveConstantParameters(allParams)
        opt.Add(rt.RooFit.Constrain(allParams))

        mu.setVal(1)
        mu.setConstant(True)



        nll = simPdf_s.createNLL(combData)
        m2 = rt.RooMinimizer(nll)
        m2.setStrategy(2)
        m2.setMaxFunctionCalls(100000)
        m2.setMaxIterations(100000)
        m2.setPrintLevel(-1)
        m2.setPrintEvalErrors(-1)
        m2.setEps(1e-5)
        m2.optimizeConst(2)

        
        migrad_status = m2.minimize('Minuit2', 'migrad')
        improve_status = m2.minimize('Minuit2', 'improve')
        hesse_status = m2.minimize('Minuit2', 'hesse')
        
        fr = m2.save()
        fr.Print('v')

        c = rt.TCanvas('c','c',500,400)
        w.writeToFile(self._rhalphabet_output_path.replace('.root','_newupdate.root'), True)

        pvalues = {}
        obsvalues = {}
        for cat in self._categories:
            print cat
            os.system("pushd %s; "%(self._outdir) + 
                      "combine -M GoodnessOfFit card_rhalphabet_%s.txt --freezeParameters tqqeffSF_2017,tqqnormSF_2017 --algo saturated -n %s; "%(cat.replace('pass_',''),cat) + 
                      "combine -M GoodnessOfFit card_rhalphabet_%s.txt --freezeParameters tqqeffSF_2017,tqqnormSF_2017 --algo saturated -n %s -t 500 --toysFreq; "%(cat.replace('pass_',''),cat) +
                      "popd")

            obs_tfile = rt.TFile.Open('%s/higgsCombine%s.GoodnessOfFit.mH120.root'%(self._outdir,cat),'read')
            obs_limit = obs_tfile.Get('limit')
            obs_limit.GetEntry(0)
            obs_q = obs_limit.limit
            exp_tfile = rt.TFile.Open('%s/higgsCombine%s.GoodnessOfFit.mH120.123456.root'%(self._outdir,cat))
            exp_limit = exp_tfile.Get('limit')
            pass_q = exp_limit.Draw('limit','limit>%f'%obs_q)
            all_q = exp_limit.Draw('limit','limit>0')
            obsvalues[cat] = obs_q
            pval = 100.*pass_q/all_q
            pvalues[cat] = pval
            print ''
            print '%s obs = %.2f'%(cat, obs_q)
            print '%s p-value = %.1f%%'%(cat, pval)
            print ''
        
        icat = 0
        for cat in self._categories:
            icat += 1
            rooCat.setLabel(cat)
            frame = x.frame()
            combData.plotOn(frame,rt.RooFit.Cut("cat==cat::%s"%cat))
            simPdf_s.plotOn(frame,rt.RooFit.Slice(rooCat,cat),rt.RooFit.ProjWData(rt.RooArgSet(rooCat),combData))
            frame.Draw()
            c.Print("%s/x_%s.pdf"%(self._outdir,cat))

        for cat in self._categories:
            print '%s p-value = %.1f%%'%(cat, pvalues[cat])
        

        # final sensitivity check
        os.system("pushd %s; "%(self._outdir) + 
                  "combineCards.py  cat1_2017=card_rhalphabet_cat1.txt  cat2_2017=card_rhalphabet_cat2.txt  cat3_2017=card_rhalphabet_cat3.txt  cat4_2017=card_rhalphabet_cat4.txt  cat5_2017=card_rhalphabet_cat5.txt  cat6_2017=card_rhalphabet_cat6.txt > card_rhalphabet_all_2017.txt; " + 
                  "text2workspace.py -P HiggsAnalysis.CombinedLimit.PhysicsModel:multiSignalModel -m 125  --PO verbose --PO 'map=.*/*hqq125:r[1,0,20]' --PO 'map=.*/zqq:r_z[1,0,20]' card_rhalphabet_all_2017.txt  -o card_rhalphabet_all_2017_floatZ_freeFit.root; " +
                  "combine -M Significance -t -1 --toysFreq card_rhalphabet_all_2017_floatZ_freeFit.root  --setParameters r=1,r_z=1 --redefineSignalPOIs r  --freezeParameters tqqnormSF_2017,tqqeffSF_2017; " +
                  "combine -M Significance -t -1 --toysFreq card_rhalphabet_all_2017_floatZ_freeFit.root  --setParameters r=1,r_z=1 --redefineSignalPOIs r_z  --freezeParameters tqqnormSF_2017,tqqeffSF_2017; " +
                  "combine -M FitDiagnostics card_rhalphabet_all_2017_floatZ_freeFit.root  --setParameters r=1,r_z=1 --redefineSignalPOIs r  --freezeParameters tqqnormSF_2017,tqqeffSF_2017 --plots -t -1 --toysFreq; " + 
                  #"combine -M GoodnessOfFit --algo saturated card_rhalphabet_all_2017_floatZ_freeFit.root  --setParameters r=1,r_z=1 --redefineSignalPOIs r  --freezeParameters tqqnormSF_2017,tqqeffSF_2017; " + 
                  #"combine -M GoodnessOfFit --algo saturated card_rhalphabet_all_2017_floatZ_freeFit.root  --setParameters r=1,r_z=1 --redefineSignalPOIs r  --freezeParameters tqqnormSF_2017,tqqeffSF_2017 -t 200 --toysFreq; " +
                  "popd")

def reset(w, fr, exclude=None):
    for p in RootIterator(fr.floatParsFinal()):
        if exclude is not None and exclude in p.GetName(): continue
        if w.var(p.GetName()):
            print 'setting %s = %e +/- %e from %s' % (p.GetName(), p.getVal(), p.getError(), fr.GetName())
            w.var(p.GetName()).setVal(p.getVal())
            w.var(p.GetName()).setError(p.getError())
    return True


if __name__ == '__main__':
    rt.gROOT.SetBatch()
    parser = OptionParser()
    parser.add_option("--nm", dest="nm", default=-1, type="int", help="mass order", metavar="nm")

    (options, args) = parser.parse_args()
    ff = FreeFit(options.nm)
