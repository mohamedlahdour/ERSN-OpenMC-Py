#!/bin/bash
# This script will download and build NJOY package

set -ex
#===============================================================================
# Build options
WORK_DIR=$1                                 # Where to put data/XS
NJOY_RELEASE=$2
cd $WORK_DIR
if [[ $NJOY_RELEASE == NJOY21 ]]; then
    # Download the source code
    git clone https://github.com/njoy/NJOY21.git
    # Get the desired version of NJOY21 (1.1.0 in this example)
    cd NJOY21
    wget https://raw.githubusercontent.com/njoy/signatures/master/NJOY21/1.1.0-NJOY21.json
    python3 ./metaconfigure/fetch_subprojects.py 1.1.0-NJOY21.json
    # Configure the build process
    mkdir bin
    cd bin
    cmake -D fetched_subprojects=true ../
    # Build NJOY1
    make -j$((`nproc`-1)) 
    # Test NJOY1
    make test
else 
    if [[ $NJOY_RELEASE == NJOY2016 ]]; then
        git clone https://github.com/njoy/NJOY2016.git
        cd NJOY2016
        # mkdir build && cd build
        # cmake -Dstatic=on ..
        # make
        wget https://raw.githubusercontent.com/njoy/signatures/master/NJOY2016/2020-03-31_15:16:37.json
        python3 ./metaconfigure/fetch_subprojects.py 2020-03-31_15:16:37.json
        mkdir bin
        cd bin
        cmake -D fetched_subprojects=true -Dstatic_libraries=ON -Dstatic_njoy=ON -DCMAKE_EXE_LINKER_FLAGS=-static ../
        make -j$((`nproc`-1))
        make test
    fi
fi

