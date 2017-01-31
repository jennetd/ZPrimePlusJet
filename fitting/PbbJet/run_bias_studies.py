import os
import sys
import array
import ROOT
from ROOT import *
sys.path.append("/uscms/home/dryu/DAZSLE/CMSSW_7_4_7/src/DAZSLE/ZPrimePlusJet/python")
import analysis_configuration as analysis_config

gROOT.SetBatch(True)
#gSystem.Load("~/Dijets/CMSSW_7_4_15/lib/slc6_amd64_gcc491/libMyToolsRootUtils.so")
gStyle.SetOptStat(0)
gStyle.SetOptTitle(0)
gStyle.SetPalette(1)
gInterpreter.Declare("#include \"MyTools/RootUtils/interface/CanvasHelpers.h\"")
gSystem.Load(os.path.expandvars("$CMSSW_BASE/lib/$SCRAM_ARCH/libMyToolsRootUtils.so"))

#seaborn = Root.SeabornInterface()
#seaborn.Initialize()

# Light temperature palette
stops = array.array('d', [0.0000, 0.1250, 0.2500, 0.3750, 0.5000, 0.6250, 0.7500, 0.8750, 1.0000])
red = array.array('d', [  31./255.,  71./255., 123./255., 160./255., 210./255., 222./255., 214./255., 199./255., 183./255.])
green = array.array('d', [  40./255., 117./255., 171./255., 211./255., 231./255., 220./255., 190./255., 132./255.,  65./255.])
blue = array.array('d', [ 234./255., 214./255., 228./255., 222./255., 210./255., 160./255., 105./255.,  60./255.,  34./255.])
palette_index = TColor.CreateGradientColorTable(9, stops, red, green, blue, 255, 1.)
gStyle.SetNumberContours(255)
gStyle.SetPaintTextFormat('1.2f')

top_directory = "/uscms/home/dryu/DAZSLE/data/LimitSetting/BiasStudies/"

def run_bias_study(name, datacard, workspace, n_toys=1000, mu=0, dry_run=True):
	print "Running bias study " + name
	working_directory = top_directory + name
	print "\tDirectory = " + working_directory
	os.system("mkdir -pv " + working_directory)
	script_path = working_directory + "/run.sh"
	script = open(script_path, 'w')
	script.write("#!/bin/bash\n")
	script.write("mkdir higgsCombine" + name)
	script.write("combine -M GenerateOnly --expectSignal " + str(mu) + " -n " + name + " -t " + str(n_toys) + " --saveToys --rMin -1000 --rMax 1000 " + os.path.basename(datacard) + "\n")
	script.write("combine -M MaxLikelihoodFit -n " + name + " -t " + str(n_toys) + " --out test_fit --saveNormalizations --toysFile higgsCombine" + name + ".GenerateOnly.mH120.123456.root --rMin -1000 --rMax 1000 --robustFit=0 --verbose 2 " + os.path.basename(datacard) + "\n")
	script.close()
	if not dry_run:
		os.system("csub " + script_path + " --cmssw --no_retar -d " + working_directory + " -F " + datacard + "," + workspace)

