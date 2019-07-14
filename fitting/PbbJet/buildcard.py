#!/usr/bin/env python

import ROOT as r,sys,math,array,os
from optparse import OptionParser
from operator import add
import math
import sys,os,re
import datetime

# including other directories
sys.path.insert(0, '../.')
from tools import *
from buildRhalphabetHbb import SF2018,SF2017,SF2016

##-------------------------------------------------------------------------------------
def exec_me(command, outf, dryRun=False):
    print command
    if not dryRun:
        outf.write("%s\n"%command)
        os.system(command)

def getPolyOrder(s):
    re_polyorder = re.compile("TF(?P<o1>\d)(?P<o2>\d)")
    match_polyorder = re_polyorder.search(s)
    if match_polyorder:
        o1 = int(match_polyorder.group("o1"))
        o2 = int(match_polyorder.group("o2"))
    else:
        sys.exit()
    #print "Order = {}, {}".format(o1, o2)
    return o1,o2
    

def main(options,mode,dryRun):
    ifile = options.ifile
    odir  = options.odir
    cats  = options.cats
    if hasattr(options,'suffix'): suffix= options.suffix
    else:                         suffix=''
    if hasattr(options,'suffix'): pseudo= options.pseudo
    else:                         pseudo=''
    if hasattr(options,'suffix'): blind = options.blind
    else:                         blind = True
    if hasattr(options,'suffix'): iloose= options.iloose
    else:                         iloose=''
    if hasattr(options,'suffix'): muonCR= options.muonCR
    else:                         muonCR=''
    if hasattr(options,'suffix'): is2017= options.is2017
    else:                         is2017=True
    if hasattr(options,'suffix'): year  = options.year
    else:                         year  =''
    if hasattr(options,'suffix'): exp  = options.exp
    else:                         exp  = False
    if hasattr(options,'suffix'): pseudoPass  = options.pseudoPass
    else:                         pseudoPass  = False
    if hasattr(options,'suffix'): nr    = options.nr
    else:                         nr    = 2
    if hasattr(options,'suffix'): np    = options.np
    else:                         np    = 2
    if hasattr(options,'suffix'): skipQCD = options.skipQCD
    else:                         skipQCD = False
    if hasattr(options,'MiNLO'): MiNLO = options.MiNLO
    else:                        MiNLO = False
    if   year=='2018':   SF = SF2018
    elif year=='2017':   SF = SF2017
    elif year=='2016':   SF = SF2016
    else:                SF = {}

 
    now = datetime.datetime.now()
    ifileName = ifile.split("/")[-1]
    if odir=="":
        odir = os.path.dirname(ifile) 
        print "using default output dir:", odir
    logf  = odir +"buildcard.log" 
    outf  = open(logf,"a")
    if not dryRun:
        outf.write("=======buildcard.py==========\n")
        outf.write("===ifile = %s ==========\n"%ifile)
        outf.write("===odir  = %s ==========\n"%odir)
        outf.write("===mode  = %s ==========\n"%mode)
        outf.write("===time  = %s ==========\n"%now.strftime("%Y-%m-%d %H:%M"))
        outf.write('===git status -uno =======\n')
        os.system('git status -uno  >> %s\n'%logf)
        outf.write('===git log =========== \n')
        os.system('git log -n 1 >> %s\n'%logf)
        outf.write("=== Using SF: ==========\n")
        for key,item in sorted(SF.iteritems()): outf.write("%s       %s\n"%(key,item))
        
    print "=======buildcard.py=========="
    print "====  ifile   = %s =========="%ifile
    print "====  odir    = %s =========="%odir
    print "====  mode    = %s =========="%mode
    print "====  time    = %s =========="%now.strftime("%Y-%m-%d %H:%M")
    print "====  logfile = %s =========="%logf
    print " Using SF:"
    for key,item in sorted(SF.iteritems()): print("%s       %s"%(key,item))
    exec_me('git log -n 1 ',outf,dryRun)

    #rhalph_base    = "python buildRhalphabetHbb.py -i %s -o %s --nr %i --np %i --remove-unmatched --prefit --addHptShape "%(ifile,odir,nr,np)
    rhalph_base    = "python buildRhalphabetHbb.py -i %s -o %s --nr %i --np %i --remove-unmatched --prefit "%(ifile,odir,nr,np)
    makecard_base  = "python makeCardsHbb.py       -i %s -o %s --remove-unmatched --no-mcstat-shape "%(ifile,odir)
    makemuonCR_base = "python writeMuonCRDatacard.py       -i %s -o %s "%(muonCR,odir)
    combcards_base = "combineCards.py "
    if mode =="vbf":
        t2ws_vbf ="text2workspace.py -P HiggsAnalysis.CombinedLimit.PhysicsModel:multiSignalModel -m 125  --PO verbose --PO 'map=.*/hqq125:r[1,0,20]' --PO 'map=.*/vbfhqq125:r_vbf[1,0,20]'"
    t2ws_rz      ="text2workspace.py -P HiggsAnalysis.CombinedLimit.PhysicsModel:multiSignalModel -m 125  --PO verbose --PO 'map=.*/*hqq125:r[1,0,20]' --PO 'map=.*/zqq:r_z[1,0,20]'"
    for cat in cats:
        combcards_base += " %s=%s "%(cat['name'],cat['card'])
   
    if not MiNLO:
        rhalph_base += " --addHptShape"
        makecard_base += " --addHptShape"
        
    if suffix:
        rhalph_base += " --suffix %s"%suffix
        makecard_base += " --suffix %s"%suffix
        makemuonCR_base += " --suffix %s"%suffix
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
    if exp:
        rhalph_base += " --exp "
    if pseudoPass:
        rhalph_base += " --createPassFromFail "
    if skipQCD:
        rhalph_base += " --skipQCD "
        
    if blind:
        rhalph_base += " --blind "
        makecard_base +=" --blind "
    if year:
        rhalph_base += " --year %s "%year
        makecard_base +=" --year %s "%year
        if muonCR:
            makemuonCR_base +=" --year %s "%year
            makemuonCR_cp   = makemuonCR_base.replace(odir,options.idir+"muonCR/")
       
    if mode =="vbf":
        t2ws_vbf += " %s -o %s"%(combcard_all, combcard_all.replace(".txt","_floatVBF.root"))
    t2ws_rz += " %s -o %s"%(combcard_all, combcard_all.replace(".txt","_floatZ.root"))
    if hasattr(options, 'scaleLumi') and options.scaleLumi:
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
        cmds.insert(2,makemuonCR_cp)
    if hasattr(options, 'scaleLumi') and options.scaleLumi:
        cmds.insert(3,insert)
    ## skip all building commands for comb
    if mode=='comb':
        cmds = [
           combcards_base,
           t2ws_rz
        ]
    for cmd in cmds:
        exec_me(cmd,outf, dryRun)
    if  not dryRun:
        print "=========== Summary ============="
        for cmd in cmds:
            if 'combineCards.py' in cmd:
                print cmd.replace(".txt",'.txt \n')
            else:
                print cmd
        print "Using SF:"
        for key,item in sorted(SF.iteritems()): print("%s       %s"%(key,item))

