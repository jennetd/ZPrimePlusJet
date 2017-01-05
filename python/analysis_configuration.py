# Samples
samples = [
	"qcd",
	"tqq_4f",
	"tqq_5f",
	"wqq",
	"zqq",
	"data"
]
signal_masses = [50,75,100,125,150,250,300,400,500]
for mass in signal_masses:
	samples.append("Pbb_{}".format(mass))


# Skims
skims = {}
skims["data"] = [
	#"/eos/uscms/store/user/jduarte1/zprimebits-v11.061/JetHTRun2016B_PromptReco_v2_resub.root",
	#"/eos/uscms/store/user/jduarte1/zprimebits-v11.061/JetHTRun2016C_PromptReco_v2.root",
	#"/eos/uscms/store/user/jduarte1/zprimebits-v11.061/JetHTRun2016D_PromptReco_v2.root",
	"/eos/uscms/store/user/jduarte1/zprimebits-v11.061/JetHTRun2016E_PromptReco_v2.root",
	#"/eos/uscms/store/user/jduarte1/zprimebits-v11.061/JetHTRun2016F_PromptReco_v1.root",
	#"/eos/uscms/store/user/jduarte1/zprimebits-v11.061/JetHTRun2016G_PromptReco_v1.root",
	#"/eos/uscms/store/user/jduarte1/zprimebits-v11.061/JetHTRun2016H_PromptReco_v2.root",
]
skims["qcd"] = [
	"/eos/uscms/store/user/jduarte1/zprimebits-v11.061/QCD_HT100to200_13TeV.root",
	"/eos/uscms/store/user/jduarte1/zprimebits-v11.061/QCD_HT200to300_13TeV_ext.root",
	"/eos/uscms/store/user/jduarte1/zprimebits-v11.061/QCD_HT300to500_13TeV_ext.root",
	"/eos/uscms/store/user/jduarte1/zprimebits-v11.061/QCD_HT500to700_13TeV_ext.root",
	"/eos/uscms/store/user/jduarte1/zprimebits-v11.061/QCD_HT700to1000_13TeV_ext.root",
	"/eos/uscms/store/user/jduarte1/zprimebits-v11.061/QCD_HT1000to1500_13TeV_ext.root",
	"/eos/uscms/store/user/jduarte1/zprimebits-v11.061/QCD_HT1500to2000_13TeV_ext.root",
	"/eos/uscms/store/user/jduarte1/zprimebits-v11.061/QCD_HT2000toInf_13TeV_ext.root",
]
skims["tqq_4f"] = [
	"/eos/uscms/store/user/jduarte1/zprimebits-v11.061/ST_t-channel_antitop_4f_inclusiveDecays_13TeV_powheg.root",
	"/eos/uscms/store/user/jduarte1/zprimebits-v11.061/ST_t-channel_top_4f_inclusiveDecays_13TeV_powheg.root",
]
skims["tqq_5f"] = [
	"/eos/uscms/store/user/jduarte1/zprimebits-v11.061/ST_tW_antitop_5f_inclusiveDecays_13TeV.root",
	"/eos/uscms/store/user/jduarte1/zprimebits-v11.061/ST_tW_top_5f_inclusiveDecays_13TeV.root",
]
skims["wqq"] = [
	"/eos/uscms/store/user/jduarte1/zprimebits-v11.061/WJetsToQQ_HT_600ToInf_13TeV.root",
]
skims["zqq"] = [
	"/eos/uscms/store/user/jduarte1/zprimebits-v11.061/DYJetsToQQ_HT180_13TeV.root",
]
skims["ttbar"] = [
	"/eos/uscms/store/user/jduarte1/zprimebits-v11.061/TTJets_13TeV.root",
]
for mass in signal_masses:
	skims["Pbb_{}".format(mass)] = ["/eos/uscms/store/user/jduarte1/zprimebits-v11.061/DMSpin0_ggPhibb1j_{}.root".format(mass)]

