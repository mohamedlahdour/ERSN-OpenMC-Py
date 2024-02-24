# change the path of cross sections if necessary
# use the following commande to set the openmc environment and cross section data path
# source bash_scripts/openmc_env.sh

# Cross sections based on ENDF-B8.0
# export OPENMC_CROSS_SECTIONS=$HOME/Py-OpenMC-2023/data/endfb80_hdf5/cross_sections.xmlexport OPENMC_CROSS_SECTIONS=$HOME/Py-OpenMC-2023/data/endfb80_hdf5/cross_sections.xml

# Cross sections based on ENDF-B7.1
export OPENMC_CROSS_SECTIONS=$HOME/Py-OpenMC-2023/data/endfb80_hdf5/cross_sections.xmlexport OPENMC_CROSS_SECTIONS=$HOME/Py-OpenMC-2023/data/endfb71_hdf5/cross_sections.xml



conda activate openmc-py3.7
export HDF5_USE_FILE_LOCKING=FALSE
