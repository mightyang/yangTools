#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File              : ytWidgets.py
# Author            : yang <mightyang@hotmail.com>
# Date              : 04.03.2019
# Last Modified Date: 06.03.2019
# Last Modified By  : yang <mightyang@hotmail.com>


import ytNode
import nuke
from ytLoggingSettings import yl
import logging

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
        if isinstance(root, ytNode.ytNode):
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
            pn.appendChildren([ytNode.ytNode(), ytNode.ytNode(), ytNode.ytNode(), ytNode.ytNode(), ])
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

    def createNode(self, node, caller):
        yl.debug('create node in treeview')
        parent = node.getParent()
        if parent is not None:
            yl.debug('parent is %s' % parent.getName())
            parentIndex = self.getIndexFromNode(parent)
            i = node.getIndex()
            selection = QtCore.QItemSelection(self._parent.selectionModel().selection())
            yl.debug('store selection indexes: %s' % str([a.row() for a in selection.indexes()]))
            yl.debug('before insert node selection indexes: %s' % str([a.row() for a in self._parent.selectionModel().selection().indexes()]))
            self.beginInsertRows(parentIndex, i, i)
            if parentIndex.isValid():
                self.insertRow(i, parentIndex)
            else:
                self.insertRow(i, QtCore.QModelIndex())
            yl.debug('insert item %s in parent: %s at row %d' % (node.getName(), parent.getName(), i))
            yl.debug('between insert node selection indexes: %s' % str([a.row() for a in self._parent.selectionModel().selection().indexes()]))
            self.endInsertRows()
            self._parent.selectionModel().selection().merge(selection, QtCore.QItemSelectionModel.Select)
            yl.debug('after insert node selection indexes: %s' % str([a.row() for a in self._parent.selectionModel().selection().indexes()]))

    def deleteNode(self, node, caller):
        yl.debug('treeview delete node')
        index = self.getIndexFromNode(node)
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


class ytLogWidget(QtGuiWidgets.QWidget, logging.StreamHandler):
    def __init__(self, parent=None):
        super(ytLogWidget, self).__init__(parent)
        logging.StreamHandler.__init__(self)
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
        yl.addHandler(logging.StreamHandler(self.logWidget))
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
