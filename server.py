import socket
from Crypto.Cipher import AES
import database
import sys
import datetime

PORT = 65430



multiples_16 = [16,32,48,64,80,96,112,128,144,160,176,192,208,224,240,256]


def check_if_multiple(var_len):
    if var_len in multiples_16:
        return True
    else:
        return False

def add_padding(message):
    var_len = len(message)
    pad = "#"
    while check_if_multiple(var_len) == False:
        message = message + pad
        var_len = len(message)
        print(var_len)
    print(message)
    return message

def do_encrypt(message):
    iv = 16 * "\x00"
    print(iv)
    print(len(message))
    key = "glSM_ZF8[sg2KpZ1"
    aes_mode = AES.MODE_CBC
    obj = AES.new(key,aes_mode, iv)
    ciphertext = obj.encrypt(message)
    return ciphertext

def do_decrypt(ciphertext):
    iv = 16 * "\x00"
    key = "glSM_ZF8[sg2KpZ1"
    aes_mode = AES.MODE_CBC
    obj2 = AES.new(key, aes_mode, iv)
    message = obj2.decrypt(ciphertext*16)
    message = str(message)
    return message.strip("#")

def get_secrets(conn, addr):
    message = "Username,Password?"
    message = add_padding(message)
    ciphertext = do_encrypt(message)
    #ciphertext = ciphertext.decode('iso-8859-1')
    #ciphertext=ciphertext.encode('utf-8')
    conn.send(ciphertext)
    try:
        data = do_decrypt(conn.recv(4096))
        user = data.split(',')[0]
        password = data.split(',')[1].split("#")[0]
        user = user.split("'")[1]
        if "root" not in str(user) and "password" not in str(password):
            message = "Auth Failed"
            message = add_padding(message)
            ciphertext = do_encrypt(message)
            conn.send(ciphertext)
            conn.close()
        elif user == "root" and password == "password":
            message = "[+] Authentication Successful"
            message = add_padding(message)
            ciphertext = do_encrypt(message)
            conn.send(ciphertext)
            print(f"[+] Authentication successful from: {addr}")
            return True
        else:
            message = "Auth Failed"
            message = add_padding(message)
            ciphertext = do_encrypt(message)
            conn.send(ciphertext)
            conn.close()
    except IndexError:
        print("Missing user, password or both...")
        message = "Missing user, password or both..."
        message = add_padding(message)
        ciphertext = do_encrypt(message)
        conn.send(ciphertext)
        conn.close()
        conn.close()
        pass

def collect(data, addr, conn):
    data = data.split("#")[0]
    data = data.split("b'")[1]
    database.create_database()
    IP = data.split(',')[0]
    auth_type = data.split(',')[1]
    mac_addr = data.split(',')[2]
    ID = data.split(',')[3]
    hello_timeout = data.split(',')[4]
    _data = (IP, auth_type, mac_addr, ID, hello_timeout)
    database.update_database(_data)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM)as s:
     #s.setblocking(0)
     s.bind(('10.1.1.1', PORT))
     s.listen()
     srv_condition = True
     while srv_condition:
        conn, addr = s.accept()
        #check database if connection still active, if so, skip the auth
        from_client = ''
        if get_secrets(conn,addr):
            print("Passed auth")
            data = do_decrypt(conn.recv(4096))
            data = collect(data, addr, conn)
            #if not data: break
            from_client += str(data)
            print(from_client)
            message = "I AM SERVER"
            message = add_padding(message)
            ciphertext = do_encrypt(message)
            conn.send(ciphertext)
            if conn:
                print("still active inside")
            conn.close()
        conn.close()
        print("Connection terminated.")
        if conn:
            print("Still active")
            print(conn)
     print("Broke out of infinite loop")        
     conn.close()
     if conn:
         print("Still active")
         print(conn)
