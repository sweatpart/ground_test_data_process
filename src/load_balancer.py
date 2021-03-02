# 用于调度processor


from collections import deque

# pylint: disable=wrong-import-position
from src.roadmap_processor import Processor
# pylint: enable=wrong-import-position

class LoadBalancer(object):

    def __init__(self):
        self._command_list = deque()

    def send(self, command):
        self._command_list.append(command)

    def resign(self, command, processor):
        processor.send(command)

    def run(self):
        pass
    
