import os
import sys
from collections import deque

from src.solvers import SOLVERS

class SelectorError(Exception):
    pass

class SelectorExit(SelectorError):
    pass

class SoverSelected(SelectorError):
    pass

class Selector(object):

    def __init__(self):
        self._message_box = deque()
        self.selected_solver = ''
        self.error_information = ''
        self.input_prompt = 'Select solver No. '
        number = 1
        self.solver_dict = dict()
        for solver_name in SOLVERS.keys(): 
            self.solver_dict[str(number)] = solver_name 
            number += 1

    def __repr__(self):
        return type(self).__name__
    
    def draw_title(self):
        print('SOVER SELECTOR')
        print('-'*30)

    def draw_status(self):
        if self.selected_solver:
            status = self.selected_solver.__name__
        else:
            status = self.selected_solver
        print('Selected solver: {}\n'.format(status))

    def draw_main(self):
        for number, solver_name in self.solver_dict.items():
            sys.stdout.write('{}. {}\n'.format(number, solver_name))
        sys.stdout.write('\n')
        sys.stdout.flush()

    def draw_input(self):
        user_input = input('{}{}: '.format(self.error_information, self.input_prompt))
        self._message_box.append(user_input)

    def draw(self):
        os.system('clear')

        self.draw_title()
        self.draw_status()
        self.draw_main()
        self.draw_input()
    
    def user_input_handler(self):
        user_input = self._message_box.popleft()

        if user_input == ':q':
            raise SelectorExit
        elif user_input == ':s':
            if self.selected_solver:
                raise SoverSelected
            else:
                self.error_information = '[Error: No solver selected.]'
        elif user_input in self.solver_dict.keys():
            self.error_information = ''
            self.selected_solver = SOLVERS[self.solver_dict[user_input]][0]  # 直接返回solver类
        else:
            self.error_information = '[Error: not valid ]'
        
        return self.selected_solver


class SelectorContext(object):
    def __init__(self):
        self.selector = Selector()
    
    def run(self):
        while True:
            try:
                self.selector.draw()
                selected_solver = self.selector.user_input_handler()
            except SelectorExit:
                print('Selector close successfully.\n')
                return True
            except SoverSelected:
                return selected_solver

def main():
    test_selector = SelectorContext()
    selected_solver = test_selector.run()
    print(selected_solver)

if __name__ == '__main__':
    main()
