#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File              : ytPlugins.py
# Author            : yang <mightyang@hotmail.com>
# Date              : 10.03.2019
# Last Modified Date: 10.03.2019
# Last Modified By  : yang <mightyang@hotmail.com>

import ytPlugin
from ytLoggingSettings import yl


plugins = []

def registerPlugin(plugin):
    global plugins
    if isinstance(plugin, ytPlugin.ytPlugin):
        if plugin.name not in getPluginsName():
            p = ytPlugin.ytRegeditPlugin(plugin)
            plugins.append(p)
            yl.debug('registered plugin: %s' % p.getName())
            return True
        else:
            yl.warning('plugin: %s has existed, ignore' % p.getName())
    return False

def deRegeditPlugin(pluginName):
    global plugins
    if pluginName in getPluginsName():
        yl.debug('deRegedited plugin: %s' % pluginName)
        p = getPluginByName(pluginName)
        plugins.pop(getPluginsName().index(pluginName))
    else:
        yl.warning('plugin: %s do not existed, ignore' % p.getName())

def getPluginByIndex(index):
    global plugins
    return plugins[index]

def getPluginByName(name):
    global plugins
    return plugins[getPluginsName().index(name)]

def getPluginsName():
    global plugins
    return [p.getName() for p in plugins]

