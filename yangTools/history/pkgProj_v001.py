#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File              : pkgProj_v001.py
# Author            : yang <mightyang@hotmail.com>
# Date              : 31.12.2018
# Last Modified Date: 01.01.2019
# Last Modified By  : yang <mightyang@hotmail.com>


import os
import re
import nuke
import shutil
import sys
import thread


if nuke.NUKE_VERSION_MAJOR <= 10:
    print 'Nuke version is %s, import PySide.' % nuke.NUKE_VERSION_STRING
    from PySide import QtGui as QtGuiWidgets
    from PySide import QtCore
elif nuke.NUKE_VERSION_MAJOR > 10:
    print 'Nuke version is %s, import PySide2.' % nuke.NUKE_VERSION_STRING
    from PySide2 import QtGui as QtGuiWidgets
    from PySide2 import QtWidgets as QtGuiWidgets
    from PySide2 import QtCore

# (fun, (argvs))
valueChangedCallback = []
statusChangedCallback = []
countChangedCallback = []
createCallback = []
pkgFileCallback = []

perNodeClassCallback = []
perNodeFilePathCallback = []
perFileCallback = []
perSpaceCallback = []
perPkgFileCallback = []
startGetFilesCallback = []
spaceRootCallback = []
searchNodes = [['Read', 'file', None, None],
               ['ReadGeo', 'file', None, None],
               ['ReadGeo2', 'file', None, None],
               ['Camera', 'file', 'read_from_file', True],
               ['Camera2', 'file', 'read_from_file', True],
               ['ModifyRIB', 'ribArchive', 'useRibArchive', True],
               ['Vectorfield', 'vfield_file', None, None],
               ['OCIOFileTransform', 'file', None, None],
               ['ParticleCache', 'file', None, None],
               ['AudioRead', 'file', None, None],
               ['Precomp', 'file', None, None]]


def unitePath(path):
    try:
        path = str(path)
    except Exception, e:
        print e.message
    if os.path.isfile(path):
        return path.replace('\\', '/')
    elif os.path.isdir(path):
        if not path.endswith('/') or not path.endswith('\\'):
            path += '/'
        return path.replace('\\', '/')


class pkgStatus(object):
    NORMAL = 'pkg_status_normal'
    PKGED = 'pkg_status_pkged'
    NOEXISTS = 'pkg_status_file'


class pkgItemType(object):
    NORMAL = 'pkg_item_normal'
    SPACEROOT = 'pkg_item_spaceRoot'
    SPACE = 'pkg_item_SPACE'
    NODECLASS = 'pkg_item_nodeClass'
    NODE = 'pkg_item_node'
    NODEFILES = 'pkg_item_nodefiles'
    DIR = 'pkg_item_dir'
    FILE = 'pkg_item_file'
    SEQUENCE = 'pkg_item_sequence'


