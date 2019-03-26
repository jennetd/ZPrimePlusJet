#!/usr/bin/env python

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

def main(options,mode,dryRun):
    ifile = options.ifile
    odir  = options.odir
    cats  = options.cats
    suffix= options.suffix
    pseudo= options.pseudo
    blind = options.blind
    iloose= options.iloose
    muonCR= options.muonCR
    is2017= options.is2017
    nr    = options.nr
    np    = options.np
    
    now = datetime.datetime.now()
    ifileName = ifile.split("/")[-1]
    if odir=="":
        odir = os.path.dirname(ifile) 
        print "using default output dir:", odir
    tfile = r.TFile.Open(ifile)
    logf  = odir +"buildcard.log" 
    outf  = open(logf,"a")
    if not dryRun:
        outf.write("=======buildcard.py==========\n")
        outf.write("===ifile = %s ==========\n"%ifile)
        outf.write("===odir  = %s ==========\n"%odir)
        outf.write("===mode  = %s ==========\n"%mode)
        outf.write("===time  = %s ==========\n"%now.strftime("%Y-%m-%d %H:%M"))
    print "=======buildcard.py=========="
    print "====  ifile   = %s =========="%ifile
    print "====  odir    = %s =========="%odir
    print "====  mode    = %s =========="%mode
    print "====  time    = %s =========="%now.strftime("%Y-%m-%d %H:%M")
    print "====  logfile = %s =========="%logf

    rhalph_base    = "python buildRhalphabetHbb.py -i %s -o %s --nr %i --np %i --remove-unmatched --prefit --addHptShape "%(ifile,odir,nr,np)
    makecard_base  = "python makeCardsHbb.py       -i %s -o %s --remove-unmatched --no-mcstat-shape "%(ifile,odir)
    if muonCR:
        makemuonCR_base = "python writeMuonCRDatacard.py       -i %s -o %s "%(muonCR,odir)
    combcards_base = "combineCards.py "
    if mode =="vbf":
        t2ws_vbf ="text2workspace.py -P HiggsAnalysis.CombinedLimit.PhysicsModel:multiSignalModel -m 125  --PO verbose --PO 'map=.*/hqq125:r[1,0,20]' --PO 'map=.*/vbfhqq125:r_vbf[1,0,20]'"
    t2ws_rz      ="text2workspace.py -P HiggsAnalysis.CombinedLimit.PhysicsModel:multiSignalModel -m 125  --PO verbose --PO 'map=.*/*hqq125:r[1,0,20]' --PO 'map=.*/zqq:r_z[1,0,20]'"
    for cat in cats:
        combcards_base += " %s=%s "%(cat['name'],cat['card'])
    
    if suffix:
        rhalph_base += " --suffix %s"%suffix
        makecard_base += " --suffix %s"%suffix
        combcard_all = "%scard_rhalphabet_all_%s.txt "%(odir,suffix)
        combcards_base += " > %s"%(combcard_all)
        
    else:
        combcard_all = "%scard_rhalphabet_all.txt "%(odir)
        combcards_base += " > %s"%(combcard_all)
    if iloose:
        rhalph_base   += " --ifile-loose %s "%iloose
        makecard_base += " --ifile-loose %s "%iloose
    if pseudo:
        rhalph_base += " --pseudo "
        
    if blind:
        rhalph_base += " --blind "
        makecard_base +=" --blind "
    if is2017:
        rhalph_base += " --is2017 "
        makecard_base +=" --is2017 "
        if muonCR:
            makemuonCR_base +=" --is2017 "
       
    if mode =="vbf":
        t2ws_vbf += " %s -o %s"%(combcard_all, combcard_all.replace(".txt","_floatVBF.root"))
    t2ws_rz += " %s -o %s"%(combcard_all, combcard_all.replace(".txt","_floatZ.root"))
    if options.scaleLumi:
        insert = 'echo -e "lumiscale rateParam * * 1 \\nnuisance edit freeze lumiscale" >> %s'%combcard_all
        t2ws_rz += " --X-nuisance-group-function mcstat 'expr::lumisyst(\"1/sqrt(@0)\",lumiscale[1])' "
    

    cmds = [
       rhalph_base,
       makecard_base,
       combcards_base,
       t2ws_rz
    ]
    if mode =="vbf":
        cmds.append(t2ws_vbf)
    if muonCR:
        cmds.insert(2,makemuonCR_base)
    if options.scaleLumi:
        cmds.insert(3,insert)
    for cmd in cmds:
        exec_me(cmd,outf, dryRun)
    if not dryRun:
        print "=========== Summary ============="
        for cmd in cmds:    print cmd

