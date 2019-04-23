import json,glob,os,copy
import controlPlotsGGH 
import Hbb_create
import normSampleContainer
from optparse import OptionParser
import ROOT as r

def expand(fpaths):
    expandedPaths = []
    for p in fpaths:
        if "*" in p:
            if "root://" in p:
                redirector = "root://cmseos.fnal.gov/"
                eosp = p.replace("root://cmseos.fnal.gov/","")  #glob does not work with redirector
                globpaths = glob.glob(eosp)
                for i,glob_p in enumerate(globpaths):
                    globpaths[i] = redirector+glob_p
                expandedPaths.extend(globpaths)
        else:
            expandedPaths.append(p)
    return expandedPaths 

def expandPath(fdict):
    rdict = {}
    for sample,subSample in fdict.iteritems():
        if type(subSample)==type([]):       # already filenames
            rdict[sample] = expand(subSample)
            if len(rdict[sample])==0:            print "ERROR: %s has no files"%(sample)
        elif type(subSample)==type({}):     # subSamples has list of files each, expand
            d={} 
            for subSname,subpaths in subSample.iteritems():
                expandedPath = expand(subpaths) 
                if len(expandedPath)==0:
                    print "ERROR: %s has no files"%(subSname)
                    print "Trying to expand path with %s"%subpaths
                d[subSname] = expandedPath 
            rdict[sample] =  d
    return rdict

#Get the number of events from the NEvents histogram
def getNentriesAndPu(oTreeFiles):
        n = 0
        f1 = r.TFile.Open(oTreeFiles[0])
        h_puMC = f1.Get("Pu").Clone()
        n     += f1.Get("NEvents").GetBinContent(1)
        h_puMC.SetDirectory(0)
        f1.Close()
        for otf in oTreeFiles[1:]:
            f  = r.TFile.Open(otf)
            n += f.Get("NEvents").GetBinContent(1)
            h_puMC.Add(f.Get("Pu"))
            f.Close()
        return n,h_puMC

def makeNormRoot(diffjson,remakeAllnorms=False):
    #diffjsonf  = open('test.json','r')
    #diffjson  = json.load(diffjsonf)
    for fset,samples in  diffjson.iteritems():
        if remakeAllnorms==True:
            norm = r.TFile("ggH/norm_%s.root"%fset,"RECREATE")
        else:
            norm = r.TFile("ggH/norm_%s.root"%fset,"UPDATE")
        for sample,subsample in samples.iteritems():
            #ignore data
            if type(subsample)==type([]):continue
            for s,paths in subsample.iteritems():
                if len(paths)>0:
                    print "updating ",s
                    nevents = "_".join(['h',sample,s,'n'])
                    pu      = "_".join(['h',sample,s,'pu'])
                    n, h_pu   = getNentriesAndPu(paths)
                    h_nevents = r.TH1F(nevents,nevents,1,0,1)
                    norm.cd()
                    h_pu.SetName(pu)
                    h_nevents.SetBinContent(1,n)
                    h_pu.Write("",r.TObject.kOverwrite)
                    h_nevents.Write("",r.TObject.kOverwrite)
        norm.Close()

def diffDict(loadedJson,finaljson):
    if loadedJson == finaljson:
        print "No changes to samplefiles.json detected" 
        return
    else:
        diffed_json = {}
        changed_subsamples = []
        for fset in  finaljson.keys():
            diffed_json[fset] = copy.deepcopy(finaljson[fset])
            if len(finaljson[fset]) is not len(loadedJson[fset]):
                print "list of sample changed."
            samples       = finaljson[fset]
            loadedsamples = loadedJson[fset]
            for sample,subsample in samples.iteritems():
                if type(subsample)==type([]):
                    ## ignore data 
                    diffed_json[fset][sample] = []
                elif type(subsample)==type({}):
                    loadedsubsamples = loadedsamples[sample]
                    for s,paths in subsample.iteritems():
                        loadedpaths = loadedsubsamples[s]
                        if len(loadedpaths) != len(paths):
                            print s,'is different'
                            changed_subsamples.append(s)
                            diffed_json[fset][sample][s] = paths 
                        else:
                            diffed_json[fset][sample][s] = []
        #print json.dumps(diffed_json,indent=4)
        return  diffed_json,changed_subsamples

def main(options,args):
    outf = open(os.path.expandvars("$ZPRIMEPLUSJET_BASE/analysis/ggH/samplefiles.json"),"r")
    loadedJson = json.load(outf)

    finaljson = {}
    finaljson['controlPlotsGGH_2017']      = expandPath(controlPlotsGGH.get2017files()) 
    finaljson['controlPlotsGGH_2018']      = expandPath(controlPlotsGGH.get2018files()) 
    finaljson['Hbb_create_2017']           = expandPath(Hbb_create.get2017files(False)) 
    finaljson['Hbb_create_2017_muCR']      = expandPath(Hbb_create.get2017files(True)) 
    finaljson['Hbb_create_2018']           = expandPath(Hbb_create.get2018files(False)) 
    finaljson['Hbb_create_2018_muCR']      = expandPath(Hbb_create.get2018files(True)) 
    print "LoadedJson == new json: ", loadedJson == finaljson
    updateNorms = True 
    remakeAllnorms = options.remakeAllnorms
    if loadedJson != finaljson and updateNorms :
        diffed_json, changed_subsamples = diffDict(loadedJson,finaljson)
        #print "Following subsamples are changed:"
        #for s in changed_subsamples: print s
        makeNormRoot(diffed_json)
    if remakeAllnorms:
        makeNormRoot(finaljson,remakeAllnorms=True)
        

    if not options.printOnly and finaljson is not {}:
        outf = open(os.path.expandvars("$ZPRIMEPLUSJET_BASE/analysis/ggH/samplefiles.json"),"w")
        print "Writing to ", os.path.expandvars("$ZPRIMEPLUSJET_BASE/analysis/ggH/samplefiles.json")
        outf.write((json.dumps(finaljson,indent=4)))
    else:
        print (json.dumps(finaljson,indent=4,sort_keys=True))
    for key,tfiles in sorted(finaljson.iteritems()):
        print "list of samples used by %s =  "%key, sorted(tfiles.keys())


if __name__ == '__main__':
    parser = OptionParser()
    #parser.add_option('-o','--odir', dest='odir', default = '',help='directory to write plots', metavar='odir')
    parser.add_option('-p','--printOnly', dest='printOnly',action='store_true', default=False,help='print json to screen only', metavar='printOnly')
    parser.add_option('--remakeAllnorms', dest='remakeAllnorms',action='store_true', default=False,help='Remake all PU histograms and Nevent ', metavar='printOnly')
    (options, args) = parser.parse_args()
    main(options,args)

