import Pyro5.api
import sys
import json
sys.path.append('..')  
sys.path.insert(1, './') 
from Models.Person import Person
import threading

from rsaCreate import createNewKey, getPublicKey

daemon = Pyro5.api.Daemon()

@Pyro5.api.expose
class Client(object):
    
    def notification(self,produto): 
        print(produto)
        x = threading.Thread(target=self.processNotification, args=(produto,))
        x.start()
           
    def processNotification(self,produto):
        print(produto)


def acess_server():
    nameserver = Pyro5.api.locate_ns()
    uri = nameserver.lookup("server.register")
    
    return Pyro5.api.Proxy(uri)

def create_new_client(name):
    createNewKey(name)
    publicKeyA = getPublicKey(name); 
    uri = daemon.register(Client)
    return Person(name,str(uri),publicKeyA)
    

gestor = create_new_client("Lucas")
server = acess_server()
server.create_client(json.dumps(gestor.__dict__))
daemon.requestLoop()





