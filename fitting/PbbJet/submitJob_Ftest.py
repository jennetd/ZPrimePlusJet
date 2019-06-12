import glob
import sys, commands, os, fnmatch
from optparse import OptionParser,OptionGroup

def exec_me(command, dryRun=False):
    print command
    if not dryRun:
        os.system(command)

#def write_condor(exe='runjob.sh', arguments = [], files = [],dryRun=True):
#    job_name = exe.replace('.sh','.jdl')
#    out = 'universe = vanilla\n'
#    out += 'Executable = %s\n'%exe
#    out += 'Should_Transfer_Files = YES\n'
#    out += 'WhenToTransferOutput = ON_EXIT_OR_EVICT\n'
#    out += 'Transfer_Input_Files = %s,%s\n'%(exe,','.join(files))
#    out += 'Output = %s.stdout\n'%job_name
#    out += 'Error  = %s.stderr\n'%job_name
#    out += 'Log    = %s.log\n'   %job_name
#    #out += 'notify_user = jduarte1@FNAL.GOV\n'
#    #out += 'x509userproxy = /tmp/x509up_u42518\n'
#    out += 'Arguments = %s\n'%(' '.join(arguments))
#    out += 'Queue 1\n'
#    with open(job_name, 'w') as f:
#        f.write(out)
#    if not dryRun:
#        os.system("condor_submit %s"%job_name)

def write_condor(njobs, exe='runjob', arguments =[], files = [], dryRun=True):
    fname = '%s.jdl' % exe
    out = """universe = vanilla
Executable = {exe}.sh
Should_Transfer_Files = YES
WhenToTransferOutput = ON_EXIT_OR_EVICT
Transfer_Input_Files = {exe}.sh,{files}
Output = {exe}.$(Process).stdout
Error  = {exe}.$(Process).stderr
Log    = {exe}.$(Process).log
Arguments =  {args}
Queue {njobs}
    """.format(exe=exe,args=' '.join(arguments), files=','.join(files), njobs=njobs)
    with open(fname, 'w') as f:
        f.write(out)
    if not dryRun:
        os.system("condor_submit %s" % fname)


