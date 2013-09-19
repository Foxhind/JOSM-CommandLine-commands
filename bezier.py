#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       bezier.py {Points} {Segments}
#       
#       Copyright 2011 Hind <foxhind@gmail.com>
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
from OsmData import OsmData, LON, LAT, TAG, REF, NODES

def main():
  if len(sys.argv) != 3:
    return 0
  segments = int(sys.argv[2])
  pointlist = (sys.argv[1].split(';'))
  coordlist = []
  for point in pointlist:
    coords = point.split(',')
    coordlist.append(projections.from4326((float(coords[0]), float(coords[1])), "EPSG:3857"))
  if len(coordlist) < 3:
    sys.stdout.write("<!--Too few control points-->")
    return 0
  if segments == 0: # optimal number of segments
    for i in range(0, len(coordlist) - 2):
      P1 = coordlist[i]
      P2 = coordlist[i+1]
      P1P2 = (P2[0]-P1[0], P2[1]-P1[1])
      P1P2abs = math.sqrt(P1P2[0]*P1P2[0] + P1P2[1]*P1P2[1])
      segments += math.ceil(math.log(P1P2abs, 4)) # cat's magic formula
  
  tData = OsmData()
  wayid = tData.addway()
  step = 1.0 / segments
  for i in range(segments + 1):
    t = step * i
    node = projections.to4326(getpoint(coordlist, t), "EPSG:3857")
    nodeid = tData.addnode()
    tData.nodes[nodeid][LON] = node[0]
    tData.nodes[nodeid][LAT] = node[1]
    tData.ways[wayid][REF].append(nodeid)
  tData.addcomment("Done.")
  tData.write(sys.stdout)
  return 0

def getpoint(points, t):
  Bx = 0
  By = 0
  length = len(points)
  n = length - 1
  for i in range(0, length):
    bin = ni(n, i) * pow(t, i) * pow(1.0 - t, n - i)
    Bx = Bx + bin * points[i][0]
    By = By + bin * points[i][1]
  return (Bx, By)

def ni(n, i):
  nominator = 1
  denominator = 1
  for u in range(1, n-i+1):
    nominator *= (u + i)
    denominator *= u
  return nominator / denominator

if __name__ == '__main__':
  main()

