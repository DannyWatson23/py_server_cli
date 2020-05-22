import sqlite3
import datetime

def create_database():
    # create on launch, checks to see if already created
    # We need in the database against every authenticated client:
    #    - IP
    #    - Authentication type (AES, plaintext, none)
    #    - MAC address
    #    - Timestamp created
    #    - Timestamp of last hello
    #    - ID
    #    - Timestamp of last challenge
    #    - Hello timeout interval
    #    - Authenticated
    try:
        datab = sqlite3.connect('/tmp/server_active.db')
        c = datab.cursor()
        c.execute(""" CREATE TABLE active_connections (
        IP text,
        auth_type text,
        mac_address text,
        time_created text,
        time_last_hello text,
        time_last_challenge text,
        ID text,
        hello_timeout integer,
        authenticated boolean
                )""")
        datab.commit()
        datab.close()
    except Exception as e:
            pass
def update_database(data):
    #Updates the database with the hello received, the ID and the timestamp, if does not exist, create
    conn = sqlite3.connect('/tmp/server_active.db')
    sql = " SELECT * from active_connections where ID is "+"'"+str(ID)+"'"
    c = conn.cursor()
    c.execute(sql)
    _data = c.fetchone()
    if _data == None:
        sql = " INSERT INTO active_connections(IP, auth_type, mac_address, time_created, time_last_hello, time_last_challenge, ID, hello_timeout, authenticated) VALUES(?,?,?,?,?,?,?,?,?)"
        c = conn.cursor()
        c.execute(sql, data)
        conn.commit()
        print("Created entry in table")
        conn.close()
    else:
        sql = "UPDATE active_connections set IP = ?, time_last_hello = ?, time_last_challenge = ?, authenticated = ? where ID = ?"
        colValues = (data[0], data[4], data[5], data[-1], data[6])
        c = conn.cursor()
        c.execute(sql, colValues)
        conn.commit()
        print("Updated table")
        conn.close()
def check_if_active(ID):
    #Checks the database against the ID, if it is in the active list and has authenticated, allow traffic
    print("Checking if active and authenticated...")
    conn = sqlite3.connect('/tmp/server_active.db')
    sql = " SELECT authenticated from active_connections where ID is "+"'"+str(ID)+"'"
    c = conn.cursor()
    c.execute(sql)
    _data = str(c.fetchone()[0])
    if _data == None:
        print("No entry in database, reject traffic until authenticated...")
    if '1' in _data:
        print("Authenticated, allow traffic")
        return True
    elif '0' in _data:
        print("Not authenticated, reject traffic...")
        return False
    conn.close()
def check_last_hello(ID):
    #Returns last hello seen from ID
    conn = sqlite3.connect('/tmp/server_active.db')
    sql = "SELECT time_last_hello from active_connections where ID is "+"'"+str(ID)+"'"
    c = conn.cursor()
    c.execute(sql)
    data = c.fetchall()
    conn.close()
    print(data)
def delete_active():
    # If the hello timeout has exceeded [TBD] then the ID is removed from the active connections
    time = datetime.datetime.now()
    conn = sqlite3.connect('/tmp/server_active.db')
    sql = "SELECT time_last_hello from active_connections where ID is "+"'"+str(ID)+"'"
    c = conn.cursor()
    c.execute(sql)
    data = c.fetchone()[0]
    data = data.split(" ")
    new_date = data[1] + " " + data[2] + " " + data[3] + " " + data[5]
    #print new_date
    last_hello_time = datetime.datetime.strptime(new_date, "%d %b %H:%M:%S %Y")
    #print(last_hello_time)
    #print(time)
    time_differential = time - last_hello_time
    #print time_differential
    if time_differential > datetime.timedelta(minutes=30):
        print("Exceeded 30 minutes since last hello")
        sql = "DELETE from active_connections where ID is "+"'"+str(ID)+"'"
        c.execute(sql)
        conn.commit()
        print("Deleted active session from database due to hello timeout")
    conn.close()

def test(data):
    try:
        conn = sqlite3.connect('/tmp/server_active.db')
        sql = '''INSERT INTO active_connections(IP, auth_type, mac_address, time_created, time_last_hello, time_last_challenge, ID, hello_timeout, authenticated) VALUES(?,?,?,?,?,?,?,?,?)''' 
        c = conn.cursor()
        c.execute(sql, data)
        conn.commit()
        conn.close()
    except Exception as e:
        print(e)
        pass
    

def wipe_database():
    conn = sqlite3.connect("/tmp/server_active.db")
    sql = """ DROP table active_connections"""
    c = conn.cursor()
    c.execute(sql)
    conn.commit()
    conn.close()

#data = ("192.168.1.22", "AES", "aa:bb:cc:dd:ee:ff","Fri 22 May 16:28:08 BST 2020","Fri 22 May 16:16:23 BST 2020", "Fri 22 May 16:30:23 BST 2020", "test", 60, True)
#data = ("192.168.1.23", "AES", "aa:bb:cc:dd:ee:f3","Fri 21 May 16:28:08 BST 2020","Fri 21 May 16:16:23 BST 2020", "Fri 22 May 16:30:23 BST 2020", "test1", 180, True)
#data = ("192.168.1.24", "AES", "aa:bb:cc:dd:ee:f2","Fri 20 May 16:28:08 BST 2020","Fri 20 May 16:16:23 BST 2020", "Fri 22 May 16:30:23 BST 2020", "test2", 320, True)
#data = ("192.168.1.25", "None", "aa:bb:cc:dd:ee:f1","Fri 20 May 16:11:08 BST 2020","Fri 22 May 10:16:23 BST 2020", "Fri 22 May 16:30:23 BST 2020", "test3", 60, True)
data = ("192.168.1.26", "Plaintext", "aa:bb:cc:dd:ee:f4","Fri 22 May 16:28:08 BST 2020","Fri 01 May 19:16:23 BST 2020", "Fri 22 May 16:30:23 BST 2020", "test4", 90, True)
ID = data[6]
#wipe_database()
#create_database()
#test(data)
update_database(data)
#check_last_hello(ID)
#update_database(data)
delete_active()
#check_if_active(ID)
