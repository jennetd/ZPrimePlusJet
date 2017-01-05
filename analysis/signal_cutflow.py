import os
import sys
import ROOT
from DAZSLE.ZPrimePlusJet.analysis_base import AnalysisBase
from math import ceil, sqrt

from ROOT import gInterpreter, gSystem, gROOT, gStyle, Root, TCanvas, TLegend, TH1F, TFile, TGraphErrors
gInterpreter.Declare("#include \"MyTools/RootUtils/interface/SeabornInterface.h\"")
gInterpreter.Declare("#include \"MyTools/RootUtils/interface/HistogramManager.h\"")
gSystem.Load("/uscms/home/dryu/DAZSLE/CMSSW_8_0_20/lib/slc6_amd64_gcc530/libMyToolsRootUtils.so")
gInterpreter.Declare("#include \"MyTools/AnalysisTools/interface/EventSelector.h\"")
gSystem.Load("/uscms/home/dryu/DAZSLE/CMSSW_8_0_20/lib/slc6_amd64_gcc530/libMyToolsAnalysisTools.so")
gROOT.SetBatch(ROOT.kTRUE);
gStyle.SetOptStat(0)
gStyle.SetOptTitle(0)
seaborn = Root.SeabornInterface()
seaborn.Initialize()

class SignalCutflow(AnalysisBase):
	def __init__(self):
		super(SignalCutflow, self).__init__()
		self._output_path = ""

	def set_output_path(self, output_path):
		self._output_path = output_path

	def start(self):
		self._processed_events = 0

		# Histograms
		self._histograms = ROOT.Root.HistogramManager()
		self._histograms.AddPrefix("h_")
		self._histograms.AddTH1D("input_nevents", "input_nevents", "", 1, -0.5, 0.5)
		self._histograms.AddTH1D("input_nevents_weighted", "input_nevents_weighted", "", 1, -0.5, 0.5)
		self._histograms.AddTH1D("pass_nevents", "pass_nevents", "", 1, -0.5, 0.5)
		self._histograms.AddTH1D("pass_nevents_weighted", "pass_nevents_weighted", "", 1, -0.5, 0.5)
		self._histograms.AddTH1D("AK8Jet_msd", "AK8Jet_msd", "m_{sd} [GeV]", 1000, 0., 1000.)
		self._histograms.AddTH1D("AK8Jet_doublecsv", "AK8Jet_doublecsv", "Double b-tag", 40, -1., 1.)
		self._histograms.AddTH1D("AK8Jet_tau21", "AK8Jet_tau21", "#tau_{21}", 20, 0., 1.)
		self._histograms.AddTH1D("AK8Jet_tau32", "AK8Jet_tau32", "#tau_{32}", 20, 0., 1.)
		self._histograms.AddTH2D("AK8Jet_msd_vs_doublecsv", "AK8Jet_msd_vs_doublecsv", "m_{sd} [GeV]", 100, 0., 1000., "Double b-tag", 20, -1., 1.)
		self._histograms.AddTH2D("AK8Jet_msd_vs_tau21", "AK8Jet_msd_vs_tau21", "m_{sd} [GeV]", 100, 0., 1000., "#tau_{21}", 20, 0., 1.)
		self._histograms.AddTH2D("AK8Jet_msd_vs_tau32", "AK8Jet_msd_vs_tau32", "m_{sd} [GeV]", 100, 0., 1000., "#tau_{32}", 20, 0., 1.)
		self._histograms.AddTH2D("AK8Jet_doublecsv_vs_tau21", "AK8Jet_doublecsv_vs_tau21", "Double b-tag", 20, -1., 1., "#tau_{21}", 20, 0., 1.)
		self._histograms.AddTH2D("AK8Jet_tau21_vs_tau32", "AK8Jet_tau21_vs_tau32", "#tau_{21}", 20, 0., 1., "#tau_{32}", 20, 0., 1.)

		# Event selection
		self._event_selector = ROOT.EventSelector("BaconData")()
		ROOT.BaconEventCutFunctions.Configure(self._event_selector)
		cut_parameters = {}

		cut_parameters["Min_AK8Puppijet0_pt"] = ROOT.vector("double")()
		cut_parameters["Min_AK8Puppijet0_pt"].push_back(500.)
		self._event_selector.RegisterCut("Min_AK8Puppijet0_pt", ROOT.vector("TString")(), cut_parameters["Min_AK8Puppijet0_pt"])

		cut_parameters["Max_AK8Puppijet0_tau21DDT"] = ROOT.vector("double")()
		cut_parameters["Max_AK8Puppijet0_tau21DDT"].push_back(0.4)
		self._event_selector.RegisterCut("Max_AK8Puppijet0_tau21DDT", ROOT.vector("TString")(), cut_parameters["Max_AK8Puppijet0_tau21DDT"])

		cut_parameters["Min_AK8CHSjet0_doublecsv"] = ROOT.vector("double")()
		cut_parameters["Min_AK8CHSjet0_doublecsv"].push_back(0.90)
		self._event_selector.RegisterCut("Min_AK8CHSjet0_doublecsv", ROOT.vector("TString")(), cut_parameters["Min_AK8CHSjet0_doublecsv"])

		cut_parameters["Max_nmuLoose"] = ROOT.vector("double")()
		cut_parameters["Max_nmuLoose"].push_back(0)
		self._event_selector.RegisterCut("Max_nmuLoose", ROOT.vector("TString")(), cut_parameters["Max_nmuLoose"])

		cut_parameters["Max_neleLoose"] = ROOT.vector("double")()
		cut_parameters["Max_neleLoose"].push_back(0)
		self._event_selector.RegisterCut("Max_neleLoose", ROOT.vector("TString")(), cut_parameters["Max_neleLoose"])

	def run(self, max_nevents=-1, first_event=0):
		if max_nevents > 0:
			limit_nevents = min(max_nevents, self._chain.GetEntries())
		else:
			limit_nevents = self._chain.GetEntries()

		n_checkpoints = 20
		print_every = int(ceil(1. * limit_nevents / n_checkpoints))

		print "[SignalCutflow::run] INFO : Running loop over tree from event {} to {}".format(first_event, limit_nevents - 1)

		self.start_timer()
		for entry in xrange(first_event, limit_nevents):
			self.print_progress(entry, first_event, limit_nevents, print_every)
			self._processed_events += 1
			self._data.GetEntry(entry)
			event_weight = self._data.scale1fb
			self._histograms.GetTH1D("input_nevents").Fill(0)
			self._histograms.GetTH1D("input_nevents_weighted").Fill(0, event_weight)
			self._event_selector.ProcessEvent(self._data, event_weight)
			if self._event_selector.Pass():
				self._histograms.GetTH1D("pass_nevents").Fill(0)
				self._histograms.GetTH1D("pass_nevents_weighted").Fill(0, event_weight)
				self._histograms.GetTH1D("AK8Jet_msd").Fill(self._data.AK8Puppijet0_msd, event_weight)
				self._histograms.GetTH1D("AK8Jet_doublecsv").Fill(self._data.AK8CHSjet0_doublecsv, event_weight)
				self._histograms.GetTH1D("AK8Jet_tau21").Fill(self._data.AK8Puppijet0_tau21, event_weight)
				self._histograms.GetTH1D("AK8Jet_tau32").Fill(self._data.AK8Puppijet0_tau32, event_weight)
				self._histograms.GetTH2D("AK8Jet_msd_vs_doublecsv").Fill(self._data.AK8Puppijet0_msd, self._data.AK8CHSjet0_doublecsv, event_weight)
				self._histograms.GetTH2D("AK8Jet_msd_vs_tau21").Fill(self._data.AK8Puppijet0_msd, self._data.AK8Puppijet0_tau21, event_weight)
				self._histograms.GetTH2D("AK8Jet_msd_vs_tau32").Fill(self._data.AK8Puppijet0_msd, self._data.AK8Puppijet0_tau32, event_weight)
				self._histograms.GetTH2D("AK8Jet_doublecsv_vs_tau21").Fill(self._data.AK8CHSjet0_doublecsv, self._data.AK8Puppijet0_tau21, event_weight)
				self._histograms.GetTH2D("AK8Jet_tau21_vs_tau32").Fill(self._data.AK8Puppijet0_tau21, self._data.AK8Puppijet0_tau32, event_weight)

	def finish(self):
		if self._output_path == "":
			self._output_path = "/uscms/home/dryu/DAZSLE/data/EventSelection/SignalCutflow_{}.root".format(time.time)
			print "[SignalCutflow::finish] WARNING : Output path was not provided! Saving to {}".format(self._output_path)
		print "[SignalCutflow::finish] INFO : Saving histograms to {}".format(self._output_path)
		f_out = ROOT.TFile(self._output_path, "RECREATE")
		self._histograms.SaveAll(f_out)
		self._event_selector.MakeCutflowHistograms(f_out)
		self._event_selector.SaveNMinusOneHistograms(f_out)
		f_out.Close()

