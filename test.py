from src.solvers import RainflowSolver
import json

def main():
    path = ['/root/ground_test_data_process/tests/1.csv']
    rf = RainflowSolver()
    result = rf.solver_method(path)
    print(result)
    with open('/root/ground_test_data_process/tests/test.json', 'w') as j:
        json.dump(result, j)

if __name__ == '__main__':
    main() 