# Sklims
sklims = {}
sklims["data"] = [
	#"/eos/uscms/store/user/jduarte1/zprimebits-v11.061/sklim-v0-Nov29/JetHTRun2016B_PromptReco_v2_resub.root",
	#"/eos/uscms/store/user/jduarte1/zprimebits-v11.061/sklim-v0-Nov29/JetHTRun2016C_PromptReco_v2.root",
	#"/eos/uscms/store/user/jduarte1/zprimebits-v11.061/sklim-v0-Nov29/JetHTRun2016D_PromptReco_v2.root",
	"/eos/uscms/store/user/jduarte1/zprimebits-v11.061/sklim-v0-Nov29/JetHTRun2016E_PromptReco_v2.root",
	#"/eos/uscms/store/user/jduarte1/zprimebits-v11.061/sklim-v0-Nov29/JetHTRun2016F_PromptReco_v1.root",
	#"/eos/uscms/store/user/jduarte1/zprimebits-v11.061/sklim-v0-Nov29/JetHTRun2016G_PromptReco_v1.root",
	#"/eos/uscms/store/user/jduarte1/zprimebits-v11.061/sklim-v0-Nov29/JetHTRun2016H_PromptReco_v2.root",
]
sklims["qcd"] = [
	"/eos/uscms/store/user/jduarte1/zprimebits-v11.061/sklim-v0-Nov29/QCD_HT100to200_13TeV_1000pb_weighted.root",
	"/eos/uscms/store/user/jduarte1/zprimebits-v11.061/sklim-v0-Nov29/QCD_HT200to300_13TeV_ext_1000pb_weighted.root",
	"/eos/uscms/store/user/jduarte1/zprimebits-v11.061/sklim-v0-Nov29/QCD_HT300to500_13TeV_ext_1000pb_weighted.root",
	"/eos/uscms/store/user/jduarte1/zprimebits-v11.061/sklim-v0-Nov29/QCD_HT500to700_13TeV_ext_1000pb_weighted.root",
	"/eos/uscms/store/user/jduarte1/zprimebits-v11.061/sklim-v0-Nov29/QCD_HT700to1000_13TeV_ext_1000pb_weighted.root",
	"/eos/uscms/store/user/jduarte1/zprimebits-v11.061/sklim-v0-Nov29/QCD_HT1000to1500_13TeV_ext_1000pb_weighted.root",
	"/eos/uscms/store/user/jduarte1/zprimebits-v11.061/sklim-v0-Nov29/QCD_HT1500to2000_13TeV_ext_1000pb_weighted.root",
	"/eos/uscms/store/user/jduarte1/zprimebits-v11.061/sklim-v0-Nov29/QCD_HT2000toInf_13TeV_ext_1000pb_weighted.root",
]
sklims["tqq_4f"] = [
	"/eos/uscms/store/user/jduarte1/zprimebits-v11.061/sklim-v0-Nov29/ST_t-channel_antitop_4f_inclusiveDecays_13TeV_powheg_1000pb_weighted.root",
	"/eos/uscms/store/user/jduarte1/zprimebits-v11.061/sklim-v0-Nov29/ST_t-channel_top_4f_inclusiveDecays_13TeV_powheg_1000pb_weighted.root",
]
sklims["tqq_5f"] = [
	"/eos/uscms/store/user/jduarte1/zprimebits-v11.061/sklim-v0-Nov29/ST_tW_antitop_5f_inclusiveDecays_13TeV_1000pb_weighted.root",
	"/eos/uscms/store/user/jduarte1/zprimebits-v11.061/sklim-v0-Nov29/ST_tW_top_5f_inclusiveDecays_13TeV_1000pb_weighted.root",
]
sklims["wqq"] = [
	"/eos/uscms/store/user/jduarte1/zprimebits-v11.061/sklim-v0-Nov29/WJetsToQQ_HT_600ToInf_13TeV_1000pb_weighted.root",
]
sklims["zqq"] = [
	"/eos/uscms/store/user/jduarte1/zprimebits-v11.061/sklim-v0-Nov29/DYJetsToQQ_HT180_13TeV_1000pb_weighted.root",
]
sklims["ttbar"] = [
	"/eos/uscms/store/user/jduarte1/zprimebits-v11.061/sklim-v0-Nov29/TTJets_13TeV_1000pb_weighted.root",
]
for mass in signal_masses:
	sklims["Pbb_{}".format(mass)] = ["/eos/uscms/store/user/jduarte1/zprimebits-v11.061/sklim-v0-Nov29/DMSpin0_ggPhibb1j_{}_1000pb_weighted.root".format(mass)]
