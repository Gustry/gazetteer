import unittest


from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from qgis.core import QgsProject, QgsPointXY
from qgis.utils import plugins, iface
from PyQt5.QtTest import QTest
from qgis.gui import QgsMapTool

from utils.database import Database
from utils.test_data_handler import TestDataHandler


class TestUi(unittest.TestCase):
    """
    Just test UI elements. No data requests
    """

    @classmethod
    def setUpClass(cls):
        """
        Runs at TestCase init.
        """

        # insert required sys_codes to allow new feature creation
        test_data_handler = TestDataHandler()
        test_data_handler.insert_sys_codes()

        # Start plugin
        if not plugins.get("NZGBplugin"):
            pass
        else:
            cls.gazetteer_plugin = plugins.get("NZGBplugin")
            cls.gazetteer_plugin._runaction.trigger()

    @classmethod
    def tearDownClass(cls):
        """
        runs at TestCase teardown.
        """
        # removed required sys_codes to allow new feature creation

        test_data_handler = TestDataHandler()
        test_data_handler.delete_sys_codes()

    def setUp(cls):
        """
        Runs before each test.
        """
        pass
        # todo// ensure docket widget is on the correct tab

    def tearDown(cls):
        """
        Runs after each test
        """
        iface.dlg_create_new.uFeatName.setText("")


    def trigger_new_feature_dlg(self, x=174.76318, y=-41.28338):
        """
        
        """
        widget = iface.mapCanvas().viewport()
        canvas_point = QgsMapTool(iface.mapCanvas()).toCanvasCoordinates
        QTest.mouseClick(
            widget, Qt.LeftButton, pos=canvas_point(QgsPointXY(x, y)), delay=0
        )
        QTest.qWait(1000)

    def close_new_feature_dlg(self):
        QTest.qWait(1000)
        iface.dlg_create_new.close()

    def test_new_feature_dlg(self):
        """
        Test new feature dialog opens on map canvas click
        """

        # Mimic user selecting new feature tool
        self.gazetteer_plugin._newfeat.trigger()
        self.trigger_new_feature_dlg()
        self.assertEquals(iface.dlg_create_new.uFeatName.text(), "")
        self.close_new_feature_dlg()

    def test_new_feature_dlg(self):
        """
        Test new feature dialog opens on map canvas click
        """

        # Mimic user selecting new feature tool
        self.gazetteer_plugin._newfeat.trigger()
        self.trigger_new_feature_dlg()
        self.assertEquals(iface.dlg_create_new.uFeatName.text(), "")
        self.close_new_feature_dlg()

    def test_new_feature_dlg_name_missing(self):
        """
        Test new feature dialog opens throws and error to the
        user when no name is provided
        """

        self.gazetteer_plugin._newfeat.trigger()
        self.trigger_new_feature_dlg()
        iface.dlg_create_new.accept()
        QTest.qWait(1000)

        # MessageBar is level WARNING
        self.assertEqual(iface.messageBar().currentItem().level(), 2)
        self.assertEqual(
            iface.messageBar().currentItem().children()[2].toPlainText(),
            "New feature errors: You must enter a name for the new feature",
        )
        iface.messageBar().clearWidgets()
        self.close_new_feature_dlg()

    def test_invalid_lon_not_in_range(self):
        self.gazetteer_plugin._newfeat.trigger()
        # QTimer.singleShot(0, self.trigger_new_feature_dlg)
        self.trigger_new_feature_dlg()
        QTest.qWait(1000)
        iface.dlg_create_new.uFeatName.setText("test123")
        iface.dlg_create_new.uLongitude.setText("-42")
        iface.dlg_create_new.accept()

        # MessageBar is level WARNING
        self.assertEqual(iface.messageBar().currentItem().level(), 2)
        self.assertEqual(
            iface.messageBar().currentItem().children()[2].toPlainText(),
            "New feature errors: The longitude must be in the range 0 to 360 degrees",
        )
        iface.messageBar().clearWidgets()
        self.close_new_feature_dlg()

    def test_invalid_geom_lat_lon(self):
        self.gazetteer_plugin._newfeat.trigger()
        self.trigger_new_feature_dlg(600, 42.576)
        iface.dlg_create_new.uFeatName.setText("test123")

        # MessageBar is level WARNING
        self.assertEqual(iface.messageBar().currentItem().level(), 2)
        self.assertEqual(
            iface.messageBar().currentItem().children()[2].toPlainText(),
            "Gazetter location error: The location selected for the new feature is not at a valid latitude and longitude",
        )
        iface.messageBar().clearWidgets()
        # self.close_new_feature_dlg()

    def test_new_feature(self):
        feature_name = "Ashburton Folks"
        feature_x = 169.82699229328563
        feature_y = -44.200093724057346
        self.trigger_new_feature_dlg(feature_x,feature_y )
        iface.dlg_create_new.uFeatName.setText(feature_name)

        # Check the a new dockwidget tab has been added with the features name "test"
        self.gazetteer_plugin._editor.findChildren(QTabBar)[1].tabText(
            self.gazetteer_plugin._editor.findChildren(QTabBar)[1].currentIndex()
        ) = feature_name


def suite():
    suite = unittest.TestSuite()
    suite.addTests(unittest.makeSuite(UnitLevel, "test"))
    return suite


def run_tests():
    unittest.TextTestRunner(verbosity=3).run(suite())
