import re

class MaybeAlternative(object):
  def __init__(self, start, end, content):
    self.start = start
    self.end = end
    self.content = content

  def __repr__(self):
    return "[{start}:{end} {content}]".format(start=self.start, end=self.end, content=self.content)

class MaybeStatement(object):
  ASSIGNMENT = "assignment"
  BLOCK = "block"

  def __init__(self, maybe_type, start, label, end=None):
    self.maybe_type = maybe_type
    self.start = start
    self.end = end
    self.label = label
    self.alternatives = []

  def __repr__(self):
    return "\{{maybe_type} {start}:{end} {label}\}".format(maybe_type=self.maybe_type,
                                                           start=self.start, end=self.end,
                                                           label=self.label)

  @property
  def is_assignment(self):
    return self.maybe_type == MaybeStatement.ASSIGNMENT

  @property
  def is_block(self):
    return self.maybe_type == MaybeStatement.BLOCK

ASSIGNMENT_PATTERN = re.compile(r"""(?xum)
                                ^(?P<indent>[^\S\n]*)
                                (?P<variable>.*?)
                                =\s*maybe\s*
                                \((?P<label>.+?)\)\s*
                                (?P<alternatives>(?:[^,;]+,)+\s*
                                [^,\n]+)\s*?
                                ;$""")

def record_assignments(content, statements={}):
  def record_assignment(match):
    maybe_statement = MaybeStatement(MaybeStatement.ASSIGNMENT, match.start(), match.group('label').strip(), match.end())
    assert not statements.has_key(maybe_statement.label)
    alternative_start = match.start('alternatives')
    for alternative in match.group('alternatives').split(','):
      alternative_content = alternative.strip()
      alternative_start += len(alternative) - len(alternative.lstrip())
      maybe_alternative = MaybeAlternative(alternative_start, alternative_start + len(alternative_content), alternative_content)
      maybe_statement.alternatives.append(maybe_alternative)
      alternative_start += len(alternative.lstrip()) + 1
    statements[maybe_statement.label] = maybe_statement
  
  for match in ASSIGNMENT_PATTERN.finditer(content):
    record_assignment(match)

  return statements

def replace_assignments(content):
  labels = {}
  def replace_assignment(match):
    label = match.group('label').strip()
    assert not labels.has_key(label)
    indent = match.group('indent')
    variable = match.group('variable').rstrip()
    separator = "\n{indent}}} or {{\n".format(indent=indent)
    name = re.split(r"""\s+""", match.group('variable').strip())[-1]
    inner = separator.join(["{indent}  {name} = {a};".format(indent=indent, name=name, a=a.strip()) for a in match.group('alternatives').split(',')])
    replacement =  """
{indent}{variable};
{indent}maybe ({label}) {{
{inner}
{indent}}}
""".format(indent=indent,
           variable=variable,
           label=label,
           inner=inner)
    labels[label] = replacement
    return replacement
  
  output = ASSIGNMENT_PATTERN.sub(replace_assignment, content)
  return output, labels

MULTI_LINE_COMMENTS_PATTERN= re.compile(r"""(?s)/\*.*?(?:\*/|$)""") 
SINGLE_LINE_COMMENTS_PATTERN= re.compile(r"""(?m)//.*$""") 

SINGLE_QUOTE_STRING_PATTERN= re.compile(r"""'(?:\\'|[^'\n])*'""")
DOUBLE_QUOTE_STRING_PATTERN= re.compile(r'"(?:\\"|[^"\n])*"')

def clean_block(string):
  string = MULTI_LINE_COMMENTS_PATTERN.sub("", string)
  string = SINGLE_LINE_COMMENTS_PATTERN.sub("", string)
  string = SINGLE_QUOTE_STRING_PATTERN.sub("", string)
  string = DOUBLE_QUOTE_STRING_PATTERN.sub("", string)
  return string

def is_block(string):
  return (string.count("{") - string.count("}") == 0)

def match_to_block(match, content):
  maybe_block = MaybeStatement(MaybeStatement.BLOCK, match.start(), match.group('label').strip())
  buffer_start = match.end() - 1

  while True:
    buffer_end = buffer_start
    search_start = buffer_start
    
    while True:
      buffer_increment = content[search_start:].find("}")
      assert buffer_increment != -1, "Unmatched braces."
      buffer_end += buffer_increment + 1
      block_buffer = content[buffer_start:buffer_end + 1]
      if is_block(clean_block(block_buffer)):
        maybe_block.alternatives.append(MaybeAlternative(buffer_start + 1,
                                                         buffer_end,
                                                         block_buffer[1:-1]))
        break
      else:
        search_start += buffer_increment + 1
    or_match = ALTERNATIVE_START_PATTERN.match(content[buffer_end:])
    if or_match != None:
      buffer_start = buffer_end + or_match.end() - 1
    else:
      break
  maybe_block.end = buffer_end
  return maybe_block

BLOCK_START_PATTERN = re.compile(r"""^(?m)(?P<indent>[^\S\n]*)maybe\s*\((?P<label>.+?)\)\s*{""")
ALTERNATIVE_START_PATTERN = re.compile(r"""^\s*or\s*{""")

def record_blocks(content, statements={}):
  for match in BLOCK_START_PATTERN.finditer(content):
    maybe_block = match_to_block(match, content)
    assert not statements.has_key(maybe_block.label)
    statements[maybe_block.label] = maybe_block
  return statements
