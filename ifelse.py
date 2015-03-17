#!/usr/bin/env python

import re,os,argparse,csv,sys
from lib import clean_string, find_block, ProjectsMap, MissingProject

class IfElseAlternative(object):
  def __init__(self, offset, start, end, content):
    self.offset = offset
    self.start = start - offset
    self.end = end - offset
    assert self.start > 0, "%d should be greater than zero" % (self.start,)
    assert self.end > 0, "%d should be greater than zero" % (self.end,)
    self.content = content
    self.file_line_count = None

class IfElseStatement(object):
  def __init__(self, start, line, end=None, ignored=False, content=None):
    self.start = start
    self.line = line
    self.end = end
    self.ignored = ignored
    self.content = content
    self.alternatives = []

  @classmethod
  def ignored(cls, statements):
    return [S for S in statements if S.ignored]
  
  @classmethod
  def correct(cls, statements):
    return [S for S in statements if not S.ignored]

  @classmethod
  def ignored_count(cls, statements):
    return len(cls.ignored(statements))
  
  @classmethod
  def correct_count(cls, statements):
    return len(cls.correct(statements))

  @property
  def as_dict(self):
    return {'content': self.content,
            'line': self.line,
            'alternatives': [a.as_dict for a in self.alternatives]}
  
BLOCK_START_PATTERN = re.compile(r"""\bif\s*\(""")
ELSE_PREVIOUS_PATTERN = re.compile(r"""^\s+esle""")
BRACE_PATTERN = re.compile(r"""^\s*{""")
IFELSE_START_PATTERN = re.compile(r"""^\s*else\s+if\s*\(""")
ELSE_START_PATTERN = re.compile(r"""^\s*else\s*{""")

class BrokenStatement(Exception):
  pass

def match_to_block(match, cleaned_content, content):
  assert cleaned_content[match.end() - 1] == "(", "Block starts with %s" % (cleaned_content[match.end() - 1],)
  condition_end, condition_buffer = find_block(cleaned_content, match.end() - 1, "(", ")")
  block_content = content[match.end():condition_end - 1]
  brace_match = BRACE_PATTERN.match(cleaned_content[condition_end:])
  line = len(content[:match.end()].splitlines())
  ifelse_block = IfElseStatement(match.start(), line, content=block_content)
  if not brace_match:
    ifelse_block.ignored = True
    return ifelse_block
  
  buffer_start = condition_end + brace_match.end() - 1
  alternatives = [] 
  try:
    while True:
      buffer_end, block_buffer = find_block(cleaned_content, buffer_start, "{", "}")
      
      alternatives.append(IfElseAlternative(ifelse_block.start,
                                            buffer_start + 1,
                                            buffer_end,
                                            content[buffer_start + 1:buffer_end - 1]))
      
      ifelse_match = IFELSE_START_PATTERN.match(cleaned_content[buffer_end:])
      else_match = ELSE_START_PATTERN.match(cleaned_content[buffer_end:])

      if ifelse_match != None:
        condition_end, unused = find_block(cleaned_content, buffer_end + ifelse_match.end() - 1, "(", ")")
        brace_match = BRACE_PATTERN.match(cleaned_content[condition_end:])
        if not brace_match:
          raise BrokenStatement()
        buffer_start = condition_end + brace_match.end() - 1
      elif else_match != None:
        buffer_start = buffer_end + else_match.end() - 1
      else:
        break
  except BrokenStatement:
    ifelse_block.ignored = True
  else:
    ifelse_block.ignored = False
    for a in alternatives:
      ifelse_block.alternatives.append(a)
  finally:
    return ifelse_block

def find_blocks(content):
  matches = []
  for match in BLOCK_START_PATTERN.finditer(content):
    previous = content[0:match.start()]
    previous = previous[::-1]
    if not ELSE_PREVIOUS_PATTERN.match(previous):
      matches.append(match)
  return matches

def record_blocks(content, statements=None):
  if not statements:
    statements = []
  file_line_count = len(content.splitlines())
  cleaned_content = clean_string(content)
  
  for match in find_blocks(cleaned_content):
    if_else_block = match_to_block(match, cleaned_content, content)
    if_else_block.file_line_count = file_line_count
    statements.append(if_else_block)
  return statements

def main(args):
  projects = ProjectsMap(args.projects)
  files = list(set([os.path.normpath(l.strip()) for l in open(args.toparse, 'rU')]))
  
  writer = csv.writer(sys.stdout)
  
  for input_file in files:
    correct, ignored = [], []
    try:
      statements = record_blocks(open(input_file, 'rU').read())
      for statement in statements:
        link, project = projects.link_file(input_file, statement.line)
        if not statement.ignored:
          correct.append(["C", link, project['name'], os.path.basename(input_file), input_file, statement.file_line_count, statement.line, len(statement.alternatives), len(statement.content), statement.content])
        else:
          ignored.append(["I", link, project['name'], os.path.basename(input_file), input_file, statement.file_line_count, statement.line])
      writer.writerows(correct)
      writer.writerows(ignored)
    except MissingProject:
      pass
    except Exception, e:
      print >>sys.stderr, "SKIPPING %s: %s" % (input_file, e)
      writer.writerow(["S", input_file])
  
if __name__=='__main__':
  parser = argparse.ArgumentParser(description='Find if-else statements in AOSP.')
  parser.add_argument('toparse', type=str, help="List of files to parse, relative to current directory.")
  parser.add_argument('projects', type=str, help="Filename to project mapping for files.")
  args = parser.parse_args()
  main(args)
