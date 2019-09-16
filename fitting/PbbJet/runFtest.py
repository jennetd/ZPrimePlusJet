import ROOT as r,sys,math,os
from ROOT import TFile, TTree, TChain, gPad, gDirectory
from buildRhalphabetHbb import SF2018,SF2017,SF2016
from multiprocessing import Process
from optparse import OptionParser
from operator import add
import math
import sys
import time
import array


def exec_me(command, outf, dryRun=False):
    print command
    outf.write("%s\n"%command)
    if not dryRun:
        os.system(command)

def buildcats(ifile,odir,muonCR,suffix):
    #get N ptbins
    tf = r.TFile(ifile)
    ncats=tf.Get("data_obs_pass").GetYaxis().GetNbins()
    cats=[]
    for icat in range(1,ncats+1):
        cats.append( {"name":"cat%s"%icat,"card":odir+"card_rhalphabet_cat%s.txt"%icat})
    if muonCR:
        cats.append({"name":"muonCR","card":odir+"datacard_muonCR.txt"})
    if suffix:
        for catdict in cats:
            catdict['name'] = catdict['name']+"_"+suffix
    return cats


def buildcards(odir,nr,np, options):
    ifile = options.ifile
    dryRun= options.dryRun
    if hasattr(options,'suffix'): suffix= options.suffix
    else:                         suffix=''
    if hasattr(options,'pseudo'): pseudo= options.pseudo
    else:                         pseudo=''
    if hasattr(options,'blind'): blind = options.blind
    else:                         blind = True
    if hasattr(options,'ifile_loose'): iloose= options.ifile_loose
    else:                         iloose=''
    if hasattr(options,'ifile_muon'): muonCR= options.ifile_muon
    else:                         muonCR=''
    if hasattr(options,'year'): year  = options.year
    else:                         year  =''
    if hasattr(options,'exp'): exp  = options.exp
    else:                         exp  = False
    if hasattr(options,'pseudoPass'): pseudoPass  = options.pseudoPass
    else:                         pseudoPass  = False
    if hasattr(options,'MiNLO'): MiNLO = options.MiNLO
    else:                        MiNLO = False
    if hasattr(options,'qcdTF'): qcdTF = options.qcdTF
    else:                        qcdTF = False
    if   year=='2018':   SF = SF2018
    elif year=='2017':   SF = SF2017
    elif year=='2016':   SF = SF2016
    else:                SF = {}

    
    ifileName = ifile.split("/")[-1]
    if odir=="":
        odir = os.path.dirname(ifile) 
        print "using default output dir:", odir
    rhalph_base    = "python buildRhalphabetHbb.py -i %s -o %s --nr %i --np %i --remove-unmatched --prefit "%(ifile,odir,nr,np)
    makecard_base  = "python makeCardsHbb.py       -i %s -o %s                 --remove-unmatched --no-mcstat-shape "%(ifile,odir)
    if muonCR:
        makemuonCR_base = "python writeMuonCRDatacard.py       -i %s -o %s --no-mcstat-shape "%(muonCR,odir)
    combcards_base = "combineCards.py "
    t2ws_rz      ="text2workspace.py -P HiggsAnalysis.CombinedLimit.PhysicsModel:multiSignalModel -m 125  --PO verbose --PO 'map=.*/*_hbb:r[1,0,20]' --PO 'map=.*/zqq:r_z[1,0,20]'"

    #construct {catX_suffix:card_rhalphabet_cat%s.txt}
    cats = buildcats(ifile,odir,muonCR,suffix)
    for cat in cats:
        combcards_base += " %s=%s "%(cat['name'],cat['card'])
    
    if not MiNLO:
        rhalph_base += " --addHptShape"
        makecard_base += " --addHptShape"

    if suffix:
        rhalph_base += " --suffix %s"%suffix
        makecard_base += " --suffix %s"%suffix
        makemuonCR_base += " --suffix %s"%suffix
        combcard_all = "%scard_rhalphabet_all_%s_r%ip%i.txt "%(odir,suffix,nr,np)
        combcards_base += " > %s"%(combcard_all)
    else:
        combcard_all = "%scard_rhalphabet_all_r%ip%i.txt "%(odir,nr,np)
        combcards_base += " > %s"%(combcard_all)
    if iloose:
        rhalph_base   += " --ifile-loose %s "%iloose
        makecard_base += " --ifile-loose %s "%iloose
    if pseudo:
        rhalph_base += " --pseudo "
    if exp:
        rhalph_base += " --exp "
    if blind:
        rhalph_base += " --blind "
        makecard_base +=" --blind "
    #if is2017:
    #    rhalph_base += " --is2017 "
    #    makecard_base +=" --is2017 "
    #    if muonCR:
    #        makemuonCR_base+=" --is2017 "
    if year:
        rhalph_base   +=" --year %s "%year
        makecard_base +=" --year %s "%year
        if muonCR:
            makemuonCR_base +=" --year %s "%year
    if qcdTF: 
        makecard_base +=" --addqcdCovMat "


    wsRoot = combcard_all.replace(".txt","_floatZ.root")       
    t2ws_rz += " %s -o %s"%(combcard_all, wsRoot)

    cmds = [
       rhalph_base,
       makecard_base,
       combcards_base,
       t2ws_rz
    ]
    if muonCR:
        cmds.insert(2,makemuonCR_base)
    if options.justPlot:
        return wsRoot
    for cmd in cmds:
        exec_me(cmd,logf, dryRun)
    
    #return name of root file product
    return wsRoot
        
