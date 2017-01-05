import os
import sys
import ROOT
from DAZSLE.ZPrimePlusJet.analysis_base import AnalysisBase
import DAZSLE.ZPrimePlusJet.analysis_configuration as config
from math import ceil, sqrt

import ROOT
from ROOT import *
gInterpreter.Declare("#include \"MyTools/RootUtils/interface/SeabornInterface.h\"")
gInterpreter.Declare("#include \"MyTools/RootUtils/interface/HistogramManager.h\"")
gSystem.Load(os.path.expandvars("$CMSSW_BASE/lib/slc6_amd64_gcc530/libMyToolsRootUtils.so"))
gInterpreter.Declare("#include \"MyTools/AnalysisTools/interface/EventSelector.h\"")
gSystem.Load(os.path.expandvars("$CMSSW_BASE/lib/slc6_amd64_gcc530/libMyToolsAnalysisTools.so"))
gSystem.Load(os.path.expandvars("$CMSSW_BASE/lib/slc6_amd64_gcc530/libDAZSLEZPrimePlusJet.so"))
#from ROOT import gInterpreter, gSystem, gROOT, gStyle, Root, TCanvas, TLegend, TH1F, TFile, TGraphErrors
gROOT.SetBatch(ROOT.kTRUE);
gStyle.SetOptStat(0)
gStyle.SetOptTitle(0)
seaborn = Root.SeabornInterface()
seaborn.Initialize()