def buildcats(ifile,odir,muonCR,suffix):
    #get N ptbins
    tf = r.TFile(ifile)
    ncats=tf.Get("qcd_pass").GetYaxis().GetNbins()
    cats=[]
    for icat in range(1,ncats+1):
        cats.append( {"name":"cat%s"%icat,"card":odir+"card_rhalphabet_cat%s.txt"%icat})
    if muonCR:
        cats.append({"name":"muonCR","card":odir+"datacard_muonCR.txt"})
    if suffix:
        for catdict in cats:
            catdict['name'] = catdict['name']+"_"+suffix
    return cats

def VBFddb(options):
    dryRun = options.dryRun
    options.pseudo = True 
    options.is2017 = True
    mode = 'vbf'
    options.suffix = "ggF"
    options.blind  = ""
    options.muonCR = "" 
    options.iloose = ""
    #options.odir  ="./ddb_VBF/4cats/vbf/mcOnly/"
    #options.ifile= "./ddb_VBF/4cats/vbf/data/hist_1DZbb_pt_scalesmear.root"
    options.odir  ="./ddb_VBF/6cats/ggF/mcOnly/"
    options.ifile= "./ddb_VBF/6cats/ggF/data/hist_1DZbb_pt_scalesmear.root"
    options.cats = buildcats(options.ifile,options.odir,options.muonCR,options.suffix)
    main(options, mode,dryRun)

def QGmain(options):
    dryRun = options.dryRun
    pseudo = True 
    mode = 'vbf'
    suffix = "QGgluon"
    blind  = ""
    muonCR = "" 
    iloose = ""
    odir ="./QG/QGgluon/fixMCstat/"
    ifile= "./QG/QGgluon/hist_1DZbb_pt_scalesmear.root"
    QGgluon_cats = [    
       {"name":"cat1_QGgluon","card":odir+"card_rhalphabet_cat1.txt"},       {"name":"cat2_QGgluon","card":odir+"card_rhalphabet_cat2.txt"},
       {"name":"cat3_QGgluon","card":odir+"card_rhalphabet_cat3.txt"},       {"name":"cat4_QGgluon","card":odir+"card_rhalphabet_cat4.txt"},
       {"name":"cat5_QGgluon","card":odir+"card_rhalphabet_cat5.txt"},       {"name":"cat6_QGgluon","card":odir+"card_rhalphabet_cat6.txt"},
    ]
    #main(ifile,odir,QGgluon_cats,suffix,pseudo,blind,iloose,muonCR,mode,dryRun)
    odir ="./QG/QGquark/fixMCstat/"
    ifile= "./QG/QGquark/hist_1DZbb_pt_scalesmear.root"
    suffix = "QGquark"
    QGquark_cats = [    
       {"name":"cat1_QGquark","card":odir+"card_rhalphabet_cat1.txt"},       {"name":"cat2_QGquark","card":odir+"card_rhalphabet_cat2.txt"},
       {"name":"cat3_QGquark","card":odir+"card_rhalphabet_cat3.txt"},       {"name":"cat4_QGquark","card":odir+"card_rhalphabet_cat4.txt"},
       {"name":"cat5_QGquark","card":odir+"card_rhalphabet_cat5.txt"},       {"name":"cat6_QGquark","card":odir+"card_rhalphabet_cat6.txt"}   
    ]
    #main(ifile,odir,QGquark_cats,suffix,pseudo,blind,iloose,muonCR,mode,dryRun)
   
    suffix = ""
    odir ="./QG/topR6/fixMCstat/"
    ifile= "./QG/topR6/hist_1DZbb_pt_scalesmear.root"
    normcats = [    
       {"name":"cat1","card":odir+"card_rhalphabet_cat1.txt"},       {"name":"cat2","card":odir+"card_rhalphabet_cat2.txt"},
       {"name":"cat3","card":odir+"card_rhalphabet_cat3.txt"},       {"name":"cat4","card":odir+"card_rhalphabet_cat4.txt"},
       {"name":"cat5","card":odir+"card_rhalphabet_cat5.txt"},       {"name":"cat6","card":odir+"card_rhalphabet_cat6.txt"},
    ]
    #main(ifile,odir,normcats,suffix,pseudo,blind,iloose,muonCR,"vbf",dryRun)
    #combine cards
    suffix ="QGcomb"
    #main(ifile,odir,QGquark_cats+QGgluon_cats,suffix,pseudo,blind,iloose,muonCR,"vbf",True)