if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option('-m','--mass'   ,action='store',type='int',dest='mass'   ,default=125, help='mass')
    parser.add_option('--nr1','--NR1' ,action='store',type='int',dest='NR1'   ,default=1, help='order of rho polynomial for model 1')
    parser.add_option('--np1','--NP1' ,action='store',type='int',dest='NP1'   ,default=1, help='order of pt polynomial for model 1')
    parser.add_option('--nr2','--NR2' ,action='store',type='int',dest='NR2'   ,default=2, help='order of rho polynomial for model 2')
    parser.add_option('--np2','--NP2' ,action='store',type='int',dest='NP2'   ,default=1, help='order of pt polynomial for model 2')
    parser.add_option('--scale',dest='scale', default=1,type='float',help='scale factor to scale MC (assuming only using a fraction of the data)')
    parser.add_option('-l','--lumi'   ,action='store',type='float',dest='lumi'   ,default=36.4, help='lumi')
    parser.add_option('-i','--ifile', dest='ifile', default = 'hist_1DZbb.root',help='file with histogram inputs', metavar='ifile')
    parser.add_option('--ifile-loose', dest='ifile_loose', default=None, help='second file with histogram inputs (looser b-tag cut to take W/Z/H templates)',
                      metavar='ifile_loose')
    parser.add_option('--suffix', dest='suffix', default=None, help='suffix for conflict variables',metavar='suffix')
    parser.add_option('--ifile-muon', dest='ifile_muon', default=None, help='path to muonCR templates ',metavar='ifile_muon')
    parser.add_option('-t','--toys'   ,action='store',type='int',dest='toys'   ,default=200, help='number of toys')
    parser.add_option('-s','--seed'   ,action='store',type='int',dest='seed'   ,default=-1, help='random seed')
    parser.add_option('-r','--r',dest='r', default=1 ,type='float',help='default value of r')    
    parser.add_option('-n','--n' ,action='store',type='int',dest='n'   ,default=5*20, help='number of bins')
    parser.add_option('--just-plot', action='store_true', dest='justPlot', default=False, help='just plot')
    parser.add_option('--pseudo', action='store_true', dest='pseudo', default=False, help='run on asimov dataset')
    parser.add_option('-y' ,'--year', type='choice', dest='year', default ='2016',choices=['2016','2017','2018'],help='switch to use different year ', metavar='year')
    parser.add_option('--blind', action='store_true', dest='blind', default=False, help='run on blinded dataset')
    parser.add_option('--qcdTF', action='store_true', dest='qcdTF', default=False, help='switch to make qcdTF cards')
    parser.add_option('--qcdfitdir', dest='qcdfitdir', default='./', help='dir to look for qcdTF cards')
    parser.add_option('--exp', action='store_true', dest='exp', default=False, help='use exp(bernstein poly) transfer function',metavar='exp')
    parser.add_option('--freezeNuisances'   ,action='store',type='string',dest='freezeNuisances'   ,default='None', help='freeze nuisances')
    parser.add_option('--dryRun',dest="dryRun",default=False,action='store_true',
                  help="Just print out commands to run")    
    parser.add_option('-o', '--odir', dest='odir', default='./', help='directory to write plots', metavar='odir')


    (options,args) = parser.parse_args()

    logf  = open(options.ifile.replace(".root","_report.txt"),"w")
    logf.write("=======runFtest.py==========\n")
    logf.write("===ifile = %s ==========\n"%options.ifile)
    logf.write("===odir  = %s ==========\n"%options.odir)
    print "=======runFtest.py=========="
    print "===ifile = %s =========="%options.ifile
    print "===odir  = %s =========="%options.odir


    if options.pseudo:
        cardsDir1 = '%s/cards_mc_r%ip%i/'%(options.odir,options.NR1,options.NP1)
        cardsDir2 = '%s/cards_mc_r%ip%i/'%(options.odir,options.NR2,options.NP2)
    else:        
        cardsDir1 = '%s/cards_r%ip%i/'%(options.odir,options.NR1,options.NP1)
        cardsDir2 = '%s/cards_r%ip%i/'%(options.odir,options.NR2,options.NP2)
    
    toysDir = "%s/ftest_r%ip%i_r%ip%i_muonCR"%(options.odir,options.NR1,options.NP1,options.NR2,options.NP2)
    
    if not options.justPlot: 
        exec_me('mkdir -p %s'%options.odir,logf,options.dryRun)
        exec_me('mkdir -p %s'%(toysDir),logf,options.dryRun)
        exec_me('mkdir -p %s'%cardsDir1,logf,options.dryRun)
        exec_me('mkdir -p %s'%cardsDir2,logf,options.dryRun)
        datacardWS1 = buildcards(cardsDir1,options.NR1, options.NP1,options)
        datacardWS2 = buildcards(cardsDir2,options.NR2, options.NP2,options)
    else:
        datacardWS1 = buildcards(cardsDir1,options.NR1, options.NP1,options)
        datacardWS2 = buildcards(cardsDir2,options.NR2, options.NP2,options)

    p_sig = 2
    if 'r'  in options.freezeNuisances.split(","):   p_sig -=1
    if 'r_z'in options.freezeNuisances.split(","):   p_sig -=1 
    p1 = int((options.NR1+1)*(options.NP1+1)) + p_sig # paramaters including floating Hbb and Zbb signals
    p2 = int((options.NR2+1)*(options.NP2+1)) + p_sig # parameters including floating Hbb and Zbb signals
    

    dataString = ''
    if not options.pseudo:
        dataString = '--data'

    if not options.justPlot:    
        limit_cmd = 'python limit.py -M FTest --datacard %s --datacard-alt %s -o %s -n %i --p1 %i --p2 %i -t %i --lumi %f %s -r %f --seed %s --freezeNuisances %s '%(datacardWS1,datacardWS2,toysDir, options.n, p1, p2, options.toys, options.lumi, dataString, options.r, options.seed, options.freezeNuisances)
        exec_me(limit_cmd,logf,options.dryRun)
    else:
        # use toys from hadd-ed directory
        toysDir +="/toys/ "
        limit_cmd = 'python limit.py -M FTest --datacard %s --datacard-alt %s -o %s -n %i --p1 %i --p2 %i -t %i --lumi %f %s -r %f --seed %s --freezeNuisances %s '%(datacardWS1,datacardWS2,toysDir, options.n, p1, p2, options.toys, options.lumi, dataString, options.r, options.seed, options.freezeNuisances)
        exec_me(limit_cmd+" --just-plot ",logf,options.dryRun)
