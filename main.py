from collections import deque
from queue import Queue
import os

from src.roadmap_processor import Processor
from src.file_browser import BrowserContext, NormalMode
from src.solver_selector import SelectorContext

def async_file_browser():
    _ = yield
    while True:
        fb = BrowserContext(NormalMode)
        files_to_process = fb.run()
        yield files_to_process

def async_solver_selector():
    _ = yield
    while True:
        ss = SelectorContext()
        selected_solver = ss.run()
        yield selected_solver

class MainContextError(Exception):
    pass


class MainContextExit(MainContextError):
    pass


class MainContext(object):

    def __init__(self):
        self._message_box = deque()
        self.result_q = Queue()
        self.error_information = ''

        self.file_browser = async_file_browser()
        next(self.file_browser)
        self.solver_selector = async_solver_selector()
        next(self.solver_selector)
        
        self.processor = Processor()
    
    def draw_title(self):
        pass

    def draw_instructions(self):
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
        if user_input == ':add':
            self.files_to_process = self.file_browser.send('add')
        elif user_input == ':cancel':
            self.processor.close()
        elif user_input == ':solver':
            self.solver = self.solver_selector.send('add')
        elif user_input == ':start':
            if self.files_to_process and self.solver:
                self.processor.start(self.result_q)
                self.processor.send((self.files_to_process, self.solver))
        elif user_input == ':quit':
            raise MainContextExit

    def run(self):
        while True:
            try:
                self.draw()
                self.user_input_handler()
            except MainContextExit:
                print('MainContext close successfully.')

def main():
    test_maincontext = MainContext()
    test_maincontext.run()

if __name__ == '__main__':
    main()
    
    
