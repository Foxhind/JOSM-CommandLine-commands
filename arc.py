#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       arc.py {Point1},{Point2},{Point3} {Segments} {Params}
#           stdin: -
#       
#       Script creates an arc by three specified points - start, intermediate and end of an arc. Arc will have specified number of segments.
#       Params: 0 - nothing special, 1 - creates axes of an arc
#       Segments = 0 will use autocalculation for smooth arc
#       Note: arc will not be more than semicircle, if intermediate point is far from start and end
#           then script will create counterpart arc of same circle (TOFIX)
#       
#       Copyright 2010-2011 Hind <foxhind@gmail.com>
#       modified by OverQuantum:
#       2014-12-13 Fix to 4 spaces indentation; added Params (0/1) - 1 for creation of axes
#       
#       This program is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; either version 2 of the License, or
#       (at your option) any later version.
#       
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.    See the
#       GNU General Public License for more details.
#       
#       You should have received a copy of the GNU General Public License
#       along with this program; if not, write to the Free Software
#       Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#       MA 02110-1301, USA.

import sys
import math
import projections
from OsmData import OsmData, Map, LON, LAT, ACTION, MODIFY, TAG, CREATE, REF, NODES, WAYS

if sys.version_info[0] < 3:
    reload(sys)
    sys.setdefaultencoding("utf-8")                    # a hack to support UTF-8 

def intersect(vector1, pivot1, vector2, pivot2): # intersection of 2 lines
    k1 = vector1[1]/vector1[0]
    b1 = (vector1[0]*pivot1[1] - vector1[1]*pivot1[0]) / vector1[0]
    k2 = vector2[1]/vector2[0]
    b2 = (vector2[0]*pivot2[1] - vector2[1]*pivot2[0]) / vector2[0]
    x = (b1 - b2) / (k2 - k1)
    y = (k2*b1 - k1*b2) / (k2 - k1)
    return (x, y)

def createarc(C, P1, P2, r, segments):
    arc = [P1]
    CP1 = (P1[0]-C[0], P1[1]-C[1])
    CP2 = (P2[0]-C[0], P2[1]-C[1])
    a1 = math.atan(CP1[1]/CP1[0]) # start angle
    if CP1[0] < 0:
        a1 += math.pi
    if a1 < 0:
        a1 += math.pi*2
    a2 = math.atan(CP2[1]/CP2[0]) # end angle
    if CP2[0] < 0:
        a2 += math.pi
    if a2 < 0:
        a2 += math.pi*2
    
    if a2-a1 > math.pi:
        a2 -= math.pi*2
    elif a1-a2 > math.pi:
        a1 -= math.pi*2
        
    if segments == 0: # optimal number of segments
        P1P2 = (P2[0]-P1[0], P2[1]-P1[1])
        P1P2abs = math.sqrt(P1P2[0]*P1P2[0] + P1P2[1]*P1P2[1])
        segments = int(math.ceil(math.log(P1P2abs, 4) * (math.cos((a2-a1)/2) + 1.5))) # cat's magic formula
        
    interval = (a2 - a1) / segments
    for n in range(1, segments):
        val = a1 + interval * n
        arc.append(( C[0] + r * math.cos(val), C[1] + r * math.sin(val) ))
    arc.append(P2)
    return arc

def main():
    if len(sys.argv) != 4:
        return 0
    coords = (sys.argv[1].split(','))
    A = projections.from4326((float(coords[0]),float(coords[1])), "EPSG:3857")
    B = projections.from4326((float(coords[2]),float(coords[3])), "EPSG:3857")
    C = projections.from4326((float(coords[4]),float(coords[5])), "EPSG:3857")
    segments = int(sys.argv[2])
    params = int(sys.argv[3])    
    AM = ((B[0] - A[0])/2, (B[1] - A[1])/2)
    BN = ((C[0] - B[0])/2, (C[1] - B[1])/2)
    M = (A[0] + AM[0], A[1] + AM[1])
    N = (B[0] + BN[0], B[1] + BN[1])
    MM = (AM[1], -AM[0])
    NN = (BN[1], -BN[0])
    O = intersect(MM, M, NN, N)                      # circle center
    OA = (O[0] - A[0], O[1] - A[1])
    r = math.sqrt(OA[0]*OA[0] + OA[1]*OA[1])        # radius
    arc = createarc(O, A, C, r, segments)
    
    tData = OsmData()
    wayid = tData.addway()
    for point in arc:
        p = projections.to4326(point, "EPSG:3857")
        newid = tData.addnode()
        tData.nodes[newid][LON] = p[0]
        tData.nodes[newid][LAT] = p[1]
        tData.nodes[newid][TAG] = {}
        tData.ways[wayid][REF].append(newid)
    if params == 1:
        p2 = projections.to4326(O, "EPSG:3857")                     # center
        p1 = projections.to4326((O[0]-r*1.05,O[1]), "EPSG:3857")   # axes points
        p3 = projections.to4326((O[0]+r*1.05,O[1]), "EPSG:3857")
        p4 = projections.to4326((O[0],O[1]-r*1.05), "EPSG:3857")
        p5 = projections.to4326((O[0],O[1]+r*1.05), "EPSG:3857")
        wayid = tData.addway()
        newid = tData.addnode()
        tData.nodes[newid][LON] = p1[0]
        tData.nodes[newid][LAT] = p1[1]
        tData.nodes[newid][TAG] = {}
        tData.ways[wayid][REF].append(newid)
        newid2 = tData.addnode()
        tData.nodes[newid2][LON] = p2[0]
        tData.nodes[newid2][LAT] = p2[1]
        tData.nodes[newid2][TAG] = {}
        tData.ways[wayid][REF].append(newid2)
        newid = tData.addnode()
        tData.nodes[newid][LON] = p3[0]
        tData.nodes[newid][LAT] = p3[1]
        tData.nodes[newid][TAG] = {}
        tData.ways[wayid][REF].append(newid)
        wayid = tData.addway()
        newid = tData.addnode()
        tData.nodes[newid][LON] = p4[0]
        tData.nodes[newid][LAT] = p4[1]
        tData.nodes[newid][TAG] = {}
        tData.ways[wayid][REF].append(newid)
        tData.ways[wayid][REF].append(newid2)
        newid = tData.addnode()
        tData.nodes[newid][LON] = p5[0]
        tData.nodes[newid][LAT] = p5[1]
        tData.nodes[newid][TAG] = {}
        tData.ways[wayid][REF].append(newid)
    
    tData.addcomment("Done.")
    tData.write(sys.stdout)
    #f = open("out.txt", "w")
    #tData.write(f)
    #f.close()
    return 0

if __name__ == '__main__':
    main()
