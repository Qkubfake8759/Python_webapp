import pyodbc

conn = pyodbc.connect("DRIVER={SQL Server}; SERVER=FTRESAFETY_O; DATABASE=iStockCoop;UID=sa;PWD=sql2022;")

def connection_database():
    if conn:
        print("Connection successfull!")
        code = 1
        return code        
    else:
        print("Connection failed.")
        code = 0
        return code
    
def execute_data(query):
    corsur = conn.cursor()
    corsur.execute(query)   
    row = corsur.fetchall()
    #print("row :", row)
    conn.commit()

    return row

def execute_data_insert(query):
    cursor = conn.cursor()
    cursor.execute(query)
    conn.commit()

    try:
        row = cursor.fetchall()
    except:
        row = None

    cursor.close()
    return row

def execute_data_fetch(query):
    cursor = conn.cursor()
    cursor.execute(query)
    conn.commit()

    try:
        row = cursor.fetchall()
    except:
        row = None

    cursor.close()
    return row