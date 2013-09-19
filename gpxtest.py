#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

reload(sys)
sys.setdefaultencoding("utf-8")          # a hack to support UTF-8 

def main():
  f = open("out.txt", "w")
  f.write(sys.argv[1] + " " + sys.argv[2] + " " + sys.argv[3])
  f.close()
  sys.stdout.write("<!--Ololo-->")
  return 0

if __name__ == '__main__':
	main()
