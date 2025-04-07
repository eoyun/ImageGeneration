#!/bin/bash
source /cvmfs/cms.cern.ch/cmsset_default.sh
source /cvmfs/sft.cern.ch/lcg/views/LCG_104/x86_64-centos7-gcc12-opt/setup.sh
voms-proxy-info -all
voms-proxy-info -all --file $1
cd /u/user/eoyun/4l/25.03.26/ImageGeneration
mkdir -p ./data/test/WtoLNu_1J_MLMEE
python3 mkImg2.py -d WtoLNu_1J_MLMEE -i $1 -o test