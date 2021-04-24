from src.tools.interface import Interface
from src.db import query_db
from cliui.file_browser import BrowserContext
import sys
import json

class Error(Exception):
    pass

class RecordSelected(Error):
    pass

class Checker(Interface):
    def __init__(self):
        Interface.__init__(self)
        self.title = 'RESULT CHECKER'
        self.input_prompt = 'Search'
        self.info_prompt = 'Search parm'
        self.parm = None
        self.value = None
        

    def draw_main(self):
        records = query_db(parm=self.parm, value=self.value)
        
        self.records_list = []

        number = 0
        sys.stdout.write('{:<10}{:<10}{:<10}{}\n'.format('number', 'id', 'user_id', 'project'))
        if records:
            for record in records:
                self.records_list.append((number, record['user_id'], record['project'], record['_id']))
                sys.stdout.write('{:<10}{:<10}{:<10}{}\n'.format(*self.records_list[number]))
                number += 1

    def user_input_handler(self):
        user_input = self._message_box.popleft()

        if user_input == ':u':
            self.parm = 'user_id'
            self.info = self.parm
            self.value = None
        
        elif user_input == ':p':
            self.parm = 'project'
            self.info = self.parm
            self.value = None

        else:

            try:
                assert type(int(user_input)) == int
                self.selected_record = [i for i in query_db(parm='_id', value=self.records_list[int(user_input)][3])]
                raise RecordSelected
            except RecordSelected:
                raise
            except:
                self.value = user_input
    

class Context(object):
    def __init__(self):
        self.checker = Checker()        

    def run(self):
        while True:
            try:
                self.checker.draw()
                self.checker.user_input_handler()
            except RecordSelected: 
                f = BrowserContext()
                p = f.run()
                with open(p+'test.json', 'w') as j:
                    self.checker.selected_record[0].pop('_id')
                    json.dump(self.checker.selected_record[0], j)

                print(self.checker.selected_record)
                break


def main():
    context = Context()
    context.run()

if __name__ == '__main__':
    main()
    
