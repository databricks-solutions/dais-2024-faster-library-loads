#! /usr/bin/env bash

mkdir -p /root/.ipython/profile_default
rm -rf /root/.ipython/profile_default/startup
## need to add "/dbfs" to mounted IPYTHON_PROFILE_PATH 
ln -s /dbfs/mnt/dais24_demo/faster_lib_loads/13.3LTS_ML/clusterEnv/.ipython/profile_pyenv/startup /root/.ipython/profile_default/startup

## symbolic link 
# use the ln command to create the links for the files and the -s option to specify that this will be a symbolic link