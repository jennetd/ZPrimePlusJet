import glob
import sys, commands, os, fnmatch
from optparse import OptionParser,OptionGroup

def exec_me(command, dryRun=False):
    print command
    if not dryRun:
        os.system(command)

def write_condor(njobs, exe='runjob', files = [], dryRun=True):
    fname = '%s.jdl' % exe
    out = """universe = vanilla
Executable = {exe}.sh
Should_Transfer_Files = YES
WhenToTransferOutput = ON_EXIT_OR_EVICT
Transfer_Input_Files = {exe}.sh,{files}
Output = {exe}.$(Process).$(Cluster).stdout
Error  = {exe}.$(Process).$(Cluster).stdout
Log    = {exe}.$(Process).$(Cluster).log
Arguments = $(Process) {njobs}
Queue {njobs}
    """.format(exe=exe, files=','.join(files), njobs=njobs)
    with open(fname, 'w') as f:
        f.write(out)
    if not dryRun:
        os.system("condor_submit %s" % fname)

def write_bash(temp = 'runjob.sh', command = '' ,gitClone=""):
    out = '#!/bin/bash\n'
    out += 'date\n'
    out += 'MAINDIR=`pwd`\n'
    out += 'ls\n'
    out += '#CMSSW from scratch (only need for root)\n'
    out += 'export CWD=${PWD}\n'
    out += 'export PATH=${PATH}:/cvmfs/cms.cern.ch/common\n'
    out += 'export CMS_PATH=/cvmfs/cms.cern.ch\n'
    out += 'export SCRAM_ARCH=slc6_amd64_gcc530\n'
    out += 'scramv1 project CMSSW CMSSW_8_1_0\n'
    out += 'cd CMSSW_8_1_0/src\n'
    out += 'eval `scramv1 runtime -sh` # cmsenv\n'
    out += gitClone + '\n'
    out += 'cd ZPrimePlusJet\n'
    out += 'echo "Execute with git status/log:"\n'
    out += 'git status -uno \n'
    out += 'git log -n 1 \n'
    out += 'source setup.sh\n'
    out += 'cd ${CWD}\n'
    out += command + '\n'
    out += 'echo "Inside $MAINDIR:"\n'
    out += 'ls\n'
    out += 'echo "DELETING..."\n'
    out += 'rm -rf CMSSW_8_1_0\n'
    out += 'rm -rf *.pdf *.C core*\n'
    out += 'ls\n'
    out += 'date\n'
    with open(temp, 'w') as f:
        f.write(out)

