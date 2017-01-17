import os
import sys
import ROOT
from ROOT import *
gROOT.SetBatch(ROOT.kTRUE);
gStyle.SetOptStat(0)
gStyle.SetOptTitle(0)
gStyle.SetNumberContours(80)
gStyle.SetPalette(87)

# Plot results of optimization studies

# Grid points
opt_vars = ["tau21_ddt", "dcsv"]
opt_var_values = {
	"tau21_ddt":[0.35,0.4,0.45,0.5,0.55,0.6],
	"dcsv":[0.7,0.8,0.85,0.9,0.95],
}

def PlotExpectedLimitGrid(signal_mass, jet_type):
	h_exp_limit = TH2D("h_exp_limit_M{}".format(signal_mass), "h_exp_limit_{}".format(signal_mass), len(opt_var_values["tau21_ddt"]), 0.5, len(opt_var_values["tau21_ddt"]) + 0.5, len(opt_var_values["dcsv"]), 0.5, len(opt_var_values["dcsv"]) + 0.5)
	for xbin in xrange(1, len(opt_var_values["tau21_ddt"]) + 1):
		h_exp_limit.GetXaxis().SetBinLabel(xbin, str(round(opt_var_values["tau21_ddt"][xbin-1], 2)))
	for ybin in xrange(1, len(opt_var_values["dcsv"]) + 1):
		h_exp_limit.GetYaxis().SetBinLabel(ybin, str(round(opt_var_values["dcsv"][ybin-1], 2)))

	for xbin, tau21_ddt_value in enumerate(opt_var_values["tau21_ddt"], start=1):
		for ybin, dcsv_value in enumerate(opt_var_values["dcsv"], start=1):
			selection_name = "jet_type_{}_tau21_ddt_{}_dcsv_{}".format(jet_type, tau21_ddt_value, dcsv_value)
			print "Opening " + "/uscms_data/d3/dryu/DAZSLE/data/LimitSetting/Optimization/{}/combine/higgsCombinecombine_Pbb_M{}.Asymptotic.mH{}.root".format(selection_name, signal_mass, signal_mass)
			f = TFile("/uscms_data/d3/dryu/DAZSLE/data/LimitSetting/Optimization/{}/combine/higgsCombinecombine_Pbb_M{}.Asymptotic.mH{}.root".format(selection_name, signal_mass, signal_mass), "READ")
			t = f.Get("limit")
			if not t:
				print "[PlotExpectedLimitGrid] WARNING : Limit job failed for tau21DDT={}, dcsv={}. Setting to zero and moving on.".format(tau21_ddt_value, dcsv_value)
				h_exp_limit.SetBinContent(xbin, ybin, 0.)
				continue
			t.GetEntry(2)
			exp_limit = t.GetLeaf("limit").GetValue(0)
			h_exp_limit.SetBinContent(xbin, ybin, exp_limit)

	c_exp_limit = TCanvas("c_exp_limit_M{}".format(signal_mass), "c_exp_limit_M{}".format(signal_mass), 800, 600)
	c_exp_limit.SetRightMargin(0.2)
	h_exp_limit.GetXaxis().SetTitle("#tau_{21}^{DDT} cut")
	h_exp_limit.GetYaxis().SetTitle("Double b-tag cut")
	h_exp_limit.Draw("text colz")
	c_exp_limit.SaveAs("~/DAZSLE/data/LimitSetting/Optimization/figures/{}.pdf".format(c_exp_limit.GetName()))

if __name__ == "__main__":
	for signal_mass in [50,75,100,125,150,250]:
		for jet_type in ["AK8"]:#, "CA15"]:
			PlotExpectedLimitGrid(signal_mass, jet_type)