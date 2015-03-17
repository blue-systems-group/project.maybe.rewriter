#!/usr/bin/env python

import re,os,argparse,csv,sys
from lib import clean_string, find_block, ProjectsMap, MissingProject

class TimerLine(object):
  def __init__(self, timer_type, line):
    self.timer_type = timer_type
    self.line = line

TIMER_PATTERN = re.compile(r"""(?m)^.*(?P<timer_type>(?:\b(?:AlarmManager|PendingIntent|ScheduledThreadPoolExecutor|TimeUnit)\b)|(?:TIMEOUT|INTERVAL)).*$""")

def record_timers(content):
  if not statements:
    statements = []
  cleaned_content = clean_string(content)

  for match in TIMER_PATTERN.finditer(content):
    line = len(content[:match.end()].splitlines())
    statements.append(TimerLine(match.group('timer_type').strip(), line))

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
        rows.append([timer.timer_type, link, project['name'], os.path.basename(input_file), input_file, statement.line])
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
