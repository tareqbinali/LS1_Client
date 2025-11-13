# short non gui version of gcpClient.py
# last update : 04 Dec 2024

# pip install google-cloud-bigquery google-cloud-storage


import os
import sys
import pathlib
from google.cloud import storage 
from google.cloud import bigquery
import json
import socket
import uuid
import re

import logging

from constants import service_file

# meipass_path = sys._MEIPASS if getattr(sys, 'frozen', False) else os.path.abspath(".")
# service_file = os.path.join(meipass_path, "ls1-sample.json")
os.environ['GOOGLE_APPLICATION_CREDENTIALS']=service_file


STORAGE_CLASSES=('STANDARD', 'NEARLINE', 'COLDLINE', 'ARCHIVE')

def runQuery(client, query):
    success=False
    data=None
    try:    
        query_job=client.query(query)
        # Check the job's state
        if query_job.state == "DONE":
            success=True
            if re.search(r'\bSELECT\b', query, re.IGNORECASE):
                rows = query_job.result()
                data=[]
                for row in rows:
                    my_dict = dict(row.items())
                    my_list = list(my_dict.values())
                    data.append(my_list)
            else:
                data=True        
            # table = client.get_table(table_id)
            # field_names = [field.name for field in table.schema]

    except Exception as e:
        print(f"Error : {e}")
    
    return success, data #, field_names

def colnames(table_name, dataset_id, bigquery_client):
    query = f'''
        SELECT column_name, data_type
        FROM `{bigquery_client.project}.{dataset_id}.INFORMATION_SCHEMA.COLUMNS`
        WHERE table_name = '{table_name}';
    '''
    s, data=runQuery(bigquery_client,query)
    if s:
    # Unpack the inner lists into separate lists
        column_names, data_types = zip(*data)
    return column_names, data_types


def findIndex(item_to_find, my_list):
    if item_to_find in my_list:
        return my_list.index(item_to_find)
    else:
        return None
        
