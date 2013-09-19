#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       move.py {FirstPoint} {SecondPoint} {Copy}
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

from OsmData import OsmData, Map, LON, LAT, ACTION, MODIFY, TAG, CREATE, REF, NODES, WAYS, RELATIONS

if sys.version_info[0] < 3:
  reload(sys)
  sys.setdefaultencoding("utf-8")          # a hack to support UTF-8 

def main():
  if len(sys.argv) != 4:
    return 0
  rData = OsmData() # References
  mData = OsmData() # Objects for moving
  rData.read(sys.stdin)
  mData.read(sys.stdin)
  coords = sys.argv[1].split(',')
  p1 = (float(coords[0]), float(coords[1]))
  if sys.argv[3] == "No":
    coords = (sys.argv[2].split(','))
    p2 = (float(coords[0]), float(coords[1]))
    vector = (p2[0] - p1[0], p2[1] - p1[1])
    rData.nodes.update(mData.nodes)
    for nkey in rData.nodes.keys():
      rData.nodes[nkey][LON] += vector[0]
      rData.nodes[nkey][LAT] += vector[1]
      rData.nodes[nkey][ACTION] = MODIFY
    rData.write(sys.stdout)
  elif sys.argv[3] == "Yes":
    nData = OsmData()
    nMap = Map()
    wMap = Map()
    rMap = Map()
    no = wo = ro = 0 # Offsets
    rData.nodes.update(mData.nodes)
    rData.ways.update(mData.ways)
    rData.relations.update(mData.relations)
    pointlist = (sys.argv[2].split(';'))
    for point in pointlist:
      cData = OsmData()
      coords = point.split(',')
      p2 = (float(coords[0]), float(coords[1]))
      vector = (p2[0] - p1[0], p2[1] - p1[1])
      for key in rData.nodes.keys():
        cData.nodes[nMap[key]] = {}
        cData.nodes[nMap[key]][TAG] = rData.nodes[key][TAG]
        cData.nodes[nMap[key]][LON] = rData.nodes[key][LON] + vector[0]
        cData.nodes[nMap[key]][LAT] = rData.nodes[key][LAT] + vector[1]
        cData.nodes[nMap[key]][ACTION] = CREATE
      for key in rData.ways.keys():
        cData.ways[wMap[key]] = {}
        cData.ways[wMap[key]][TAG] = rData.ways[key][TAG]
        cData.ways[wMap[key]][REF] = []
        for nd in rData.ways[key][REF]:
          cData.ways[wMap[key]][REF].append(nMap[nd + no])
        cData.ways[wMap[key]][ACTION] = CREATE
      for key in rData.relations.keys():
        cData.relations[rMap[key]] = {}
        cData.relations[rMap[key]][TAG] = rData.relations[key][TAG]
        cData.relations[rMap[key]][REF] = [[], [], []]
        for nd in rData.relations[key][REF][NODES]:
          if cData.nodes.get(nMap[nd[0] + no]) != None:
            cData.relations[rMap[key]][REF][NODES].append((nMap[nd[0] + no], nd[1]))
        for way in rData.relations[key][REF][WAYS]:
          if cData.ways.get(wMap[way[0] + wo]) != None:
            cData.relations[rMap[key]][REF][WAYS].append((wMap[way[0] + wo], way[1]))
        for relation in rData.relations[key][REF][RELATIONS]:
          if rData.relations.get(relation) != None or mData.relations.get(relation) != None:
            cData.relations[rMap[key]][REF][RELATIONS].append((rMap[relation[0] + ro], relation[1]))
        cData.relations[rMap[key]][ACTION] = CREATE
      nMap.omap.clear()
      wMap.omap.clear()
      rMap.omap.clear()
      nData.nodes.update(cData.nodes)
      nData.ways.update(cData.ways)
      nData.relations.update(cData.relations)
    nData.addcomment("Done.")
    nData.write(sys.stdout)
  return 0

if __name__ == '__main__':
	main()
