# -*- coding: utf-8 -*-
"""
@author: ZohrehRaziei
"""

"""
Porgrammer Zohreh Raziei: zohrehraziei@gmail.com
vehicle Routing Problem with Disruption - using callback for adding cuts - Simulation

            
approach:

       - solve the vehicle routing problem.
       - start with assignment model (depot has a special status)
       - add cuts until all components of the graph are connected
       
    Parameters:
        - V: set/list of nodes in the graph
        - c[i,j]: travel cost for traversing edge (i,j)
        - m: number of vehicles available
        - q[i]: demand for customer i
        - Q: vehicle capacity
        
    Returns the optimum objective value and the list of edges used.
    
    vrp_callback: add constraint to eliminate infeasible solutions
            - Parameters: gurobi standard:
            - model: current model
            - where: indicator for location in the search
        If solution is infeasible, adds a cut using cbLazy
        
"""
import math
import random
import networkx
from gurobipy import *

def vrp(V,c,m,q,Q,vlu):
    def vrp_callback(model,where):

        # remember to set     model.params.DualReductions = 0     before using!
        # remember to set     model.params.LazyConstraints = 1     before using!
        if where != GRB.callback.MIPSOL:
            return
        edges = []
        for (i,j) in x:
            if model.cbGetSolution(x[i,j]) > .5:
                if i != V[0] and j != V[0]:
                    edges.append( (i,j) )
        G = networkx.Graph()
        G.add_edges_from(edges)
        Components = networkx.connected_components(G)
        for S in Components:
            S_card = len(S)
            q_sum = sum(q[i] for i in S)
            NS = int(math.ceil(float(q_sum)/Q))
            S_edges = [(i,j) for i in S for j in S if i<j and (i,j) in edges]
            if S_card >= 3 and (len(S_edges) >= S_card or NS > 1):
                model.cbLazy(quicksum(x[i,j] for i in S for j in S if j > i) <= S_card-NS)
                print ("adding cut for",S_edges)
        return


    model = Model("vrp")
    x = {}
    for i in V:
        for j in V:
            if j > i and i == V[0]:       # depot
                x[i,j] = model.addVar(ub=2, vtype="I", name="x(%s,%s)"%(i,j))
            elif j > i:
                x[i,j] = model.addVar(ub=1, vtype="I", name="x(%s,%s)"%(i,j))
    model.update()

    model.addConstr(quicksum(x[V[0],j] for j in V[1:]) == 2*m, "DegreeDepot")
    for i in V[1:]:
        model.addConstr(quicksum(x[j,i] for j in V if j < i) +
                        quicksum(x[i,j] for j in V if j > i) == 2, "Degree(%s)"%i)

    model.setObjective(quicksum(c[i,j]*x[i,j] for i in V for j in V if j>i), GRB.MINIMIZE)

    model.update()
    model.__data = x
    return model,vrp_callback

def vrp_disrupt(V,c,m,q,Q,vlu,disrpt):
    def vrp_callback(model,where):

        # remember to set     model.params.DualReductions = 0     before using!
        # remember to set     model.params.LazyConstraints = 1     before using!
        if where != GRB.callback.MIPSOL:
            return
        edges = []
        for (i,j) in x:
            if model.cbGetSolution(x[i,j]) > .5:
                if i != V[0] and j != V[0]:
                    edges.append( (i,j) )
        G = networkx.Graph()
        G.add_edges_from(edges)
        Components = networkx.connected_components(G)
        for S in Components:
            S_card = len(S)
            q_sum = sum(q[i] for i in S)
            NS = int(math.ceil(float(q_sum)/Q))
            S_edges = [(i,j) for i in S for j in S if i<j and (i,j) in edges]
            if S_card >= 3 and (len(S_edges) >= S_card or NS > 1):
                model.cbLazy(quicksum(x[i,j] for i in S for j in S if j > i) <= S_card-NS)
                print ("adding cut for",S_edges)
        return


    model = Model("vrp")
    x = {}
    for i in V:
        for j in V:
            if j > i and i == V[0]:       # depot
                x[i,j] = model.addVar(ub=2, vtype="I", name="x(%s,%s)"%(i,j))
            elif j > i:
                x[i,j] = model.addVar(ub=1, vtype="I", name="x(%s,%s)"%(i,j))
    model.update()

    model.addConstr(quicksum(x[V[0],j] for j in V[1:]) == 2*m, "DegreeDepot")
    for i in V[1:]:
        model.addConstr(quicksum(x[j,i] for j in V if j < i) +
                        quicksum(x[i,j] for j in V if j > i) == 2, "Degree(%s)"%i)

    model.setObjective(quicksum((disrpt + c[i,j])*x[i,j] for i in V for j in V if j>i), GRB.MINIMIZE)

    model.update()
    model.__data = x
    return model,vrp_callback