def TriggerMain(options):
    dryRun = options.dryRun
    mode   = 'norm'
    suffix = ""
    blind  = ""
    pseudo = True
    idir  = "trigger/BtoF_noPS/"
    odir  = "trigger/BtoF_noPS/mcOnly/"
    ifile  = idir+"data/hist_1DZbb_pt_scalesmear.root"
    muonCR = idir+"muonCR/hist_1DZbb_muonCR.root" 
    iloose = idir+"looserWZ/hist_1DZbb_pt_scalesmear_looserWZ.root"

    normcats = [    
       {"name":"cat1","card":odir+"card_rhalphabet_cat1.txt"},       {"name":"cat2","card":odir+"card_rhalphabet_cat2.txt"},
       {"name":"cat3","card":odir+"card_rhalphabet_cat3.txt"},       {"name":"cat4","card":odir+"card_rhalphabet_cat4.txt"},
       {"name":"cat5","card":odir+"card_rhalphabet_cat5.txt"},       {"name":"cat6","card":odir+"card_rhalphabet_cat6.txt"},
       {"name":"muonCR","card":odir+"datacard_muonCR.txt"}
    ]
    main(ifile,odir,normcats,suffix,pseudo,blind,iloose,muonCR,mode,dryRun)

def secJetMain(options):
    dryRun = options.dryRun
    mode   = 'norm'
    suffix = "secJet"
    blind  = ""
    pseudo = True
    idir  = "2ndjet/powheg/"
    odir  = "2ndjet/powheg/mcOnly/"
    ifile  = idir+"data/hist_1DZbb_pt_scalesmear.root"
    muonCR = "2ndjet/leading_pow/muonCR/hist_1DZbb_muonCR.root"
    iloose = idir+"looserWZ/hist_1DZbb_pt_scalesmear_looserWZ.root"
    options.nr     = 2
    options.np     = 1

    secJet = buildcats(options.ifile,odir,muonCR,suffix)
    #main(ifile,odir,secJet,suffix,pseudo,blind,iloose,muonCR,mode,dryRun)
    #leading jet
    suffix = "leadJet"
    idir  = "2ndjet/leading_pow/"
    odir  = "2ndjet/leading_pow/mcOnly/"
    ifile  = idir+"data/hist_1DZbb_pt_scalesmear.root"
    muonCR = "2ndjet/leading_pow/muonCR/hist_1DZbb_muonCR.root"
    iloose = idir+"looserWZ/hist_1DZbb_pt_scalesmear_looserWZ.root"
    
    leading_cats = buildcats(options.ifile,odir,muonCR,suffix)
    #main(ifile,odir,leading_cats,suffix,pseudo,blind,iloose,muonCR,mode,dryRun)
    suffix ="12comb"
    main(ifile,odir,secJet+leading_cats,suffix,pseudo,blind,iloose,muonCR,"norm",True)

def DB_MC_main(options):
    dryRun = options.dryRun
    mode   = 'norm'
    options.suffix = ""
    options.blind  = ""
    options.pseudo = True
    options.is2017 = False 
    options.scaleLumi = False
    options.nr     = 2
    options.np     = 1
    options.idir  = "db_Mar7/"  #fix JEC/JER ,default pT1200 
    options.odir  = "db_Mar7/TF21_sf2016/"
    options.ifile  = options.idir+"data/hist_1DZbb_pt_scalesmear.root"
    #options.muonCR = options.idir+"/muonCR/hist_1DZbb_muonCR.root"
    options.muonCR = "" 
    options.iloose = ""
    options.cats = buildcats(options.ifile,options.odir,options.muonCR,options.suffix)
    main(options, mode,dryRun)