def MakeBasicPlots(samples, sample_output_files, legend_entries = {}):
	rebin = {
		"h_AK8Jet_msd":5,
	}
	plots_1D = ["h_AK8Jet_msd", "h_AK8Jet_doublecsv", "h_AK8Jet_tau21", "h_AK8Jet_tau32", "h_nminusone_Max_AK8Puppijet0_tau21DDT", "h_nminusone_Min_AK8CHSjet0_doublecsv"]
	plots_2D = ["h_AK8Jet_msd_vs_doublecsv","h_AK8Jet_msd_vs_tau21","h_AK8Jet_msd_vs_tau32","h_AK8Jet_doublecsv_vs_tau21","h_AK8Jet_tau21_vs_tau32"]
	for sample in samples:
		f = TFile(sample_output_files[sample], "READ")
		os.system("mkdir -pv /uscms/home/dryu/DAZSLE/data/EventSelection/figures/{}/".format(sample))
		for plot in plots_1D:
			h = f.Get(plot)
			if plot in rebin:
				h.Rebin(rebin[plot])
			c = TCanvas("c_{}_{}".format(plot.replace("h_", ""), sample), "c_{}_{}".format(plot.replace("h_", ""), sample), 800, 600)
			h.Draw()
			c.SaveAs("/uscms/home/dryu/DAZSLE/data/EventSelection/figures/{}/{}.pdf".format(sample, c.GetName()))
		for plot in plots_2D:
			h = f.Get(plot)
			c = TCanvas("c_{}_{}".format(plot.replace("h_", ""), sample), "c_{}_{}".format(plot.replace("h_", ""), sample), 800, 600)
			h.Draw("colz")
			c.SaveAs("/uscms/home/dryu/DAZSLE/data/EventSelection/figures/{}/{}.pdf".format(sample, c.GetName()))
		f.Close()

	# All 1D plots on the same canvas
	for plot in plots_1D:
		c = TCanvas("c_{}_all".format(plot.replace("h_", "")), "c_{}_all".format(plot.replace("h_", "")), 800, 600)
		c.SetRightMargin(0.2)
		l = TLegend(0.81, 0.4, 0.99, 0.9)
		l.SetFillColor(0)
		l.SetBorderSize(1)
		style_counter = 0
		for sample in samples:
			f = TFile(sample_output_files[sample], "READ")
			h = f.Get(plot)
			if plot in rebin:
				h.Rebin(rebin[plot])
			h.SetMaximum(h.GetMaximum() * 1.3)
			h.SetName(h.GetName() + "_" + sample)
			h.SetDirectory(0)
			h.SetMarkerColor(seaborn.GetColorRoot("cubehelixlarge", style_counter, len(samples)))
			h.SetMarkerStyle(20 + style_counter)
			h.SetLineColor(seaborn.GetColorRoot("cubehelixlarge", style_counter, len(samples)))
			if style_counter == 0:
				if plot == "h_AK8Jet_msd":
					h.GetXaxis().SetRangeUser(0., 600.)
				h.Draw("hist")
			h.Draw("hist same")
			h.Draw("pe same")
			if sample in legend_entries:
				l.AddEntry(h, legend_entries[sample], "pl")
			else:
				l.AddEntry(h, sample, "pl")
			style_counter += 1
		l.Draw()
		c.SaveAs("/uscms/home/dryu/DAZSLE/data/EventSelection/figures/{}.pdf".format(c.GetName()))
		c.SetLogy()
		c.SaveAs("/uscms/home/dryu/DAZSLE/data/EventSelection/figures/{}_log.pdf".format(c.GetName()))