class gcp:
    def __init__(self):
        super().__init__()
        self.working_dir=pathlib.Path.cwd()
        files_folder=self.working_dir.joinpath('UploadFolder')
        downloads_folder=self.working_dir.joinpath('DownloadFolder')

        self.connected=self.internetConnection()
        self.createClients()
        self.query_select_dialog=None
        self.query_update_dialog=None
        self.bucket_name=None

    def createClients(self):
        if self.connected:
            try:
                self.storage_client=storage.Client()              
                self.bigquery_client=bigquery.Client()
                self.job_config = bigquery.LoadJobConfig(
                    source_format='NEWLINE_DELIMITED_JSON')
            except Exception:
                print(Exception)
    
    def archiveEntry(self, LoggerSN, RecFilename):
        
        # self.copyTableSchema('LS1_RawWavURL_Archive') # creates a table manually if it does not exist

        table_id="LS1_Data.LS1_RawWavURL"
        table_id_archive="LS1_Data.LS1_RawWavURL_Archive"
        
        # read entry from table_id
        query = f"SELECT * FROM {table_id} WHERE LS1_LoggerSN='{LoggerSN}' AND LS1_RecFilename='{RecFilename}';"
        query_job=self.bigquery_client.query(query)
        result = query_job.result()

        for row in result:
            # Insert the entry into the destination table, only one entry
            # Convert None values to 'NULL' for SQL INSERT
            values = [f'\'{value}\''.replace('None', 'NULL') if value is not None else 'NULL' for value in row]
            query = f'''
                INSERT INTO `{table_id_archive}`
                VALUES ({', '.join(map(str, values))});
            '''
            try:
                # Execute the insert query
                query_job=self.bigquery_client.query(query)   
                result = query_job.result()

                query = f"DELETE FROM {table_id} WHERE LS1_LoggerSN='{LoggerSN}' AND LS1_RecFilename='{RecFilename}';"
                query_job=self.bigquery_client.query(query)
                result = query_job.result()
        
                return True  

            except Exception as e:
                print(f"Query failed : {e}")
                return False    
     

    def checkEntry(self, LoggerSN, RecFilename):
        # table_id=dataset + '.' +table
        table_id="LS1_Data.LS1_RawWavURL"
        query = f"SELECT * FROM {table_id} WHERE LS1_LoggerSN='{LoggerSN}' AND LS1_RecFilename='{RecFilename}' LIMIT 1;" 

        query_job=self.bigquery_client.query(query)
        result = query_job.result()
        row_count=result.total_rows 
        return row_count


    def copyTableSchema(self,new_table_name, table_to_be_copied, data_set ):
        
        # table_to_be_copied="LS1_RawWavURL"
        # data_set="LS1_Data"
        # new_table_name="LS1_RawWavURL_Archive"
        # table_id="LS1_Data.LS1_RawWavURL"
        table_id=f"{data_set}.{table_to_be_copied}"
        new_table_id=f"{data_set}.{new_table_name}"
        query = f"CREATE TABLE {new_table_id} AS SELECT * FROM {table_id} WHERE FALSE;" 

        query_job=self.bigquery_client.query(query)
        result = query_job.result()   
      
   
    def read(self, dataset='', table='', condition_string='', query=''):
        if query:
             match = re.search(r"FROM\s+([\w.]+)", query, re.IGNORECASE)
             table_id = match.group(1)
        else:
            table_id=dataset + '.' +table
        # print("reading from ", table_id)
        logging.info(f"reading from {table_id}")

        # query=''

        if condition_string=="ALL":
            query = f"SELECT * FROM {table_id} "

        if condition_string=="Last 10":
            # query = f"SELECT * FROM {table_id} ORDER BY LS1_RecFilename DESC LIMIT 10"
            query = f"SELECT * FROM {table_id} ORDER BY LS1_WavFileURL DESC LIMIT 3"    
        
        if condition_string=="Empty SpecURL":
            condition="LS1_SpecFileURL IS NULL OR LS1_SpecFileURL = '' OR LS1_SpecFileURL = 'None'"
            query = f"SELECT * FROM {table_id} WHERE {condition}"

        if condition_string=="Empty audio profile":
            condition="LS1_AudioProfile IS NULL OR LS1_AudioProfile = '' OR LS1_AudioProfile = 'None'"
            query = f"SELECT * FROM {table_id} WHERE {condition}" 
                    
        if condition_string=="Empty URL":
            condition="LS1_AudioProfile IS NULL OR LS1_SpecFileURL IS NULL"
            query = f"SELECT * FROM {table_id} WHERE {condition}" 
        
        
        if condition_string=="SpecURL only":
            condition="LS1_SpecFileURL IS NOT NULL"
            query = f"SELECT * FROM {table_id} WHERE {condition}"
        
        # if condition_string=="Dates":
        #     condition="LS1_SpecFileURL IS NOT NULL"
        #     query = f"SELECT * FROM {table_id} WHERE {condition}"    

        if condition_string=="Noise NOT null":
            condition="LS1_NoiseType IS NOT NULL"
            query = f"SELECT * FROM {table_id} WHERE {condition}" 

        # if condition_string=="Noise types":
        #     NoiseType=listBox(NoiseTypes, TitleStr="Select an item", width=500, height=300)
        #     query = f"SELECT * FROM {table_id} WHERE LS1_NoiseType='{NoiseType}'"

        if condition_string.startswith("LoggerSN"):
            LoggerSN=condition_string.replace('LoggerSN=', '')
            query = f"SELECT * FROM {table_id} WHERE LS1_LoggerSN='{LoggerSN}'"

        if condition_string.startswith("Date"):
            Date=condition_string.replace('Date=', '')
            query = f"SELECT * FROM {table_id} WHERE DATE(LS1_TestDate)= DATE '{Date}';"

        if condition_string.startswith("Range"):
            #format :  condition_string = "Range=2025-01-28 to 2025-01-29"
            match = re.search(r"(\d{4}-\d{2}-\d{2}) to (\d{4}-\d{2}-\d{2})", condition_string)
            start_date, end_date = match.groups()
            query = f"SELECT * FROM {table_id} WHERE DATE(LS1_TestDate) >= DATE '{start_date}' AND DATE(LS1_TestDate) <= DATE '{end_date}';"    
        
        if condition_string.startswith("UploadDate"):
            Date=condition_string.replace('UploadDate=', '')
            query = f"SELECT * FROM {table_id} WHERE DATE(LS1_UploadDate)= DATE '{Date}';"        

        
        # query=f"SELECT DISTINCT LS1_LoggerSN from {table_id}"# TO FIND UNIQUE LOGGER IDS 



        if not query:
            # query=f"SELECT * FROM {table_id} WHERE LS1_RawFileURL like ('%2023-09-06%')"# current 
            query=f"SELECT * FROM {table_id} WHERE LS1_RawFileURL like ('%{condition_string}%')"# current   




        # if condition_string=="None":
        #     condition="LS1_SpecFileURL = 'None'"
        #     query = f"SELECT * FROM {table_id} WHERE {condition}"               
                  

        # query="SELECT * FROM " + table_id
        
        # query="""
        #     SELECT *
        #     FROM LS1_Data.LS1_RawWavURL
        # """
        # logging.info(f"query :  {query}")
        query_job=self.bigquery_client.query(query)
        rows = query_job.result()
        data=[]
        for row in rows:
            # print(row)
            # data.append(row)
            # converting row object to form standard python list
            my_dict = dict(row.items())
            my_list = list(my_dict.values())
            data.append(my_list)
    #    first_column = [row[0] for row in data]
        table = self.bigquery_client.get_table(table_id)
        field_names = [field.name for field in table.schema]
        
        # print("finished reading data!")
        logging.info(f"{len(data)} - entry found")
        return data, field_names
         
    
 
    def list_datasets(self):
        datasets = list(self.bigquery_client.list_datasets())  # Make an API request.
        project = self.bigquery_client.project
        dataset_ids=[]
        if datasets:
            print("Datasets in project {}:".format(project))
            for dataset in datasets:
                print("\t{}".format(dataset.dataset_id))
                dataset_ids.append(dataset.dataset_id)
        else:
            print("{} project does not contain any datasets.".format(project))
        return dataset_ids

    def list_tables(self, dataset_id):
        tables = self.bigquery_client.list_tables(dataset_id)  
        print("Tables contained in '{}':".format(dataset_id))
        table_ids=[]        
        for table in tables:
            print("{}.{}.{}".format(table.project, table.dataset_id, table.table_id))
            table_ids.append(table.table_id)
        return table_ids

    def getHeaderNames(self):
        #  not completed yet
        query=f"""SELECT
            column_name
            FROM
            `ls1-sample.LS1_Data.INFORMATION_SCHEMA.COLUMNS`
            WHERE
            table_name = 'LS1_MainData';
        """ 

        table = self.bigquery_client.get_table('ls1-sample.LS1_Data.LS1_MainData')
        field_names = [field.name for field in table.schema]   

    def bucketList(self):
        bucketnames=[]
        buckets=self.storage_client.list_buckets()
        for bucket in buckets:
            print("bucket : ", bucket.name)
            bucketnames.append(bucket.name)
        return bucketnames 
    
    
    def tables(self, bucketname):
        tablelist=self.bigquery_client.list_tables(bucketname)
        print("Tables contained in '{}':".format(bucketname))
        tablenames=[]
        for table in tablelist:
            # print("{}.{}.{}".format(table.project, table.dataset_id, table.table_id))
            print(table.table_id)     
            tablenames.append(table.table_id)
        return tablenames    


