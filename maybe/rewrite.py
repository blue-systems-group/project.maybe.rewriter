import re

ASSIGNMENT_PATTERN = re.compile(r"""(?xum)
                                ^(?P<indent>[^\S\n]*)
                                (?P<variable>.*?)
                                =\s*maybe\s*
                                \((?P<label>.+?)\)
                                (?P<alternatives>(?:[^,;]+,)+\s*
                                [^,\n]+)\s*?
                                ;$""")



def assignment(content):
  labels = {}
  def replace_assignment(match):
    indent = match.group('indent')
    separator = "\n{indent}}} or {{\n".format(indent=indent)
    name = re.split(r"""\s+""", match.group('variable').strip())[-1]
    label = match.group('label').strip()
    inner = separator.join(["{indent}  {name} = {a};".format(indent=indent, name=name, a=a.strip()) for a in match.group('alternatives').split(',')])
    replacement =  """
{indent}{variable};
{indent}maybe ({label}) {{
{inner}
{indent}}}
""".format(indent=indent,
           variable=match.group('variable').rstrip(),
           label=label,
           inner=inner)
    assert not labels.has_key(label)
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

BLOCK_START_PATTERN = re.compile(r"""^(?m)(?P<indent>[^\S\n]*)maybe\s*\((?P<label>.+?)\)\s*{""")
ALTERNATIVE_START_PATTERN = re.compile(r"""^\s*or\s*{""")

class MaybeBlock(object):
  def __init__(self, match):
    self.start = match.start()
    self.end = None
    self.alternatives = []

def block(content):
  blocks = []
  for match in BLOCK_START_PATTERN.finditer(content):
    maybe_block = MaybeBlock(match)
    buffer_start = match.end() - 1

    while True:
      buffer_end = buffer_start
      search_start = buffer_start
      
      while True:
        buffer_increment = content[search_start:].find("}")
        assert buffer_increment != -1, "Unmatched braces."
        buffer_end += buffer_increment + 1
        block_buffer = content[buffer_start:buffer_end + 1]
        if is_block(block_buffer):
          maybe_block.alternatives.append(block_buffer[1:-1])
          break
        else:
          search_start += buffer_increment + 1
      or_match = ALTERNATIVE_START_PATTERN.match(content[buffer_end:])
      if or_match != None:
        buffer_start = buffer_end + or_match.end() - 1
      else:
        break
    maybe_block.end = buffer_end
    print content[maybe_block.start:maybe_block.end]
    blocks.append(maybe_block)

  return blocks
