#! /usr/bin/env bash

if [ -z ${IPYTHON_PROFILE_DIR+x} ];
then
    echo "IPYTHON_PROFILE_DIR is unset"
else
    echo "IPYTHON_PROFILE_DIR is set to '$IPYTHON_PROFILE_DIR'"
    mkdir -p /root/.ipython/profile_default
    rm -rf /root/.ipython/profile_default/startup
    ln -s $IPYTHON_PROFILE_DIR/startup /root/.ipython/profile_default/startup
fi

## symbolic link 
# use the ln command to create the links for the files and the -s option to specify that this will be a symbolic link

## Advanced Cluster Environment Configuration:
## IPYTHON_PROFILE_DRI=IPYTHON_PROFILE_PATH
# IPYTHON_PROFILE_DIR=/dbfs/mnt/dais24_demo/faster_lib_loads/13.3LTS_ML/clusterEnv/.ipython/profile_pyenv