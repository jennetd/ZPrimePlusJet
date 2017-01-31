import os
import sys
import ROOT
from ROOT import *
gROOT.SetBatch(ROOT.kTRUE);
gStyle.SetOptStat(0)
gStyle.SetOptTitle(0)
gStyle.SetNumberContours(80)
gStyle.SetPalette(87)
import array

# Plot results of optimization studies

# Grid points
opt_vars = ["tau21_ddt", "dcsv"]
opt_var_values = {
	"tau21_ddt":[0.35,0.4,0.45,0.5,0.55,0.6],
	"dcsv":[0.7,0.8,0.85,0.9,0.95],
}

class BrazilPlot():
	def __init__(self, name, x=None):
		self._name = name
		if x:
			self._x = x
		else:
			self._x = []
		self._exp_limits = []
		self._exp_limits_p1 = []
		self._exp_limits_p2 = []
		self._exp_limits_m1 = []
		self._exp_limits_m2 = []
		self._obs_limits = []

		self._x_title = ""
		self._y_title = "Limit"
		self._x_min = None
		self._x_max = None
		self._y_min = None
		self._y_max = None
		self._logx = False
		self._logy = True
		self._legend_x1 = 0.7
		self._legend_y1 = 0.65
		self._legend_x2 = 0.88
		self._legend_y2 = 0.88

	def SetX(self, x):
		self._x = x

	def SetExpLimits(self, exp_limits):
		if len(exp_limits) != len(self._x):
			print "[BrazilPlot::SetExpLimit] ERROR : Length mismatch between expected limits and x points."
			sys.exit(1)
		self._exp_limits = exp_limits

	# Set +/- 1 sigma limits
	def SetExp1SLimits(self, exp_p1_limits, exp_m1_limits):
		if len(exp_p1_limits) != len(self._x):
			print "[BrazilPlot::SetExp1SLimits] ERROR : Length mismatch between expected (+1s) limits and x points."
			sys.exit(1)
		if len(exp_m1_limits) != len(self._x):
			print "[BrazilPlot::SetExp1SLimits] ERROR : Length mismatch between expected (-1s) limits and x points."
			sys.exit(1)
		self._exp_limits_p1 = exp_p1_limits
		self._exp_limits_m1 = exp_m1_limits

	# Set +/- 2 sigma limits
	def SetExp2SLimits(self, exp_p2_limits, exp_m2_limits):
		if len(exp_p2_limits) != len(self._x):
			print "[BrazilPlot::SetExp2SLimits] ERROR : Length mismatch between expected (+2s) limits and x points."
			sys.exit(1)
		if len(exp_m2_limits) != len(self._x):
			print "[BrazilPlot::SetExp2SLimits] ERROR : Length mismatch between expected (-2s) limits and x points."
			sys.exit(1)
		self._exp_limits_p2 = exp_p2_limits
		self._exp_limits_m2 = exp_m2_limits

	def SetObsLimits(self, obs_limits):
		if len(obs_limits) != len(self._x):
			print "[BrazilPlot::SetObsLimits] ERROR : Length mismatch between observed limits and x points."
			sys.exit(1)
		self._obs_limits = obs_limits

	def SetXaxisLimits(self, x_min, x_max):
		self._x_min = x_min
		self._x_max = x_max

	def SetYaxisLimits(self, y_min, y_max):
		self._y_min = y_min
		self._y_max = y_max

	def SetLogx(self, logx=True):
		self._logx = logx

	def SetLogy(self, logy=True):
		self._logy = logy

	def SetLegendLimits(self, x1, y1, x2, y2):
		self._legend_x1 = x1
		self._legend_y1 = y1
		self._legend_x2 = x2
		self._legend_y2 = y2

	def Draw(self):
		self._canvas = TCanvas(name, name, 800, 600)
		self._legend = TLegend(self._legend_x1, self._legend_y1, self._legend_x2, self._legend_y2)
		self._legend.SetFillColor(0)
		self._legend.SetBorderSize(0)

		if not (self._x_min and self._x_max):
			min_x_value = min(self._x)
			max_x_value = max(self._x)
			if self._logx:
				self._x_min = min_x_value / 10.
				self._x_max = max_x_value * 10.
			else:
				self._x_min = min_x_value - 0.1 * (max_x_value - min_x_value)
				self._x_max = max_x_value + 0.1 * (max_x_value - min_x_value)

		if not (self._y_min and self._y_max):
			min_y_value = min(self._y)
			max_y_value = max(self._y)
			if self._logy:
				self._y_min = min_y_value / 10.
				self._y_max = max_y_value * 10.
			else:
				self._y_min = min_y_value - 0.166 * (max_y_value - min_y_value)
				self._y_max = max_y_value + 0.166 * (max_y_value - min_y_value)

		self._frame = TH1F("frame_{}".format(name), "frame_{}".format(name), 100, self._x_min, self._x_max)
		self._frame.SetMinimum(self._y_min)
		self._frame.SetMaximum(self._y_max)
		self._frame.GetXaxis().SetTitle(self._x_title)
		self._frame.GetYaxis().SetTitle(self._y_title)
		self._frame.Draw()

		# TGraphAsymmErrors (Int_t n, const Double_t *x, const Double_t *y, const Double_t *exl=0, const Double_t *exh=0, const Double_t *eyl=0, const Double_t *eyh=0)
		self._tg_exp_limits_2sigma = TGraphAsymmErrors(len(self._x), 
										array.array("d", self._x), array.array("d", self._exp_limits), 
										array.array("d", [0.]*len(self._x)), 
										array.array("d", [0.]*len(self._x)), 
										array.array("d", [math.abs(self._exp_limits[i]-self._exp_limits_m2[i]) for i in len(self._x)]), 
										array.array("d", [math.abs(self._exp_limits_p2[i]-self._exp_limits[i]) for i in len(self._x)])
									)
		self._tg_exp_limits_1sigma = TGraphAsymmErrors(len(self._x), 
										array.array("d", self._x), array.array("d", self._exp_limits), 
										array.array("d", [0.]*len(self._x)), 
										array.array("d", [0.]*len(self._x)), 
										array.array("d", [math.abs(self._exp_limits[i]-self._exp_limits_m1[i]) for i in len(self._x)]), 
										array.array("d", [math.abs(self._exp_limits_p1[i]-self._exp_limits[i]) for i in len(self._x)])
									)
		self._tg_exp_limits = TGraph(len(self._x), array.array("d", self._x), array.array("d", self._exp_limits))
		self._tg_obs_limits = TGraph(len(self._x), array.array("d", self._x), array.array("d", self._obs_limits))

		self._tg_exp_limits_2sigma.SetFillColor(ROOT.kYellow)
		self._tg_exp_limits_2sigma.Draw("F")
		self._tg_exp_limits_1sigma.SetFillColor(ROOT.kGreen)
		self._tg_exp_limits_1sigma.Draw("F")
		self._tg_exp_limits.SetLineColor(ROOT.kBlue)
		self._tg_exp_limits.SetLineWidth(2)
		self._tg_exp_limits.SetLineStyle(2)
		self._tg_exp_limits.Draw("l")
		self._tg_obs_limits.SetLineColor(ROOT.kBlack)
		self._tg_obs_limits.SetLineWidth(2)
		self._tg_obs_limits.SetLineStyle(1)
		self._tg_obs_limits.SetMarkerColor(ROOT.kBlack)
		self._tg_obs_limits.SetMarkerSize(1)
		self._tg_obs_limits.SetMarkerStyle(20)
		self._tg_obs_limits.Draw("pl")

		self._legend.SetHeader("95% CL Upper Limits")
		self._legend.AddEntry(self._tg_obs_limits, "Observed", "pl")
		self._legend.AddEntry(self._tg_exp_limits, "Expected", "l")
		self._legend.AddEntry(self._tg_exp_limits_1sigma, "Expected #pm1#sigma", "f")
		self._legend.AddEntry(self._tg_exp_limits_2sigma, "Expected #pm2#sigma", "f")
		self._legend.Draw()

	def SaveAs(self, directory=None, path=None):
		if path:
			self._canvas.SaveAs(path)
		elif directory:
			self._canvas.SaveAs("{}/{}.pdf".format(directory, self._canvas.GetName()))
		else:
			self._canvas.SaveAs("{}.pdf".format(self._canvas.GetName()))


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

