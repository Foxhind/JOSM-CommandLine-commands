#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       offset.py {Offset} {Direction} {Copy}
#       
#       Copyright 2010-2011 Hind <foxhind@gmail.com>
#       
#       This program is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; either version 2 of the License, or
#       (at your option) any later version.
#       
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#       
#       You should have received a copy of the GNU General Public License
#       along with this program; if not, write to the Free Software
#       Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#       MA 02110-1301, USA.

import sys
import math
import projections
import copy
from OsmData import OsmData, Map, LON, LAT, ACTION, MODIFY, DELETE, REF, CREATE, NODES, WAYS, RELATIONS, CHANGESET, TAG

if sys.version_info[0] < 3:
  reload(sys)
  sys.setdefaultencoding("utf-8")          # a hack to support UTF-8  

def main():
  if len(sys.argv) != 4:
    return 0
  offset = float(sys.argv[1])
  nMap = Map()
  wMap = Map()
  both = False
  copye = False
  if sys.argv[2] == "Left":
    offset *= (-1)
  elif sys.argv[2] == "Both":
    both = True
  if sys.argv[3] == "Yes":
    copye = True
  data = OsmData()
  ndata = OsmData()
  data.read(sys.stdin)
  data.read(sys.stdin)
  
  if both:
    if copye:
      nwaydata1 = calcoffset(data, offset, True, nMap, wMap)
      nwaydata2 = calcoffset(data, -offset, True, nMap, wMap)
    else:
      nwaydata1 = calcoffset(data, offset, True, nMap, wMap)
      nwaydata2 = calcoffset(data, -offset, False, nMap, wMap)
    ndata.nodes.update(nwaydata1.nodes)
    ndata.nodes.update(nwaydata2.nodes)
    ndata.ways.update(nwaydata1.ways)
    ndata.ways.update(nwaydata2.ways)
  else:
    if copye:
      nwaydata = calcoffset(data, offset, True, nMap, wMap)
    else:
      nwaydata = calcoffset(data, offset, False, nMap, wMap)
    ndata.nodes.update(nwaydata.nodes)
    ndata.ways.update(nwaydata.ways)
  
  ndata.addcomment("Done.")
  ndata.write(sys.stdout)
  return 0

def calcoffset(waydata, offset, copye, nMap, wMap):
  nwaydata = OsmData()
  wid, way = waydata.ways.popitem()
  waydata.ways[wid] = way
  
  if copye:
    newref = []
    for ref in way[REF]:
      newref.append(nMap[ref])
      nwaydata.nodes[nMap[ref]] = {}
      nwaydata.nodes[nMap[ref]][LON] = waydata.nodes[ref][LON]
      nwaydata.nodes[nMap[ref]][LAT] = waydata.nodes[ref][LAT]
      nwaydata.nodes[nMap[ref]][TAG] = waydata.nodes[ref][TAG]
    wid = wMap[wid]
    nwaydata.ways[wid] = {}
    nwaydata.ways[wid][TAG] = copy.deepcopy(way[TAG])
    nwaydata.ways[wid][REF] = copy.deepcopy(way[REF])
    way = nwaydata.ways[wid]
  else:
    nwaydata.nodes = copy.deepcopy(waydata.nodes)
    nwaydata.ways[wid] = way
  
  ispolygon = way[REF][0] == way[REF][len(way[REF]) - 1]
  to = len(way[REF])
  if ispolygon: to -= 1
  for i in range(to):
    nodes = [None, None, None]
    if i > 0:
      nodes[0] = waydata.nodes[way[REF][i-1]]
    else:
      if ispolygon:
        nodes[0] = waydata.nodes[way[REF][len(way[REF]) - 2]]
    nodes[1] = waydata.nodes[way[REF][i]]
    if i < (len(way[REF]) - 1):
      nodes[2] = waydata.nodes[way[REF][i+1]]
    else:
      if ispolygon:
        nodes[2] = waydata.nodes[way[REF][0]]
    lon, lat = calcpos(nodes, offset)
    if copye: nodeid = nMap[way[REF][i]]
    else: nodeid = way[REF][i]
    nwaydata.nodes[nodeid][LON] = lon
    nwaydata.nodes[nodeid][LAT] = lat
    if copye:
      nwaydata.nodes[nodeid][ACTION] = CREATE
    else:
      nwaydata.nodes[nodeid][ACTION] = MODIFY
  if copye:
    way[REF] = newref
    way[ACTION] = CREATE
    nMap.omap.clear()
    wMap.omap.clear()
  return nwaydata

def calcpos(nodes, offset):
  coords = [None, None, None]
  if nodes[0] != None: coords[0] = projections.from4326((nodes[0][LON],nodes[0][LAT]), "EPSG:3857")
  coords[1] = projections.from4326((nodes[1][LON],nodes[1][LAT]), "EPSG:3857")
  if nodes[2] != None: coords[2] = projections.from4326((nodes[2][LON],nodes[2][LAT]), "EPSG:3857")
  
  if coords[0] == None:
    coords[0] = (2*coords[1][0] - coords[2][0], 2*coords[1][1] - coords[2][1])
    v1 = normalize((coords[2][1] - coords[1][1], coords[1][0] - coords[2][0]))
    v = (v1[0] * offset, v1[1] * offset)
  elif coords[2] == None:
    coords[2] = (2*coords[1][0] - coords[0][0], 2*coords[1][1] - coords[0][1])
    v1 = normalize((coords[1][1] - coords[0][1], coords[0][0] - coords[1][0]))
    v = (v1[0] * offset, v1[1] * offset)
  else:
    v1 = normalize((coords[0][0] - coords[1][0], coords[0][1] - coords[1][1]))
    v2 = normalize((coords[2][0] - coords[1][0], coords[2][1] - coords[1][1]))
    v1p2 = normalize((v1[0] + v2[0], v1[1] + v2[1]))
    soffset = offset * sign(v1[0]*v2[1] - v1[1]*v2[0])
    v = (v1p2[0] * soffset, v1p2[1] * soffset)
  return projections.to4326((coords[1][0] + v[0], coords[1][1] + v[1]), "EPSG:3857")
 
def normalize(vector):
  l = math.sqrt(vector[0]*vector[0] + vector[1]*vector[1])
  return (vector[0] / l, vector[1] / l)
 
def sign(value):
  if value > 0:
    return 1
  elif value < 0:
    return -1
  return 0

if __name__ == '__main__':
	main()
