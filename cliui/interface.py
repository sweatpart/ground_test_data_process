import os
from collections import deque, namedtuple
import sys

class Interface(object):

    def __init__(self):
        self.title = ''
        self.input_prompt = ''
        self.error_information = ''
        self.info_prompt = ''
        self.info = ''

        self._message_box = deque()

    def __repr__(self):
        return type(self).__name__
    
    def draw_title(self):
        sys.stdout.write('{}\n'.format(self.title))
        sys.stdout.write('-'*50 + '\n')

    def draw_toolbar(self):
        sys.stdout.write('{}  {}  {}  {}\n'.format('PathMode(:p)', 'FileMode(:f)', 'NormalMode(:n)', 'Quit(:q)'))

    def draw_info(self):
        sys.stdout.write('{}: {}\n'.format(self.info_prompt, self.info))

    def draw_main(self):
        pass

    def draw_status(self):
        sys.stdout.write('State: {}\n'.format(self))
    
    def draw_input(self):
        user_input = input('{}{}: '.format(self.error_information, self.input_prompt))
        self._message_box.append(user_input)

    def draw(self):
        os.system('clear')

        self.draw_title()
        self.draw_toolbar()
        self.draw_info()
        self.draw_main()
        self.draw_status()
        self.draw_input()
        sys.stdout.flush()