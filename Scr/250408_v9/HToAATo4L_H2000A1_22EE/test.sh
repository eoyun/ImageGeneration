#!/bin/bash
source /cvmfs/cms.cern.ch/cmsset_default.sh
source /cvmfs/sft.cern.ch/lcg/views/LCG_104/x86_64-centos7-gcc12-opt/setup.sh
export X509_USER_PROXY=/u/user/eoyun/proxy.cert
voms-proxy-info -all
voms-proxy-info -all -file $1
export export LD_PRELOAD=/usr/lib64/libXrdPosixPreload.so
cd /u/user/eoyun/4l/25.03.26/ImageGeneration
echo "Proxy : $X509_USER_PROXY"
echo "=== DEBUG: Proxy check ==="
echo "X509_USER_PROXY: $X509_USER_PROXY"
ls -l $X509_USER_PROXY
voms-proxy-info -all || echo "No proxy available!"