def run_many_bias_studies(top_name, job_names, datacards, workspaces, n_toys, mu, dry_run=True):
	working_directory = top_directory + top_name
	print "\tDirectory = " + working_directory
	os.system("mkdir -pv " + working_directory)
	script_paths = []
	files_to_transfer = []
	for name in job_names:
		script_path = working_directory + "/run_" + name + ".sh"
		script_paths.append(script_path)
		script = open(script_path, 'w')
		script.write("#!/bin/bash\n")

		script.write("echo $PWD\n")
		script.write("ls -lrth\n")
		script.write("mkdir -pv higgsCombine" + name + "\n")
		script.write("combine -M GenerateOnly --expectSignal " + str(mu) + " -n " + name + " -t " + str(n_toys) + " --saveToys --rMin -1000 --rMax 1000 " + os.path.basename(datacards[name]) + "\n")
		script.write("combine -M MaxLikelihoodFit -n " + name + " -t " + str(n_toys) + " --saveNormalizations --toysFile higgsCombine" + name + ".GenerateOnly.mH120.123456.root --rMin -1000 --rMax 1000 --robustFit=0 --verbose 2 " + os.path.basename(datacards[name]) + "\n") #  --out test_fit
		script.write("echo $PWD\n")
		script.write("ls -lrth\n")
		script.write("rm -f higgsCombine" + name + ".GenerateOnly.mH120.123456.root")
		files_to_transfer.append(datacards[name])
		files_to_transfer.extend(workspaces[name])
		files_to_transfer.append(script_path)
		script.close()

	files_to_transfer = list(set(files_to_transfer))

	# Master script
	master_script_path = working_directory + "/run_master.sh"
	master_script = open(master_script_path, "w")
	master_script.write("#!/bin/bash\n")
	master_script.write("job_scripts=( " + " ".join([os.path.basename(x) for x in script_paths]) + " )\n")
	master_script.write("source ${job_scripts[$1]}\n")
	master_script.close()

	if not dry_run:
		print "csub " + master_script_path + " --cmssw --no_retar -d " + working_directory + " -F " + ",".join(files_to_transfer) + " -n " + str(len(script_paths))
		os.system("csub " + master_script_path + " --cmssw --no_retar -d " + working_directory + " -F " + ",".join(files_to_transfer) + " -n " + str(len(script_paths)))
	else:
		print "csub " + master_script_path + " --cmssw --no_retar -d " + working_directory + " -F " + ",".join(files_to_transfer) + " -n " + str(len(script_paths))

