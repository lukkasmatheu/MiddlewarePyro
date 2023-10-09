from datetime import datetime,timedelta
from math import prod
import os
import threading
import time
from unicodedata import name
import schedule
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
        with open("server/users/person_"+ nameUser + ".json","r") as f:
            user = f.read()
        return Person.from_dict(json.loads(user))   

    def send_client_notification(self,notification):
        person = self.load_user(userAcess)
        client = Pyro5.api.Proxy(person.referenceRemote)
        client.notification(notification)

    def validate_signature(self,signature):
        global userAcess
        signature = bytes.fromhex(signature)
        person = self.load_user(userAcess)
        message = "the user " + person.name + " .signature check." 
        try:
            rsa.verify(message.encode(),signature,rsa.PublicKey.load_pkcs1(person.publicKey.encode()))
            return True
        except rsa.VerificationError:
            return False

    def init_report(self):
        schedule.every(1).minutes.do(self.report_product)
        while True:
            schedule.run_pending()
            time.sleep(1)

    def report_product(self):
        if os.path.exists("server/product/"):
            try:
                produtcsPath = os.listdir('server/product/')
                notification = []
                if produtcsPath:
                    for productPath in produtcsPath:
                        product =  Product.from_dict(self.read_file("server/product/" + productPath))
                        if float(product.amount) < float(product.minimalStorage):
                            notification.append("O Produto " + product.name + " codigo:" + product.code + " esta com estoque minimo. quantidade:" + str(product.amount) + " reabasteça seu estoque.")
                    
                    notification.append(self.show_products_without_stock_period(3))
                    self.send_client_notification(notification)
            except:
                time.sleep(1)  
                
    def save_file(self,pathName,jsonItem):
        with open(pathName,"w") as f:
                f.write(jsonItem)
    
    def read_file(self,pathName):
        with open(pathName,"r") as f:
               return json.loads(f.read())
    
    def show_products_without_stock_period(self,period):
        produtcsPath = os.listdir('server/product/')
        notification = []
        for productPath in produtcsPath:
            product =  Product.from_dict(self.read_file("server/product/" + productPath))
            haschange = True
            for changes in product.history:
                if changes["action"] == "retirada" and datetime.datetime.strptime(changes["date"], '%Y-%m-%d %H:%M:%S.%f') > datetime.now() + timedelta(minutes=-float(period)):
                        haschange = False
            if haschange:
                notification.append("O Produto " + product.name + " codigo:" + product.code + " não esta sendo vendido no periodo. quantidade:" + str(product.amount) + " Altere o preço do produto se necessario.")
        return notification
                

@Pyro5.api.expose
class ServerController(object):
    
    __service = Services()
    @Pyro5.api.oneway
    def create_client(this, person):
        global userAcess
        person_data = json.loads(person)
        userAcess= person_data["name"]
        pathName = "server/users/person_"+ userAcess + ".json"
        if not os.path.exists(pathName):
            print("Realizando cadastro de cliente")
            this.__service.save_file(pathName,person)
        else:
            personDTO = this.__service.load_user(userAcess)
            personDTO.referenceRemote = person_data["referenceRemote"]
            this.__service.save_file(pathName,json.dumps(personDTO.__dict__))
            print("Cliente ja cadastrado. Realizando login\n")
        x = threading.Thread(target=this.__service.init_report(), args=(1,))
        x.start()
    #metodo que realiza o save ou update do produto
    def save_product(this,product): 
        newProduct = Product.from_dict(json.loads(product))
        pathName = "server/product/"+ newProduct.code + ".json"
        if not os.path.exists(pathName):
            newProduct.add_data_history({"action":"criacao","reason":"Criando produto na base", "date": datetime.now()})
            this.__service.save_file(pathName,json.dumps(newProduct.__dict__, default=str))
            return "produto criado com sucesso"
        else:
            lastProducts = Product.from_dict(this.__service.read_file(pathName))
        
        if newProduct.amount > 0:
            lastProducts.amount = float(lastProducts.amount) + float(newProduct.amount)
            lastProducts.add_data_history({"action":"alteracao","reason":"Adicionando " + newProduct.amount + "ao estoque. ","date": datetime.now()})
        if newProduct.price != lastProducts.price:
            lastProducts.add_data_history({"action":"alteracao","reason":"Alterando o preço do produto de " + lastProducts.price + "para " + newProduct.price ,"date": datetime.now()})
            lastProducts.price = newProduct.price

        this.__service.save_file(pathName,json.dumps(lastProducts.__dict__, default=str))
        return "Produto Alterado com sucesso"


    def create_product(this,product,signature):
        validRequest = this.__service.validate_signature(signature)
        if validRequest:
            return this.save_product(product)
        else:
            return "A assinatura do usuario não é valida para realizar essa ação"
    
    def get_product(this,code,amount,signature):
        pathName = "server/product/"+ code + ".json"
        validRequest = this.__service.validate_signature(signature)
        if validRequest:
            if os.path.exists(pathName):
                produto =  Product.from_dict(this.__service.read_file(pathName))
                if float(produto.amount) - float(amount) >= 0:
                    produto.add_data_history({"action":"retirada","reason":"Removendo " + amount + " " + produto.name + " do estoque.", "date": datetime.now()})
                    produto.amount = float(produto.amount) - float(amount)
                    this.__service.save_file(pathName,json.dumps(produto.__dict__,default=str))
                    return "\nRetirada de " + produto.name + "realizada com sucesso. Estoque atual : " + str(produto.amount) 
                else:
                    return 'Não foi possivel retirar o produto ' + produto.name + ' . A quantidade que voce busca retirar e maior que o estoque atual.'

        else:
            return "A assinatura do usuario não é valida para realizar essa ação"
    
    def show_stock(this):
        stock = []
        produtcsPath = os.listdir('server/product/')
        for productPath in produtcsPath:
           product =  Product.from_dict(this.__service.read_file("server/product/" + productPath))
           stock.append({"produto": product.name,"quantidade":product.amount})
        return stock


daemon = Pyro5.server.Daemon()       
ns = Pyro5.api.locate_ns()             
uri = daemon.register(ServerController)   
ns.register("server.register", uri)   
daemon.requestLoop() 