#buildcats from ifile
def buildcats(ifile,odir,muonCR,suffix):
    #get N ptbins
    tf = r.TFile(ifile)
    print ifile
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

def loadcats(idir,odir,muonCR,suffix):
    if not os.path.exists(idir+'../data/hist_1DZbb_pt_scalesmear.root'):
        sys.exit()
    else:
        return buildcats(idir+'../data/hist_1DZbb_pt_scalesmear.root',idir,muonCR,suffix)

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

def DDB_combination(options):
    mode = 'comb'
    idirs = [
       #'ddb_Jun24_v2/ddb_M2_full/TF22_blind_muonCR_bbSF1_v6_ewk/',
       #'ddb2018_Jun24/ddb_M2_full/TF22_blind_muonCR_bbSF1_v6_ewk/',
        'ddb2018_Jun24_MiNLO/ddb_M2_full/TF22_blind_muonCR_SFJul8/',
        'ddb_Jun24_MiNLO/ddb_M2_full/TF22_blind_muonCR_SFJul8/'
    ]
    odir = 'ddb_comb_Jun24/comb1718/MiNLO_blind_SFJul8/'
    if not os.path.exists(odir): os.mkdir(odir)
    allcards = []
    for idir in idirs:
        if   '2018' in idir:    suffix = '2018'
        elif '2016' in idir:    suffix = '2016'
        else:                   suffix = '2017'
        if 'muonCR' in idir:    muonCR=True
        else               :    muonCR=False
        allcards += loadcats(idir,odir, muonCR,suffix)
    options.cats  = allcards 
    options.odir  = odir
    main(options, mode,options.dryRun)

