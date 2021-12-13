# Databricks notebook source
# MAGIC %run ./includes/utils

# COMMAND ----------

mountDataLake(clientId="64492359-3450-4f1e-be01-8717789fd01e",
              clientSecret=dbutils.secrets.get(
                  scope="datalake", key="adappsecret"),
              tokenEndPoint="https://login.microsoftonline.com/0b55e01a-573a-4060-b656-d1a3d5815791/oauth2/token",
              storageAccountName="datalakefdvu573zsnpjo",
              containerName="data")
