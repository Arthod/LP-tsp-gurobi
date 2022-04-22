import gurobipy as gp
from gurobipy import GRB
from collections import OrderedDict

from tsputil import *
from itertools import chain, combinations


def powerset(iterable):
    "powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)"
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(len(s)+1))

def solve_tsp_mtz(points, vartype=GRB.BINARY, solver="glpk", silent=True):
    # https://math.stackexchange.com/questions/2798418/miller-tucker-zemlin-notation-to-make-tsp-relaxation
    points=list(points)
    V = range(len(points))
    E = gp.tuplelist([(i, j) for i in V for j in V if i != j]) # complete graph

    m = gp.Model("TSP0")
    if silent:
        m.setParam(GRB.Param.OutputFlag, 0)
    ######### BEGIN: Write here your model for Task 1
    ## Vars
    x = m.addVars(E, vtype=GRB.BINARY)  # 1 if we drive from city i to city j, else 0
    u = m.addVars(V, vtype=GRB.CONTINUOUS, lb=0) # Number of cities visited at city i
    
    ## Objective
    m.setObjective(gp.quicksum([distance(points[i], points[j]) * x[i, j] for i, j in E.select("*", "*")]), GRB.MINIMIZE)
    
    ## Constraints
    # Enter each city once
    for j in V:
        m.addConstr(gp.quicksum([x[i, j] for i, _ in E.select("*", j)]) == 1)

    for i in V:
        m.addConstr(gp.quicksum([x[i, j] for _, j in E.select(i, "*")]) == 1)
    
    
    # Subtour break
    n = len(V)
    for i, j in E.select("*", "*"):
        if (i != 0 and j != 0):
            m.addConstr(u[i] - u[j] + n * x[i, j] <= n - 1)
            #m.addConstr(u[j] >= u[i] + 1 - (n) * (1 - x[i, j]))
    m.addConstr(u[0] == 1)

    
    ######### END
    
    m.display()
    #m.write("tsplp.lp")
    m.optimize()
    
    if m.status == GRB.status.OPTIMAL:
        print('The optimal objective is %g' % m.objVal)
        result = {e: x[e].X for e in E}
        return result
    else:
        print("Something wrong in solve_tsp")
        raise SystemExit

def solve_tsp_dfj(points, vartype=GRB.BINARY, solver="glpk", silent=True):
    points=list(points)
    V = range(len(points))
    E = gp.tuplelist([(i, j) for i in V for j in V if i<j]) # complete graph

    #subtours = list(powerset(range(len(points))))
    #subtours = subtours[1:(len(subtours)-1)]

    m = gp.Model("TSP0")
    if silent:
        m.setParam(GRB.Param.OutputFlag, 0)
    ######### BEGIN: Write here your model for Task 1
    ## Vars
    x = m.addVars(E, vtype=vartype)
    
    ## Objective
    m.setObjective(gp.quicksum([distance(points[i], points[j]) * x[i, j] for i, j in E.select("*", "*")]), GRB.MINIMIZE)
    
    ## Constraints
    for i in V:
        m.addConstr(
            gp.quicksum([x[i, j] for _, j in E.select(i, "*") if j != i]) + gp.quicksum([x[j, i] for j, _ in E.select("*", i) if j != i]) == 2)

    
    m.optimize()
    subtour = []
    while True:
        subtour = find_subtour(x, E, len(V))
        
        if (len(subtour) == len(V)):
            break
        m.addConstr(gp.quicksum([x[i, j] for i in subtour for j in subtour if i < j]) <= len(subtour) - 1)
        m.optimize()

    #while (i_initial != i)

    # Find a random subtour


    #for S in subtours:
    #    if (2 <= len(S) <= len(points) - 1):
            #E_S = [(i, j) for i, j in E if i in S and j in S]
    #        m.addConstr(gp.quicksum([x[i, j] for i in S for j in S if i < j]) <= len(S) - 1)
    #S = [11,2,7]
    #m.addConstr(gp.quicksum([x[i, j] for i in S for j in S if i < j]) <= len(S) - 1)

    #S = [1,9,15,12,18]
    #m.addConstr(gp.quicksum([x[i, j] for i in S for j in S if i < j]) <= len(S) - 1)
    
    #S = [0,6,14,3,4,19,16,10,17,13,8,5]
    #m.addConstr(gp.quicksum([x[i, j] for i in S for j in S if i < j]) <= len(S) - 1)

    ######### END
    
    m.display()
    
    if m.status == GRB.status.OPTIMAL:
        print('The optimal objective is %g' % m.objVal)
        result = {e: x[e].X for e in E}
        return result
    else:
        print("Something wrong in solve_tsp")
        raise SystemExit

def find_subtour(x, E, amt):
    i_initial = random.randint(0, amt - 1)
    i = i_initial
    subtour = [i_initial]
    while (True):
        i_old = i
        for e in E.select(i, "*") + E.select("*", i):
            if (x[e].X == 1):
                if (e[0] in subtour and e[1] in subtour):
                    continue
                if (e[0] == i):
                    i = e[1]
                else:
                    i = e[0]
                break
        if i == i_old:
            break
            
        subtour.append(i)
    return subtour

