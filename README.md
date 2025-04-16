# dais-2024-faster-library-loads

### Overview: 
`faster-library-loads` is a productivity hack to cluster library installation wait times. 

This repository contains demo notebooks for the corresponding DAIS2024 lightning talk:   
 > [GOODBYE TO CLUSTER WAIT TIME: HELLO LIGHTNING-FAST R/PY LIBRARY LOADS!](https://youtu.be/ajGahfVgkD0?feature=shared)!
 <!--- (https://www.databricks.com/dataaisummit/session/goodbye-cluster-wait-time-hello-lightning-fast-rpy-library-loads) --->

 > ABSTRACT: *Ever wished you could start up an interactive cluster without having to wait for libraries to be pulled down from repositories and installed before you could begin your work? You're not alone! Many people find themselves in this same situation, and to ‘save’ time they multitask while waiting, only to have the cluster terminate after a certain amount of time of inactivity, forcing them to start over. Imagine being able to skip this waiting game and have all the required libraries available right from the start. This can be a reality for R packages as well as Python libraries. The approach can also be applied to other DSML developments and workflows. There is a productivity hack that can have you load up libraries in under 60 seconds whenever your cluster spins up!*

---      

### Summary: 

The solution proposed is similar for both R and Python libraries/packages. 

The overarching message is **Pre-Install Once : Available Every Time** (whenever the cluster compute spins up)   

This is achieved by: 
 1. Testing installation of required packages/libraries in a suitable [Databricks Runtime](https://docs.databricks.com/aws/en/release-notes/runtime/) that will support the required dependencies. 
 
 2. Pre-installing required libraries/packages for a DS/ML project or workflow to a `{R/Python}_LIB_PATH_MOUNTED` path `dbfs/mnt` with `readOnly` access post installation. 

 3. This `{R/Python}_LIB_PATH_MOUNTED` path will be appended to the default library search path for either R `.libPaths()` or Python `sys.path()` within the R or Python `Profile` files that are associated with the paths referenced within respective `init.sh` scripts.  

 4. The `init.sh` scripts makes a symbolical link between user-defined and the corresponding default R or Python `Profile` paths:
    - [.Rprofile](https://docs.posit.co/ide/user/2023.06.1/ide/guide/environments/r/managing-r.html#rprofile) file is automatically sourced (if it exists) when R starts up and allows you to specify the startup script that will be sourced during the R startup process. 

    - [.ipython/profile_default/startup](https://ipython.readthedocs.io/en/stable/interactive/tutorial.html#startup-files) directory files will be executed as soon as the IPython shell is constructed, before any other code or scripts specified. The files will be run in lexicographical order of their names (and as such the order of the scripts to be run). 

 5. We add the corresponding Volumes `init.sh` scripts to R/Python specific Clusters Advanced Options. 

 6. Whenever the cluster initialization is complete, the project relevant libraries/packages should be available on the corresponding library or system search paths for R or Python. 

------

> [!IMPORTANT]
> The solution documented in this repo has been predominantly tested on Azure Databricks using Compute for Single Node | Single User Access mode.
> Please be aware that code modifications are likely neccesary for Databricks on AWS / GCP cloud and/or where other Compute Access modes are used. 

------     

> [!NOTE] 
> The following are packages/libraries (in addition to defaults on cluster dbr) used in the demo assets:     
  
##### R 
`dbr14.3LTS_ML`
  
  - data.table
  - car
  - lmtest
  - mclust
  - fitdistrplus
  - mixtools
  - extraDistr
  - actuar
  - forecast
  - stringi
  - assertthat
  - naniar
  - tidyverse
  - XML
  - xml2
  - rcompanion
  - librarian 
  - ggiraph
  - ggiraphExtra
  - gtable 
  - ggplot2

   ```
   Installation: 

   options(repos = c(POSIT = "https://packagemanager.posit.co/cran/__linux__/jammy/latest", 
                     CRAN="http://cran.us.r-project.org")
                     )

   #e.g. 
   install.packages(packages, 
                  dependencies=TRUE,
                  INSTALL_opts = "--no-lock", 
                  repos=c(POSIT = "https://packagemanager.posit.co/cran/__linux__/jammy/latest"),                 
                  lib = R_LIB_PATH_MOUNTED,                  
                  upgrade=TRUE, update.packages = TRUE,
                  quiet = FALSE, 
                  verbose = TRUE
                  ) 

   ```

##### Python
`dbr13.3LTS_ML`

- easydict https://pypi.org/project/easydict/
- torch-scatter https://pypi.org/project/torch-scatter/ | https://github.com/rusty1s/pytorch_scatter | 
- torch-sparse https://pypi.org/project/torch-sparse/
- torch-spline-conv https://pypi.org/project/torch-spline-conv/
- torch_geometric https://pypi.org/project/torch-geometric/ 


```
Installation:

pip install <library-name>
``` 


------      



