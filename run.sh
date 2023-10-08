#!/bin/bash
myArray=( "$@" )

source /cvmfs/sft.cern.ch/lcg/views/LCG_103/x86_64-centos7-gcc11-opt/setup.sh
tar --strip-components=0 -zxvf input.tar.gz

itr=$1
python3 run.py -i $itr


condorOutDir1=/eos/user/p/psuryade/ritam/out_307
xrdcp -f data_out_${itr}.pkl root://eosuser.cern.ch/${condorOutDir1}
