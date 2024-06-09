# Databricks notebook source
# MAGIC %md 
# MAGIC ### DEMO: Cluster + PreInstalled R Packages 
# MAGIC
# MAGIC <!-- (init script: append `R_LIB_PATH_MOUNTED` with pre-installed packages to `.libPaths()` as `/root/.Rprofile`)  -->
# MAGIC
# MAGIC <!-- 
# MAGIC Cluster: `mmt_14.3LTSML_cpu_(fasterlibloads_r)`
# MAGIC
# MAGIC Volumes init: `/Volumes/mmt_external/dais24/ext_vols/init_scripts/r_profile_init.sh` 
# MAGIC -->

# COMMAND ----------

# DBTITLE 1,Check `.libPaths()`
.libPaths()

# COMMAND ----------

# MAGIC %md
# MAGIC ### Load up some libraries!

# COMMAND ----------

# DBTITLE 1,rcompanion
library(rcompanion)

# COMMAND ----------

# DBTITLE 1,compareLM: Compare fit statistics for linear models
rcompanion::compareLM 

# COMMAND ----------

# MAGIC %md
# MAGIC ### Let's test it out

# COMMAND ----------

# DBTITLE 1,Load up dataset 
BrendonSmall <- rcompanion::BrendonSmall
BrendonSmall

# COMMAND ----------

# DBTITLE 1,Define a few different linear models 
BrendonSmall$Calories = as.numeric(BrendonSmall$Calories)

BrendonSmall$Calories2 = BrendonSmall$Calories * BrendonSmall$Calories
BrendonSmall$Calories3 = BrendonSmall$Calories * BrendonSmall$Calories * BrendonSmall$Calories
BrendonSmall$Calories4 = BrendonSmall$Calories * BrendonSmall$Calories * BrendonSmall$Calories * BrendonSmall$Calories

model.1 = lm(Sodium ~ Calories, data = BrendonSmall)
model.2 = lm(Sodium ~ Calories + Calories2, data = BrendonSmall)
model.3 = lm(Sodium ~ Calories + Calories2 + Calories3, data = BrendonSmall)
model.4 = lm(Sodium ~ Calories + Calories2 + Calories3 + Calories4,
             data = BrendonSmall)

rcompanion::compareLM(model.1, model.2, model.3, model.4)

# COMMAND ----------

# DBTITLE 1,Run pairwiseModelAnova to assess model fit
rcompanion::pairwiseModelAnova(model.1, model.2, model.3, model.4)

# COMMAND ----------

# DBTITLE 1,Q: loaded package location?
system.file(package="rcompanion")

# COMMAND ----------

# MAGIC %md
# MAGIC ---              

# COMMAND ----------

# DBTITLE 1,Default DBR R package path for `ggplot2`
system.file(package="ggplot2") 

# COMMAND ----------

# DBTITLE 1,However specific packages require different version dependencies
system.file(package = "ggiraphExtra") ## requires ggplot2 version: 3.5.0

# COMMAND ----------

# DBTITLE 1,Load library with specific lib.loc = pre-installed lib-path
library("ggiraphExtra", lib.loc=.libPaths()[7])
ggiraphExtra::ggPoints

# COMMAND ----------

# DBTITLE 1,Q: loaded ggplot2 package location?
system.file(package="ggplot2") ## loaded dependecies are found on pre-installed path

# COMMAND ----------

mtcars

# COMMAND ----------

# DBTITLE 1,Version specific library/package loads
library(ggplot2, lib.loc = .libPaths()[7]) # ggiraphExtra require version 3.5.0
library(ggiraphExtra, lib.loc = .libPaths()[7]) 
library(ggiraph, lib.loc = .libPaths()[7]) 
library(plyr) 

ggPoints(aes(x=wt,y=mpg,color=am),data=mtcars,method="lm")

# COMMAND ----------

iris

# COMMAND ----------

ggRadar(data=iris,aes(color=Species))

# COMMAND ----------

# DBTITLE 1,If just using ggplot2 -- either default/pre-installed package will work...
ggplot(diamonds, aes(carat, price, colour = clarity, group = clarity)) + geom_point(alpha = 0.5) + stat_smooth()

# COMMAND ----------

diamonds

# COMMAND ----------

# DBTITLE 0,Q: loaded ggplot2 package location?
system.file(package="ggplot2")

# COMMAND ----------

# DBTITLE 1,packages installed 
installed_packages <- installed.packages()
packINFO <- data.frame(Package = installed_packages[, "Package"],
                       Version = installed_packages[, "Version"],
                       loc = installed_packages[, "LibPath"])

knitr::kable(packINFO, format = "markdown")

# COMMAND ----------


