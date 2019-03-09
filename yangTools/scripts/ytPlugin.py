#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File              : ytPlugin.py
# Author            : yang <mightyang@hotmail.com>
# Date              : 04.03.2019
# Last Modified Date: 08.03.2019
# Last Modified By  : yang <mightyang@hotmail.com>

import abc
from ytLoggingSettings import yl
import ytVersion


class ytIcon():
    icon = {}

    def __init__(self, icon=None):
        self.icon['normal'] = icon

    def getIcon(self, status='normal'):
        if status in self.icon:
            return self.icon[status]
        return self.icon['normal']

    def setIcon(self, icon, status='normal'):
        self.icon[status] = icon


class ytPlugin:
    __metaclass__ = abc.ABCMeta
    name = 'ytPlugin'
    version = ytVersion.ytVersion()
    icon = ytIcon()

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


class ytRegeditPlugin(object):
    def __new__(cls, plugin):
        if isinstance(plugin, ytPlugin):
            return object.__new__(cls, plugin)
        else:
            yl.error('TypeError: plugin need ytPlugin, but: %s' % str(type(plugin)))

    def __init__(self, plugin):
        self.plugin = plugin

    def start(self):
        self.startCallback()
        self.plugin.ytStart()

    def stop(self):
        self.stopCallback()
        self.plugin.ytStop()

    def startCallback(self):
        pass

    def stopCallback(self):
        pass

    def addStartCallback(self, func):
        pass

    def addStopCallback(self, func):
        pass
