# Databricks notebook source
# MAGIC %md
# MAGIC ## Overview of how to set up mounted path and pre-install libraries/packages:
# MAGIC
# MAGIC 1. Establish a standard convention within your Organization and your shared workspace for `{project}/{dbr_version}/{Library}` &/or `{.ipython/profile/startup}` paths   
# MAGIC
# MAGIC 2. Install libraries and packages in the path identified above as `PYTHON_LIB_PATH_MOUNTED`   
# MAGIC
# MAGIC 3. Set up Cluster Configs:  
# MAGIC     - Create a `.ipython/profile_{pyenv}/startup/00_{pyenv}.py`file which executes the command to append `PYTHON_LIB_PATH_MOUNTED` with pre-installed python libraries to `sys.path()`.  
# MAGIC
# MAGIC     - 3A [Recommended]: Set the Cluster Init Scripts with path to Volumes Init Script, which will create a symbolic `IPYTHON_PROFILE_PATH/startup` and `/root/ipython/profile_default/startup` paths.       
# MAGIC     - 3B [Alternative]: Create a Cluster Environment variable `IPYTHON_PROFILE_DIR` and set the  Cluster Init Scripts with path to Volumes Init Script, which will create a symbolic `IPYTHON_PROFILE_DIR/startup` and `/root/ipython/profile_default/startup` paths       
# MAGIC
# MAGIC
# MAGIC ##### Post Installation of Library/Packages + Cluster Init Script / Environment Variable set up
# MAGIC With our Libs pre-installed + Cluster Init Script (via Volumes) and if required, Cluster Environment Variable set up, we will now make sure that the mounted path is `Read-Only`:   
# MAGIC
# MAGIC 4. Unmount + Remount Storage onto DBFS with Read-Only permissions     
# MAGIC
# MAGIC 5. Post Compute re-start/updates .... [TEST] Python_library loads!

# COMMAND ----------

# MAGIC %md
# MAGIC ### 1. Establish a standard convention within your Organization and your shared workspace for `{project}/{dbr_version}/{Library}` &/or `{.ipython/profile/}` paths

# COMMAND ----------

# DBTITLE 1,Folder paths to organize project | dbr_version | libraries
PROJECT_GROUP = "dais24_demo" 
PROJECT_DIR = "faster_lib_loads"
DBR_VERSION = "13.3LTS_ML" 

PATH_MOUNTED = f"/mnt/{PROJECT_GROUP}/" ## points to blobContainerName = "dais24" 
PYTHON_LIB_PATH_MOUNTED = f"/mnt/{PROJECT_GROUP}/{PROJECT_DIR}/{DBR_VERSION}/libs/python/" 

IPYTHON_PROFILE_PATH = f"/mnt/{PROJECT_GROUP}/{PROJECT_DIR}/{DBR_VERSION}/clusterEnv/.ipython/profile_pyenv/"

print('PATH_MOUNTED :', PATH_MOUNTED)
print('PYTHON_LIB_PATH_MOUNTED :', PYTHON_LIB_PATH_MOUNTED)
print('IPYTHON_PROFILE_PATH :', IPYTHON_PROFILE_PATH)


# COMMAND ----------

# DBTITLE 1,Blob Storage to associate PATH_MOUNTED  as dbfs/mnt path to install specific library  packages
from IPython.display import Image
Image(filename="/Workspace/Users/may.merkletan@databricks.com/Faster_Lib_Loads/markdown_images/access_storage_container.png", width=1600)

# COMMAND ----------

# DBTITLE 1,Create Shared Access Tokens
from IPython.display import Image
Image(filename="/Workspace/Users/may.merkletan@databricks.com/Faster_Lib_Loads/markdown_images/generateSAStoken.png", width=1600)

# COMMAND ----------

# DBTITLE 1,readNwrite | read-only secrets are pre-configured to user/group scope
secret_scope_name = "dais24_fasterlibloads" 
dbutils.secrets.list(f'{secret_scope_name}') 

# COMMAND ----------

# DBTITLE 1,Function to mount with Shared Access Tokens stored as Scope Secrets 
storageAccountName = "hlsfieldexternal"
blobContainerName = "dais24" 
secret_scope_name = "dais24_fasterlibloads"
r_sasToken = dbutils.secrets.get(f'{secret_scope_name}','r_token')
rwr_sasToken = dbutils.secrets.get(f'{secret_scope_name}','rwr_token')

