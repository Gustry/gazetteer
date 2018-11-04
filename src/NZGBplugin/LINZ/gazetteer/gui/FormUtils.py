################################################################################
#
# Copyright 2015 Crown copyright (c)
# Land Information New Zealand and the New Zealand Government.
# All rights reserved
#
# This program is released under the terms of the new BSD license. See the 
# LICENSE file for more information.
#
################################################################################


from builtins import str
import os.path

from PyQt5.QtCore import *
from PyQt5.QtGui import *

from LINZ.gazetteer.gui.Controller import Controller
from LINZ.gazetteer.Model import SystemCode
from LINZ.Widgets import QtUtils

def populateCodeCombo( combo, code_group, showAny=False, special=None, category=None ):
    codes = SystemCode.codeGroup( code_group )
    rows = [(c.code, c.value) for c in codes if category==None or c.category==category]
    rows.sort( key=lambda x:str(x[1]).upper() )
    if special:
        rows[0:0]=special
    if showAny:
        rows.insert(0,(None, '(Any)'))
    QtUtils.populateCombo(combo,rows)
    combo.setCurrentIndex(0)
