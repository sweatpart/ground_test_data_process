from collections import deque
from queue import Queue
import os

from src.roadmap_processor import Processor
from src.file_browser import Context, NormalMode

def async_file_browser():
    _ = yield
    while True:
        file_browser = Context(NormalMode)
        files_to_process = file_browser.run()
        yield files_to_process

class MainContext():
    def __init__(self):
        self._message_box = deque()
        self.result_q = Queue()
        self.error_information = ''
        self.file_browser = async_file_browser()
        next(self.file_browser)
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
            files_to_process = self.file_browser.send('add')
            self.processor.start(self.result_q)
            self.processor.send(files_to_process)
        elif user_input == ':cancel':
            self.processor.close()

    def run(self):
        while True:
            try:
                self.draw()
                self.user_input_handler()
            except:
                raise

if __name__ == '__main__':
    test_maincontext = MainContext()
    test_maincontext.run()
    