mountPoint = PATH_MOUNTED 

def mount_azblob(storageAccountName, blobContainerName, mountPoint, sasToken):

  # first unmount if already mounted 
  if any(mount.mountPoint == mountPoint for mount in dbutils.fs.mounts()):
    dbutils.fs.unmount(mountPoint)
    
  try:
    # mount to specified mountPoint
    dbutils.fs.mount(
      source = f"wasbs://{blobContainerName}@{storageAccountName}.blob.core.windows.net",
      mount_point = mountPoint,    
      extra_configs = {f"fs.azure.sas.{blobContainerName}.{storageAccountName}.blob.core.windows.net": sasToken}
    )
    print("mount succeeded!")
  except Exception as e:
    print("mount exception", e)

    dbutils.fs.refreshMounts()

# COMMAND ----------

# DBTITLE 1,mount with rwr_sasToken
mount_azblob(storageAccountName, blobContainerName, mountPoint, rwr_sasToken)

# COMMAND ----------

# DBTITLE 1,Check mounts
[p for p in dbutils.fs.mounts() if f"{blobContainerName}" in p.source]

# COMMAND ----------

print(PATH_MOUNTED)
display(dbutils.fs.ls(f'{PATH_MOUNTED}'))

# COMMAND ----------

PYTHON_LIB_PATH_MOUNTED

# COMMAND ----------

# MAGIC %md
# MAGIC ### 2. Install libraries and packages in the path identified above as `PYTHON_LIB_PATH_MOUNTED`. 

# COMMAND ----------

# DBTITLE 1,If not already exist, mkdirs for path to install libraries
dbutils.fs.mkdirs(f"{PYTHON_LIB_PATH_MOUNTED}")

# COMMAND ----------

# MAGIC %md
# MAGIC #### 2.1 Create os.environ target path variable for use with pip install
# MAGIC - NB: `/dbfs` prefix is required for correct path location 

# COMMAND ----------

# DBTITLE 1,Create os.environ path variable 
import os
os.environ["PYTHON_LIB_PATH_MOUNTED"]=f'/dbfs{PYTHON_LIB_PATH_MOUNTED}'
os.environ["PYTHON_LIB_PATH_MOUNTED"]

# COMMAND ----------

# MAGIC %sh echo $PYTHON_LIB_PATH_MOUNTED

# COMMAND ----------

# MAGIC %md
# MAGIC #### 2.2 Install libraries of interest to `$PYTHON_LIB_PATH_MOUNTED`

# COMMAND ----------

# DBTITLE 1,Update pip + install libs 
# MAGIC %sh pip install --upgrade pip

# COMMAND ----------

# MAGIC %md
# MAGIC #### 2.2.1 Check that libraries aren't already installed on cluster by default 

# COMMAND ----------

# DBTITLE 0,check that libs aren't installed on cluster
import easydict

# COMMAND ----------

import torch_scatter

# COMMAND ----------

import torch_sparse

# COMMAND ----------

import torch_spline_conv

# COMMAND ----------

import torch_geometric

# COMMAND ----------

# MAGIC %md
# MAGIC #### 2.2.2 Install libraries to `$PYTHON_LIB_PATH_MOUNTED`

# COMMAND ----------

# DBTITLE 1,Libs 2 install
# easydict torch-scatter torch-sparse torch-spline-conv torch_geometric

# Install commands took in total approx. ~45mins to install 

# COMMAND ----------

# DBTITLE 1,install easydict
# MAGIC %sh pip install --upgrade easydict --target=$PYTHON_LIB_PATH_MOUNTED

# COMMAND ----------

# DBTITLE 1,install torch-scatter
# MAGIC %sh pip install --upgrade torch-scatter --target=$PYTHON_LIB_PATH_MOUNTED --verbose

# COMMAND ----------

# DBTITLE 1,install torch-sparse
# MAGIC %sh pip install --upgrade torch-sparse --target=$PYTHON_LIB_PATH_MOUNTED --verbose

# COMMAND ----------

# DBTITLE 1,install torch-spline-conv
# MAGIC %sh pip install --upgrade torch-spline-conv --target=$PYTHON_LIB_PATH_MOUNTED --verbose

# COMMAND ----------

# DBTITLE 1,- check cuda version for torch_geometric
# MAGIC %sh ls -l /usr/local | grep cuda

