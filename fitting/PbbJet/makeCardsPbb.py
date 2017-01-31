#!/usr/bin/env python

import ROOT as r,sys,math,array,os
from ROOT import TFile, TTree, TChain, gPad, gDirectory
from multiprocessing import Process
from optparse import OptionParser
from operator import add
import math
import sys
import time
import array

# including other directories
sys.path.insert(0, '.')
sys.path.insert(0, '../.')
from tools import *


##-------------------------------------------------------------------------------------
def main(options,args):
	lines = []
	for line in open("datacardPbb.tpl"):
		lines.append(line.strip())
	for signal_mass in [50,75,125,100,150,250,300]:
		#dctpl[signal_mass] = open("datacardPbb.tpl")
		#dctpl[signal_mass].seek(0)
		numberOfMassBins = 23;

		for i in range(1,5+1):

			tag = "cat" + str(i)
			dctmp = open(options.odir+"/card_rhalphabet_%s_M%i.txt" % (tag, signal_mass), 'w')
			for line in lines:
				line = line.strip().replace("CATX", tag).replace("CATY", str(signal_mass))
				dctmp.write(line + "\n");
			for mass_bin in range(numberOfMassBins):
				dctmp.write("qcd_fail_%s_Bin%i flatParam \n" % (tag, mass_bin+1))
			dctmp.close()
		#dctpl[signal_mass].close()


###############################################################


	
##-------------------------------------------------------------------------------------
if __name__ == '__main__':
	parser = OptionParser()
	parser.add_option('-b', action='store_true', dest='noX', default=False, help='no X11 windows')
	parser.add_option("--lumi", dest="lumi", type=float, default = 30,help="luminosity", metavar="lumi")
	parser.add_option('-i','--idir', dest='idir', default = 'data/',help='directory with data', metavar='idir')
	parser.add_option('-o','--odir', dest='odir', default = 'cards/',help='directory to write cards', metavar='odir')
	parser.add_option('--pseudo', action='store_true', dest='pseudo', default =False,help='signal comparison', metavar='isData')

	(options, args) = parser.parse_args()

	import tdrstyle
	tdrstyle.setTDRStyle()
	r.gStyle.SetPadTopMargin(0.10)
	r.gStyle.SetPadLeftMargin(0.16)
	r.gStyle.SetPadRightMargin(0.10)
	r.gStyle.SetPalette(1)
	r.gStyle.SetPaintTextFormat("1.1f")
	r.gStyle.SetOptFit(0000)
	r.gROOT.SetBatch()
	
	main(options,args)
##-------------------------------------------------------------------------------------
