import re,json,os

def find_block(content, start, delimiter_left, delimiter_right):
  def is_block(string, delimiter_left, delimiter_right):
    return (string.count(delimiter_left) - string.count(delimiter_right) == 0)
  
  assert content[start] == delimiter_left, "Buffer does not start with delimiter."

  search_start = start
  buffer_end = start

  while True:
    buffer_increment = content[search_start:].find(delimiter_right)
    assert buffer_increment != -1, "Unmatched delimiters: %s" % (content[start:start+100])
    buffer_end += buffer_increment + 1
    block_buffer = content[start:buffer_end]
    if is_block(block_buffer, delimiter_left, delimiter_right):
      return buffer_end, block_buffer
    else:
      search_start += buffer_increment + 1

MULTI_LINE_COMMENTS_PATTERN = re.compile(r"""(?s)/\*.*?\*/""") 
SINGLE_LINE_COMMENTS_PATTERN = re.compile(r"""(?m)//.*$""") 

SINGLE_QUOTE_STRING_PATTERN = re.compile(r"""'(?P<quoted>(?:\\'|[^'\n])*?)'""")
DOUBLE_QUOTE_STRING_PATTERN = re.compile(r'"(?P<quoted>(?:\\"|[^"\n])*?)"')
WHITESPACE_PATTERN = re.compile(r"""(?m)\s+""")

def clean_string(string, remove_newlines=False):
  
  def equivalent_whitespace(match):
    return " " * len(match.group())

  def single_quotes(match):
    assert len(match.group()) == (len(match.group('quoted')) + 2), "Length mismatch: %d %d" % (len(match.group()), len(match.group('quoted')))
    return "'%s'" % (" " * len(match.group('quoted')),)
  
  def double_quotes(match):
    assert len(match.group()) == (len(match.group('quoted')) + 2), "Length mismatch: %d %d" % (len(match.group()), len(match.group('quoted')))
    return '"%s"' % (" " * len(match.group('quoted')),)
  
  initial_length = len(string)
  
  string = SINGLE_QUOTE_STRING_PATTERN.sub(single_quotes, string)
  string = DOUBLE_QUOTE_STRING_PATTERN.sub(double_quotes, string)
  string = MULTI_LINE_COMMENTS_PATTERN.sub(equivalent_whitespace, string)
  string = SINGLE_LINE_COMMENTS_PATTERN.sub(equivalent_whitespace, string)
  if remove_newlines:
    string = WHITESPACE_PATTERN.sub(equivalent_whitespace, string)
    assert string.find("\n") == -1, "Newlines left in string"

  assert len(string) == initial_length, "Cleaning changed string length."
  return string

class ProjectsMap(object):
  BASE_LINK = "http://platform.phone-lab.org:8080/gitweb?p={project}.git;a=blob;f={filename};hb=refs/heads/phonelab/android-4.4.4_r1/develop#l{linenumber}"

  def __init__(self, projects_file):
    self.projects = []
    for line in open(projects_file, 'rU'):
      self.projects.append(json.loads(line.strip().replace("'", '"')))

  def map_file(self, filename):
    matches = sorted([p for p in self.projects if filename.startswith(p['path'])], key=lambda p: len(p['path']))[::-1]
    if len(matches) == 0:
      return None
    else:
      return matches[0]

  def link_file(self, filename, number):
    match = self.map_file(filename)
    assert match, "%s does not match a project" % (filename,)
    return self.BASE_LINK.format(project=match['name'], filename=os.path.relpath(filename, match['path']), linenumber=number), match
