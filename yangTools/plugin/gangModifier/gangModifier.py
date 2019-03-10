#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File              : gangModifier.py
# Author            : yang <mightyang@hotmail.com>
# Date              : 05.03.2019
# Last Modified Date: 10.03.2019
# Last Modified By  : yang <mightyang@hotmail.com>

import logging
import nuke
import ytPlugin
import ytPlugins
import ytVersion
import ytVariables


yl = logging.getLogger('yangTools')

class gangModifier(ytPlugin.ytPlugin):
    def __init__(self):
        ytPlugin.ytPlugin.__init__(self)
        yl.debug('initialize gangModifier')
        self.gangModifierRunning = False
        self.selectedNodes = []
        self.files = {}
        self.gangItem = None
        self.ignoreKnobs = ['xpos', 'ypos']
        self.name = 'gangModifier'
        self.version = ytVersion.ytVersion(0, 0, 0)
        self.icon = ytPlugin.ytIcon()
        self.icon.setIcon('icons/play.ico', ytVariables.ytIcon.ytIcon_status_stopped)
        self.icon.setIcon('icons/stop.ico', ytVariables.ytIcon.ytIcon_status_running)

    def ytStart(self):
        if not self.gangModifierRunning:
            self.selectedNodes = nuke.selectedNodes()
            nuke.addKnobChanged(self.run)
            self.gangModifierRunning = True
            self.icon.setStatus(ytVariables.ytIcon.ytIcon_status_running)
            yl.info('gangModifier is started')

    def ytStop(self):
        if self.gangModifierRunning:
            self.selectedNodes = []
            self.files = {}
            nuke.removeKnobChanged(self.run)
            self.gangModifierRunning = False
            self.icon.setStatus(ytVariables.ytIcon.ytIcon_status_stopped)
            yl.info('gangModifier is stoped')

    def isRunning(self):
        return self.gangModifierRunning

    def nodeSelected(self, node):
        yl.debug('append selected node to selected-list')
        if node not in self.selectedNodes:
            self.selectedNodes.append(node)

    def nodeDeselected(self, node):
        yl.debug('remove deselected node to selected-list')
        if node in self.selectedNodes:
            self.selectedNodes.remove(node)

    def run(self):
        k = nuke.thisKnob()
        if k.name() in self.ignoreKnobs:
            return None
        n = nuke.thisNode()
        if k.name() == 'selected':
            if k.value():
                self.nodeSelected(n)
            else:
                self.nodeDeselected(n)
        else:
            for sn in self.selectedNodes:
                if sn.name() != n.name():
                    if k.name() != 'file':
                        sn[k.name()].setValue(k.value())


ytPlugins.registerPlugin(gangModifier())
