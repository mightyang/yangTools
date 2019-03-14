#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File              : scriptsytWidgets.py
# Author            : yang <mightyang@hotmail.com>
# Date              : 04.03.2019
# Last Modified Date: 14.03.2019
# Last Modified By  : yang <mightyang@hotmail.com>


import ytNode
import sys
import nuke
import ytPlugin
import ytPlugins
from ytLoggingSettings import yl, logging

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


class ytNodeModel(QtCore.QAbstractItemModel):
    # resetModeSignal = QtCore.Signal(ytNode.ytNode, int)
    createNodeSignal = QtCore.Signal(ytNode.ytNode, int)
    deleteNodeSignal = QtCore.Signal(ytNode.ytNode, int)

    def __init__(self, root=None, parent=None):
        super(ytNodeModel, self).__init__(parent)
        yl.debug('initialize ytNode.ytNodeModel')
        self._parent = parent
        self.root = root
        self._header = []
        # self.resetModeSignal.connect(self.updateView)
        self.createNodeSignal.connect(self.createNode)
        self.deleteNodeSignal.connect(self.deleteNode)

    def setRoot(self, root):
        yl.debug('set root')
        if isinstance(root, ytNode.ytNode):
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

    #  def removeRows(self, row, count, parent):
    #      yl.debug('remove rows')
    #      self.beginRemoveRows(parent, row, row + count - 1)
    #      if parent.isValid():
    #          parentPkg = self.getNodeFromIndex(parent)
    #          parentPkg.removeChildren(row, count)
    #      self.endRmoveRows()
    #      return True

    #  def insertRows(self, row, count, parent):
    #      yl.debug('insert rows')
    #      self.beginInsertRows(parent, row, row + count - 1)
    #      if parent.isValid():
    #          pn = self.getNodeFromIndex(parent)
    #          pn.appendChildren([ytNode.ytNode() for i in range(count)])
    #      self.endInsertRows()
    #      return True

    def getNodeFromIndex(self, index):
        if index.isValid():
            return index.internalPointer()
        else:
            return self.root

    def getIndexFromNode(self, pNode):
        yl.debug('get index from node')
        pNodeFullIndex = pNode.getFullIndex()
        modelIndex = QtCore.QModelIndex()
        if pNodeFullIndex is not None:
            for i in pNodeFullIndex:
                modelIndex = self.index(i, 0, modelIndex)
        return modelIndex

    def setHeader(self, header):
        if isinstance(header, list) or isinstance(header, tuple):
            self._header = header

    def createNode(self, node, caller):
        yl.debug('create node in treeview')
        parent = node.getParent()
        if parent is not None:
            parentIndex = self.getIndexFromNode(parent)
            i = node.getIndex()
            #  selection = QtCore.QItemSelection(self._parent.selectionModel().selection())
            self.beginInsertRows(parentIndex, i, i)
            if parentIndex.isValid():
                self.insertRow(i, parentIndex)
            else:
                self.insertRow(i, QtCore.QModelIndex())
            self.endInsertRows()
            #  self._parent.selectionModel().selection().merge(selection, QtCore.QItemSelectionModel.Select)

    def deleteNode(self, node, caller):
        yl.debug('treeview delete node')
        index = self.getIndexFromNode(node)
        #  selection = QtCore.QItemSelection(self._parent.selectionModel().selection())
        self.beginRemoveRows(index.parent(), index.row(), index.row())
        if index.isValid():
            #  self._parent.selectionModel().select(index, QtCore.QItemSelectionModel.Deselect)
            yl.debug('remove index: %d' % index.row())
            self.removeRow(index.row(), self.parent(index))
        self.endRemoveRows()
        #  self._parent.selectionModel().selection().merge(selection, QtCore.QItemSelectionModel.Select)

    def resetModel(self):
        self.beginResetModel()
        self.endResetModel()


class ytTreeView(QtGuiWidgets.QTreeView):
    def __init__(self, parent=None):
        super(ytTreeView, self).__init__(parent)
        yl.debug('initialize ytTreeView')
        self.treeViewModel = ytNodeModel(parent=self)
        self.setModel(self.treeViewModel)
        self.setSelectionMode(QtGuiWidgets.QAbstractItemView.ExtendedSelection)


class ytStreamHandler(logging.StreamHandler):
    def __init__(self, widget=None):
        super(ytStreamHandler, self).__init__()
        self.setFormatter(logging.Formatter('%(levelname)s %(asctime)s %(filename)s %(funcName)s[%(lineno)d]: %(message)s'))
        self.widget = widget

    def emit(self, record):
        msg = self.format(record)
        if self.widget:
            self.widget.append(msg.rstrip('\n'))
        else:
            sys.stdout(msg.rstrip('\n'))


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


class ytToolButton(QtGuiWidgets.QToolButton):
    def __init__(self, parent=None):
        super(ytToolButton, self).__init__(parent)
        self.plugin = None

    def setPlugin(self, plugin):
        if isinstance(plugin, ytPlugin.ytRegeditPlugin):
            self.plugin = plugin

    def getPlugin(self):
        return self.plugin


class ytOutlineWidget(QtGuiWidgets.QWidget):
    closedSignal = QtCore.Signal()

    def __init__(self, parent=None):
        super(ytOutlineWidget, self).__init__(parent)
        yl.debug('initialize ytOutlineWidget')
        self.setWindowFlags(QtCore.Qt.Window)
        self.setStyleSheet('QToolButton:hover {background-color:gray; border:1px;}')
        self.pluginButtons = []
        self.init()

    def init(self):
        self.resize(1000, 500)
        self.mainLayout = QtGuiWidgets.QVBoxLayout(self)
        self.mainSplitter = QtGuiWidgets.QSplitter(self)
        # log
        self.logFrame = QtGuiWidgets.QFrame(self)
        self.logLayout = QtGuiWidgets.QVBoxLayout(self.logFrame)
        self.logWidget = ytLogWidget(self)
        self.logLayout.addWidget(self.logWidget)
        self.logHandle = ytStreamHandler(self.logWidget.textEdit)
        yl.addHandler(self.logHandle)
        # toolbar
        self.toolbar = QtGuiWidgets.QToolBar(self)
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

    def addPlugin(self, plugin):
        if isinstance(plugin, ytPlugin.ytRegeditPlugin):
            button = ytToolButton(self)
            button.setPlugin(plugin)
            button.setIcon(QtGui.QIcon(plugin.getIcon()))
            button.setText(plugin.getName())
            button.setToolTip(plugin.getTooltip())
            button.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)
            button.clicked.connect(plugin.go)
            self.toolbar.addWidget(button)
            self.pluginButtons.append(button)

    def closeEvent(self, event):
        self.closedSignal.emit()

    def updateIcon(self, plugin):
        button = self.pluginButtons[ytPlugins.getPluginsName().index(plugin.getName())]
        yl.debug('set icon: %s' % plugin.getIcon())
        button.setIcon(QtGui.QIcon(plugin.getIcon()))
