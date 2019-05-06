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
    parser.add_option('--resubmit', dest='resubmit', action='store_true',default = False, help='resubmit missing files', metavar='resubmit')
    parser.add_option('--dryRun', dest='dryRun', action='store_true',default = False, help='dryRun', metavar='dryRun')
    parser.add_option('-o', '--odir', dest='odir', default='./', help='directory to write histograms/job output', metavar='odir')
    
    script_group  = OptionGroup(parser, "script options")
    script_group.add_option("--lumi", dest="lumi", default = 35.9,type=float,help="luminosity", metavar="lumi")
    script_group.add_option('-s','--isData', action='store_true', dest='isData', default =False,help='signal comparison', metavar='isData')
    script_group.add_option('-m','--muonCR', action='store_true', dest='muonCR', default =False,help='for muon CR', metavar='muonCR')
    script_group.add_option('-y' ,'--year', type='choice', dest='year', default ='2017',choices=['2016legacy','2016','2017','2018'],help='switch to use different year ', metavar='year')
    script_group.add_option("--puOpt"  , dest="puOpt", default="2017", help="select pu weight source", metavar="puOpt")


    parser.add_option_group(script_group)

    (options, args) = parser.parse_args()
    hadd  = options.hadd

    maxJobs = 500
    dryRun = options.dryRun 

    outpath= options.odir 
    #gitClone = "git clone -b Hbb git://github.com/DAZSLE/ZPrimePlusJet.git"
    #gitClone = "git clone -b Hbb_test git://github.com/kakwok/ZPrimePlusJet.git"
    gitClone = "git clone -b newTF  git://github.com/kakwok/ZPrimePlusJet.git"

    #Small files used by the exe
    files = ['']
    #ouput to ${MAINDIR}/ so that condor transfer the output to submission dir
    command      = 'python ${CMSSW_BASE}/src/ZPrimePlusJet/analysis/controlPlotsGGH.py -o ${MAINDIR}/ --i-split $1 --max-split $2 '

    for opts in script_group.option_list:
        if not getattr(options, opts.dest)==opts.default:
            print "Using non default option %s = %s "%(opts.dest, getattr(options, opts.dest))
            if opts.action == 'store_true':
                command  += " --%s "%(opts.metavar)
            else:
                command  += " --%s %s "%(opts.dest,getattr(options, opts.dest))

    plot_command = command.replace("-o ${MAINDIR}/ --i-split $1 --max-split $2","-o %s/"%outpath)

    if not hadd:
        print "command to run: ", command
    else:
        print "plot command to run: ", plot_command

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
            exec_me("hadd -f %s/Plots_1000pb_weighted.root %s/Plots_1000pb_weighted_*.root"%(outpath,outpath),dryRun)
            print "DONE hadd. Removing subjob files"
            exec_me("rm %s/Plots_1000pb_weighted_*.root"%(outpath),dryRun)
            if options.clean:
                print "Cleaning submission files..." 
                #remove all but _0 file
                for i in range(1,10):
                    exec_me("rm %s/runjob.%s*"%(outpath,i),dryRun)
                exec_me("rm %s/core*"%(outpath),dryRun)
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
            if options.resubmit:
                os.chdir(outpath)
                for i_job in nMissJobs:
                    exec_me("condor_submit rubjob.%s.jdl"%i_job)

