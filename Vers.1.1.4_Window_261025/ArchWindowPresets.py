# SPDX-License-Identifier: LGPL-2.1-or-later

# ***************************************************************************
# *                                                                         *
# *   Copyright (c) 2020 Yorik van Havre <yorik@uncreated.net>              *
# *                                                                         *
# *   This file is part of FreeCAD.                                         *
# *                                                                         *
# *   FreeCAD is free software: you can redistribute it and/or modify it    *
# *   under the terms of the GNU Lesser General Public License as           *
# *   published by the Free Software Foundation, either version 2.1 of the  *
# *   License, or (at your option) any later version.                       *
# *                                                                         *
# *   FreeCAD is distributed in the hope that it will be useful, but        *
# *   WITHOUT ANY WARRANTY; without even the implied warranty of            *
# *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU      *
# *   Lesser General Public License for more details.                       *
# *                                                                         *
# *   You should have received a copy of the GNU Lesser General Public      *
# *   License along with FreeCAD. If not, see                               *
# *   <https://www.gnu.org/licenses/>.                                      *
# *                                                                         *
# ***************************************************************************

import math

import FreeCAD

from FreeCAD import Vector
from draftutils.translate import translate


WindowPresets = [
    # 1) Fenster
    "Fixed",
    "Open 1-pane",
    "Open 2-pane",
    "Sash 2-pane",
    "Sliding 2-pane",
    "Sliding 4-pane",
    "Awning",
    "Arched window",
    "Oval fixed window",
    # 2) Öffnung
    "Opening only",
    # 3) Türen
    "Simple door",
    "Glass door",
    "Glassfilled door",
    "Arched Glass door",
    "Arched Glassfilled door",
]


