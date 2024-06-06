## Ref ipython init.sh 
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