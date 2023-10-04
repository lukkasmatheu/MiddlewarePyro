class Product:
    def __init__(self,code,name,description,amount,price,minimalStorage):
        self.code = code
        self.name = name
        self.description = description
        self.amount = amount
        self.price = price
        self.minimalStorage = minimalStorage
        self.history = []


    @classmethod
    def from_dict(self, data):
        return self(data['code'], data['name'], data['description'], data['amount'], data['price'], data['minimalStorage'])

    def add_data_history(self,history):
        self.history.append(history)        

        