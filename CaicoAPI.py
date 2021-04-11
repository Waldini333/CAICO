from flask import Flask, request, jsonify
from InsuranceCompany import *
from Customer import *

# these modules are used for stats
import itertools
from operator import itemgetter

app = Flask(__name__)

# Root object for the insurance company
company = InsuranceCompany ("Be-Safe Insurance Company")

#Add a new customer (parameters: name, address).
@app.route("/customer", methods=["POST"])
def addCustomer():
    # parameters are passed in the body of the request
    cid = company.addCustomer(request.args.get('name'), request.args.get('address'))
    return jsonify(f"Added a new customer with ID {cid}")

#Return the details of a customer of the given customer_id.
@app.route("/customer/<customer_id>", methods=["GET"])
def customerInfo(customer_id):
    c = company.getCustomerById(customer_id)
    if(c!=None):
        return jsonify(c.serialize())
    return jsonify(
            success = False, 
            message = "Customer not found")

#Add a new car (parameters: model, numberplate).
@app.route("/customer/<customer_id>/car", methods=["POST"])
def addCar(customer_id):
    c = company.getCustomerById(customer_id)
    #check if customer is existing (look up getCusomerById method)
    if(c!=None):
        car = Car(request.args.get('model_name'), request.args.get('number_plate'), request.args.get('motor_power'), request.args.get('year'))
        c.addCar(car)
        #set a customer for car object
        car.setOwner(c)
        return jsonify(f"Added a new car to {c.ID}")
    return jsonify(
            success = c!=None,
            message = "Customer not found")
    
@app.route("/customer/<customer_id>", methods=["DELETE"])
def deleteCustomer(customer_id):
    c = company.getCustomerById(customer_id)
    result = company.deleteCustomer(customer_id)
    if(result): 
        message = f"Customer with id {c.ID} was deleted"
    else: 
        message = "Customer not found"
    return jsonify(
            success = result, 
            message = message)

@app.route("/customers", methods=["GET"])
def allCustomers():
    return jsonify(customers=[h.serialize() for h in company.getCustomers()])

#Add a new agent (parameters: name, address).
@app.route("/agent", methods=["POST"])
def addAgent():
    # parameters are passed in the body of the request
    aid = company.addAgent(request.args.get('name'), request.args.get('address'))
    return jsonify(f"Added a new agent with ID {aid}")

#Return the details of a agent of the given agent_id.
@app.route("/agent/<agent_id>", methods=["GET"])
def agentInfo(agent_id):
    a = company.getAgentById(agent_id)
    #check if agent is existing (look up getAgentById method)
    if(a!=None):
        return jsonify(a.serialize())
    return jsonify(
            success = False,
            message = "Agent not found")

#Assign a new customer with the provided customer_ID to the agent with agent_ID
@app.route("/agent/<agent_id>/<customer_id>", methods=["POST"])
def assignCustomer(agent_id, customer_id):
    a = company.getAgentById(agent_id)
    c = company.getCustomerById(customer_id)
    if(c!=None and a!= None):
        success = c.addAgent(a) #adds one agent max (BUT ONLY ID DUE TO RECURSION PROBLEMS) (look up method and customer serialization)
        if success:
            a.assignCustomer(c) #adds customer objects to agent
            return jsonify(f"Added a new Customer {c.ID} to Agent {a.ID}")
        else:
            return jsonify(
            success = success,
            message = f"Customer {c.ID} has already an Agent"
            )
    return jsonify(
            success = c!=None,
            message = "Customer not found")

@app.route("/agent/<agent_id>", methods=["DELETE"])
def deleteAgent(agent_id):
    a = company.getAgentById(agent_id)
    if a != None:
        #check if agent has already customers
        if len(a.customers) != 0:
            list_agents = company.getAgents()
            len_agents = len(list_agents)
            #checking if only one agent
            if len_agents > 1:
                index_agent = list_agents.index(a)
                #checking if there is another agent left or right to agent who will be deleted
                if index_agent >= 1:

                    #moving all CUSTOMERS from agent who will be deleted to other agent
                    for c in a.customers:
                        c.agent = list_agents[index_agent-1].ID
                        list_agents[index_agent-1].customers.append(c)

                    # moving all CLAIMS from agent who will be deleted to other agent
                    for claim in a.claims:
                        claim.responsible_agent = list_agents[index_agent-1].ID
                        list_agents[index_agent - 1].claims.append(claim)


                    result = company.deleteAgent(agent_id)
                    message = f"Agent with id {agent_id} was deleted and his customers, claims moved to Agent with ID {list_agents[index_agent-1].ID}"
                else:
                    # moving all CUSTOMERS from agent who will be deleted to other agent
                    for c in a.customers:
                        c.agent = list_agents[index_agent + 1].ID
                        list_agents[index_agent + 1].customers.append(c)

                    # moving all CLAIMS from agent who will be deleted to other agent
                    for claim in a.claims:
                        claim.responsible_agent = list_agents[index_agent + 1].ID
                        list_agents[index_agent + 1].claims.append(claim)

                    result = company.deleteAgent(agent_id)
                    message = f"Agent with id {agent_id} was deleted and his customers, claims moved to Agent with ID {list_agents[index_agent+1].ID}"


            else:
                result = False
                message = f"Agent with id {agent_id} has customers but is the only agent in the company"

        else:
            result = company.deleteAgent(agent_id)
            message = f"Agent with id {agent_id} was deleted"

    else:
        result = False
        message = f"Agent with id {agent_id} not found"

    return jsonify(
            success = result,
            message = message)