def DDB_MC_combination(options):
    dryRun = options.dryRun
    mode   = 'norm'
    options.blind  = ""
    options.pseudo = True
    options.is2017 = True
    options.scaleLumi = False
    options.iloose = ""
    options.nr     = 2 
    options.np     = 1
    options.idir  = "ddb_Mar19/ddb_M2/"  #fix delta-phi , 0.7 qcd kfactor, 0.9 beff SF
    #options.ifile  = options.idir+"fakeQCD/hist_1DZbb_pt_scalesmear.root"
    #options.odir  = "ddb_comb_Mar29/msd47_TF21_fakeQCD/2017/"
    options.ifile  = options.idir+"data/hist_1DZbb_pt_scalesmear.root"
    options.odir  = "ddb_comb_Mar29/msd47_TF21/2017/"
    options.suffix = "2017"
    options.cats = buildcats(options.ifile,options.odir,options.muonCR,options.suffix)
    cards2017    = buildcats(options.ifile,options.odir,options.muonCR,options.suffix)
    #main(options, mode,dryRun)
    options.idir   = "ddb2018_Mar19/ddb_M2/"  #fix delta-phi 
    #options.ifile  = options.idir+"fakeQCD/hist_1DZbb_pt_scalesmear.root"
    #options.odir   = "ddb_comb_Mar29/msd47_TF21_fakeQCD/2018/"
    options.ifile  = options.idir+"data/hist_1DZbb_pt_scalesmear.root"
    options.odir   = "ddb_comb_Mar29/msd47_TF21/2018/"
    options.suffix = "2018"
    options.cats   = buildcats(options.ifile,options.odir,options.muonCR,options.suffix)

    cards2018    = buildcats(options.ifile,options.odir,options.muonCR,options.suffix)
    #main(options, mode,dryRun)



