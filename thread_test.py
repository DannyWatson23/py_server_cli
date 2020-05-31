import threading
import sqlite3
import time
import logging
from random import randint

logging.basicConfig(level=logging.DEBUG, filename='/tmp/master.log', format='%(asctime)s %(levelname)s %(threadName)s:%(message)s')
import sys

# Global thread_list that can be added to from any function
thread_list = list()


def test(ID):
    #print(str(ID))
    #print(str(ID)+ " inside test")
    time.sleep(randint(10,30))
    conn = sqlite3.connect("/tmp/server_active.db")
    sql = " DELETE from active_connections where ID is "+"'"+str(ID)+"'"
    c = conn.cursor()
    c.execute(sql)
    conn.commit()
    conn.close()
    print("Removed "+str(ID)+" from database")
    thread_list.remove(ID)
    print("thread_list after removal: "+str(thread_list))
     
    
    

def run_threads(thread_list):
    print("Thread list before applying the threading... " +str(thread_list))
    
    #############################################################################
    tmp_list = list()
    #Return list of active threads
    active_list = threading.enumerate()
    # remove Main thread as it can't be used in a way we want
    active_list.pop(0)
    #############################################################################
    
    #print("Active list: \n" + str(active_list))
    
    if len(active_list) < 1:
        #print("Less than 1")
        for thread in thread_list:
            t = threading.Thread(name=thread, target=test, args=(thread,))
            t.daemon = True
            t.start()
    else:
        #print("\n\n\n")
        for thread in active_list:
            tmp_list.append(thread.getName())
            
        print(thread_list)
        print(active_list)
        for thread in thread_list:
            if thread not in tmp_list:
                #print(str(thread) + "not in list")
                t = threading.Thread(name=str(thread), target=test, args=(thread,))
                t.daemon=True
                t.start()    

def report():
    while True:
        
        # Create temporary thread list
        # This is used to store possible new threads from the any new active connections
        temp_thread_list = list()
        
        
        
        conn = sqlite3.connect('/tmp/server_active.db')
        sql = """ SELECT * from active_connections """
        c = conn.cursor()
        c.execute(sql)
        conn.commit()
        _data = c.fetchall()
        if len(_data) > 0:
            conn.close()
            #logging.info("Found hosts")
            #print("Found hosts")
            #print(_data)
            
            for active_session in _data:
                time.sleep(2)
                stuff = active_session[6]
                temp_thread_list.append(stuff)
                # Add all data into temp_thread_list
                
            # Try and determine if the temp thread exists in the global thread list, if it does this should indicate that it is running
            for thread in temp_thread_list:
                if thread in thread_list:
                    pass
                else:
                    thread_list.append(thread)
            # Run through run_threads with the thread_list
            run_threads(thread_list)
            #print("Outside run_threads")
        else:
            print("Database empty... nothing to do")
            time.sleep(0.1)
        
report()