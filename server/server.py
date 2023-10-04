from datetime import datetime
import os
from tkinter import E
import Pyro5.api
import json
import sys


sys.path.append('..') 
sys.path.insert(1, './') # Adicione o diretório pai (project) ao sys.path
from Models.Person import Person
from Models.Product import Product
import rsa


userAcess= ''

class Services:
    def load_user(self,nameUser):
        with open("person_"+ nameUser,"r") as f:
            return Person.from_dict(json.loads(f.read()))
            
    def send_client_notification(person:Person):
        client = Pyro5.api.Proxy(person.referenceRemote)
        client.notification("acessado com sucesso")
        print("tentativa de acesso ao client")

    def validate_signature(self,person:Person,signature):
        message = "the user " + person.name + " .signature check."
        rsa.verify(message.encode(),signature,rsa.PublicKey.load_pkcs1(person.publicKey.encode()))

@Pyro5.api.expose
class ServerController(object):
    @Pyro5.api.oneway
    def create_client(this, person):
        person_data = json.loads(person)
        userAcess= person_data["name"]
        if not os.path.exists("server/users/person_"+ userAcess + ".json"):
            print("Realizando cadastro de cliente")
            with open("server/users/person_"+ userAcess + ".json","w") as f:
                f.write(person)
        else:
            print("Cliente ja cadastrado")

    def save_product(this,product):
        productData = json.loads(product)
        newProduct = Product.from_dict(productData)
        pathName = "server/product/"+ newProduct.code + "_" + newProduct.name + ".json"
        if not os.path.exists(pathName):
            newProduct.add_data_history({"action":"Criando produto na base", "date": datetime.now()})
            with open(pathName,"w") as f:
                f.write(product)
                return "produto criado com sucesso"
        else:
            with open(pathName,"r") as f:
               lastProducts = Product.from_dict(json.loads(f.read()))
        
        if newProduct.amount > 0:
            lastProducts.amount += newProduct.amount
            lastProducts.add_data_history({"action":"Adicionando " + newProduct.amount + "ao estoque. ","date": datetime.now()})
        elif newProduct.price != lastProducts.price:
            lastProducts.add_data_history({"action":"Alterando o preço do produto de " + lastProducts.price + "para " + newProduct.price ,"date": datetime.now()})
            lastProducts.price = newProduct.price
        with open(pathName,"w") as f:
                f.write(json.dumps())
        return "Produto Alterado com sucesso"


    def create_product(this,product,signature):
        service = Services()
        signature = bytes.fromhex(signature)
        user = service.load_user(userAcess)
        validRequest = service.validate_signature(user,signature)
        if validRequest:
            return this.save_product(product)
        else:
            return "A assinatura do usuario não é valida para realizar essa ação"



daemon = Pyro5.server.Daemon()         # make a Pyro daemon
ns = Pyro5.api.locate_ns()             # find the name server
uri = daemon.register(ServerController)   # register the greeting maker as a Pyro object
ns.register("server.register", uri)   # register the object with a name in the name server
daemon.requestLoop() 