# COMMAND ----------

# DBTITLE 1,- check torch version for torch_geometric
import torch;
torch.__version__ #'1.13.1+cu117'

# COMMAND ----------

# DBTITLE 1,install torch_geometric
# MAGIC %sh pip install torch_geometric --target=$PYTHON_LIB_PATH_MOUNTED --verbose

# COMMAND ----------

# dbutils.library.restartPython()

# COMMAND ----------

# DBTITLE 1,Check libs installed 
display(dbutils.fs.ls(f"{PYTHON_LIB_PATH_MOUNTED}")) 

# COMMAND ----------

# MAGIC %md
# MAGIC #### 2.3 Append mounted path with pre-installed libraries to `sys.path`

# COMMAND ----------

# DBTITLE 1,Append PYTHON_LIB_PATH_MOUNTED to `sys.path`
import sys
sys.path.append(f"/dbfs{PYTHON_LIB_PATH_MOUNTED}") 

# COMMAND ----------

# DBTITLE 1,Check sys.path for appended path 
sys.path

# COMMAND ----------

# MAGIC %md
# MAGIC #### 2.4 Quick test of appended mounted path with pre-installed libraries to sys.path

# COMMAND ----------

# DBTITLE 1,Test library import
import os
import torch_geometric
path = os.path.abspath(torch_geometric.__file__)
path

# COMMAND ----------

# DBTITLE 0,Test import 
from torch_geometric.data import Data, InMemoryDataset, DataLoader
from torch_geometric.nn import NNConv, BatchNorm, EdgePooling, TopKPooling, global_add_pool
from torch_geometric.utils import get_laplacian, to_dense_adj

# COMMAND ----------

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.nn import Sequential, Linear, ReLU, Sigmoid, Tanh, Dropout, LeakyReLU
from torch.autograd import Variable
from torch.distributions import normal, kl

# COMMAND ----------

display(dbutils.fs.ls(f"{PYTHON_LIB_PATH_MOUNTED}"))

# COMMAND ----------

# MAGIC %md
# MAGIC ### 3. Set the Cluster Environment variable:
# MAGIC
# MAGIC We will leverage the unique properties of the default `{##}_{filename}.py` files within `/root/.ipython/profile_default/startup/` path [## LINK to info.].      
# MAGIC
# MAGIC By symbolically linking our corresponding `IPYTHON_PROFILE_PATH` to the default `/root/.ipython/profile_default/startup/` path, our "bespoke" `.ipython/profile_pyenv/startup/00_pyenv.py` will execute our desired code for appending the `PYTHON_LIB_PATH_MOUNTED` with pre-installed python libraries to `sys.path()` during cluster initialization. 
# MAGIC
# MAGIC To achieve this, we will: 
# MAGIC
# MAGIC  - [3.1] Create a workspace `.ipython/profile/startup/00_pyenv.py` file which executes the command to append `PYTHON_LIB_PATH_MOUNTED` with pre-installed python libraries to `sys.path()`.  
# MAGIC
# MAGIC  - [3.2] Copy the workspace `.ipython/profile/startup` files to our mounted external cloud storage `IPYTHON_PROFILE_PATH` with similar folder structure.  
# MAGIC
# MAGIC  - [3.3] Use `init.sh` script in UC Volumes to create symbolic link between `{IPYTHON_PROFILE_PATH or IPYTHON_PROFILE_DIR}/startup` and `/root/ipython/profile_default/startup` paths.    
# MAGIC
# MAGIC     This can be in the following form:   
# MAGIC      - [A] Direct association between `IPYTHON_PROFILE_PATH` to the default `/root/.ipython/profile_default/startup/` path.    
# MAGIC
# MAGIC      - [B] Creating a Cluster Environment Variable : `IPYTHON_PROFILE_DIR` and associating `IPYTHON_PROFILE_DIR` to the default `/root/.ipython/profile_default/startup/` path -- this option means that you can update the cluster Advanced Environmental Variable without having to code-update the `init.sh` files.
# MAGIC
# MAGIC

# COMMAND ----------

# MAGIC %md
# MAGIC #### 3.1 Create a workspace `.ipython/profile/startup/00_pyenv.py` file which executes the command to append `PYTHON_LIB_PATH_MOUNTED` with pre-installed python libraries to `sys.path()`.

# COMMAND ----------

