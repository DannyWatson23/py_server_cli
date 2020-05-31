import sqlite3
import datetime
from multiprocessing.dummy import Pool as ThreadPool
import threading
import time
import logging
logging.basicConfig(level=logging.DEBUG, filename='/tmp/master.log', format='%(asctime)s %(levelname)s %(threadName)s:%(message)s')


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
        hello_timeout integer
                )""")
        datab.commit()
        datab.close()
    except Exception as e:
            print(e)
            pass
    
def if_hello_exceeded(last_hello, now, hello):
    last_hello_time = datetime.datetime.strptime(last_hello.split('.')[0], "%Y-%m-%d %H:%M:%S")
    print(last_hello_time)
    print(now)
    time_differential = now - last_hello_time
    print(time_differential)
    print(hello)    
    
    

    
def update_database(data):
    #Updates the database with the hello received, the ID and the timestamp, if does not exist, create
    conn = sqlite3.connect('/tmp/server_active.db')
    sql = " SELECT * from active_connections where ID is "+"'"+str(data[3])+"'"
    c = conn.cursor()
    now = datetime.datetime.now()
    sql_data = (data[0], data[1], data[2], now, now, now, data[3], data[4])
    c.execute(sql)
    _data = c.fetchone()
    if _data == None:
        sql = " INSERT INTO active_connections(IP, auth_type, mac_address, time_created, time_last_hello, time_last_challenge, ID, hello_timeout) VALUES(?,?,?,?,?,?,?,?)"
        c = conn.cursor()
        c.execute(sql, sql_data)
        conn.commit()
        print("Created entry in table")
        conn.close()
    else:
        sql = "UPDATE active_connections set time_last_hello = ? where ID = ?"
        print(data)
        colValues = (now, data[3])
        c = conn.cursor()
        c.execute(sql, colValues)
        conn.commit()
        print("Last hello updated.")
        conn.close()
def check_if_active(ID):
    #Checks the database against the ID, if it is in the active list and has authenticated, allow traffic
    print("Checking if active and authenticated...")
    conn = sqlite3.connect('/tmp/server_active.db')
    sql = " SELECT from active_connections where ID is "+"'"+str(ID)+"'"
    c = conn.cursor()
    c.execute(sql)
    _data = str(c.fetchone()[0])
    if _data == None:
        print("No entry in database, reject traffic until authenticated...")
    if _data:
        print("Authenticated, allow traffic")
        return True
    else:
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
def delete_unactive(ID):
    # If the hello timeout has exceeded [TBD] then the ID is removed from the active connections
    sql = "DELETE from active_connections where ID is "+"'"+str(ID)+"'"
    conn = sqlite3.connect('/tmp/server_active.db')
    c = conn.cursor()
    c.execute(sql)
    conn.commit()
    logging.debug("Deleted active session from database due to hello timeout")
    conn.close()
def test(data):
    try:
        conn = sqlite3.connect('/tmp/server_active.db')
        sql = '''INSERT INTO active_connections(IP, auth_type, mac_address, time_created, time_last_hello, time_last_challenge, ID, hello_timeout) VALUES(?,?,?,?,?,?,?,?)''' 
        c = conn.cursor()
        c.execute(sql, data)
        conn.commit()
        conn.close()
    except Exception as e:
        print(e)
        pass
    
def report_last_hello(ID, hello_interval):
    print("Checking "+ str(ID) + " for last hello " + str(hello_interval))
    logging.info("Current thread: "+ str(threading.currentThread()))
    
    print(ID)
    try:
     while True:
        time.sleep(1)
        conn = sqlite3.connect('/tmp/server_active.db')
        print(conn)
        sql = "SELECT time_last_hello from active_connections where ID is "+"'"+str(ID)+"'"
        c = conn.cursor()
        c.execute(sql)
        conn.commit()
        _data = c.fetchone()
        conn.close()
        now = datetime.datetime.now()
        last_time = str(_data).split('.')[0]
        last_time = last_time.split("'")[1]
        last_time = datetime.datetime.strptime(last_time, "%Y-%m-%d %H:%M:%S")
        time_differential = now - last_time
        print(time_differential)
        if time_differential >= datetime.timedelta(minutes=hello_interval):
            logging.debug(str(ID)+" is eligble to be marked as delete from database due to exceeding hello timeout")
            delete_unactive(ID)
    except Exception as e:
        with open("/tmp/error.log", "a+")as file:
            file.write(str(e))
            file.close()
        pass        
            
    
        
    
def spawn_watchdogs():
    #TODO: We need to figure out a way for it to dynamically create new threads while ensuring it doesn't create duplicate threads
    #
    #    new_thread = MyThread(next_job_details())
    #    new_thread.run()
    #    my_threads.append(new_thread)
    #  THIS WAY WE CAN SEARCH THE LIST FOR ACTIVE THREADS AND DECIDE NOT TO RUN IF THERE IS ALREADY ONE RUNNING
    #
    #
    while True:
        conn = sqlite3.connect('/tmp/server_active.db')
        sql = """ SELECT * from active_connections """
        c = conn.cursor()
        c.execute(sql)
        conn.commit()
        _data = c.fetchall()
        if len(_data) > 0:
            conn.close()
            logging.info("Found hosts, running watchdog...")
            print(_data)
            for active_session in _data:
                thread = threading.Thread(target=report_last_hello, args=(active_session[6], active_session[7]))
                thread.daemon = True          
                thread.start()
                #thread.join()
                logging.info("Sleeping 5 minutes...")
        else:
           conn.close()
           logging.info("No active hosts found in database... sleeping")
        time.sleep(5)
        print("Slept!")
        
        
    
    

def wipe_database():
    conn = sqlite3.connect("/tmp/server_active.db")
    sql = """ DROP table active_connections"""
    c = conn.cursor()
    c.execute(sql)
    conn.commit()
    conn.close()

#data = ("192.168.1.22", "AES", "aa:bb:cc:dd:ee:ff","Fri 22 May 16:28:08 BST 2020","Fri 22 May 16:16:23 BST 2020", "Fri 22 May 16:30:23 BST 2020", "test", 60)
#data = ("192.168.1.23", "AES", "aa:bb:cc:dd:ee:f3","Fri 21 May 16:28:08 BST 2020","Fri 21 May 16:16:23 BST 2020", "Fri 22 May 16:30:23 BST 2020", "test1", 180)
#data = ("192.168.1.24", "AES", "aa:bb:cc:dd:ee:f2","Fri 20 May 16:28:08 BST 2020","Fri 20 May 16:16:23 BST 2020", "Fri 22 May 16:30:23 BST 2020", "test2", 320)
#data = ("192.168.1.25", "None", "aa:bb:cc:dd:ee:f1","Fri 20 May 16:11:08 BST 2020","Fri 22 May 10:16:23 BST 2020", "Fri 22 May 16:30:23 BST 2020", "test3", 60)
#data = ("192.168.1.26", "Plaintext", "aa:bb:cc:dd:ee:f4","Fri 22 May 16:28:08 BST 2020","Fri 01 May 19:16:23 BST 2020", "Fri 22 May 16:30:23 BST 2020", "test4", 90)
#ID = data[6]
#wipe_database()
#create_database()
#test(data)
#update_database(data)
#check_last_hello(ID)
#update_database(data)
#delete_active()
#check_if_active(ID)
