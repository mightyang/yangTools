#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File              : ytEnvInit.py
# Author            : yang <mightyang@hotmail.com>
# Date              : 09.03.2019
# Last Modified Date: 10.03.2019
# Last Modified By  : yang <mightyang@hotmail.com>

import platform
import os
import sys


# set environment sperator
envSperator = ':'
if platform.system() == 'Windows':
    envSperator = ';'


def appendEnv(env, value):
    global envSperator
    if env in os.environ:
        valList = os.environ[env].split(envSperator)
    else:
        valList = []
    if value not in valList:
        valList.append(value)
    os.environ[env] = envSperator.join(valList)


def updateEnv():
    global envSperator
    ppList = sys.path
    if 'YT_PATH' in os.environ:
        ytPathList = os.environ['YT_PATH'].split(envSperator)
        ppList.extend(ytPathList)
    if 'YT_SCRIPT_PATH' in os.environ:
        ytPluginPathList = os.environ['YT_SCRIPT_PATH'].split(envSperator)
        ppList.extend(ytPluginPathList)
    if 'YT_DATA_PATH' in os.environ:
        ytDataPathList = os.environ['YT_DATA_PATH'].split(envSperator)
        ppList.extend(ytDataPathList)
    os.environ['PYTHONPATH'] = envSperator.join(list(set(ppList)))


# add YT_PATH environment which is yangTool's root path
preEnv = {'YT_PATH': os.path.dirname(os.path.abspath(__file__)),
          'YT_SCRIPT_PATH': os.path.join(os.path.dirname(os.path.abspath(__file__)), 'scripts'),
          'YT_DATA_PATH': os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
          }

for env, val in preEnv.items():
    appendEnv(env, val)
updateEnv()

del appendEnv, updateEnv, preEnv, envSperator
