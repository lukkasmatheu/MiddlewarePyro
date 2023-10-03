import os
import rsa

def createNewKey(name):
    namePath = name + "_key.pem"
    if not os.path.exists("client/public_" + namePath):
        public_key, private_key = rsa.newkeys(1024)
        with open("client/public_"+ namePath,"wb") as f:
            f.write(public_key.save_pkcs1("PEM"))
        with open("client/private_" + namePath,"wb") as f:
            f.write(private_key.save_pkcs1("PEM"))

def getPublicKey(name):
    namePath = name + "_key.pem"
    with open("client/public_"+ namePath,"rb") as f:
        return f.read().decode()