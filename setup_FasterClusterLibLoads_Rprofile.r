# Databricks notebook source
# MAGIC %md
# MAGIC ## Overview of how to set up mounted path and pre-install libraries/packages:
# MAGIC
# MAGIC 1. Establish a standard convention within your Organization and your shared workspace for `{project}/{dbr_version}/{Library}` &/or `{.Rprofile}` paths 
# MAGIC
# MAGIC 2. Install libraries and packages in the path identified as `R_LIB_PATH_MOUNTED`   
# MAGIC
# MAGIC 3. Set up Cluster Configs:      
# MAGIC
# MAGIC     - 3A [Recommended]: Set the Cluster Init Scripts with path to Volumes Init Script      
# MAGIC     - 3B [Alternative]: Set the Cluster Environment variable `R_PROFILE_USER`     
# MAGIC     
# MAGIC      
# MAGIC ##### Post Installation of Library/Packages + Cluster Init Script / Environment Variable set up
# MAGIC With our Libs pre-installed + Cluster Init Script (via Volumes) OR Environment Variables set up, we will now make sure that the mounted path is `Read-Only`:          
# MAGIC
# MAGIC 4. Unmount + Remount Storage onto DBFS with `Read-Only` permissions        
# MAGIC
# MAGIC 5. Post Compute re-start/updates .... [TEST] R_library loads! 

# COMMAND ----------

## START cluster for setup: mmt_dbr14.3LTSML_cpu

# COMMAND ----------

# MAGIC %md 
# MAGIC ### 1. Establish a standard convention within your Organization and your shared workspace for `{project}/{dbr_version}/{Library}` &/or `{.Rprofile}` paths
# MAGIC

# COMMAND ----------

# MAGIC %md 
# MAGIC #### 1.1 Use Python and [dbutils](https://docs.databricks.com/en/dev-tools/databricks-utils.html) to  
# MAGIC - set up `Project`, `Library` paths
# MAGIC - extract configured `Scopes` and `Secrets` [[AWS](https://docs.databricks.com/en/security/secrets/secret-scopes.html) | [Azure](https://learn.microsoft.com/en-us/azure/databricks/security/secrets/secret-scopes)] to store e.g. `External StorageBlob e.g. ADLS/S3` Shared Access Tokens 

# COMMAND ----------

# DBTITLE 1,Folder paths to organize project | dbr_version | libraries
# MAGIC %python
# MAGIC
# MAGIC PROJECT_GROUP = "dais24_demo"  
# MAGIC PROJECT_DIR = "faster_lib_loads"
# MAGIC DBR_VERSION = "14.3LTS_ML" 
# MAGIC
# MAGIC PATH_MOUNTED = f"/mnt/{PROJECT_GROUP}/" ## points to blobContainerName = "dais24" 
# MAGIC R_LIB_PATH_MOUNTED = f"/mnt/{PROJECT_GROUP}/{PROJECT_DIR}/{DBR_VERSION}/libs/r/"
# MAGIC
# MAGIC R_PROFILE_PATH = f"/mnt/{PROJECT_GROUP}/{PROJECT_DIR}/{DBR_VERSION}/clusterEnv/r_profile/" #.Rprofile
# MAGIC
# MAGIC print (f"PATH_MOUNTED: {PATH_MOUNTED}")
# MAGIC print(f"R_LIB_PATH_MOUNTED: {R_LIB_PATH_MOUNTED}")
# MAGIC print(f"R_PROFILE_PATH: {R_PROFILE_PATH}")

# COMMAND ----------

# MAGIC %md
# MAGIC #### 1.2 Blob Storage to associate PATH_MOUNTED  as `dbfs/mnt path to install specific r packages`

# COMMAND ----------

# DBTITLE 1,Blob Storage to associate PATH_MOUNTED 
# MAGIC %python
# MAGIC from IPython.display import Image
# MAGIC Image(filename="/Workspace/Users/{username@email.com}/Faster_Lib_Loads/markdown_images/access_storage_container.png", width=1600)

# COMMAND ----------

# DBTITLE 1,Create Shared Access Tokens
# MAGIC %python
# MAGIC from IPython.display import Image
# MAGIC Image(filename="/Workspace/Users/{username@email.com}/Faster_Lib_Loads/markdown_images/generateSAStoken.png", width=1600)

# COMMAND ----------

# DBTITLE 1,readNwrite | read-only secrets are pre-configured to user/group scope
# MAGIC %python
# MAGIC secret_scope_name = "dais24_fasterlibloads" 
# MAGIC dbutils.secrets.list(f'{secret_scope_name}') 

# COMMAND ----------

