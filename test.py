from src.solvers import RainflowSolver
import json
import csv

def main():
    path = ['/Users/sunlei/Documents/GitHub/ground_test_data_process/tests/testinput.csv']
    rf = RainflowSolver()
    result = rf.solver_method(path)
    print(result)
    with open('/Users/sunlei/Documents/GitHub/ground_test_data_process/tests/test.json', 'w') as j:
        json.dump(result, j)

def tocsv():
    with open('/Users/sunlei/Documents/GitHub/ground_test_data_process/tests/abs/6.json', 'r') as j:
        data = json.load(j)
        with open('/Users/sunlei/Documents/GitHub/ground_test_data_process/tests/abs/6.csv', 'w', newline='') as csvfile:
            fieldnames = ['torque'] + [str(angal) + '.0' for angal in range(0,27)]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for torque, count in data:
                count['torque'] = str(torque)
                writer.writerow(count) 

if __name__ == '__main__':
    main()