def MakeBrazilPlot(selection_name):
	x = []
	exp_limits = []
	exp_limits_m1 = []
	exp_limits_m2 = []
	exp_limits_p1 = []
	exp_limits_p2 = []
	for mass in [50, 75, 100, 125, 150, 250]:
		x.append(mass)
		print "Opening " + "/uscms_data/d3/dryu/DAZSLE/data/LimitSetting/Optimization/{}/combine/higgsCombinecombine_Pbb_M{}.Asymptotic.mH{}.root".format(selection_name, mass, mass)
		f = TFile("/uscms_data/d3/dryu/DAZSLE/data/LimitSetting/Optimization/{}/combine/higgsCombinecombine_Pbb_M{}.Asymptotic.mH{}.root".format(selection_name, signal_mass, signal_mass), "READ")
		t = f.Get("limit")
		if not t:
			print "[PlotExpectedLimitGrid] WARNING : Limit job failed for tau21DDT={}, dcsv={}. Setting to zero and moving on.".format(tau21_ddt_value, dcsv_value)
			h_exp_limit.SetBinContent(xbin, ybin, 0.)
			continue
		t.GetEntry(0)
		exp_limits_m2.append(t.GetLeaf("limit").GetValue(0))
		t.GetEntry(1)
		exp_limits_m1.append(t.GetLeaf("limit").GetValue(0))
		t.GetEntry(2)
		exp_limits.append(t.GetLeaf("limit").GetValue(0))
		t.GetEntry(3)
		exp_limits_p1.append(t.GetLeaf("limit").GetValue(0))
		t.GetEntry(4)
		exp_limits_p2.append(t.GetLeaf("limit").GetValue(0))
		t.GetEntry(5)
		obs_limits.append(t.GetLeaf("limit").GetValue(0))
	brazil_plot = BrazilPlot("limits_{}".format(selection_name))
	brazil_plot._x_title = "m_{#Phi} [GeV]"
	brazil_plot._y_title = "#sigma [pb]"
	brazil_plot.SetLogy()
	brazil_plot.Draw()
	brazil_plot.SaveAs(directory="/uscms_data/d3/dryu/DAZSLE/data/LimitSetting/Optimization/figures")


if __name__ == "__main__":
	for signal_mass in [50,75,100,125,150,250]:
		for jet_type in ["AK8"]:#, "CA15"]:
			PlotExpectedLimitGrid(signal_mass, jet_type)

	for jet_type in ["AK8"]:
		for tau21_ddt in [0.4]:
			for dcsv in [0.9]:
				selection_name = "jet_type_{}_tau21_ddt_{}_dcsv_{}".format(jet_type, tau21_ddt_value, dcsv_value)
				MakeBrazilPlot(selection_name)
	