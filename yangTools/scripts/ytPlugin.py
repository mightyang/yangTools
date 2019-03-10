#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File              : ytPlugin.py
# Author            : yang <mightyang@hotmail.com>
# Date              : 04.03.2019
# Last Modified Date: 10.03.2019
# Last Modified By  : yang <mightyang@hotmail.com>

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
        if status in ytVariables.ytIcon.__dict__.values():
            self.icon[status] = icon
        else:
            yl.error('TypeError: status need ytVariables.ytIcon.status')

    def setStatus(self, status):
        if status in ytVariables.ytIcon.__dict__:
            self.status = status
        else:
            yl.error('TypeError: status need ytVariables.ytIcon.status')


class ytPlugin():
    def __init__(self):
        self.name = 'ytPlugin'
        self.version = ytVersion.ytVersion()
        self.help = ''
        self.icon = ytIcon()

    def ytStart(self):
        pass

    def ytStop(self):
        pass

    def isRunning(self):
        pass


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

    def getName(self):
        return self.plugin.name

    def getTooltip(self):
        return self.plugin.help

    def getIcon(self):
        return self.plugin.icon.getIcon()

    def startCallback(self):
        if len(self.startCallbackList) > 0:
            yl.debug('startCallback of plugin: %s ' % self._name)
            try:
                for c in self.startCallbackList:
                    c[0](self, *c[1])
            except Exception as e:
                yl.error(e.message)

    def startedCallback(self):
        if len(self.startedCallbackList) > 0:
            yl.debug('startedCallback of plugin: %s ' % self._name)
            try:
                for c in self.startCallbackList:
                    c[0](self, *c[1])
            except Exception as e:
                yl.error(e.message)

    def stopCallback(self):
        if len(self.stopCallbackList) > 0:
            yl.debug('stopCallback of plugin: %s ' % self._name)
            try:
                for c in self.startCallbackList:
                    c[0](self, *c[1])
            except Exception as e:
                yl.error(e.message)

    def stoppedCallback(self):
        if len(self.stoppedCallbackList) > 0:
            yl.debug('stoppedCallback of plugin: %s ' % self._name)
            try:
                for c in self.startCallbackList:
                    c[0](self, *c[1])
            except Exception as e:
                yl.error(e.message)

    def addStartCallback(self, func, *argvs, **kwargvs):
        self.startCallbackList.append((func, (argvs, kwargvs)))

    def addStartedCallback(self, func, *argvs, **kwargvs):
        self.startedCallbackList.append((func, (argvs, kwargvs)))

    def addStopCallback(self, func, *argvs, **kwargvs):
        self.stopCallbackList.append((func, (argvs, kwargvs)))

    def addStoppedCallback(self, func, *argvs, **kwargvs):
        self.stoppedCallbackList.append((func, (argvs, kwargvs)))
    def removeStartCallback(self, func, *argvs, **kwargvs):
        i = [f[0] for f in self.startCallbackList].index(func)
        if i:
            self.startCallbackList.pop(i)

    def removeStartedCallback(self, func, *argvs, **kwargvs):
        i = [f[0] for f in self.startedCallbackList].index(func)
        if i:
            self.startedCallbackList.pop(i)

    def removeStopCallback(self, func, *argvs, **kwargvs):
        i = [f[0] for f in self.stopCallbackList].index(func)
        if i:
            self.stopCallbackList.pop(i)

    def removeStoppedCallback(self, func, *argvs, **kwargvs):
        i = [f[0] for f in self.stoppedCallbackList].index(func)
        if i:
            self.stoppedCallbackList.pop(i)
