#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File              : yangTools.py
# Author            : yang <mightyang@hotmail.com>
# Date              : 31.12.2018
# Last Modified Date: 04.03.2019
# Last Modified By  : yang <mightyang@hotmail.com>

import os
import re
import threading
import sys
import time
import nuke
import traceback
import abc


class yLogging():
    DEBUG = 0
    INFO = 1
    WARNING = 2
    ERROR = 3

    def __init__(self):
        self.__level = self.DEBUG
        self.__activeLevel = self.__level
        self.__levelStr = ['DEBUG', 'INFO', 'WARNING', 'ERROR']
        self.__results = []
        self.setFormat('%(acstime)s %(funcname)s[%(lineno)d] %(levelname)s: %(message)s')
        self.__file = open(os.path.join(os.path.expanduser('~'), 'yt.log'), 'w')
        self.__handler = None

    def setFormat(self, yFormat):
        '''
        %(levelno)s: the number of log level
        %(levelname)s: the name of log level
        %(pathname)s: sys.argv[0]
        %(filename)s: file name
        %(funcname)s: function name of current running
        %(lineno)d: current line of log
        %(acstime)s: time of log
        %(thread)d: thread id
        %(threadname)s: thread name
        %(process)d: process id
        %(message)s: log message
        '''
        pattern = re.compile(
            r'(.*?)(%\(levelno\)s|%\(levelname\)s|%\(pathname\)s|%\(filename\)s|%\(funcname\)s|%\(lineno\)d|%\(acstime\)s|%\(thread\)d|%\(threadname\)s|%\(process\)d|%\(message\)s)(.*?)'
        )
        self.__results = [j for i in pattern.findall(yFormat) for j in i if j]

    def replaceTag(self, tag, info):
        if tag == '%(levelno)s':
            return self.__activeLevel
        elif tag == '%(levelname)s':
            return self.__levelStr[self.__activeLevel]
        elif tag == '%(pathname)s':
            return sys._getframe().f_code.co_filename
        elif tag == '%(filename)s':
            return os.path.basename(sys._getframe().f_code.co_filename)
        elif tag == '%(funcname)s':
            return sys._getframe().f_back.f_back.f_code.co_name
        elif tag == '%(lineno)d':
            return str(sys._getframe().f_back.f_back.f_lineno)
        elif tag == '%(acstime)s':
            return time.asctime()
        elif tag == '%(thread)d':
            return str(threading.currentThread().ident)
        elif tag == '%(threadname)s':
            return threading.currentThread().name
        elif tag == '%(process)d':
            return str(os.getpid())
        elif tag == '%(message)s':
            return info
        else:
            return tag

    def setLevel(self, level):
        if isinstance(level, int) and level >= 0 and level <= 3:
            self.level = level
        else:
            print 'log level must be DEBUG, INFO, WARNING, ERROR.'

    def debug(self, info):
        if self.__level <= self.DEBUG:
            self.__activeLevel = self.DEBUG
            self.__write("".join([self.replaceTag(r, info) for r in self.__results]))

    def info(self, info):
        if self.__level <= self.INFO:
            self.__activeLevel = self.INFO
            self.__write("".join([self.replaceTag(r, info) for r in self.__results]))

    def warning(self, info):
        if self.__level <= self.WARNING:
            self.__activeLevel = self.WARNING
            self.__write("".join([self.replaceTag(r, info) for r in self.__results]))

    def error(self, info):
        if self.__level <= self.ERROR:
            self.__activeLevel = self.ERROR
            self.__write("".join([self.replaceTag(r, info) for r in self.__results]))

    def setHandler(self, handler):
        self.__handler = handler

    def __write(self, msg):
        self.__handler.write(msg + '\n')


yl = yLogging()
yl.setHandler(sys.stdout)

