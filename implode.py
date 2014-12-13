#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       implode.py
#           stdin: {Ways}
#       
#       Script implodes each selected way to a single node (bbox center) which inherits all way's tags
#
#       Made from wipe script by Xmypblu (2014-01-18, https://github.com/Xmypblu)
#       by OverQuantum, 2014-12-10
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

from OsmData import OsmData, Map, LON, LAT, ACTION, MODIFY, TAG, CREATE, REF, NODES, WAYS, RELATIONS, DELETE

if sys.version_info[0] < 3:
    reload(sys)
    sys.setdefaultencoding("utf-8")     # a hack to support UTF-8 

def main():
    nData = OsmData() # Nodes
    rData = OsmData() # Reference ways
    nData.read(sys.stdin)
    rData.read(sys.stdin)
    idn = list(rData.ways.keys())
    createnode(rData, nData, idn)

def createnode(rData, nData, idn):
    for a in idn:
        rbbox = getbbox(rData, nData, a)
        rcenter = getbboxcenter(rbbox)
        nid = rData.addnode()
        rData.nodes[nid][LON] = rcenter[0]
        rData.nodes[nid][LAT] = rcenter[1]
        rData.nodes[nid][TAG] = rData.ways[a][TAG].copy()
        way = rData.ways[a]
        way[ACTION] = DELETE
        ispolygon = way[REF][0] == way[REF][len(way[REF]) - 1]
        to = len(way[REF])
        if ispolygon: to -= 1
        for i in range(to):
            nodeid = way[REF][i]
            nData.nodes[nodeid][ACTION] = DELETE
    rData.nodes.update(nData.nodes)
    rData.ways.update(rData.ways)
    rData.write(sys.stdout)
    return 0

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
