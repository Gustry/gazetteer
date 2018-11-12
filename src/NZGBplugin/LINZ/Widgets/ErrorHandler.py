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
import sys

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets  import *

def handleException():
    type, value, traceback = sys.exc_info()
    if type == None:
        return
    QMessageBox.warning(QApplication.instance().activeWindow(),'Error',str(value))
