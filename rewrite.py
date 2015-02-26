#!/usr/bin/env python

import re,random,json,argparse,os

class MaybeAlternative(object):
  def __init__(self, value, offset, start, end, content):
    self.value = value
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
            'end': self.end,
            'content': self.content}

class MaybeStatement(object):
  ASSIGNMENT = "assignment"
  BLOCK = "block"

  def __init__(self, maybe_type, start, label, end=None):
    self.maybe_type = maybe_type
    self.start = start
    self.end = end
    self.label = label
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
            'alternatives': [a.as_dict for a in self.alternatives]}

  @property
  def is_assignment(self):
    return self.maybe_type == MaybeStatement.ASSIGNMENT

  @property
  def is_block(self):
    return self.maybe_type == MaybeStatement.BLOCK

def remove_comments_and_strings(string):
  MULTI_LINE_COMMENTS_PATTERN= re.compile(r"""(?s)/\*.*?\*/""") 
  SINGLE_LINE_COMMENTS_PATTERN= re.compile(r"""(?m)//.*$""") 

  SINGLE_QUOTE_STRING_PATTERN= re.compile(r"""'(?P<quoted>(?:\\'|[^'\n])*?)'""")
  DOUBLE_QUOTE_STRING_PATTERN= re.compile(r'"(?P<quoted>(?:\\"|[^"\n])*?)"')
  
  def equivalent_whitespace(match):
    return " " * len(match.group())

  def single_quotes(match):
    assert len(match.group()) == (len(match.group('quoted')) + 2), "Length mismatch: %d %d" % (len(match.group()), len(match.group('quoted')))
    return "'%s'" % (" " * len(match.group('quoted')),)
  
  def double_quotes(match):
    assert len(match.group()) == (len(match.group('quoted')) + 2), "Length mismatch: %d %d" % (len(match.group()), len(match.group('quoted')))
    return '"%s"' % (" " * len(match.group('quoted')),)
  
  initial_length = len(string)

  string = MULTI_LINE_COMMENTS_PATTERN.sub(equivalent_whitespace, string)
  string = SINGLE_LINE_COMMENTS_PATTERN.sub(equivalent_whitespace, string)
  string = SINGLE_QUOTE_STRING_PATTERN.sub(single_quotes, string)
  string = DOUBLE_QUOTE_STRING_PATTERN.sub(double_quotes, string)

  assert len(string) == initial_length, "Cleaning changed string length."
  return string

ASSIGNMENT_PATTERN = re.compile(r"""(?xum)
                                ^(?P<indent>[^\S\n]*)
                                (?P<variable>.*?)
                                =\s*maybe\s*
                                \((?P<label>.+?)\)
                                (?P<alternatives>(?:[^,;]+,)+\s*
                                [^,\n]+)\s*?
                                ;$""")
ASSIGNMENT_TEMPLATE = """
{variable};
maybe ("{label}") {{
{inner}
}}
"""

def record_assignments(content, statements=None):
  if not statements:
    statements = {}
  cleaned_content = remove_comments_and_strings(content)
  
  def record_assignment(match):
    label = eval(content[match.start('label'):match.end('label')].strip())
    maybe_statement = MaybeStatement(MaybeStatement.ASSIGNMENT, match.start(), label, match.end())
    maybe_statement.content = content[match.start():match.end()]
    assert not statements.has_key(maybe_statement.label)
    alternative_start = match.start('alternatives')
    alternatives = content[match.start('alternatives'):match.end('alternatives')]
    for value, alternative in enumerate(alternatives.split(',')):
      alternative_content = alternative.strip()
      alternative_start += len(alternative) - len(alternative.lstrip())
      maybe_alternative = MaybeAlternative(value,
                                           maybe_statement.start,
                                           alternative_start,
                                           alternative_start + len(alternative_content),
                                           alternative_content)
      maybe_statement.alternatives.append(maybe_alternative)
      alternative_start += len(alternative.lstrip()) + 1
    statements[maybe_statement.label] = maybe_statement
  
  for match in ASSIGNMENT_PATTERN.finditer(cleaned_content):
    record_assignment(match)

  return statements

def replace_assignments(content, standard_indent="\t"):
  labels = {}
  def replace_assignment(match, content):
    label = eval(content[match.start('label'):match.end('label')].strip())
    assert not labels.has_key(label)
    indent = match.group('indent')
    variable = match.group('variable').rstrip()
    separator = "\n{indent}}} or {{\n".format(indent=indent)
    name = re.split(r"""\s+""", match.group('variable').strip())[-1]
    alternatives = content[match.start('alternatives'):match.end('alternatives')]
    inner = separator.join(["{indent}{name} = {a};".format(indent=standard_indent, name=name, a=a.strip()) for a in alternatives.split(',')])
    replacement = ASSIGNMENT_TEMPLATE.format(indent=indent,
                                             variable=variable,
                                             label=label,
                                             inner=inner)
    indented_replacement = ""
    for line in replacement.splitlines():
      indented_replacement += indent + line
    replacement = indented_replacement
    labels[label] = replacement
    return content[:match.start()] + replacement + content[match.end():]
  
  while True:
    cleaned_content = remove_comments_and_strings(content)
    assignment_match = ASSIGNMENT_PATTERN.search(cleaned_content)
    if assignment_match:
      content = replace_assignment(assignment_match, content)
    else:
      break
  return content, labels

