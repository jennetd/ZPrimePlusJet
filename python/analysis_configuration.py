import os

# Signal, background, data names
background_names = [
	"qcd",
	"st_4f",
	"st_5f",
	"tqq",
	"wqq",
	"zqq"
]
signal_names = []
signal_masses = [50,75,100,125,150,250,300,400,500]
for mass in signal_masses:
	signal_names.append("Pbb_{}".format(mass))
data_names = ["data_obs"]
supersamples = []
supersamples.extend(background_names)
supersamples.extend(signal_names)
supersamples.extend(data_names)


# Sample names. Dictionary is [signal/background/data name]:[list of samples] 
samples = {
	"qcd":["QCD_HT100to200_TuneCUETP8M1_13TeV-madgraphMLM-pythia8","QCD_HT200to300_TuneCUETP8M1_13TeV-madgraphMLM-pythia8","QCD_HT300to500_TuneCUETP8M1_13TeV-madgraphMLM-pythia8","QCD_HT500to700_TuneCUETP8M1_13TeV-madgraphMLM-pythia8","QCD_HT700to1000_TuneCUETP8M1_13TeV-madgraphMLM-pythia8","QCD_HT1000to1500_TuneCUETP8M1_13TeV-madgraphMLM-pythia8","QCD_HT1500to2000_TuneCUETP8M1_13TeV-madgraphMLM-pythia8","QCD_HT2000toInf_TuneCUETP8M1_13TeV-madgraphMLM-pythia8"],
	"st_4f":["ST_t-channel_antitop_4f_inclusiveDecays_13TeV-powhegV2-madspin-pythia8_TuneCUETP8M1","ST_t-channel_top_4f_inclusiveDecays_13TeV-powhegV2-madspin-pythia8_TuneCUETP8M1"],
	"st_5f":["ST_tW_top_5f_inclusiveDecays_13TeV-powheg-pythia8_TuneCUETP8M1","ST_tW_antitop_5f_inclusiveDecays_13TeV-powheg-pythia8_TuneCUETP8M1"],
	"tqq":["TTJets_TuneCUETP8M1_13TeV-madgraphMLM-pythia8"],
	"wqq":["WJetsToQQ_HT-600ToInf_TuneCUETP8M1_13TeV-madgraphMLM-pythia8"],
	"zqq":["ZJetsToQQ_HT-600ToInf_TuneCUETP8M1_13TeV-madgraphMLM-pythia8"],
	"Pbb_50":["DMSpin0_ggPhibb1j_50"],
	"Pbb_75":["DMSpin0_ggPhibb1j_75"],
	"Pbb_100":["DMSpin0_ggPhibb1j_100"],
	"Pbb_125":["DMSpin0_ggPhibb1j_125"],
	"Pbb_150":["DMSpin0_ggPhibb1j_150"],
	"Pbb_250":["DMSpin0_ggPhibb1j_250"],
	"Pbb_300":["DMSpin0_ggPhibb1j_300"],
	"Pbb_400":["DMSpin0_ggPhibb1j_400"],
	"Pbb_500":["DMSpin0_ggPhibb1j_500"],
	"data_obs":["JetHTRun2016B","JetHTRun2016C","JetHTRun2016D","JetHTRun2016E","JetHTRun2016F","JetHTRun2016G","JetHTRun2016H"],
}

