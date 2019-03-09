#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File              : gangModifier.py
# Author            : yang <mightyang@hotmail.com>
# Date              : 05.03.2019
# Last Modified Date: 08.03.2019
# Last Modified By  : yang <mightyang@hotmail.com>

import logging
import nuke
from src import ytPlugin


yl = logging.getLogger('yangTools')


class gangModifier(ytPlugin):
    def __init__(self):
        yl.debug('initialize gangModifier')
        self.gangModifierRunning = False
        self.selectedNodes = []
        self.files = {}
        self.gangItem = None
        self.ignoreKnobs = ['xpos', 'ypos']

    def nodeSelected(self, node):
        yl.debug('append selected node to selected-list')
        if node not in self.selectedNodes:
            self.selectedNodes.append(node)

    def nodeDeselected(self, node):
        yl.debug('remove deselected node to selected-list')
        if node in self.selectedNodes:
            self.selectedNodes.remove(node)

    def start(self):
        self.selectedNodes = nuke.selectedNodes()
        nuke.addKnobChanged(self.run)
        self.gangModifierRunning = True
        yl.info('gangModifyer is started')

    def stop(self):
        self.selectedNodes = []
        self.files = {}
        nuke.removeKnobChanged(self.run)
        self.gangModifierRunning = False
        yl.info('gangModifyer is stoped')

    def go(self):
        if self.gangModifierRunning:
            yl.debug('stop gangModifier')
            self.callback(self, 1, self)
            self.stop()
        else:
            yl.debug('start gangModifier')
            self.callback(self, 0, self)
            self.start()

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

    def isrunning(self):
        return self.gangModifierRunning

