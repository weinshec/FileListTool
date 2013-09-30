#!/bin/bash

export ATLAS_LOCAL_ROOT_BASE=/cvmfs/atlas.cern.ch/repo/ATLASLocalRootBase
alias setupATLAS='source ${ATLAS_LOCAL_ROOT_BASE}/user/atlasLocalSetup.sh'

setupATLAS

export DQ2_LOCAL_SITE=MAINZGRID_LOCALGROUPDISK
localSetupDQ2Client --skipConfirm --quiet

export RUCIO_ACCOUNT=$(whoami)