class pkgItem(object):
    def __new__(cls, parent=None, value='', status=None, itemtype=None, count=0, pos=0):
        if not (parent is None or isinstance(parent, pkgItem)):
            print 'parameter type error: parent.'
        elif not isinstance(value, str):
            print 'parameter type error: value.'
        elif status not in pkgStatus.__dict__.values():
            print 'parameter type error: status.'
        elif itemtype not in pkgItemType.__dict__.values():
            print 'parameter type error: itemtype.'
        elif not isinstance(count, int):
            print 'parameter type error: count.'
        else:
            return object.__new__(cls, value, status, itemtype, count)

    def __init__(self, parent=None, value='', status=None, itemtype=None, count=0, pos=0):
        self.__value = value
        self.__dirPath = None
        self.__nodePath = None
        self.__status = status
        self.__count = count
        self.__type = itemtype
        self.__list = []
        self.__parent = parent
        self.__pos = pos
        self.callback(self, 3)

    def __getitem__(self, key):
        if isinstance(key, int):
            return self.__list[key]
        elif isinstance(key, str):
            for i in self.__list:
                if i.getValue() == key:
                    return i
        return None

    def __setitem__(self, key, item):
        if isinstance(item, pkgItem):
            if isinstance(key, int):
                self.__list[key] = item
            elif isinstance(key, str):
                for index, it in enumerate(self.__list):
                    if it.getValue() == key:
                        self.__list[index] = item
                    else:
                        print 'there is no %s key.' % key
        else:
            print 'value must be a pkgItem object.'

    def __len__(self):
        return len(self.__list)

    def __str__(self):
        return self.__value

    def appendItem(self, item):
        callBackType = 2
        if isinstance(item, pkgItem):
            self.__list.append(item)
            self.__count += 1
            self.callback(self, callBackType)
        else:
            print 'item need pkgItem class.'

    def removeItem(self, item):
        callBackType = 2
        if item in self.__list:
            self.__list.remove(item)
            self.__count -= 1
            self.callback(self, callBackType)

    def popItem(self, index=-1):
        callBackType = 2
        try:
            self.__list.pop(index)
        except Exception, e:
            print e.message
            return
        self.__count -= 1
        self.callback(self, callBackType)

    def insert(self, index, item):
        self.__list.insert(index, item)

    def children(self):
        return self.__list

    def setValue(self, val):
        callbackType = 0
        self.__val = val
        self.callback(val, callbackType)

    def setDirPath(self, path):
        self.__dirPath = path

    def setNodePath(self, path):
        self.__nodePath = path

    def setStatus(self, s):
        callbackType = 1
        if hasattr(pkgStatus, s):
            self.__status = s
            self.callback(s, callbackType)
        else:
            print 'pkgStatus do not have [%s] attribute.' % s

    def setType(self, tp):
        self.__type = tp

    def setPos(self, pos):
        if isinstance(pos, int):
            self.__pos = pos
        else:
            print 'TypeError: pos need int, but receive a %s.' % type(pos)

    def callback(self, item, n):
        '''
        n value:
            0: valueChanged
            1: statusChanged
            2: countChanged
            3: create
        '''
        global valueChangedCallback
        global statusChangedCallback
        global countChangedCallback
        global createCallback
        if n == 0 and valueChangedCallback:
            try:
                for c in valueChangedCallback:
                    c[0](item, *c[1])
            except Exception, e:
                print e.message
        elif n == 1 and statusChangedCallback:
            try:
                for c in statusChangedCallback:
                    c[0](item, *c[1])
            except Exception, e:
                print e.message
        elif n == 2 and countChangedCallback:
            try:
                for c in countChangedCallback:
                    c[0](item, *c[1])
            except Exception, e:
                print e.message
        elif n == 3 and createCallback:
            try:
                for c in createCallback:
                    c[0](item, *c[1])
            except Exception, e:
                print e.message

    def getValue(self):
        return self.__value

    def getStatus(self):
        return self.__status

    def getType(self):
        return self.__type

    def getCount(self):
        return self.__count

    def getPos(self):
        return self.__pos

    def getParent(self):
        return self.__parent

    def getDirPath(self):
        return self.__dirPath

    def getNodePath(self):
        return self.__nodePath

    def pkg(self, path, pkgedFilePathList):
        if self.__type in (pkgItemType.FILE, pkgItemType.DIR):
            if self.getParent().getStatus() != pkgStatus.PKGED:
                pkgPath = os.path.join(path, '/'.join(self.getParent().__nodePath.split('.')), os.path.basename(self.getDirPath()))
                if not os.path.exists(pkgPath):
                    try:
                        os.makedirs(pkgPath)
                    except Exception, e:
                        print e.message
                try:
                    shutil.copy(os.path.join(self.__dirPath, self.__value), os.path.join(pkgPath, self.__value))
                    self.__status = pkgStatus.PKGED
                    self.callback(self, 1)
                except Exception, e:
                    print e.message
        elif self.__type == pkgItemType.NODE:
            pkgPath = os.path.join(path, '/'.join(self.__nodePath.split('.')))
            filePath = os.path.join(pkgPath, os.path.basename(os.path.dirname(self.__dirPath)), os.path.basename(self.__dirPath)).replace('\\', '/')
            if self.__dirPath not in pkgedFilePathList:
                pkgedFilePathList[self.__dirPath] = filePath
            else:
                filePath = pkgedFilePathList[self.__dirPath]
                self.__status = pkgStatus.PKGED
            n = nuke.toNode(self.__nodePath)
            for nodeClass, knob, conditionKnob, conditionKnobValue in searchNodes:
                if n.Class() == nodeClass:
                    n[knob].setValue(filePath)
        elif self.__type == pkgItemType.SPACEROOT:
            pkgPath = os.path.join(path, os.path.basename(self.getDirPath()))
            if not os.path.exists(pkgPath):
                try:
                    os.makedirs(pkgPath)
                except Exception, e:
                    print e.message
            try:
                nuke.scriptSaveAs(os.path.join(path, self.__value))
                self.__status = pkgStatus.PKGED
                self.callback(self, 1)
            except Exception, e:
                print e.message
        else:
            print 'item %s is not a file or dir, set type to file or dir first.' % self.__value


