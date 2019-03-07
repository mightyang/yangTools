#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File              : srcytPlugin.py
# Author            : yang <mightyang@hotmail.com>
# Date              : 04.03.2019
# Last Modified Date: 07.03.2019
# Last Modified By  : yang <mightyang@hotmail.com>

import abc


class ytPlugin:
    __metaclass__ = abc.ABCMeta
    name = 'ytPlugin'
    version = ''
    iconRun = ''
    iconStop = ''

    def __init__(self):
        super().__init__()

    def start(self, *args, **kwargs):
        self.startCallback()
        self.ytStart()

    def stop(self, *args, **kwargs):
        self.stopCallback()
        self.stop()

    @abc.abstractmethod
    def ytStart(self):
        pass

    @abc.abstractmethod
    def ytStop(self):
        pass

    def setRunningIcon(self, icon):
        self.iconRun = icon

    def setStoppedIcon(self, icon):
        self.iconStop = icon

    def getRunningIcon(self):
        return self.iconRun

    def getStoppedIcon(self):
        return self.iconStop

    def startCallback(self, *args, **kwargs):
        pass

    def stoppCallback(self, *args, **kwargs):
        pass
