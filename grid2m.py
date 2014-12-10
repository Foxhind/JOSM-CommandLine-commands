#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       grid2m.py {Cell}
#       
#       Script creates square grid escribing selected object(s)
#       (members of selected relations is not counted)
#       Will not create grid for 1 node or so
#
#       Made from grid2m script by Xmypblu (2014-01-18, https://github.com/Xmypblu)
#       by OverQuantum 2014
#       2014-12-10 updated for counting several objects, including nodes (+minor modification)
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
from OsmData import OsmData, LON, LAT, REF, ACTION, DELETE

if sys.version_info[0] < 3:
    reload(sys)
    sys.setdefaultencoding("utf-8")          # a hack to support UTF-8 

def main():
    nData = OsmData() # Nodes
    rData = OsmData() # Escribing way
    nData.read(sys.stdin)
    rData.read(sys.stdin)
    cell = float(sys.argv[1].replace(',', '.')) # cell size, meters
    
    rbbox = getbbox(rData, nData) # bbox of escribing objects
    if rbbox[0]>rbbox[2]:  #degenerate bbox, nothing was selected or only relations
        return 0
    rcenter = getbboxcenter(rbbox)     # bbox center
    
    b_cells = bbox_cell(rbbox, rcenter, cell)
    createcell(b_cells, rData, nData)

def bbox_cell (rbbox, rcenter, cell):
    nbbox_lon = []
    nbbox_lat = []
    nbbox = []
    
    a1 = projections.from4326((rbbox[0],rbbox[1]), "EPSG:3857")
    b1 = projections.from4326((rbbox[2],rbbox[3]), "EPSG:3857")
    cell = float(cell)/math.cos(math.radians(rcenter[1]))
    
    a = a1[0]   # base coordinates
    b = a1[1]
    
    while a < b1[0]:
        nbbox_lon.append(a)
        a += cell
        
    while b < b1[1]:
        nbbox_lat.append(b)
        b += cell
    
    for z in nbbox_lon:
        for x in nbbox_lat:
            z2 = z + cell
            x2 = x + cell
            nbbox.append([[z, x2], [z2, x2], [z2, x], [z, x]])
    return nbbox

def createcell(b_cells, rData, nData):
    n=0
    for i in b_cells:
        wayid = rData.addway()
        for y in i:
            node = projections.to4326((y[0], y[1]), "EPSG:3857")
            nodeid = rData.addnode()
            rData.nodes[nodeid][LON] = node[0]
            rData.nodes[nodeid][LAT] = node[1]
            rData.ways[wayid][REF].append(nodeid)
        rData.ways[wayid][REF].append(rData.ways[wayid][REF][0])
        n+=1
    rData.addcomment("Created " + str(n) + " squares.")
    rData.write(sys.stdout)
    return 0

def getbbox(data, nodedata):
    bbox = [1000, 1000, -1000, -1000]  #degenerate bbox for lat/lon
    for wayid in data.ways.keys():
        for nodeid in data.ways[wayid][REF]:
            node = nodedata.nodes[nodeid]
            if node[LON] < bbox[0]:
                bbox[0] = node[LON]
            if node[LON] > bbox[2]:
                bbox[2] = node[LON]
            if node[LAT] < bbox[1]:
                bbox[1] = node[LAT]
            if node[LAT] > bbox[3]:
                bbox[3] = node[LAT]
    for nodeid in data.nodes.keys():
        node = data.nodes[nodeid]
        if node[LON] < bbox[0]:
            bbox[0] = node[LON]
        if node[LON] > bbox[2]:
            bbox[2] = node[LON]
        if node[LAT] < bbox[1]:
            bbox[1] = node[LAT]
        if node[LAT] > bbox[3]:
            bbox[3] = node[LAT]
    return bbox

def getbboxcenter(bbox):
    return ((bbox[0] + bbox[2]) * 0.5, (bbox[1] + bbox[3]) * 0.5)

if __name__ == '__main__':
  main()
