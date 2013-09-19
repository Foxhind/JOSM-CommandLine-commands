#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       mirror.py {FirstPoint} {SecondPoint} {Copy}
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
from OsmData import OsmData, Map, LON, LAT, ACTION, MODIFY, REF, CREATE, NODES, WAYS, RELATIONS, CHANGESET, TAG

if sys.version_info[0] < 3:
  reload(sys)
  sys.setdefaultencoding("utf-8")          # a hack to support UTF-8 

def mirror(M, P1, P2):
  vx = M[0] - P1[0]
  vy = M[1] - P1[1]
  ux = P2[0] - P1[0]
  uy = P2[1] - P1[1]
  l = (ux*ux + uy*uy)**0.5
  ux /= l
  uy /= l
  lp = vx * ux + vy * uy
  return (M[0] + 2*(ux * lp - vx), M[1] + 2*(uy * lp - vy))

def main():
  if len(sys.argv) != 4:
    return 0
  rData = OsmData() # References
  mData = OsmData() # Objects for moving
  rData.read(sys.stdin)
  mData.read(sys.stdin)
  coords = (sys.argv[1].split(','))
  p1 = projections.from4326((float(coords[0]),float(coords[1])), "EPSG:3857")
  coords = (sys.argv[2].split(','))
  p2 = projections.from4326((float(coords[0]),float(coords[1])), "EPSG:3857")
  if sys.argv[3] == "Yes":
    nData = OsmData() # New objects
    nMap = Map()
    wMap = Map()
    rMap = Map()
    for key in rData.nodes.keys():
      p = projections.from4326((rData.nodes[key][LON],rData.nodes[key][LAT]), "EPSG:3857")
      p = mirror(p, p1, p2)
      p = projections.to4326(p, "EPSG:3857")
      nData.nodes[nMap[key]] = {}
      nData.nodes[nMap[key]][TAG] = rData.nodes[key][TAG]
      nData.nodes[nMap[key]][LON] = p[0]
      nData.nodes[nMap[key]][LAT] = p[1]
      nData.nodes[nMap[key]][ACTION] = CREATE
    for key in mData.nodes.keys():
      p = projections.from4326((mData.nodes[key][LON],mData.nodes[key][LAT]), "EPSG:3857")
      p = mirror(p, p1, p2)
      p = projections.to4326(p, "EPSG:3857")
      nData.nodes[nMap[key]] = {}
      nData.nodes[nMap[key]][TAG] = mData.nodes[key][TAG]
      nData.nodes[nMap[key]][LON] = p[0]
      nData.nodes[nMap[key]][LAT] = p[1]
      nData.nodes[nMap[key]][ACTION] = CREATE
    for key in rData.ways.keys():
      nData.ways[wMap[key]] = {}
      nData.ways[wMap[key]][TAG] = rData.ways[key][TAG]
      nData.ways[wMap[key]][REF] = []
      for nd in rData.ways[key][REF]:
        nData.ways[wMap[key]][REF].append(nMap[nd])
      nData.ways[wMap[key]][ACTION] = CREATE
    for key in mData.ways.keys():
      nData.ways[wMap[key]] = {}
      nData.ways[wMap[key]][TAG] = mData.ways[key][TAG]
      nData.ways[wMap[key]][REF] = []
      for nd in mData.ways[key][REF]:
        nData.ways[wMap[key]][REF].append(nMap[nd])
      nData.ways[wMap[key]][ACTION] = CREATE
    for key in rData.relations.keys():
      nData.relations[rMap[key]] = {}
      nData.relations[rMap[key]][TAG] = rData.relations[key][TAG]
      nData.relations[rMap[key]][REF] = [[], [], []]
      for nd in rData.relations[key][REF][NODES]:
        if nData.nodes.get(nMap[nd]) != None:
          nData.relations[rMap[key]][REF][NODES].append((nMap[nd[0]], nd[1]))
      for way in rData.relations[key][REF][WAYS]:
        if nData.ways.get(wMap[way]) != None:
          nData.relations[rMap[key]][REF][WAYS].append((wMap[way[0]], way[1]))
      for relation in rData.relations[key][REF][RELATIONS]:
        if rData.relations.get(relation) != None or mData.relations.get(relation) != None:
          nData.relations[rMap[key]][REF][RELATIONS].append((rMap[relation[0]], relation[1]))
      nData.relations[rMap[key]][ACTION] = CREATE
    for key in mData.relations.keys():
      nData.relations[rMap[key]] = {}
      nData.relations[rMap[key]][TAG] = mData.relations[key][TAG]
      nData.relations[rMap[key]][REF] = [[], [], []]
      for nd in mData.relations[key][REF][NODES]:
        if nData.nodes.get(nMap[nd[0]]) != None:
          nData.relations[rMap[key]][REF][NODES].append((nMap[nd[0]], nd[1]))
      for way in mData.relations[key][REF][WAYS]:
        if nData.ways.get(wMap[way[0]]) != None:
          nData.relations[rMap[key]][REF][WAYS].append((wMap[way[0]], way[1]))
      for relation in mData.relations[key][REF][RELATIONS]:
        if rData.relations.get(relation[0]) != None or mData.relations.get(relation) != None:
          nData.relations[rMap[key]][REF][RELATIONS].append((rMap[relation[0]], relation[1]))
      nData.relations[rMap[key]][ACTION] = CREATE
    nData.addcomment("Done.")
    nData.write(sys.stdout)
    
  elif sys.argv[3] == "No":
    rData.nodes.update(mData.nodes)
    for nkey in rData.nodes.keys():
      p = projections.from4326((rData.nodes[nkey][LON],rData.nodes[nkey][LAT]), "EPSG:3857")
      p = mirror(p, p1, p2)
      p = projections.to4326(p, "EPSG:3857")
      rData.nodes[nkey][LON] = p[0]
      rData.nodes[nkey][LAT] = p[1]
      rData.nodes[nkey][ACTION] = MODIFY
    rData.write(sys.stdout)
  return 0

if __name__ == '__main__':
	main()