# bucket_name='gcs_api_demo'    
        
    def create_bucket(self, bucket_name, storage_class, bucket_location='US'):
        bucket=self.client.bucket(bucket_name)
        bucket.storage_class=storage_class
        return self.client.create_bucket(bucket, bucket_location)    
  
    def upload_stream_to_bucket(self,bucket_name, image_buffer, blob_name, content_type='image/png', replace=True):
        bucket=self.storage_client.get_bucket(bucket_name)
        blob=bucket.blob(blob_name)
        try:
            blob.upload_from_file(image_buffer, content_type='image/png')
            token = str(uuid.uuid4())
            # metadata={'firebaseStorageDownloadTokens': 'e53beebe-7c97-4aee-9d7c-f93976ab53ba'}
            metadata={'firebaseStorageDownloadTokens': token}
            blob.metadata = metadata
            blob.patch()
            # Construct the download URL with the token
            # the following does not work
            download_url = blob.public_url + "?alt=media&token=" + token
            # work around
            media_link=blob.media_link
            id1=media_link.find(bucket_name)
            id2=media_link.find("?")
            url="https://firebasestorage.googleapis.com/v0/b/" + media_link[id1:id2] + "?alt=media&token=" + token
            return  True, url    
        except Exception as e:
            print(e)
            return False

        
    def upload_to_bucket(self,bucket_name, file_path, destination_folder='', replace=True):
        try:
            bucket=self.storage_client.get_bucket(bucket_name)
         
            dir_name, file_name = os.path.split(file_path)
            blob_name=destination_folder + '/' + file_name
            
            blob=bucket.blob(blob_name)
            # if not blob.exists():
            if replace:
                blob.upload_from_filename(file_path)
                token = str(uuid.uuid4())
                # metadata={'firebaseStorageDownloadTokens': 'e53beebe-7c97-4aee-9d7c-f93976ab53ba'}
                metadata={'firebaseStorageDownloadTokens': token}
                blob.metadata = metadata
                blob.patch()

                # Construct the download URL with the token
                # the following does not work
                download_url = blob.public_url + "?alt=media&token=" + token
                # work around
                media_link=blob.media_link
                id1=media_link.find(bucket_name)
                id2=media_link.find("?")
                url="https://firebasestorage.googleapis.com/v0/b/" + media_link[id1:id2] + "?alt=media&token=" + token
                return  True, url
            # else:
            #     return True, None 
        except Exception as e:
            print(e)
            return False


    def bulkUpdate(self, entries_to_update, HeaderName):
        # not working yet
        project_id = "ls1-sample" # this must be lower case letter it was (LS1-Sample)
        dataset_id = "LS1_Data"
        table_id = "LS1_RawWavURL"
        # Assuming you have a list of entries to update
        # entries_to_update = [
        #     {"LoggerSN": "123", "RecFilename": "file1.txt", "HeaderValue": "value1"},
        #     {"LoggerSN": "456", "RecFilename": "file2.txt", "HeaderValue": "value2"},
        #     {"LoggerSN": "789", "RecFilename": "file3.txt", "HeaderValue": "value3"}
        # ]
            # Set the table and project IDs
        # Create the update queries for each entry
        update_queries = []
        for entry in entries_to_update:
            str_to_upload = entry["HeaderValue"]
            LoggerSN = entry["LoggerSN"]
            RecFilename = entry["RecFilename"]
            update_query = f"""
                UPDATE `{project_id}.{dataset_id}.{table_id}`
                SET {HeaderName} = '{str_to_upload}' 
                WHERE LS1_LoggerSN = '{LoggerSN}'
                AND LS1_RecFilename = '{RecFilename}'
            """
            update_queries.append(update_query)

        # Combine the update queries into a single query
        combined_query = "\n".join(update_queries)

        # Execute the combined update query
        query_job = self.bigquery_client.query(combined_query)
        query_job.result()
    
    
    def updateTable(self, str_to_upload, LoggerSN, RecFilename, HeaderName):
        try:
            # table_ref=self.bigquery_client.dataset("LS1_Data").table("LS1_RawWavURL")
            # Set the table and project IDs
            project_id = "ls1-sample" # this must be lower case letter it was (LS1-Sample)
            dataset_id = "LS1_Data"
            table_id = "LS1_RawWavURL"

            # Define the update query
            update_query = f"""
                UPDATE `{project_id}.{dataset_id}.{table_id}`
                SET {HeaderName} = '{str_to_upload}' 
                WHERE LS1_LoggerSN =  '{LoggerSN}'
                AND LS1_RecFilename= '{RecFilename}'
            """
            # Execute the update query
            query_job = self.bigquery_client.query(update_query)
            # Wait for the query to complete
            query_job.result()
            return True
        except Exception as e:
            print(e)
            return False
        
    def insert(self, LoggerSN, RecFilename, WavFileURL, SpecFileURL, UploadDate, AudioProfile, TestDate):
        try:
            project_id = "ls1-sample" # this must be lower case letter it was (LS1-Sample)
            dataset_id = "LS1_Data"
            table_id = "LS1_RawWavURL"

            # Define the update query
            insert_query = f"""
                INSERT INTO `{project_id}.{dataset_id}.{table_id}`
                (LS1_LoggerSN, LS1_RecFilename, LS1_WavFileURL, LS1_SpecFileURL, LS1_UploadDate, LS1_AudioProfile, LS1_TestDate)
                VALUES
                ('{LoggerSN}', '{RecFilename}', '{WavFileURL}', '{SpecFileURL}', '{UploadDate}', '{AudioProfile}', '{TestDate}')
            """
            # Execute the update query
            query_job = self.bigquery_client.query(insert_query)
            # Wait for the query to complete
            query_job.result()
            return True
        except Exception as e:
            print(e)
            return False 

    def insert_from_json_file(self):
        # Define the dataset ID and table ID
        dataset_id = "LS1_Data"
        table_id = "LS1_MainData"

        json_file="C:\\wi\\data.json"

        # Load JSON data from file
        with open(json_file, "r") as json_file:
            json_data = json.load(json_file)

        # Replace empty strings with None
        for entry in json_data:
            for key, value in entry.items():
                if value == "":
                    entry[key] = None    

        # Get the table reference
        table_ref = self.bigquery_client.dataset(dataset_id).table(table_id)
        table = self.bigquery_client.get_table(table_ref)

        # Insert JSON data into the table
        errors = self.bigquery_client.insert_rows_json(table, json_data)

        if errors == []:
            print("Data inserted successfully.")
        else:
            print("Encountered errors while inserting data:")
            for error in errors:
                print(error)


    
    def updateUrl(self, LoggerSN, RecFilename, SpecFileURL, UploadDate, AudioProfile, TestDate):
        status=None
        try:
            project_id = "ls1-sample" # this must be lower case letter it was (LS1-Sample)
            dataset_id = "LS1_Data"
            table_id = "LS1_RawWavURL"

            # Define the update query
            update_query = f"""
                UPDATE `{project_id}.{dataset_id}.{table_id}`
                SET
                    LS1_SpecFileURL='{SpecFileURL}',
                    LS1_UploadDate='{UploadDate}',
                    LS1_AudioProfile='{AudioProfile}',
                    LS1_TestDate='{TestDate}'
                WHERE 
                    LS1_LoggerSN='{LoggerSN}'
                    AND LS1_RecFilename='{RecFilename}'
            """
            # Execute the update query
            query_job = self.bigquery_client.query(update_query)
            # Wait for the query to complete
            query_job.result()
            return True, status
        except Exception as e:
            if "streaming" in e.message:
                status="table still in streaming buffer"
            else:
                status=e.message
                print(e)

            return False, status
    def updateNoiseType(self, LoggerSN, RecFilename, NoiseType=None, NoiseNotes=None, NoiseAuto=None):
        status=None
        try:
            project_id = "ls1-sample" # this must be lower case letter it was (LS1-Sample)
            dataset_id = "LS1_Data"
            table_id = "LS1_RawWavURL"


            NoiseStr=f"LS1_Auto='{NoiseAuto}'"


            # Define the update query
            update_query = f"""
                UPDATE `{project_id}.{dataset_id}.{table_id}`
                SET {NoiseStr}
                WHERE 
                    LS1_LoggerSN='{LoggerSN}'
                    AND LS1_RecFilename='{RecFilename}'
            """
            # Execute the update query
            query_job = self.bigquery_client.query(update_query)
            # Wait for the query to complete
            query_job.result()
            return True, status
        except Exception as e:
            if "streaming" in e.message:
                status="table still in streaming buffer"
            else:
                status=e.message
                print(e)

            return False, status                 

    def renameHeader(self, old_field_name, new_field_name):
        try:
            project_id = "ls1-sample" # this must be lower case letter it was (LS1-Sample)
            dataset_id = "LS1_Data"
            table_id = "LS1_RawWavURL"

            # Define the query
            alter_query = f"""
                ALTER TABLE `{project_id}.{dataset_id}.{table_id}`
                RENAME COLUMN `{old_field_name}` TO `{new_field_name}` 
            """
            # Execute the update query
            query_job = self.bigquery_client.query(alter_query)
            # Wait for the query to complete
            query_job.result()
            return True
        except Exception as e:
            print(e)
            return False                  

    
    def updateTable2(self, SpecLink, LoggerSN, RecFilename):
        # table_ref=self.bigquery_client.dataset("LS1_Data").table("LS1_RawWavURL")
        # Set the table and project IDs
        project_id = "ls1-sample" # this must be lower case letter it was (LS1-Sample)
        dataset_id = "LS1_Data"
        table_id = "LS1_RawWavURL"

        # Define the update query
        update_query = f"""
            UPDATE `{project_id}.{dataset_id}.{table_id}`
            SET LS1_SpecFileURL = '{SpecLink}' 
            WHERE LS1_LoggerSN =  '{LoggerSN}'
            AND LS1_RecFilename= '{RecFilename}'
        """

        # Execute the update query
        query_job = self.bigquery_client.query(update_query)
        # Wait for the query to complete
        query_job.result()


    
    def addVarToSchema(self):        
        # table = self.bigquery_client.get_table(table_id)  # Make an API request.

        original_schema = table.schema
        new_schema = original_schema[:]  # Creates a copy of the schema.
        new_schema.append(bigquery.SchemaField("MeasurementUnit", "STRING", "REPEATED"))

        table.schema = new_schema
        table = self.bigquery_client.update_table(table, ["schema"])  # Make an API request.

        if len(table.schema) == len(original_schema) + 1 == len(new_schema):
            print("A new column has been added.")
        else:
            print("The column has not been added.")

    def internetConnection(self):
        IPaddress = socket.gethostbyname(socket.gethostname())
        if IPaddress == "127.0.0.1":
            print("No internet, your localhost is " + IPaddress)
            return False
        else:
            print("Connected, with the IP address: " + IPaddress)
            return True
