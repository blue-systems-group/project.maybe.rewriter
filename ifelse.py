import re
from lib import clean_string, find_block

class IfElseAlternative(object):
  def __init__(self, offset, start, end, content):
    self.offset = offset
    self.start = start - offset
    self.end = end - offset
    assert self.start > 0, "%d should be greater than zero" % (self.start,)
    assert self.end > 0, "%d should be greater than zero" % (self.end,)
    self.content = content

  def __repr__(self):
    return "[{start}:{end} {content}]".format(start=self.start, end=self.end, content=self.content)

  @property
  def as_dict(self):
    return {'value': self.value,
            'start': self.start,
            'end': self.end}

class IfElseStatement(object):
  def __init__(self, start, line, end=None, ignored=False):
    self.start = start
    self.line = line
    self.end = end
    self.ignored = ignored
    self.alternatives = []
    self.content = None

  def __repr__(self):
    return "{{{maybe_type} {start}:{end} {label}}}".format(maybe_type=self.maybe_type,
                                                           start=self.start, end=self.end,
                                                           label=self.label)
  @property
  def as_dict(self):
    return {'type': self.maybe_type,
            'label': self.label,
            'content': self.content,
            'line': self.line,
            'alternatives': [a.as_dict for a in self.alternatives]}

BLOCK_START_PATTERN = re.compile(r"""\bif\s*\(""")
ELSE_PREVIOUS_PATTERN = re.compile(r"""^\s+esle""")
BRACE_PATTERN = re.compile(r"""^\s*{""")

def match_to_block(match, cleaned_content, content):
  assert cleaned_content[match.end() - 1] == "(", "Block starts with %s" % (cleaned_content[match.end() - 1],)
  condition_end, condition_buffer = find_block(cleaned_content, match.end() - 1, "(", ")")
  brace_match = BRACE_PATTERN.match(cleaned_content[condition_end:])
  line = len(content[:match.start()].splitlines()) + 1
  if not brace_match:
    return IfElseStatement(match.start(), line, ignored=True)

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
  cleaned_content = clean_string(content)
  
  for match in find_blocks(cleaned_content):
    if_else_block = match_to_block(match, cleaned_content, content)
    statements.append(if_else_block)
  return statements