import ROOT
from ROOT import TFile
from sampleContainer import *
import glob

class normSampleContainer:
    def __init__(self, sampleName, subSamples, sf=1, DBTAGCUTMIN=-99., lumi=1, isData=False, fillCA15=False, cutFormula='1',
                 minBranches=False, iSplit = 0, maxSplit = 1, triggerNames={}, treeName='', 
                 doublebName='AK8Puppijet0_doublecsv', doublebCut = 0.9, puOpt={}):

        self.sampleName            = sampleName
        self.subSampleContainers    = {}
        self.subSamples             = subSamples
        self._sf                    = sf
        self._lumi                  = lumi
        self._triggerNames          = triggerNames 
        self.DBTAGCUTMIN = DBTAGCUTMIN
        self.DBTAGCUT = doublebCut
        self.doublebName = doublebName
        self.xsectionFile    = os.path.expandvars("$ZPRIMEPLUSJET_BASE/analysis/ggH/xSections.dat")
        self.treeName        = treeName

        # subSamples = {subsampleName: [paths]}
        for subSampleName,paths in self.subSamples.iteritems():
            xSection = self.getXsection(subSampleName,self.xsectionFile)   # in pb
            tfiles = {}
            tfiles[subSampleName] = paths 
            if  len(tfiles[subSampleName])>0:
                print "normSampleContainer:: subSample = %s , Nfiles = %s , basePath = %s"%(subSampleName, len(tfiles[subSampleName]), paths[0].replace(paths[0].split("/")[-1],""))
            else:
                print "normSampleContainer:: subSample = %s  "%(subSampleName)
            #look up TreeName in the first file if not specified
            if self.treeName =='':
                self.SetTreeName(tfiles[subSampleName])
            Nentries,h_puMC,checksum           = self.getNentriesAndPu(tfiles[subSampleName])
            puOpt['MC'] = h_puMC
            print "puOpt = ",puOpt
            lumiWeight         =  (xSection*1000*lumi) / Nentries
            print "normSampleContainer:: [sample %s, subsample %s] lumi = %s fb-1, xSection = %.3f pb, nEvent = %s, weight = %.5f, Nfiles=%s,(chkSum=%s)" % (sampleName, subSampleName, lumi, xSection, Nentries, lumiWeight,len(tfiles[subSampleName]),checksum)
            self.subSampleContainers[subSampleName] = sampleContainer(subSampleName, tfiles[subSampleName], sf, DBTAGCUTMIN, lumiWeight, isData, fillCA15, cutFormula, minBranches, iSplit ,maxSplit,triggerNames,self.treeName,doublebName,doublebCut,puOpt)

    #Set treeName
    def SetTreeName(self,oTreeFiles):
        treeNames=["otree","Events"]
        print "Trying to get tree with file=",oTreeFiles[0]
        exampleFile = TFile.Open(oTreeFiles[0])
        for tName in treeNames:
            if exampleFile.Get(tName):
                print "Found tree=",tName
                self.treeName= tName
                break 
        if self.treeName=="":       
            print "Error! Cannot find any tress with names= ",treeNames
        return  

    #Get the number of events from the NEvents histogram
    def getNentriesAndPu(self,oTreeFiles):
        n = 0
        f1 = TFile.Open(oTreeFiles[0])
        h_puMC = f1.Get("Pu").Clone()
        n     += f1.Get("NEvents").GetBinContent(1)
        h_puMC.SetDirectory(0)
        checksum = 1
        f1.Close()
        for otf in oTreeFiles[1:]:
            f  = TFile.Open(otf)
            n += f.Get("NEvents").GetBinContent(1)
            checksum +=1
            h_puMC.Add(f.Get("Pu"))
            f.Close()
        return n,h_puMC,checksum

    def getXsection(self,fDataSet,xSectionFile):
        thisXsection = 1.0
        FoundXsection = False
        print "NormSampleContainer:: using xsection files from : ",xSectionFile
        with open(xSectionFile) as xSections:
            for line in xSections:
                if line[0]=="\n" or line[0]=="#": continue
                line       = line.strip().split()
                DataSetRef = line[0]
                xSection   = line[1]
                if fDataSet == DataSetRef:
                    thisXsection = eval(xSection)
                    FoundXsection = True
                    break
        if not FoundXsection:
            print "NormSampleContainer:: Cannot find xsection for %s",fDataSet
            sys.exit()
        return thisXsection

    ## Add all plots from subSamples,  Returns plots in { sampleName_plotName : sc.attr }
    def addPlots(self,plots):
        allplots = {}
        for plot in plots:
            firstName     = self.subSampleContainers.keys()[0]
            sc            = self.subSampleContainers[firstName]
            allplots[plot] = getattr(sc, plot).Clone(plot.replace("h_","h_%s_"%self.sampleName))      #Clone the histograms from first sample
        for plot in plots:
            for subSample in self.subSampleContainers.keys()[1:] :   #Add the rest of the histos
                sc             = self.subSampleContainers[subSample]
                allplots[plot].Add(getattr(sc,plot))
        return allplots

