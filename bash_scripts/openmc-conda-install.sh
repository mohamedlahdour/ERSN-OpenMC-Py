#!/bin/bash
    
# This script installs OpenMC, its Python API, and all necessary dependencies
# into a conda environment. Because it uses compilers and CMake from the
# Anaconda repository, it's not necessary to have those installed on your
# system. However, at a minimum, you do need to have 'make' installed as well as
# a linker. To get the OpenMC git repository, you'll need git installed as
# well. On Debian derivatives, you can install all of these with:
#
# sudo apt install -y make binutils git

set -e

#===============================================================================
# INSTALLATION OPTIONS
INSTALL_MINICONDA=$1
DOWNLOAD_MINICONDA=$2
CHECKSUM=$3
SCRIPT=$4
CONDA_MD5=$5
UPDATE_CONDA=$6
CONDA_URL=$7
INSTALL_PREREQUISITES=$8                    # In stall prerequisites and dependencies
WITH_MPI=$9                                 # Install with MPI support
INSTALL_IN_CONDA=${10}                      # Install OpenMC executable/package directly in conda environment?
INSTALL_EDITABLE=${11}                      # Install in editable mode (overrides INSTALL_IN_CONDA)
DELETE_SRC=${12}
UPDATE_ENV=${13}
PYTHON_VERSION=${14}                        # What version of Python to use
ENVNAME=${15}                               # conda environment name
WORK_DIR=${16}                              # Where to put openmc sources if not deleted
INSTALL_PREFIX=${17}                        # Where to install (if INSTALL_IN_CONDA and INSTALL_EDITABLE are disabled)
conda=${18}
CONDA_DIR=${19}
INSTALL_OPENMC=${20}
OPENMC_RELEASE=${21}
DOWNLOAD_OPENMC=${22}
OPENMC_DIR=${23}
INSTALL_PQTY=${24}

#===============================================================================
#                     Download and install miniconda
#===============================================================================
if [[ $INSTALL_MINICONDA == yes ]]; then
    if [[ $DOWNLOAD_MINICONDA == yes ]]; then
        if [[ -f "$SCRIPT" ]]; then
            echo "#########     $SCRIPT script already exists !     #########"
            if [[ $CHECKSUM == yes ]]; then
                CHECK=$(sha256sum  $SCRIPT | awk '{print $1}')
                if [[ $CHECK != $CONDA_MD5 ]]; then
                    echo "#########     checksum fails; script will be deleted and downloaded again !     #########"
                    rm -rf $SCRIPT
                    wget $CONDA_URL
                fi
            fi
        else        
            wget $CONDA_URL
        fi
        if [[ $CHECKSUM == yes ]]; then
            CHECK=$(sha256sum  $SCRIPT | awk '{print $1}')
            if [[ $CHECK != $CONDA_MD5 ]]; then
                echo "#########     Could not install Miniconda3, checksum fails; check your connexion and try again !     #########"
                rm -rf $SCRIPT
                exit 1
            fi
        fi
    fi
    echo "#########     miniconda3 will be installed !     #########"
    bash $SCRIPT -b 
    # $HOME/miniconda3/bin/conda update -y -n base -c defaults conda
    $HOME/miniconda3/bin/conda init bash
    source ~/.bashrc
    if [ $? -eq 0 ]; then 
        if [[ $UPDATE_CONDA == yes ]]; then
            # source ~/.bashrc
            $HOME/miniconda3/bin/conda update -y -n base -c defaults conda
        else
            echo "#########     An update of miniconda may be required !     #########"
        fi  
    else
        echo "#########     Check if miniconda has been installed successfuly !     #########"
    fi
    echo "==> For changes to take effect, close and re-open your current shell. <=="
else
    if [[ $UPDATE_CONDA == yes ]]; then
        if [[ -f "$HOME/miniconda3/condabin/conda" ]]; then
            $HOME/miniconda3/condabin/conda update -y -n base -c defaults conda
            $HOME/miniconda3/condabin/conda init bash
            # source ~/.bashrc
            echo
            echo "==> For changes to take effect, close and re-open your current shell. <=="
        else
            echo "#########     Miniconda must be installed before updating it !     #########"
        fi
    else
        if [[ -f "$HOME/miniconda3/condabin/conda" ]]; then
            echo "#########     An update of miniconda may be required !     #########"
        else
            echo "#########     Miniconda must be installed before installing openmc !     #########"
        fi
    fi
