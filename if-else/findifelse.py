#!/usr/bin/python
import sys, os, io, re
import argparse, json
import pickle

def set_default(obj):
  if isinstance(obj, set):
    return list(obj)

class IfElseAlternative(object):
  def __init__(self, value, content):
    self.value = value
    self.content = content

  def __repr__(self):
    return "{{'{value}':'{content}'}}".format(value=self.value, \
                                          content=self.content)

class IfElseStatement(object):

  def __init__(self, condition, start, end=None):
    self.content = None
    self.condition = condition
    self.start = start
    self.end = end
    self.alternatives = []

  @property
  def as_dict(self):
    return {'condition': '('+self.condition+')',
            'condition_len': len(self.condition),
            'content': self.content,
            'alternatives': {a for a in self.alternatives}}


def is_block(string):
  return (string.count("{") - string.count("}") == 0)

BLOCK_START_PATTERN = re.compile(r"""^(?m)(?P<indent>[^\S\n]*)if\s*\((?s)(?P<condition>.+?)\)\s*{""")
ALTERNATIVE_START_PATTERN_ONE = re.compile(r"""^\s*else\s*{""")
ALTERNATIVE_START_PATTERN_TWO = re.compile(r"""^\s*else\sif\s*\((?P<condition>.+?)\)\s*{""")

def match_to_block(match, content):
  #print match.group(0)[:-1]
  condition = match.group('condition')
  if_else_block = IfElseStatement(condition, match.start())
  #print if_else_block.as_dict
  buffer_start = match.end() - 1

  value = 0
  while True:
    buffer_end = buffer_start
    search_start = buffer_start

    while True:
      buffer_increment = content[search_start:].find("}")
      assert buffer_increment != -1, "Unmatched braces."
      buffer_end += buffer_increment + 1
      block_buffer = content[buffer_start:buffer_end]
      if is_block(block_buffer):
        if_else_block.alternatives.append(IfElseAlternative(value,
                                                        block_buffer[1:-1]))
        value += 1
        break
      else:
        search_start += buffer_increment + 1
    else_match = ALTERNATIVE_START_PATTERN_ONE.match(content[buffer_end:])
    if else_match != None:
      buffer_start = buffer_end + else_match.end() - 1
    else:
      else_match = ALTERNATIVE_START_PATTERN_TWO.match(content[buffer_end:])
      if else_match != None:
        buffer_start = buffer_end + else_match.end() - 1
      else:
        break
  if_else_block.content = content[match.start()-1:buffer_end].strip('\n')
  return if_else_block

def extract_blocks(content, statements=None):
  if not statements:
    statements = []
  content = remove_comments_and_strings(content)

  for match in BLOCK_START_PATTERN.finditer(content):
    #print match.group(0)[:-1]
    if_else_block = match_to_block(match, content)
    statements.append(if_else_block.as_dict)
  return statements

def remove_comments_and_strings(content):
  MULTI_LINE_COMMENTS_PATTERN = re.compile(r"""(?s)/\*.*?\*/""")
  SINGLE_LINE_COMMENTS_PATTERN = re.compile(r"""(?m)//.*$""")

  SINGLE_QUOTE_STRING_PATTERN= re.compile(r"""'(?P<quoted>(?:\\'|[^'\n])*?)'""")
  DOUBLE_QUOTE_STRING_PATTERN= re.compile(r'"(?P<quoted>(?:\\"|[^"\n])*?)"')
  
  content = MULTI_LINE_COMMENTS_PATTERN.sub("", content)
  content = SINGLE_LINE_COMMENTS_PATTERN.sub("", content)
  content = SINGLE_QUOTE_STRING_PATTERN.sub("", content)
  content = DOUBLE_QUOTE_STRING_PATTERN.sub("", content)
  
  return content

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='Find if-else blocks.')
  parser.add_argument('-source', type=str, help="Source dir to search for \
                                                if-else blocks.")
  args = parser.parse_args()
  possible_entensions = ['.java']
  
  for root, dirs, files in os.walk(args.source):
    for file in files:
      basename, ext = os.path.splitext(file)
      if ext in possible_entensions:
        data_to_print = {}
        data_to_print[root+"/"+file] = []
        f = open(root+"/"+file, "r")
        file_content = f.read()
        blocks = extract_blocks(file_content)
        for block in blocks:
          data_to_print[root+"/"+file].append(block)
        print json.dumps(data_to_print, default = set_default)
        #print type(data_to_print)
        #print json.dumps(data_to_print)
