#!/usr/bi#n/env python
         #
import ROOT as r,sys,math,array,os
from optparse import OptionParser
from operator import add
import math
import sys,os
import datetime

# including other directories
sys.path.insert(0, '../.')
from tools import *

##-------------------------------------------------------------------------------------
def exec_me(command, outf, dryRun=False):
    print command
    if not dryRun:
        outf.write("%s\n"%command)
        os.system(command)

def main(options,dryRun):
    idir    = options.idir
    ifile    = options.ifile
    ifileMuon= options.ifileMuon
    odir     = options.odir
    blind = options.blind
    year  = options.year
    pseudo = options.pseudo
    nr1    = options.nr1
    np1    = options.np1
    nr2    = options.nr2
    np2    = options.np2
    ntoys  = options.ntoys
    hadd   = options.hadd
    exp    = options.exp
    if 'MiNLO' in idir:
        MiNLO = True
    #qcdfitdir    = options.qcdfitdir
    if hasattr(options,'freezeNuisances'):
        freezeNuisances = options.freezeNuisances
    setParameters = options.setParameters
    
    now = datetime.datetime.now()
    ifileName = ifile.split("/")[-1]
    if odir=="":
        #odir = os.path.dirname(idir)+'/ftest_floatrz/' 
        odir = os.path.dirname(idir)+'/ftest_blind_rz_t400/' 
        #odir = os.path.dirname(idir)+'/ftest_unblinded_t400/' 
        #odir = os.path.dirname(idir)+'/ftest_qcdTF21uncV5/' 
        #odir = os.path.dirname(idir)+'/ftest_MC/' 
        print "using default output dir:", odir
    tfile = r.TFile.Open(ifile)
    
    if not os.path.exists(odir):
       print 'mkdir -p %s'%(odir)
       os.system('mkdir -p %s'%(odir))
    logf  = odir +"ftest.log" 
    outf  = open(logf,"a")
    if not dryRun:
        outf.write("=======ftest.py==========\n")
        outf.write("===ifile = %s ==========\n"%ifile)
        outf.write("===odir  = %s ==========\n"%odir)
        outf.write("===time  = %s ==========\n"%now.strftime("%Y-%m-%d %H:%M"))
    print "=======ftest.py=========="
    print "====  ifile   = %s =========="%ifile
    print "====  odir    = %s =========="%odir
    print "====  time    = %s =========="%now.strftime("%Y-%m-%d %H:%M")
    print "====  logfile = %s =========="%logf

    toysdir = odir + "ftest_r%sp%s_r%sp%s_muonCR/toys/"%(nr1,np1,nr2,np2)

    ftest_base    = "python submitJob_Ftest.py -i %s "%(ifile)
    if ifileMuon:
        ftest_base+= ' --ifile-muon %s'% ifileMuon
    if hasattr(options,'ifileLoose') and options.ifileLoose:
        ftest_base+= ' --ifile-loose %s '% options.ifileLoose
    ftest_base    += " -o %s " % toysdir
    ftest_base    += " --nr1 %s --np1 %s --nr2 %s --np2 %s  "%(nr1,np1,nr2,np2)
    #ftest_base    += " -r 1  -t %s "%ntoys
    ftest_base    += "  -t %s "%ntoys
    if blind:
        ftest_base += ' --blind '
    if MiNLO:
        ftest_base += ' --MiNLO '
    if exp:
        ftest_base += ' --exp '
    if pseudo:
        ftest_base += ' --pseudo '
    if hasattr(options,'freezeNuisances') and freezeNuisances:
        ftest_base += ' --freezeNuisances %s '%freezeNuisances
    if setParameters:
        ftest_base += ' --setParameters %s '%setParameters
    if hasattr(options,'qcdTF') and options.qcdTF:
        ftest_base += ' --qcdTF '
    if year:
        ftest_base += ' --year %s '%year
        ftest_base += ' --suffix %s '%year
    if hadd:
        ftest_base += ' --hadd --clean'
   
    ###counting dof:
    # n = 23(mass bins) * 6 (pt cats) - 8(removing rho) + 23(muonCR,ptbin summed) =153
    # n = 23(mass bins) * 6 (pt cats) - 8(removing rho)                           =130
    # n = 23(mass bins) * 6 (pt cats) - 8(removing rho) - msd47*6cat              =124
    # n = 23(mass bins) * 6 (pt cats) - 8(removing rho) - (msd47+3xblind)*6cat    =106    [blinded without muonCR]
    # n = 22(mass bins) * 6 (pt cats) - 8(removing rho) - (3xblind)*6cat+23muonCR =129    [blinded with muonCR] 
    # VBF n 
    # n = 22(mass bins) * 3 (pt cats) - 7(removing rho) - (3xblind)*3cat          =50    [blinded with muonCR] 

    # baseline signal region bins
    n = 22*6 -8
    #n = 22*3 -7
    #if blind    :  n -= 3*3
    if blind    :  n -= 6*3
    #if ifileMuon:  n += 23
    #if ifileMuon:  n += 1
    ftest_base += ' -n %s '%n
    ftest_base += ' --lumi  %s '%options.lumi
    

    cmds = [
        ftest_base
    ]
    for cmd in cmds:
        exec_me(cmd,outf, dryRun)
    if not dryRun:
        print "=========== Summary ============="
        for cmd in cmds:    print cmd