@app.route("/agents", methods=["GET"])
def allAgents():
    return jsonify(agents=[h.serialize() for h in company.getAgents()])

#Add a new claim (parameters: date, incident_description, claim_amount).
@app.route("/claims/<customer_id>/file", methods=["POST"])
def addClaim(customer_id):
    c = company.getCustomerById(customer_id)

    # parameters are passed in the body of the request
    claim_id = company.addClaim(request.args.get('date'), request.args.get('incident_description'), request.args.get('claim_amount'))
    claim = company.getClaimById(claim_id)

    #checking if customer has already an agent
    if len(c.agent) != 0:
        #adding claim object to customer
        success = c.addClaim(claim)
        #getting agent from customer object
        a = company.getAgentById(c.agent)
        #adding claim object to responsible agent as well
        a.addClaim(claim)

        #set IDs for claim objects from customer and agent
        claim.setApplicant(c)
        claim.setAgent(a)

        return jsonify(
            success=success,
            message=f"Claim with ID {claim.ID} for Customer {c.ID} was filed and Agent {a.ID} got notified"
        )
    else:
        return jsonify(
            success= False,
            message=f"Customer {c.ID} has no agent yet"
        )

#Return the details of a claim
@app.route("/claims/<claim_id>", methods=["GET"])
def claimInfo(claim_id):
    claim = company.getClaimById(claim_id)
    if(claim != None):
        return jsonify(claim.serialize())
    return jsonify(
            success = False,
            message = "Claim not found")

#Changes the status of a claim
@app.route("/claims/<claim_id>/status", methods=["PUT"])
def claimStatus(claim_id):
    claim = company.getClaimById(claim_id)
    approved_amount = request.args.get('approved_amount')
    if(claim != None):
        claim.evaluateStatus(approved_amount)
    return jsonify(
            success = False,
            message = "Claim not found")

@app.route("/claims", methods=["GET"])
def allClaims():
    return jsonify(claims=[h.serialize() for h in company.getClaims()])

#Add a new RECEIVED payment (parameters: date,customer_id, amount_received).
@app.route("/payment/in", methods=["POST"])
def receivePayment():
    customer_id = request.args.get('customer_id')
    c = company.getCustomerById(customer_id)

    #checking if customer is existing
    if c != None:
        a = company.getAgentById(c.agent)
        #checking if customer has already an agent
        if a != None:
            revenue_id = company.addRevenue(request.args.get('date'), request.args.get('customer_id'), request.args.get('amount_received'))
            revenue = company.getPaymentById(revenue_id)
            c.addPayment(revenue)

            return jsonify(
                success=True,
                message=f"Payment with ID {revenue.ID} from Customer {c.ID} was added"
            )
        else:
            return jsonify(
                success=False,
                message=f"Customer with ID {c.ID} has no agent yet"
            )

    else:
        return jsonify(
            success=False,
            message=f"Customer not found"
        )

#Add a new TRANSFERRED payment (parameters: date,agent_id, amount_sent).
@app.route("/payment/out", methods=["POST"])
def transferPayment():
    agent_id = request.args.get('agent_id')
    a = company.getAgentById(agent_id)
    if a != None:
        expense_id = company.addExpense(request.args.get('date'), request.args.get('agent_id'), request.args.get('amount_sent'))
        expense = company.getPaymentById(expense_id)
        a.addPayment(expense)

        return jsonify(
            success=True,
            message=f"Payment with ID {expense.ID} to Agent with ID {a.ID} was added"
        )
    else:
        return jsonify(
            success=False,
            message=f"Agent not found"
        )

