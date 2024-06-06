# Append mounted path with pre-installed python libraries to sys.path()

## need to add "/dbfs" to mounted path 
PYTHON_LIB_PATH_MOUNTED = "/dbfs/mnt/dais24_demo/faster_lib_loads/13.3LTS_ML/libs/python/"

import sys
sys.path.append(PYTHON_LIB_PATH_MOUNTED)
