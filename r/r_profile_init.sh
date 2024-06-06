#!/bin/bash

cat >>/root/.Rprofile <<EOL
## in R code:
# lib_path <- "/dbfs{R_LIB_PATH_MOUNTED}"
lib_path <- "/dbfs/mnt/dais24_demo/faster_lib_loads/14.3LTS_ML/libs/r/" 
.libPaths(c(.libPaths(), lib_path))
EOL


## instead of using env variable
# R_PROFILE_USER=/dbfs/mnt/dais24_demo/faster_lib_loads/14.3LTS_ML/clusterEnv/r_profile/.Rprofile