@app.route("/payments", methods=["GET"])
def allPayments():
    return jsonify(claims=[h.serialize() for h in company.getPayments()])

@app.route("/stats/claims", methods=["GET"])
def statsClaims():
    list_customers = [h.serialize() for h in company.getCustomers()]
    list_of_dicts= []

    # group all claims by agents
    # forming a list of dicts for each claim

    for i in list_customers:
        list_of_dicts.append({"agent" : i["agent"] , "claims" : i["claims"]})

    list_claims_grouped = []

    # aggregate the dicts

    for key, value in itertools.groupby(list_of_dicts, key=itemgetter('agent')):
        list_claims_grouped.append({key : i.get("claims") for i in value})


    return jsonify(
        data_structure="{<agent_ID> : [<claims>]}",
        data = list_claims_grouped
    )

@app.route("/stats/revenues", methods=["GET"])
def statsRevenues():

    #same procedure as stats/claims

    list_customers = [h.serialize() for h in company.getCustomers()]
    list_of_dicts = []


    for i in list_customers:
        list_of_dicts.append({"agent" : i["agent"] , "revenues" : i["payments"]})

    list_revenues_grouped = []

    for key, value in itertools.groupby(list_of_dicts, key=itemgetter('agent')):
        list_revenues_grouped.append({key : i.get("revenues") for i in value})

    return jsonify(
        data_structure="{<agent_ID> : [<revenues>]}",
        data=list_revenues_grouped
    )

@app.route("/stats/agents", methods=["GET"])
def statsAgents():

    list_customers = [h.serialize() for h in company.getCustomers()]
    list_of_dicts= []

#group all claims by agents
    #forming a list of dicts for each claim
    for i in list_customers:
        list_of_dicts.append({"agent" : i["agent"] , "claims" : i["claims"]})

    list_claims_grouped = []

    #aggregate the dicts
    for key, value in itertools.groupby(list_of_dicts, key=itemgetter('agent')):
        list_claims_grouped.append({key : i.get("claims") for i in value})

    list_claims_points = []

    #use length of values for each agent to form points with an factor
    for i in list_claims_grouped:
        for k, v in i.items():
            list_claims_points .append({k: len(v)*(-0.5)}) #factor


    ###############################
    #same procedure as claims

    list_of_dicts = []

    for i in list_customers:
        list_of_dicts.append({"agent": i["agent"], "revenues": i["payments"]})

    list_revenues_grouped = []

    for key, value in itertools.groupby(list_of_dicts, key=itemgetter('agent')):
        list_revenues_grouped.append({key: i.get("revenues") for i in value})

    list_revenues_points = []

    for i in list_revenues_grouped:
        for k, v in i.items():
            list_revenues_points.append({k: len(v) * (0.5)})


    ###############################
    # same procedure as claims

    list_agents = [h.serialize() for h in company.getAgents()]
    list_of_dicts = []

    for i in list_agents:
        list_of_dicts.append({"agent" : i["id"] , "customers" : i["customers"]})


    list_customers_grouped = []

    for key, value in itertools.groupby(list_of_dicts, key=itemgetter('agent')):
        list_customers_grouped.append({key : i.get("customers") for i in value})

    list_customers_points = []

    for i in list_customers_grouped:
        for k, v in i.items():
            list_customers_points.append({k: len(v) * (1)})

    ###################################

    #append all lists with pointdicts to superlist

    superlist = []
    for i in list_claims_points:
        superlist.append(i)
    for i in list_revenues_points:
        superlist.append(i)
    for i in list_customers_points:
        superlist.append(i)


    #Group points by keys and sum them up

    aggregate_dict = dict.fromkeys(set().union(*superlist), 0)

    for d in superlist:
        for k in d.keys():
            aggregate_dict[k] += d[k]


    #sort the dictionary
    sorted_tuples = sorted(aggregate_dict.items(), key=itemgetter(1))
    sorted_aggregate_dict = {k: v for k, v in sorted_tuples}



    return jsonify(
        data_structure="sorted by values (points) decreasing {<agent_ID> : <sum of points>}",
        data = sorted_aggregate_dict
    )


###DO NOT CHANGE CODE BELOW THIS LINE ##############################
@app.route("/")
def index():
    return jsonify(
            success = True, 
            message = "Your server is running! Welcome to the Insurance Company API.")

@app.after_request
def add_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] =  "Content-Type, Access-Control-Allow-Headers, Authorization, X-Requested-With"
    response.headers['Access-Control-Allow-Methods']=  "POST, GET, PUT, DELETE"
    return response

if __name__ == "__main__":
    app.run(debug=True, port=8888)