if nuke.NUKE_VERSION_MAJOR <= 10:
    yl.info('Nuke\' version is %s, import PySide.' % nuke.NUKE_VERSION_STRING)
    from PySide import QtGui as QtGuiWidgets
    from PySide import QtGui
    from PySide import QtCore
elif nuke.NUKE_VERSION_MAJOR > 10:
    yl.info('Nuke\'s version is %s, import PySide2.' % nuke.NUKE_VERSION_STRING)
    # from PySide2 import QtGui as QtGuiWidgets
    from PySide2 import QtWidgets as QtGuiWidgets
    from PySide2 import QtGui
    from PySide2 import QtCore


class ytCallbacks():
    ytNode_selectionChanged_callback = []
    ytNode_parentChanged_callback = []
    ytNode_nameChanged_callback = []
    ytNode_nodeChanged_callback = []
    ytNode_childCreated_callback = []
    ytNode_childDestroyed_callback = []

    gangModifier_start_callback = []
    gangModifier_stop_callback = []


class ytVariables():
    yt_caller_gui = 0
    yt_caller_nuke = 1
    yt_caller_isGuiCallback = False
    yt_caller_isNukeCallback = False


class ytNode(object):
    def __new__(cls, name='', node=None, parent=None):
        if parent is not None and not isinstance(parent, ytNode):
            yl.error('TypeError: parameter parent need ytNode')
        elif not isinstance(name, str):
            yl.error('TypeError: parameter name need string')
        else:
            return object.__new__(cls, name=name, node=node, parent=parent)

    def __init__(self, name='', node=None, parent=None):
        yl.debug('initialize ytNode: %s' % name)
        self._name = name
        self._node = node
        self._selected = False
        self._children = []
        self._parent = parent
        if self._parent is not None and self not in self._parent.getChildren():
            parent.appendChild(self)

    def __repr(self):
        return self._name

    def __getitem__(self, index):
        if isinstance(index, int) and index < self.getChildCount() and index >= -self.getChildCount():
            return self._children[index]
        else:
            yl.error('TypeError: parameter need int')

    def __len__(self):
        return len(self._children)

    def setNode(self, node, caller=ytVariables.yt_caller_gui):
        self._node = node
        self.callback(self, 3, caller)

    def setParent(self, parent, caller=ytVariables.yt_caller_gui):
        self._parent = parent
        self.callback(self, 1, caller)
        return True

    def setName(self, name, caller=ytVariables.yt_caller_gui):
        self.callback(self, 2, caller)
        self._name = name

    def setSelection(self, selected, caller=ytVariables.yt_caller_gui):
        self._selected = selected
        self.callback(self, 0, caller)

    def appendChild(self, child, caller=ytVariables.yt_caller_gui):
        if not isinstance(child, ytNode):
            yl.error('TypeError: parameter child need ytNode')
        if child not in self._children:
            self._children.append(child)
            self.callback(child, 4, caller)
            child.setParent(self)
            yl.debug('append child: %s' % child.getName())
        else:
            yl.error('%s has exist in %s, pass' % (child.getName(), self._name))

    def appendChildren(self, children, caller=ytVariables.yt_caller_gui):
        if isinstance(children, list):
            for child in children:
                self._children.append(child)
            self.callback(child, 4, caller)

    def insertChild(self, index, child, caller=ytVariables.yt_caller_gui):
        self._children.insert(index, child)
        self.callback(child, 4, caller)
        child.setParent(self)
        yl.debug('insert child: %s at %d' % (child.getName(), index))

    def removeChild(self, child, caller=ytVariables.yt_caller_gui):
        if child in self._children:
            child.setParent(None)
            self._children.remove(child)
            self.callback(child, 5, caller)
            yl.debug('remove child: %s' % child.getName())
            return True
        else:
            return False

    def removeChildren(self, index, count, caller=ytVariables.yt_caller_gui):
        if count < 1:
            yl.error('count need greater than 0')
            return False
        if index + count > len(self._children) or index - count < -len(self._children):
            yl.error('out of range')
            return False
        [(i.setParent(None) and i.setDel(True)) for i in self._children[index: index + count]]
        self._children = self._children[:index] + self._children[index + count:]
        self.callback(child, 5, caller)
        yl.debug('remove children from %d to %d' % (index, index + count - 1))
        return True

    def hasChild(self, child):
        return child in self._children

    def getChild(self, index=-1):
        if index < len(self._children) and index >= -len(self._children):
            return self._children[index]
        else:
            yl.error('index:%d out of children range' % index)

    def getNode(self):
        return self._node

    def getChildrenName(self):
        return [c.getName() for c in self._children]

    def getParent(self):
        return self._parent

    def getName(self):
        return self._name

    def getSelection(self):
        return self._selected

    def getChildren(self):
        return self._children

    def getChildCount(self):
        return len(self._children)

    def getPath(self):
        if self._parent is not None:
            return self._parent.getPath() + '.' + self._name
        else:
            return self._name

    def getIndex(self):
        if self._parent is not None and self in self._parent.getChildren():
            return self._parent.getChildren().index(self)
        else:
            return 0

    def getFullIndex(self):
        if self._parent is not None and self in self._parent.getChildren():
            fullIndex = []
            child = self
            while True:
                fullIndex.insert(0, child.getIndex())
                child = child.getParent()
                if child.getParent() is None:
                    return fullIndex

    def callback(self, item, n, caller):
        '''
        n value:
            0: ytNode_selectionChanged_callback
            1: ytNode_parentChanged_callback
            2: ytNode_nameChanged_callback
            3: ytNode_nodeChanged_callback
            4: ytNode_childrenChanged_callback
        '''
        if n == 0 and len(ytCallbacks.ytNode_selectionChanged_callback) > 0:
            yl.debug('ytNode: %s selection changed callback' % self._name)
            try:
                for c in ytCallbacks.ytNode_selectionChanged_callback:
                    c[0](item, caller, *c[1])
            except Exception as e:
                yl.error(e.message)
        if n == 1 and len(ytCallbacks.ytNode_parentChanged_callback) > 0:
            yl.debug('ytNode: %s parent changed callback' % self._name)
            try:
                for c in ytCallbacks.ytNode_parentChanged_callback:
                    c[0](item, caller, *c[1])
            except Exception as e:
                yl.error(e.message)
        if n == 2 and len(ytCallbacks.ytNode_nameChanged_callback) > 0:
            yl.debug('ytNode: %s name changed callback' % self._name)
            try:
                for c in ytCallbacks.ytNode_nameChanged_callback:
                    c[0](item, caller, *c[1])
            except Exception as e:
                yl.error(e.message)
        if n == 3 and len(ytCallbacks.ytNode_nodeChanged_callback) > 0:
            yl.debug('ytNode: %s node changed callback' % self._name)
            try:
                for c in ytCallbacks.ytNode_nodeChanged_callback:
                    c[0](item, caller, *c[1])
            except Exception as e:
                yl.error(e.message)
        if n == 4 and len(ytCallbacks.ytNode_childCreated_callback) > 0:
            yl.debug('ytNode: child %s created callback' % self._name)
            try:
                for c in ytCallbacks.ytNode_childCreated_callback:
                    c[0](item, caller, *c[1])
            except Exception as e:
                yl.error(e.message)
        if n == 5 and len(ytCallbacks.ytNode_childDestroyed_callback) > 0:
            yl.debug('ytNode: child %s deleted callback' % self._name)
            try:
                for c in ytCallbacks.ytNode_childDestroyed_callback:
                    c[0](item, caller, *c[1])
            except Exception as e:
                yl.error(e.message)


