#!/bin/bash
source /cvmfs/cms.cern.ch/cmsset_default.sh
source /cvmfs/sft.cern.ch/lcg/views/LCG_104/x86_64-centos7-gcc12-opt/setup.sh
voms-proxy-info -all
voms-proxy-info -all --file $1
cd /u/user/eoyun/4l/25.03.26/ImageGeneration
mkdir -p ./data/250408_V2/HToAATo4L_H250A10_22
python3 mkImg2.py -d HToAATo4L_H250A10_22 -i $1 -o 250408_V2