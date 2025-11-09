from Inputbuilder.inputbuilder import InputBuilder
from Solver.solver import Solver

def main():
    print("Starting the Stage 1 optimization process...")
    start time = time.time()
    # Build input data
    input_builder = InputBuilder()
    input_builder.build()

    # Initialize and run the solver
    solver = Solver(input_builder)
    solver.solve()

    print("Stage 1 completed."+ str(time.time() - start_time) + "seconds")

if __name__ == "__main__":
    main()