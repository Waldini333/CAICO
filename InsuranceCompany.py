from Customer import *
from Agent import *

class InsuranceCompany:
    def __init__(self, name):
        self.name = name # Name of the Insurance company
        self.customers = [] # list of customers
        self.agents = []  # list of dealers
        self.claims = []
        self.payments = []
        self.revenues = []
        self.expenses = []
        
    def getCustomers (self):
        return list(self.customers)

    def addCustomer (self, name, address):
        c = Customer (name, address)
        self.customers.append(c)
        return c.ID

    def getCustomerById(self, id_):
        for d in self.customers:
            if(d.ID==id_):
                #d is object customer
                return d
        return None


    def deleteCustomer (self, customer_id):
        c = self.getCustomerById(customer_id)
        self.customers.remove(c)
        return True

    def addAgent (self, name, address):
        a = Agent(name, address)
        self.agents.append(a)
        return a.ID

    def getAgentById(self, id_):
        for d in self.agents:
            if(d.ID==id_):
                #d is object agent
                return d
        return None

    def deleteAgent (self, agent_id):
        a = self.getAgentById(agent_id)
        self.agents.remove(a)
        return True

    def getAgents(self):
        return list(self.agents)

    def addClaim(self, date, incident_description, claim_amount):
        claim = Claim(date, incident_description, claim_amount)
        self.claims.append(claim)
        return claim.ID

    def getClaimById(self, id_):
        for d in self.claims:
            if(d.ID==id_):
                #d is object claim
                return d
        return None

    def getClaims(self):
        return list(self.claims)

    def addRevenue(self, date, customer_id, amount_received):
        revenue = Revenue(date, customer_id, amount_received)
        self.revenues.append(revenue)
        self.payments.append(revenue)
        return revenue.ID

    def addExpense(self, date, agent_id, amount_sent):
        expense = Expense(date, agent_id, amount_sent)
        self.expenses.append(expense)
        self.payments.append(expense)
        return expense.ID

    def getPaymentById(self, id_):
        for d in self.payments:
            if(d.ID==id_):
                #d is object Revenue or Expense
                return d
        return None

    def getPayments(self):
        return list(self.payments)

    def getRevenues(self):
        return list(self.revenues)


