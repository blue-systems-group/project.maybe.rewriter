#!/usr/bin/python
import sys, os, io, re
import pprint


class MaybeAlternative(object):
  def __init__(self, value, offset, start, end, content):
    self.value = value
    self.offset = offset
    self.start = start - offset
    self.end = end - offset
    self.content = content


class MaybeStatement(object):
  BLOCK = "block"

  def __init__(self, maybe_type, start, end=None):
    self.maybe_type = maybe_type
    self.start = start
    self.end = end
    self.alternatives = []
    self.content = None
    self.line = None

  def __repr__(self):
    return "{{{maybe_type} {start}:{end}}}".format(maybe_type=self.maybe_type,
                                                start=self.start, end=self.end)



def is_block(string):
  return (string.count("{") - string.count("}") == 0)

def remove_comments_and_strings(content):
  MULTI_LINE_COMMENT_PATTERN = re.compile(r"""(?s)/\*.*?\*/""")
  SINGLE_LINE_COMMENT_PATTERN = re.compile(r"""(?m)//.*$""")

  content = MULTI_LINE_COMMENT_PATTERN.sub("", content)
  content = SINGLE_LINE_COMMENT_PATTERN.sub("", content)
  
  return content

ALTERNATIVE_START_PATTERN = re.compile(r"""^\s*else\s*{""")

def match_to_block(match, content):
  maybe_block = MaybeStatement(MaybeStatement.BLOCK, match.start())
  maybe_block.line = len(content[:match.start()].splitlines()) + 1
  buffer_start = match.end() - 1

  value = 0
  while True:
    buffer_end = buffer_start
    search_start = buffer_start

    while True:
      buffer_increment = content[search_start:].find("}")
      #assert buffer_increment != -1, "Unmatched braces."
      buffer_end += buffer_increment + 1
      block_buffer = content[buffer_start:buffer_end]
      if is_block(block_buffer):
        maybe_block.alternatives.append(MaybeAlternative(value,
                                          maybe_block.start,
                                          buffer_start + 1,
                                          buffer_end,
                                          block_buffer[1:-1]))
        value += 1
        break
      else:
        search_start += buffer_increment + 1
    else_match = ALTERNATIVE_START_PATTERN.match(content[buffer_end:])
    if else_match != None:
      buffer_start = buffer_end + else_match.end() - 1
    else:
      break
  maybe_block.end = buffer_end
  maybe_block.content = content[maybe_block.start:maybe_block.end]
  return maybe_block.content


BLOCK_START_PATTERN = re.compile(r"""^(?m)(?P<indent>[^\S\n]*)if\s*\((?P<label>.+?)\)\s*{""")


def record_blocks(content):
  statements = []
  for match in BLOCK_START_PATTERN.finditer(content):
    #print match.group(0)[:-1]
    if_else_block = match_to_block(match, content)
    statements.append(if_else_block)
  return statements


if __name__ == '__main__':
  dont_search = ['ClipData.java', 'IntentResolver.java', \
      'DocumentsActivity.java', 'VideoEditorActivity.java', \
      'DriverRS.java.template', 'CameraActivity.java']
  for root, dirs, files in os.walk("/home/jerry/WORKING_DIRECTORY"):
    for file in files:
      file_name = file.split('.')
      if len(file_name) > 1:
        if file_name[1] == 'java':
          print root+"/"+file
          if file in dont_search:
            continue
          else:
            f = open(root+"/"+file, "r")
            file_content = f.read()
            inter_file_content = remove_comments_and_strings(file_content)
            blocks = record_blocks(inter_file_content)
            for block in blocks:
              print root+"/"+file
              print block
              print "==================================="