def makeWindowPreset(windowtype, width, height, h1, h2, h3, w1, w2, o1, o2, placement=None):
    """makeWindowPreset(windowtype,width,height,h1,h2,h3,w1,w2,o1,o2,[placement]): makes a
    window object based on the given data. windowtype must be one of the names
    defined in Arch.WindowPresets"""

    if not FreeCAD.ActiveDocument:
        FreeCAD.Console.PrintError("No active document. Aborting\n")
        return

    def makeSketch(windowtype, width, height, h1, h2, h3, w1, w2, o1, o2):

        import Part
        import Sketcher

        width = float(width)
        height = float(height)
        h1 = float(h1)
        h2 = float(h2)
        h3 = float(h3)
        w1 = float(w1)
        w2 = float(w2)
        o1 = float(o1)
        o2 = float(o2)
        if width * height * h1 * h2 * w1 * w2 == 0:
            FreeCAD.Console.PrintError(
                "Width, Height, H1, H2, W1 and W2 parameters cannot be zero. Aborting\n"
            )
            return
        tol = h1 / 10
        gla = 10
        s = FreeCAD.ActiveDocument.addObject("Sketcher::SketchObject", "Sketch")

        def addRectangle(s, p1, p2, p3, p4):
            idx = s.GeometryCount
            s.addGeometry(Part.LineSegment(p1, p2))
            s.addGeometry(Part.LineSegment(p2, p3))
            s.addGeometry(Part.LineSegment(p3, p4))
            s.addGeometry(Part.LineSegment(p4, p1))
            s.addConstraint(Sketcher.Constraint("Coincident", idx, 2, idx + 1, 1))
            s.addConstraint(Sketcher.Constraint("Coincident", idx + 1, 2, idx + 2, 1))
            s.addConstraint(Sketcher.Constraint("Coincident", idx + 2, 2, idx + 3, 1))
            s.addConstraint(Sketcher.Constraint("Coincident", idx + 3, 2, idx, 1))
            s.addConstraint(Sketcher.Constraint("Horizontal", idx))
            s.addConstraint(Sketcher.Constraint("Horizontal", idx + 2))
            s.addConstraint(Sketcher.Constraint("Vertical", idx + 1))
            s.addConstraint(Sketcher.Constraint("Vertical", idx + 3))

        def addFrame(s, p1, p2, p3, p4, p5, p6, p7, p8):
            addRectangle(s, p1, p2, p3, p4)
            addRectangle(s, p5, p6, p7, p8)

        def simpleFrame(s, width, height, h1, h2, tol):
            p1 = Vector(h1 + tol, h1 + tol, 0)
            p2 = Vector(width - (h1 + tol), h1 + tol, 0)
            p3 = Vector(width - (h1 + tol), height - (h1 + tol), 0)
            p4 = Vector(h1 + tol, height - (h1 + tol), 0)
            p5 = Vector(h1 + h2, h1 + h2, 0)
            p6 = Vector(width - (h1 + h2), h1 + h2, 0)
            p7 = Vector(width - (h1 + h2), height - (h1 + h2), 0)
            p8 = Vector(h1 + h2, height - (h1 + h2), 0)
            addFrame(s, p1, p2, p3, p4, p5, p6, p7, p8)
            s.addConstraint(Sketcher.Constraint("DistanceX", 8, 1, 12, 1, h2))
            s.addConstraint(Sketcher.Constraint("DistanceY", 8, 1, 12, 1, h2))
            s.addConstraint(Sketcher.Constraint("DistanceX", 14, 1, 10, 1, h2))
            s.addConstraint(Sketcher.Constraint("DistanceY", 14, 1, 10, 1, h2))
            s.addConstraint(Sketcher.Constraint("DistanceX", 4, 1, 8, 1, tol))
            s.addConstraint(Sketcher.Constraint("DistanceY", 4, 1, 8, 1, tol))
            s.addConstraint(Sketcher.Constraint("DistanceX", 10, 1, 6, 1, tol))
            s.addConstraint(Sketcher.Constraint("DistanceY", 10, 1, 6, 1, tol))
            if h2 == h1:
                s.renameConstraint(39, "Frame5")
                s.renameConstraint(40, "Frame6")
                s.renameConstraint(42, "Frame7")
                s.renameConstraint(41, "Frame8")

        def outerFrame(s, width, height, h1, w1, o1):
            p1 = Vector(0, 0, 0)
            p2 = Vector(width, 0, 0)
            p3 = Vector(width, height, 0)
            p4 = Vector(0, height, 0)
            p5 = Vector(h1, h1, 0)
            p6 = Vector(width - h1, h1, 0)
            p7 = Vector(width - h1, height - h1, 0)
            p8 = Vector(h1, height - h1, 0)
            addFrame(s, p1, p2, p3, p4, p5, p6, p7, p8)
            s.addConstraint(Sketcher.Constraint("DistanceY", 1, height))
            s.addConstraint(Sketcher.Constraint("DistanceX", 0, width))
            s.renameConstraint(16, "Height")
            s.renameConstraint(17, "Width")
            s.addConstraint(Sketcher.Constraint("DistanceY", 6, 2, 2, 2, h1))
            s.addConstraint(Sketcher.Constraint("DistanceX", 2, 2, 6, 2, h1))
            s.addConstraint(Sketcher.Constraint("DistanceX", 4, 2, 0, 2, h1))
            s.addConstraint(Sketcher.Constraint("DistanceY", 0, 2, 4, 2, h1))
            s.renameConstraint(18, "Frame1")
            s.renameConstraint(19, "Frame2")
            s.renameConstraint(20, "Frame3")
            s.renameConstraint(21, "Frame4")
            s.addConstraint(Sketcher.Constraint("Coincident", 0, 1, -1, 1))
            return ["OuterFrame", "Frame", "Wire0,Wire1", str(w1 - w2) + "+V", "0.00+V"]

        def doorFrame(s, width, height, h1, w1, o1):
            p1 = Vector(0, 0, 0)
            p2 = Vector(width, 0, 0)
            p3 = Vector(width, height, 0)
            p4 = Vector(0, height, 0)
            p5 = Vector(h1, 0, 0)
            p6 = Vector(width - h1, 0, 0)
            p7 = Vector(width - h1, height - h1, 0)
            p8 = Vector(h1, height - h1, 0)
            addFrame(s, p1, p2, p3, p4, p5, p6, p7, p8)
            s.addConstraint(Sketcher.Constraint("DistanceY", 1, height))
            s.addConstraint(Sketcher.Constraint("DistanceX", 0, width))
            s.renameConstraint(16, "Height")
            s.renameConstraint(17, "Width")
            s.addConstraint(Sketcher.Constraint("DistanceY", 6, 2, 2, 2, h1))
            s.addConstraint(Sketcher.Constraint("DistanceX", 2, 2, 6, 2, h1))
            s.addConstraint(Sketcher.Constraint("DistanceX", 4, 2, 0, 2, h1))
            s.addConstraint(Sketcher.Constraint("DistanceY", 0, 2, 4, 2, 0.0))
            s.addConstraint(Sketcher.Constraint("Coincident", 0, 1, -1, 1))
            s.renameConstraint(18, "Frame1")
            s.renameConstraint(19, "Frame2")
            s.renameConstraint(20, "Frame3")
            return ["OuterFrame", "Frame", "Wire0,Wire1", str(w1 - w2) + "+V", "0.00+V"]
        
        def add_door_handle(s, tol, h1):
            ph_x = width - (h1 + tol) - 55 
            ph_y = tol + 1050
            s.addGeometry(Part.Circle(Vector(ph_x, ph_y, 0), Vector(0, 0, 1), 9.5))
            s.addConstraint(Sketcher.Constraint("DistanceX", 0, 1, s.GeometryCount - 1, 3, ph_x))
            s.renameConstraint(s.ConstraintCount - 1, "ph_x")
            s.addConstraint(Sketcher.Constraint("DistanceY", 0, 1, s.GeometryCount - 1, 3, ph_y))
            s.renameConstraint(s.ConstraintCount - 1, "ph_y")
            
        def add_arched_wire(s, width, height, h3):
            idx = s.GeometryCount
            p1, p2 = Vector(0, 0, 0), Vector(width, 0, 0)
            p3, p4, p5 = Vector(width, height, 0), Vector(width / 2, height + h3, 0), Vector(0, height, 0)

            s.addGeometry(Part.LineSegment(p1, p2))
            s.addGeometry(Part.LineSegment(p2, p3))
            s.addGeometry(Part.ArcOfCircle(p3, p4, p5))
            s.addGeometry(Part.LineSegment(p5, p1))
            s.addGeometry(Part.Point(p4))
            s.setConstruction(idx + 4, True)

            s.addConstraint(Sketcher.Constraint("Coincident", idx + 0, 2, idx + 1, 1))
            s.addConstraint(Sketcher.Constraint("Coincident", idx + 1, 2, idx + 2, 1))
            s.addConstraint(Sketcher.Constraint("Coincident", idx + 2, 2, idx + 3, 1))
            s.addConstraint(Sketcher.Constraint("Coincident", idx + 3, 2, idx + 0, 1))
            s.addConstraint(Sketcher.Constraint("Horizontal", idx + 0))
            s.addConstraint(Sketcher.Constraint("Vertical", idx + 1))
            s.addConstraint(Sketcher.Constraint("Vertical", idx + 3))
            s.addConstraint(Sketcher.Constraint("Horizontal", idx + 1, 2, idx + 3, 1))
            s.addConstraint(Sketcher.Constraint("PointOnObject", idx + 4, 1, idx + 2))
            return idx
        
        def apply_relative_arched_constraints(s, w_outer, w_inner, dist, lth):
            s.addConstraint(Sketcher.Constraint("DistanceX", w_outer, 1, w_inner, 1, dist))
            s.addConstraint(Sketcher.Constraint("DistanceX", w_inner, 2, w_outer, 2, dist))
            s.addConstraint(Sketcher.Constraint("DistanceY", w_outer, 1, w_inner, 1, lth))
            s.addConstraint(Sketcher.Constraint("Vertical", w_outer + 4, 1, w_inner + 4, 1))
            s.addConstraint(Sketcher.Constraint("DistanceY", w_inner + 4, 1, w_outer + 4, 1, dist))
            s.addConstraint(Sketcher.Constraint("Distance", w_inner + 3, 1, w_outer + 2, dist))

        def arched_outer_frame(s, width, height, h1, h3, w1, w2, o1):    
            wi0 = add_arched_wire(s, width, height, h3)
            wi1 = add_arched_wire(s, width, height, h3)         
            s.addConstraint(Sketcher.Constraint("Coincident", wi0, 1, -1, 1))
            s.addConstraint(Sketcher.Constraint("DistanceX", wi0, 1, wi0, 2, width))
            s.addConstraint(Sketcher.Constraint("DistanceY", wi0, 1, wi0 + 3, 1, height))
            s.addConstraint(Sketcher.Constraint("DistanceY", wi0 + 3, 1, wi0 + 4, 1, h3))
            s.addConstraint(Sketcher.Constraint("DistanceX", -1, 1, wi0 + 4, 1, width / 2))
            s.renameConstraint(s.ConstraintCount - 4, "Width")
            s.renameConstraint(s.ConstraintCount - 3, "Height")
            s.renameConstraint(s.ConstraintCount - 2, "h3")
            return wi0, wi1

        def arched_inner_frame(s, width, height, h1, h2, h3, w1, w2, tol, o1):
            wi1 = 5         
            wi2 = add_arched_wire(s, width, height, h3)
            wi3 = add_arched_wire(s, width, height, h3) 
            apply_relative_arched_constraints(s, wi1, wi2, tol, tol)
            apply_relative_arched_constraints(s, wi2, wi3, h2, h2)
            fw = str(w2)
            if w2 == w1:
                fw = "0.00+V"             
            return ["InnerFrame", "Frame", "Wire2,Wire3,Edge8,Mode1", fw, str(o2) + "+V"]

        if windowtype == "Fixed":
            wp = outerFrame(s, width, height, h1, w1, o1)
            wp.extend(["Glass", "Glass panel", "Wire1", str(w1 / gla), str(w1 / 2) + "+V"])

        elif windowtype == "Open 1-pane":
            wp = outerFrame(s, width, height, h1, w1, o1)
            simpleFrame(s, width, height, h1, h2, tol)
            fw = str(w2)
            if w2 == w1:
                fw = "0.00+V"
            wp.extend(["InnerFrame", "Frame", "Wire2,Wire3,Edge8,Mode1", fw, str(o2) + "+V"])
            wp.extend(["InnerGlass", "Glass panel", "Wire3", str(w2 / gla), str(o2 + w2 / 2) + "+V"])

        elif windowtype == "Open 2-pane":
            wp = outerFrame(s, width, height, h1, w1, o1)
            p1 = Vector(h1 + tol, h1 + tol, 0)
            p2 = Vector((width / 2) - tol, h1 + tol, 0)
            p3 = Vector((width / 2) - tol, height - (h1 + tol), 0)
            p4 = Vector(h1 + tol, height - (h1 + tol), 0)
            p5 = Vector(h1 + h2, h1 + h2, 0)
            p6 = Vector((width / 2) - h2, h1 + h2, 0)
            p7 = Vector((width / 2) - h2, height - (h1 + h2), 0)
            p8 = Vector(h1 + h2, height - (h1 + h2), 0)
            addFrame(s, p1, p2, p3, p4, p5, p6, p7, p8)
            p1 = Vector((width / 2) + tol, h1 + tol, 0)
            p2 = Vector(width - (h1 + tol), h1 + tol, 0)
            p3 = Vector(width - (h1 + tol), height - (h1 + tol), 0)
            p4 = Vector((width / 2) + tol, height - (h1 + tol), 0)
            p5 = Vector((width / 2) + h2, h1 + h2, 0)
            p6 = Vector(width - (h1 + h2), h1 + h2, 0)
            p7 = Vector(width - (h1 + h2), height - (h1 + h2), 0)
            p8 = Vector((width / 2) + h2, height - (h1 + h2), 0)
            addFrame(s, p1, p2, p3, p4, p5, p6, p7, p8)
            s.addConstraint(Sketcher.Constraint("DistanceY", 8, 1, 12, 1, h2))
            s.addConstraint(Sketcher.Constraint("DistanceX", 8, 1, 12, 1, h2))
            s.addConstraint(Sketcher.Constraint("DistanceX", 21, 2, 17, 2, h2))
            s.addConstraint(Sketcher.Constraint("DistanceY", 21, 2, 17, 2, h2))
            s.addConstraint(Sketcher.Constraint("DistanceX", 16, 1, 20, 1, h2))
            s.addConstraint(Sketcher.Constraint("DistanceX", 14, 1, 10, 1, h2))
            s.addConstraint(Sketcher.Constraint("Equal", 22, 14))
            s.addConstraint(Sketcher.Constraint("DistanceY", 8, 2, 16, 1, 0.0))
            s.addConstraint(Sketcher.Constraint("DistanceY", 10, 1, 18, 2, 0.0))
            s.addConstraint(Sketcher.Constraint("DistanceX", 4, 1, 8, 1, tol))
            s.addConstraint(Sketcher.Constraint("DistanceY", 4, 1, 8, 1, tol))
            s.addConstraint(Sketcher.Constraint("DistanceX", 6, 1, 18, 1, -tol))
            s.addConstraint(Sketcher.Constraint("DistanceY", 6, 1, 18, 1, -tol))
            s.addConstraint(Sketcher.Constraint("DistanceX", 9, 1, 19, 2, tol))
            s.addConstraint(Sketcher.Constraint("PointOnObject", 13, 2, 22))
            s.addConstraint(Sketcher.Constraint("PointOnObject", 20, 1, 12))
            if h1 == h2:
                s.renameConstraint(55, "Frame5")
                s.renameConstraint(56, "Frame6")
                s.renameConstraint(57, "Frame7")
                s.renameConstraint(58, "Frame8")
                s.renameConstraint(59, "Frame9")
                s.renameConstraint(60, "Frame10")
            fw = str(w2)
            if w2 == w1:
                fw = "0.00+V"
            wp.extend(["LeftFrame", "Frame", "Wire2,Wire3,Edge8,Mode1", fw, str(o2) + "+V"])
            wp.extend(["LeftGlass", "Glass panel", "Wire3", str(w2 / gla), str(o2 + w2 / 2) + "+V"])
            wp.extend(["RightFrame", "Frame", "Wire4,Wire5,Edge6,Mode2", fw, str(o2) + "+V"])
            wp.extend(["RightGlass", "Glass panel", "Wire5", str(w2 / gla), str(o2 + w2 / 2) + "+V"])

        elif windowtype == "Sash 2-pane":
            wp = outerFrame(s, width, height, h1, w1, o1)
            p1 = Vector(h1 + tol, h1 + tol, 0)
            p2 = Vector(width - (h1 + tol), h1 + tol, 0)
            p3 = Vector(width - (h1 + tol), (height / 2) - tol, 0)
            p4 = Vector(h1 + tol, (height / 2) - tol, 0)
            p5 = Vector(h1 + h2, h1 + h2, 0)
            p6 = Vector(width - (h1 + h2), h1 + h2, 0)
            p7 = Vector(width - (h1 + h2), (height / 2) - h2, 0)
            p8 = Vector(h1 + h2, (height / 2) - h2, 0)
            addFrame(s, p1, p2, p3, p4, p5, p6, p7, p8)
            p1 = Vector(h1 + tol, (height / 2) + tol, 0)
            p2 = Vector(width - (h1 + tol), (height / 2) + tol, 0)
            p3 = Vector(width - (h1 + tol), height - (h1 + tol), 0)
            p4 = Vector(h1 + tol, height - (h1 + tol), 0)
            p5 = Vector(h1 + h2, (height / 2) + h2, 0)
            p6 = Vector(width - (h1 + h2), (height / 2) + h2, 0)
            p7 = Vector(width - (h1 + h2), height - (h1 + h2), 0)
            p8 = Vector(h1 + h2, height - (h1 + h2), 0)
            addFrame(s, p1, p2, p3, p4, p5, p6, p7, p8)
            s.addConstraint(Sketcher.Constraint("DistanceY", 8, 1, 12, 1, h2))
            s.addConstraint(Sketcher.Constraint("DistanceX", 8, 1, 12, 1, h2))
            s.addConstraint(Sketcher.Constraint("DistanceX", 21, 2, 17, 2, h2))
            s.addConstraint(Sketcher.Constraint("DistanceY", 21, 2, 17, 2, h2))
            s.addConstraint(Sketcher.Constraint("DistanceY", 16, 2, 20, 1, h2))
            s.addConstraint(Sketcher.Constraint("DistanceY", 10, 2, 14, 2, -h2))
            s.addConstraint(Sketcher.Constraint("Equal", 23, 15))
            s.addConstraint(Sketcher.Constraint("DistanceX", 12, 1, 20, 1, 0.0))
            s.addConstraint(Sketcher.Constraint("DistanceX", 13, 2, 20, 2, 0.0))
            s.addConstraint(Sketcher.Constraint("DistanceX", 4, 1, 8, 1, tol))
            s.addConstraint(Sketcher.Constraint("DistanceY", 4, 1, 8, 1, tol))
            s.addConstraint(Sketcher.Constraint("DistanceX", 6, 1, 18, 1, -tol))
            s.addConstraint(Sketcher.Constraint("DistanceY", 6, 1, 18, 1, -tol))
            s.addConstraint(Sketcher.Constraint("DistanceY", 10, 1, 16, 1, tol))
            s.addConstraint(Sketcher.Constraint("PointOnObject", 9, 2, 17))
            s.addConstraint(Sketcher.Constraint("PointOnObject", 16, 1, 11))
            if h1 == h2:
                s.renameConstraint(55, "Frame5")
                s.renameConstraint(56, "Frame6")
                s.renameConstraint(57, "Frame7")
                s.renameConstraint(58, "Frame8")
                s.renameConstraint(59, "Frame9")
                s.renameConstraint(60, "F10")
                s.setExpression(".Constraints.F10", "-.Constraints.Frame5")
            fw = str(w2)
            if w2 == w1:
                fw = "0.00+V"
            wp.extend(["LowerFrame", "Frame", "Wire2,Wire3", fw, str(o2 + w2) + "+V"])
            wp.extend(["LowerGlass", "Glass panel", "Wire3", str(w2 / gla), str(o2 + w2 + w2 / 2) + "+V"])
            wp.extend(["UpperFrame", "Frame", "Wire4,Wire5", fw, str(o2) + "+V"])
            wp.extend(["UpperGlass", "Glass panel", "Wire5", str(w2 / gla), str(o2 + w2 / 2) + "+V"])

        elif windowtype == "Sliding 2-pane":
            wp = outerFrame(s, width, height, h1, w1, o1)
            p1 = Vector(h1 + tol, h1 + tol, 0)
            p2 = Vector((width / 2) - tol, h1 + tol, 0)
            p3 = Vector((width / 2) - tol, height - (h1 + tol), 0)
            p4 = Vector(h1 + tol, height - (h1 + tol), 0)
            p5 = Vector(h1 + h2, h1 + h2, 0)
            p6 = Vector((width / 2) - h2, h1 + h2, 0)
            p7 = Vector((width / 2) - h2, height - (h1 + h2), 0)
            p8 = Vector(h1 + h2, height - (h1 + h2), 0)
            addFrame(s, p1, p2, p3, p4, p5, p6, p7, p8)
            p1 = Vector((width / 2) + tol, h1 + tol, 0)
            p2 = Vector(width - (h1 + tol), h1 + tol, 0)
            p3 = Vector(width - (h1 + tol), height - (h1 + tol), 0)
            p4 = Vector((width / 2) + tol, height - (h1 + tol), 0)
            p5 = Vector((width / 2) + h2, h1 + h2, 0)
            p6 = Vector(width - (h1 + h2), h1 + h2, 0)
            p7 = Vector(width - (h1 + h2), height - (h1 + h2), 0)
            p8 = Vector((width / 2) + h2, height - (h1 + h2), 0)
            addFrame(s, p1, p2, p3, p4, p5, p6, p7, p8)
            s.addConstraint(Sketcher.Constraint("DistanceY", 8, 1, 12, 1, h2))
            s.addConstraint(Sketcher.Constraint("DistanceX", 8, 1, 12, 1, h2))
            s.addConstraint(Sketcher.Constraint("DistanceX", 21, 2, 17, 2, h2))
            s.addConstraint(Sketcher.Constraint("DistanceY", 21, 2, 17, 2, h2))
            s.addConstraint(Sketcher.Constraint("DistanceX", 16, 1, 20, 1, h2))
            s.addConstraint(Sketcher.Constraint("DistanceX", 14, 1, 10, 1, h2))
            s.addConstraint(Sketcher.Constraint("Equal", 22, 14))
            s.addConstraint(Sketcher.Constraint("DistanceY", 8, 2, 16, 1, 0.0))
            s.addConstraint(Sketcher.Constraint("DistanceY", 10, 1, 18, 2, 0.0))
            s.addConstraint(Sketcher.Constraint("DistanceX", 4, 1, 8, 1, tol))
            s.addConstraint(Sketcher.Constraint("DistanceY", 4, 1, 8, 1, tol))
            s.addConstraint(Sketcher.Constraint("DistanceX", 6, 1, 18, 1, -tol))
            s.addConstraint(Sketcher.Constraint("DistanceY", 6, 1, 18, 1, -tol))
            s.addConstraint(Sketcher.Constraint("DistanceX", 9, 1, 19, 2, tol))
            s.addConstraint(Sketcher.Constraint("PointOnObject", 13, 2, 22))
            s.addConstraint(Sketcher.Constraint("PointOnObject", 12, 2, 20))
            if h1 == h2:
                s.renameConstraint(55, "Frame5")
                s.renameConstraint(56, "Frame6")
                s.renameConstraint(57, "Frame7")
                s.renameConstraint(58, "Frame8")
                s.renameConstraint(59, "Frame9")
                s.renameConstraint(60, "Frame10")
            fw = str(w2)
            if w2 == w1:
                fw = "0.00+V"
            wp.extend(["LeftFrame", "Frame", "Wire2,Wire3", fw, str(o2) + "+V"])
            wp.extend(["LeftGlass", "Glass panel", "Wire3", str(w2 / gla), str(o2 + w2 / 2) + "+V"])
            wp.extend(["RightFrame", "Frame", "Wire4,Wire5", fw, str(o2 + w2) + "+V"])
            wp.extend(["RightGlass", "Glass panel", "Wire5", str(w2 / gla), str(o2 + w2 + w2 / 2) + "+V"])

        elif windowtype == "Sliding 4-pane":
            wp = outerFrame(s, width, height, h1, w1, o1)
            p1 = Vector(h1 + tol, h1 + tol, 0)
            p2 = Vector(width / 4 - tol, h1 + tol, 0)
            p3 = Vector(width / 4 - tol, height - (h1 + tol), 0)
            p4 = Vector(h1 + tol, height - (h1 + tol), 0)
            p5 = Vector(h1 + h2, h1 + h2, 0)
            p6 = Vector(width / 4 - h2, h1 + h2, 0)
            p7 = Vector(width / 4 - h2, height - (h1 + h2), 0)
            p8 = Vector(h1 + h2, height - (h1 + h2), 0)
            addFrame(s, p1, p2, p3, p4, p5, p6, p7, p8)
            p1 = Vector(width / 4 + tol, h1 + tol, 0)
            p2 = Vector(width / 2 - tol, h1 + tol, 0)
            p3 = Vector(width / 2 - tol, height - (h1 + tol), 0)
            p4 = Vector(width / 4 + tol, height - (h1 + tol), 0)
            p5 = Vector(width / 4 + h2, h1 + h2, 0)
            p6 = Vector(width / 2 - h2, h1 + h2, 0)
            p7 = Vector(width / 2 - h2, height - (h1 + h2), 0)
            p8 = Vector(width / 4 + h2, height - (h1 + h2), 0)
            addFrame(s, p1, p2, p3, p4, p5, p6, p7, p8)
            p1 = Vector(width / 2 + tol, h1 + tol, 0)
            p2 = Vector(width * 3 / 4 - tol, h1 + tol, 0)
            p3 = Vector(width * 3 / 4 - tol, height - (h1 + tol), 0)
            p4 = Vector(width / 2 + tol, height - (h1 + tol), 0)
            p5 = Vector(width / 2 + h2, h1 + h2, 0)
            p6 = Vector(width * 3 / 4 - h2, h1 + h2, 0)
            p7 = Vector(width * 3 / 4 - h2, height - (h1 + h2), 0)
            p8 = Vector(width / 2 + h2, height - (h1 + h2), 0)
            addFrame(s, p1, p2, p3, p4, p5, p6, p7, p8)
            p1 = Vector(width * 3 / 4 + tol, h1 + tol, 0)
            p2 = Vector(width - (h1 + tol), h1 + tol, 0)
            p3 = Vector(width - (h1 + tol), height - (h1 + tol), 0)
            p4 = Vector(width * 3 / 4 + tol, height - (h1 + tol), 0)
            p5 = Vector(width * 3 / 4 + h2, h1 + h2, 0)
            p6 = Vector(width - (h1 + h2), h1 + h2, 0)
            p7 = Vector(width - (h1 + h2), height - (h1 + h2), 0)
            p8 = Vector(width * 3 / 4 + h2, height - (h1 + h2), 0)
            addFrame(s, p1, p2, p3, p4, p5, p6, p7, p8)
            s.addConstraint(Sketcher.Constraint("DistanceX", 4, 1, 8, 1, tol))
            s.addConstraint(Sketcher.Constraint("DistanceX", 8, 2, 16, 1, tol))
            s.addConstraint(Sketcher.Constraint("DistanceX", 17, 1, 27, 2, tol))
            s.addConstraint(Sketcher.Constraint("DistanceX", 24, 2, 32, 1, tol))
            s.addConstraint(Sketcher.Constraint("DistanceX", 32, 2, 4, 2, tol))
            s.addConstraint(Sketcher.Constraint("DistanceY", 4, 1, 8, 1, tol))
            s.addConstraint(Sketcher.Constraint("DistanceY", 10, 2, 6, 2, tol))
            s.addConstraint(Sketcher.Constraint("DistanceY", 17, 2, 26, 2, 0.0))
            s.addConstraint(Sketcher.Constraint("DistanceY", 25, 2, 34, 2, 0.0))
            s.addConstraint(Sketcher.Constraint("DistanceY", 8, 2, 16, 1, 0.0))
            s.addConstraint(Sketcher.Constraint("DistanceY", 9, 2, 18, 2, 0.0))
            s.addConstraint(Sketcher.Constraint("DistanceY", 16, 2, 24, 1, 0.0))
            s.addConstraint(Sketcher.Constraint("DistanceY", 24, 2, 32, 1, 0.0))
            s.addConstraint(Sketcher.Constraint("DistanceX", 8, 1, 12, 1, h2))
            s.addConstraint(Sketcher.Constraint("DistanceY", 8, 1, 12, 1, h2))
            s.addConstraint(Sketcher.Constraint("DistanceX", 13, 2, 9, 2, h2))
            s.addConstraint(Sketcher.Constraint("DistanceY", 13, 2, 9, 2, h2))
            s.addConstraint(Sketcher.Constraint("DistanceX", 16, 1, 20, 1, h2))
            s.addConstraint(Sketcher.Constraint("DistanceY", 16, 1, 20, 1, h2))
            s.addConstraint(Sketcher.Constraint("DistanceX", 21, 2, 17, 2, h2))
            s.addConstraint(Sketcher.Constraint("DistanceY", 21, 2, 17, 2, h2))
            s.addConstraint(Sketcher.Constraint("DistanceX", 24, 1, 28, 1, h2))
            s.addConstraint(Sketcher.Constraint("DistanceY", 24, 1, 28, 1, h2))
            s.addConstraint(Sketcher.Constraint("DistanceX", 29, 2, 25, 2, h2))
            s.addConstraint(Sketcher.Constraint("DistanceY", 29, 2, 25, 2, h2))
            s.addConstraint(Sketcher.Constraint("DistanceX", 32, 1, 36, 1, h2))
            s.addConstraint(Sketcher.Constraint("DistanceY", 32, 1, 36, 1, h2))
            s.addConstraint(Sketcher.Constraint("DistanceX", 37, 2, 33, 2, h2))
            s.addConstraint(Sketcher.Constraint("DistanceY", 37, 2, 33, 2, h2))
            s.addConstraint(Sketcher.Constraint("Equal", 14, 22))
            s.addConstraint(Sketcher.Constraint("Equal", 22, 30))
            s.addConstraint(Sketcher.Constraint("Equal", 30, 38))
            if h1 == h2:
                s.renameConstraint(100, "Frame5")
                s.renameConstraint(101, "Frame6")
                s.renameConstraint(102, "Frame7")
                s.renameConstraint(103, "Frame8")
                s.renameConstraint(104, "Frame9")
                s.renameConstraint(105, "Frame10")
                s.renameConstraint(106, "Frame11")
                s.renameConstraint(107, "Frame12")
                s.renameConstraint(108, "Frame13")
                s.renameConstraint(109, "Frame14")
                s.renameConstraint(110, "Frame15")
                s.renameConstraint(111, "Frame16")
                s.renameConstraint(112, "Frame17")
                s.renameConstraint(113, "Frame18")
                s.renameConstraint(114, "Frame19")
                s.renameConstraint(115, "Frame20")
            fw = str(w2)
            if w2 == w1:
                fw = "0.00+V"
            wp.extend(["LeftMostFrame", "Frame", "Wire2,Wire3", fw, str(o2) + "+V"])
            wp.extend(["LeftMostGlass", "Glass panel", "Wire3", str(w2 / gla), str(o2 + w2 / 2) + "+V"])
            wp.extend(["LeftFrame", "Frame", "Wire4,Wire5", fw, str(o2 + w2) + "+V"])
            wp.extend(["LeftGlass", "Glass panel", "Wire5", str(w2 / gla), str(o2 + w2 + w2 / 2) + "+V"])
            wp.extend(["RightFrame", "Frame", "Wire6,Wire7", fw, str(o2 + w2) + "+V"])
            wp.extend(["RightGlass", "Glass panel", "Wire7", str(w2 / gla), str(o2 + w2 + w2 / 2) + "+V"])
            wp.extend(["RightMostFrame", "Frame", "Wire8,Wire9", fw, str(o2) + "+V"])
            wp.extend(["RightMostGlass", "Glass panel", "Wire9", str(w2 / gla), str(o2 + w2 / 2) + "+V"])

        elif windowtype == "Awning":
            wp = outerFrame(s, width, height, h1, w1, o1)
            simpleFrame(s, width, height, h1, h2, tol)
            fw = str(w2)
            if w2 == w1:
                fw = "0.00+V"
            wp.extend(["InnerFrame", "Frame", "Wire2,Wire3,Edge7,Mode1", fw, str(o2) + "+V"])
            wp.extend(["InnerGlass", "Glass panel", "Wire3", str(w2 / gla), str(o2 + w2 / 2) + "+V"])

        elif windowtype == "Arched window":
            wi0, wi1 = arched_outer_frame(s, width, height, h1, h3, w1, w2, o1)
            apply_relative_arched_constraints(s, wi0, wi1, h1, h1)
            s.renameConstraint(s.ConstraintCount - 6, "Frame3")
            wp = ["OuterFrame", "Frame", "Wire0,Wire1", str(w1 - w2) + "+V", "0.00+V"]            
            wp.extend(arched_inner_frame(s, width, height, h1, h2, h3, w1, w2, tol, o1))
            wp.extend(["Glass", "Glass panel", "Wire3", str(w2 / gla), str(o2 + w2 / 2) + "+V"])    

        elif windowtype == "Oval fixed window":
            vp1 = Vector(width / 2, 0, 0)
            vp2 = Vector(width / 2, height, 0)
            vp3 = Vector(0, height / 2, 0)
            vp4 = Vector(width, height / 2, 0)
            vp5 = Vector(width / 6, 5 * height / 6, 0)
            vp6 = Vector(5 * width / 6, 5 * height / 6, 0)
            vp7 = Vector(5 * width / 6, height / 6, 0)
            vp8 = Vector(width / 6, height / 6, 0)

            vp1a = vp1 + Vector(0, h1, 0)
            vp2a = vp2 - Vector(0, h1, 0)
            vp3a = vp3 + Vector(h1, 0, 0)
            vp4a = vp4 - Vector(h1, 0, 0)

            geo_v = s.addGeometry(Part.LineSegment(vp1, vp2), True)
            geo_h = s.addGeometry(Part.LineSegment(vp3, vp4), True)

            s.addConstraint(Sketcher.Constraint("PointOnObject", geo_v, 1, -1))
            s.addConstraint(Sketcher.Constraint("PointOnObject", geo_h, 1, -2))
            s.addConstraint(Sketcher.Constraint("Vertical", geo_v))
            s.addConstraint(Sketcher.Constraint("Symmetric", geo_h, 1, geo_h, 2, geo_v))

            s.addConstraint(Sketcher.Constraint("DistanceY", -1, 1, geo_v, 2, height))
            s.renameConstraint(s.ConstraintCount - 1, "height")
            s.addConstraint(Sketcher.Constraint("DistanceX", -2, 1, geo_h, 2, width))
            s.renameConstraint(s.ConstraintCount - 1, "width")
            s.addConstraint(Sketcher.Constraint("DistanceY", -1, 1, geo_h, 1, height / 2))

            geo_arc1 = s.addGeometry(Part.Arc(vp5, vp2, vp6), False)
            geo_arc2 = s.addGeometry(Part.Arc(vp8, vp1, vp7), False)
            geo_arc3 = s.addGeometry(Part.Arc(vp5, vp3, vp8), False)
            geo_arc4 = s.addGeometry(Part.Arc(vp6, vp4, vp7), False)

            s.addConstraint(Sketcher.Constraint('PointOnObject', geo_v, 2, geo_arc1))
            s.addConstraint(Sketcher.Constraint('PointOnObject', geo_v, 1, geo_arc2))
            s.addConstraint(Sketcher.Constraint('PointOnObject', geo_h, 1, geo_arc3))
            s.addConstraint(Sketcher.Constraint('PointOnObject', geo_h, 2, geo_arc4))
            
            s.addConstraint(Sketcher.Constraint('Coincident', geo_arc1, 2, geo_arc3, 1))  
            s.addConstraint(Sketcher.Constraint('Tangent', geo_arc1, 1, geo_arc4, 2))
            s.addConstraint(Sketcher.Constraint('Tangent', geo_arc2, 2, geo_arc4, 1))
            s.addConstraint(Sketcher.Constraint('Tangent', geo_arc2, 1, geo_arc3, 2))

            s.addConstraint(Sketcher.Constraint('Equal', geo_arc1, geo_arc2))
            s.addConstraint(Sketcher.Constraint('Equal', geo_arc3, geo_arc4))
            s.addConstraint(Sketcher.Constraint('PointOnObject', geo_arc3, 3, geo_h))

            Wlinie = s.addGeometry(Part.LineSegment(Vector(0, 0, 0), Vector(10, 10, 0)), True)
            s.addConstraint(Sketcher.Constraint('Symmetric', geo_v, 1, geo_v, 2, Wlinie, 1))
            s.addConstraint(Sketcher.Constraint('Coincident', Wlinie, 2, geo_arc1, 2))

            s.addConstraint(Sketcher.Constraint('Angle', geo_v, 2, Wlinie, 1, math.radians(47.56)))
            s.toggleDriving(s.ConstraintCount - 1)

            def berechne_innen_punkte(sketch, arc_index, h1):
                edge = sketch.Geometry[arc_index]
                if not hasattr(edge, "Center"):
                    raise ValueError(f"Die Geometrie am Index {arc_index} ist kein Kreisbogen.")
                pm = edge.Center
                p_start = edge.StartPoint
                p_end = edge.EndPoint
                pv1 = p_start + ((pm - p_start).normalize() * h1)
                pv2 = p_end + ((pm - p_end).normalize() * h1)
                return (pv1, pv2)

            vp5a, vp6a = berechne_innen_punkte(s, geo_arc1, h1)
            vp8a, vp7a = berechne_innen_punkte(s, geo_arc2, h1) 

            geo_arc5 = s.addGeometry(Part.Arc(vp5a, vp2a, vp6a), False)
            geo_arc6 = s.addGeometry(Part.Arc(vp8a, vp1a, vp7a), False)
            geo_arc7 = s.addGeometry(Part.Arc(vp8a, vp3a, vp5a), False)
            geo_arc8 = s.addGeometry(Part.Arc(vp6a, vp4a, vp7a), False)

            vp1h = s.Geometry[geo_arc2].EndPoint
            vp2h = s.Geometry[geo_arc6].EndPoint
            spl = s.addGeometry(Part.LineSegment(vp1h, vp2h), True)

            s.addConstraint(Sketcher.Constraint('Coincident', geo_arc5, 1, geo_arc8, 2))
            s.addConstraint(Sketcher.Constraint('Coincident', geo_arc6, 2, geo_arc8, 1))
            s.addConstraint(Sketcher.Constraint('Coincident', geo_arc6, 1, geo_arc7, 2))
            
            s.addConstraint(Sketcher.Constraint("Coincident", geo_arc1, 3, geo_arc5, 3))
            s.addConstraint(Sketcher.Constraint("Coincident", geo_arc2, 3, geo_arc6, 3))
            s.addConstraint(Sketcher.Constraint("Coincident", geo_arc3, 3, geo_arc7, 3))
            s.addConstraint(Sketcher.Constraint("Coincident", geo_arc4, 3, geo_arc8, 3))

            s.addConstraint(Sketcher.Constraint('Tangent', geo_arc5, 2, geo_arc7, 1))
            s.addConstraint(Sketcher.Constraint('Horizontal', geo_arc5, 2, geo_arc5, 1))
            s.addConstraint(Sketcher.Constraint('Vertical', geo_arc7, 1, geo_arc7, 2))

            s.addConstraint(Sketcher.Constraint("Perpendicular", spl, 1, geo_arc2, 2))
            s.addConstraint(Sketcher.Constraint("Coincident", spl, 2, geo_arc6, 2))
            s.addConstraint(Sketcher.Constraint("Distance", spl, h1))
            s.renameConstraint(s.ConstraintCount - 1, "h1")

            wp = ["OuterFrame", "Frame", "Wire0,Wire1", str(w1 - w2) + "+V", "0.00+V"]
            wp.extend(["Glass", "Glass panel", "Wire1", str(w1 / gla), str(w1 / 2) + "+V"])

        elif windowtype == "Simple door":
            wp = doorFrame(s, width, height, h1, w1, o1)
            add_door_handle(s, h1, tol)
            wp.extend(["DoorPanel", "Solid panel", "Wire1,Wire2,Edge8,Mode1", str(w2), str(o2) + "+V"])

        elif windowtype == "Glass door":
            wp = doorFrame(s, width, height, h1, w1, o1)
            add_door_handle(s, h1, tol)
            wp.extend(["GlassDoorPanel", "Glass panel", "Wire1,Wire2,Edge8,Mode1", str(w2 / gla), str(o2 + w2 / 2) + "+V"])

        elif windowtype == "Glassfilled door":
            wp = doorFrame(s, width, height, h1, w1, o1)
            p1 = Vector(h1 + tol, h1 + tol, 0)
            p2 = Vector(width - (h1 + tol), h1 + tol, 0)
            p3 = Vector(width - (h1 + tol), height - (h1 + tol), 0)
            p4 = Vector(h1 + tol, height - (h1 + tol), 0)
            p5 = Vector(h1 + h2, h1 + h3, 0)
            p6 = Vector(width - (h1 + h2), h1 + h3, 0)
            p7 = Vector(width - (h1 + h2), height - (h1 + h2), 0)
            p8 = Vector(h1 + h2, height - (h1 + h2), 0)
            addFrame(s, p1, p2, p3, p4, p5, p6, p7, p8)
            s.addConstraint(Sketcher.Constraint("DistanceX", 8, 1, 12, 1, h2))
            s.addConstraint(Sketcher.Constraint("DistanceY", 8, 1, 12, 1, h3))
            s.addConstraint(Sketcher.Constraint("DistanceX", 14, 1, 10, 1, h2))
            s.addConstraint(Sketcher.Constraint("DistanceY", 14, 1, 10, 1, h2))
            s.addConstraint(Sketcher.Constraint("DistanceX", 4, 1, 8, 1, tol))
            s.addConstraint(Sketcher.Constraint("DistanceY", 4, 1, 8, 1, tol))
            s.addConstraint(Sketcher.Constraint("DistanceX", 10, 1, 6, 1, tol))
            s.addConstraint(Sketcher.Constraint("DistanceY", 10, 1, 6, 1, tol))
            if h2 == h1:
                s.renameConstraint(39, "Frame5")
                s.renameConstraint(40, "Frame6")
                s.renameConstraint(42, "Frame7")
                s.renameConstraint(41, "Frame8")
            fw = str(w2)
            if w2 == w1:
                fw = "0.00+V"
            if h2 >= 100:
                add_door_handle(s, h1, tol)
                wp.extend(["DoorPanel", "Frame", "Wire2,Wire3,Wire4,Edge8,Mode1", fw, str(o2) + "+V"])
                wp.extend(["InnerGlass", "Glass panel", "Wire3", str(w2 / gla), str(o2 + w2 / 2) + "+V"])
            else:
                wp.extend(["DoorPanel", "Frame", "Wire2,Wire3,Edge8,Mode1", fw, str(o2) + "+V"])
                wp.extend(["InnerGlass", "Glass panel", "Wire3", str(w2 / gla), str(o2 + w2 / 2) + "+V"])

        elif windowtype == "Arched Glass door":
            wi0, wi1 = arched_outer_frame(s, width, height, h1, h3, w1, w2, o1)
            apply_relative_arched_constraints(s, wi0, wi1, h1, 0)
            s.renameConstraint(s.ConstraintCount - 6, "Frame3")
            wp = ["OuterFrame", "Frame", "Wire0,Wire1", str(w1 - w2) + "+V", "0.00+V"]
            add_door_handle(s, h1, tol)
            wp.extend(["GlassDoorPanel", "Glass panel", "Wire1,Wire2,Edge8,Mode1", str(w2 / gla), str(o2 + w2 / 2) + "+V"])

        elif windowtype == "Arched Glassfilled door":
            wi0, wi1 = arched_outer_frame(s, width, height, h1, h3, w1, w2, o1)
            apply_relative_arched_constraints(s, wi0, wi1, h1, 0)
            s.renameConstraint(s.ConstraintCount - 6, "Frame3")
            wp = ["OuterFrame", "Frame", "Wire0,Wire1", str(w1 - w2) + "+V", "0.00+V"]            
            wp.extend(arched_inner_frame(s, width, height, h1, h2, h3, w1, w2, tol, o1))
            add_door_handle(s, h1, tol)
            wp[-3] = wp[-3].replace("Wire2,Wire3", "Wire2,Wire3,Wire4")
            wp.extend(["InnerGlass", "Glass panel", "Wire3", str(w2 / gla), str(o2 + w2 / 2) + "+V"])

        elif windowtype == "Opening only":
            wp = []
            p1 = Vector(0, 0, 0)
            p2 = Vector(width, 0, 0)
            p3 = Vector(width, height, 0)
            p4 = Vector(0, height, 0)
            addRectangle(s, p1, p2, p3, p4)
            s.addConstraint(Sketcher.Constraint("Coincident", 0, 1, -1, 1))
            s.addConstraint(Sketcher.Constraint("DistanceX", 0, width))
            s.addConstraint(Sketcher.Constraint("DistanceY", 1, height))
            s.renameConstraint(9, "Width")
            s.renameConstraint(10, "Height")

        return (s, wp)

    if windowtype in WindowPresets:
        import Arch

        default = makeSketch(windowtype, width, height, h1, h2, h3, w1, w2, o1, o2)
        FreeCAD.ActiveDocument.recompute()
        if default:
            if placement:
                default[0].Placement = placement
                FreeCAD.ActiveDocument.recompute()
            obj = Arch.makeWindow(default[0], width, height, default[1])
            obj.Preset = WindowPresets.index(windowtype) + 1
            obj.Frame = w2
            obj.Offset = o1
            obj.Placement = FreeCAD.Placement()
            if "door" in windowtype.lower():
                obj.IfcType = "Door"
                obj.Label = translate("Arch", "Door")
            elif "opening" in windowtype.lower():
                obj.IfcType = "Opening Element"
                obj.Label = translate("Arch", "Opening")
            FreeCAD.ActiveDocument.recompute()
            return obj

    print("Arch: Unknown window type")