class ytNodeModel(QtCore.QAbstractItemModel):
    # resetModeSignal = QtCore.Signal(ytNode, int)
    createNodeSignal = QtCore.Signal(ytNode, int)
    deleteNodeSignal = QtCore.Signal(ytNode, int)

    def __init__(self, root=None, parent=None):
        super(ytNodeModel, self).__init__(parent)
        yl.debug('initialize ytNodeModel')
        self._parent = parent
        self.root = root
        self._header = []
        # self.resetModeSignal.connect(self.updateView)
        self.createNodeSignal.connect(self.createNode)
        self.deleteNodeSignal.connect(self.deleteNode)

    def setRoot(self, root):
        if isinstance(root, ytNode):
            yl.debug('set ytNodeMode\'s root: %s' % root.getName())
            self.root = root
        else:
            yl.error('TypeError: ytNodeMode\'s root need ytNode')

    def columnCount(self, parent):
        return 1

    def rowCount(self, parent):
        n = self.getNodeFromIndex(parent)
        if n is not None:
            return n.getChildCount()
        else:
            return 0

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if not index.isValid():
            return ''
        if role == QtCore.Qt.DisplayRole or role == QtCore.Qt.EditRole:
            return self.getNodeFromIndex(index).getName()

    def parent(self, child):
        if child.isValid():
            n = self.getNodeFromIndex(child)
            pNode = n.getParent()
            if pNode is None or pNode == self.root:
                return QtCore.QModelIndex()
            else:
                return self.createIndex(pNode.getIndex(), 0, pNode)

    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        if role == QtCore.Qt.DisplayRole and orientation == QtCore.Qt.Horizontal:
            if len(self._header) > 0:
                return self._header[section]
            else:
                yl.debug('there is no header')

    def index(self, row, column, parent):
        p = self.getNodeFromIndex(parent)
        child = p.getChild(row)
        if child is not None:
            return self.createIndex(row, column, self.getNodeFromIndex(parent)[row])
        else:
            return QtCore.QModelIndex()

    def flags(self, index):
        return (QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)

    def removeRows(self, row, count, parent):
        self.beginRemoveRows(parent, row, row + count - 1)
        if parent.isValid():
            parentPkg = self.getNodeFromIndex(parent)
            parentPkg.removeChildren(row, count)
        self.endRmoveRows()
        return True

    def insertRows(self, row, count, parent):
        self.beginInsertRows(parent, row, row + count - 1)
        if parent.isValid():
            pn = self.getNodeFromIndex(parent)
            pn.appendChildren([ytNode(), ytNode(), ytNode(), ytNode(), ])
        self.endInsertRows()
        return True

    def getNodeFromIndex(self, index):
        if index.isValid():
            return index.internalPointer()
        else:
            return self.root

    def getIndexFromNode(self, pNode):
        pNodeFullIndex = pNode.getFullIndex()
        modelIndex = QtCore.QModelIndex()
        if pNodeFullIndex is not None:
            for i in pNodeFullIndex:
                modelIndex = self.index(i, 0, modelIndex)
        return modelIndex

    def setHeader(self, header):
        if isinstance(header, list) or isinstance(header, tuple):
            self._header = header

    def createNode(self, ytNode, caller):
        yl.debug('create node in treeview')
        parent = ytNode.getParent()
        if parent is not None:
            yl.debug('parent is %s' % parent.getName())
            parentIndex = self.getIndexFromNode(parent)
            i = ytNode.getIndex()
            selection = QtCore.QItemSelection(self._parent.selectionModel().selection())
            yl.debug('store selection indexes: %s' % str([a.row() for a in selection.indexes()]))
            yl.debug('before insert node selection indexes: %s' % str([a.row() for a in self._parent.selectionModel().selection().indexes()]))
            self.beginInsertRows(parentIndex, i, i)
            if parentIndex.isValid():
                self.insertRow(i, parentIndex)
            else:
                self.insertRow(i, QtCore.QModelIndex())
            yl.debug('insert item %s in parent: %s at row %d' % (ytNode.getName(), parent.getName(), i))
            yl.debug('between insert node selection indexes: %s' % str([a.row() for a in self._parent.selectionModel().selection().indexes()]))
            self.endInsertRows()
            self._parent.selectionModel().selection().merge(selection, QtCore.QItemSelectionModel.Select)
            yl.debug('after insert node selection indexes: %s' % str([a.row() for a in self._parent.selectionModel().selection().indexes()]))

    def deleteNode(self, ytNode, caller):
        yl.debug('treeview delete node')
        index = self.getIndexFromNode(ytNode)
        selection = QtCore.QItemSelection(self._parent.selectionModel().selection())
        yl.debug('store selection indexes: %s' % str([a.row() for a in selection.indexes()]))
        yl.debug('before remove node selection indexes: %s' % str([a.row() for a in self._parent.selectionModel().selection().indexes()]))
        self.beginRemoveRows(index.parent(), index.row(), index.row())
        if index.isValid():
            self.removeRow(index.row(), self.parent(index))
        self.endRemoveRows()
        self._parent.selectionModel().selection().merge(selection, QtCore.QItemSelectionModel.Select)
        yl.debug('after remove node selection indexes: %s' % str([a.row() for a in self._parent.selectionModel().selection().indexes()]))


