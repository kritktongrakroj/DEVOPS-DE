# Encryption functions 
spark.sql(f""" CREATE FUNCTION IF NOT EXISTS encrypt AS 'AESEncryptedUDF'
                USING JAR '/Jars/jars/{require_jar_dict["AESEncryption_UDF_V3_3_0"]}' """) 

spark.sql(f""" CREATE FUNCTION IF NOT EXISTS decrypt AS 'AESDecryptedUDF'
                USING JAR '/Jars/jars/{require_jar_dict["AESEncryption_UDF_V3_3_0"]}' """)


# COMMAND ----------
dbutils.notebook.exit("SUCCESS")
