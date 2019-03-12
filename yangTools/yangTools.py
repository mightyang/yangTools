#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File              : yangTools.py
# Author            : yang <mightyang@hotmail.com>
# Date              : 31.12.2018
# Last Modified Date: 12.03.2019
# Last Modified By  : yang <mightyang@hotmail.com>

import nuke
import ytEnvInit
from PySide2 import QtWidgets, QtCore
import ytNode, ytVariables, ytCallbacks, ytVersion
from ytWidgets import ytOutlineWidget
from ytLoggingSettings import yl, logging
import ytPlugins
from plugin import *


class yangTools(object):
    def __init__(self):
        yl.debug('initialize yangTools')
        self.version = ytVersion.ytVersion()
        yl.debug('version of yangTools: %s' % self.version.getVersion())
        self.isShow = False
        yl.debug('initialize root node')
        self.rootNode = ytNode.ytNode('root', nuke.root())
        yl.debug('initialize gui of yangTools')
        self.initGui()
        yl.debug('initialize plugins')
        self.initPlugin()
        yl.debug('connect gui\'s signal')
        self.connectGuiSignal()
        yl.debug('add method to ytNode\'s callback lists and plugin\'s callback list')
        self.addYtCallback()

    def initGui(self):
        self.outlineGui = ytOutlineWidget(self.getNukeMainWindow())
        self.outlineGui.outlineTreeView.model().setHeader(['name', 'type'])
        self.outlineGui.outlineTreeView.model().setRoot(self.rootNode)
        self.outlineGui.logHandle.setLevel(logging.DEBUG)


    def initPlugin(self):
        for p in ytPlugins.plugins:
            self.outlineGui.addPlugin(p)
            p.addStartedCallback((self.outlineGui.updateIcon, ()))
            p.addStoppedCallback((self.outlineGui.updateIcon, ()))

    def getNodePath(self, node):
        path = node.getName()
        while True:
            parent = node.getParent()
            if parent:
                path = parent.getName() + '.' + path
                node = parent
            else:
                break
        return path

    def getNodeTree(self, space=None):
        yl.debug('get node tree')
        if space is None:
            space = ytNode.ytNode('root', nuke.root())
        ns = nuke.toNode(space.getPath()).nodes()
        if len(ns) > 0:
            for n in ns:
                pn = ytNode.ytNode(n.name(), n, space)
                pn.setSelection(n['selected'].value(), ytVariables.ytCaller.yt_caller_nuke)
                if n.Class() == 'Group':
                    self.getNodeTree(pn)

    def printNodeTree(self, space=None, level=0):
        if space is None:
            space = self.rootNode
            print '\nroot'
        children = space.getChildren()
        if len(children) > 0:
            prefix = '│' * (level != 0) + '  ' * level
            for index, child in enumerate(children):
                if index == len(children) - 1:
                    print '%-60s%s' % (prefix + '└─' + child.getName(), str(child.getSelection()))
                elif index != len(children):
                    print '%-60s%s' % (prefix + '├─' + child.getName(), str(child.getSelection()))
                if child.getNode().Class() == 'Group':
                    self.printNodeTree(child, level + 1)

    def nukeCreateNodeCallback(self):
        '''the callback that called while creating node in nuke'''
        yl.debug('nukeCreateNodeCallback')
        node = nuke.thisNode()
        if '.' not in node.fullName():
            parent = self.getPkgNodeByPath()
        else:
            parent = self.getPkgNodeByPath('.'.join(node.fullName().split('.')[:-1]))
        if parent is not None:
            ytNode.ytNode(node.name(), node, parent)

    def nukeDestroyNodeCallback(self):
        '''the callback that called while deleting node in nuke'''
        yl.debug('nukeDestroyNodeCallback')
        node = nuke.thisNode()
        nodePkg = self.getPkgNodeByPath(node.fullName())
        nodePkg.getParent().removeChild(nodePkg)

    def nukeSelectionCallback(self):
        '''the callback that called while selecting node in nuke'''
        k = nuke.thisKnob()
        if k.name() == 'selected':
            yl.debug('nukeSelectNodeCallback')
            n = nuke.thisNode()
            if ytVariables.ytCaller.yt_caller_isGuiCallback:
                ytVariables.ytCaller.yt_caller_isGuiCallback = False
                return
            yt = self.getPkgNodeByPath(n.fullName())
            if yt is not None:
                yt.setSelection(k.value(), ytVariables.ytCaller.yt_caller_nuke)

    def addNukeCallback(self):
        '''add method to Nuke callback list'''
        yl.debug('nukeAddNodeCallback')
        if '*' not in nuke.onCreates or (self.nukeCreateNodeCallback, (), {}, None) not in nuke.onCreates['*']:
            nuke.addOnCreate(self.nukeCreateNodeCallback)
        if '*' not in nuke.onDestroys or (self.nukeDestroyNodeCallback, (), {}, None) not in nuke.onDestroys['*']:
            nuke.addOnDestroy(self.nukeDestroyNodeCallback)
        if '*' not in nuke.knobChangeds or (self.nukeSelectionCallback, (), {}, None) not in nuke.knobChangeds['*']:
            nuke.addKnobChanged(self.nukeSelectionCallback)

    def removeNukeCallback(self):
        '''remove method from Nuke callback list'''
        yl.debug('nukeDestroyNodeCallback')
        if '*' in nuke.onCreates and (self.nukeCreateNodeCallback, (), {}, None) in nuke.onCreates['*']:
            nuke.removeOnCreate(self.nukeCreateNodeCallback)
        if '*' in nuke.onDestroys and (self.nukeDestroyNodeCallback, (), {}, None) in nuke.onDestroys['*']:
            nuke.removeOnDestroy(self.nukeDestroyNodeCallback)
        if '*' in nuke.knobChangeds or (self.nukeSelectionCallback, (), {}, None) in nuke.knobChangeds['*']:
            nuke.removeKnobChanged(self.nukeSelectionCallback)

    def ytNodeSelectionCallback(self, pNode, caller):
        '''the callback that called while selecting node in nuke or in treeView'''
        yl.debug('call ytNodeSelectionCallback to select node in nuke or in treeView')
        if caller == ytVariables.ytCaller.yt_caller_gui:
            yl.debug('this is a operator in treeView, select node in nuke')
            ytVariables.ytCaller.yt_caller_isGuiCallback = True
            pNode.getNode().setSelected(pNode.getSelection())
        elif caller == ytVariables.ytCaller.yt_caller_nuke:
            yl.debug('this is a operator in nuke, select node in treeView')
            modelIndex = self.outlineGui.outlineTreeView.model().getIndexFromNode(pNode)
            selected = self.outlineGui.outlineTreeView.selectionModel().isSelected(modelIndex)
            yl.debug('selection status: %s[pgNode:%s] VS %s[treeview:%d %s]' % (pNode.getSelection(), pNode.getName(), selected, modelIndex.row(), self.outlineGui.outlineTreeView.model().getNodeFromIndex(modelIndex).getName()))
            if not pNode.getSelection() is selected:
                ytVariables.ytCaller.yt_caller_isNukeCallback = True
                if pNode.getSelection():
                    self.outlineGui.outlineTreeView.selectionModel().select(modelIndex, QtCore.QItemSelectionModel.Select)
                else:
                    self.outlineGui.outlineTreeView.selectionModel().select(modelIndex, QtCore.QItemSelectionModel.Deselect)
                yl.debug('selection indexes: %s' % str([i.row() for i in self.outlineGui.outlineTreeView.selectionModel().selection().indexes()]))

    def ytTreeViewSelectionCallback(self, selected, deselected):
        # signal loop break: gui -> ytNode -> nuke -> (break here) -> ytNode -> gui -> ...
        yl.debug('ytTreeViewSelectionCallback')
        if ytVariables.ytCaller.yt_caller_isNukeCallback:
            ytVariables.ytCaller.yt_caller_isNukeCallback = False
            return
        # deselect deselected node in nuke
        [i.internalPointer().setSelection(False) for i in deselected.indexes()]
        # select selected node in nuke
        [i.internalPointer().setSelection(True) for i in selected.indexes()]

    def addYtCallback(self):
        '''add methods to corresponding callback lists'''
        ytCallbacks.ytNode_selectionChanged_callback.append((self.ytNodeSelectionCallback, ()))
        ytCallbacks.ytNode_childCreated_callback.append((self.outlineGui.outlineTreeView.model().createNodeSignal.emit, ()))
        ytCallbacks.ytNode_childDestroyed_callback.append((self.outlineGui.outlineTreeView.model().deleteNodeSignal.emit, ()))

    def connectGuiSignal(self):
        self.outlineGui.closedSignal.connect(self.stop)
        self.outlineGui.outlineTreeView.selectionModel().selectionChanged.connect(self.ytTreeViewSelectionCallback)

    def getPkgNodeByPath(self, nodePkgPath=''):
        '''
        used by root ytNode
        nodePath is node fullName in nuke, getted by node.fullName()
        '''
        if not isinstance(nodePkgPath, str):
            yl.error(
                'TypeError: parameter need string, getted by node.fullName() in nuke')
            return None
        if nodePkgPath == '':
            return self.rootNode
        pathNames = nodePkgPath.split('.')
        nodePkg = self.rootNode
        if pathNames != []:
            for p in pathNames:
                cn = nodePkg.getChildrenName()
                if p in cn:
                    nodePkg = nodePkg[cn.index(p)]
                else:
                    yl.error('can not find node: %s' % nodePkgPath)
                    return None
            return nodePkg
        return None

    def show(self):
        if not self.isShow:
            self.addNukeCallback()
            self.getNodeTree(self.rootNode)
            self.outlineGui.show()
            self.isShow = True

    def stop(self):
        if self.isShow:
            self.removeNukeCallback()
            self.rootNode.clearChildren()
            self.outlineGui.outlineTreeView.model().resetModel()
            [p.go() for p in ytPlugins.plugins]
            self.isShow = False

    def addPluginSearchPath(self, path):
        ytEnvInit.appendEnv('YT_PLUGIN_PATH', path)
        ytEnvInit.appendEnv('PATH', path)

    def getPlugins(self):
        return ytPlugins.plugins

    def getNukeMainWindow(self):
        yl.debug('get main window instance of nuke')
        self.app = QtWidgets.QApplication.instance()
        for w in self.app.topLevelWidgets():
            if w.inherits('QMainWindow') and w.metaObject().className() == 'Foundry::UI::DockMainWindow':
                return w
        else:
            yl.error('RuntimeError: Could not find DockMainWindow instance')