def MakeCutflowPlot(samples, histograms, save_tag, legend_entries={}):
	c = TCanvas("c_{}".format(save_tag), "c_{}".format(save_tag), 800, 700)
	c.SetBottomMargin(0.2)
	l = TLegend(0.65, 0.55, 0.85, 0.85)
	l.SetFillColor(0)
	l.SetBorderSize(0)

	frame_cutflow = TH1F("frame_cutflow", "frame_cutflow", histograms[samples[0]].GetNbinsX(), histograms[samples[0]].GetXaxis().GetXmin(), histograms[samples[0]].GetXaxis().GetXmax())
	for bin in xrange(1, histograms[samples[0]].GetNbinsX() + 1):
		frame_cutflow.GetXaxis().SetBinLabel(bin, histograms[samples[0]].GetXaxis().GetBinLabel(bin))
	frame_cutflow.GetXaxis().SetNdivisions(frame_cutflow.GetXaxis().GetNbins(), 0, 0, False)
	frame_cutflow.GetYaxis().SetTitle("Fraction of events remaining")
	frame_cutflow.SetMaximum(1.1)
	frame_cutflow.Draw()

	style_counter = 0
	for sample in samples:
		histograms[sample].SetLineColor(seaborn.GetColorRoot("cubehelixlarge", style_counter, len(samples)))
		histograms[sample].SetLineWidth(2)
		histograms[sample].SetLineStyle(1)
		histograms[sample].Draw("hist same")
		if sample in legend_entries:
			l.AddEntry(histograms[sample], legend_entries[sample], "l")
		else:
			l.AddEntry(histograms[sample], sample, "l")
		style_counter += 1
	l.Draw()
	c.SaveAs("/uscms/home/dryu/DAZSLE/data/EventSelection/figures/{}.pdf".format(c.GetName()))