# Skims. Dictionary is [sample name]:[path to skim].
skims = {}
skims["JetHTRun2016B"] = "root://cmsxrootd-site.fnal.gov//store/user/jduarte1/zprimebits-v11.061/JetHTRun2016B_PromptReco_v2_resub.root"
skims["JetHTRun2016C"] = "root://cmsxrootd-site.fnal.gov//store/user/jduarte1/zprimebits-v11.061/JetHTRun2016C_PromptReco_v2.root"
skims["JetHTRun2016D"] = "root://cmsxrootd-site.fnal.gov//store/user/jduarte1/zprimebits-v11.061/JetHTRun2016D_PromptReco_v2.root"
skims["JetHTRun2016E"] = "root://cmsxrootd-site.fnal.gov//store/user/jduarte1/zprimebits-v11.061/JetHTRun2016E_PromptReco_v2.root"
skims["JetHTRun2016F"] = "root://cmsxrootd-site.fnal.gov//store/user/jduarte1/zprimebits-v11.061/JetHTRun2016F_PromptReco_v1.root"
skims["JetHTRun2016G"] = "root://cmsxrootd-site.fnal.gov//store/user/jduarte1/zprimebits-v11.061/JetHTRun2016G_PromptReco_v1.root"
skims["JetHTRun2016H"] = "root://cmsxrootd-site.fnal.gov//store/user/jduarte1/zprimebits-v11.061/JetHTRun2016H_PromptReco_v2.root"
skims["QCD_HT100to200_TuneCUETP8M1_13TeV-madgraphMLM-pythia8"] = "root://cmsxrootd-site.fnal.gov//store/user/jduarte1/zprimebits-v11.061/QCD_HT100to200_13TeV.root"
skims["QCD_HT200to300_TuneCUETP8M1_13TeV-madgraphMLM-pythia8"] = "root://cmsxrootd-site.fnal.gov//store/user/jduarte1/zprimebits-v11.061/QCD_HT200to300_13TeV_ext.root"
skims["QCD_HT300to500_TuneCUETP8M1_13TeV-madgraphMLM-pythia8"] = "root://cmsxrootd-site.fnal.gov//store/user/jduarte1/zprimebits-v11.061/QCD_HT300to500_13TeV_ext.root"
skims["QCD_HT500to700_TuneCUETP8M1_13TeV-madgraphMLM-pythia8"] = "root://cmsxrootd-site.fnal.gov//store/user/jduarte1/zprimebits-v11.061/QCD_HT500to700_13TeV_ext.root"
skims["QCD_HT700to1000_TuneCUETP8M1_13TeV-madgraphMLM-pythia8"] = "root://cmsxrootd-site.fnal.gov//store/user/jduarte1/zprimebits-v11.061/QCD_HT700to1000_13TeV_ext.root"
skims["QCD_HT1000to1500_TuneCUETP8M1_13TeV-madgraphMLM-pythia8"] = "root://cmsxrootd-site.fnal.gov//store/user/jduarte1/zprimebits-v11.061/QCD_HT1000to1500_13TeV_ext.root"
skims["QCD_HT1500to2000_TuneCUETP8M1_13TeV-madgraphMLM-pythia8"] = "root://cmsxrootd-site.fnal.gov//store/user/jduarte1/zprimebits-v11.061/QCD_HT1500to2000_13TeV_ext.root"
skims["QCD_HT2000toInf_TuneCUETP8M1_13TeV-madgraphMLM-pythia8"] = "root://cmsxrootd-site.fnal.gov//store/user/jduarte1/zprimebits-v11.061/QCD_HT2000toInf_13TeV_ext.root"
skims["ST_t-channel_antitop_4f_inclusiveDecays_13TeV-powhegV2-madspin-pythia8_TuneCUETP8M1"] = "root://cmsxrootd-site.fnal.gov//store/user/jduarte1/zprimebits-v11.061/ST_t-channel_antitop_4f_inclusiveDecays_13TeV_powheg.root"
skims["ST_t-channel_top_4f_inclusiveDecays_13TeV-powhegV2-madspin-pythia8_TuneCUETP8M1"] =  "root://cmsxrootd-site.fnal.gov//store/user/jduarte1/zprimebits-v11.061/ST_t-channel_top_4f_inclusiveDecays_13TeV_powheg.root"
skims["ST_tW_antitop_5f_inclusiveDecays_13TeV-powheg-pythia8_TuneCUETP8M1"] = "root://cmsxrootd-site.fnal.gov//store/user/jduarte1/zprimebits-v11.061/ST_tW_antitop_5f_inclusiveDecays_13TeV.root"
skims["ST_tW_top_5f_inclusiveDecays_13TeV-powheg-pythia8_TuneCUETP8M1"] = "root://cmsxrootd-site.fnal.gov//store/user/jduarte1/zprimebits-v11.061/ST_tW_top_5f_inclusiveDecays_13TeV.root"
skims["WJetsToQQ_HT-600ToInf_TuneCUETP8M1_13TeV-madgraphMLM-pythia8"] = "root://cmsxrootd-site.fnal.gov//store/user/jduarte1/zprimebits-v11.061/WJetsToQQ_HT_600ToInf_13TeV.root"
skims["ZJetsToQQ_HT-600ToInf_TuneCUETP8M1_13TeV-madgraphMLM-pythia8"] = "root://cmsxrootd-site.fnal.gov//store/user/jduarte1/zprimebits-v11.061/ZJetsToQQ_HT600toInf_13TeV_madgraph.root.root"
skims["TTJets_TuneCUETP8M1_13TeV-madgraphMLM-pythia8"] = "root://cmsxrootd-site.fnal.gov//store/user/jduarte1/zprimebits-v11.061/TTJets_13TeV.root"
for mass in signal_masses:
	skims["DMSpin0_ggPhibb1j_{}".format(mass)] = "root://cmsxrootd-site.fnal.gov//store/user/jduarte1/zprimebits-v11.061/DMSpin0_ggPhibb1j_{}.root".format(mass)