def distance(x1,y1,x2,y2):
    """distance: euclidean distance between (x1,y1) and (x2,y2)"""
    return math.sqrt((x2-x1)**2 + (y2-y1)**2)

def make_data(n):
    """make_data: compute matrix distance based on euclidean distance"""
    V = range(1,n+1)
    x = dict([(i,random.random()) for i in V])
    y = dict([(i,random.random()) for i in V])
    c,q,vlu = {},{}
    Q = 200
    for i in V:
     #   q[i] = random.randint(10,20)
       # Valuee[i] = random.randint(20,30)
        for j in V:
            if j > i:
                c[i,j] = distance(x[i],y[i],x[j],y[j])
                
    return V,c,q,Q,vlu

def read_data():
    import xlrd
    file_loc=".\\dist.xlsx"
    wkb=xlrd.open_workbook(file_loc)
    dat_mat = []
    nrow = 0
    for sht in range(3): #Three sheets: 0:c[i,j] 1:q[j], 2:vlu[j]
        sheet=wkb.sheet_by_index(sht)
        _matrix=[]
        nrow = 0
        for row in range (sheet.nrows):
            _row = []
            nrow += 1
            for col in range (sheet.ncols):
                _row.append(sheet.cell_value(row,col))
            _matrix.append(_row)    
        dat_mat.append(_matrix)
    
    V = range(1,nrow+1)
    c,q,vlu = {},{},{}
    Q = 500
   # q = {}
    for i in V:
        q[i] = dat_mat[1][i-1][0]
        vlu[i] = dat_mat[2][i-1][0]
        for j in V:
            if j > i:
                c[i,j] = dat_mat[0][i-1][j-1]
          
    return V,c,q,Q,vlu

            
if __name__ == "__main__":
    import sys

    #n = 20
    m = 3
    seed = 1
    random.seed(seed)
    #V,c,q,Q = make_data(n)
    V,c,q,Q,vlu = read_data()
    
    opt_cost = 0
    for scen in range(1000):
        random.seed(scen)
        disrpt = random.uniform(0,10)
        model,vrp_callback = vrp_disrupt(V,c,m,q,Q,vlu,disrpt)
    
        # model.Params.OutputFlag = 0 # silent mode
        # 0 : min value
        model.params.DualReductions = 0 
        model.params.LazyConstraints = 1  
        #1: Implies Gurobi algorithms to avoid certain reductions and transformations
        #that are incompatible with lazy constraints.
        model.optimize(vrp_callback)
        x = model.__data
        
        edges = []
        tour = ''
        for i in V:
            if i > V[0] and x[V[0],i].X > .5:
                cond = True
                for t in edges:
                    if str(i) in t:
                        cond = False
                        break
                if cond == True:
                    tour = str(V[0]) + ' - ' + str(i)
                    fi = V[0]
                    fj = i
                    nextn = i   
                    point = [str(V[0]) + ',' + str(i)]
                    condit = True
                    prevnext = nextn 
                    for v in V:
                        if nextn == V[0]:
                            break;
                        for (ii,jj) in x:
                            e = str(ii) + ',' + str(jj)
                            if e not in point and x[ii,jj].X > .5:
                                if str(nextn) == str(ii):
                                    point.append(str(ii) + ',' + str(jj))
                                    tour += ' - ' + str(jj)
                                    nextn = jj
                                elif str(nextn) == str(jj):
                                    point.append(str(ii) + ',' + str(jj))
                                    tour += ' - ' + str(ii)
                                    nextn = ii
                                if nextn == V[0]:
                                    edges.append(tour)
                                    break;
    
                    
        opt_cost += model.ObjVal
        print ("Optimal solution:",model.ObjVal)
        print ("Edges in the solution:")
        print (sorted(edges))
    print ("Optimal solution of 1000 scenarios:",opt_cost/1000)