# DBTITLE 1,Create a workspace .ipython/profile_pyenv/startup/00_pyenv.py with the following code:
# MAGIC %sh head /Workspace/Users/may.merkletan@databricks.com/Faster_Lib_Loads/.ipython/profile_pyenv/startup/00_pyenv.py

# COMMAND ----------

# DBTITLE 1,Structure of the .ipython/profile_pyenv/startup/ folder also includes a README 
# MAGIC %sh ls -lah /Workspace/Users/may.merkletan@databricks.com/Faster_Lib_Loads/.ipython/profile_pyenv/startup/

# COMMAND ----------

# DBTITLE 1,.ipython/profile_pyenv/startup/README details:
# MAGIC %sh head /Workspace/Users/may.merkletan@databricks.com/Faster_Lib_Loads/.ipython/profile_pyenv/startup/README

# COMMAND ----------

# MAGIC %md
# MAGIC #### 3.2 Copy the workspace `ipython/profile/startup` files to our mounted external cloud storage `IPYTHON_PROFILE_PATH` with similar folder structure.  

# COMMAND ----------

# DBTITLE 1,copy workspace .ipython/profile_pyenv folder to mounted IPYTHON_PROFILE_PATH
# MAGIC %sh cp -r /Workspace/Users/may.merkletan@databricks.com/Faster_Lib_Loads/.ipython/profile_pyenv /dbfs/mnt/dais24_demo/faster_lib_loads/13.3LTS_ML/clusterEnv/.ipython/

# COMMAND ----------

# DBTITLE 1,check copied startup/00_pyenv.py script
# MAGIC %fs head dbfs:/mnt/dais24_demo/faster_lib_loads/13.3LTS_ML/clusterEnv/.ipython/profile_pyenv/startup/00_pyenv.py

# COMMAND ----------

# MAGIC %md
# MAGIC #### 3.3A Use init.sh scripts in UC Volumes to create symbolic link between `IPYTHON_PROFILE_PATH/startup` and `/root/ipython/profile_default/startup` paths. 

# COMMAND ----------

# DBTITLE 1,[3A.1] init script : create symbolic link for mounted IPYTHON_PROFILE_PATH/startup to /root/ipython/profile_default/startup path
!head /Workspace/Users/may.merkletan@databricks.com/Faster_Lib_Loads/.ipython/ipython_profile_symlink2mnt_init.sh

# COMMAND ----------

# DBTITLE 1,[3A.2] copy workspace .init file to UC Volumes path to init_scripts
!cp -r /Workspace/Users/may.merkletan@databricks.com/Faster_Lib_Loads/.ipython/ipython_profile_symlink2mnt_init.sh /Volumes/mmt_external/dais24/ext_vols/init_scripts/

# COMMAND ----------

# DBTITLE 1,[3A.3] check copied .init file content
print(dbutils.fs.head("/Volumes/mmt_external/dais24/ext_vols/init_scripts/ipython_profile_symlink2mnt_init.sh"))

# COMMAND ----------

# DBTITLE 1,[3A.4] Add Volumes  init script to Cluster
from IPython.display import Image
Image(filename="/Workspace/Users/may.merkletan@databricks.com/Faster_Lib_Loads/markdown_images/cluster_ipython_profile_symlink_initVol.png", width=1600)

# COMMAND ----------

# MAGIC %md
# MAGIC #### 3.3B Use `init.sh` scripts in UC Volumes to create symbolic link between `IPYTHON_PROFILE_DIR/startup` and `/root/ipython/profile_default/startup paths`. 

# COMMAND ----------

# DBTITLE 1,[3B.1] create an .init script to create symbolic link for Cluster Env. Var IPYTHON_PROFILE_DIR to /root/ipython/profile/startup
!cat /Workspace/Users/may.merkletan@databricks.com/Faster_Lib_Loads/.ipython/ipython_profile_clusterEnvVar_init.sh

# COMMAND ----------

# DBTITLE 1,[3B.2] copy workspace .init file to UC Volumes path to init_scripts
## copy .init script to mounted external UC Volumes path 
!cp -r /Workspace/Users/may.merkletan@databricks.com/Faster_Lib_Loads/.ipython/ipython_profile_clusterEnvVar_init.sh /Volumes/mmt_external/dais24/ext_vols/init_scripts/

# COMMAND ----------

