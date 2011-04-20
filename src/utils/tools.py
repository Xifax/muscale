# -*- coding: utf-8 -*-
__author__ = 'Geoffrey Foster, Yadavito'

# internal #
from threading import Event, Thread
import collections

# own #
from utils.const import LR_PRNTH_MAPPINGS, L_PRNTH, R_PRNTH

class RepeatTimer(Thread):
    def __init__(self, interval, function, iterations=0, args=[], kwargs={}):
        Thread.__init__(self)
        self.interval = interval
        self.function = function
        self.iterations = iterations
        self.args = args
        self.kwargs = kwargs
        self.finished = Event()

    def run(self):
        count = 0
        while not self.finished.is_set() and (self.iterations <= 0 or count < self.iterations):
            self.finished.wait(self.interval)
            if not self.finished.is_set():
                self.function(*self.args, **self.kwargs)
                count += 1

    def cancel(self):
        self.finished.set()

def checkParentheses(string):
    '''Check that all parentheses in a string come in matched nested pairs.'''
    parenstack = collections.deque()
    for ch in string:
        if ch in L_PRNTH:
            parenstack.append(ch)
        elif ch in R_PRNTH:
            try:
                if LR_PRNTH_MAPPINGS[parenstack.pop()] != ch:
                    return False
            except IndexError:
                return False
    return not parenstack