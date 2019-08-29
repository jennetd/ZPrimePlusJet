import sys
sys.path.insert(0, '/uscms_data/d3/ncsmith/dazsle/sl7combine/CMSSW_10_2_13/src/rhalphalib')
import rhalphalib as rl
import ROOT
rl.util.install_roofit_helpers()
import numpy as np
import re

def createdeco(qcdfit, fbase, year, fout):
    def getconst(name):
        p = qcdfit.constPars().find(name)
        if p == None:
            raise ValueError(name)
        return p.getVal()

    rhalphabase = ROOT.TFile.Open(fbase + 'rhalphabase.root')
    with open(fbase + 'card_rhalphabet_all_%s.txt' % year) as fin:
        card_in = list(fin)

    ptbins = np.array([450, 500, 550, 600, 675, 800, 1200])
    npt = len(ptbins) - 1
    msdbins = np.linspace(40, 201, 24)
    msd = rl.Observable('x', msdbins)

    # here we derive these all at once with 2D array
    ptpts, msdpts = np.meshgrid(ptbins[:-1] + 0.3 * np.diff(ptbins), msdbins[:-1] + 0.5 * np.diff(msdbins), indexing='ij')
    rhopts = 2*np.log(msdpts/ptpts)
    ptscaled = (ptpts - 450.) / (1200. - 450.)
    rhoscaled = (rhopts - (-6)) / ((-2.1) - (-6))
    validbins = (rhoscaled >= 0) & (rhoscaled <= 1)
    validbins[:, 0] = False  # cut msd 40-47
    # validbins[:, 10:13] = False  # blind
    rhoscaled[~validbins] = 1  # we will mask these out later

    tf_MCtempl = rl.BernsteinPoly("qcdfit_tf_%s" % year, (2, 2), ['pt', 'rho'], limits=(-10, 10))
    param_names = ['p%dr%d_%s' % (ipt, irho, year) for ipt in range(3) for irho in range(3)]
    decoVector = rl.DecorrelatedNuisanceVector.fromRooFitResult(tf_MCtempl.name + '_deco', qcdfit, param_names)
    tf_MCtempl.parameters = decoVector.correlated_params.reshape(tf_MCtempl.parameters.shape)
    qcdeff = getconst("qcdeff_%s" % year)
    tf_MCtempl_params_final = tf_MCtempl(ptscaled, rhoscaled)

    tf_dataResidual = rl.BernsteinPoly("dataResidual_%s" % year, (2, 2), ['pt', 'rho'], limits=(-10, 10), coefficient_transform=None)
    tf_dataResidual_params = tf_dataResidual(ptscaled, rhoscaled)
    tf_params = qcdeff * tf_MCtempl_params_final * tf_dataResidual_params

    with open("card_rhalphabet_all_%s.txt" % year, "w") as card:
        for line in card_in:
            if line.startswith('kmax'):
                line = 'kmax * number of nuisance parameters'
            m = re.match("^shapes qcd *cat\d_(201[678])_(fail|pass)_(cat\d)", line)
            if m is not None:
                line = "shapes qcd                      {2}_{0}_{1}_{2}     qcdfit_decorrelated.root qcdfit_deco_{0}:$PROCESS_{1}_{2}_{0}\n".format(*m.groups())
            m = re.match("^shapes \* +(\w+) +(.*)", line)
            if m is not None and 'FAKE' not in line:
                line = "shapes *                        {0}     martin/{1}\n".format(*m.groups())
            if line.startswith("qcdeff"):
                continue
            card.write(line)
        for param in decoVector.parameters:
            card.write("%s param 0 1\n" % param.name)

        for (i, j), param in np.ndenumerate(tf_dataResidual.parameters):
            param.name = 'p%dr%d_%s' % (i, j, year)
            # already in card
            # card.write("%s flatParam\n" % param.name)

        fout.cd()
        ws = ROOT.RooWorkspace("qcdfit_deco_%s" % year)
        for ipt in range(npt):
            wbase = rhalphabase.Get('w_fail_cat%d' % (ipt + 1, ))
            qcdinV = np.full(msd.nbins, None)
            qcduncV = np.full(msd.nbins, None)
            qcdparamV = np.full(msd.nbins, None)
            for imsd in range(msd.nbins):
                qcdin_name = "qcd_fail_cat{ptcat}_Bin{msdbin}_In_{year}".format(ptcat=ipt + 1, msdbin=imsd + 1, year=year)
                qcdunc_name = "qcd_fail_cat{ptcat}_Bin{msdbin}_Unc_{year}".format(ptcat=ipt + 1, msdbin=imsd + 1, year=year)
                qcdparam_name = "qcd_fail_cat{ptcat}_Bin{msdbin}_{year}".format(ptcat=ipt + 1, msdbin=imsd + 1, year=year)
                qcdin = wbase.var(qcdin_name).getVal()
                qcdunc = wbase.var(qcdunc_name).getVal()
                # already in card
                # card.write("%s flatParam\n" % qcdparam_name)
                valid = validbins[ipt, imsd]
                if not valid and qcdin > 0.:
                    print("nonzero qcdin for bin %d,%d: %d" % (ipt, imsd, qcdin))
                qcdinV[imsd] = rl.IndependentParameter(qcdin_name, qcdin, constant=True)
                qcduncV[imsd] = rl.IndependentParameter(qcdunc_name, qcdunc, constant=True)
                if valid:
                    qcdparamV[imsd] = rl.IndependentParameter(qcdparam_name, 0., lo=-50, hi=50)
                else:
                    qcdparamV[imsd] = rl.IndependentParameter(qcdparam_name, 0., constant=True)

            scaledparams = qcdinV * (qcduncV**qcdparamV)
            fail_qcd = rl.ParametericSample('qcd_fail_cat%d_%s' % (ipt + 1, year), rl.Sample.BACKGROUND, msd, scaledparams)
            fail_qcd.renderRoofit(ws)
            pass_qcd = rl.TransferFactorSample('qcd_pass_cat%d_%s' % (ipt + 1, year), rl.Sample.BACKGROUND, tf_params[ipt, :], fail_qcd)
            pass_qcd.renderRoofit(ws)

    ws.Write()
    return ws