class pkgProjGUI(QtGuiWidgets.QWidget):
    def __init__(self):
        super(pkgProjGUI, self).__init__()
        self.init()

    def getNukeWindow(self):
        app = QtCore.QCoreApplication.instance()
        for w in app.topLevelWidgets():
            if w.metaObject().className() == 'Foundry::UI::DockMainWindow':
                return w

    def init(self):
        self.setParent(self.getNukeWindow())
        self.setWindowTitle('nuke 打包工具')
        self.resize(1000, 500)
        self.setWindowFlags(QtCore.Qt.Tool)
        self.mainLayout = QtGuiWidgets.QVBoxLayout()
        self.setLayout(self.mainLayout)

        # path widget
        self.pathFrame = QtGuiWidgets.QFrame()
        self.pathLayout = QtGuiWidgets.QHBoxLayout()
        self.pathLabel = QtGuiWidgets.QLabel('打包路径')
        self.pathField = QtGuiWidgets.QLineEdit('请输入打包路径')
        self.pathBrowserButton = QtGuiWidgets.QPushButton('浏览')
        self.pathBrowserButton.clicked.connect(self.browserPath)
        self.pathLayout.addWidget(self.pathLabel)
        self.pathLayout.addWidget(self.pathField)
        self.pathLayout.addWidget(self.pathBrowserButton)
        self.pathFrame.setLayout(self.pathLayout)

        # update list
        self.updateButtonFrame = QtGuiWidgets.QFrame()
        self.updateButtonLayout = QtGuiWidgets.QHBoxLayout()
        self.updateButtonFrame.setLayout(self.updateButtonLayout)
        self.updateButton = QtGuiWidgets.QPushButton('刷新')
        self.updateButtonLayout.addWidget(self.updateButton)

        # nodeClass, nodeName, files treeView
        self.fileFrame = QtGuiWidgets.QFrame()
        self.fileLayout = QtGuiWidgets.QVBoxLayout()
        self.fileFrame.setLayout(self.fileLayout)
        self.fileTreeWidget = QtGuiWidgets.QTreeWidget()
        self.fileTreeWidget.setColumnCount(2)
        self.fileTreeWidget.setHeaderLabels(['名称', '数量'])
        self.fileLayout.addWidget(self.fileTreeWidget)
        self.fileTreeWidget.setColumnWidth(0, 800)

        # infomation of node, files
        self.infoFrame = QtGuiWidgets.QFrame()
        self.infoLayout = QtGuiWidgets.QHBoxLayout()
        self.infoFrame.setLayout(self.infoLayout)
        self.infoNodeCountLabel = QtGuiWidgets.QLabel('节点总数:')
        self.infoFileCountLabel = QtGuiWidgets.QLabel('文件总数:')
        self.infoCopyedFileCountLabel = QtGuiWidgets.QLabel('已复制:')
        self.infoLayout.addWidget(self.infoNodeCountLabel)
        self.infoLayout.addWidget(self.infoFileCountLabel)
        self.infoLayout.addWidget(self.infoCopyedFileCountLabel)

        self.fileLayout.addWidget(self.infoFrame)

        # package button
        self.packageFrame = QtGuiWidgets.QFrame()
        self.packageLayout = QtGuiWidgets.QHBoxLayout()
        self.packageFrame.setLayout(self.packageLayout)
        self.packageButton = QtGuiWidgets.QPushButton('打包')
        self.packageLayout.addWidget(self.packageButton)

        # add frames to main layout
        self.mainLayout.addWidget(self.pathFrame)
        self.mainLayout.addWidget(self.updateButtonFrame)
        self.mainLayout.addWidget(self.fileFrame)
        self.mainLayout.addWidget(self.packageButton)

    def setPkgPath(self, path):
        self.pathField.setText(unitePath(path))

    def browserPath(self):
        dirPath = QtGuiWidgets.QFileDialog.getExistingDirectory(None, 'Package Directory Path', QtCore.QDir.homePath(), QtGuiWidgets.QFileDialog.ShowDirsOnly)
        if dirPath:
            self.setPkgPath(dirPath)

    def updateTreeView(self, item):
        if isinstance(item, pkgItem):
            qitem = QtGuiWidgets.QTreeWidgetItem()
            qitem.setText(0, item.getValue())
            qitem.setText(1, str(item.getCount()))
            if item.getType() == pkgItemType.SPACEROOT:
                self.fileTreeWidget.addTopLevelItem(qitem)
            elif item.getType() == pkgItemType.SPACE:
                self.fileTreeWidget.topLevelItem(0).insertChild(item.getPos(), qitem)
            elif item.getType() == pkgItemType.NODECLASS:
                self.fileTreeWidget.topLevelItem(0).child(item.getParent().getPos()).insertChild(item.getPos(), qitem)
            elif item.getType() == pkgItemType.NODE:
                self.fileTreeWidget.topLevelItem(0).child(item.getParent().getParent().getPos()).child(item.getParent().getPos()).insertChild(item.getPos(), qitem)
            elif item.getType() in (pkgItemType.DIR, pkgItemType.FILE):
                self.fileTreeWidget.topLevelItem(0).child(item.getParent().getParent().getParent().getParent().getPos()).child(item.getParent().getParent().getPos()).child(item.getParent().getPos()).insertChild(item.getPos(), qitem)
        else:
            print 'TypeError: item need pkgItem, but recevie a %s.' % type(item)

    def updateItemCount(self, item):
        if isinstance(item, pkgItem):
            if item.getType() == pkgItemType.SPACEROOT:
                self.fileTreeWidget.topLevelItem(0).setText(1, str(item.getCount()))
            elif item.getType() == pkgItemType.SPACE:
                self.fileTreeWidget.topLevelItem(0).child(item.getPos()).setText(1, str(item.getCount()))
            elif item.getType() == pkgItemType.NODECLASS:
                self.fileTreeWidget.topLevelItem(0).child(item.getParent().getPos()).child(item.getPos()).setText(1, str(item.getCount()))
            elif item.getType() == pkgItemType.NODE:
                self.fileTreeWidget.topLevelItem(0).child(item.getParent().getParent().getPos()).child(item.getParent().getPos()).child(item.getPos()).setText(1, str(item.getCount()))
            elif item.getType() in (pkgItemType.DIR, pkgItemType.FILE):
                self.fileTreeWidget.topLevelItem(0).child(item.getParent().getParent().getParent().getPos()).child(item.getParent().getParent().getPos()).child(item.getParent().getPos()).child(item.getPos()).setText(1, str(item.getCount()))
        else:
            print 'TypeError: item need pkgItem, but recevie a %s.' % type(item)

    def clearTree(self):
        self.fileTreeWidget.clear()


