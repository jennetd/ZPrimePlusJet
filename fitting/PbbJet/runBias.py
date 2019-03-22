import ROOT as r,sys,math,os
from ROOT import TFile, TTree, TChain, gPad, gDirectory
from multiprocessing import Process
from optparse import OptionParser
from operator import add
import math
import sys
import time
import array

def exec_me(command, dryRun=False):
    print command
    if not dryRun:
        os.system(command)
        
if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option('-m','--mass'   ,action='store',type='int',dest='mass'   ,default=125, help='mass')
    parser.add_option('-d','--datacard'   ,action='store',type='string',dest='datacard'   ,default='card_rhalphabet.txt', help='datacard name')
    parser.add_option('--datacard-alt'   ,action='store',type='string',dest='datacardAlt'   ,default='card_rhalphabet_alt.txt', help='alternative datacard name')
    parser.add_option('-l','--lumi'   ,action='store',type='float',dest='lumi'   ,default=36.4, help='lumi')
    parser.add_option('--scaleLumi'   ,action='store',type='float',dest='scaleLumi'   ,default=-1, help='scale nuisances by scaleLumi')
    parser.add_option('-t','--toys'   ,action='store',type='int',dest='toys'   ,default=200, help='number of toys')
    parser.add_option('-s','--seed'   ,action='store',type='int',dest='seed'   ,default=-1, help='random seed')
    parser.add_option('-r','--r',dest='r', default=1 ,type='float',help='default value of r')    
    parser.add_option('--just-plot', action='store_true', dest='justPlot', default=False, help='just plot')
    parser.add_option('--freezeNuisances'   ,action='store',type='string',dest='freezeNuisances'   ,default='None', help='freeze nuisances')
    parser.add_option('--dryRun',dest="dryRun",default=False,action='store_true',
                  help="Just print out commands to run")    
    parser.add_option('-o', '--odir', dest='odir', default='./', help='directory to write plots', metavar='odir')

    (options,args) = parser.parse_args()


    if options.datacard == options.datacardAlt or options.datacardAlt == parser.get_option("--datacard-alt").default:
        if options.datacardAlt == parser.get_option("--datacard-alt").default:
            options.datacardAlt = options.datacard
            print "Using same datacard as alternative by default: ", options.datacardAlt
        toysDir= '%s/bias_self_r%i'%(options.odir,options.r)
        exec_me('mkdir -p %s'%(toysDir),options.dryRun)

    if not options.justPlot:    
        limit_cmd = 'python limit.py -M Bias --datacard %s --datacard-alt %s -o %s '%(options.datacard,options.datacardAlt,toysDir)
        limit_cmd +=' -t %i --lumi %f -r %f --seed %s --freezeNuisances %s ' %(options.toys, options.lumi,  options.r, options.seed, options.freezeNuisances)
        limit_cmd +=' --scaleLumi %f ' %options.scaleLumi
        exec_me(limit_cmd,options.dryRun)
    else:
        # use toys from hadd-ed directory
        limit_cmd = 'python limit.py -M Bias --datacard %s --datacard-alt %s -o %s '%(options.datacard,options.datacardAlt,toysDir)
        limit_cmd +=' -t %i --lumi %f -r %f --seed %s --freezeNuisances %s ' %(options.toys, options.lumi,  options.r, options.seed, options.freezeNuisances)
        exec_me(limit_cmd+" --just-plot ",options.dryRun)
