#!/usr/bin/python
import sys, os, io, re
import argparse, json

def remove_comments(content):
  MULTI_LINE_COMMENT_PATTERN = re.compile(r"""(?s)/\*.*?\*/""")
  SINGLE_LINE_COMMENT_PATTERN = re.compile(r"""(?m)//.*$""")

  content = MULTI_LINE_COMMENT_PATTERN.sub(" ", content)
  content = SINGLE_LINE_COMMENT_PATTERN.sub(" ", content)
  
  return content


def is_block(string):
  return (string.count("{") - string.count("}") == 0)


ALTERNATIVE_START_PATTERN_ONE = re.compile(r"""^\s*else\s*{""")
ALTERNATIVE_START_PATTERN_TWO = re.compile(r"""^\s*else\sif\s*{""")

def match_to_block(match, content):
  #print match.group(0)[:-1]
  string = match.group(0)[:-1]
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
#  print content[match.start():buffer_end]
#  print "==================="
  return content[match.start():buffer_end]


BLOCK_START_PATTERN = re.compile(r"""^(?m)(?P<indent>[^\S\n]*)if\s*\((?P<condition>.+?)\)\s*{""")


def record_blocks(content):
  statements = []
  for match in BLOCK_START_PATTERN.finditer(content):
    #print match.group(0)[:-1]
    if_else_block = match_to_block(match, content)
#    print if_else_block
#    print "============"
    statements.append(if_else_block)
  return statements


if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='Find if-else blocks.')
  parser.add_argument('-source', type=str, help="Source dir to search for \
                                                if-else blocks.")
  args = parser.parse_args()
  possible_entensions = ['.java']
  dont_parse = ['ClipData.java', 'IntentResolver.java', \
      'DocumentsActivity.java', 'VideoEditorActivity.java', \
      'CameraActivity.java', 'DriverRS.java.template']
  
  for root, dirs, files in os.walk(args.source):
    for file in files:
      basename, ext = os.path.splitext(file)
      if (ext in possible_entensions) and (file not in dont_parse):
        data_to_print = {}
        data_to_print[root+"/"+file] = []
        f = open(root+"/"+file, "r")
        file_content = f.read()
        inter_file_content = remove_comments(file_content)
        blocks = record_blocks(inter_file_content)
        for block in blocks:
          data_to_print[root+"/"+file].append(block)
        print json.dumps(data_to_print)