# DBTITLE 1,Function to mount with Shared Access Tokens stored as Scope Secrets 
# MAGIC %python
# MAGIC
# MAGIC storageAccountName = "hlsfieldexternal"
# MAGIC blobContainerName = "dais24" 
# MAGIC secret_scope_name = "dais24_fasterlibloads"
# MAGIC r_sasToken = dbutils.secrets.get(f'{secret_scope_name}','r_token')
# MAGIC rwr_sasToken = dbutils.secrets.get(f'{secret_scope_name}','rwr_token')
# MAGIC
# MAGIC mountPoint = PATH_MOUNTED 
# MAGIC
# MAGIC def mount_azblob(storageAccountName, blobContainerName, mountPoint, sasToken):
# MAGIC
# MAGIC   # first unmount if already mounted 
# MAGIC   if any(mount.mountPoint == mountPoint for mount in dbutils.fs.mounts()):
# MAGIC     dbutils.fs.unmount(mountPoint)
# MAGIC     
# MAGIC   try:
# MAGIC     # mount to specified mountPoint
# MAGIC     dbutils.fs.mount(
# MAGIC       source = f"wasbs://{blobContainerName}@{storageAccountName}.blob.core.windows.net",
# MAGIC       mount_point = mountPoint,    
# MAGIC       extra_configs = {f"fs.azure.sas.{blobContainerName}.{storageAccountName}.blob.core.windows.net": sasToken}
# MAGIC     )
# MAGIC     print("mount succeeded!")
# MAGIC   except Exception as e:
# MAGIC     print("mount exception", e)
# MAGIC
# MAGIC     dbutils.fs.refreshMounts()

# COMMAND ----------

# DBTITLE 1,mount with rwr_sasToken
# MAGIC %python
# MAGIC mount_azblob(storageAccountName, blobContainerName, mountPoint, rwr_sasToken)

# COMMAND ----------

# MAGIC %python
# MAGIC dbutils.fs.mounts()

# COMMAND ----------

# DBTITLE 1,Check mounted path
# MAGIC %python
# MAGIC [p for p in dbutils.fs.mounts() if f"{blobContainerName}" in p.source]

# COMMAND ----------

# DBTITLE 1,List mounted path
# MAGIC %python
# MAGIC mountpath = PATH_MOUNTED 
# MAGIC display(dbutils.fs.ls(mountpath))

# COMMAND ----------

# MAGIC %python
# MAGIC R_LIB_PATH_MOUNTED

# COMMAND ----------

# MAGIC %md
# MAGIC ### 2. Install libraries and packages in the path identified above as R_LIB_PATH_MOUNTED 

# COMMAND ----------

# MAGIC %md 
# MAGIC #### 2.1 Use R language for R packages installation 

# COMMAND ----------

# DBTITLE 1,Update package manager to posit.co/cran + linux binaries
# setup HTTP User agent so that posit knows what version of R we are using
options(HTTPUserAgent = sprintf("R/%s R (%s)", getRversion(), paste(getRversion(), R.version["platform"], R.version["arch"], R.version["os"])))

# https://packagemanager.posit.co/client/#/
# this will vary based on Databricks runtime version! 
options(repos = c(POSIT = "https://packagemanager.posit.co/cran/__linux__/jammy/latest", CRAN="http://cran.us.r-project.org"))

# Ensure that you update the URL to match the linux version of the runtime e.g. jammy or bionic
# options(repos = c(POSIT = "https://packagemanager.posit.co/cran/__linux__/<linux-release-name>/latest"))


# COMMAND ----------

# DBTITLE 1,if not already done so: mkdirs DBFS path to where your r-packages should live
# MAGIC %fs mkdirs "dbfs:/mnt/dais24_demo/faster_lib_loads/14.3LTS_ML/libs/r/"

# COMMAND ----------

# DBTITLE 1,check/list path to libs
# MAGIC %fs ls "dbfs:/mnt/dais24_demo/faster_lib_loads/14.3LTS_ML/libs/r/"

# COMMAND ----------

# DBTITLE 1,Install via posit/cran  to DBFS mounted path "once"
packages <- c("data.table","car","lmtest","mclust","fitdistrplus","mixtools","extraDistr","actuar","forecast","SparkR","stringi","assertthat","naniar","tidyverse","XML","xml2","rcompanion","librarian", "ggiraph","ggiraphExtra","gtable", "ggplot2")

R_LIB_PATH_MOUNTED <- '/dbfs/mnt/dais24_demo/faster_lib_loads/14.3LTS_ML/libs/r/'

install.packages(packages, 
                 dependencies=TRUE,
                 INSTALL_opts = "--no-lock", 
                 repos=c(POSIT = "https://packagemanager.posit.co/cran/__linux__/jammy/latest"),                 
                 lib = R_LIB_PATH_MOUNTED,                  
                 upgrade=TRUE, update.packages = TRUE,
                 quiet = FALSE, 
                 verbose = TRUE
                ) 

# dependencies are downloaded and installed to lib path 

