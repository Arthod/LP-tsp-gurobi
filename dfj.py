import gurobipy as gp
from gurobipy import GRB
import networkx as nx

from tsputil import distance, Cities, plot_situation

def solve_rtsplp(points, subtours=[], silent=True):
    points=list(points)
    V = range(len(points))
    E = gp.tuplelist([(i, j) for i in V for j in V if i<j]) # complete graph

    m = gp.Model("RTSPLP")
    if silent:
        m.setParam(GRB.Param.OutputFlag, 0)
    ######### BEGIN: Write here your model for Task 1
    ## Vars
    x = m.addVars(E, vtype=GRB.CONTINUOUS)
    
    ## Objective
    m.setObjective(gp.quicksum([distance(points[i], points[j]) * x[i, j] for i, j in E.select("*", "*")]), GRB.MINIMIZE)
    
    ## Constraints
    for i in V:
        m.addConstr(
            gp.quicksum([x[i, j] for _, j in E.select(i, "*") if j != i]) + gp.quicksum([x[j, i] for j, _ in E.select("*", i) if j != i]) == 2)

    
    for subtour in subtours:
        m.addConstr(gp.quicksum([x[i, j] for i in subtour for j in subtour if i < j]) <= len(subtour) - 1)
    m.optimize()

    ######### END
    
    m.display()
    
    if m.status == GRB.status.OPTIMAL:
        print('The optimal objective is %g' % m.objVal)
        result = {e: x[e].X for e in E}
        return result
    else:
        print("Something wrong in solve_tsp")
        raise SystemExit

def solve_separation(points, x_optimal, k):
    G = nx.Graph()

    G.add_nodes_from(range(len(points)))
    for e, cap in x_optimal.items():
        G.add_edge(*e, capacity=cap)

    val, partition = nx.minimum_cut(G, 0, k)
    #print(val, partition)
    if (val < 2):
        return list(partition[1])
    return None
        
"""
def solve_separation(points, x_optimal, k, silent=True):
    points = list(points)
    V = list(range(len(points)))
    Vprime = list(range(1, len(points)))
    E = [(i, j) for i in V for j in V if i < j]
    Eprime = [(i, j) for i in Vprime for j in Vprime if i < j]

    m = m.Model("SEP")
    if silent:
        m.setParam(GRB.Param.OutputFlag, 0)
    # BEGIN: Write here your model for Task 5
    m.
   
    
    # END
    m.optimize()
    
    if m.status == GRB.status.OPTIMAL:
        print('Separation problem solved for k=%d, solution value %g' % (k, m.objVal))
        # BEGIN: Write here the subtour found from the solution of the model
        # it must be a list of points
        subtour = []
        subtour = list(filter(lambda i: z[i].X >= 0.99, Vprime))
        # END
        return m.value(), subtour
    else:
        print("Something wrong in solve_separation")
        raise SystemExit
"""

if __name__ == "__main__":
    
    points = Cities(n=100, seed=35)
    E = gp.tuplelist([(i, j) for i in range(len(points)) for j in range(len(points)) if i<j]) # complete graph
    subtours = []

    #points = read_instance("data/bier127.dat")

    x = solve_rtsplp(points, subtours)
    for _  in range(10):
        #plot_situation(points, x)
        for k in range(1, len(points)):
            subtours_new = solve_separation(points, x, k)
            if (subtours_new is not None):
                subtours.append(subtours_new)

        
        x = solve_rtsplp(points, subtours)

    #solve_separation(points, x, 10)
    plot_situation(points, x)