class pkgProj(object):
    __perNodeClassCallback = ()
    __perNodeFilePathCallback = ()
    __perFileCallback = ()
    __isGettingFiles = False
    __spaceRoot = None
    __pkgedFilePath = {}

    def printRootTree(self):
        print self.__spaceRoot
        for idr, r in enumerate(self.__spaceRoot.children()):
            print '├─' + r.getValue()
            for idi, i in enumerate(r.children()):
                print '│ ├─' + i.getValue()
                for idj, j in enumerate(i.children()):
                    print '│ │ ├─' + j.getValue()
                    for idn, n in enumerate(j.children()):
                        print '│ │ │ ├─' + n.getValue()

    def getFiles(self):
        if self.__isGettingFiles:
            print 'i am getting files, drink a coffee.'
            return
        if not nuke.root().name():
            print 'save project first.'
            return
        self.__isGettingFiles = True
        print 'start getting files.'
        # start get files callback
        self.callback(self, 6)
        # 初始化根 spaceRoot
        self.__spaceRoot = pkgItem(value=os.path.basename(nuke.root()['name'].value()), status=pkgStatus.NORMAL, itemtype=pkgItemType.SPACEROOT)
        self.__spaceRoot.setDirPath(os.path.dirname(nuke.root()['name'].value()))
        # spaceRootCallback
        self.callback(self.__spaceRoot, 0)
        for spaces in self.getSpaces():
            for space in spaces:
                sp = pkgItem(parent=self.__spaceRoot, value=space, status=pkgStatus.NORMAL, itemtype=pkgItemType.SPACE)
                sp.setNodePath(space)
                # perSpaceCallback
                self.callback(sp, 2)
                self.__spaceRoot.appendItem(sp)
                self.getFilesInSpace(sp)
        self.__isGettingFiles = False
        print 'get files complet.'
        return

    def getFilesInSpace(self, spaceItem):
        global searchNodes
        # perNodeClassCallback
        callbackType = 2
        for index, node in enumerate(searchNodes):
            pi = pkgItem(parent=spaceItem, value=node[0], status=pkgStatus.NORMAL, itemtype=pkgItemType.NODECLASS, pos=index)
            pi.setNodePath('.'.join((spaceItem.getNodePath(), pi.getValue())))
            self.callback(pi, callbackType)
            spaceItem.appendItem(pi)
            self.getNodeFilePath(pi, node[1], node[2], node[3])

    def getNodeFilePath(self, nodeClassItem, knob, conditionKnob=None, conditionValue=None):
        # perNodeFilePathCallback
        callbackType = 3
        nodes = [n for n in nuke.toNode(nodeClassItem.getParent().getNodePath()).nodes() if n.Class() == nodeClassItem.getValue()]
        for index, node in enumerate(nodes):
            if node.knob(knob) and (conditionKnob is None or (node.knob(conditionKnob) and node[conditionKnob].getValue() is conditionValue)):
                path = node[knob].getValue()
                pi = pkgItem(parent=nodeClassItem, value=node.name(), status=pkgStatus.NORMAL, itemtype=pkgItemType.NODE, pos=index)
                pi.setDirPath(node[knob].value())
                pi.setNodePath('.'.join((nodeClassItem.getParent().getNodePath(), node.name())))
                self.callback(pi, callbackType)
                nodeClassItem.appendItem(pi)
                self.pathAnalysis(pi, path)

    def pathAnalysis(self, nodePathItem, path):
        # means this function used to get file one by one, so call perFileCallback.
        callbackType = 4
        bn = os.path.basename(path)
        pdir = os.path.dirname(path)
        pattern = re.compile(r'^(.*)\.?((#+)|%(\d*)d)\.?(\w+)$')
        result = pattern.match(bn)
        if os.path.exists(path):
            if os.path.isdir(path):
                pi = pkgItem(parent=nodePathItem, value=bn, status=pkgStatus.NORMAL, itemtype=pkgItemType.DIR, count=1)
                pi.setDirPath(pdir)
            else:
                pi = pkgItem(parent=nodePathItem, value=bn, status=pkgStatus.NORMAL, itemtype=pkgItemType.FILE, count=1)
                pi.setDirPath(pdir)
            self.callback(pi, callbackType)
            nodePathItem.appendItem(pi)
        elif not os.path.exists(pdir):
            pi = pkgItem(parent=nodePathItem, value=bn, status=pkgStatus.NOEXISTS, itemtype=pkgItemType.FILE)
            pi.setDirPath(pdir)
            self.callback(pi, callbackType)
            nodePathItem.appendItem(pi)
        elif result:
            numLenth = (result.groups()[2] and len(result.groups()[2])) or (result.groups()[1] and ((result.groups()[3] and int(result.groups()[3])) or 1))
            if result:
                fn = 0
                newPattern = re.compile(result.groups()[0] + r'\.?(\d{%d,})' % numLenth + r'\.?' + result.groups()[4] + '$')
                for obj in os.listdir(pdir):
                    result = newPattern.match(obj)
                    if result and (len(result.groups()[0]) == numLenth or len(result.groups()[0]) > numLenth and not result.groups()[0].startswith('0')):
                        pi = pkgItem(parent=nodePathItem, value=obj, status=pkgStatus.NORMAL, itemtype=pkgItemType.FILE, count=1, pos=fn)
                        pi.setDirPath(pdir)
                        self.callback(pi, callbackType)
                        nodePathItem.appendItem(pi)
                        fn += 1
            if fn == 0:
                pi = pkgItem(parent=nodePathItem, value=bn, status=pkgStatus.NOEXISTS, itemtype=pkgItemType.FILE)
                pi.setDirPath(pdir)
                self.callback(pi, callbackType)
                nodePathItem.appendItem(pi)
        else:
            pi = pkgItem(parent=nodePathItem, value=bn, status=pkgStatus.NOEXISTS, itemtype=pkgItemType.FILE)
            pi.setDirPath(pdir)
            self.callback(pi, callbackType)
            nodePathItem.appendItem(pi)

    def getSpaces(self):
        spaces = ['root']
        while len(spaces) > 0:
            yield spaces
            spaces = ['.'.join((s, n.name())) for s in spaces for n in nuke.toNode(s).nodes() if n.Class() == 'Group']

    def walkItems(self):
        childrens = [self.__spaceRoot]
        while childrens:
            yield childrens
            childrens = [j for i in childrens for j in i.children()]

    def pkgItems(self, path):
        if os.path.isdir(path):
            for items in self.walkItems():
                for index, item in enumerate(items):
                    item.pkg(path, self.__pkgedFilePath)
        else:
            print 'path: %s is not exists.' % path

    def callback(self, item, n):
        '''
        n value:
            0: spaceRoot
            1: space
            2: nodeclass
            3: nodefilepath
            4: filepath
            5: package file
            6: start get files
        '''
        global perNodeClassCallback
        global perNodeFilePathCallback
        global perFileCallback
        global perSpaceCallback
        global perPkgFileCallback
        global startGetFilesCallback
        global spaceRootC
        if n == 0 and spaceRootCallback:
            try:
                for c in spaceRootCallback:
                    c[0](item, *c[1])
            except Exception, e:
                print e.message
        elif n == 1 and perSpaceCallback:
            try:
                for c in perSpaceCallback:
                    c[0](item, *c[1])
            except Exception, e:
                print e.message
        elif n == 2 and perNodeClassCallback:
            try:
                for c in perNodeClassCallback:
                    c[0](item, *c[1])
            except Exception, e:
                print e.message
        elif n == 3 and perNodeFilePathCallback:
            try:
                for c in perNodeFilePathCallback:
                    c[0](item, *c[1])
            except Exception, e:
                print e.message
        elif n == 4 and perFileCallback:
            try:
                for c in perFileCallback:
                    c[0](item, *c[1])
            except Exception, e:
                print e.message
        elif n == 5 and perPkgFileCallback:
            try:
                for c in perPkgFileCallback:
                    c[0](item, *c[1])
            except Exception, e:
                print e.message
        elif n == 6 and startGetFilesCallback:
            try:
                for c in startGetFilesCallback:
                    c[0](item, *c[1])
            except Exception, e:
                print e.message