class LimitHistograms(AnalysisBase):
	def __init__(self, label, tree_name="otree"):
		super(LimitHistograms, self).__init__(tree_name=tree_name)
		self._output_path = ""
		self._label = label

	def set_output_path(self, output_path):
		self._output_path = output_path

	def start(self):
		self._processed_events = 0

		# Histograms
		self._histograms = ROOT.Root.HistogramManager()
		self._histograms.AddPrefix("h_")
		self._pass_histogram_name = "{}_pass_ak8".format(self._label)
		self._histograms.AddTH2F(self._pass_histogram_name, "; AK8 m_{SD}^{PUPPI} (GeV); AK8 p_{T} (GeV)", "m_{SD}^{PUPPI} [GeV]", 75, 0, 500, "p_{T} [GeV]", 5, 500, 1000)
		self._fail_histogram_name = "{}_fail_ak8".format(self._label)
		self._histograms.AddTH2F(self._fail_histogram_name, "; AK8 m_{SD}^{PUPPI} (GeV); AK8 p_{T} (GeV)", "m_{SD}^{PUPPI} [GeV]", 75, 0, 500, "p_{T} [GeV]", 5, 500, 1000)
		self._histograms.AddTH1D("input_nevents", "input_nevents", "", 1, -0.5, 0.5)
		self._histograms.AddTH1D("input_nevents_weighted", "input_nevents_weighted", "", 1, -0.5, 0.5)
		self._histograms.AddTH1D("pass_nevents", "pass_nevents", "", 1, -0.5, 0.5)
		self._histograms.AddTH1D("pass_nevents_weighted", "pass_nevents_weighted", "", 1, -0.5, 0.5)
		self._histograms.AddTH2D("pt_dcsv", "pt_dcsv", "p_{T} [GeV]", 200, 0., 2000., "Double b-tag", 20, -1., 1.)

		# Event selection
		self._event_selector = ROOT.EventSelector("BaconData")()
		ROOT.BaconEventCutFunctions.Configure(self._event_selector)
		cut_parameters = {}

		cut_parameters["Max_AK8Puppijet0_tau21DDT"] = ROOT.vector("double")()
		cut_parameters["Max_AK8Puppijet0_tau21DDT"].push_back(0.4)
		self._event_selector.RegisterCut("Max_AK8Puppijet0_tau21DDT", ROOT.vector("TString")(), cut_parameters["Max_AK8Puppijet0_tau21DDT"])

		#cut_parameters["Min_AK8CHSjet0_doublecsv"] = ROOT.vector("double")()
		#cut_parameters["Min_AK8CHSjet0_doublecsv"].push_back(0.90)
		#self._event_selector.RegisterCut("Min_AK8CHSjet0_doublecsv", ROOT.vector("TString")(), cut_parameters["Min_AK8CHSjet0_doublecsv"])

		cut_parameters["Max_neleLoose"] = ROOT.vector("double")()
		cut_parameters["Max_neleLoose"].push_back(0)
		self._event_selector.RegisterCut("Max_neleLoose", ROOT.vector("TString")(), cut_parameters["Max_neleLoose"])

		cut_parameters["Max_nmuLoose"] = ROOT.vector("double")()
		cut_parameters["Max_nmuLoose"].push_back(0)
		self._event_selector.RegisterCut("Max_nmuLoose", ROOT.vector("TString")(), cut_parameters["Max_nmuLoose"])

		cut_parameters["Max_ntau"] = ROOT.vector("double")()
		cut_parameters["Max_ntau"].push_back(0)
		self._event_selector.RegisterCut("Max_ntau", ROOT.vector("TString")(), cut_parameters["Max_ntau"])

		cut_parameters["Max_nphoLoose"] = ROOT.vector("double")()
		cut_parameters["Max_nphoLoose"].push_back(0)
		self._event_selector.RegisterCut("Max_nphoLoose", ROOT.vector("TString")(), cut_parameters["Max_nphoLoose"])

		cut_parameters["AK8Puppijet0_isTightVJet"] = ROOT.vector("double")()
		self._event_selector.RegisterCut("AK8Puppijet0_isTightVJet", ROOT.vector("TString")(), cut_parameters["AK8Puppijet0_isTightVJet"])

		cut_parameters["Max_pfmet"] = ROOT.vector("double")()
		cut_parameters["Max_pfmet"].push_back(180.)
		self._event_selector.RegisterCut("Max_pfmet", ROOT.vector("TString")(), cut_parameters["Max_pfmet"])

		cut_parameters["Max_nAK4PuppijetsdR08"] = ROOT.vector("double")()
		cut_parameters["Max_nAK4PuppijetsdR08"].push_back(4)
		self._event_selector.RegisterCut("Max_nAK4PuppijetsdR08", ROOT.vector("TString")(), cut_parameters["Max_nAK4PuppijetsdR08"])

		cut_parameters["Max_nAK4PuppijetsTdR08"] = ROOT.vector("double")()
		cut_parameters["Max_nAK4PuppijetsTdR08"].push_back(2)
		self._event_selector.RegisterCut("Max_nAK4PuppijetsTdR08", ROOT.vector("TString")(), cut_parameters["Max_nAK4PuppijetsTdR08"])

	def run(self, max_nevents=-1, first_event=0):
		if max_nevents > 0:
			limit_nevents = min(max_nevents, self._chain.GetEntries())
		else:
			limit_nevents = self._chain.GetEntries()

		n_checkpoints = 20
		print_every = int(ceil(1. * limit_nevents / n_checkpoints))

		print "[LimitHistograms::run] INFO : Running loop over tree from event {} to {}".format(first_event, limit_nevents - 1)

		self.start_timer()
		for entry in xrange(first_event, limit_nevents):
			self.print_progress(entry, first_event, limit_nevents, print_every)
			self._processed_events += 1
			self._data.GetEntry(entry)
			event_weight = self._data.puWeight # No luminosity weight here. Apply this as a weight to the output histograms later.
			self._histograms.GetTH1D("input_nevents").Fill(0)
			self._histograms.GetTH1D("input_nevents_weighted").Fill(0, event_weight)

			self._event_selector.ProcessEvent(self._data, event_weight)
			if self._event_selector.Pass():
				self._histograms.GetTH1D("pass_nevents").Fill(0)
				self._histograms.GetTH1D("pass_nevents_weighted").Fill(0, event_weight)
				self._histograms.GetTH2D("pt_dcsv").Fill(self._data.AK8Puppijet0_pt, self._data.AK8CHSjet0_doublecsv, event_weight)
				if self._data.AK8Puppijet0_pt > 500.:
					if self._data.AK8CHSjet0_doublecsv > 0.9:
						self._histograms.GetTH2F(self._pass_histogram_name).Fill(self._data.AK8Puppijet0_msd, self._data.AK8Puppijet0_pt, event_weight)
					else:
						self._histograms.GetTH2F(self._fail_histogram_name).Fill(self._data.AK8Puppijet0_msd, self._data.AK8Puppijet0_pt, event_weight)

	def finish(self):
		if self._output_path == "":
			self._output_path = "/uscms/home/dryu/DAZSLE/data/LimitSetting/InputHistograms_{}.root".format(time.time)
			print "[SignalCutflow::finish] WARNING : Output path was not provided! Saving to {}".format(self._output_path)
		print "[SignalCutflow::finish] INFO : Saving histograms to {}".format(self._output_path)
		f_out = ROOT.TFile(self._output_path, "RECREATE")
		self._histograms.SaveAll(f_out)
		self._event_selector.MakeCutflowHistograms(f_out)
		self._event_selector.SaveNMinusOneHistograms(f_out)
		f_out.Close()

