# Databricks notebook source
jar_file_list = dbutils.fs.ls("FileStore/Jars/jars/")
require_jar_dict = {}

for jar_file in jar_file_list:
    if "decodeTiHex2Str_UDF_V1_1_1" in jar_file[1]:
        require_jar_dict['decodeTiHex2Str_UDF_V1_1_1'] = jar_file[1]
    elif "AESEncryptionRotator_UDF_V1_0_1" in jar_file[1]:
        require_jar_dict['AESEncryptionRotator_UDF_V1_0_1'] = jar_file[1]
    elif "AESEncryption_UDF_V3_3_0" in jar_file[1]:
        require_jar_dict['AESEncryption_UDF_V3_3_0'] = jar_file[1]
    elif "CustomDateTime_Convertor_UDF_V2_1_0" in jar_file[1]:
        require_jar_dict['CustomDateTime_Convertor_UDF_V2_1_0'] = jar_file[1]

# COMMAND ----------        
        
%sql
drop function IF EXISTS encrypt
drop function IF EXISTS decrypt   
        
# COMMAND ----------

# Encryption functions 
spark.sql(f""" CREATE FUNCTION IF NOT EXISTS encrypt AS 'AESEncryptedUDF'
                USING JAR '/Jars/jars/{require_jar_dict["AESEncryption_UDF_V3_3_0"]}' """) 

spark.sql(f""" CREATE FUNCTION IF NOT EXISTS decrypt AS 'AESDecryptedUDF'
                USING JAR '/Jars/jars/{require_jar_dict["AESEncryption_UDF_V3_3_0"]}' """)


# COMMAND ----------
dbutils.notebook.exit("SUCCESS")
