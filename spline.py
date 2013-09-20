#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       spline.py {Points} {Segments}
#       
#       Copyright 2013 Eric Ladner <eric.ladner@gmail.com>
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
import numpy
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
  if len(coordlist) < 4:
    sys.stdout.write("<!--Too few control points-->")
    return 0
  if segments < 0:
    sys.stdout.write("<!--Segments must be greater than zero-->");
  
  tData = OsmData()
  wayid = tData.addway()
  step = 1.0 / segments
  for j in range (1, len(coordlist)-2):
    # for segments other than the first, skip the first point since it's the
    # last point of the previous segment - otherwise you'll get overlapping points
    # at the segment ends.
    if j > 1:
      segs = range(1,segments+1)
    else:
      segs = range(segments+1)
    for i in segs:
      t = step * i
      node = projections.to4326(spline_4p(t, coordlist[j-1], coordlist[j], coordlist[j+1], coordlist[j+2]), "EPSG:3857")
      nodeid = tData.addnode()
      tData.nodes[nodeid][LON] = node[0]
      tData.nodes[nodeid][LAT] = node[1]
      tData.ways[wayid][REF].append(nodeid)
  tData.addcomment("Done.")
  tData.write(sys.stdout)
  return 0

def spline_4p( t, p_1, p0, p1, p2 ):
  """ Catmull-Rom
      (Ps can be numpy vectors or arrays too: colors, curves ...)
  """
  # wikipedia Catmull-Rom -> Cubic_Hermite_spline
  # 0 -> p0,  1 -> p1,  1/2 -> (- p_1 + 9 p0 + 9 p1 - p2) / 16
  # assert 0 <= t <= 1
  return (
    t*((2-t)*t - 1)   * numpy.array(p_1[0:2])
    + (t*t*(3*t - 5) + 2) * numpy.array(p0[0:2])
    + t*((4 - 3*t)*t + 1) * numpy.array(p1[0:2])
    + (t-1)*t*t         * numpy.array(p2[0:2]) ) / 2

if __name__ == '__main__':
  main()