def get_sample_from_skim(skim):
	found_sample = ""
	for sample, filename in skims.iteritems():
		if os.path.basename(filename) == os.path.basename(skim):
			found_sample = sample
			break
	return found_sample

# Sklims
sklims = {}
sklims["JetHTRun2016B"] = "root://cmsxrootd-site.fnal.gov//store/user/jduarte1/zprimebits-v11.061/sklim-v0-Nov29/JetHTRun2016B_PromptReco_v2_resub.root"
sklims["JetHTRun2016C"] = "root://cmsxrootd-site.fnal.gov//store/user/jduarte1/zprimebits-v11.061/sklim-v0-Nov29/JetHTRun2016C_PromptReco_v2.root"
sklims["JetHTRun2016D"] = "root://cmsxrootd-site.fnal.gov//store/user/jduarte1/zprimebits-v11.061/sklim-v0-Nov29/JetHTRun2016D_PromptReco_v2.root"
sklims["JetHTRun2016E"] = "root://cmsxrootd-site.fnal.gov//store/user/jduarte1/zprimebits-v11.061/sklim-v0-Nov29/JetHTRun2016E_PromptReco_v2.root"
sklims["JetHTRun2016F"] = "root://cmsxrootd-site.fnal.gov//store/user/jduarte1/zprimebits-v11.061/sklim-v0-Nov29/JetHTRun2016F_PromptReco_v1.root"
sklims["JetHTRun2016G"] = "root://cmsxrootd-site.fnal.gov//store/user/jduarte1/zprimebits-v11.061/sklim-v0-Nov29/JetHTRun2016G_PromptReco_v1.root"
sklims["JetHTRun2016H"] = "root://cmsxrootd-site.fnal.gov//store/user/jduarte1/zprimebits-v11.061/sklim-v0-Nov29/JetHTRun2016H_PromptReco_v2.root"
sklims["QCD_HT100to200_TuneCUETP8M1_13TeV-madgraphMLM-pythia8"] = "root://cmsxrootd-site.fnal.gov//store/user/jduarte1/zprimebits-v11.061/sklim-v0-Nov29/QCD_HT100to200_13TeV_1000pb_weighted.root"
sklims["QCD_HT200to300_TuneCUETP8M1_13TeV-madgraphMLM-pythia8"] = "root://cmsxrootd-site.fnal.gov//store/user/jduarte1/zprimebits-v11.061/sklim-v0-Nov29/QCD_HT200to300_13TeV_ext_1000pb_weighted.root"
sklims["QCD_HT300to500_TuneCUETP8M1_13TeV-madgraphMLM-pythia8"] = "root://cmsxrootd-site.fnal.gov//store/user/jduarte1/zprimebits-v11.061/sklim-v0-Nov29/QCD_HT300to500_13TeV_ext_1000pb_weighted.root"
sklims["QCD_HT500to700_TuneCUETP8M1_13TeV-madgraphMLM-pythia8"] = "root://cmsxrootd-site.fnal.gov//store/user/jduarte1/zprimebits-v11.061/sklim-v0-Nov29/QCD_HT500to700_13TeV_ext_1000pb_weighted.root"
sklims["QCD_HT700to1000_TuneCUETP8M1_13TeV-madgraphMLM-pythia8"] = "root://cmsxrootd-site.fnal.gov//store/user/jduarte1/zprimebits-v11.061/sklim-v0-Nov29/QCD_HT700to1000_13TeV_ext_1000pb_weighted.root"
sklims["QCD_HT1000to1500_TuneCUETP8M1_13TeV-madgraphMLM-pythia8"] = "root://cmsxrootd-site.fnal.gov//store/user/jduarte1/zprimebits-v11.061/sklim-v0-Nov29/QCD_HT1000to1500_13TeV_ext_1000pb_weighted.root"
sklims["QCD_HT1500to2000_TuneCUETP8M1_13TeV-madgraphMLM-pythia8"] = "root://cmsxrootd-site.fnal.gov//store/user/jduarte1/zprimebits-v11.061/sklim-v0-Nov29/QCD_HT1500to2000_13TeV_ext_1000pb_weighted.root"
sklims["QCD_HT2000toInf_TuneCUETP8M1_13TeV-madgraphMLM-pythia8"] = "root://cmsxrootd-site.fnal.gov//store/user/jduarte1/zprimebits-v11.061/sklim-v0-Nov29/QCD_HT2000toInf_13TeV_ext_1000pb_weighted.root"
sklims["ST_t-channel_antitop_4f_inclusiveDecays_13TeV-powhegV2-madspin-pythia8_TuneCUETP8M1"] = "root://cmsxrootd-site.fnal.gov//store/user/jduarte1/zprimebits-v11.061/sklim-v0-Nov29/ST_t-channel_antitop_4f_inclusiveDecays_13TeV_powheg_1000pb_weighted.root"
sklims["ST_t-channel_top_4f_inclusiveDecays_13TeV-powhegV2-madspin-pythia8_TuneCUETP8M1"] =  "root://cmsxrootd-site.fnal.gov//store/user/jduarte1/zprimebits-v11.061/sklim-v0-Nov29/ST_t-channel_top_4f_inclusiveDecays_13TeV_powheg_1000pb_weighted.root"
sklims["ST_tW_antitop_5f_inclusiveDecays_13TeV-powheg-pythia8_TuneCUETP8M1"] = "root://cmsxrootd-site.fnal.gov//store/user/jduarte1/zprimebits-v11.061/sklim-v0-Nov29/ST_tW_antitop_5f_inclusiveDecays_13TeV_1000pb_weighted.root"
sklims["ST_tW_top_5f_inclusiveDecays_13TeV-powheg-pythia8_TuneCUETP8M1"] = "root://cmsxrootd-site.fnal.gov//store/user/jduarte1/zprimebits-v11.061/sklim-v0-Nov29/ST_tW_top_5f_inclusiveDecays_13TeV_1000pb_weighted.root"
sklims["WJetsToQQ_HT-600ToInf_TuneCUETP8M1_13TeV-madgraphMLM-pythia8"] = "root://cmsxrootd-site.fnal.gov//store/user/jduarte1/zprimebits-v11.061/sklim-v0-Nov29/WJetsToQQ_HT_600ToInf_13TeV_1000pb_weighted.root"
sklims["ZJetsToQQ_HT-600ToInf_TuneCUETP8M1_13TeV-madgraphMLM-pythia8"] = "root://cmsxrootd-site.fnal.gov//store/user/jduarte1/zprimebits-v11.061/sklim-v0-Nov29/ZJetsToQQ_HT600toInf_13TeV_madgraph_1000pb_weighted.root"
sklims["TTJets_TuneCUETP8M1_13TeV-madgraphMLM-pythia8"] = "root://cmsxrootd-site.fnal.gov//store/user/jduarte1/zprimebits-v11.061/sklim-v0-Nov29/TTJets_13TeV_1000pb_weighted.root"
for mass in signal_masses:
	sklims["DMSpin0_ggPhibb1j_{}".format(mass)] = "root://cmsxrootd-site.fnal.gov//store/user/jduarte1/zprimebits-v11.061/DMSpin0_ggPhibb1j_{}_1000pb_weighted.root".format(mass)

def get_sample_from_sklim(sklim):
	found_sample = ""
	for sample, filename in sklims.iteritems():
		if os.path.basename(filename) == os.path.basename(sklim):
			found_sample = sample
			break
	return found_sample

