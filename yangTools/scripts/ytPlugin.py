#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File              : ytPlugin.py
# Author            : yang <mightyang@hotmail.com>
# Date              : 04.03.2019
# Last Modified Date: 10.03.2019
# Last Modified By  : yang <mightyang@hotmail.com>

import abc
from ytLoggingSettings import yl
import ytVariables
import ytVersion


class ytIcon():
    icon = {}

    def __init__(self, icon=None):
        self.status = ytVariables.ytIcon.ytIcon_status_stopped
        self.icon[self.status] = icon

    def getIcon(self):
        if self.status in self.icon:
            return self.icon[self.status]
        return self.icon[ytVariables.ytIcon.ytIcon_status_stopped]

    def setIcon(self, icon, status):
        if status in ytVariables.ytIcon.__dict__:
            self.icon[status] = icon
        else:
            yl.error('TypeError: status need ytVariables.ytIcon.status')

    def setStatus(self, status):
        if status in ytVariables.ytIcon.__dict__:
            self.status = status
        else:
            yl.error('TypeError: status need ytVariables.ytIcon.status')


class ytPlugin:
    __metaclass__ = abc.ABCMeta
    name = 'ytPlugin'
    version = ytVersion.ytVersion()
    help = ''
    icon = ytIcon()

    @abc.abstractmethod
    def ytStart(self):
        pass

    @abc.abstractmethod
    def ytStop(self):
        pass

    @abc.abstractmethod
    def isRunning(self):
        pass

    def getName(self):
        return self.name

    def getTooltip(self):
        return self.help


class ytRegeditPlugin(object):
    def __new__(cls, plugin):
        if isinstance(plugin, ytPlugin):
            return object.__new__(cls, plugin)
        else:
            yl.error('TypeError: plugin need ytPlugin, but: %s' % str(type(plugin)))

    def __init__(self, plugin):
        self.plugin = plugin
        self.startCallbackList = []
        self.startedCallbackList = []
        self.stopCallbackList = []
        self.stoppedCallbackList = []

    def run(self):
        if not self.plugin.isRunning():
            self.startCallback()
            self.plugin.ytStart()
            self.plugin.icon.setStatus(ytVariables.ytIcon_status_running)
            self.startedCallback()
        else:
            self.stopCallback()
            self.plugin.ytStop()
            self.plugin.icon.setStatus(ytVariables.ytIcon_status_stopped)
            self.stopedCallback()

    def startCallback(self):
        pass

    def startedCallback(self):
        pass

    def stopCallback(self):
        pass

    def stoppedCallback(self):
        pass

    def addStartCallback(self, func):
        self.startCallbackList.append(func)

    def addStartedCallback(self, func):
        pass

    def addStopCallback(self, func):
        pass

    def addStoppedCallback(self, func):
        pass
