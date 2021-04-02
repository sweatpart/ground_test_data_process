from src.solvers import RainflowSolver, DutyCycleSolver
import json
import csv

def rainflow():

    test_file = '/Users/sunlei/Documents/GitHub/ground_test_data_process/tests/testinput.csv'
    paths = [test_file]
    config = {
        'main_parm' : 'torque',
        'optional_parms' : ['speed', 'angal'],
        'ndigits' : 0
    }

    rf = RainflowSolver()
    result = rf.solver_method(paths=paths, config=config)
    print(result)
    
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

def dutycycle():
    test_file = '/Users/sunlei/Documents/GitHub/ground_test_data_process/tests/1.csv'
    paths = [test_file]
    config = {
        'main_parm' : 'Torque_RL[Nm]',
        'optional_parms' : ['WhlGndVelLDrvnHSC1[km/h]', 'JounceAngle_RL[deg]'],
        'tire_radius' : 0.3,
        'time_interval' : 0.05
    }

    dc = DutyCycleSolver()
    result = dc.solver_method(paths, config)
    print(result)

if __name__ == '__main__':
    rainflow()
    #dutycycle()