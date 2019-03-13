#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File              : scriptsytPlugin.py
# Author            : yang <mightyang@hotmail.com>
# Date              : 04.03.2019
# Last Modified Date: 13.03.2019
# Last Modified By  : yang <mightyang@hotmail.com>

from ytLoggingSettings import yl
import ytVariables
import ytVersion
import platform
import os

# set environment sperator
envSperator = ':'
if platform.system() == 'Windows':
    envSperator = ';'

class ytIcon():
    icon = {}

    def __init__(self, icon='play.ico'):
        self.status = ytVariables.ytIcon.ytIcon_status_stopped
        self.icon[self.status] = icon
        self.icon[ytVariables.ytIcon.ytIcon_status_running] = 'stop.ico'

    def getIcon(self):
        if self.status in self.icon:
            return self.icon[self.status]
        return self.icon[ytVariables.ytIcon.ytIcon_status_stopped]

    def setIcon(self, icon, status):
        if status in ytVariables.ytIcon.__dict__.values():
            i = self.findIcon(icon)
            if i:
                self.icon[status] = i
            else:
                yl.error('can not find icon: %s, use default icon' % icon)
        else:
            yl.error('TypeError: status need ytVariables.ytIcon.status')

    def setStatus(self, status):
        if status in ytVariables.ytIcon.__dict__.values():
            self.status = status
        else:
            yl.error('TypeError: status need ytVariables.ytIcon.status')

    def findIcon(self, icon):
        # if icon is exist
        if os.path.isfile(icon):
            return icon
        # find icon in YT_ICON_PATH
        paths = os.environ['YT_ICON_PATH'].split(envSperator)
        for p in paths:
            ip = os.path.join(p, icon)
            if os.path.isfile(ip):
                return ip


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

    def go(self):
        if not self.plugin.isRunning():
            try:
                self.startCallback()
                self.plugin.ytStart()
                self.startedCallback()
            except Exception, e:
                yl.error(e.message)
        else:
            try:
                self.stopCallback()
                self.plugin.ytStop()
                self.stoppedCallback()
            except Exception, e:
                yl.error(e.message)

    def stop(self):
        try:
            self.stopCallback()
            self.plugin.ytStop()
            self.stoppedCallback()
        except Exception, e:
            yl.error(e.message)

    def getName(self):
        return self.plugin.name

    def getTooltip(self):
        return self.plugin.help

    def getIcon(self):
        return self.plugin.icon.getIcon()

    def startCallback(self):
        if len(self.startCallbackList) > 0:
            yl.debug('startCallback of plugin: %s ' % self.plugin.name)
            try:
                for c in self.startCallbackList:
                    c[0](self, *c[1])
            except Exception as e:
                yl.error(e.message)

    def startedCallback(self):
        if len(self.startedCallbackList) > 0:
            yl.debug('startedCallback of plugin: %s ' % self.plugin.name)
            try:
                for c in self.startedCallbackList:
                    c[0](self, *c[1])
            except Exception as e:
                yl.error(e.message)

    def stopCallback(self):
        if len(self.stopCallbackList) > 0:
            yl.debug('stopCallback of plugin: %s ' % self.plugin.name)
            try:
                for c in self.stopCallbackList:
                    c[0](self, *c[1])
            except Exception as e:
                yl.error(e.message)

    def stoppedCallback(self):
        if len(self.stoppedCallbackList) > 0:
            yl.debug('stoppedCallback of plugin: %s ' % self.plugin.name)
            try:
                for c in self.stoppedCallbackList:
                    c[0](self, *c[1])
            except Exception as e:
                yl.error(e.message)

    def addStartCallback(self, callback):
        '''callback need list or tuple: (func, *argvs, **kwargvs)'''
        self.startCallbackList.append(callback)

    def addStartedCallback(self, callback):
        '''callback need list or tuple: (func, *argvs, **kwargvs)'''
        self.startedCallbackList.append(callback)

    def addStopCallback(self, callback):
        '''callback need list or tuple: (func, *argvs, **kwargvs)'''
        self.stopCallbackList.append(callback)

    def addStoppedCallback(self, callback):
        '''callback need list or tuple: (func, *argvs, **kwargvs)'''
        self.stoppedCallbackList.append(callback)

    def removeStartCallback(self, func):
        i = [f[0] for f in self.startCallbackList].index(func)
        if i:
            self.startCallbackList.pop(i)

    def removeStartedCallback(self, func):
        i = [f[0] for f in self.startedCallbackList].index(func)
        if i:
            self.startedCallbackList.pop(i)

    def removeStopCallback(self, func):
        i = [f[0] for f in self.stopCallbackList].index(func)
        if i:
            self.stopCallbackList.pop(i)

    def removeStoppedCallback(self, func):
        i = [f[0] for f in self.stoppedCallbackList].index(func)
        if i:
            self.stoppedCallbackList.pop(i)
