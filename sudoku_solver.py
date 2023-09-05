import pandas as pd
import pyomo.environ as pyo

def sudoku_model(board):

    model = pyo.ConcreteModel()

    # store the starting board
    # board = pd.read_excel('./sudoku_input_0.xlsx', header=None)
    board.index += 1
    board.columns += 1
    display(board)

    # create sets for rows, columns and subsquares
    model.ROWS = pyo.Set(initialize=board.index)
    model.COLS = pyo.Set(initialize=board.columns)
    model.VALUES = pyo.Set(initialize=pyo.RangeSet(1, 9))
    
    model.U = pyo.Set(initialize=[0, 3, 6])
    model.W = pyo.Set(initialize=[0, 3, 6])

    # create the binary variables
    model.y = pyo.Var(model.ROWS, model.COLS, model.VALUES, within=pyo.Binary)

    # fix variables based on the current board
    for r in model.ROWS:
        for c in model.COLS:
            if board.loc[r, c] in model.VALUES:
                model.y[r, c, board.loc[r, c]].fix(1)

    # exactly one number in each row
    def _row_cstr(model, c, v):
        return sum(model.y[:, c, v]) == 1
    
    model.row_cstr = pyo.Constraint(model.COLS, model.VALUES, rule=_row_cstr)

    # exactly one number in each column
    def _col_cstr(model, r, v):
        return sum(model.y[r, :, v]) == 1

    model.col_cstr = pyo.Constraint(model.ROWS, model.VALUES, rule=_col_cstr)

    # exactly one number in each subsquare
    def _subsquares_cstr(model, u, w, v):
        return sum(model.y[r+u, c+w, v] for r in range(1, 4) for c in range(1, 4)) == 1

    model.subsquares_cstr = pyo.Constraint(model.U, model.W, model.VALUES, rule=_subsquares_cstr)

    # exactly one number in each cell
    def _value_cstr(model, r, c):
        return sum(model.y[r, c, :]) == 1

    model.value_cstr = pyo.Constraint(model.ROWS, model.COLS, rule=_value_cstr)

    # objective function - feasibility problem so we just make it a constant
    model.obj = pyo.Objective(expr=1.0)


# adding a new integer cur to the model
def add_integer_cut(model):
    # add the ConstraintList to store the IntegerCuts if it does not already exist
    if not hasattr(model, 'IntegerCuts'):
        model.IntegerCuts = pyo.ConstraintList()

    # add the integer cut corresponding to the current solution in the model
    cut_expr = 0.0
    for r in model.ROWS:
        for c in model.COLS:
            for v in model.VALUES:
                if not model.y[r, c, v].fixed:
                    if pyo.value(model.y[r, c, v]) >= 0.5:
                        cut_expr += (1.0 - model.y[r, c, v])
                    else:
                        cut_expr += model.y[r, c, v]
    model.IntegerCuts.add(cut_expr >= 1)


# prints the solution stored in the model
def print_solution(model):
    for r in model.ROWS:
        print(' '.join(str(v) for c in model.COLS
                       for v in model.VALUES
                       if pyo.value(model.y[r, c, v]) >= 0.5))