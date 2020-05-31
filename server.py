import socket
from Crypto.Cipher import AES
import database
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
    print(ciphertext)
    print(type(ciphertext))
    #ciphertext = ciphertext.decode('iso-8859-1')
    #ciphertext=ciphertext.encode('utf-8')
    conn.send(ciphertext)
    try:
        data = do_decrypt(conn.recv(4096))
        print(data)
        user = data.split(b',')[0]
        password = data.split(b',')[1]
        if "root" not in str(user) and "password" not in str(password):
            conn.send(b"Auth failed")
            conn.close()
        elif user == b"root" and password == b"password":
            conn.send(b"[+] Authentication successful")
            print(f"[+] Authentication successful from: {addr}")
            return True
        else:
            conn.send(b"Auth Failed")
            conn.close()
    except IndexError:
        print("Missing user, password or both...")
        conn.send(b"Missing user, password or both...")
        conn.close()
        conn.close()
        pass

def collect(conn, addr):
    print(conn)
    database.create_database()
    IP = conn.split(b',')[0].decode('utf-8')
    auth_type = conn.split(b',')[1].decode('utf-8')
    mac_addr = conn.split(b',')[2].decode('utf-8')
    ID = conn.split(b',')[3].decode('utf-8')
    hello_timeout = conn.split(b',')[4].decode('utf-8')
    data = (IP, auth_type, mac_addr, ID, hello_timeout)
    database.update_database(data)

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
            data = collect(conn.recv(4096), addr)
            #if not data: break
            from_client += str(data)
            print(from_client)
            conn.send(b"I AM SERVER")
            conn.close()
        conn.close()
        print("Connection terminated.")
     print("Broke out of infinite loop")        
     conn.close()