def data2016(options):

    #options.idir = 'ddb2016_Apr28/ddb_M2/'
    #options.idir = 'ddb2016_May21_v2/ddb_M2/'
    #options.idir = 'ddb2016_May28_v2/ddb_M2/'
    #options.idir = 'ddb2016_Jun24_v3/ddb_M2_full/'
    options.idir = 'ddb2016_Jun24_MiNLO_v2/ddb_M2_full/'

    options.ifile     = options.idir + 'data/hist_1DZbb_pt_scalesmear.root'
    options.ifileMuon = options.idir + 'muonCR/hist_1DZbb_muonCR.root'
    options.ifileLoose = options.idir + 'looserWZ_p80/hist_1DZbb_pt_scalesmear_looserWZ.root'

    options.year = '2016'
    options.ntoys = 400
    options.lumi  = '35.9'
    options.exp    = False

    
    for i,point in enumerate(points):
        (options.nr1,options.np1, options.nr2,options.np2) = point
        main(options,options.dryRun)


def data2017(options):
    #options.idir = 'ddb_VBF_May15/vbf_mc/'
    #options.idir = 'ddb_VBF_May15/ggf_mc/'
    #options.idir = 'ddb_Jun24_v2/ddb_M2_full/'
    options.idir = 'ddb_Jun24_MiNLO/ddb_M2_full/'
    options.ifile     = options.idir + 'data/hist_1DZbb_pt_scalesmear.root'
    options.ifileMuon = options.idir + 'muonCR/hist_1DZbb_muonCR.root'
    options.ifileLoose = '' 
    options.year = '2017'
    options.ntoys = 400
    options.lumi  = '41.1'
    
    for i,point in enumerate(points):
        (options.nr1,options.np1, options.nr2,options.np2) = point
        main(options,options.dryRun)

def data2018(options):

    #options.idir = 'ddb2018_Apr17/ddb_M2/'
    #options.idir = 'ddb2018_Jun24_v3/ddb_M2_full/'
    options.idir = 'ddb2018_Jun24_MiNLO/ddb_M2_full/'
    options.ifile     = options.idir + 'data/hist_1DZbb_pt_scalesmear.root'
    options.ifileMuon = options.idir + 'muonCR/hist_1DZbb_muonCR.root'
    options.ifileLoose = ''
    options.year = '2018'
    options.ntoys = 400
    options.lumi  = '59.2'
   
    #### MC points 
    for i,point in enumerate(points):
        (options.nr1,options.np1, options.nr2,options.np2) = point
        main(options,options.dryRun)
 
##-------------------------------------------------------------------------------------
if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option('-i', dest='ifile', default='card_rhalphabet_muonCR_floatZ.root', help='datacard root')
    parser.add_option('-o','--odir', dest='odir', default = '',help='directory to write cards', metavar='odir')
    parser.add_option('--dryRun', dest='dryRun', action='store_true',default=False,help='dryRun', metavar='dryRun')
    parser.add_option('--hadd', dest='hadd', action='store_true',default=False,help='hadd', metavar='hadd')

    (options, args) = parser.parse_args()
    options.qcdTF =  True
    options.exp    = False
    options.pseudo = False 
    options.blind  = True
    #options.blind  = False
    options.freezeNuisances = 'r'
    options.setParameters   = 'r_z=1,r=0'
    #options.setParameters   = 'r_z=1,r=1'

    points = [
        (1,1,2,1),      #(1,1) v (2,1) etc
        (1,1,1,2),
        (1,2,2,2),      # 1,2
        (1,2,1,3),     
        (2,1,2,2),      # 2,1
        (2,1,3,1),     
        (2,2,2,3),      # 2,2
        (2,2,3,2), 
        #(3,1,3,2),      # 3,1
        #(3,1,4,1),    
        #(3,2,3,3),      # 3,2
        #(3,2,4,2),    
        #(4,1,4,2),      # 4,1
        #(4,1,5,1),    
    ] 

    ############# QG###########
    data2016(options)
    data2018(options)
    data2017(options)