def DDB_MC_main(options):
    dryRun = options.dryRun
    mode   = 'norm'
    options.suffix = ""
    options.blind  = ""
    options.pseudo = True
    options.is2017 = True
    options.scaleLumi = False
    options.nr     = 2 
    options.np     = 1
    options.idir  = "ddb_dec31/MC/" #first ddb
    options.idir  = "ddb_Jan17/MC/" #fix QCD xsec
    options.idir  = "ddb_Jan31/MC/" #dbtag >0.88
    options.idir  = "ddb_Feb5/MC/"  #ttbar rejection round1
    options.idir  = "ddb_Mar7/ddb_M2/"  #fix JEC/JER ,default pT1200 
    options.idir  = "ddb_Mar19/ddb_M2/"  #fix delta-phi 
    #options.idir  = "ddb2018_Mar19/ddb_M2/"  #fix delta-phi 
    #options.idir  = "coffea_Mar27/ddb_M2/"  #fix delta-phi 
    #options.idir  = "matching/ddb_M2/"  #fix delta-phi,alternative matching
    options.ifile  = options.idir+"data/hist_1DZbb_pt_scalesmear.root"
    #options.ifile  = options.idir+"fakeQCD/hist_1DZbb_pt_scalesmear.root"
    #options.ifile  = options.idir+"fakeData/hist_1DZbb_pt_scalesmear.root"
    #options.ifile  = options.idir+"poissonQCD/hist_1DZbb_pt_scalesmear.root"
    options.muonCR = options.idir+"/muonCR/hist_1DZbb_muonCR.root"
    #options.muonCR = "" 
    #options.iloose = options.idir+"/looserWZ/hist_1DZbb_pt_scalesmear.root"
    options.iloose = ""
    #options.odir  = "ddb2018_Mar19/ddb_M2/msd47_TF21_fakeQCD/"
    #options.odir  = "ddb_Mar19/ddb_M2/msd47_TF21_muonCR_fakeQCD/"
    options.odir  = "ddb_Mar19/ddb_M2/msd47_TF21_muonCR/"
    #options.odir  = "coffea_Mar27/ddb_M2/msd47_TF21/"

    idirs = [
        #'ddb_Apr17/ddb_M2/',
        #'ddb2018_Apr17/ddb_M2/',
        'ddb2016_May28_v2/ddb_M2/',
        'ddb2018_Jun6_v2/ddb_M2/',
        'ddb_Jun6_v2/ddb_M2/',
    ]
    odirs = [
        'TF22_SFJun4/',
        'TF22_muonCR_SFJun4/'
    ]
    options.nr     = 2
    options.np     = 2

    paths = []
    for idir in idirs:
        options.idir = idir
        if   '2018' in idir:    options.year = '2018'
        elif '2016' in idir:    options.year = '2016'
        else:                   options.year = '2017'
        options.suffix = options.year
        for odir in odirs:
            options.odir = idir+odir
            if not os.path.exists(options.odir): os.mkdir(options.odir)
            options.ifile  = options.idir+"data/hist_1DZbb_pt_scalesmear.root"
            if 'muonCR' in odir:                options.muonCR = options.idir+"muonCR/hist_1DZbb_muonCR.root"
            else:                               options.muonCR = '' 
            if 'blind' in odir:                 options.blind = True
            else:                               options.blind = False

            options.cats = buildcats(options.ifile,options.odir,options.muonCR,options.suffix)
            main(options, mode,dryRun)
            paths.append( idir+odir)
    print "==============================="
    for p in paths: print p
    #options.cats = buildcats(options.ifile,options.odir,options.muonCR,options.suffix)
    #main(options, mode,dryRun)
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
    options.blind  = True 
    options.pseudo = False 
    options.is2017 = True
    #options.idir  = "ddb_Jan9_10p/"
    #options.odir  = "ddb_Jan9_10p/10p_blind/"
    #options.idir  = "ddb_Jan17/10p_blind/"
    #ptions.odir  = "ddb_Jan17/10p_blind/10p_blind_muonCR/"
    #options.odir  = "ddb_Mar19/ddb_M2_p10/msd47_TF21_x10/"
    options.idir  = "ddb_Mar19/ddb_M2_p10/"
    options.odir  = "ddb_Mar19/ddb_M2_p10/msd47_TF21_muonCR_blind/"
    options.ifile  = options.idir+"data/hist_1DZbb_pt_scalesmear.root"
    #options.muonCR = ""
    options.muonCR = "ddb_Mar19/ddb_M2/muonCR/hist_1DZbb_muonCR.root"
    options.iloose = ""
    options.nr     = 2
    options.np     = 1
    options.scaleLumi = False 

    options.cats = buildcats(options.ifile,options.odir,options.muonCR,options.suffix)
    main(options, mode,dryRun)