def solve_tsp_flow(points, vartype=GRB.BINARY, solver="glpk", silent=True):
    points=list(points)
    V = range(len(points))
    E = gp.tuplelist([(i, j) for i in V for j in V if i != j]) # complete graph

    m = gp.Model("TSP0")
    if silent:
        m.setParam(GRB.Param.OutputFlag, 0)
    ######### BEGIN: Write here your model for Task 1
    ## Vars
    x = m.addVars(E, vtype=GRB.BINARY)
    y = m.addVars(E, vtype=GRB.CONTINUOUS, lb=0)
    flow = 0.01
    
    ## Objective
    m.setObjective(gp.quicksum([distance(points[i], points[j]) * x[i, j] for i, j in E.select("*", "*")]), GRB.MINIMIZE)
    
    ## Constraints
    # Arrive in each city
    for i in V:
        if (i != 0):
            m.addConstr(gp.quicksum([y[j, i] for i, j in E.select(i, "*")]) >= 1)

    for i in V:
        if (i != 0):
            m.addConstr(gp.quicksum([y[i, j] for i, j in E.select(i, "*")]) - gp.quicksum([y[j, i] for i, j in E.select(i, "*")]) == flow)

    n = len(V)
    m.addConstr(gp.quicksum([x[i, j] for i, j in E.select("*", "*")]) <= n)

    for i, j in E.select("*", "*"):
        m.addConstr(y[i, j] <= (1 + n * flow) * x[i, j])

    # Model tightener
    #for i in V:
     #   if (i != 0):
    #        m.addConstr(gp.quicksum([x[j, i] for i, j in E.select("*", "*")]) == 1)
    

    """
    for i in range(2, len(points)):
        m.addConstr(gp.quicksum([y[j, i] for _, j in E.select(i, "*")]) >= 1)

    # Flow with gain of f
    for i in range(1, len(points)):
        m.addConstr(gp.quicksum([y[i, j] for _, j in E.select(i, "*")]) - gp.quicksum([y[j, i] for j, _ in E.select("*", i)]) == flow)

    # Only n positive vars
    n = len(points) - 1
    m.addConstr(gp.quicksum([x[i, j] for i, j in E.select("*", "*")]) <= n)

    # Force the y_ij vars
    for i, j in E.select("*", "*"):
        m.addConstr(y[i, j] <= (1 + n * flow) * x[i, j])
    """

    
    ######### END
    
    m.display()
    #m.write("tsplp.lp")
    m.optimize()
    
    if m.status == GRB.status.OPTIMAL:
        print('The optimal objective is %g' % m.objVal)
        result = {}
        for i, j in E.select("*", "*"):

            if 0.9 <= x[i, j].X <= 1.1:

                result[i, j] = x[i, j].X
        return result
    else:
        print("Something wrong in solve_tsp")
        raise SystemExit


def solve_tsp_step(points, vartype=GRB.BINARY, solver="glpk", silent=True):
    points=list(points)
    V = range(len(points))
    E = gp.tuplelist([(i, j, t) for i in V for j in V for t in V if i != j]) # complete graph

    m = gp.Model("TSP0")
    if silent:
        m.setParam(GRB.Param.OutputFlag, 0)
    ######### BEGIN: Write here your model for Task 1
    ## Vars
    x = m.addVars(E, vtype=GRB.BINARY)
    
    ## Objective
    m.setObjective(gp.quicksum([distance(points[i], points[j]) * x[i, j, t] for i, j, t in E.select("*", "*", "*")]), GRB.MINIMIZE)
    
    ## Constraints
    for i in V:
        m.addConstr(gp.quicksum([x[i, j, t] for _, j, t in E.select(i, "*", "*")]) == 1)
        
    n = len(points) - 1
    for i in V:
        m.addConstr(
            gp.quicksum([x[j, i, n] for j in V if i != j]),
            GRB.EQUAL,
            gp.quicksum([x[i, t, 0] for t in V if i != t]))

    for t in V:
        for j in V:
            if (t <= n - 1):
                m.addConstr(
                    gp.quicksum([x[i, j, t] for i in V if i != j]),
                    GRB.EQUAL,
                    gp.quicksum([x[j, k, t + 1] for k in V if k != j])
                )

    """
    for j in V:
        for t in range(1, len(points)):
            m.addConstr(gp.quicksum([x[i, j, t] for i, _, _ in E.select("*", j, t)]) - gp.quicksum([x[j, k, t + 1] for _, k, _ in E.select(j, "*", t + 1)]) == 0)

    # Go to each city once
    for i in range(1, len(points)):
        m.addConstr(gp.quicksum([x[i, j, t] for _, j, t in E.select(i, "*", "*")]) == 1)
    """
    
    ######### END
    
    m.display()
    #m.write("tsplp.lp")
    m.optimize()

    if m.status == GRB.status.OPTIMAL:
        print('The optimal objective is %g' % m.objVal)
        result = {}
        for t in V:
            for i, j, _ in E.select("*", "*", t):

                if 0.9 <= x[i, j, t].X <= 1.1:

                    result[i, j] = x[i, j, t].X
        return result
    else:
        print("Something wrong in solve_tsp")
        raise SystemExit


def check(alg, points):
    t0 = time.time()
    x = alg(points)
    t1 = time.time()
    print(f"{t1 - t0} secs")
    plot_situation(points, x)

if __name__ == "__main__":

    # RANDOM
    #points = Cities(n=50,seed=25)
    #points = read_instance(f"data/dantzig42.dat")
    #print("MTZ")
    #check(solve_tsp_mtz, points)

    points = Cities(n=100, seed=25)
    #points = read_instance("data/bier127.dat")

    check(solve_tsp_dfj, points)
    #x = solve_tsp_dfj(points, silent=True, vartype=GRB.BINARY)
    #plot_situation(points, x)

    #print("FLOW")
    #check(solve_tsp_flow, points)
    #print("STEP")
    #check(solve_tsp_step, points)
    #print("DFJ")
    #check(solve_tsp_dfj, points)

    #plot_situation(ran_points)