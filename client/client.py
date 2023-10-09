from os import wait
import time
import Pyro5.api
import sys
import json
sys.path.append('..')  
sys.path.insert(1, './') 
from Models.Person import Person
from Models.Product import Product
import threading

from rsaCreate import createNewKey, getPublicKey, getSignatureToKey

gestor = ''
daemon = Pyro5.api.Daemon()

## Classe exposta com metodos de notificação
@Pyro5.api.expose
class Client(object):
    
    def notification(self,notification):
        print("--Notificação--") 
        for detail in notification:
            print(detail)
        print("--------")

def acess_server():
    nameserver = Pyro5.api.locate_ns()
    uri = nameserver.lookup("server.register")
    
    return Pyro5.api.Proxy(uri)

server = acess_server()

## Criação de cliente
def createAcessClient(this):
    daemon.requestLoop()
    

def create_new_client(name):
    createNewKey(name)
    publicKeyA = getPublicKey(name);
    cliente = Client() 
    uri = daemon.register(cliente)
    x = threading.Thread(target=createAcessClient, args=(1,))
    x.start()
    return Person(name,str(uri),publicKeyA)
    
    
## Funções de exibição de menus
def printMenu():
    print("--------------------------------")
    print("          MENU         \n")
    print("[1] - Cadastrar Novo produto")
    print("[2] - Retirar produto")
    print("[3] - Gerar Relatorio")
    print("[4] - Sair \n")
    option = input("Digite a ação que deseja realizar\n").strip()
    if option in [1,"1"]:
        addProduct()
    elif option in [2,"2"]:
        getProduct()
    elif option in [3,"3"]:
        printMenuRelatorio()
    elif option in [4,"4"]:
        exit()
    printMenu()

def return_menu():
    option = input("\nDeseja voltar ao menu S/n (S)\n").strip()
    if option == 'S' or option == 's':
        printMenuRelatorio()
    elif option == 'N' or "n":
        exit()
    else:
        return_menu()

def printMenuRelatorio():
    print("\n          MENU RELATORIO        \n")
    print("[1] - Visualizar estoque")
    print("[2] - Entrada e Saida")
    print("[3] - Produtos sem saida")
    print("[4] - Voltar")
    option = input("Digite a ação que deseja realizar\n").strip()
    if option in [1,"1"]:
        show_stock()
    elif option == "2":
        period = input("Digite o periodo de visualização em minutos\n").strip()
        show_input_output_stock(period)
    elif option == "3":
      period = input("Digite o periodo de visualização em minutos\n").strip()
      show_products_without_stock_period(period)
    elif option == "4":
        printMenu()

## --------

## Funções de ação aos produtos
def addProduct():
    global gestor
    name = input("Qual o nome do produto:\n").strip()
    code = input("Qual o codigo do produto:\n").strip()
    description = input("Qual a descrição do produto:\n").strip()
    amount = input("Qual a quantidade do produto:\n").strip()
    price = input("Qual o preço do produto:\n").strip()
    minimalStorage = input("Qual a quantidade minima do produto:\n").strip()
    produto = Product(code,name,description,amount,price,minimalStorage)
    result = server.create_product(json.dumps(produto.__dict__),getSignatureToKey(gestor.name))
    print(result)

def getProduct():
    global gestor
    code = input("Qual o codigo do produto:").strip()
    amount = input("Qual a quantidade do produto sera retirada:").strip()
    result = server.get_product(code,amount,getSignatureToKey(gestor.name))
    print(result)

## ---------

## Relatorios de pedido

def show_stock():
    stock = server.show_stock()
    print("Estoque de produtos:")    
    for obj in stock:
        print(obj)
    return_menu()

def show_input_output_stock(period):
    stock = server.show_input_output_stock(period)
    for obj in stock:
        print(obj)
    return_menu()

def  show_products_without_stock_period(period):
    stock = server.show_products_without_stock_period(period) 
    for obj in stock:
        print(obj)
    return_menu()

## ------------------

def init_user():
    global gestor
    name = input("\nDigite o nome do gestor que esta acessando o Sistema\n").strip()
    gestor = create_new_client(name)
    server.create_client(json.dumps(gestor.__dict__))
    print("Gestor acessado com sucesso \n")

init_user()
printMenu()
