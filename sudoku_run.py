import pandas as pd
from pyomo.opt import SolverFactory, TerminationCondition
from sudoku_solver import sudoku_model, add_integer_cut, print_solution, solution_to_dataframe

# import the board
board = pd.read_excel('./input/sudoku_input.xlsx', header=None)

model = sudoku_model(board)

solution_count = 0
while 1:
    with SolverFactory("glpk") as opt:
        results = opt.solve(model)
        if results.solver.termination_condition != TerminationCondition.optimal:
            print("All board solutions have been found")
            break

    solution_count += 1

    add_integer_cut(model)

    print("Solution #%d" % (solution_count))
    print_solution(model)

    solution_to_dataframe(model)
    
with pd.ExcelWriter('./sudoku_output.xlsx') as file:
    for key, df in solution_df.items():
        df.to_excel(file, sheet_name=key)