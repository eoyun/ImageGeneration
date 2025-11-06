#!/bin/bash
source /cvmfs/cms.cern.ch/cmsset_default.sh
source /cvmfs/sft.cern.ch/lcg/views/LCG_104/x86_64-el9-gcc12-opt/setup.sh
voms-proxy-info -all
voms-proxy-info -all -file $1
export export LD_PRELOAD=/usr/lib64/libXrdPosixPreload.so
cd /u/user/eoyun/4l/25.03.26/ImageGeneration
echo "Proxy : $X509_USER_PROXY"
mkdir -p ./data/251105_v1/DYto2L_4J_MLMEE
python3 mkImg2.py -d DYto2L_4J_MLMEE -i $1 -o 251105_v1