class ytTreeView(QtGuiWidgets.QTreeView):
    def __init__(self, parent=None):
        super(ytTreeView, self).__init__(parent)
        yl.debug('initialize ytTreeView')
        self.treeViewModel = ytNodeModel(parent=self)
        self.setModel(self.treeViewModel)
        self.setSelectionMode(QtGuiWidgets.QAbstractItemView.ExtendedSelection)


class ytLogWidget(QtGuiWidgets.QWidget):
    def __init__(self, parent=None):
        super(ytLogWidget, self).__init__(parent)
        yl.debug('initialize ytLogWidget')
        self.init()

    def init(self):
        self.mainLayout = QtGuiWidgets.QVBoxLayout(self)
        self.textEdit = QtGuiWidgets.QTextEdit(self)
        self.textEdit.setReadOnly(True)
        self.clearButton = QtGuiWidgets.QPushButton(self)
        self.clearButton.setText('Clean')
        self.clearButton.clicked.connect(self.textEdit.clear)
        self.mainLayout.addWidget(self.textEdit)
        self.mainLayout.addWidget(self.clearButton)

    def write(self, msg):
        self.textEdit.append(msg.rstrip('\n'))
        self.update()


class ytOutlineWidget(QtGuiWidgets.QWidget):
    closedSignal = QtCore.Signal()

    def __init__(self, parent=None):
        super(ytOutlineWidget, self).__init__(parent)
        yl.debug('initialize ytOutlineWidget')
        self.setWindowFlags(QtCore.Qt.Window)
        self.setStyleSheet('QToolButton:hover {background-color:gray; border:1px;}')
        self.init()

    def init(self):
        global yl
        self.resize(1000, 500)
        self.mainLayout = QtGuiWidgets.QVBoxLayout(self)
        self.mainSplitter = QtGuiWidgets.QSplitter(self)
        # log
        self.logFrame = QtGuiWidgets.QFrame(self)
        self.logLayout = QtGuiWidgets.QVBoxLayout(self.logFrame)
        self.logWidget = ytLogWidget(self)
        self.logLayout.addWidget(self.logWidget)
        yl.setHandler(self.logWidget)
        # toolbar
        self.toolbar = QtGuiWidgets.QToolBar(self)
        self.gangModifierButton = QtGuiWidgets.QToolButton(self)
        self.gangModifierButton.setIcon(QtGui.QIcon('play.ico'))
        self.gangModifierButton.setText('gang')
        self.gangModifierButton.setToolTip('this is a tool that add method to nuke\'s knobChangeds callback list, so when you change knob\'s value, nuke will call this method to change the same name knob of other selected nodes synchronous')
        self.gangModifierButton.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)
        self.toolbar.addWidget(self.gangModifierButton)
        # outline
        self.outlineFrame = QtGuiWidgets.QFrame(self)
        self.outlineLayout = QtGuiWidgets.QVBoxLayout(self)
        self.outlineFrame.setLayout(self.outlineLayout)
        self.outlineTreeView = ytTreeView(self)
        self.outlineLayout.addWidget(self.outlineTreeView)
        # add widget in mainSplitter
        self.mainSplitter.addWidget(self.outlineFrame)
        self.mainSplitter.addWidget(self.logFrame)
        self.mainSplitter.setStretchFactor(0, 1)
        self.mainSplitter.setStretchFactor(1, 4)
        # add widget in mainLayout
        self.mainLayout.addWidget(self.toolbar)
        self.mainLayout.addWidget(self.mainSplitter)

    def setGangModifierSatus(self, item, caller, running):
        if running:
            yl.debug('gangModifier is running, change icon to stop.ico')
            self.gangModifierButton.setIcon(QtGui.QIcon('stop.ico'))
        else:
            yl.debug('gangModifier is stoped, change icon to play.ico')
            self.gangModifierButton.setIcon(QtGui.QIcon('play.ico'))

    def closeEvent(self, event):
        self.closedSignal.emit()


