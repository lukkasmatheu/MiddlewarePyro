from datetime import datetime
import os
from sched import scheduler
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

    def report_product(self):
        print(os.listdir('/produtos'))

    def save_file(self,pathName,jsonItem):
        with open(pathName,"w") as f:
                f.write(jsonItem)
    
    def read_file(self,pathName):
        with open(pathName,"w") as f:
               return json.loads(f.read())


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
            print("Cliente ja cadastrado. Realizando login")

    #metodo que realiza o save ou update do produto
    def save_product(this,product): 
        service = Services()
        newProduct = Product.from_dict(json.loads(product))
        pathName = "server/product/"+ newProduct.code + ".json"
        if not os.path.exists(pathName):
            newProduct.add_data_history({"action":"Criando produto na base", "date": datetime.now()})
            service.save_file(pathName,json.dumps(newProduct))
            return "produto criado com sucesso"
        else:
            lastProducts = Product.from_dict(service.read_file(pathName))
        
        if newProduct.amount > 0:
            lastProducts.amount += newProduct.amount
            lastProducts.add_data_history({"action":"Adicionando " + newProduct.amount + "ao estoque. ","date": datetime.now()})
        if newProduct.price != lastProducts.price:
            lastProducts.add_data_history({"action":"Alterando o preço do produto de " + lastProducts.price + "para " + newProduct.price ,"date": datetime.now()})
            lastProducts.price = newProduct.price

        service.save_file(pathName,json.dumps(lastProducts))
        return "Produto Alterado com sucesso"


    def create_product(this,product,signature):
        service = Services()
        scheduler.every(1).minutes.do(service.report_product)
        signature = bytes.fromhex(signature)
        user = service.load_user(userAcess)
        validRequest = service.validate_signature(user,signature)
        if validRequest:
            return this.save_product(product)
        else:
            return "A assinatura do usuario não é valida para realizar essa ação"
    
    def get_product(this,code,amount):
        pathName = "server/product/"+ code + ".json"
        if os.path.exists(pathName):
            with open(pathName,"r") as f:
               produto =  Product.from_dict(json.loads(f.read()))
        produto.add_data_history({"action":"Criando produto na base", "date": datetime.now()})


daemon = Pyro5.server.Daemon()       
ns = Pyro5.api.locate_ns()             
uri = daemon.register(ServerController)   
ns.register("server.register", uri)   
daemon.requestLoop() 