#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       fillet.py {Radius} {Segments}
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
from OsmData import OsmData, Map, LON, LAT, ACTION, MODIFY, TAG, CREATE, REF, NODES, WAYS

if sys.version_info[0] < 3:
  reload(sys)
  sys.setdefaultencoding("utf-8")          # a hack to support UTF-8 

def project(vector, pivot, point):
  k1 = -vector[0]/vector[1]
  b1 = (vector[1]*point[1] + vector[0]*point[0]) / vector[1]
  k2 = vector[1]/vector[0]
  b2 = (vector[0]*pivot[1] - vector[1]*pivot[0]) / vector[0]
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
    segments = math.ceil(math.log(P1P2abs, 4) * (math.cos((a2-a1)/2) + 1.5)) # cat's magic formula
    
  interval = (a2 - a1) / segments
  for n in range(1, segments):
    val = a1 + interval * n
    arc.append(( C[0] + r * math.cos(val), C[1] + r * math.sin(val) ))
  arc.append(P2)
  return arc

def main():
  if len(sys.argv) != 3:
    return 0
  wData = OsmData() # Way
  nData = OsmData() # Nodes
  wData.read(sys.stdin)
  wData.read(sys.stdin)
  nData.read(sys.stdin)
  radius = float(sys.argv[1])
  segments = int(sys.argv[2])
  
  nodes = []
  usednodes = set()
  for way in wData.ways.items():
    for key in nData.nodes.keys():
      if key in usednodes:
        continue
      try:
        index = way[1][REF].index(key)
      except ValueError:
        pass
      else:
        lastindex = len(way[1][REF]) - 1
        if way[1][REF][0] == way[1][REF][lastindex]: # polygon
          if index == 0:
            nodes.append([way[1][REF][lastindex-1], key, way[1][REF][index+1], way[0], index]) # previous node, node for fillet, next node, way
            usednodes.add(key)
          else:
            nodes.append([way[1][REF][index-1], key, way[1][REF][index+1], way[0], index])
            usednodes.add(key)
        else: # way
          if index > 0 and index < lastindex:
            nodes.append([way[1][REF][index-1], key, way[1][REF][index+1], way[0], index])
            usednodes.add(key)
  tData = OsmData()
  tData.mergedata(nData)
  tData.mergedata(wData)
  for pack in nodes:
    M = projections.from4326( (wData.nodes[pack[0]][LON], wData.nodes[pack[0]][LAT]), "EPSG:3857") # previous node
    O = projections.from4326( (wData.nodes[pack[1]][LON], wData.nodes[pack[1]][LAT]), "EPSG:3857") # center node
    N = projections.from4326( (wData.nodes[pack[2]][LON], wData.nodes[pack[2]][LAT]), "EPSG:3857") # next node
    r = radius / math.cos(math.radians(wData.nodes[pack[1]][LAT]))
    OM = (M[0] - O[0], M[1] - O[1])
    ON = (N[0] - O[0], N[1] - O[1])
    OMabs = math.sqrt(OM[0]*OM[0] + OM[1]*OM[1])
    ONabs = math.sqrt(ON[0]*ON[0] + ON[1]*ON[1])
    cosa = (OM[0]*ON[0] + OM[1]*ON[1]) / (OMabs * ONabs)
    OCabs = r / (math.sqrt((1 - cosa) / 2))
    OMnorm = (OM[0]/OMabs, OM[1]/OMabs)
    ONnorm = (ON[0]/ONabs, ON[1]/ONabs)
    bisectrix = (OMnorm[0] + ONnorm[0], OMnorm[1] + ONnorm[1])
    bisectrixabs = math.sqrt(bisectrix[0]*bisectrix[0] + bisectrix[1]*bisectrix[1])
    bisectrixnorm = (bisectrix[0]/bisectrixabs, bisectrix[1]/bisectrixabs)
    OC = (bisectrixnorm[0]*OCabs, bisectrixnorm[1]*OCabs)
    C = (O[0]+OC[0], O[1]+OC[1])

    P1 = project(OM, O, C)
    P2 = project(ON, O, C)
    arc = createarc(C, P1, P2, r, segments)
    arcref = []
    exists = int(segments/2)
    for point in range(len(arc)):
      p = projections.to4326(arc[point], "EPSG:3857")
      if point == exists:
        tData.nodes[pack[1]][ACTION] = MODIFY
        tData.nodes[pack[1]][LON] = p[0]
        tData.nodes[pack[1]][LAT] = p[1]
        arcref.append(pack[1])
      else:
        newid = tData.addnode()
        tData.nodes[newid][LON] = p[0]
        tData.nodes[newid][LAT] = p[1]
        tData.nodes[newid][TAG] = {}
        arcref.append(newid)

    way = tData.ways[pack[3]]
    way[ACTION] = MODIFY
    lastindex = len(way[REF]) - 1
    index = way[REF].index(pack[1])
    ref = way[REF][:]
    if way[REF][0] == way[REF][lastindex] and index == 0: # polygon
      way[REF] = arcref[:]
      way[REF] += (ref[1:lastindex])
      way[REF] += [(arcref[0])]
    else: # way
      way[REF] = ref[:index] + arcref + ref[index+1:]
    tData.ways[pack[3]] = way
  tData.addcomment("Done.")
  tData.write(sys.stdout)
  #f = open("out.txt", "w")
  #tData.write(f)
  #f.close()
  return 0

if __name__ == '__main__':
  main()