if __name__ == "__main__":
	import argparse
	parser = argparse.ArgumentParser(description='Produce and plot ieta-iphi histograms to look for buggy events')
	parser.add_argument('--samples', type=str, help="Sample name(s), comma separated")
	parser.add_argument('--files', type=str, help="Input file name(s), comma separated")
	parser.add_argument('--run', action="store_true", help="Run")
	parser.add_argument('--condor_run', action="store_true", help="Run on condor")
	parser.add_argument('--output_folder', type=str, help="Output folder")
	args = parser.parse_args()

	if args.samples != None and args.files != None:
		print "[setup_limits] ERROR : Cannot specify args.samples and args.files at the same time."
		sys.exit(1)

	if args.samples:
		if args.samples == "all":
			samples = config.samples
		else:
			samples = args.samples.split(",")
		files = []
		for sample in samples:
			files.extend(config.skims[sample])
	elif args.files:
		files = args.files.split(",")

	if args.run:
		for filename in files:
			label = os.path.basename(filename).replace(".root", "")
			limit_histogrammer = LimitHistograms(label, tree_name="Events")
			if args.output_folder:
				limit_histogrammer.set_output_path("{}/InputHistograms_{}.root".format(args.output_folder, label))
			else:
				limit_histogrammer.set_output_path("/uscms/home/dryu/DAZSLE/data/LimitSetting/InputHistograms_{}.root".format(label))
			limit_histogrammer.add_file(filename)
			limit_histogrammer.start()
			limit_histogrammer.run()
			limit_histogrammer.finish()
	if args.condor_run:
		import time
		for sample in samples:
			start_directory = os.getcwd()
			job_tag = "job_{}_{}".format(sample, time.time())
			submission_directory = "/uscms/home/dryu/DAZSLE/data/LimitSetting/condor/{}".format(job_tag)
			os.system("mkdir -pv {}".format(submission_directory))
			os.chdir(submission_directory)
			job_script = open("run.sh".format(submission_directory), 'w')
			job_script.write("#!/bin/bash\n")
			job_script.write("python $CMSSW_BASE/src/DAZSLE/ZPrimePlusJet/fitting/setup_limits.py --files {} --output_folder . --run\n".format(",".join([os.path.basename(x) for x in config.skims[sample]])))
			job_script.close()
			submission_command = "csub run.sh --cmssw -F {}".format(",".join(config.skims[sample]))
			print submission_command
			os.system(submission_command)
			os.chdir(start_directory)