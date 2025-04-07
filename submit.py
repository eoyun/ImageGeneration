import os
import sys
import subprocess
import argparse


parser = argparse.ArgumentParser()
parser.add_argument("-o", "--outputdir", dest="outputdir", action="store")
args = parser.parse_args()

def Make_CondorScr(outname,dataset) :
    os.system("mkdir -p Scr/"+outname+"/"+dataset+"/log")
    condor_filename = "Scr/"+outname+"/"+dataset+"/condor.submit"
    lines =0
    with open("./input/"+outname+"/"+dataset+".dat","r") as fp :
        lines = len(fp.readlines())
    f = open(condor_filename,"w")
    f.write('# Unix submit description file\n')
    f.write('Universe = vanilla\n')
    #f.write('transfer_input_files = /afs/cern.ch/user/y/yeo/tmp/x509up\n')
    f.write('Executable = ./Scr/'+outname+"/"+dataset+'/test.sh\n')
    f.write('request_memory = 1000\n')
    f.write('should_transfer_files   = Yes\n')
    f.write('arguments = $(ProcId)\n')
    f.write('output = ./Scr/'+outname+"/"+dataset+'/log/$(ProcId).out\n')
    f.write('error = ./Scr/'+outname+"/"+dataset+'/log/$(ProcId).err\n')
    f.write('log = ./Scr/'+outname+"/"+dataset+'/log/$(ProcId).log\n')
    f.write('+MaxRuntime = 36000\n')
    f.write('Queue '+str(lines)+'\n')
    f.close()
    subchMod = "condor_submit ./Scr/"+outname+"/"+dataset+"/condor.submit"
    os.system("pwd")
    os.system(subchMod)
    return 0

def Make_Scr(outname,dataset) :
    os.system("mkdir -p Scr/"+outname+"/"+dataset)
    scr_filename = "Scr/"+outname+"/"+dataset+"/test.sh"
    f = open(scr_filename,"w")
    f.write('#!/bin/bash\n')
    f.write('source /cvmfs/cms.cern.ch/cmsset_default.sh\n')
    f.write('source /cvmfs/sft.cern.ch/lcg/views/LCG_104/x86_64-centos7-gcc12-opt/setup.sh\n')
    #f.write('export X509_USER_PROXY=/afs/cern.ch/user/y/yeo/tmp/x509up\n')
    f.write('voms-proxy-info -all\n')
    f.write('voms-proxy-info -all --file $1\n')
    #f.write('cd /afs/cern.ch/user/y/yeo/rdf/24.09.25\n') 
    pwd = os.getcwd()
    f.write('cd '+ pwd +'\n')
    f.write('mkdir -p ./data/'+outname+"/"+dataset+'\n')
    f.write('python3 mkImg2.py -d '+dataset+' -i $1 -o '+outname)
    f.close()
    return 0




def Make_input(dataset,directory,outname,inputfiledate):
    os.system("mkdir -p input/"+outname)
    os.system("find "+directory+inputfiledate+"_*/*/ -maxdepth 1 -type f -print > ./input/"+outname+"/"+dataset+".dat")

#find /pnfs/knu.ac.kr/data/cms/store/user/yeo/HToAATo4L_H2000A1_TuneCP5_13p6TeV-pythia8/HToAATo4L_H2000A1_22EE/250225_*/*/ -maxdepth 1 -type f -print


outname = args.outputdir
with open ("./inputdata.dat","r") as fp :
    #print(fp.readlines())
    lines = fp.readlines()

if (os.path.isdir('./input/'+outname)) :
   print("plz check output name")
else :

    for line in lines :
        parts = line.strip().split(" ",1)
        dataset, directory  = parts
        Make_input(dataset,directory,outname,"250328")
        Make_Scr(outname,dataset)
        Make_CondorScr(outname,dataset)
        #print(dataset)
        #print("----------------")
        #print(directory)
