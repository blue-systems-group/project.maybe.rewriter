#!/usr/bin/env python

import re,os,argparse,csv,sys
from lib import clean_string, find_block, ProjectsMap, MissingProject

class TimerLine(object):
  def __init__(self, timer_type, line, content, file_line_count):
    self.timer_type = timer_type
    self.line = line
    self.content = content
    self.file_line_count = file_line_count

  @classmethod
  def parse(cls, string):
    csv_list = csv.reader(string)
    timer_type      = csv_list[0]
    link            = csv_list[1]
    project_name    = csv_list[2]
    basename        = csv_list[3]
    full_path       = csv_list[4]
    file_line_count = csv_list[5]
    line            = csv_list[6]
    content         = csv_list[7]
    return TimerLine(timer_type, line, content, file_line_count)

TIMER_PATTERN = re.compile(r"""(?m)^.*(int|long).*(?P<timer_type>(?:(?:TIMEOUT|INTERVAL|RATE|MS|DELAY|DURATION|PERIOD|NUM))).*=.*[^\"1-9];$""")

def record_timers(content, statements=None):
  if not statements:
    statements = []
  cleaned_content = clean_string(content)

  file_line_count = len(content.splitlines())

  for match in TIMER_PATTERN.finditer(content):
    line = len(content[:match.end()].splitlines())
    statements.append(TimerLine(match.group('timer_type').strip(), line, match.group().strip(), file_line_count))

  return statements

def main(args):
  projects = ProjectsMap(args.projects)
  files = list(set([os.path.normpath(l.strip()) for l in open(args.toparse, 'rU')]))
  
  writer = csv.writer(sys.stdout)
  
  for input_file in files:
    rows = []
    try:
      timers = record_timers(open(input_file, 'rU').read())
      for timer in timers:
        link, project = projects.link_file(input_file, timer.line)
        rows.append([timer.timer_type, link, project['name'], os.path.basename(input_file), input_file, timer.file_line_count, timer.line, timer.content])
      writer.writerows(rows)
    except MissingProject:
      pass
    except Exception, e:
      print >>sys.stderr, "SKIPPING %s: %s" % (input_file, e)
      writer.writerow(["S", input_file])
  
if __name__=='__main__':
  parser = argparse.ArgumentParser(description='Find timers in AOSP.')
  parser.add_argument('toparse', type=str, help="List of files to parse, relative to current directory.")
  parser.add_argument('projects', type=str, help="Filename to project mapping for files.")
  args = parser.parse_args()
  main(args)
