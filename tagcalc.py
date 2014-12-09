#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       regexp.py {NewTag} {Formula}
#       
#       Made from regexp.py ( Copyright 2011 Hind <foxhind@gmail.com> )
#       by OverQuantum, 2014-12-06 - 2014-12-09
#
#       Formula = [ <fix string> ] [ #tag=<tag># ] [ <fix string> ] [ #p=<param># ] [ <fix string> ]
#       <tag> - tag name (key) of this object
#       <param> =    lat / lon / uid / ver / user / chg / nodes / ways / rels
#       uid - user id; nodes - valid for ways and relations; lat and lon works only for nodes
#       note: <fix string> should contain "" to have " in result (due to command line interface)
#
#       example:  regexp.py "name" "Height #tag=ele#"
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
import re
import copy
import locale
from OsmData import OsmData, ACTION, MODIFY, TAG, LAT, LON, UID, VERSION, USER, CHANGESET, REF, NODES, WAYS, RELATIONS

if sys.version_info[0] < 3:
    reload(sys)
    sys.setdefaultencoding("utf-8")                            # a hack to support UTF-8 

def process(objects, newtag, formula, objtype):
    num = 0
    tagmatches=re.findall('#tag=[^#]*#',formula)               #find tags
    parammatches=re.findall('#p=[^#]*#',formula)               #find params
    for objid in objects.keys():
        prevvalue=''
        if newtag in objects[objid][TAG]:
            prevvalue=objects[objid][TAG][newtag]
        result=formula
        for match in tagmatches:
            tagname=re.search('#tag=(.*)#',match).group(1)     #extract tag name from match
            repl=''
            if tagname in objects[objid][TAG]:
                repl=objects[objid][TAG][tagname]              #get tag value
            result=re.sub(match,repl,result)                   #replace match with tag value
        for match in parammatches:
            paramname=re.search('#p=(.*)#',match).group(1)     #extract param name from match
            repl=''
            #switch on paramname
            if paramname == 'lat' and LAT in objects[objid]:
                repl=str(format(objects[objid][LAT]))
            elif paramname == 'lon' and LON in objects[objid]:
                repl=str(format(objects[objid][LON]))
            elif paramname == 'uid' and UID in objects[objid]:
                repl=str(objects[objid][UID])
            elif paramname == 'ver' and VERSION in objects[objid]:
                repl=str(objects[objid][VERSION])
            elif paramname == 'user' and USER in objects[objid]:
                repl=str(objects[objid][USER])
            elif paramname == 'chg' and CHANGESET in objects[objid]:
                repl=str(objects[objid][CHANGESET])
            elif paramname == 'nodes' and REF in objects[objid]:
                if objtype==2:
                    repl=str(len(objects[objid][REF]))
                elif objtype==3:
                    repl=str(len(objects[objid][REF][NODES]))
            elif paramname == 'ways' and objtype==3 and REF in objects[objid]:
                    repl=str(len(objects[objid][REF][WAYS]))
            elif paramname == 'rels' and objtype==3 and REF in objects[objid]:
                    repl=str(len(objects[objid][REF][RELATIONS]))
            result=re.sub(match,repl,result)                   #replace match with param value
        if result != prevvalue:                                #only if changed
            objects[objid][TAG][newtag] = result
            objects[objid][ACTION] = MODIFY
            num += 1
    return num

def main():
    if len(sys.argv) != 3:
        return 0
    rdata = OsmData()
    data = OsmData()
    rdata.read(sys.stdin)
    data.read(sys.stdin)
    
    codeset = locale.getdefaultlocale()[1]
    newtag = unicode(sys.argv[1], codeset)
    formula = unicode(sys.argv[2], codeset)
    
    nodes = process(data.nodes, newtag, formula,1)
    ways = process(data.ways, newtag, formula,2)
    relations = process(data.relations, newtag, formula,3)
    
    data.addcomment("Done. " + str(nodes) + " nodes, " + str(ways) + " ways and " + str(relations) + " relations changed.")
    data.write(sys.stdout)
    return 0

if __name__ == '__main__':
    main()