def is_block(string):
  return (string.count("{") - string.count("}") == 0)

def match_to_block(match, content):
  label = eval(content[match.start('label'):match.end('label')].strip())
  maybe_block = MaybeStatement(MaybeStatement.BLOCK, match.start(), label)
  buffer_start = match.end() - 1
  
  value = 0
  while True:
    buffer_end = buffer_start
    search_start = buffer_start
    
    while True:
      buffer_increment = content[search_start:].find("}")
      assert buffer_increment != -1, "Unmatched braces."
      buffer_end += buffer_increment + 1
      block_buffer = content[buffer_start:buffer_end + 1]
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
    or_match = ALTERNATIVE_START_PATTERN.match(content[buffer_end:])
    if or_match != None:
      buffer_start = buffer_end + or_match.end() - 1
    else:
      break
  maybe_block.end = buffer_end
  maybe_block.content = content[maybe_block.start:maybe_block.end]
  return maybe_block

BLOCK_START_PATTERN = re.compile(r"""^(?m)(?P<indent>[^\S\n]*)maybe\s*\((?P<label>.+?)\)\s*{""")
ALTERNATIVE_START_PATTERN = re.compile(r"""^\s*or\s*{""")

JAVA_BLOCK_TEMPLATE = """
int {name} = 0;

try {{
{stdindent}{name} = getMaybeAlternative("{label}");
}} catch (Exception e) {{ }};
switch ({name}) {{
{inner}
}}
"""
JAVA_BLOCK_ALTERNATIVE_TEMPLATE = """
case {value}: {{
{contents}
{stdindent}break;
}}
"""

def record_blocks(content, statements=None):
  if not statements:
    statements = {}
  cleaned_content = remove_comments_and_strings(content)
  
  for match in BLOCK_START_PATTERN.finditer(cleaned_content):
    maybe_block = match_to_block(match, content)
    assert not statements.has_key(maybe_block.label)
    statements[maybe_block.label] = maybe_block
  return statements

def replace_blocks(content, standard_indent="\t"):
  labels = {}
  
  while True:
    cleaned_content = remove_comments_and_strings(content)
    block_match = BLOCK_START_PATTERN.search(cleaned_content)
    if block_match:
      maybe_block = match_to_block(block_match, content)
      assert not labels.has_key(maybe_block.label)
      name = "__{slug}__{nonce}".format(slug=re.sub("[^A-Za-z0-9]", "_", maybe_block.label),
                                        nonce=random.randint(0,1024))
      inner = ""
      for alternative in maybe_block.alternatives:
        contents = ""
        for line in alternative.content.splitlines():
          contents += standard_indent + line
        inner += JAVA_BLOCK_ALTERNATIVE_TEMPLATE.format(value=alternative.value,
                                                        contents=contents,
                                                        stdindent=standard_indent)
      replacement = JAVA_BLOCK_TEMPLATE.format(name=name, stdindent=standard_indent,
                                               label=maybe_block.label,
                                               inner=inner)
      labels[maybe_block.label] = replacement
      content = content[:block_match.start()] + replacement + content[block_match.end():]
    else:
      break

  return content, labels

JAVA_PACKAGE_STATEMENT = re.compile(r"""^package\s+(?P<name>\S+)""")

def dump_statements(content, statements):
  package_match = JAVA_PACKAGE_STATEMENT.match(content)
  assert package_match, "No package name provided"
  package_name = package_match.group('name').strip()
  
  statement_list = []
  for statement in sorted(statements.values(), key=lambda s: s.start):
    statement_list.append(statement.as_dict)
  complete_dict = {"package": package_name,
                   "statements": statement_list}
  return json.dumps(complete_dict, indent=4)

if __name__=='__main__':
  parser = argparse.ArgumentParser(description='Rewrite maybe statements.')
  parser.add_argument('input_file', type=str, help="Input file to rewrite.")
  args = parser.parse_args()
  basename, ext = os.path.splitext(args.input_file)
  assert ext == '.java', "Input must be a Java file: %s" % (ext,)
  content = open(args.input_file, 'rU').read()

  statements = record_assignments(content)
  statements = record_blocks(content, statements)

  print dump_statements(content, statements)