# x-axis = mass
# One per model
def plot_all_averages(injected_mu=0):
	#results_tree = TTree("bias_study_results", "bias_study_results")
	#containers = {}
	##containers["f_gen"] = array.array('i', [0])
	##containers["f_fit"] = array.array('i', [0])
	#containers["mass"] = array.array('d', [0])
	#containers["average_mu"] = array.array('d', [0])
	#containers["average_pull"] = array.array('d', [0])
	#containers["average_pull_centered"] = array.array('d', [0])
	#containers["rms_pull"] = array.array('d', [0])
	#for container_name, container in containers.iteritems():
	#	print "Making branch for " + container_name
	#	results_tree.Branch(container_name, container)
	masses = [50, 75, 100, 125, 150, 250]

	tg_avg_mu = TGraphErrors(len(masses))
	tg_avg_mu.SetName("tg_avg_mu")
	#tg_avg_pull = TGraphErrors(len(masses))
	#tg_avg_pull.SetName("tg_avg_pull")
	tg_avg_centered_pull = TGraphErrors(len(masses))
	tg_avg_centered_pull.SetName("tg_avg_centered_pull")

	pull_hists = {}

	for i, mass in enumerate(masses):
		pull_hists[mass] = TH1D("pull_hist_{}_{}".format(mass, injected_mu), "pull_hist_{}_{}".format(mass, injected_mu), 24, -3., 3.)
		pull_hists[mass].SetDirectory(0)
		results_file = TFile("/uscms/home/dryu/DAZSLE/data/LimitSetting/BiasStudies/Pbb_M{}_mu{}/mlfitPbb_M{}_mu{}.root".format(mass, injected_mu, mass, injected_mu), "READ")
		if not results_file.IsOpen():
			print "[plot_all_averages] WARNING : Results file not found at path " + "/uscms/home/dryu/DAZSLE/data/LimitSetting/BiasStudies/Pbb_M{}_mu{}/mlfitPbb_M{}_mu{}.root".format(mass, injected_mu, mass, injected_mu)
			continue
		t = results_file.Get("tree_fit_sb")
		if not t:
			print "[plot_all_averages] WARNING : File found but tree tree_fit_sb not available at path" + "/uscms/home/dryu/DAZSLE/data/LimitSetting/BiasStudies/Pbb_M{}_mu{}/mlfitPbb_M{}_mu{}.root".format(mass, injected_mu, mass, injected_mu)
			continue
		weights = 0
		mu_sum = 0.
		mu2_sum = 0.
		pull_sum = 0.
		pull2_sum = 0.
		centered_pull_sum = 0.
		centered_pull2_sum = 0.
		t.SetBranchStatus("*", 0)
		containers = {}
		containers["mu"] = array.array('d', [0.])
		containers["muErr"] = array.array('d', [0.])
		for branch_name, branch_container in containers.iteritems():
			t.SetBranchStatus(branch_name, 1)
			t.SetBranchAddress(branch_name, branch_container)
		for entry in xrange(t.GetEntriesFast()):
			t.GetEntry(entry)
			if containers["muErr"][0] <= 0:
				continue
			if abs(containers["mu"][0] / containers["muErr"][0]) > 10:
				continue
			mu_sum += containers["mu"][0]
			mu2_sum += containers["mu"][0]**2
			pull_sum += containers["mu"][0] / containers["muErr"][0]
			pull2_sum += (containers["mu"][0] / containers["muErr"][0])**2
			centered_pull_sum += (containers["mu"][0] - injected_mu) / containers["muErr"][0]
			centered_pull2_sum += ((containers["mu"][0] - injected_mu) / containers["muErr"][0])**2
			weights += 1
			pull_hists[mass].Fill((containers["mu"][0] - injected_mu) / containers["muErr"][0])
		if weights > 0:
			mu_avg = mu_sum / weights
			mu2_avg = mu2_sum / weights
			pull_avg = pull_sum / weights
			pull2_avg = pull2_sum / weights
			centered_pull_avg = centered_pull_sum / weights
			centered_pull2_avg = centered_pull2_sum / weights
			mu_rms = (mu2_avg - (mu_avg**2))**0.5
			pull_rms = (pull2_avg - (pull_avg**2))**0.5
		else:
			mu_avg = 1.e20
			mu2_avg = 1.e20
			pull_avg = 1.e20
			pull2_avg = 1.e20
			centered_pull_avg = 1.e20
			centered_pull2_avg = 1.e20
			mu_rms = 1.e20
			pull_rms = 1.e20

		tg_avg_mu.SetPoint(i, mass, mu_avg)
		#tg_avg_pull.SetPoint(i, mass, pull_avg)
		#tg_avg_pull.SetPointError(i, 0., pull_rms)
		tg_avg_centered_pull.SetPoint(i, mass, centered_pull_avg)
		tg_avg_centered_pull.SetPointError(i, 0., pull_rms)
		#containers["average_mu"][0] = mu_avg
		#containers["average_pull"][0] = pull_avg
		#containers["average_pull_centered"][0] = centered_pull_avg
		#containers["rms_pull"][0] = pull_rms
		#results_tree.Fill()
		c_pull_hist = TCanvas("c_pulls_M{}_mu{}".format(mass, injected_mu), "c_pulls_M{}_mu{}".format(mass, injected_mu), 800, 600)
		pull_hists[mass].Draw("hist")
		Root.myText(0.15, 0.8, 1, "Mean={}".format(round(centered_pull_avg, 2)), 0.75)
		Root.myText(0.15, 0.7, 1, "RMS={}".format(round(pull_rms, 2)), 0.75)
		c_pull_hist.SaveAs(top_directory + "/" + c_pull_hist.GetName() + ".pdf")
	c_avg_mu = TCanvas("c_avg_mu_vs_mass_" + str(injected_mu), "c_avg_mu_vs_mass", 800, 600)
	c_avg_mu.SetRightMargin(0.2)
	c_avg_mu.SetBottomMargin(0.15)
	tg_avg_mu.GetHistogram().GetXaxis().SetTitle("m_{X} [GeV]")
	tg_avg_mu.GetHistogram().GetYaxis().SetTitle("#LT#mu#GT")
	tg_avg_mu.GetHistogram().SetMinimum(injected_mu - 0.1)
	tg_avg_mu.GetHistogram().SetMaximum(injected_mu + 0.1)
	tg_avg_mu.SetMarkerStyle(20)
	tg_avg_mu.SetMarkerSize(1)
	tg_avg_mu.Draw("ap")
	c_avg_mu.SaveAs(top_directory + "/" + c_avg_mu.GetName() + ".pdf")

	#c_avg_pull = TCanvas("c_avg_pull_f_vs_mass_" + str(injected_mu), "c_avg_pull_f_vs_mass", 800, 600)
	#c_avg_pull.SetRightMargin(0.2)
	#c_avg_pull.SetBottomMargin(0.15)
	#tg_avg_pull.GetHistogram().GetXaxis().SetTitle("Signal mass")
	#tg_avg_pull.GetHistogram().GetYaxis().SetTitle("#LT#mu/#sigma_{#mu}#GT")
	#if injected_mu == 0:
	#	tg_avg_pull.GetHistogram().SetMinimum(-5.)
	#	tg_avg_pull.GetHistogram().SetMaximum(5.)
	#tg_avg_pull.GetHistogram().Draw("ap")
	#c_avg_pull.SaveAs(top_directory + "/" + c_avg_pull.GetName() + ".pdf")

	c_avg_centered_pull = TCanvas("c_avg_centered_pull_vs_mass_" + str(injected_mu), "c_avg_centered_pull_vs_mass", 800, 600)
	c_avg_centered_pull.SetRightMargin(0.2)
	c_avg_centered_pull.SetBottomMargin(0.15)
	tg_avg_centered_pull.GetHistogram().GetXaxis().SetTitle("Signal mass")
	tg_avg_centered_pull.GetHistogram().GetYaxis().SetTitle("#LT(#mu-#mu_{inj})/#sigma_{#mu}#GT")
	tg_avg_centered_pull.GetHistogram().SetMinimum(-3)
	tg_avg_centered_pull.GetHistogram().SetMaximum(3)
	tg_avg_centered_pull.SetMarkerStyle(20)
	tg_avg_centered_pull.SetMarkerSize(1)
	tg_avg_centered_pull.Draw("ap")
	lines = {}
	for y in range(-3, 4, 1):
		lines[y] = TLine(tg_avg_mu.GetHistogram().GetXaxis().GetXmin(), y, tg_avg_mu.GetHistogram().GetXaxis().GetXmax(), y)
		lines[y].SetLineColor(ROOT.kGray)
		lines[y].SetLineStyle(2)
		lines[y].Draw("same")
	c_avg_centered_pull.SaveAs(top_directory + "/" + c_avg_centered_pull.GetName() + ".pdf")

	results_file = TFile(top_directory + "/summary_mu" + str(injected_mu) + ".root", "RECREATE")
	tg_avg_mu.Write()
	#tg_avg_pull.Write()
	tg_avg_centered_pull.Write()
	#results_tree.Write()
	results_file.Close()

