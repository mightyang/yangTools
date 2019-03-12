#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File              : plugingangModifiergangModifier.py
# Author            : yang <mightyang@hotmail.com>
# Date              : 05.03.2019
# Last Modified Date: 12.03.2019
# Last Modified By  : yang <mightyang@hotmail.com>

import logging
import nuke
import ytPlugin
import ytPlugins
import ytVersion
import ytVariables
from PySide2 import QtWidgets


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
        self.help = 'used to change value of knob of selected nodes in sync\nselect nodes => open property panel of one node => change knob => knobs which have the same name of other selected node would be changed too'
        self.icon = ytPlugin.ytIcon()
        self.icon.setIcon('play.ico', ytVariables.ytIcon.ytIcon_status_stopped)
        self.icon.setIcon('stop.ico', ytVariables.ytIcon.ytIcon_status_running)
        self.app = QtWidgets.QApplication.instance()
        self.cw = self.app.focusWidget()

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

    def getWidgetUntilName(self, widget, name):
        n = widget.windowTitle()
        if n:
            if n.strip() == name:
                return widget
            else:
                return None
        elif widget.parent():
            self.getWidgetUntilName(widget.parent())
        else:
            return None

    def run(self):
        k = nuke.thisKnob()
        if self.cw != self.app.focusWidget():
            self.cw = self.app.focusWidget()
            if self.getWidgetUntilName(self.cw, 'Dope Sheet'):
                return None

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
