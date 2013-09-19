#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       circle.py {Center} {Radius} {Sides}
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
from OsmData import OsmData, LON, LAT, TAG, REF, NODES

def main():
	if len(sys.argv) != 4:
		return 0
	sides = int(sys.argv[3])
	if sides < 3:
		return 0
	coords = (sys.argv[1].split(','))
	lon = float(coords[0])
	lat = float(coords[1])
	radius = float(sys.argv[2])/math.cos(math.radians(lat))
	if radius <= 0:
		return 0
	startangle = 0
	coords_m = projections.from4326((lon,lat), "EPSG:3857")
	
	tData = OsmData()
	wayid = tData.addway()
	for i in range(sides):
		angle = startangle + 2*math.pi*i/sides
		x = coords_m[0] + radius * math.cos(angle)
		y = coords_m[1] + radius * math.sin(angle)
		node = projections.to4326((x, y), "EPSG:3857")
		nodeid = tData.addnode()
		tData.nodes[nodeid][LON] = node[0]
		tData.nodes[nodeid][LAT] = node[1]
		tData.ways[wayid][REF].append(nodeid)
	tData.ways[wayid][REF].append(tData.ways[wayid][REF][0])
	tData.addcomment("Done.")
	tData.write(sys.stdout)
	return 0

if __name__ == '__main__':
	main()