# Histograms = CSV N-1 histograms
def MakeCSVEfficiencyPlot(samples, histograms, save_tag, legend_entries={}):
	c = TCanvas("c_{}".format(save_tag), "c_{}".format(save_tag), 800, 600)
	l = TLegend(0.65, 0.55, 0.85, 0.85)
	l.SetFillColor(0)
	l.SetBorderSize(0)

	frame_csv = TH1F("frame_csv", "frame_csv", 100, histograms[samples[0]].GetXaxis().GetXmin(), histograms[samples[0]].GetXaxis().GetXmax())
	frame_csv.GetXaxis().SetTitle("Double b-tag cut")
	frame_csv.GetYaxis().SetTitle("Efficiency")
	frame_csv.SetMaximum(1.1)
	frame_csv.Draw("axis")

	efficiency_tgraphs = {}
	style_counter = 0
	for sample in samples:
		total_events = histograms[sample].Integral(0, histograms[sample].GetNbinsX() + 1)
		efficiency_tgraphs[sample] = TGraphErrors(histograms[sample].GetNbinsX())
		efficiency_tgraphs[sample].SetName("csv_efficiency_{}".format(sample))
		for bin in xrange(1, histograms[sample].GetNbinsX() + 1):
			pass_events = histograms[sample].Integral(bin, histograms[sample].GetNbinsX() + 1)
			efficiency = 1. * pass_events / total_events
			defficiency = max(sqrt(efficiency * (1. - efficiency) / total_events), 1./total_events)
			efficiency_tgraphs[sample].SetPoint(bin-1, histograms[sample].GetXaxis().GetBinLowEdge(bin), efficiency)
			efficiency_tgraphs[sample].SetPointError(bin-1, 0., defficiency)
		efficiency_tgraphs[sample].SetMarkerStyle(20+style_counter)
		efficiency_tgraphs[sample].SetMarkerSize(1)
		efficiency_tgraphs[sample].SetMarkerColor(seaborn.GetColorRoot("cubehelixlarge", style_counter, len(samples)))
		efficiency_tgraphs[sample].SetLineStyle(1)
		efficiency_tgraphs[sample].SetLineWidth(1)
		efficiency_tgraphs[sample].SetLineColor(seaborn.GetColorRoot("cubehelixlarge", style_counter, len(samples)))
		efficiency_tgraphs[sample].Draw("pl")
		if sample in legend_entries:
			l.AddEntry(efficiency_tgraphs[sample], legend_entries[sample], "pl")
		else:
			l.AddEntry(efficiency_tgraphs[sample], sample, "pl")
		style_counter += 1
	l.Draw()
	c.SaveAs("/uscms/home/dryu/DAZSLE/data/EventSelection/figures/{}.pdf".format(c.GetName()))

