#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       regexp.py {Expression} {What}
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
import re
import copy
import locale
from OsmData import OsmData, ACTION, MODIFY, TAG

if sys.version_info[0] < 3:
  reload(sys)
  sys.setdefaultencoding("utf-8")          # a hack to support UTF-8 

def process(objects, search, replace, prtags, prvalues):
  num = 0
  for objid in objects.keys():
    for tag in copy.deepcopy(objects[objid][TAG].keys()):
      if prvalues:
        val = objects[objid][TAG][tag]
        oldval = val
        val = search.sub(replace, val)
        if oldval != val:
            objects[objid][TAG][tag] = val
            objects[objid][ACTION] = MODIFY
            num += 1
      if prtags:
        oldtag = tag
        tag = search.sub(replace, tag)
        if oldtag != tag:
            objects[objid][TAG][tag] = objects[objid][TAG].pop(oldtag)
            objects[objid][ACTION] = MODIFY
            num += 1
  return num

def main():
  if len(sys.argv) != 4:
    return 0
  rdata = OsmData()
  data = OsmData()
  rdata.read(sys.stdin)
  data.read(sys.stdin)
  
  codeset = locale.getdefaultlocale()[1]
  search = re.compile(unicode(sys.argv[1], codeset))
  replace = unicode(sys.argv[2], codeset)
  prtags = False
  prvalues = False
  if sys.argv[3] == 'Tags':
    prtags = True
  elif sys.argv[3] == 'Values':
    prvalues = True
  elif sys.argv[3] == 'Both':
    prtags = True
    prvalues = True
  else:
    data.addcomment("Processing data (tags, values or both) isn't selected.")
    data.write(sys.stdout)
    return 0
  
  nodes = process(data.nodes, search, replace, prtags, prvalues)
  ways = process(data.ways, search, replace, prtags, prvalues)
  relations = process(data.relations, search, replace, prtags, prvalues)
  
  data.addcomment("Done. " + str(nodes) + " nodes, " + str(ways) + " ways and " + str(relations) + " relations changed.")
  data.write(sys.stdout)
  return 0

if __name__ == '__main__':
  main()
