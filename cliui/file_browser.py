import os
from collections import deque, namedtuple
import sys

config_command = namedtuple('config_command', 'item value')

class FileError(Exception):
    pass

class BrowserExit(FileError):
    pass

class FilesSelected(FileError):
    pass

class PathSelected(FileError):
    pass

# TODO 太多重复代码，是否有方案优化
class BaseMode(object):

    def __init__(self, path, config):
        self.title = ''
        self.input_prompt = ''
        self.error_information = ''
        self.info_prompt = ''
        self.info = ''

        self.path_head = path
        self.config = config

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
        self.paths_in_dir = os.listdir(self.path_head)
        if self.config['hide']:
            self.paths_in_dir = [path for path in self.paths_in_dir if not path.startswith('.')]

        if self.config['number']:
            line_number = 0
        else:
            line_number = ''
        
        sys.stdout.write('\n')

        for path in self.paths_in_dir:
            sys.stdout.write('{} {}\n'.format(line_number, path))
            if self.config['number']:
                line_number += 1

        sys.stdout.write('\n')

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


class NormalMode(BaseMode):

    def __init__(self, path, config):
        BaseMode.__init__(self, path, config)

        self.title = 'BROWSER'
        self.input_prompt = 'User command'
        self.info_prompt = 'Path'
        self.info = self.path_head
    
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
        
        elif user_input in command_dict.keys():
            command = command_dict[user_input]
            self.config[command.item] = command.value

        else:
            self.error_information = '[Error: Not a command.]'
        
        return self


class PathMode(BaseMode):

    def __init__(self, path, config):
        BaseMode.__init__(self, path, config)

        self.title = 'BROWSER'
        self.input_prompt = 'Path to jump'
        self.info_prompt = 'Path'
        self.info = self.path_head

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
            raise PathSelected

        elif user_input == '..':
            self.error_information = ''
            temp = self.path_head.split('/')
            temp.pop(-2)  # 删掉当前目录名
            self.path_head = '/'.join(temp)
            self.info = self.path_head
        

        elif os.path.isdir(self.path_head + user_input):
            self.error_information = ''
            self.path_head += user_input
            if not user_input.endswith('/'):  
                self.path_head += '/'

            self.info = self.path_head

        elif user_input.startswith(':'):
            self.error_information = '[Error: invalid command.]'

        else:
            try:
                assert os.path.isdir(self.path_head + self.paths_in_dir[int(user_input)] + '/')
                self.error_information = ''
                self.path_head += self.paths_in_dir[int(user_input)] + '/'
                self.info = self.path_head

            except:    
                self.error_information = '[Error: input is not a dir.]'

        return self


class FileMode(BaseMode):

    def __init__(self, path, config):
        BaseMode.__init__(self, path, config)

        self.title = 'BROWSER'
        self.input_prompt = 'File to select'
        self.info_prompt = 'File selected'   

        self.files_to_process = []
        self.info = len(self.files_to_process)

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
            if self.files_to_process:
                raise FilesSelected
            else:
                self.error_information = '[Error: No file selected.]'

        elif os.path.isfile(self.path_head + user_input):
            self.error_information = ''
            self.files_to_process.append(self.path_head + user_input)

        else:
            try:  
                assert os.path.isfile(self.path_head + self.paths_in_dir[int(user_input)])  # 按序号添加文件
                self.error_information = ''
                self.files_to_process.append(self.path_head + self.paths_in_dir[int(user_input)])
                self.info = len(self.files_to_process)
            except:
                try:  # 可以通过1-10这种形式批量选择文件，但需保证所有均为文件才可选中
                    boundaries = user_input.split('-')
                    for file_no in range(int(boundaries[0]), int(boundaries[1])+1):
                        assert os.path.isfile(self.path_head + self.paths_in_dir[file_no])
                        self.files_to_process.append(self.path_head + self.paths_in_dir[file_no])

                    self.error_information = ''
                    self.info = len(self.files_to_process)

                except:
                    self.error_information = '[Error: input is not a file.]'

        return self
            

class BrowserContext(object):

    def __init__(self, init_state=PathMode):
        path = os.getcwd() + '/'
        config = {
            'number': 1,  # 显示行号
            'hide': 1  # 显示隐藏文件
        }
        self._state = init_state(path, config)

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
            except PathSelected:
                print('Path selected successfully.')
                return self._state.path_head

            else:
                pass


def main():
    test_fileexplorer = BrowserContext()
    files_to_process = test_fileexplorer.run()
    print(files_to_process)
           
if __name__ == '__main__':
    main()
    