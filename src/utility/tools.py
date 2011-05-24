# -*- coding: utf-8 -*-
__author__ = 'Geoffrey Foster, Yadavito'

# internal #
import os
from threading import Event, Thread
import collections

# own #
from utility.const import LR_PRNTH_MAPPINGS, L_PRNTH, R_PRNTH

# external #
from numpy import array_equal

class RepeatTimer(Thread):
    '''Timer with custom number of iterations'''
    def __init__(self, interval, function, iterations=0, args=None, kwargs=None):
        Thread.__init__(self)
        self.interval = interval
        self.function = function
        self.iterations = iterations
        if args is None:
            args = []
        self.args = args
        if kwargs is None:
            kwargs = {}
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

def clearFolderContents(path):
    for the_file in os.listdir(path):
        file_path = os.path.join(path, the_file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except Exception, e:
            pass

'''Name 'parser' for enum model objects'''
prettifyNames = lambda list: [item.replace('_', ' ') for item in list]

'''Dictionary reverse search'''
reverseSearch = lambda dic, value : [k for k, lst in dic.iteritems() if value in lst]

'''Select unique models'''
uniqueModels = lambda models : list(set(models))

def arrayIndex(list, array):
    index = 0
    size = len(list)
    while index != size and not array_equal(list[index], array):
        index += 1
    if index != size:
        return index
    else:
        return 0