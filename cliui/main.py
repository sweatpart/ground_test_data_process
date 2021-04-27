from collections import deque
from queue import Queue
import os
import json

from src.processor import Processor
from cliui.file_browser import BrowserContext, NormalMode
from cliui.solver_selector import SelectorContext

def async_file_browser():
    _messgae = yield
    while True:
        fb = BrowserContext(NormalMode)
        files_to_process = fb.run()
        yield files_to_process

def async_solver_selector():
    _messgae = yield
    while True:
        ss = SelectorContext()
        selected_solver = ss.run()
        yield selected_solver

class MainContextError(Exception):
    pass


class MainContextExit(MainContextError):
    pass


class Command(object):
    
    def __init__(self, files, config, solver):
        self.comand_info = (files, config, solver)

    def sendto(self,load_balancer):
        load_balancer.send(self.comand_info)


class MainContext(object):

    def __init__(self, load_balancer):
        self._message_box = deque()
        self._command_list = deque()
        self.result_q = Queue()
        self.error_information = ''

        self.file_browser = async_file_browser()
        next(self.file_browser)
        self.solver_selector = async_solver_selector()
        next(self.solver_selector)
        
        self.load_balancer = load_balancer
    
    def draw_title(self):
        pass

    def draw_instructions(self):
        pass
    
    def draw_commands(self):
        pass
    
    def draw_status(self):
        if not self.result_q.empty():
            result = self.result_q.get()
            print(result)

    def draw_input(self):
        user_input = input('{}>> '.format(self.error_information))
        self._message_box.append(user_input)

    def draw(self):
        os.system('clear')
        self.draw_status()
        self.draw_input()

    def user_input_handler(self):
        user_input = self._message_box.popleft()

        if user_input == ':file':
            self.files_to_process = self.file_browser.send('file')

        elif user_input == ':config':
            with open(self.file_browser.send('config')[0]) as j:
                self.config = json.load(j)

        elif user_input == ':cancel':
            self.load_balancer.close()

        elif user_input == ':solver':
            self.solver = self.solver_selector.send('add')

        elif user_input == ':add':
            try:
                self._command_list.append(Command(self.files_to_process, self.config, self.solver))
            except:
                self.error_information = 'Invalid command.'
    
        elif user_input == ':start':
            if self._command_list:
                self.load_balancer.start(self.result_q)
                for command in self._command_list:
                    command.sendto(self.load_balancer)
    
        elif user_input == ':quit':
            raise MainContextExit

    def run(self):
        while True:
            try:
                self.draw()
                self.user_input_handler()
            except MainContextExit:
                print('MainContext close successfully.')
                break


def main():
    load_balancer = Processor()
    test_maincontext = MainContext(load_balancer)
    test_maincontext.run()

if __name__ == '__main__':
    main()
    
    
