#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File              : srcytCallbacks.py
# Author            : yang <mightyang@hotmail.com>
# Date              : 04.03.2019
# Last Modified Date: 04.03.2019
# Last Modified By  : yang <mightyang@hotmail.com>


class ytCallbacks():
    ytNode_selectionChanged_callback = []
    ytNode_parentChanged_callback = []
    ytNode_nameChanged_callback = []
    ytNode_nodeChanged_callback = []
    ytNode_childCreated_callback = []
    ytNode_childDestroyed_callback = []

    gangModifier_start_callback = []
    gangModifier_stop_callback = []