class gangModifier(object):
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

    def callback(self, item, n, caller):
        '''
        n value:
            0:gangModifier_start_callback
            1:gangModifier_stop_callback
        '''
        if n == 0 and len(ytCallbacks.gangModifier_start_callback) > 0:
            yl.debug('gangModifier starting callback')
            try:
                for c in ytCallbacks.gangModifier_start_callback:
                    c[0](item, caller, *c[1])
            except Exception:
                yl.error(traceback.format_exc())
        if n == 1 and len(ytCallbacks.gangModifier_stop_callback) > 0:
            yl.debug('gangModifier stopping callback')
            try:
                for c in ytCallbacks.gangModifier_stop_callback:
                    c[0](item, caller, *c[1])
            except Exception:
                yl.error(traceback.format_exc())

    def compareString(self, ms, s):
        pass


class ytPlugin():
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

    def startCallback(self, *args, **kwargs):
        pass

    def stoppCallback(self, *args, **kwargs):
        pass


class yangTools(object):
    def __init__(self):
        yl.debug('initialize yangTools')
        self.rootNode = ytNode('root', nuke.root())
        self.initGui()
        self.gangModifier = gangModifier()
        self.connectGuiSlot()
        self.connectButton()
        self.addNukeCallback()
        self.addYtCallback()
        self.getNodeTree(self.rootNode)

    def stop(self):
        self.removeNukeCallback()
        self.gangModifier.stop()

    def initGui(self):
        self.outlineGui = ytOutlineWidget(self.getNukeMainWindow())
        self.outlineGui.outlineTreeView.model().setHeader(['name', 'type'])
        self.outlineGui.outlineTreeView.model().setRoot(self.rootNode)

    def getNukeMainWindow(self):
        yl.debug('get main window instance of nuke')
        self.app = QtGuiWidgets.QApplication.instance()
        for w in self.app.topLevelWidgets():
            if w.inherits('QMainWindow') and w.metaObject().className() == 'Foundry::UI::DockMainWindow':
                return w
        else:
            yl.error('RuntimeError: Could not find DockMainWindow instance')

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
            space = ytNode('root', nuke.root())
        ns = nuke.toNode(space.getPath()).nodes()
        if len(ns) > 0:
            for n in ns:
                pn = ytNode(n.name(), n, space)
                pn.setSelection(n['selected'].value(), ytVariables.yt_caller_nuke)
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
            ytNode(node.name(), node, parent)

    def nukeDestroyNodeCallback(self):
        '''the callback that called while deleting node in nuke'''
        node = nuke.thisNode()
        nodePkg = self.getPkgNodeByPath(node.fullName())
        nodePkg.getParent().removeChild(nodePkg)

    def nukeSelectionCallback(self):
        '''the callback that called while selecting node in nuke'''
        k = nuke.thisKnob()
        if k.name() == 'selected':
            n = nuke.thisNode()
            if ytVariables.yt_caller_isGuiCallback:
                ytVariables.yt_caller_isGuiCallback = False
                return
            yt = self.getPkgNodeByPath(n.fullName())
            if yt is not None:
                yt.setSelection(k.value(), ytVariables.yt_caller_nuke)

    def addNukeCallback(self):
        '''add method to Nuke callback list'''
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
        if caller == ytVariables.yt_caller_gui:
            yl.debug('this is a operator in treeView, select node in nuke')
            ytVariables.yt_caller_isGuiCallback = True
            pNode.getNode().setSelected(pNode.getSelection())
        elif caller == ytVariables.yt_caller_nuke:
            yl.debug('this is a operator in nuke, select node in treeView')
            modelIndex = self.outlineGui.outlineTreeView.model().getIndexFromNode(pNode)
            selected = self.outlineGui.outlineTreeView.selectionModel().isSelected(modelIndex)
            yl.debug('selection status: %s[pgNode:%s] VS %s[treeview:%d %s]' % (pNode.getSelection(), pNode.getName(), selected, modelIndex.row(), self.outlineGui.outlineTreeView.model().getNodeFromIndex(modelIndex).getName()))
            if not pNode.getSelection() is selected:
                ytVariables.yt_caller_isNukeCallback = True
                if pNode.getSelection():
                    self.outlineGui.outlineTreeView.selectionModel().select(modelIndex, QtCore.QItemSelectionModel.Select)
                else:
                    self.outlineGui.outlineTreeView.selectionModel().select(modelIndex, QtCore.QItemSelectionModel.Deselect)
                yl.debug('selection indexes: %s' % str([i.row() for i in self.outlineGui.outlineTreeView.selectionModel().selection().indexes()]))

    def addYtCallback(self):
        '''add callbacks to corresponding callback lists'''
        yl.debug('call addYtCallback to add callback method to ytNode\'s callback lists and plugin\'s callback list')
        ytCallbacks.ytNode_selectionChanged_callback.append((self.ytNodeSelectionCallback, ()))
        ytCallbacks.ytNode_childCreated_callback.append((self.outlineGui.outlineTreeView.model().createNodeSignal.emit, ()))
        ytCallbacks.ytNode_childDestroyed_callback.append((self.outlineGui.outlineTreeView.model().deleteNodeSignal.emit, ()))
        ytCallbacks.gangModifier_start_callback.append((self.outlineGui.setGangModifierSatus, (True, )))
        ytCallbacks.gangModifier_stop_callback.append((self.outlineGui.setGangModifierSatus, (False, )))

    def ytTreeViewSelectionCallback(self, selected, deselected):
        # signal loop break: gui -> ytNode -> nuke -> (break here) -> ytNode -> gui -> ...
        yl.debug('ytTreeViewSelectionCallback')
        if ytVariables.yt_caller_isNukeCallback:
            ytVariables.yt_caller_isNukeCallback = False
            return
        # deselect deselected node in nuke
        [i.internalPointer().setSelection(False) for i in deselected.indexes()]
        # select selected node in nuke
        [i.internalPointer().setSelection(True) for i in selected.indexes()]

    def connectGuiSlot(self):
        self.outlineGui.closedSignal.connect(self.removeNukeCallback)
        self.outlineGui.closedSignal.connect(self.gangModifier.stop)
        self.outlineGui.outlineTreeView.selectionModel().selectionChanged.connect(self.ytTreeViewSelectionCallback)

    def connectButton(self):
        self.outlineGui.gangModifierButton.clicked.connect(self.gangModifier.go)

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
        self.addNukeCallback()
        self.outlineGui.show()


if __name__ == '__main__':
    t = yangTools()
    t.show()
