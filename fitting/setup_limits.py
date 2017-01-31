import os
import sys
import ROOT
from DAZSLE.ZPrimePlusJet.analysis_base import AnalysisBase
import DAZSLE.ZPrimePlusJet.analysis_configuration as config
from math import ceil, sqrt,floor
import array

import ROOT
from ROOT import *
gInterpreter.Declare("#include \"MyTools/RootUtils/interface/SeabornInterface.h\"")
gInterpreter.Declare("#include \"MyTools/RootUtils/interface/HistogramManager.h\"")
gSystem.Load(os.path.expandvars("$CMSSW_BASE/lib/$SCRAM_ARCH/libMyToolsRootUtils.so"))
gInterpreter.Declare("#include \"MyTools/AnalysisTools/interface/EventSelector.h\"")
gSystem.Load(os.path.expandvars("$CMSSW_BASE/lib/$SCRAM_ARCH/libMyToolsAnalysisTools.so"))
gSystem.Load(os.path.expandvars("$CMSSW_BASE/lib/$SCRAM_ARCH/libDAZSLEZPrimePlusJet.so"))
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
		self._input_nevents = 0
		self._tau21_ddt_cut = 0.4
		self._dcsv_cut = 0.9
		self._jet_type = "AK8"

	def set_cut(self, cut_name, cut_value):
		if cut_name == "tau21_ddt":
			self._tau21_ddt_cut = cut_value
		elif cut_name == "dcsv":
			self._dcsv_cut = cut_value
		else:
			print "[LimitHistograms::set_cut] ERROR : Unknown cut {}. Exiting.".format(cut_name)
			sys.exit(1)

	def set_jet_type(self, jet_type):
		if jet_type != "AK8" and jet_type != "CA15":
			print "[LimitHistograms::set_jet_type] ERROR : Unknown jet type {}. Exiting.".format(jet_type)
			sys.exit(1)
		self._jet_type = jet_type 

	# Overload add_file to extract the number of input events to the skims, stored in histogram NEvents in the same file as the trees
	def add_file(self, filename):
		super(LimitHistograms, self).add_file(filename)
		f = ROOT.TFile.Open(filename, "READ")
		self._input_nevents += f.Get("NEvents").Integral()
		f.Close()

	def set_output_path(self, output_path):
		self._output_path = output_path
		os.system("mkdir -pv {}".format(os.path.dirname(self._output_path)))

	def start(self):
		self._processed_events = 0

		# Histograms
		self._pt_bins = array.array("d", [500.,550.,600.,675.,800.,1000.])

		self._histograms = ROOT.Root.HistogramManager()
		self._histograms.AddPrefix("h_")
		self._histograms.AddTH1F("input_nevents", "input_nevents", "", 1, -0.5, 0.5)
		self._histograms.GetTH1F("input_nevents").SetBinContent(1, self._input_nevents)
		self._histograms.AddTH2F("pass_ak8", "; AK8 m_{SD}^{PUPPI} (GeV); AK8 p_{T} (GeV)", "m_{SD}^{PUPPI} [GeV]", 52, 40, 404, "p_{T} [GeV]", len(self._pt_bins) - 1, self._pt_bins)
		self._histograms.AddTH2F("fail_ak8", "; AK8 m_{SD}^{PUPPI} (GeV); AK8 p_{T} (GeV)", "m_{SD}^{PUPPI} [GeV]", 52, 40, 404, "p_{T} [GeV]", len(self._pt_bins) - 1, self._pt_bins)
		self._histograms.AddTH1D("processed_nevents", "processed_nevents", "", 1, -0.5, 0.5)
		self._histograms.AddTH1D("processed_nevents_weighted", "processed_nevents_weighted", "", 1, -0.5, 0.5)
		self._histograms.AddTH1D("pass_nevents", "pass_nevents", "", 1, -0.5, 0.5)
		self._histograms.AddTH1D("pass_nevents_weighted", "pass_nevents_weighted", "", 1, -0.5, 0.5)
		self._histograms.AddTH2D("pt_dcsv", "pt_dcsv", "p_{T} [GeV]", 200, 0., 2000., "Double b-tag", 20, -1., 1.)

		# Event selection
		self._event_selector = ROOT.EventSelector("BaconData")()
		ROOT.BaconEventCutFunctions.Configure(self._event_selector)
		cut_parameters = {}

		# General event cuts, independent of jet type
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

		cut_parameters["Max_pfmet"] = ROOT.vector("double")()
		cut_parameters["Max_pfmet"].push_back(180.)
		self._event_selector.RegisterCut("Max_pfmet", ROOT.vector("TString")(), cut_parameters["Max_pfmet"])

		# AK8 or CA15 cuts
		if self._jet_type == "AK8":
			cut_parameters["Max_AK8Puppijet0_tau21DDT"] = ROOT.vector("double")()
			cut_parameters["Max_AK8Puppijet0_tau21DDT"].push_back(self._tau21_ddt_cut)
			self._event_selector.RegisterCut("Max_AK8Puppijet0_tau21DDT", ROOT.vector("TString")(), cut_parameters["Max_AK8Puppijet0_tau21DDT"])

			cut_parameters["AK8Puppijet0_isTightVJet"] = ROOT.vector("double")()
			self._event_selector.RegisterCut("AK8Puppijet0_isTightVJet", ROOT.vector("TString")(), cut_parameters["AK8Puppijet0_isTightVJet"])

			#cut_parameters["Min_AK8CHSjet0_doublecsv"] = ROOT.vector("double")()
			#cut_parameters["Min_AK8CHSjet0_doublecsv"].push_back(0.90)
			#self._event_selector.RegisterCut("Min_AK8CHSjet0_doublecsv", ROOT.vector("TString")(), cut_parameters["Min_AK8CHSjet0_doublecsv"])


			cut_parameters["Max_nAK4PuppijetsdR08"] = ROOT.vector("double")()
			cut_parameters["Max_nAK4PuppijetsdR08"].push_back(4)
			self._event_selector.RegisterCut("Max_nAK4PuppijetsdR08", ROOT.vector("TString")(), cut_parameters["Max_nAK4PuppijetsdR08"])

			cut_parameters["Max_nAK4PuppijetsTdR08"] = ROOT.vector("double")()
			cut_parameters["Max_nAK4PuppijetsTdR08"].push_back(2)
			self._event_selector.RegisterCut("Max_nAK4PuppijetsTdR08", ROOT.vector("TString")(), cut_parameters["Max_nAK4PuppijetsTdR08"])

		elif self._jet_type == "CA15":
			cut_parameters["Max_CA15Puppijet0_tau21DDT"] = ROOT.vector("double")()
			cut_parameters["Max_CA15Puppijet0_tau21DDT"].push_back(self._tau21_ddt_cut)
			self._event_selector.RegisterCut("Max_CA15Puppijet0_tau21DDT", ROOT.vector("TString")(), cut_parameters["Max_CA15Puppijet0_tau21DDT"])

			cut_parameters["CA15Puppijet0_isTightVJet"] = ROOT.vector("double")()
			self._event_selector.RegisterCut("CA15Puppijet0_isTightVJet", ROOT.vector("TString")(), cut_parameters["CA15Puppijet0_isTightVJet"])

			# Cuts on nearby jets: calculated w.r.t. the AK8 jet. Need to calculate w.r.t. CA15... ask the group to add to BaconTuple?
			#cut_parameters["Max_nAK4PuppijetsdR08"] = ROOT.vector("double")()
			#cut_parameters["Max_nAK4PuppijetsdR08"].push_back(4)
			#self._event_selector.RegisterCut("Max_nAK4PuppijetsdR08", ROOT.vector("TString")(), cut_parameters["Max_nAK4PuppijetsdR08"])

			#cut_parameters["Max_nAK4PuppijetsTdR08"] = ROOT.vector("double")()
			#cut_parameters["Max_nAK4PuppijetsTdR08"].push_back(2)
			#self._event_selector.RegisterCut("Max_nAK4PuppijetsTdR08", ROOT.vector("TString")(), cut_parameters["Max_nAK4PuppijetsTdR08"])


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
			self._histograms.GetTH1D("processed_nevents").Fill(0)
			self._histograms.GetTH1D("processed_nevents_weighted").Fill(0, event_weight)

			self._event_selector.ProcessEvent(self._data, event_weight)
			if self._event_selector.Pass():
				self._histograms.GetTH1D("pass_nevents").Fill(0)
				self._histograms.GetTH1D("pass_nevents_weighted").Fill(0, event_weight)
				self._histograms.GetTH2D("pt_dcsv").Fill(self._data.AK8Puppijet0_pt, self._data.AK8CHSjet0_doublecsv, event_weight)
				if self._data.AK8Puppijet0_pt > 500.:
					if self._data.AK8CHSjet0_doublecsv > self._dcsv_cut:
						self._histograms.GetTH2F("pass_ak8").Fill(self._data.AK8Puppijet0_msd, self._data.AK8Puppijet0_pt, event_weight)
					else:
						self._histograms.GetTH2F("fail_ak8").Fill(self._data.AK8Puppijet0_msd, self._data.AK8Puppijet0_pt, event_weight)

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

