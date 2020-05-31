import socket
import os
from Crypto.Cipher import AES
HOST = "10.1.1.1"
PORT=65430

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
    iv = 16 * '\x00'
    key = "glSM_ZF8[sg2KpZ1"
    aes_mode = AES.MODE_CBC
    obj = AES.new(key, AES.MODE_CBC, iv)
    ciphertext = obj.encrypt(message)
    return ciphertext

def do_decrypt(ciphertext):
    iv = 16 * '\x00'
    print("cipher: ",ciphertext)
    key = "glSM_ZF8[sg2KpZ1"
    aes_mode = AES.MODE_CBC
    obj2 = AES.new(key, AES.MODE_CBC, iv)
    message = obj2.decrypt(ciphertext)
    message = str(message)
    print("\nDecoded:",message.split("#")[0])
    return message

def send_secrets(data,s):
     if "Username,Password?" in data:
        message = "root,password"
        message = add_padding(message)
        s.send(do_encrypt(message))
        #s.send(b"root,password")
        do_decrypt(s.recv(4096))
        message = "192.168.1.50,AES,a1:b3:5d:af:cc:ff,remote99,1"
        message = add_padding(message)
        s.send(do_encrypt(message))
        data = do_encrypt(s.recv(4096))
        print(data)
        return True
     else:
         print("Unknown response received from server")
         s.close()
         return False
     
def connect():
 with socket.socket(socket.AF_INET, socket.SOCK_STREAM)as s:
    s.connect((HOST, PORT))
    data = do_decrypt(s.recv(4096))
    if send_secrets(data,s):
      print("Logged in.")
    
connect()

      
      
    

