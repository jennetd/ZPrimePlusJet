import glob
import sys, commands, os, fnmatch
from optparse import OptionParser

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
Output = {exe}.$(Process).stdout
Error  = {exe}.$(Process).stderr
Log    = {exe}.$(Process).log
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
    out += 'source setup.sh\n'
    out += 'cd ${CWD}\n'
    out += command + '\n'
    out += 'echo "Inside $MAINDIR:"\n'
    out += 'ls\n'
    out += 'echo "DELETING..."\n'
    out += 'rm -rf CMSSW_8_1_0\n'
    out += 'rm -rf *.pdf *.C\n'
    out += 'ls\n'
    out += 'date\n'
    with open(temp, 'w') as f:
        f.write(out)

if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option('--hadd', dest='hadd', action='store_true',default = False, help='hadd roots from subjobs', metavar='hadd')
    parser.add_option('--dryRun', dest='dryRun', action='store_true',default = False, help='dryRun', metavar='dryRun')
    parser.add_option('-o', '--odir', dest='odir', default='./', help='directory to write histograms/job output', metavar='odir')

    (options, args) = parser.parse_args()
    hadd  = options.hadd

    maxJobs = 1000
    dryRun = options.dryRun 

    #outpath= 'ratioPlotsGGH_jobs_deepdoubleb_massdecor'
    outpath= options.odir 
    gitClone = "git clone -b Hbb git://github.com/DAZSLE/ZPrimePlusJet.git"

    #Small files used by the exe
    files = ['']
    #ouput to ${MAINDIR}/ so that condor transfer the output to submission dir
    #command      = 'python ${CMSSW_BASE}/src/ZPrimePlusJet/analysis/ratioPlotsGGH.py --lumi 41.1 -o ${MAINDIR}/ --i-split $1 --max-split $2 --double-b-name AK8Puppijet0_deepdoubleb --double-b-cut 0.7'
    command    = 'python ${CMSSW_BASE}/src/ZPrimePlusJet/analysis/comparisonSignals.py --lumi 41.1 -o ${MAINDIR}/ --i-split $1 --max-split $2'

    plot_command = command.replace("-o ${MAINDIR}/ --i-split $1 --max-split $2","-o %s/"%outpath)

    if not options.hadd:
        if not os.path.exists(outpath):
            exec_me("mkdir -p %s"%(outpath), False)
        os.chdir(outpath)
        print "submitting jobs from : ",os.getcwd()
        exe = "runjob"
        write_bash(exe+".sh", command, gitClone)
        write_condor(maxJobs, exe,  files, dryRun)
    else:
        print "Trying to hadd subjob files from %s"%outpath
        nOutput = len(glob.glob("%s/Plots_1000pb_weighted_*.root"%outpath))
        if nOutput==maxJobs:
            print "Found %s subjob output files"%nOutput
            exec_me("hadd %s/Plots_1000pb_weighted.root %s/Plots_1000pb_weighted_*.root"%(outpath,outpath),dryRun)
            print "DONE hadd. Removing subjob files"
            exec_me("rm %s/Plots_1000pb_weighted_*.root"%(outpath),dryRun)
            print "Cleaning submission files..." 
            #remove all but _0 file
            for i in range(1,10):
                exec_me("rm %s/runjob.%s*"%(outpath,i),dryRun)

            print "Plotting...."
            exec_me(plot_command,dryRun)
        else:
            print "%s/%s jobs done, not hadd-ing"%(nOutput,maxJobs)
            files = glob.glob("%s/Plots_1000pb_weighted_*.root"%outpath)
            nMissJobs = range(0,maxJobs)
            for f in files:
                jobN = int(f.split("/")[-1].replace(".root","").split("_")[-1])
                if jobN in nMissJobs:
                    nMissJobs.remove(int(jobN))
            print "Missing jobs = ",nMissJobs
            os.chdir(outpath)
            for i_job in nMissJobs:
                exec_me("condor_submit rubjob.%s.jdl"%i_job)