# Not using this right now! It was intended for joblib parallel processing, but you weren't able to figure out joblib on condor. 
#def RunSingleFile(args, samples, filename, label="", tree_name="Events"):
#	print "Input file {}".format(filename)
#	limit_histogrammer = LimitHistograms(label, tree_name=tree_name)
#	if args.output_folder:
#		limit_histogrammer.set_output_path("{}/InputHistograms_{}.root".format(args.output_folder, label))
#	else:
#		limit_histogrammer.set_output_path("/uscms/home/dryu/DAZSLE/data/LimitSetting/InputHistograms_{}.root".format(label))
#	limit_histogrammer.add_file(filename)
#	limit_histogrammer.start()
#	limit_histogrammer.run()
#	limit_histogrammer.finish()

if __name__ == "__main__":
	import argparse
	parser = argparse.ArgumentParser(description='Produce and plot ieta-iphi histograms to look for buggy events')
	input_group = parser.add_mutually_exclusive_group() 
	input_group.add_argument('--all', action="store_true", help="Run over all supersamples")
	input_group.add_argument('--supersamples', type=str, help="Supersample name(s), comma separated. Must correspond to something in analysis_configuration.(background_names, signal_names, or data_names).")
	input_group.add_argument('--samples', type=str, help="Sample name(s), comma separated. Must be a key in analysis_configuration.skims.")
	input_group.add_argument('--files', type=str, help="Input file name(s), comma separated")
	input_group.add_argument('--n_jobs', type=int, default=4, help="For --run, specify the number of parallel jobs.")
	action_group = parser.add_mutually_exclusive_group() 
	action_group.add_argument('--combine_outputs', action="store_true", help="Compile results into one file for next step (buildRhalphabet). Also applies luminosity weights to MC.")
	action_group.add_argument('--run', action="store_true", help="Run")
	action_group.add_argument('--condor_run', action="store_true", help="Run on condor")
	action_group.add_argument('--rhalphabet', action="store_true", help="Run rhalpabet and create workspaces for combine")
	action_group.add_argument('--datacards', action="store_true", help="Create datacards for combine")
	parser.add_argument('--output_folder', type=str, help="Output folder")
	parser.add_argument('--label', type=str, help="If running with --files, need to specify a label manually, in lieu of the sample names, for the output file naming.")
	parser.add_argument('--luminosity', type=float, default=34207, help="Luminosity in pb^-1")
	args = parser.parse_args()

	# Make a list of input samples and files
	samples = []
	sample_files = {} # Dictionary is sample : [list of files in sample]
	if args.all:
		supersamples = config.supersamples
		samples = [] 
		for supersample in supersamples:
			samples.extend(config.samples[supersample])
			for sample in config.samples[supersample]:
				sample_files[sample] = config.skims[sample]
	elif args.supersamples:
		supersamples = args.supersamples.split(",")
		samples = [] 
		for supersample in supersamples:
			samples.extend(config.samples[supersample])
			for sample in config.samples[supersample]:
				sample_files[sample] = config.skims[sample]
	elif args.samples:
		samples = args.samples.split(",")
		for sample in samples:
			sample_files[sample] = config.skims[sample]
	elif args.files:
		files = args.files.split(",")
		for filename in files:
			if args.label:
				this_sample = args.label
			else:
				this_sample = "UnknownSample"
			if not this_sample in sample_files:
				sample_files[this_sample] = []
			sample_files[this_sample].append(filename)
		samples = sample_files.keys()
	print "List of input samples: ",
	print samples
	#print "List of sample => input files:",
	#print sample_files


	if args.run:
		#from joblib import Parallel
		#from joblib import delayed
		for sample in samples:
			print "\n *** Running sample {}".format(sample)
			limit_histogrammer = LimitHistograms(sample, tree_name="Events")
			if args.output_folder:
				limit_histogrammer.set_output_path("{}/InputHistograms_{}.root".format(args.output_folder, sample))
			else:
				limit_histogrammer.set_output_path("/uscms/home/dryu/DAZSLE/data/LimitSetting/InputHistograms_{}.root".format(sample))
			for filename in sample_files[sample]:
				print "Input file {}".format(filename)
				limit_histogrammer.add_file(filename)
			limit_histogrammer.start()
			limit_histogrammer.run()
			limit_histogrammer.finish()
			#subjob_index = 0
			#for subjob_index, filename in enumerate(sample_files[sample]):
			#	RunSingleFile(args, samples, filename, label=sample)
			# joblib doesn't work on condor! Yet.
			#if len(sample_files[sample]) >= 2:
			#	Parallel(n_jobs=4)(
			#		delayed(RunSingleFile)(
			#			args, 
			#			samples, 
			#			sample_files[sample][i], 
			#			label="{}_subjob{}".format(sample, i)
			#		) for i in xrange(len(sample_files[sample]))
			#	)
			#else:
			#	RunSingleFile(args, samples, sample_files[sample][0], label=sample)

	if args.condor_run:
		import time
		hadd_scripts = []
		for sample in samples:
			start_directory = os.getcwd()
			job_tag = "job_{}_{}".format(sample, int(floor(time.time())))
			submission_directory = "/uscms/home/dryu/DAZSLE/data/LimitSetting/condor/{}".format(job_tag)
			os.system("mkdir -pv {}".format(submission_directory))
			os.chdir(submission_directory)

			files_per_job = 1
			if "JetHTRun2016" in sample:
				files_per_job = 10
			elif "QCD" in sample:
				files_per_job = 3

			csubjob_index = 0
			this_job_input_files = []
			input_files_to_transfer = []
			for file_counter, filename in enumerate(sample_files[sample], start=1):
				print file_counter, filename
				if "root://" in filename:
					this_job_input_files.append(filename)
				else:
					input_files_to_transfer.append(filename)
					this_job_input_files.append(os.path.basename(filename))
				
				if file_counter % files_per_job == 0 or file_counter == len(sample_files[sample]):
					print "\nSubmitting jobs now."
					print "\t input_files_to_transfer = ",
					print input_files_to_transfer
					job_script_path = "{}/run_csubjob{}.sh".format(submission_directory, csubjob_index)
					job_script = open(job_script_path, 'w')
					job_script.write("#!/bin/bash\n")
					job_script.write("python $CMSSW_BASE/src/DAZSLE/ZPrimePlusJet/fitting/setup_limits.py --files {} --label {}_csubjob{} --output_folder . --run 2>&1\n".format(",".join(this_job_input_files), sample, csubjob_index))
					job_script.close()
					submission_command = "csub {} --cmssw --no_retar".format(job_script_path)
					if len(input_files_to_transfer) >= 1:
						submission_command += " -F " + ",".join(input_files_to_transfer)
					print submission_command
					os.system(submission_command)
					this_job_input_files = []
					input_files_to_transfer = []
					csubjob_index += 1
			hadd_scripts.append("{}/hadd.sh".format(submission_directory))
			hadd_script = open("{}/hadd.sh".format(submission_directory), "w")
			hadd_script.write("#!/bin/bash\n")
			hadd_script.write("hadd /uscms/home/dryu/DAZSLE/data/LimitSetting/InputHistograms_{}.root {}/InputHistograms*csubjob*root\n".format(sample, submission_directory))
			hadd_script.close()
			os.chdir(start_directory)
		# One hadd script to rule them all
		master_hadd_script_path = "/uscms/home/dryu/DAZSLE/data/LimitSetting/condor/master_hadd"
		if not args.all:
			master_hadd_script_path += "_" + str(int(floor(time.time())))
		master_hadd_script_path += ".sh"
		master_hadd_script = open(master_hadd_script_path, "w")
		master_hadd_script.write("#!/bin/bash\n")
		for hadd_script_path in hadd_scripts:
			master_hadd_script.write("source " + hadd_script_path + "\n")
		master_hadd_script.close()		

	if args.combine_outputs:
		luminosity = args.luminosity # in pb^-1
		from DAZSLE.ZPrimePlusJet.cross_sections import cross_sections
		output_file = ROOT.TFile("/uscms/home/dryu/DAZSLE/data/LimitSetting/hists_1D.root", "RECREATE")
		pass_histograms = {}
		fail_histograms = {}
		for supersample in ["data_obs", "qcd", "tqq", "wqq", "zqq", "Pbb_50", "Pbb_75", "Pbb_100", "Pbb_125", "Pbb_150", "Pbb_250", "Pbb_300", "Pbb_400", "Pbb_500"]:
			first = True
			for sample in config.samples[supersample]:
				input_histogram_filename = "/uscms/home/dryu/DAZSLE/data/LimitSetting/InputHistograms_{}.root".format(sample)
				print "Opening {}".format(input_histogram_filename)
				input_file = ROOT.TFile(input_histogram_filename, "READ")
				this_pass_histogram = input_file.Get("h_pass_ak8")
				this_fail_histogram = input_file.Get("h_fail_ak8")
				if supersample in config.background_names or supersample in config.signal_names:
					n_input_events = input_file.Get("h_input_nevents").Integral()
					if n_input_events > 0:
						print sample
						print "\tSample input events = {}".format(n_input_events)
						print "\tSample processed events = {}".format(input_file.Get("h_processed_nevents").Integral())
						print "\tSample pass events = {}".format(input_file.Get("h_pass_nevents").Integral())
						print "\tScaled nevents ({} pb-1) = {}".format(luminosity, luminosity * cross_sections[sample])
						print "\tLuminosity scale factor = {}".format(luminosity * cross_sections[sample] / n_input_events)
						this_pass_histogram.Scale(luminosity * cross_sections[sample] / n_input_events)
						this_fail_histogram.Scale(luminosity * cross_sections[sample] / n_input_events)
					else:
						print "[setup_limits] WARNING : Found zero input events for sample {}. Something went wrong in an earlier step. I'll continue, but you need to fix this.".format(sample)

				if first:
					pass_histograms[supersample] = this_pass_histogram.Clone()
					pass_histograms[supersample].SetDirectory(0)
					pass_histograms[supersample].SetName("{}_pass".format(supersample))
					fail_histograms[supersample] = this_fail_histogram.Clone()
					fail_histograms[supersample].SetDirectory(0)
					fail_histograms[supersample].SetName("{}_fail".format(supersample))
					first = False
				else:
					pass_histograms[supersample].Add(this_pass_histogram)
					fail_histograms[supersample].Add(this_fail_histogram)
				#if sample in cross_sections:
				#	n_input_events += input_file.Get("h_input_nevents").Integral()
				input_file.Close()
			output_file.cd()
			pass_histograms[supersample].Write()
			fail_histograms[supersample].Write()
		output_file.Close()

	if args.rhalphabet:
		top_directory = "/uscms/home/dryu/DAZSLE/data/LimitSetting/"
		os.system("mkdir -pv {}/combine".format(top_directory))
		rhalphabet_command = "python /uscms_data/d3/dryu/DAZSLE/CMSSW_7_4_7/src/DAZSLE/ZPrimePlusJet/fitting/PbbJet/buildRhalphabetPbb.py -i {}/hists_1D.root -b -o {}/combine --pseudo".format(top_directory, top_directory)
		print rhalphabet_command
		os.system(rhalphabet_command)

	if args.datacards:
		os.system("python PbbJet/makeCardsPbb.py -i /uscms/home/dryu/DAZSLE/data/LimitSetting/combine -o /uscms/home/dryu/DAZSLE/data/LimitSetting/combine -b --pseudo")
