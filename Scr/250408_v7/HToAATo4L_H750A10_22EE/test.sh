#!/bin/bash
source /cvmfs/cms.cern.ch/cmsset_default.sh
source /cvmfs/sft.cern.ch/lcg/views/LCG_104/x86_64-centos7-gcc12-opt/setup.sh
export X509_USER_PROXY=/tmp/x509up_u41146
voms-proxy-info -all
voms-proxy-info -all -file $1
export export LD_PRELOAD=/usr/lib64/libXrdPosixPreload.so
cd /u/user/eoyun/4l/25.03.26/ImageGeneration
mkdir -p ./data/250408_v7/HToAATo4L_H750A10_22EE
python3 mkImg2.py -d HToAATo4L_H750A10_22EE -i $1 -o 250408_v7