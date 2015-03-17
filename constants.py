#!/usr/bin/env python

import re,os,argparse,csv,sys
from lib import clean_string, find_block, ProjectsMap, MissingProject

class ConstantLine(object):
  def __init__(self, line, content):
    self.line = line
    self.content = content

CONSTANT_PATTERN = re.compile(r"""(?m)^.*\bstatic final int\b.*$""")

def record_constants(content, statements=None):
  if not statements:
    statements = []
  cleaned_content = clean_string(content)

  for match in CONSTANT_PATTERN.finditer(content):
    line = len(content[:match.end()].splitlines())
    statements.append(ConstantLine(line, match.group().strip()))

  return statements

def main(args):
  projects = ProjectsMap(args.projects)
  files = list(set([os.path.normpath(l.strip()) for l in open(args.toparse, 'rU')]))
  
  writer = csv.writer(sys.stdout)
  
  for input_file in files:
    rows = []
    try:
      constants = record_constants(open(input_file, 'rU').read())
      for constant in constants:
        link, project = projects.link_file(input_file, constant.line)
        rows.append([link, project['name'], os.path.basename(input_file), input_file, constant.line, constant.content])
      writer.writerows(rows)
    except MissingProject:
      pass
    except Exception, e:
      print >>sys.stderr, "SKIPPING %s: %s" % (input_file, e)
      writer.writerow(["S", input_file])
  
if __name__=='__main__':
  parser = argparse.ArgumentParser(description='Find constants in AOSP.')
  parser.add_argument('toparse', type=str, help="List of files to parse, relative to current directory.")
  parser.add_argument('projects', type=str, help="Filename to project mapping for files.")
  args = parser.parse_args()
  main(args)