def DDB_data_main(options):
    dryRun = options.dryRun
    mode   = 'norm'
    options.suffix = ""
    options.iloose = ""
    options.blind  = True 
    options.exp    = False
    options.pseudoPass = False
    options.pseudo = False 
    options.is2017 = True
    options.scaleLumi = False 
    idirs = [
        #'ddb_Apr17/ddb_M2_full/',
        #'ddb2018_Apr17/ddb_M2_full/',
        #'ddb2016_May28_v2/ddb_M2_full/',
        #'ddb2018_Jun6_v2/ddb_M2_full/',
        #'ddb_Jun6_v2/ddb_M2_full/',     #v1 = 1 GeV bin, v2 = nominal shifted
        #'ddb2018_Jun10/ddb_M2_full/',
        #'ddb_Jun10/ddb_M2_full/',     #Jun10 = Zprime2017 reweighting
        #'ddb_Jun12/ddb_M2_full/',     #Jun12 = Phil NLOv2 reweighting,shifted
        #'ddb_Jun16/ddb_M2_full/',          #Jun16 = Phil NLO v2 reweighting,no shift
        #'ddb_Jun16/ddb_T3_full/',         #Jun16 = Phil NLO v2 reweighting,no shift
        #'ddb2016_Jun16/ddb_M_full/',      #Jun16 = Phil NLO v2 reweighting,no shift
        #'ddb2016_Jun16/ddb_T3_full/',     #Jun16 = Phil NLO v2 reweighting,no shift
        #'ddb_Jun21/ddb_M2_full/',      #Jun16   += 2017 BtoE only
        #'ddb_Jun24/ddb_M2_full/',      #Jun16   += 2017 BtoF, prod16
        #'ddb_Jun24_v2/ddb_M2_full/',      #Jun16   += 2017 BtoF, prod16, shifted central template
        #'ddb2018_Jun24/ddb_M2_full/',      # prod16 reduced 2018D 
        #'ddb2018_Jun24_v2/ddb_M2_full/',      # prod16 reduced 2018D , shifted central template
        #'ddb2018_Jun24_v3/ddb_M2_full/',      # prod16 Full 2018D , shifted central template SF Jul8
        #'ddb2016_Jun24/ddb_M2_full/',   # 2016 fixed MC template,prod16, no QCD MC
        #'ddb2016_Jun24_v2/ddb_M2_full/',   # 2016 fixed MC template,prod16, w/ QCD MC
        #'ddb_Jun24_MiNLO/ddb_M2_full/',          #Jun24_v2   += MiNLO Jul7 shifted central template 
        #'ddb2018_Jun24_MiNLO/ddb_M2_full/',      #Jun24_v3   += MiNLO Jul7 shifted central template 
        'ddb2016_Jun24_MiNLO/ddb_M2_full/',      #Jun24_v2   += MiNLO Jul7 shifted central template 
        ###### special prod###########
        #'ddb_Jun20/ddb_M2_full/',         #Jun20 = Phil NLO v2 reweighting,no shift, no N2ddt cuti
        #'ddb2016_Jun20/ddb_M2_full/',     #Jun20 = Phil NLO v2 reweighting,no shift, no N2ddt cut
        #'ddb2018_Jun20/ddb_M2_full/',     #Jun20 = Phil NLO v2 reweighting,no shift, no N2ddt cut
        #'ddb_Jun20_v2/ddb_M2_full/',       #Jun20_v2 = Phil NLO v2 reweighting,no shift, no N2ddt cut,trigW = 1
        #'ddb2016_Jun20_v2/ddb_M2_full/',   #Jun20_v2 = Phil NLO v2 reweighting,no shift, no N2ddt cut,trigW = 1
        #'ddb2018_Jun20_v2/ddb_M2_full/',   #Jun20_v2 = Phil NLO v2 reweighting,no shift, no N2ddt cut,trigW = 1
        ###### special prod###########
    ]
    odirs = [
        #'TF22_muonCR_bbSF1/',
        #'TF22_muonCR_bbSF1_pseudoPass/',
        #'expTF22_muonCR_SFJun4_pseudoPass/',
        #'expTF31_muonCR_SFJun4_pseudoPass/',
        #'TF22_blind_SFJun4/',
        #'TF22_blind_config6/',   
        #'TF22_blind_muonCR_bbSF1_v2/',   
        'TF22_muonCR_MiNLO_SFJul8_looserWZ_p80/',   
        #'TF22_blind_muonCR_SFJul8_looserWZ_p80/',   
        #'TF22_muonCR_SFJul8_looserWZ_p80/',   
        #'TF22_blind_bbSF1_v6_ewk/',   
        #'TF22_MC_muonCR_bbSF1_v6_ewk/',  
        #'TF22_blind_muonCR_looserWZ_p80/', 
        #'TF22_blind_muonCR_looserWZ_p85/',
        #'TF22_blind_muonCR_looserWZ_p87/', 
        #'TF22_MC_muonCR_looserWZ_p87/',   
        #'TF22_MC_muonCR_looserWZ_p85/',   
        #'TF22_MC_muonCR_looserWZ_p80/',   
        #'TF22_blind_muonCR_bbSF1_pseudoPass/',   
        #'expTF22_muonCR_bbSF1/',   
        #'expTF22_muonCR_bbSF1_pseudoPass/',   
        #'expTF31_blind_muonCR_bbSF1/',   
        #'expTF31_muonCR_bbSF1_pseudoPass/',   
        #'TF22_blind_SF2016/',   
        #'TF22_blind_muonCR_config1_rescaledVqq/',   
        #'TF22_blind_muonCR_SFJun4_Jun8/',   # Jun8 = fix duplicate JER/JES
        #'expTF44_blind_muonCR_SFJun4_Jun8/',   # Jun8 = fix duplicate JER/JES
        #'expTF22_blind_muonCR_SFJun4_Jun8/',   # Jun8 = fix duplicate JER/JES
    ]

    #config1  = SFJun4-0.7 GeV scale                                 ddb_Jun6_v2/ddb_M2_full/TF22_blind_muonCR_config1/   #Best fit r_z: 1.51297  -0.293166/+0.375001  (68% CL) 
    #config2  = SFJun4-0.7 GeV scale                                 ddb_Jun6_v2/ddb_M2_full/TF22_blind_muonCR_config2/   #Best fit r_z: 1.51297  -0.293166/+0.375001  (68% CL)
    #config3  = SFJun4-0.7 GeV scale-scaleNorm                       ddb_Apr17/ddb_M2_full/TF22_blind_muonCR_config3/     #Best fit r_z: 1.17925  -0.245345/+0.39457   (68% CL)
    #config4  = SFJun4-0.7 GeV scale-scaleNorm - smear               ddb_Apr17/ddb_M2_full/TF22_blind_muonCR_config4/     #Best fit r_z: 1.18065  -0.243768/+0.414102  (68% CL)
    #config5  = SFJun4-0.7 GeV scale-scaleNorm - smear - veff        ddb_Apr17/ddb_M2_full/TF22_blind_muonCR_config5/     #Best fit r_z: 1.1395   -0.241985/+0.383181  (68% CL)w/0.68 bbeff
    #config6  = SFJun4-3% scale-scaleNorm - smear - veff             ddb_Jun16/ddb_M2_full/TF22_blind_muonCR_config6/   #Best fit r_z: 1.51297  -0.293166/+0.375001  (68% CL) 
    #config6  = SFJun4+3% scale+ -scaleNorm - smear - veff           ddb_Jun16/ddb_M2_full/TF22_blind_muonCR_config6/   #Best fit r_z: 1.51297  -0.293166/+0.375001  (68% CL) 
                                                                                                                                #Best fit r_z: 1.09698  -0.233341/+0.364163  (68% CL) w/0.7 bbeff
    #Pre App                                                         ddb_Apr17/ddb_M2_full/msd47_TF22_muonCR_beffp7_blind/    #Best fit r_z: 1.07164  -0.253762/+0.332153  (68% CL)
    #config7  = SFJun4+ x2 scaleErr                                  ddb_Jun12/ddb_M2_full/TF22_blind_muonCR_config6/   #Best fit r_z: 1.51297  -0.293166/+0.375001  (68% CL) 


    paths = []
    for idir in idirs:
        options.idir = idir
        if   '2018' in idir:    options.year = '2018'
        elif '2016' in idir:    options.year = '2016'
        else:                   options.year = '2017'
        options.suffix = options.year
        for odir in odirs:
            options.odir = idir+odir
            if not os.path.exists(options.odir): os.mkdir(options.odir)
            options.ifile  = options.idir+"data/hist_1DZbb_pt_scalesmear.root"
            #options.ifile  = options.idir+"rescaledVqq/hist_1DZbb_pt_scalesmear.root"
            if 'muonCR' in odir:                options.muonCR = options.idir+"muonCR/hist_1DZbb_muonCR.root"
            else:                               options.muonCR = '' 
            if 'blind' in odir:                 options.blind = True
            else:                               options.blind = False
            if 'exp'   in odir:                 options.exp = True
            else:                               options.exp = False
            if 'looserWZ'   in odir:            options.iloose = options.idir+'looserWZ_%s'%odir.split("_")[-1]+"/hist_1DZbb_pt_scalesmear_looserWZ.root"
            else:                               options.iloose = ''
            if 'pseudoPass'   in odir:          options.pseudoPass = True
            else:                               options.pseudoPass = False
            if 'MC'      in odir:               options.pseudo     = True
            else:                               options.pseudo     = False
            if 'MiNLO'  in odir:            options.MiNLO     = True
            else:                               options.MiNLO     = False
            if idir =='ddb2016_Jun24/ddb_M2_full/': options.skipQCD = True
            else:                                   options.skipQCD = False
            nrho, npT  = getPolyOrder(odir)
            options.nr     = nrho
            options.np     = npT

            options.cats = buildcats(options.ifile,options.odir,options.muonCR,options.suffix)
            main(options, mode,dryRun)
            paths.append( idir+odir)
    print "==============================="
    for p in paths: print p


 
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
    #DDB_combination(options)
    #DDB_MC_combination(options)
    #DB_MC_main(options)
    #DDB_10p_main(options)
    DDB_data_main(options)

    #VBFddb(options)
