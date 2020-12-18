# -*- coding: utf-8 -*-
"""
/***************************************************************************
 SWAV_BIODialog
                                 A QGIS plugin
 This plugin allows to obtain the biomass in rocky beach
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                             -------------------
        begin                : 2020-09-23
        git sha              : $Format:%H$
        copyright            : (C) 2020 by Projeto SWAV
        email                : liaduarte@fc.up.pt
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

import os

from qgis.PyQt import uic
from qgis.PyQt import QtWidgets
from qgis.core import *
from qgis.gui import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from qgis.core import *
from qgis.utils import *
from qgis.core import Qgis

# This loads your .ui file so that PyQt can populate your plugin with the elements from Qt Designer
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'swav_bio_dialog_base.ui'))


class SWUAV_BIODialog(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        """Constructor."""
        super(SWUAV_BIODialog, self).__init__(parent)
        # Set up the user interface from Designer through FORM_CLASS.
        # After self.setupUi() you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        self.widget.show()
        self.widget.setCanvasColor(Qt.white)
        self.widget.enableAntiAliasing(True)


class RectangleMapTool(QgsMapToolEmitPoint):
    rect_created = pyqtSignal(QgsRectangle)
    def __init__(self, canvas):
        self.canvas = canvas
        QgsMapToolEmitPoint.__init__(self, self.canvas)
        self.rubberBand = QgsRubberBand(self.canvas, True)
        self.rubberBand.setColor(Qt.red)
        self.rubberBand.setWidth(1)

        self.points = []
        self.finished = False
        self.poly_bbox = False
        self.double_click_flag = False


        self.reset()

    def reset(self):
        #self.startPoint = self.endPoint = None
        #self.isEmittingPoint = False
        self.rubberBand.reset(True)
        self.poly_bbox = False
        self.points.clear()

    #new
    def keyPressEvent(self,e):
        #pressing escape resets the canvas. pressing enter connects the polygon
        if (e.key()==16777216):
            self.reset()
        if (e.key()==16777220):
            self.finishPolygon()

    #new
    def canvasDoubleClickEvent(self,e):
        #finishes the polygon on double click
        self.double_click_flag = True
        self.finishPolygon()

    # def canvasPressEvent(self, e):
    #     self.startPoint = self.toMapCoordinates(e.pos())
    #     self.endPoint = self.startPoint
    #     self.isEmittingPoint = True
    #     self.showRect(self.startPoint, self.endPoint)

    def canvasReleaseEvent(self, e):
        #activated when user clicks on the canvas. gets coordinates, draws them on the map and adds to the list of points
        if self.double_click_flag:
            self.double_click_flag = False
            return

        #if the finished flag is activated, the canvas will be reset for a new polygon
        if self.finished:
            self.reset()
            self.finished = False

        self.click_point = self.toMapCoordinates(e.pos())

        self.rubberBand.addPoint(self.click_point, True)
        self.points.append(self.click_point)
        self.rubberBand.show()

    def finishPolygon(self):
        # Activated by user or when the map window is closed without connecting
        #     the polygon. Makes the polygon valid by making first and last point
        #     the same. This is reflected visually. Up until now the user has been
        #     drawing a line: a polygon is created and shown on the map
        # nothing will happen if the code below has already been ran
        if self.finished:
            return

        # connecting the polygon is valid if there's already at least 3 points
        elif len(self.points)>2:
            first_point = self.points[0]
            self.points.append(first_point)
            self.rubberBand.closePoints()
            self.rubberBand.addPoint(first_point, True)
            self.finished = True
            # a polygon is created and added to the map for visual purposes
            map_polygon = QgsGeometry.fromPolygonXY([self.points])
            self.rubberBand.setToGeometry(map_polygon)
            # get the bounding box of this new polygon
            self.poly_bbox = self.rubberBand.asGeometry().boundingBox()
        else:
            self.finished = True

    def getPoints(self):
        # Returns list of PointXY geometries, i.e. the polygon in list form
        self.rubberBand.reset(True)
        return self.points

        # self.isEmittingPoint = False
        # r = self.rectangle()
        # if r is not None:
        #     self.rect_created.emit(r)
            #QMessageBox.about(self.dlg, "teste", str('ola'))
          # print("Rectangle:", r.xMinimum(),
          #       r.yMinimum(), r.xMaximum(), r.yMaximum()
          #      )
    #
    # def canvasMoveEvent(self, e):
    #     if not self.isEmittingPoint:
    #       return
    #
    #     self.endPoint = self.toMapCoordinates(e.pos())
    #
    #     self.showRect(self.startPoint, self.endPoint)
    #
    # def showRect(self, startPoint, endPoint):
    #     self.rubberBand.reset()
    #     if startPoint.x() == endPoint.x() or startPoint.y() == endPoint.y():
    #       return
    #
    #     point1 = QgsPointXY(startPoint.x(), startPoint.y())
    #     point2 = QgsPointXY(startPoint.x(), endPoint.y())
    #     point3 = QgsPointXY(endPoint.x(), endPoint.y())
    #     point4 = QgsPointXY(endPoint.x(), startPoint.y())
    #     point5 = point1
    #
    #     self.rubberBand.addPoint(point1, False)
    #     self.rubberBand.addPoint(point2, False)
    #     self.rubberBand.addPoint(point3, False)
    #     self.rubberBand.addPoint(point4, False)
    #     self.rubberBand.addPoint(point5, True)
    #     # true to update canvas
    #     self.rubberBand.show()
    #
    #
    # def rectangle(self):
    #     if self.startPoint is None or self.endPoint is None:
    #       return None
    #     elif (self.startPoint.x() == self.endPoint.x() or \
    #           self.startPoint.y() == self.endPoint.y()):
    #       return None
    #
    #       return QgsRectangle(self.startPoint, self.endPoint)
    #
    #
    # def deactivate(self):
    #     QgsMapTool.deactivate(self)
    #     self.deactivated.emit()
