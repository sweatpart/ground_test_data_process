import os
from collections import deque, namedtuple
import sys

config_command = namedtuple('config_command', 'item value')

class BrowserExit(Exception):
    pass

class FilesSelected(Exception):
    pass

class BaseMode():
    def __init__(self, path, config):
        self.path_head = path
        self.config = config

        self._message_box = deque()
        self.error_information = ''
        self.files_to_process = []

    def __repr__(self):
        return type(self).__name__
    
    def draw_banner(self):
        sys.stdout.write('{}  {}  {}  {}\n'.format('PathMode(:p)', 'FileMode(:f)', 'NormalMode(:n)', 'Quit(:q)'))
        sys.stdout.flush()

    def draw_pwd(self):
        print('Path: {}\n'.format(self.path_head))

    def draw_main(self):
        paths_in_dir = os.listdir(self.path_head)
        if self.config['number']:
            line_number = 0
        else:
            line_number = ''
        for path in paths_in_dir:
            if self.config['hide']:
                if path.startswith('.'):
                    continue
            if self.config['number']:
                line_number += 1
            sys.stdout.write('{} {}\n'.format(line_number, path))
        sys.stdout.write('\n')
        sys.stdout.flush()

    def draw_state(self):
        print('State: {}'.format(self))
    
    def draw_input(self):
        pass

    def draw(self):
        os.system('clear')

        self.draw_banner()
        self.draw_pwd()
        self.draw_main()
        self.draw_state()
        self.draw_input()

class NormalMode(BaseMode):
    def draw_input(self):
        user_input = input('{}User command: '.format(self.error_information))
        self._message_box.append(user_input)
    
    def user_input_handler(self):
        user_input = self._message_box.popleft()
        command_dict = {
            ':numberon': config_command('number', 1),
            ':numberoff': config_command('number', 0),
            ':hideon': config_command('hide', 1),
            ':hideoff': config_command('hide', 0)
        }
        if user_input == ':p':
            return PathMode(self.path_head, self.config)

        elif user_input == ':f':
            return FileMode(self.path_head, self.config)

        elif user_input == ':n':
            return NormalMode(self.path_head, self.config)

        elif user_input == ':q':
            raise BrowserExit

        elif user_input == ':s':
            raise FilesSelected
        
        elif user_input in command_dict.keys():
            command = command_dict[user_input]
            self.config[command.item] = command.value

        else:
            self.error_information = '[Error: Not a command.]'
        
        return self

class PathMode(BaseMode):
    def draw_input(self):
        user_input = input('{}Path to jump: '.format(self.error_information))
        self._message_box.append(user_input)

    def user_input_handler(self):
        user_input = self._message_box.pop()
        if user_input == ':p':
            return PathMode(self.path_head, self.config)

        elif user_input == ':f':
            return FileMode(self.path_head, self.config)

        elif user_input == ':n':
            return NormalMode(self.path_head, self.config)

        elif user_input == ':q':
            raise BrowserExit

        elif user_input == ':s':
            raise FilesSelected

        elif user_input == '..':
            self.error_information = ''
            temp = self.path_head.split('/')
            for i in range(2): temp.pop()
            temp.append('')
            self.path_head = '/'.join(temp)

        elif os.path.isdir(self.path_head + user_input):
            self.error_information = ''
            self.path_head += user_input
            if user_input.endswith('/'): 
                pass
            else: 
                self.path_head += '/'

        else:
            self.error_information = '[Error: input is not a dir.]'

        return self

class FileMode(BaseMode):
    def draw_input(self):
        user_input = input('{}File to select: '.format(self.error_information))
        self._message_box.append(user_input)
    def user_input_handler(self):
        user_input = self._message_box.popleft()

        if user_input == ':p':
            return PathMode(self.path_head, self.config)

        elif user_input == ':f':
            return FileMode(self.path_head, self.config)

        elif user_input == ':n':
            return NormalMode(self.path_head, self.config)

        elif user_input == ':q':
            raise BrowserExit

        elif user_input == ':s':
            raise FilesSelected

        elif os.path.isfile(self.path_head + user_input):
            self.error_information = ''
            self.files_to_process.append(self.path_head + user_input)

        else:
            self.error_information = '[Error: input is not a file.]'

        return self
            


class Context():
    def __init__(self, state):
        path = '/Users/sunlei/'
        config = {
            'number': 1,
            'hide': 1
        }
        self._state = state(path, config)

    def get_state(self):
        pass

    def set_state(self, state):
        self._state = state
        
    def run(self):
        while True:
            try:
                self._state.draw()
                self.set_state(self._state.user_input_handler())
            except BrowserExit:
                print('File browser eixt successfully.')
                return True
            except FilesSelected:
                print('Files selected successfully.')
                return self._state.files_to_process
            else:
                pass
            
if __name__ == '__main__':
    test_fileexplorer = Context(PathMode)
    
    files_to_process = test_fileexplorer.run()
    print(files_to_process)