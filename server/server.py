import os
import Pyro5.api
import json
import sys
sys.path.append('..') 
sys.path.insert(1, './') # Adicione o diretório pai (project) ao sys.path
from Models.Person import Person

@Pyro5.api.expose
class ServerController(object):
    @Pyro5.api.oneway
    def create_client(this, person):
        person_data = json.loads(person)
        if not os.path.exists("server/person_"+ person_data["name"] + ".json"):
            print("Realizando cadastro de cliente")
            with open("server/person_"+ person_data["name"] + ".json","wb") as f:
                f.write(person)
        else:
            print("Cliente ja cadastrado")

class Services:
    def load_user(this,nameUser):
        with open("person_"+ nameUser,"rb") as f:
            return Person.from_dict(json.loads(f.read()))
            
    def send_client_notification(this, person:Person):
        client = Pyro5.api.Proxy(person.referenceRemote)
        client.notification("acessado com sucesso")
        print("tentativa de acesso ao client")

daemon = Pyro5.server.Daemon()         # make a Pyro daemon
ns = Pyro5.api.locate_ns()             # find the name server
uri = daemon.register(ServerController)   # register the greeting maker as a Pyro object
ns.register("server.register", uri)   # register the object with a name in the name server
daemon.requestLoop() 