if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option('--hadd', dest='hadd', action='store_true',default = False, help='hadd roots from subjobs', metavar='hadd')
    parser.add_option('--clean', dest='clean', action='store_true',default = False, help='clean submission files', metavar='clean')
    parser.add_option('-o', '--odir', dest='odir', default='./', help='directory to write histograms/job output', metavar='odir')
    parser.add_option('-n', '--njobs', dest='njobs', default=500, type="int", help='Number of jobs to split into', metavar='njobs')

    script_group  = OptionGroup(parser, "script options")
    script_group.add_option("--bb", action='store_true', dest="bb", default=False, help="sort by double b-tag")
    script_group.add_option('-m', '--muonCR', action='store_true', dest='muonCR', default=False, help='for muon CR',
                    metavar='muonCR')
    script_group.add_option('--dbtagmin', dest='dbtagmin', default=-99., type="float",
                      help='left bound to btag selection(fail region lower bound)', metavar='dbtagmin')
    script_group.add_option('--dbtagcut', dest='dbtagcut', default=0.9, type="float",
                      help='btag selection for cut value(pass region lower bound)', metavar='dbtagcut')
    script_group.add_option('--skip-qcd', action='store_true', dest='skipQCD', default=False, help='skip QCD', metavar='skip-qcd')
    script_group.add_option('--skip-data', action='store_true', dest='skipData', default=False, help='skip Data', metavar='skip-data')
    script_group.add_option("--lumi", dest="lumi", default=41.3, type="float", help="luminosity", metavar="lumi")
    script_group.add_option('-y' ,'--year', type='choice', dest='year', default ='2016',choices=['2016legacy','2016','2017','2018'],help='switch to use different year ', metavar='year')
    script_group.add_option("--sfData" , dest="sfData", default=1, type="int", help="process 1/sf of data", metavar="sfData")
    script_group.add_option("--region" , dest="region", default='topR6_N2',choices=['topR6_N2','QGquark','QGgluon'], help="region for pass/fail doubleB tag", metavar="region")
    script_group.add_option("--doublebName"  , dest="doublebName", default="AK8Puppijet0_deepdoubleb", help="double-b name", metavar="doublebName")
    parser.add_option_group(script_group)

    (options, args) = parser.parse_args()
    hadd  = options.hadd
    dryRun= False 

    maxJobs = options.njobs 

    outpath= options.odir
    #gitClone = "git clone -b Hbb git://github.com/DAZSLE/ZPrimePlusJet.git"
    #gitClone = "git clone -b shift_SF git://github.com/kakwok/ZPrimePlusJet.git"
    gitClone = "git clone -b shift_SF git://github.com/kakwok/ZPrimePlusJet.git"
    #gitClone = "git clone -b VBF6cats git://github.com/kakwok/ZPrimePlusJet.git"

    #Small files used by the exe
    files = []
    #ouput to ${MAINDIR}/ so that condor transfer the output to submission dir
    command      = 'python ${CMSSW_BASE}/src/ZPrimePlusJet/fitting/PbbJet/Hbb_create.py -o ${MAINDIR}/ --i-split $1 --max-split $2'
    #Add script options to job command
    for opts in script_group.option_list:
        if not getattr(options, opts.dest)==opts.default:
            print "Using non default option %s = %s "%(opts.dest, getattr(options, opts.dest))
            if opts.action == 'store_true':
                command  += " --%s "%(opts.metavar)
            else:
                command  += " --%s %s "%(opts.dest,getattr(options, opts.dest))

    if not hadd: 
        print "command to run: ", command

    fileName = 'hist_1DZbb_pt_scalesmear.root'
    if options.skipQCD:
        fileName = 'hist_1DZbb_pt_scalesmear_looserWZ.root'
    if options.bb:
        fileName = 'hist_1DZbb_sortByBB.root'
    elif options.muonCR:
        fileName = 'hist_1DZbb_muonCR.root'
    subFileName = fileName.replace(".root","_*.root")
    

    if not options.hadd:
        if not os.path.exists(outpath):
            exec_me("mkdir -p %s"%(outpath), False)
        os.chdir(outpath)
        print "submitting jobs from : ",os.getcwd()
        exe = "runjob"
        write_bash(exe+".sh", command, gitClone)
        #write_condor(maxJobs, exe, arguments, files, dryRun)
        write_condor(maxJobs, exe,  files, dryRun)
    else:
        print "Trying to hadd subjob files from %s/%s"%(outpath,subFileName)
        nOutput = len(glob.glob("%s/%s"%(outpath,subFileName)))
        if nOutput==maxJobs:
            print "Found %s subjob output files"%nOutput
            exec_me("hadd -f %s/%s %s/%s"%(outpath,fileName,outpath,subFileName),dryRun)
            print "DONE hadd. Removing subjob files.."
            exec_me("rm %s/%s"%(outpath,subFileName),dryRun)
            if options.clean:
                print "Cleaning submission files..." 
                #remove all but _0 file
                for i in range(1,10):
                    exec_me("rm %s/runjob.%s*.*"%(outpath,i),dryRun)
                exec_me("rm %s/core*"%(outpath),dryRun)
        else:
            print "%s/%s jobs done, not hadd-ing"%(nOutput,maxJobs)
            nMissJobs = range(0,maxJobs)
            if options.muonCR:
                files = glob.glob("%s/hist_1DZbb_muonCR_*.root"%outpath)
            else:
                files = glob.glob("%s/hist_1DZbb_pt_scalesmear_*.root"%outpath)
            for f in files:
                jobN = int(f.split("/")[-1].replace(".root","").split("_")[-1])
                if jobN in nMissJobs:
                    nMissJobs.remove(int(jobN))
            print "Missing jobs = ",nMissJobs
