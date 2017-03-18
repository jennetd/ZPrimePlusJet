import os
import math
from array import array
from ROOT import *
import sys
sys.path.append(os.path.expandvars("$CMSSW_BASE/src/DAZSLE/ZPrimePlusJet/analysis"))
from sampleContainer import *
import DAZSLE.PhiBBPlusJet.analysis_configuration as config


def RunSampleContainer(sample_name, input_filenames, output_filename, lumi, sf=1, isData=False, fillCA15=False, cutFormula="1", xsec=None, tree_name="otree"):
	output_file = TFile(output_filename, "RECREATE")
	sample = sampleContainer(sample_name, input_filenames, sf=sf, lumi=lumi, isData=isData, fillCA15=fillCA15, cutFormula=cutFormula, processEvents=-1, tree_name=tree_name)

	# Number of input events
	h_nevents = TH1D("NEvents", "NEvents", 1, 0, 1)
	h_nevents.SetBinContent(1, sample.GetNEvents())
	h_nevents.Write()
	hall={}

	# Normalization weight? For samples where scale1fb hasn't been calculated. This must be the normalization factor to 1 fb^-1, then.
	if xsec:
		scale1fb = 1000. * xsec / sample.GetNEvents()

	plots =  ['h_msd_v_pt_ak8_topR6_N2_pass',
				'h_msd_v_pt_ak8_topR6_N2_fail', #SR with N2DDT @ 26% && db > 0.9, msd corrected
				'h_msd_v_pt_ak8_topR6_N2_pass_matched',
				'h_msd_v_pt_ak8_topR6_N2_pass_unmatched', #matched and unmatached for mass up/down
				'h_msd_v_pt_ak8_topR6_N2_fail_matched',
				'h_msd_v_pt_ak8_topR6_N2_fail_unmatched', #matched and unmatached for mass up/down
				'h_msd_v_pt_ak8_topR6_N2_pass_JESUp',
				'h_msd_v_pt_ak8_topR6_N2_pass_JESDown', #JES up/down
				'h_msd_v_pt_ak8_topR6_N2_fail_JESUp',
				'h_msd_v_pt_ak8_topR6_N2_fail_JESDown', #JES up/down
				'h_msd_v_pt_ak8_topR6_N2_pass_JERUp',
				'h_msd_v_pt_ak8_topR6_N2_pass_JERDown', #JER up/down
				'h_msd_v_pt_ak8_topR6_N2_fail_JERUp',
				'h_msd_v_pt_ak8_topR6_N2_fail_JERDown', #JER up/down
				'h_msd_v_pt_ak8_topR6_N2_pass_triggerUp',
				'h_msd_v_pt_ak8_topR6_N2_pass_triggerDown', #trigger up/down
				'h_msd_v_pt_ak8_topR6_N2_fail_triggerUp',
				'h_msd_v_pt_ak8_topR6_N2_fail_triggerDown', #trigger up/down              
				'h_msd_v_pt_ak8_bbleading_topR6_pass',
				'h_msd_v_pt_ak8_bbleading_topR6_fail',
				'h_msd_ak8_muCR4_N2_pass',
				'h_msd_ak8_muCR4_N2_fail',
				'h_msd_ak8_muCR4_N2_pass_JESUp',
				'h_msd_ak8_muCR4_N2_pass_JESDown',
				'h_msd_ak8_muCR4_N2_fail_JESUp',
				'h_msd_ak8_muCR4_N2_fail_JESDown',
				'h_msd_ak8_muCR4_N2_pass_JERUp',
				'h_msd_ak8_muCR4_N2_pass_JERDown',
				'h_msd_ak8_muCR4_N2_fail_JERUp',
				'h_msd_ak8_muCR4_N2_fail_JERDown',
				'h_msd_ak8_muCR4_N2_pass_mutriggerUp',
				'h_msd_ak8_muCR4_N2_pass_mutriggerDown',
				'h_msd_ak8_muCR4_N2_fail_mutriggerUp',
				'h_msd_ak8_muCR4_N2_fail_mutriggerDown',
				'h_msd_ak8_muCR4_N2_pass_muidUp',
				'h_msd_ak8_muCR4_N2_pass_muidDown',
				'h_msd_ak8_muCR4_N2_fail_muidUp',
				'h_msd_ak8_muCR4_N2_fail_muidDown',
				'h_msd_ak8_muCR4_N2_pass_muisoUp',
				'h_msd_ak8_muCR4_N2_pass_muisoDown',
				'h_msd_ak8_muCR4_N2_fail_muisoUp',
				'h_msd_ak8_muCR4_N2_fail_muisoDown',	
	] 

	for plot in plots:
		print "[debug] On plot " + plot
		tag = plot.split('_')[-1] # 'pass' or 'fail' or systematicName
		if tag not in ['pass', 'fail']:
			tag = plot.split('_')[-2] + '_' +  plot.split('_')[-1] # 'pass_systematicName', 'pass_systmaticName', etc.
		if "muCR" in plot:
			tag += "_muCR"
		hall['%s_%s'%(sample_name,tag)] = getattr(sample,plot)
		hall['%s_%s'%(sample_name,tag)].SetName('%s_%s'%(sample_name,tag))
		if xsec:
			hall['%s_%s'%(sample_name,tag)].Scale(scale1fb)
	output_file.cd()

	for key, h in hall.iteritems():
		h.Write()

	sample.h_Cuts.Write()
	sample.h_CutEvents.Write()

	output_file.Write()
	output_file.Close()

if __name__ == "__main__":
	from argparse import ArgumentParser
	parser = ArgumentParser(description="Run sampleContainer jobs on condor")
	parser.add_argument("--input_files", type=str, help="Comma-separated list of input files")
	parser.add_argument("--sample", type=str, help="Sample name")
	parser.add_argument("--output_file", type=str, help="Output file name")
	parser.add_argument("--lumi", type=float, help="Luminosity for normalization")
	parser.add_argument("--sf", type=float, default=1., help="Manual SF")
	parser.add_argument("--isData", action="store_true", help="This is data")
	parser.add_argument("--fillCA15", action="store_true", help="Do CA15 histograms")
	parser.add_argument("--cutFormula", type=str, default="1", help="Additional cut formula")
	parser.add_argument("--xsec", type=float, help="For samples that did not have scale1fb calculated, specify a cross section [pb] now.")
	parser.add_argument("--tree_name", type=str, default="otree", help="Name of tree in input files (otree or Events)")
	args = parser.parse_args()

	RunSampleContainer(args.sample, args.input_files.split(","), args.output_file, lumi=args.lumi, sf=args.sf, isData=args.isData, fillCA15=args.fillCA15, cutFormula=args.cutFormula, tree_name=args.tree_name)