# Plot: x-axis = gen function, y-axis = fit function
# One per mass point and model

# Plot: pull histogram

if __name__ == "__main__":
	import argparse
	parser = argparse.ArgumentParser(description = 'Run bias studies and plot output')
	parser.add_argument('--masses', type=str, default="all", help='Model name')
	parser.add_argument('--run', action='store_true', help='Run bias studies')
	parser.add_argument('--retry', action='store_true', help='Rerun failed bias studies')
	parser.add_argument('--dry_run', action='store_true', help='Setup but do not run bias studies')
	parser.add_argument('--n_toys', type=int, default=100, help='Number of toys to run')
	parser.add_argument('--mu', type=int, default=0, help='Signal mu (1 = inject signal at +2sigma expected limit)')
	parser.add_argument('--test', action='store_true', help='Small test job')
	parser.add_argument('--plots', action='store_true', help='Plot results')
	args = parser.parse_args()

	if args.masses == "all":
		masses = [50, 75, 100, 125, 150, 250]
	else:
		masses = [int(x) for x in args.masses.split(",")]

	if args.run:
		for mass in masses:
			names = []
			datacards = {}
			workspaces = {}
			name = "Pbb_M{}_mu{}".format(mass, args.mu)
			names.append(name)
			datacards[name] = "/uscms/home/dryu/DAZSLE/data/LimitSetting/combine/card_rhalphabet_M{}.txt".format(mass)
			workspaces[name] = ["/uscms/home/dryu/DAZSLE/data/LimitSetting/combine/base.root", "/uscms/home/dryu/DAZSLE/data/LimitSetting/combine/rhalphabase.root"]
			run_many_bias_studies(name, names, datacards=datacards, workspaces=workspaces, n_toys=args.n_toys, mu=args.mu, dry_run=args.dry_run)

	if args.plots:
		for mu in [0, 1]:
			plot_all_averages(injected_mu=mu)