file_qcdfit16 = 'martin/ddb2016_Jun24_v3/ddb_M2_full/TF22_MC_w2Fitv2/rhalphabase.root'
file_qcdfit17 = 'martin/ddb_Jun24_v2/ddb_M2_full/TF22_MC_w2Fit/rhalphabase.root'
file_qcdfit18 = 'martin/ddb2018_Jun24_v3/ddb_M2_full/TF22_MC_w2Fit/rhalphabase.root'
fit16 = ROOT.TFile.Open(file_qcdfit16).Get("w_pass_cat1").obj("fitresult_simPdf_s_data_obs")
fit17 = ROOT.TFile.Open(file_qcdfit17).Get("w_pass_cat1").obj("fitresult_simPdf_s_data_obs")
fit18 = ROOT.TFile.Open(file_qcdfit18).Get("w_pass_cat1").obj("fitresult_simPdf_s_data_obs")

fbase16 = 'martin/ddb2016_Jun24_v3/ddb_M2_full/TF22_qcdTF22uncV5_muonCRv7_SFAug8_looserWZ_p80_v1/'
fbase17 = 'martin/ddb_Jun24_v2/ddb_M2_full/TF22_qcdTF22uncV5_muonCRv7_SFJul8_v2/'
fbase18 = 'martin/ddb2018_Jun24_v3/ddb_M2_full/TF22_qcdTF22uncV5_muonCRv7_SFJul8_v1/'

fout = ROOT.TFile.Open("qcdfit_decorrelated.root", "recreate")
ws2016 = createdeco(fit16, fbase16, '2016', fout)
ws2017 = createdeco(fit17, fbase17, '2017', fout)
ws2018 = createdeco(fit18, fbase18, '2018', fout)