# Command took 15.21 minutes -- by may.merkletan@databricks.com at 6/4/2024, 1:49:01 PM on mmt_14.3LTSML_cpu_(r)

# COMMAND ----------

# DBTITLE 1,Quick check on files installed to path
R_LIB_PATH_MOUNTED <- '/dbfs/mnt/dais24_demo/faster_lib_loads/14.3LTS_ML/libs/r/'

# COMMAND ----------

# MAGIC %fs ls /mnt/dais24_demo/faster_lib_loads/14.3LTS_ML/libs/r/

# COMMAND ----------

# MAGIC %md
# MAGIC #### 2.2 Helpful quick check on `libsPath()` appending 

# COMMAND ----------

# DBTITLE 1,Append  R_LIB_PATH_MOUNTED to .libPaths()
R_LIB_PATH_MOUNTED <- '/dbfs/mnt/dais24_demo/faster_lib_loads/14.3LTS_ML/libs/r/'
# Add the library to the search path at the start
.libPaths(c(.libPaths(), R_LIB_PATH_MOUNTED))

# COMMAND ----------

.libPaths()

# COMMAND ----------

# DBTITLE 1,List installed Packages | Versions | LibPaths
packINFO <- as.data.frame(installed.packages())[,c("Package", "Version", "LibPath")]
rownames(packINFO) <- NULL

print(packINFO) 
print(dim(packINFO))

# COMMAND ----------

# CHECK WHERE packages installed... 
system.file(package = "ggplot2") ## default DBR is found earlier in search path 

# COMMAND ----------

rcompanion::compareGLM

# COMMAND ----------

system.file(package = "rcompanion") 

# COMMAND ----------

system.file(package = "ggiraphExtra") ## 

# COMMAND ----------

library(ggiraphExtra, lib.loc=.libPaths()[7])
ggiraphExtra::ggBoxplot

# COMMAND ----------

system.file(package = "ggplot2") 

# COMMAND ----------

ggplot2::geom_boxplot

# COMMAND ----------

# MAGIC %md 
# MAGIC ### 3. Set up Cluster Configs:

# COMMAND ----------

# MAGIC %md 
# MAGIC ### 3A [Recommended]: Set the Cluster Init Scripts with path to Volumes Init Script 
# MAGIC
# MAGIC USE Volume `init.sh` to append pre-installed libraries/packages path `{R_LIB_PATH_MOUNTED}` to `.LibPaths()` leveraging `cat <<EOL`  to insert code into `/root/.Rprofile` during cluster startup
# MAGIC

# COMMAND ----------

# MAGIC %md 
# MAGIC ####  3A.1 We will use Python to help with `shell cmds`  
# MAGIC - create + copy Init shell script `r_profile_init.sh` from Workspace to Volumes

# COMMAND ----------

# DBTITLE 1,Create a workspace .sh init file with the following bash code
# MAGIC %python
# MAGIC !head -n 8 r/r_profile_init.sh

# COMMAND ----------

# DBTITLE 1,Copy this workspace .sh file to a Volumes path for init files
# MAGIC %python
# MAGIC !cp r/r_profile_init.sh /Volumes/mmt_external/dais24/ext_vols/init_scripts/r_profile_init.sh

# COMMAND ----------

# DBTITLE 1,Check contents of Volumes init file
# MAGIC %python
# MAGIC !head /Volumes/mmt_external/dais24/ext_vols/init_scripts/r_profile_init.sh

# COMMAND ----------

# MAGIC %md 
# MAGIC ####  3A.2 Next We will specify `Init Scripts` within `Cluster Advance options`

# COMMAND ----------

# DBTITLE 1,Cluster Init Scripts
# MAGIC %python
# MAGIC from IPython.display import Image
# MAGIC Image(filename="/Workspace/Users/may.merkletan@databricks.com/Faster_Lib_Loads/markdown_images/cluster_RProfile_InitVol.png", width=900)

# COMMAND ----------

# MAGIC %md
# MAGIC ### 3B [Alternative]: Set the Cluster Environment variable `R_PROFILE_USER`
# MAGIC

# COMMAND ----------

# MAGIC %md 
# MAGIC ####  3B.1 We will use Python and [dbutils](https://docs.databricks.com/en/dev-tools/databricks-utils.html) to  
# MAGIC - set up a workspace `.Rprofile` script 
# MAGIC - specify `.Rprofile` script to include path `{R_LIB_PATH_MOUNTED}` to pre-installed libraries/packages during cluster startup 
# MAGIC - copy workspace `.Rprofile` script to mounted `{R_PROFILE_USER_PATH}`

# COMMAND ----------

# DBTITLE 1,Create a workspace .Rprofile file with the following bash code
# MAGIC %python
# MAGIC !head r/.Rprofile

# COMMAND ----------

