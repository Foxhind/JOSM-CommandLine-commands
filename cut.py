#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       cut.py
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
from OsmData import OsmData, Map, LON, LAT, ACTION, MODIFY, TAG, CREATE, REF

if sys.version_info[0] < 3:
  reload(sys)
  sys.setdefaultencoding("utf-8")          # a hack to support UTF-8 

def main():
  if len(sys.argv) != 1:
    return 0
  wData = OsmData() # Way
  nData = OsmData() # Nodes
  wData.read(sys.stdin)
  wData.read(sys.stdin)
  nData.read(sys.stdin)
  nData.read(sys.stdin)
  
  ids = nData.nodes.keys()
  if sys.version_info[0] >= 3:
    ids = list(ids)
  if len(ids) != 2:
    return 0
  
  way = wData.ways.popitem()
  way1 = (way[0], way[1].copy())
  way2 = (-1 - abs(way[0]), {})
  way2[1][TAG] = way1[1][TAG].copy()
  way1[1][REF] = []
  way2[1][REF] = []
  way1[1][ACTION] = MODIFY
  way2[1][ACTION] = CREATE
  
  isNewWay = False
  isNewWayClosed = False
  cutStart = 0
  for nd in way[1][REF]:
    if nd == ids[0] or nd == ids[1]:
      if isNewWay == False:
        way1[1][REF].append(nd)
        cutStart = nd
      else:
        way2[1][REF].append(nd)
        way2[1][REF].append(cutStart)
        isNewWayClosed = True
      isNewWay = not isNewWay
    if isNewWay:
      if not isNewWayClosed:
        way2[1][REF].append(nd)
    else:
      way1[1][REF].append(nd)
  wData.ways[way1[0]] = way1[1]
  wData.ways[way2[0]] = way2[1]
  wData.addcomment("Done.")
  wData.write(sys.stdout)
  return 0

if __name__ == '__main__':
  main()
