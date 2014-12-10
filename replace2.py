#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       replace2.py
#
#       Script performs replacing geometry of target objects by reference object with care of existing nodes and tags
#       This script does not perform rotation of objects, unlike original replace.py
#     
#       Copyright 2011 Hind <foxhind@gmail.com>
#       2012-08-05 modified by OverQuantum for no rotation
#       2012-08-18 updated from new replace.py
#       2014-12-06 fix to 4 spaces indentation
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
from OsmData import OsmData, LON, LAT, TAG, REF, NODES, ACTION, CREATE, MODIFY, DELETE

if sys.version_info[0] < 3:
    reload(sys)
    sys.setdefaultencoding("utf-8")                    # a hack to support UTF-8 

def main():
    nData = OsmData() # Nodes
    rData = OsmData() # Reference way
    tData = OsmData() # Target ways
    nData.read(sys.stdin)
    rData.read(sys.stdin)
    tData.read(sys.stdin)
    
    rangle = 0
    rcenter = getbboxcenter(getbbox(rData, nData, list(rData.ways.keys())[0]))
    targets = {}
    for key in tData.ways.keys():
        tangle = 0
        tcenter = getbboxcenter(getbbox(tData, nData, key))
        targets[key] = (tangle, tcenter)
    
    for key in targets.keys():
        treplace(nData, rData, list(rData.ways.keys())[0], tData, key, (rangle, rcenter), targets[key])
    
    tData.mergedata(nData)
    tData.addcomment('Done.')
    tData.write(sys.stdout)

def treplace(nodedata, rdata, rwayid, tdata, twayid, reference, target):
    rway = rdata.ways[rwayid]
    tway = tdata.ways[twayid]
    newtwayref = []
    rtmap = {}
    for i, ref in enumerate(rway[REF]):
        if rtmap.get(ref) == None:
            if i < len(tway[REF])-1:
                node = nodedata.nodes[tway[REF][i]]
                node[ACTION] = MODIFY
                newtwayref.append(tway[REF][i])
                rtmap[ref] = tway[REF][i]
            else:
                nodeid = nodedata.addnode()
                node = nodedata.nodes[nodeid]
                newtwayref.append(nodeid)
                rtmap[ref] = nodeid
            angle = math.radians(reference[0] - target[0])
            mrefnode = projections.from4326((nodedata.nodes[ref][LON], nodedata.nodes[ref][LAT]), "EPSG:3857")
            mreference = projections.from4326((reference[1][0], reference[1][1]), "EPSG:3857")
            maboutnull = (mrefnode[0] - mreference[0], mrefnode[1] - mreference[1])
            mrotated = (maboutnull[0] * math.cos(angle) - maboutnull[1] * math.sin(angle), maboutnull[0] * math.sin(angle) + maboutnull[1] * math.cos(angle))
            mtarget = projections.from4326(target[1], "EPSG:3857")
            result = projections.to4326((mtarget[0] + mrotated[0], mtarget[1] + mrotated[1]), "EPSG:3857")
            node[LON] = result[0]
            node[LAT] = result[1]
        else:
            newtwayref.append(rtmap[ref])
    for o in range(len(tway[REF])):
        if not (tway[REF][o] in newtwayref):
            nodedata.nodes[tway[REF][o]][ACTION] = DELETE
    tway[REF] = newtwayref
    tway[ACTION] = MODIFY

def FOREL(data, radius):
    clusters = []
    while len(data) > 0:
        current = data[0]
        previous = (0, 0)
        currentcluster = []
        while current != previous:
            previous = current
            nearobjects = []
            masscenter = 0
            for i in range(len(data)-1, -1, -1):
                if (data[i][0] >= current[0]-radius) and (data[i][0] <= current[0]+radius):
                    nearobjects.append(i)
                    masscenter += data[i][0]
            masscenter /= float(len(nearobjects))
            current = (masscenter, 0)
        for i in range(len(data)-1, -1, -1):
            if i in nearobjects:
                currentcluster.append(data[i])
                data.pop(i)
        clusters.append(currentcluster)
    return clusters

def createtable(data, nodedata, wayid):
    table = []
    for n in range(len(data.ways[wayid][REF]) - 1):
        node1 = nodedata.nodes[data.ways[wayid][REF][n]]
        node2 = nodedata.nodes[data.ways[wayid][REF][n+1]]
        if node1[LON] < node2[LON]:
            c1 = projections.from4326((node1[LON], node1[LAT]), "EPSG:3857")
            c2 = projections.from4326((node2[LON], node2[LAT]), "EPSG:3857")
        else:
            c2 = projections.from4326((node1[LON], node1[LAT]), "EPSG:3857")
            c1 = projections.from4326((node2[LON], node2[LAT]), "EPSG:3857")
        c1c2 = (c2[0]-c1[0], c2[1]-c1[1])
        l = (c1c2[0]*c1c2[0] + c1c2[1]*c1c2[1]) ** 0.5
        angle = math.degrees(math.acos(c1c2[1] / l))
        if c1c2[0] < 0:
            angle = math.pi - angle
        table.append((angle, l))
    return table

def getbbox(data, nodedata, wayid):
    anynode = nodedata.nodes[data.ways[wayid][REF][0]]
    bbox = [anynode[LON], anynode[LAT], anynode[LON], anynode[LAT]]
    for nodeid in data.ways[wayid][REF]:
        node = nodedata.nodes[nodeid]
        if node[LON] < bbox[0]:
            bbox[0] = node[LON]
        elif node[LON] > bbox[2]:
            bbox[2] = node[LON]
        if node[LAT] < bbox[1]:
            bbox[1] = node[LAT]
        elif node[LAT] > bbox[3]:
            bbox[3] = node[LAT]
    return bbox

def getbboxcenter(bbox):
    return (bbox[0] + (bbox[2] - bbox[0]) / 2.0, bbox[1] + (bbox[3] - bbox[1]) / 2.0)

if __name__ == '__main__':
    main()
