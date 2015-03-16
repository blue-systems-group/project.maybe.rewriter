#!/usr/bin/env python

import re,unittest,os,yaml,rewrite,json,lib,ifelse

TESTING_INPUTS = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'testing_inputs')

def strip_whitespace(string):
  return re.sub(r"""\s+""", "", string)

def strip_quotes(string):
  return re.sub(r"""["']""", "", string)

class RecordTests(unittest.TestCase):
  def setUp(self):
		self.test_input = open(os.path.join(TESTING_INPUTS, 'example.java'), 'rU').read()
		self.answers = yaml.load(open(os.path.join(TESTING_INPUTS, 'correct.yaml'), 'rU'))
  
  def test_record_assignments(self):
    statements = rewrite.record_assignments(self.test_input)
    self.assertEqual(len(statements), 2)
    self.assertEqual(len([s for s in statements.values() if s.is_assignment]), 2)
    for label, statement in statements.items():
      self.assertEqual(statement.label, self.answers[label]['label'])
      self.assertEqual(len(statement.alternatives), len(self.answers[label]['alternatives']))
      self.assertEqual(statement.line, self.answers[label]['line'])
      for q,a in zip(statement.alternatives, self.answers[label]['alternatives']):
        self.assertEqual(str(q.content), str(a["content"]))
        self.assertEqual(q.start, a['start'])
        self.assertEqual(q.end, a['end'])
        self.assertEqual(str(statement.content[q.start:q.end]), str(q.content))

  def test_record_blocks(self):
    statements = rewrite.record_blocks(self.test_input)
    self.assertEqual(len(statements), 6)
    self.assertEqual(len([s for s in statements.values() if s.is_block]), 6)
    for label, statement in statements.items():
      self.assertEqual(statement.label, self.answers[label]['label'])
      self.assertEqual(len(statement.alternatives), self.answers[label]['alternative_count'])

class ReplaceTests(unittest.TestCase):
  def setUp(self):
		self.test_input = open(os.path.join(TESTING_INPUTS, 'example.java'), 'rU').read()
		self.answers = yaml.load(open(os.path.join(TESTING_INPUTS, 'correct.yaml'), 'rU'))

  def test_replace_assignments(self):
    unused, labels = rewrite.replace_assignments(self.test_input)
    for label, output in labels.items():
      output = strip_whitespace(output)
      answer = strip_whitespace(self.answers[label]['output'])
      self.assertEqual(output, answer)

  def test_replace_blocks(self):
    unused, labels = rewrite.replace_blocks(self.test_input)
    self.assertEqual(len(labels), 6)

class DumpTests(unittest.TestCase):
  def setUp(self):
		self.test_input = open(os.path.join(TESTING_INPUTS, 'example.java'), 'rU').read()

  def test_dump_statements(self):
    statements = rewrite.record_assignments(self.test_input)
    statements = rewrite.record_blocks(self.test_input, statements)
    json_statements = json.loads(rewrite.dump_statements(self.test_input, statements))
    self.assertEqual(json_statements['package'], "testing_inputs.maybe")
    self.assertEqual(len(json_statements['statements']), 8)

class RegexTests(unittest.TestCase):
  def setUp(self):
		self.test_file = open(os.path.join(TESTING_INPUTS, 'block.java'), 'rU').read()
		self.answers = yaml.load(open(os.path.join(TESTING_INPUTS, 'correct.yaml'), 'rU'))

  def test_clean_string(self):
    string = lib.clean_string(self.test_file).rstrip('\n')
    self.assertEqual(strip_quotes(strip_whitespace(string)), self.answers['is_block_test'])

class IfElseTests(unittest.TestCase):
  def setUp(self):
		self.test_file = open(os.path.join(TESTING_INPUTS, 'ifelse.java'), 'rU').read()
		self.answers = yaml.load(open(os.path.join(TESTING_INPUTS, 'correct.yaml'), 'rU'))['ifelse']

  def test_match_block(self):
    cleaned_content = lib.clean_string(self.test_file, remove_newlines=True)
    matches = ifelse.find_blocks(cleaned_content)
    self.assertEqual(self.answers['statement_count'], len(matches))
    for match in matches:
      self.assertEqual(match.group()[-1], "(")

  def test_dump_statements(self):
    statements = ifelse.record_blocks(self.test_file)
    self.assertEqual(len([1 for S in statements if S and S.ignored == True]),
                     self.answers['ignore_count'])
    self.assertEqual(sorted([S.line for S in statements if S and S.ignored == True]),
                     sorted(self.answers['ignored_lines']))

if __name__ == '__main__':
  unittest.main()
