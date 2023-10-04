import Pyro5.api
import sys
import json
sys.path.append('..')  
sys.path.insert(1, './') 
from Models.Person import Person
from Models.Product import Product
import threading

from rsaCreate import createNewKey, getPublicKey, getSignatureToKey


daemon = Pyro5.api.Daemon()
@Pyro5.api.expose
class Client(object):
    
    def notification(self,produto): 
        print(produto)
        
    def processNotification(self,produto):
        print(produto)


def acess_server():
    nameserver = Pyro5.api.locate_ns()
    uri = nameserver.lookup("server.register")
    
    return Pyro5.api.Proxy(uri)

server = acess_server()

def createAcessClient(args):
    daemon.requestLoop()
    

def create_new_client(name):
    createNewKey(name)
    publicKeyA = getPublicKey(name);
    cliente = Client() 
    uri = daemon.register(cliente)
    x = threading.Thread(target=createAcessClient, args=(1,))
    x.start()
    return Person(name,str(uri),publicKeyA)
    
def printMenu():
    print("\n--------------------------------------\n")
    print("\n          MENU         \n")
    print("[1] - Cadastrar Novo produto\n")
    print("[2] - Retirar produto\n")
    option = input("Digite a ação que deseja realizar").strip()
    if option in [1,"1"]:
        addProduct()
    elif option in [2,"2"]:
        getProduct()
    else:
        printMenu()

def addProduct():
    name = input("Qual o nome do produto:").strip()
    code = input("Qual o codigo do produto:").strip()
    description = input("Qual a descrição do produto:").strip()
    amount = input("Qual a quantidade do produto:").strip()
    price = input("Qual o preço do produto:").strip()
    minimalStorage = input("Qual a quantidade minima do produto:").strip()
    produto = Product(code,name,description,amount,price,minimalStorage)
    server.create_product(produto,getSignatureToKey(gestor.name))

def getProduct():
    code = input("Qual o codigo do produto:").strip()
    amount = input("Qual a quantidade do produto sera retirada:").strip()

name = input("Digite o nome do gestor que esta acessando o Sistema").strip()
gestor = create_new_client(name)
server.create_client(json.dumps(gestor.__dict__))
print("Gestor acessado com sucesso \n")
printMenu()