fi
echo
if [[ $INSTALL_PQTY == yes ]]; then
    if [[ -f "$HOME/miniconda3/etc/profile.d/conda.sh" ]]; then
        source ~/.bashrc
        . $HOME/miniconda3/etc/profile.d/conda.sh
        conda activate
        if [[ -z "$(conda list|grep pyqt)" ]]; then
            echo
            echo "#########               PyQT5 will be installed !           #########"
            #conda install -y pyqt
            pip install pyqt5
            echo
            echo "==> If QtCore module cannot be loeded from PyQt5 force reinstall PyQt5 <=="
            echo "==> Command : python3 -m pip install --upgrade --force-reinstall PyQt5 <=="
            echo
            echo "==> For changes to take effect, close and re-open your current shell. <=="
        fi
    fi
fi
#===============================================================================
#      Make sure conda is activated to install prerequisites and openmc
#===============================================================================
if [[ $INSTALL_PREREQUISITES == yes || $INSTALL_OPENMC == yes ]]; then
    if [[ -f "$HOME/miniconda3/etc/profile.d/conda.sh" ]]; then
        . $HOME/miniconda3/etc/profile.d/conda.sh
        conda activate
        if [ $? -eq 0 ]; then
            echo "#########     miniconda activated     #########"
        else
            echo "#########     miniconda activation failed. Make sur miniconda3 is installed and activated ! Or close and re-open your terminal if already installed     #########"
            exit 1
        fi
    fi
fi
#===============================================================================
#                         Install prerequisites
#===============================================================================
if [[ $INSTALL_PREREQUISITES == yes ]]; then
    # Make sure conda is activated 
    . $HOME/miniconda3/etc/profile.d/conda.sh
    rm ~/.condarc
    conda config --set channel_priority flexible
    conda activate
    # Create new Python environment to install everything into
    if [[ ! "$HOME/miniconda3/envs/$ENVNAME" || ! -d "$HOME/miniconda3/envs/$ENVNAME" ]]; then
        conda create -y -n $ENVNAME python=$PYTHON_VERSION
        echo "#########     Environment $ENVNAME created !     #########"
    fi    
    conda activate $ENVNAME
    echo "#########     $ENVNAME activated     #########"

    # Install recent version of gcc and CMake. OpenMC requires gcc 4.9+ and CMake
    # 3.3+, so if you are on an older distribution, it's possible that your version
    # is not sufficient.
    
    conda install -y gcc_linux-64 gxx_linux-64 cmake 

    # Install OpenMC's Python dependencies
    
    conda install -y numpy scipy cython pandas lxml matplotlib ipython pytest
    echo " ==== If pugixml couldn't be installed uncomment the following line in"
    echo "      openm-conda-install.sh script and comment the one that follows:"
    echo "      #conda install -c conda-forge pugixml                                  ==== "
    conda install -y -c conda-forge pugixml
    #conda install -y pugixml

    # The uncertainties package is not in the default conda channel
    conda config --append channels conda-forge/label/gcc7
    conda install -y uncertainties

    # Install MPICH for building with MPI support. Make sure to use the package
    # based on gcc7. For depletion, we also need the parallel version of h5py
    if [[ $WITH_MPI == yes ]]; then
        conda install -y mpich h5py=*=*mpich*
        export CXX=mpicxx
    else
        conda install -y h5py
    fi
    if [[ $UPDATE_ENV == yes ]]; then
        echo "#########     $ENVNAME will be updated     #########"
        conda update -y --all
    fi
        
    # install paraview/mayavi
    # conda install -y -c conda-forge paraview    
    # conda install -y -c conda-forge mayavi

    # install vtk and its dependencies
    conda install -y -c conda-forge vtk
    conda install -y tbb=2020.2
    conda install -y jsoncpp=1.8.3

    # to avoid this warning : libGL error: MESA-LOADER: failed to open iris
    conda install -c conda-forge libstdcxx-ng
fi
# conda activate $ENVNAME
# echo "#########     $ENVNAME activated     #########"

#===============================================================================
#                            OpenMC Installation
#===============================================================================
if [[ $INSTALL_OPENMC == yes ]]; then
    # Set up temporary directory
    #WORK_DIR=$(mktemp -d)
    if [[ ! "$WORK_DIR" && ! -d "$WORK_DIR" ]]
    then
        mkdir $WORK_DIR
    else
        if [[ ! "$WORK_DIR/openmc" && ! -d "$WORK_DIR/openmc" ]]
        then
            echo "#########     Could not create openmc directory !     #########"
            exit 1
        fi
    fi
