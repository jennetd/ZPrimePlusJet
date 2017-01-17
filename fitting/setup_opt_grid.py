import os
import sys
import ROOT
from DAZSLE.ZPrimePlusJet.analysis_base import AnalysisBase
import DAZSLE.ZPrimePlusJet.analysis_configuration as config
from math import ceil, sqrt,floor

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

from setup_limits import LimitHistograms

# Grid points
opt_vars = ["jet_type", "tau21_ddt", "dcsv"]
opt_var_values = {
	#"jet_type":["AK8", "CA15"],
	"jet_type":["CA15"],	
	"tau21_ddt":[0.2,0.25,0.3,0.35,0.4,0.45,0.5,0.55,0.6],
	"dcsv":[0.7,0.8,0.85,0.9,0.95],
}

if __name__ == "__main__":
	import argparse
	parser = argparse.ArgumentParser(description='Make histograms and workspaces for limit setting for optimization grid.')
	input_group = parser.add_mutually_exclusive_group() 
	input_group.add_argument('--all', action="store_true", help="Run over all supersamples")
	input_group.add_argument('--supersamples', type=str, help="Supersample name(s), comma separated. Must correspond to something in analysis_configuration.(background_names, signal_names, or data_names).")
	input_group.add_argument('--samples', type=str, help="Sample name(s), comma separated. Must be a key in analysis_configuration.skims.")
	input_group.add_argument('--files', type=str, help="Input file name(s), comma separated")
	input_group.add_argument('--n_jobs', type=int, default=4, help="For --run, specify the number of parallel jobs.")
	action_group = parser.add_mutually_exclusive_group() 
	action_group.add_argument('--run', action="store_true", help="Run")
	action_group.add_argument('--condor_run', action="store_true", help="Run on condor")
	action_group.add_argument('--combine_outputs', action="store_true", help="Compile results into one file for next step (buildRhalphabet). Also applies luminosity weights to MC.")
	action_group.add_argument('--rhalphabet', action="store_true", help="Setup rhalphabet and prepare combine workspaces.")
	action_group.add_argument('--copy_cards', action="store_true", help="Copy cards to the combine folders.")
	parser.add_argument('--output_folder', type=str, help="Output folder")
	parser.add_argument('--label', type=str, help="If running with --files, need to specify a label manually, in lieu of the sample names, for the output file naming.")
	selection_group = parser.add_mutually_exclusive_group()
	selection_group.add_argument("--single_point", type=str, nargs=3, help="Specify single (jet_type, tau21_ddt, dcsv) point.")
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

	# Generate list of selections	
	if args.single_point:
		opt_var_values["jet_type"] = [args.single_point[0]]
		opt_var_values["tau21_ddt"] = [float(args.single_point[1])]
		opt_var_values["dcsv"] = [float(args.single_point[2])]
	selection_names = []
	selection_values = {}
	for jet_type_value in opt_var_values["jet_type"]:
		for tau21_ddt_value in opt_var_values["tau21_ddt"]:
			for dcsv_value in opt_var_values["dcsv"]:
				selection_name = "jet_type_{}_tau21_ddt_{}_dcsv_{}".format(jet_type_value, round(tau21_ddt_value, 2), round(dcsv_value, 2))
				selection_names.append(selection_name)
				selection_values[selection_name] = {"jet_type":jet_type_value, "tau21_ddt":tau21_ddt_value, "dcsv":dcsv_value}

	if args.run:
		for selection_name in selection_names:
			for sample in samples:
				print "\n *** Running sample {}".format(sample)
				limit_histogrammer = LimitHistograms(sample, "Events")
				if args.output_folder:
					limit_histogrammer.set_output_path("{}/InputHistograms_{}.root".format(args.output_folder, sample))
				else:
					limit_histogrammer.set_output_path("/uscms/home/dryu/DAZSLE/data/LimitSetting/Optimization/{}/InputHistograms_{}.root".format(selection_name, sample))
				for filename in sample_files[sample]:
					print "Input file {}".format(filename)
					limit_histogrammer.add_file(filename)
				limit_histogrammer.set_jet_type(selection_values[selection_name]["jet_type"])
				limit_histogrammer.set_cut("tau21_ddt", selection_values[selection_name]["tau21_ddt"])
				limit_histogrammer.set_cut("dcsv", selection_values[selection_name]["dcsv"])
				limit_histogrammer.start()
				limit_histogrammer.run()
				limit_histogrammer.finish()

	if args.condor_run:
		import time
		postprocessing_commands = []
		for sample in samples:
			start_directory = os.getcwd()
			job_tag = "job_{}_{}".format(sample, int(floor(time.time())))
			submission_directory = "/uscms/home/dryu/DAZSLE/data/LimitSetting/Optimization/condor/{}".format(job_tag)
			os.system("mkdir -pv {}".format(submission_directory))
			os.chdir(submission_directory)

			files_per_job = 1
			if "JetHTRun2016" in sample:
				files_per_job = 5
			elif "QCD" in sample:
				files_per_job = 2

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
					job_script_path = "{}/run_csubjob{}.sh".format(submission_directory, csubjob_index)
					job_script = open(job_script_path, 'w')
					job_script.write("#!/bin/bash\n")
					for selection_name in selection_names:
						job_script.write("python $CMSSW_BASE/src/DAZSLE/ZPrimePlusJet/fitting/setup_opt_grid.py --single_point {} {} {} --files {} --label {}_{}_csubjob{} --output_folder . --run\n".format(selection_values[selection_name]["jet_type"], selection_values[selection_name]["tau21_ddt"], selection_values[selection_name]["dcsv"], ",".join(this_job_input_files), sample, selection_name, csubjob_index))
					job_script.close()
					submission_command = "csub {} --cmssw --no_retar".format(job_script_path)
					if len(input_files_to_transfer) >= 1:
						submission_command += " -F " + ",".join(input_files_to_transfer)
					print submission_command
					os.system(submission_command)
					this_job_input_files = []
					input_files_to_transfer = []
					csubjob_index += 1
			hadd_script_path = "{}/hadd.sh".format(submission_directory)
			hadd_script = open(hadd_script_path, "w")
			hadd_script.write("#!/bin/bash\n")
			for selection_name in selection_names:
				hadd_script.write("hadd /uscms/home/dryu/DAZSLE/data/LimitSetting/Optimization/{}/InputHistograms_{}.root {}/InputHistograms*{}*csubjob*root\n".format(selection_name, sample, submission_directory, selection_name))
			hadd_script.close()
			postprocessing_commands.append("source {}".format(hadd_script_path))
			os.chdir(start_directory)

		master_hadd_basename = "master_hadd"
		if args.single_point:
			master_hadd_basename += "_" + selection_names[0]
		if not args.all:
			master_hadd_basename += "_" + str(int(floor(time.time())))
		master_hadd_basename += ".sh"
		master_hadd_script_path = "/uscms/home/dryu/DAZSLE/data/LimitSetting/Optimization/{}".format(master_hadd_basename)
		master_hadd_script = open(master_hadd_script_path, "w")
		master_hadd_script.write("#!/bin/bash\n")
		for postprocessing_command in postprocessing_commands:
			master_hadd_script.write(postprocessing_command + "\n")
		master_hadd_script.close()
		print "Once jobs have finished, run hadd with:"
		print "source " + master_hadd_script_path

	if args.combine_outputs:
		luminosity = 34.207 * 1.e3 # in pb^-1
		from DAZSLE.ZPrimePlusJet.cross_sections import cross_sections
		for selection_name in selection_names:
			top_directory = "/uscms/home/dryu/DAZSLE/data/LimitSetting/Optimization/{}".format(selection_name)
			output_file = ROOT.TFile("{}/hists_1D.root".format(top_directory), "RECREATE")
			pass_histograms = {}
			fail_histograms = {}
			for supersample in ["data_obs", "qcd", "tqq", "wqq", "zqq", "Pbb_50", "Pbb_75", "Pbb_100", "Pbb_125", "Pbb_150", "Pbb_250", "Pbb_300", "Pbb_400", "Pbb_500"]:
				first = True
				for sample in config.samples[supersample]:
					input_histogram_filename = "{}/InputHistograms_{}.root".format(top_directory, sample)
					print "Opening {}".format(input_histogram_filename)
					input_file = ROOT.TFile(input_histogram_filename, "READ")
					this_pass_histogram = input_file.Get("h_pass_ak8")
					this_fail_histogram = input_file.Get("h_fail_ak8")
					if supersample in config.background_names or supersample in config.signal_names:
						n_input_events = input_file.Get("h_input_nevents").Integral()
						if n_input_events > 0:
							#print sample
							#print "\tSample input events = {}".format(n_input_events)
							#print "\tSample processed events = {}".format(input_file.Get("h_processed_nevents").Integral())
							#print "\tSample pass events = {}".format(input_file.Get("h_pass_nevents").Integral())
							#print "\tScaled nevents (30 fb-1) = {}".format(luminosity * cross_sections[sample])
							#print "\tLuminosity scale factor = {}".format(luminosity * cross_sections[sample] / n_input_events)
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
					if sample in cross_sections:
						n_input_events += input_file.Get("h_input_nevents").Integral()
					input_file.Close()
				output_file.cd()
				pass_histograms[supersample].Write()
				fail_histograms[supersample].Write()
			output_file.Close()

	if args.rhalphabet:
		for selection_name in selection_names:
			top_directory = "/uscms/home/dryu/DAZSLE/data/LimitSetting/Optimization/{}".format(selection_name)
			os.system("mkdir -pv {}/combine".format(top_directory))
			rhalphabet_command = "python /uscms_data/d3/dryu/DAZSLE/CMSSW_7_4_7/src/DAZSLE/ZPrimePlusJet/fitting/PbbJet/buildRhalphabetPbb.py -i {}/hists_1D.root -b -o {}/combine --pseudo".format(top_directory, top_directory)
			print rhalphabet_command
			os.system(rhalphabet_command)
	if args.copy_cards:
		for selection_name in selection_names:
			top_directory = "/uscms/home/dryu/DAZSLE/data/LimitSetting/Optimization/{}".format(selection_name)
			os.system("cp ~/DAZSLE/data/LimitSetting/combine/card*txt {}/combine".format(top_directory))