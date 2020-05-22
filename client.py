import socket
import os
from Crypto.Cipher import AES
HOST = "127.0.0.1"
PORT=65430

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
        s.send(b"root,password")
        print(s.recv(4096))
        s.send(b"11111111111111111111111")
        data= s.recv(4096)
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

      
      
    