# DBTITLE 1,Copy this workspace .Rprofile file to a mounted R_PROFILE_USER_PATH  
# MAGIC %python
# MAGIC
# MAGIC dbutils.fs.mkdirs(f"{R_PROFILE_PATH}")
# MAGIC
# MAGIC R_PROFILE_FILEPATH = f"/dbfs{R_PROFILE_PATH}.Rprofile"
# MAGIC !echo $R_PROFILE_FILEPATH
# MAGIC
# MAGIC !cp r/.Rprofile $R_PROFILE_FILEPATH

# COMMAND ----------

# DBTITLE 1,check contents of .Rprofile script
# MAGIC %python
# MAGIC !head $R_PROFILE_FILEPATH

# COMMAND ----------

# MAGIC %md 
# MAGIC ####  3B.2 Next We will specify `Environment variables` within `Cluster Advance options`
# MAGIC
# MAGIC `R_PROFILE_USER=/dbfs/{PROJECT_GROUP}/{PROJECT_DIR}/{DBR_version}/{clusterEnv}/r_profile/.Rprofile`
# MAGIC
# MAGIC

# COMMAND ----------

# DBTITLE 1,Set Cluster Env Var
# MAGIC %python
# MAGIC from IPython.display import Image
# MAGIC Image(filename="/Workspace/Users/may.merkletan@databricks.com/Faster_Lib_Loads/markdown_images/cluster_RProfileUser_EnvVar.png", width=900)

# COMMAND ----------

# MAGIC %md
# MAGIC ### Post Installation of Library/Packages + Cluster Init Script / Environment Variable set up
# MAGIC With our Libs pre-installed + Cluster Init Script (via Volumes) OR Environment Variables set up, we will now make sure that the mounted path is Read-Only:  

# COMMAND ----------

# DBTITLE 0,[0] Mount as Read-Only
# MAGIC %md
# MAGIC ### 4. Unmount + Remount Storage onto DBFS with Read-Only permissions 
# MAGIC Now that the Rpackages are installed,   
# MAGIC We can unmount the (Azure blob) storage with `readNwrite` permissions    
# MAGIC And re-mount the storage path with `read-only` permissions    
# MAGIC
# MAGIC *We use `Python` to facilitate this step*
# MAGIC
# MAGIC <!-- ```
# MAGIC %python
# MAGIC mountpath = PATH_MOUNTED 
# MAGIC dbutils.fs.unmount(mountpath)
# MAGIC
# MAGIC dbutils.fs.refreshMounts()
# MAGIC ``` -->

# COMMAND ----------

# DBTITLE 1,Re-mount external blob storage with Read-only access token
# MAGIC %python
# MAGIC mount_azblob(storageAccountName, blobContainerName, mountPoint, r_sasToken)

# COMMAND ----------

# DBTITLE 1,List mounts
# MAGIC %python
# MAGIC [p for p in dbutils.fs.mounts() if "dais24" in p.source]

# COMMAND ----------

# DBTITLE 1,Check Read-only permissions on mount | List mount path
# MAGIC %fs ls "dbfs:/mnt/dais24_demo/faster_lib_loads/14.3LTS_ML/libs/r/"

# COMMAND ----------

# DBTITLE 1,Check Read-only permissions on mount |  mkdirs: should fail if read-only Access Token is used
# MAGIC %fs mkdirs "dbfs:/mnt/dais24_demo/faster_lib_loads/14.3LTS_ML/libs/test"

# COMMAND ----------

# MAGIC %md
# MAGIC ### 5. Post Compute re-start/updates 

# COMMAND ----------

# - Change compute to : mmt_14.3LTSML_cpu_(fasterlibloads_r) 

# COMMAND ----------

# DBTITLE 1,re/attach compute >> mounted path to libs/r should show up!
.libPaths()

# COMMAND ----------

# MAGIC %md
# MAGIC #### 5.1 [TEST] R_library loads

# COMMAND ----------

library(rcompanion) 

# COMMAND ----------

??rcompanion 

# COMMAND ----------

rcompanion::compareGLM

# COMMAND ----------

system.file(package="rcompanion")

# COMMAND ----------

system.file(package = "ggplot2") ## default path 

# COMMAND ----------

system.file(package = "ggiraphExtra") ## actually requires a more recent version of ggplot2 

# COMMAND ----------

library("ggiraphExtra", lib.loc=.libPaths()[7]) ## requires specifying path for more recent version of ggplot2
ggiraphExtra::ggBoxplot

# COMMAND ----------

system.file(package = "ggplot2") ## 

# COMMAND ----------

library(ggplot2, lib.loc = .libPaths()[7])
ggplot(diamonds, aes(carat, price, colour = clarity, group = clarity)) + geom_point(alpha = 0.3) + stat_smooth()

# COMMAND ----------

diamonds

# COMMAND ----------

system.file(package = "ggplot2") ## 

# COMMAND ----------