if __name__ == "__main__":
	import argparse
	parser = argparse.ArgumentParser(description='Produce and plot ieta-iphi histograms to look for buggy events')
	parser.add_argument('--samples', type=str, help="Sample name")
	parser.add_argument('--run', action="store_true", help="Run cutflow")
	parser.add_argument('--basic_plots', action="store_true", help="Plot all basic distributions")
	parser.add_argument('--cutflow_plot', action="store_true", help="Make cutflow plot")
	parser.add_argument('--csv_plot', action="store_true", help="Make CSV plot")
	args = parser.parse_args()

	if args.samples == "all":
		samples = ["scalar_50", "scalar_75", "scalar_100", "scalar_125", "scalar_150", "scalar_250", "scalar_300", "scalar_400", "scalar_500"]
	else:
		samples = args.samples.split(",")

	sample_files = {
		"scalar_50":["root://cmsxrootd.fnal.gov//store/user/jduarte1/zprimebits-v11.061/sklim-v0-Nov29/DMSpin0_ggPhibb1j_50_1000pb_weighted.root"],
		"scalar_75":["root://cmsxrootd.fnal.gov//store/user/jduarte1/zprimebits-v11.061/sklim-v0-Nov29/DMSpin0_ggPhibb1j_75_1000pb_weighted.root"],
		"scalar_100":["root://cmsxrootd.fnal.gov//store/user/jduarte1/zprimebits-v11.061/sklim-v0-Nov29/DMSpin0_ggPhibb1j_100_1000pb_weighted.root"],
		"scalar_125":["root://cmsxrootd.fnal.gov//store/user/jduarte1/zprimebits-v11.061/sklim-v0-Nov29/DMSpin0_ggPhibb1j_125_1000pb_weighted.root"],
		"scalar_150":["root://cmsxrootd.fnal.gov//store/user/jduarte1/zprimebits-v11.061/sklim-v0-Nov29/DMSpin0_ggPhibb1j_150_1000pb_weighted.root"],
		"scalar_250":["root://cmsxrootd.fnal.gov//store/user/jduarte1/zprimebits-v11.061/sklim-v0-Nov29/DMSpin0_ggPhibb1j_250_1000pb_weighted.root"],
		"scalar_300":["root://cmsxrootd.fnal.gov//store/user/jduarte1/zprimebits-v11.061/sklim-v0-Nov29/DMSpin0_ggPhibb1j_300_1000pb_weighted.root"],
		"scalar_400":["root://cmsxrootd.fnal.gov//store/user/jduarte1/zprimebits-v11.061/sklim-v0-Nov29/DMSpin0_ggPhibb1j_400_1000pb_weighted.root"],
		"scalar_500":["root://cmsxrootd.fnal.gov//store/user/jduarte1/zprimebits-v11.061/sklim-v0-Nov29/DMSpin0_ggPhibb1j_500_1000pb_weighted.root"],
	}

	sample_legend_entries = {
		"scalar_50":"m_{#Phi}=50 GeV",
		"scalar_75":"m_{#Phi}=75 GeV",
		"scalar_100":"m_{#Phi}=100 GeV",
		"scalar_125":"m_{#Phi}=125 GeV",
		"scalar_150":"m_{#Phi}=150 GeV",
		"scalar_250":"m_{#Phi}=250 GeV",
		"scalar_300":"m_{#Phi}=300 GeV",
		"scalar_400":"m_{#Phi}=400 GeV",
		"scalar_500":"m_{#Phi}=500 GeV",
	}

	result_files = {
		"scalar_50":"/uscms/home/dryu/DAZSLE/data/EventSelection/SignalCutflows_scalar_50.root",
		"scalar_75":"/uscms/home/dryu/DAZSLE/data/EventSelection/SignalCutflows_scalar_75.root",
		"scalar_100":"/uscms/home/dryu/DAZSLE/data/EventSelection/SignalCutflows_scalar_100.root",
		"scalar_125":"/uscms/home/dryu/DAZSLE/data/EventSelection/SignalCutflows_scalar_125.root",
		"scalar_150":"/uscms/home/dryu/DAZSLE/data/EventSelection/SignalCutflows_scalar_150.root",
		"scalar_250":"/uscms/home/dryu/DAZSLE/data/EventSelection/SignalCutflows_scalar_250.root",
		"scalar_300":"/uscms/home/dryu/DAZSLE/data/EventSelection/SignalCutflows_scalar_300.root",
		"scalar_400":"/uscms/home/dryu/DAZSLE/data/EventSelection/SignalCutflows_scalar_400.root",
		"scalar_500":"/uscms/home/dryu/DAZSLE/data/EventSelection/SignalCutflows_scalar_500.root",
	}

	if args.run:
		for sample in samples:
			cutflow = SignalCutflow()
			for sample_file in sample_files[sample]:
				cutflow.add_file(sample_file)
			cutflow.start()
			cutflow.run()
			cutflow.set_output_path(result_files[sample])
			cutflow.finish()
	if args.basic_plots:
		MakeBasicPlots(samples, result_files, legend_entries=sample_legend_entries)
	if args.cutflow_plot:
		histograms = {}
		for sample in samples:
			f = TFile(result_files[sample], "READ")
			h = f.Get("CutFlowCounter_BaconEventSelector")
			h.SetDirectory(0)
			h.SetName("Cutflow_{}".format(sample))
			if h.GetBinContent(1) > 0:
				h.Scale(1. / h.GetBinContent(1))
			else:
				h.Scale(0.)
			histograms[sample] = h
			f.Close()
		MakeCutflowPlot(samples, histograms, "Phibb_cutflow_comparison", legend_entries=sample_legend_entries)
	if args.csv_plot:
		csv_histograms = {}
		for sample in samples:
			f = TFile(result_files[sample], "READ")
			h = f.Get("h_nminusone_Min_AK8CHSjet0_doublecsv")
			h.SetDirectory(0)
			h.SetName("h_nminusone_Min_AK8CHSjet0_doublecsv_{}".format(sample))
			csv_histograms[sample] = h
			f.Close()
		MakeCSVEfficiencyPlot(samples, csv_histograms, "Phibb_csv_efficiencies", legend_entries=sample_legend_entries)