# DBTITLE 1,[3B.3] check copied .init file content
## check contents of coped .init script
print(dbutils.fs.head("/Volumes/mmt_external/dais24/ext_vols/init_scripts/ipython_profile_clusterEnvVar_init.sh"))

# COMMAND ----------

# DBTITLE 1,[3B.4] ADD Add Volumes  init script + Adv. Env. Var to Cluster
from IPython.display import Image
Image(filename="/Workspace/Users/may.merkletan@databricks.com/Faster_Lib_Loads/markdown_images/cluster_ipython_profile_EnvVar_initVol.png", width=1600)

# COMMAND ----------

from IPython.display import Image
Image(filename="/Workspace/Users/may.merkletan@databricks.com/Faster_Lib_Loads/markdown_images/cluster_ipython_profile_user_EnvVar.png", width=1600)

# COMMAND ----------

# MAGIC %md
# MAGIC ### 4 Unmount + Remount Storage onto DBFS with Read-Only permissions 
# MAGIC Now that the Python Lbs/packages are installed,   
# MAGIC We can unmount the (Azure blob) storage with `readNwrite` permissions    
# MAGIC And re-mount the storage path with `read-only` permissions    

# COMMAND ----------

# DBTITLE 1,Re-mount external blob storage with Read-only access token
mount_azblob(storageAccountName, blobContainerName, mountPoint, r_sasToken)

# COMMAND ----------

# DBTITLE 1,List mounts
[p for p in dbutils.fs.mounts() if "dais24" in p.source]

# COMMAND ----------

# DBTITLE 1,Check Read-only permissions on mount | List mount path
# MAGIC %fs ls "dbfs:/mnt/dais24_demo/faster_lib_loads/13.3LTS_ML/libs/python/"

# COMMAND ----------

# DBTITLE 1,Check Read-only permissions on mount |  mkdirs: should fail if read-only Access Token is used
# MAGIC %fs mkdir r/.Rprofile "dbfs:/mnt/dais24_demo/faster_lib_loads/13.3LTS_ML/libs/test"

# COMMAND ----------

# MAGIC %md 
# MAGIC ### 5. TEST Cluster with new configs / RESTART Cluster!

# COMMAND ----------

# DBTITLE 1,check sys.path append | '/dbfs/mnt/hls_demo/13.3LTS_ML/libs/python/'
import sys
sys.path

# COMMAND ----------

# DBTITLE 1,import / check absolute path of library installed
import os
import torch_geometric
path = os.path.abspath(torch_geometric.__file__)
path

# COMMAND ----------

# DBTITLE 1,load torch_geometric
from torch_geometric.data import Data, InMemoryDataset, DataLoader
from torch_geometric.nn import NNConv, BatchNorm, EdgePooling, TopKPooling, global_add_pool
from torch_geometric.utils import get_laplacian, to_dense_adj

# COMMAND ----------

# DBTITLE 1,load torch
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.nn import Sequential, Linear, ReLU, Sigmoid, Tanh, Dropout, LeakyReLU
from torch.autograd import Variable
from torch.distributions import normal, kl

# COMMAND ----------

# DBTITLE 1,TEST library load
# import torch
# from torch_geometric.data import Data

edge_index = torch.tensor([[0, 1, 1, 2],
                           [1, 0, 2, 1]], dtype=torch.long)
x = torch.tensor([[-1], [0], [1]], dtype=torch.float)

data = Data(x=x, edge_index=edge_index)
Data(edge_index=[2, 4], x=[3, 1])


# COMMAND ----------

edge_index = torch.tensor([[0, 1],
                           [1, 0],
                           [1, 2],
                           [2, 1]], dtype=torch.long)
x = torch.tensor([[-1], [0], [1]], dtype=torch.float)

data = Data(x=x, edge_index=edge_index.t().contiguous())
data

# COMMAND ----------

data.validate(raise_on_error=True)

# COMMAND ----------

# DBTITLE 1,Test networkx
import networkx as nx

edge_index = torch.tensor([[0, 1, 1, 2],
                           [1, 0, 2, 1]], dtype=torch.long)
x = torch.tensor([[-1], [0], [1]], dtype=torch.float)

data = torch_geometric.data.Data(x=x, edge_index=edge_index)
g = torch_geometric.utils.to_networkx(data, to_undirected=True)
nx.draw(g)

# COMMAND ----------


