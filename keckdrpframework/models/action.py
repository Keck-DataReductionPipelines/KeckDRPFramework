'''
Created on Jul 8, 2019

@author: skwok
'''

class Action(object):
    '''
    classdocs
    '''


    def __init__(self, event_info, args):
        '''
        Constructor
        '''
        self.name, self.next_state, self.new_event = event_info
        self.args = args
        self.output = None       
        
        
    def __str__ (self):
        return f"{self.name}, {self.args}, {self.next_state}, {self.new_event}"
        