class pkgMain(object):
    def __init__(self):
        self.ypkg = pkgProj()
        self.ypkgGUI = pkgProjGUI()
        self.setCallback()
        self.connectButton()

    def show(self):
        self.ypkgGUI.show()

    def setCallback(self):
        spaceRootCallback.append((self.ypkgGUI.updateTreeView, ()))
        perSpaceCallback.append((self.ypkgGUI.updateTreeView, ()))
        perNodeClassCallback.append((self.ypkgGUI.updateTreeView, ()))
        perNodeFilePathCallback.append((self.ypkgGUI.updateTreeView, ()))
        perFileCallback.append((self.ypkgGUI.updateTreeView, ()))
        countChangedCallback.append((self.ypkgGUI.updateItemCount, ()))

    def connectButton(self):
        self.ypkgGUI.updateButton.clicked.connect(self.updateButtonFun)
        self.ypkgGUI.packageButton.clicked.connect(self.pkgButtonFun)

    def updateButtonFun(self):
        self.ypkgGUI.clearTree()
        thread.start_new_thread(self.ypkg.getFiles, ())

    def pkgButtonFun(self):
        pkgPath = self.ypkgGUI.pathField.text()
        self.ypkg.pkgItems(pkgPath)


if __name__ == '__main__':
    test = pkgMain()
    test.show()
