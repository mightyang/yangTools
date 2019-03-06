#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File              : ytLogging.py
# Author            : yang <mightyang@hotmail.com>
# Date              : 04.03.2019
# Last Modified Date: 06.03.2019
# Last Modified By  : yang <mightyang@hotmail.com>


import os
import re
import time
import threading
import sys


class yLogging():
    DEBUG = 0
    INFO = 1
    WARNING = 2
    ERROR = 3

    def __init__(self):
        self.__level = self.DEBUG
        self.__activeLevel = self.__level
        self.__levelStr = ['DEBUG', 'INFO', 'WARNING', 'ERROR']
        self.__results = []
        self.setFormat('%(asctime)s %(funcName)s[%(lineno)d] %(levelname)s: %(message)s')
        self.__file = open(os.path.join(os.path.expanduser('~'), 'yt.log'), 'w')
        self.__handler = None

    def setFormat(self, yFormat):
        '''
        %(levelno)s: the number of log level
        %(levelname)s: the name of log level
        %(pathname)s: sys.argv[0]
        %(filename)s: file name
        %(funcName)s: function name of current running
        %(lineno)d: current line of log
        %(asctime)s: time of log
        %(thread)d: thread id
        %(threadname)s: thread name
        %(process)d: process id
        %(message)s: log message
        '''
        pattern = re.compile(
            r'(.*?)(%\(levelno\)s|%\(levelname\)s|%\(pathname\)s|%\(filename\)s|%\(funcName\)s|%\(lineno\)d|%\(acstime\)s|%\(thread\)d|%\(threadname\)s|%\(process\)d|%\(message\)s)(.*?)'
        )
        self.__results = [j for i in pattern.findall(yFormat) for j in i if j]

    def replaceTag(self, tag, info):
        if tag == '%(levelno)s':
            return self.__activeLevel
        elif tag == '%(levelname)s':
            return self.__levelStr[self.__activeLevel]
        elif tag == '%(pathname)s':
            return sys._getframe().f_code.co_filename
        elif tag == '%(filename)s':
            return os.path.basename(sys._getframe().f_code.co_filename)
        elif tag == '%(funcName)s':
            return sys._getframe().f_back.f_back.f_code.co_name
        elif tag == '%(lineno)d':
            return str(sys._getframe().f_back.f_back.f_lineno)
        elif tag == '%(asctime)s':
            return time.asctime()
        elif tag == '%(thread)d':
            return str(threading.currentThread().ident)
        elif tag == '%(threadname)s':
            return threading.currentThread().name
        elif tag == '%(process)d':
            return str(os.getpid())
        elif tag == '%(message)s':
            return info
        else:
            return tag

    def setLevel(self, level):
        if isinstance(level, int) and level >= 0 and level <= 3:
            self.level = level
        else:
            print 'log level must be DEBUG, INFO, WARNING, ERROR.'

    def debug(self, info):
        if self.__level <= self.DEBUG:
            self.__activeLevel = self.DEBUG
            self.__write("".join([self.replaceTag(r, info) for r in self.__results]))

    def info(self, info):
        if self.__level <= self.INFO:
            self.__activeLevel = self.INFO
            self.__write("".join([self.replaceTag(r, info) for r in self.__results]))

    def warning(self, info):
        if self.__level <= self.WARNING:
            self.__activeLevel = self.WARNING
            self.__write("".join([self.replaceTag(r, info) for r in self.__results]))

    def error(self, info):
        if self.__level <= self.ERROR:
            self.__activeLevel = self.ERROR
            self.__write("".join([self.replaceTag(r, info) for r in self.__results]))

    def setHandler(self, handler):
        self.__handler = handler

    def __write(self, msg):
        self.__handler.write(msg + '\n')


yl = yLogging()
yl.setHandler(sys.stdout)
