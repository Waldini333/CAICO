import uuid

# Represents the customer of the car insurance company
class Customer:
    def __init__(self, name, address):
        self.ID= str(uuid.uuid1())
        self.name = name
        self.address = address
        self.cars = [] #objects
        self.agent = [] #one agent per customer only ID because of comment below
        self.claims = [] #objects
        self.payments = [] #objects

    def addCar (self, car):
        self.cars.append(car)


    def addAgent(self,agent):
        if len(self.agent) == 0:
            #!!! Can only implement ID not the whole agent object because agent and customer object
            # would reference each other and that causes the serialization to throw recursion errors
            # which Im not able solve
            self.agent = agent.ID
            return True
        else:
            return False

    def addClaim(self, claim):
        if len(self.agent) != 0:
            self.claims.append(claim)
            return True
        else:
            return False

    def addPayment(self, payment):
        self.payments.append(payment)

    # convert object o JSON
    def serialize(self):
        return {
            'id': self.ID, 
            'name': self.name, 
            'address': self.address,
            #nested serialization as a list comprehension for car objects necessary
            'cars': [car.serialize() for car in self.cars],
            'agent': self.agent,
            ### cannot implement that due to recursion issues
            #'agent': [a.serialize() for a in self.agent]
            'claims': [claim.serialize() for claim in self.claims],
            'payments': [payment.serialize() for payment in self.payments]
        }
    
class Car :
    def __init__(self, model_name, number_plate, motor_power, year):
        self.name = model_name
        self.number_plate = number_plate
        self.motor_power = motor_power
        self.year = year
        self.owner = [] #ID due to recursion error

    def setOwner(self, owner):
        self.owner = owner.ID

    # convert object o JSON
    def serialize(self):
        return {
            'model': self.name,
            'numberplate': self.number_plate,
            'motor power': self.motor_power,
            'manufacturing year': self.year,
            ### cannot implement that due to recursion issues
            #'owner': [c.serialize() for c in self.owner]
            'owner': self.owner
        }

class Claim:
    def __init__(self, date, incident_description, claim_amount):
        self.ID = str(uuid.uuid1())
        self.date = date
        self.incident_description = incident_description
        self.claim_amount = claim_amount
        self.status = None
        self.approved_amount = None
        self.responsible_agent = [] # ID only
        self.applicant = [] # ID only

    def setAgent(self, agent):
        self.responsible_agent = agent.ID

    def setApplicant(self, applicant):
        self.applicant = applicant.ID

    def evaluateStatus(self, amount):
        if self.approved_amount == None:
            self.approved_amount = amount
            if self.approved_amount >= self.claim_amount:
                self.status = "FULLY COVERED"
            elif self.approved_amount <= 0:
                self.status = "REJECTED"
            else:
                self.status = "PARTLY COVERED"
            return True
        else:
            return False

        # convert object to JSON
    def serialize(self):
        return {
            'id': self.ID,
            'date': self.date,
            'incident_description': self.incident_description,
            'claim_amount': self.claim_amount,
            'status' : self.status,
            'approved_amount' : self.approved_amount,
            'responsible_agent': self.responsible_agent,
            'applicant': self.applicant
        }

class Payment:
    def __init__(self,date):
        self.ID = str(uuid.uuid1())
        self.date = date

class Revenue(Payment):
    def __init__(self, date, customer_id, amount_received):
        Payment.__init__(self, date)
        self.customer_id = customer_id
        self.amount_received = amount_received

    def serialize(self):
        return {
            'id': self.ID,
            'date': self.date,
            'customer_id': self.customer_id,
            'amount_received': self.amount_received
        }

class Expense(Payment):
    def __init__(self, date, agent_id, amount_sent):
        Payment.__init__(self, date)
        self.agent_id = agent_id
        self.amount_sent = amount_sent

    def serialize(self):
        return {
            'id': self.ID,
            'date': self.date,
            'agent_id': self.agent_id,
            'amount_sent': self.amount_sent
        }

