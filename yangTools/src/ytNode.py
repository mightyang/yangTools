#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File              : srcytNode.py
# Author            : yang <mightyang@hotmail.com>
# Date              : 04.03.2019
# Last Modified Date: 07.03.2019
# Last Modified By  : yang <mightyang@hotmail.com>

from ytLoggingSettings import *
from ytVariables import ytVariables
from ytCallbacks import ytCallbacks


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

    def clearChildren(self):
        self._children = []

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


