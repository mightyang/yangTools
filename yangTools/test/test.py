#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File              : test.py
# Author            : yang <mightyang@hotmail.com>
# Date              : 08.02.2019
# Last Modified Date: 08.02.2019
# Last Modified By  : yang <mightyang@hotmail.com>


from PySide2 import QtGui, QtWidgets, QtCore
import sys


class yTreeView(QtWidgets.QTreeView):
    def __init__(self, parent=None):
        super(yTreeView, self).__init__(parent)
        self.__parent = parent
        self.init()

    def init(self):
        self.mode = QtGui.QStandardItemModel(0, 3, self.__parent)
        self.setModel(self.mode)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    data = [1, 2, 3, 4]
    listWidget = QtWidgets.QListWidget()
    listWidget.addItems(data)
    listWidget.show()
    sys.exit(app.exec_())