fi
# Make sure temporary directory is deleted if script exits
function cleanup {
    if [[ $DELETE_SOURCES == yes ]] 
    then
        rm -rf "$WORK_DIR/openmc"
        echo "#########     Deleted temporary working directory $WORK_DIR !     #########"
    fi
}
trap cleanup EXIT

if [[ $INSTALL_OPENMC == yes ]]; then
    # Make sure conda is activated
    . $HOME/miniconda3/etc/profile.d/conda.sh
    source ~/.bashrc
    # conda activate $ENVNAME
    # Create new Python environment to install everything into
    if [[ $UPDATE_ENV == yes ]]; then
        if [[ ! "$HOME/miniconda3/envs/$ENVNAME" || ! -d "$HOME/miniconda3/envs/$ENVNAME" ]]; then
            conda create -y -n $ENVNAME python=$PYTHON_VERSION
            echo "#########     Environment $ENVNAME created !     #########"    
            conda activate $ENVNAME
            # Install OpenMC's Python dependencies and prerequisites
            conda install -y gcc_linux-64 gxx_linux-64 cmake 
            conda install -y numpy scipy cython pandas lxml matplotlib ipython pytest    
            conda config --append channels conda-forge/label/gcc7
            conda install -y uncertainties
            # Install MPICH for building with MPI support. Make sure to use the package
            # based on gcc7. For depletion, we also need the parallel version of h5py
            if [[ $WITH_MPI == yes ]]; then
                conda install -y mpich h5py=*=*mpich*
                export CXX=mpicxx
            else
                conda install -y h5py
            fi        
        else
            conda activate $ENVNAME
        fi
        conda update -y --all
    else
        conda activate $ENVNAME
    fi
    # Clone OpenMC
    cd $WORK_DIR
    if [[ $DOWNLOAD_OPENMC == yes ]]; then
        if [[ $OPENMC_RELEASE == "latest" ]]; then
            echo "####################################################"
            echo "#########                         Wait ! Cloning openmc ...                         #########"
            echo "####################################################"

            git clone --recurse-submodules https://github.com/openmc-dev/openmc.git
            cd $OPENMC_DIR
        else
            URL="https://github.com/openmc-dev/openmc/archive/"
            EXT=".zip"
            ARCHIVE=$OPENMC_RELEASE$EXT
            echo $URL$ARCHIVE
            if [[ ! -f "$ARCHIVE" ]]; then wget $URL$ARCHIVE; fi
            unzip -o $ARCHIVE
            # cd "${OPENMC_RELEASE/v/openmc-}"
            cd $OPENMC_DIR
            if [[ $OPENMC_RELEASE == *"v0.12"* ]]; then
                # git submodules are needed
                cd vendor
                rm -rf fmt gsl-lite pugixml xtensor xtl
                git clone https://github.com/fmtlib/fmt.git
                git clone https://github.com/martinmoene/gsl-lite.git
                git clone https://github.com/zeux/pugixml.git
                git clone https://github.com/xtensor-stack/xtensor.git
                git clone https://github.com/xtensor-stack/xtl.git
                cd ..
            fi
        fi
    else
        cd $OPENMC_DIR
        rm -rf build
    fi
    # Build OpenMC library and executable
    echo $CONDA_PREFIX $INSTALL_IN_CONDA
    mkdir -p build && pushd build
    if [[ $INSTALL_IN_CONDA == yes ]]; then
        cmake -DCMAKE_INSTALL_PREFIX=$CONDA_PREFIX ..
    else
        cmake -DCMAKE_INSTALL_PREFIX=$INSTALL_PREFIX ..
    fi
    popd

    # Install Python API
    if [[ $INSTALL_EDITABLE == yes ]]; then
        pip install --no-dependencies --no-build-isolation -e .
    else
        if [[ $INSTALL_IN_CONDA == yes ]]
        then
            pip install --no-dependencies --no-build-isolation .
        else
            pip install --target=$INSTALL_PREFIX --no-dependencies --no-build-isolation .
        fi
    fi

    # Install executable
    if [[ $INSTALL_EDITABLE != yes ]]
    then
        pushd build
        make -j$((`nproc`-1)) install
        popd
    fi
fi
echo
if [ $? -eq 0 ]
then
    echo "#########     The script ran ok     #########"
    exit 0
else
    echo "#########     The script failed     #########" >&2
    exit 1
fi