def write_bash(temp = 'runjob.sh', command = '' ,gitClone="", setUpCombine=False):
    out = '#!/bin/bash\n'
    out += 'date\n'
    out += 'MAINDIR=`pwd`\n'
    out += 'ls\n'
    out += '#CMSSW from scratch (only need for root)\n'
    out += 'export CWD=${PWD}\n'
    out += 'export PATH=${PATH}:/cvmfs/cms.cern.ch/common\n'
    out += 'export CMS_PATH=/cvmfs/cms.cern.ch\n'
    out += 'export SCRAM_ARCH=slc6_amd64_gcc530\n'
    out += 'tar -xf CMSSW_8_1_0.tar.gz\n'
    out += 'cd CMSSW_8_1_0/src\n'
    out += 'scramv1 b ProjectRename\n'
    out += 'eval `scramv1 runtime -sh` # cmsenv\n'
    #out += 'export CMSSW_BASE=${CWD}/CMSSW_8_1_0/\n'
    #out += 'echo $CMSSW_BASE\n'
    #if setUpCombine:
    #    out += 'git clone -b v7.0.9 git://github.com/cms-analysis/HiggsAnalysis-CombinedLimit HiggsAnalysis/CombinedLimit\n'
    #    #out += 'git clone https://github.com/cms-analysis/CombineHarvester.git CombineHarvester\n'
    #    out += 'scramv1 build \n'
    out += gitClone + '\n'
    out += 'cd ZPrimePlusJet\n'
    out += 'source setup.sh\n'
    out += 'echo "Execute with git status/log:"\n'
    out += 'git status -uno \n'
    out += 'git log -n 1 \n'
    out += 'cd ${CMSSW_BASE}/src/ZPrimePlusJet/fitting/PbbJet/\n'
    out += command + '\n'
    out += 'cd ${CWD}\n'
    out += 'mv ./ftest*/toy*.root .\n'        #collect output
    out += 'mv ./ftest*/base*.root .\n'        #collect output
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
    #main option group: handle job submission
    parser.add_option('--hadd', dest='hadd', action='store_true',default = False, help='hadd roots from subjobs', metavar='hadd')
    parser.add_option('--clean', dest='clean', action='store_true',default = False, help='clean submission files', metavar='clean')
    parser.add_option('-o', '--odir', dest='odir', default='./', help='directory to write histograms/job output', metavar='odir')
    parser.add_option('-t','--toys'       ,action='store',type='int',dest='toys'   ,default=200, help='number of toys')
    parser.add_option('-i','--ifile', dest='ifile', default = 'hist_1DZbb.root',help='file with histogram inputs', metavar='ifile')
    parser.add_option('--ifile-loose', dest='ifile_loose', default=None, help='second file with histogram inputs (looser b-tag cut to take W/Z/H templates)', metavar='ifile_loose')
    parser.add_option('--ifile-muon', dest='ifile_muon', default=None, help='path to muonCR templates ',metavar='ifile_muon')

    #limit.py group
    script_group  = OptionGroup(parser, "script options")

    script_group.add_option('-m','--mass'   ,action='store',type='int',dest='mass'   ,default=125, help='mass')
    script_group.add_option('--nr1','--NR1' ,action='store',type='int',dest='NR1'   ,default=1, help='order of rho polynomial for model 1')
    script_group.add_option('--np1','--NP1' ,action='store',type='int',dest='NP1'   ,default=1, help='order of pt polynomial for model 1')
    script_group.add_option('--nr2','--NR2' ,action='store',type='int',dest='NR2'   ,default=2, help='order of rho polynomial for model 2')
    script_group.add_option('--np2','--NP2' ,action='store',type='int',dest='NP2'   ,default=1, help='order of pt polynomial for model 2')
    script_group.add_option('--scale',dest='scale', default=1,type='float',help='scale factor to scale MC (assuming only using a fraction of the data)')
    script_group.add_option('-l','--lumi'   ,action='store',type='float',dest='lumi'   ,default=36.4, help='lumi')
    script_group.add_option('-r','--r',dest='r', default=1 ,type='float',help='default value of r')    
    script_group.add_option('-n','--n' ,action='store',type='int',dest='n'   ,default=5*20, help='number of bins')
    script_group.add_option('--just-plot', action='store_true', dest='justPlot', default=False, help='just plot')
    script_group.add_option('--pseudo', action='store_true', dest='pseudo', default=False, help='run on asimov dataset', metavar='pseudo')
    script_group.add_option('--blind', action='store_true', dest='blind', default=False, help='run on blinded dataset',metavar='blind')
    script_group.add_option('--exp', action='store_true', dest='exp', default=False, help='use exp(bernstein poly) transfer function',metavar='exp')
    script_group.add_option('--freezeNuisances'   ,action='store',type='string',dest='freezeNuisances'   ,default='None', help='freeze nuisances')
    script_group.add_option('--dryRun',dest="dryRun",default=False,action='store_true',help="Just print out commands to run",metavar='dryRun')    
    script_group.add_option('--suffix', dest='suffix', default=None, help='suffix for conflict variables',metavar='suffix')
    script_group.add_option('--is2017', action='store_true', dest='is2017', default=False, help='use 2017SF',metavar='is2017')

    parser.add_option_group(script_group)

    (options, args) = parser.parse_args()
    hadd            = options.hadd
    dryRun          = options.dryRun
    setUpCombine    = True

    nToys           = options.toys
    nToysPerJob     = 20
    maxJobs         = nToys/nToysPerJob

    outpath= options.odir
    #gitClone = "git clone -b Hbb git://github.com/DAZSLE/ZPrimePlusJet.git"
    #gitClone = "git clone -b Hbb_test git://github.com/kakwok/ZPrimePlusJet.git"
    gitClone = "git clone -b newTF git://github.com/kakwok/ZPrimePlusJet.git"
    #gitClone = "git clone -b PerBinEff git://github.com/kakwok/ZPrimePlusJet.git"

    #Small files used by the exe
    files = [options.ifile]

    #ouput to ${MAINDIR}/ so that condor transfer the output to submission dir
    command      = 'python ${CMSSW_BASE}/src/ZPrimePlusJet/fitting/PbbJet/runFtest.py -o ${MAINDIR}/ --seed $1 --toys $2 --ifile ${MAINDIR}/$3 '
    plot_odir    = "/".join(options.odir.split("/")[:-3])
    
    #print out command to use after jobs are done
    plot_command = 'python ${CMSSW_BASE}/src/ZPrimePlusJet/fitting/PbbJet/runFtest.py -o %s --just-plot --ifile %s'%(plot_odir,options.ifile)
    
    #Command to create local copy of datacards
    if  options.ifile_loose is not None: 
        files.append( options.ifile_loose)
        command  += '--ifile-loose ${MAINDIR}/$%i'%(files.index( options.ifile_loose)+3)
        plot_command += ' --ifile-loose %s '%(options.ifile_loose)
    if  options.ifile_muon is not None:
        files.append( options.ifile_muon)
        command  += '--ifile-muon ${MAINDIR}/$%i'%(files.index( options.ifile_muon)+3)
        plot_command += ' --ifile-muon %s '%(options.ifile_muon)
    #Add script options to job command
    for opts in script_group.option_list:
        if not getattr(options, opts.dest)==opts.default:
            print "Using non default option %s = %s "%(opts.dest, getattr(options, opts.dest))
            if opts.action == 'store_true':
                command  += " --%s "%(opts.metavar)
                plot_command  += " --%s "%(opts.metavar)
            else:
                command  += " --%s %s "%(opts.dest,getattr(options, opts.dest))
                plot_command  += " --%s %s "%(opts.dest,getattr(options, opts.dest))
    if not hadd: 
        print "Copying inputfiles to submission dir:"
        if not os.path.exists(outpath):
            exec_me("mkdir -p %s"%(outpath), False)
        for f in files: 
            exec_me("cp %s %s"%(f, outpath))
        print "command to run: ", command
    else:
        print "plot command: ",plot_command

    subToy1 = "toys1_*.root"
    subToy2 = "toys2_*.root"
    toy1    = "toys1.root"
    toy2    = "toys2.root"
    cmssw   = os.path.expandvars("$ZPRIMEPLUSJET_BASE/CMSSW_8_1_0.tar.gz")

    if not options.hadd:
        if not os.path.exists(outpath):
            exec_me("mkdir -p %s"%(outpath), False)
        os.chdir(outpath)
        print "submitting jobs from : ",os.getcwd()
    
        localfiles = [path.split("/")[-1] for path in files]    #Tell script to use the transferred files
        localfiles.append(cmssw)
        arguments = [ str("$(Process)"),str(nToysPerJob)]
        for f in localfiles:
            arguments.append(str(f))
        exe       = "runjob"
        write_bash(exe+".sh", command, gitClone, setUpCombine)
        write_condor(maxJobs,exe, arguments, localfiles,dryRun)
    else:
        nOutput = len(glob.glob("%s/%s"%(outpath,subToy1)))
        print "Found %s subjob output files in path: %s/%s"%(nOutput,outpath,subToy1)
        def cleanAndPlot():
            if options.clean:
                print "Cleaning submission files..." 
                #remove all but _0 file
                for i in range(1,9):
                    exec_me("rm %s/runjob.%s*"%(outpath,i),dryRun)
                print "Finish cleaning,plotting " 
            print "plot command: ",plot_command
            exec_me(plot_command,dryRun)
        if nOutput==maxJobs:
            cleanAndPlot()
        else:
            print "%s/%s jobs done, not hadd/clean-ing"%(nOutput,maxJobs)
            proceed = raw_input("Proceed anyway?")
            if proceed=="yes":
                cleanAndPlot()