def DDB_MC_main(options):
    dryRun = options.dryRun
    mode   = 'norm'
    options.suffix = ""
    options.blind  = ""
    options.pseudo = True
    options.is2017 = True
    options.scaleLumi = False
    options.nr     = 4 
    options.np     = 1
    options.idir  = "ddb_dec31/MC/" #first ddb
    options.idir  = "ddb_Jan17/MC/" #fix QCD xsec
    options.idir  = "ddb_Jan31/MC/" #dbtag >0.88
    options.idir  = "ddb_Feb5/MC/"  #ttbar rejection round1
    options.idir  = "ddb_Mar7/ddb_M2/"  #fix JEC/JER ,default pT1200 
    options.idir  = "ddb_Mar19/ddb_M2/"  #fix delta-phi 
    options.idir  = "matching/ddb_M2/"  #fix delta-phi 
    options.ifile  = options.idir+"data/hist_1DZbb_pt_scalesmear.root"
    #options.muonCR = options.idir+"/muonCR/hist_1DZbb_muonCR.root"
    options.muonCR = "" 
    #options.iloose = options.idir+"/looserWZ/hist_1DZbb_pt_scalesmear.root"
    options.iloose = ""
    options.odir  = "matching/ddb_M2/msd47_TF21/"

    options.cats = buildcats(options.ifile,options.odir,options.muonCR,options.suffix)
    main(options, mode,dryRun)
    #other WPs:
    #for idir in ['ddb_L_tw1/','ddb_M2_tw1/']:
    #for idir in ['ddb_L/','ddb_M/','ddb_M2/','ddb_T/','ddb_T2/']:
    #for idir in ['ddb_L_pt1200/','ddb_M2_pt1200/','ddb_T2_pt1200/']:
    for idir in ['ddb_M2/']:
        options.nr     = 2
        options.np     = 1
        options.idir = "ddb_Mar7/"+idir
        options.odir = "ddb_Mar7/"+idir+'msd54_TF21_rescaled/'
        options.iloose=''
        options.ifile  = options.idir+"data/hist_1DZbb_pt_scalesmear.root"
        options.muonCR = ""  
        #options.cats = buildcats(options.ifile,options.odir,options.muonCR,options.suffix)
        #main(options, mode,dryRun)
        pass

def DDB_10p_main(options):
    dryRun = options.dryRun
    mode   = 'norm'
    options.suffix = ""
    options.blind  = False 
    options.pseudo = False 
    options.is2017 = True
    #options.idir  = "ddb_Jan9_10p/"
    #options.odir  = "ddb_Jan9_10p/10p_blind/"
    #options.idir  = "ddb_Jan17/10p_blind/"
    #ptions.odir  = "ddb_Jan17/10p_blind/10p_blind_muonCR/"
    options.idir  = "ddb_Mar19/ddb_M2_p10/"
    options.odir  = "ddb_Mar19/ddb_M2_p10/msd47_TF21_x10/"
    options.ifile  = options.idir+"data/hist_1DZbb_pt_scalesmear.root"
    #options.muonCR = options.idir+"muonCR/hist_1DZbb_muonCR.root"
    options.muonCR = ""
    options.iloose = ""
    options.nr     = 2
    options.np     = 1
    options.scaleLumi = True

    options.cats = buildcats(options.ifile,options.odir,options.muonCR,options.suffix)
    main(options, mode,dryRun)

 
##-------------------------------------------------------------------------------------
if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option('-i', dest='ifile', default='card_rhalphabet_muonCR_floatZ.root', help='datacard root')
    parser.add_option('-o','--odir', dest='odir', default = '',help='directory to write cards', metavar='odir')
    parser.add_option('-m','--mode', dest='mode', default = 'norm',help='setting of pams', metavar='mode')
    parser.add_option('--dryRun', dest='dryRun', action='store_true',default=False,help='dryRun', metavar='dryRun')

    (options, args) = parser.parse_args()

    ############# QG###########
    #QGmain(options)
    ############# Trigger###########
    #TriggerMain(options)
    ############# 2nd jet ###########
    #secJetMain(options)
    ############# DDB jet ###########
    #DDB_MC_main(options)
    #DB_MC_main(options)
    DDB_10p_main(options)

    #VBFddb(options)
