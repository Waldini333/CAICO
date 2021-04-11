import uuid
# Represents the insurance agent
class Agent:
    def __init__(self, name, address):
        self.ID= str(uuid.uuid1())
        self.name = name
        self.address = address
        self.customers = [] #objects
        self.claims = [] #objects
        self.payments = []

    def assignCustomer(self, customer):
        self.customers.append(customer)

    def addClaim(self, claim):
        self.claims.append(claim)

    def addPayment(self, payment):
        self.payments.append(payment)



    # convert object o JSON
    def serialize(self):
        return {
            'id': self.ID,
            'name': self.name, 
            'address': self.address,
            # nested serialization as a list comprehension for customer objects necessary
            'customers': [c.serialize() for c in self.customers],
            'claims' : [claim.serialize() for claim in self.claims],
            'payments': [payment.serialize() for payment in self.payments]
        }