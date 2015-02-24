import re

ASSIGNMENT_PATTERN = re.compile(r"""(?xum)
                                ^(?P<indent>[^\S\n]*)
                                (?P<variable>.*?)
                                =\s*maybe\s*
                                \((?P<label>.+?)\)
                                (?P<alternatives>(?:[^,;]+,)+\s*
                                [^,]+)\s*
                                ;$""")

JAVA_PRINT_PATTERN= re.compile(r'System.out.print.*;')

C_PRINT_PATTERN = re.compile(r'printf,*;')

SINGLE_LINE_COMMENTS_PATTERN= re.compile(r'\/\/.*') 

MULTI_LINE_COMMENTS_PATTERN= re.compile(r'/\*.*\*/', re.DOTALL) 

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

