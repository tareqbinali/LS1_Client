import pyodbc
import hashlib
import os

import logging


class MySQLDatabase:
    def __init__(self, client_cert_file, client_key_file):
        self.server = '35.230.158.71'  # Instance Public IP
        self.port = '3306'
        self.db_name = 'demodatabase'
        self.user = 'root'
        self.password = 'TestData01'
        self.client_certificate = client_cert_file
        self.client_key = client_key_file
        self.driver = '{MySQL ODBC 8.0 ANSI Driver}'
        self.connection = None

    def connect(self):
        try:
            conn_str = (
                f'DRIVER={self.driver};'
                f'SERVER={self.server};'
                f'PORT={self.port};'
                f'DATABASE={self.db_name};'
                f'UID={self.user};'
                f'PWD={self.password};'
                f'SSLCERT={self.client_certificate};'
                f'SSLKEY={self.client_key};'
                f'SSLVERIFY=1;'
            )
            self.connection = pyodbc.connect(conn_str, timeout=10)
            # logging.info("connection successful!")
       
        except pyodbc.InterfaceError as e:
            logging.exception(f"Connection failed: {e}")
        
        except pyodbc.DatabaseError as e:
            logging.exception(f"Database error: {e}")
        
        except Exception as e:
            logging.exception(f"Unexpected error: {e}")    

    def close(self):
        if self.connection:
            self.connection.close()

    # def get_table_names(self):
    #     self.connect()
    #     cursor = self.connection.cursor()
    #     cursor.execute("SHOW TABLES;")
    #     tables = [row[0] for row in cursor.fetchall()]
    #     self.close()
    #     return tables

    # def get_all_data(self, table_name):
    #     self.connect()
    #     cursor = self.connection.cursor()
    #     cursor.execute(f"SELECT * FROM {table_name};")
    #     header=[desc[0] for desc in cursor.description]
    #     data = cursor.fetchall()
    #     self.close()
    #     return data, header


    def hash_password(self, password):
        salt = os.urandom(16)
        hashed = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
        return salt.hex() + hashed.hex()
    
     # entry based on items in schema, good practice since if a column is added in future, the old version still works 
    def insert_user(self, table_name, **kwargs):
        self.connect()
        cursor = self.connection.cursor()
        
        provided_columns = []
        provided_values = []
        
        for key, value in kwargs.items():
            provided_columns.append(key)
            provided_values.append(value if key != 'password' else self.hash_password(value))

        columns_str = ', '.join(provided_columns)
        placeholders = ', '.join(['?'] * len(provided_columns))

        query = f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders});"
        try:
            cursor.execute(query, provided_values)
            self.connection.commit()
            self.close()
            return True
        except Exception as e:
            logging.error(f"user creation : {e}")

        return False

    # def extract_data(self, table_name, column_name, value):
    #     self.connect()
    #     cursor = self.connection.cursor()  
    #     # Execute the query
    #     query = f"SELECT * FROM {table_name} WHERE {column_name} = ?"
    #     cursor.execute(query, (value,))

    #     # Fetch all results
    #     results = cursor.fetchall()

    #     # # Print results
    #     # for row in results:
    #     #     print(row)
    #     self.close()
    #     return results      

    def update_cell(self, table_name, column_name, new_value, primary_key_value):
        self.connect()
        cursor = self.connection.cursor()
        query = f"UPDATE {table_name} SET {column_name} = ? WHERE id = ?"
        cursor.execute(query, (new_value, primary_key_value))
        self.connection.commit()
        self.close()   

   
    # def update_entry(self, table_name, condition_column, condition_value, **kwargs):
    #     if not kwargs:
    #         return  # No updates provided
        
    #     self.connect()
    #     cursor = self.connection.cursor()
        
    #     update_fields = ', '.join([f"{key} = ?" for key in kwargs.keys()])
    #     values = list(kwargs.values())
        
    #     # If password is being updated, hash it
    #     if 'password' in kwargs:
    #         password_index = list(kwargs.keys()).index('password')
    #         values[password_index] = self.hash_password(kwargs['password'])
        
    #     query = f"UPDATE {table_name} SET {update_fields} WHERE {condition_column} = ?;"
    #     values.append(condition_value)  # Add condition value at the end
        
    #     cursor.execute(query, values)
    #     self.connection.commit()
    #     self.close()    
    

    def check_entry(self, table_name, value, column_name='email_id'):
        # EXISTS → Efficient query that stops searching after the first match.
        # Returns 1 if email exists, otherwise 0
        self.connect()
        cursor = self.connection.cursor()
        query = f"SELECT EXISTS (SELECT 1 FROM {table_name} WHERE {column_name} = ?)"
        cursor.execute(query, (value,))
        exists = cursor.fetchone()[0]
        self.close()
        return exists         

    # def check_email_id(self, table_name, email_id):
    #     # EXISTS → Efficient query that stops searching after the first match.
    #     # Returns 1 if email exists, otherwise 0
    #     self.connect()
    #     cursor = self.connection.cursor()
    #     query = f"SELECT EXISTS (SELECT 1 FROM {table_name} WHERE email_id = ?)"
    #     cursor.execute(query, (email_id,))
    #     exists = cursor.fetchone()[0]
    #     self.close()
    #     return exists

    def verify_password(self, table_name, email, password):
        self.connect()
        cursor = self.connection.cursor()
       
        # query = f"SELECT password FROM {table_name} WHERE email_id = ?;"
        query = f"SELECT * FROM {table_name} WHERE email_id = ?;"
        cursor.execute(query, (email,))
        result = cursor.fetchone()
        self.close()
        
        if result:
            # stored_hash = result[0]
            header=[desc[0] for desc in cursor.description]
            password_index = header.index('password')
            stored_hash = result[password_index]
            
            salt = bytes.fromhex(stored_hash[:32])
            stored_password = stored_hash[32:]
            hashed_attempt = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000).hex()
            # return hashed_attempt == stored_password
            if hashed_attempt==stored_password:
                return True, result, header
        return False, None, None 
    
    def create_table(self, table_name, schema):
        self.connect()
        cursor = self.connection.cursor()
        schema_string = ', '.join(schema)
        query = f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                id INT AUTO_INCREMENT PRIMARY KEY, {schema_string}
            );
        """
        cursor.execute(query)
        self.connection.commit()
        self.close()

  

if __name__=="__main__":
    client_cert_file='client-cert.pem'
    client_key_file='client-key.pem'    
    table_name="Licence_LS1_Client"
    
    schema = [
        "first_name VARCHAR(255)",
        "last_name VARCHAR(255)",
        "email_id VARCHAR(255)",
        "expiry_date DATE",
        "client VARCHAR(255)",
        "dma VARCHAR(255)",
        "status VARCHAR(100) ", #active, review
        "role VARCHAR(100)", #user, admin, super admin
        "reg_date TIMESTAMP",
        "last_login TIMESTAMP",
        "password VARCHAR(255)"
    ]
      
    # Example usage:
    db = MySQLDatabase(client_cert_file, client_key_file)
    
    # print(db.get_table_names()) # get table names
    
    # db.create_table(table_name, schema) # create table

    # db.insert_user(table_name, first_name="tareq", last_name="ali", email_id='tareq@wi.international', password='123456', role='user', status='active')
    # db.verify_password(table_name, 'tareq@wi.international', "123456")

    
 


    # db.get_all_data(table_name)
    # print("Password verification:", db.verify_password(table_name, "m.tareq@gmail.com", "123456"))

    # Adding a new column to an existing table
    # db.add_column(table_name, "reg_date DATE")

    
    # db.check_email_id(table_name, 'tareq@wi.international')

    # db.update_cell(table_name, 'status', 'active', id)
    # db.update_cell(table_name, 'role', 'super admin', id)
    # print(db.extract_data(table_name, 'email_id', 'tareq@wi.international'))
    a=1
