#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File              : ytVersion.py
# Author            : yang <mightyang@hotmail.com>
# Date              : 07.03.2019
# Last Modified Date: 07.03.2019
# Last Modified By  : yang <mightyang@hotmail.com>


class ytVersion():
    major = 0
    minor = 0
    patch = 0

    def __init__(self, major=0, minor=0, patch=0):
        self.major = major
        self.minor = minor
        self.patch = patch

    def setMajor(self, major):
        self.major = major

    def setMinor(self, minor):
        self.minor = minor

    def setPatch(self, patch):
        self.patch = patch

    def getVersion(self):
        return '.'.join((self.major, self.minor, self.patch))


