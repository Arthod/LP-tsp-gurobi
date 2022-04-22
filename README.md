# LP Travelling Salesman Problem in Gurobi (with Python)

Implementation of several LP formulations to solve TSP in LP, the following formulations are implemented
- Dantzig, Fulkerson and Johnson (DFJ)
- Miller-Tucker-Zemlin (MTZ)
- Flow
- Dantzig Step

*DFJ is implemented to only include subtour constraints if they are not redundant.