#!/usr/bin/env python

import re,unittest,os,yaml,rewrite,json

TESTING_INPUTS = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'testing_inputs')

def strip_whitespace(string):
  return re.sub(r"""\s+""", "", string)

def strip_quotes(string):
  return re.sub(r"""["']""", "", string)

class RecordTests(unittest.TestCase):
  def setUp(self):
		self.test_input = open(os.path.join(TESTING_INPUTS, 'maybe.java'), 'rU').read()
		self.answers = yaml.load(open(os.path.join(TESTING_INPUTS, 'correct.yaml'), 'rU'))
  
  def test_record_assignments(self):
    statements = rewrite.record_assignments(self.test_input)
    self.assertEqual(len(statements), 2)
    self.assertEqual(len([s for s in statements.values() if s.is_assignment]), 2)
    for label, statement in statements.items():
      self.assertEqual(statement.label, self.answers[label]['label'])
      self.assertEqual(len(statement.alternatives), len(self.answers[label]['alternatives']))
      for q,a in zip(statement.alternatives, self.answers[label]['alternatives']):
        self.assertEqual(str(q.content), str(a["content"]))
        self.assertEqual(q.start, a['start'])
        self.assertEqual(q.end, a['end'])
        self.assertEqual(str(statement.content[q.start:q.end]), str(q.content))

  def test_record_blocks(self):
    statements = rewrite.record_blocks(self.test_input)
    self.assertEqual(len(statements), 2)
    self.assertEqual(len([s for s in statements.values() if s.is_block]), 2)

class ReplaceTests(unittest.TestCase):
  def setUp(self):
		self.test_input = open(os.path.join(TESTING_INPUTS, 'maybe.java'), 'rU').read()
		self.answers = yaml.load(open(os.path.join(TESTING_INPUTS, 'correct.yaml'), 'rU'))

  def test_replace_assignment(self):
    unused, labels = rewrite.replace_assignments(self.test_input)
    for label, output in labels.items():
      output = strip_whitespace(output)
      answer = strip_whitespace(self.answers[label]['output'])
      self.assertEqual(output, answer)

  def test_block(self):
    unused, labels = rewrite.replace_blocks(self.test_input)
    self.assertEqual(len(labels), 2)

class DumpTests(unittest.TestCase):
  def setUp(self):
		self.test_input = open(os.path.join(TESTING_INPUTS, 'maybe.java'), 'rU').read()

  def test_dump_statements(self):
    statements = rewrite.record_assignments(self.test_input)
    json_statements = json.loads(rewrite.dump_statements(self.test_input, statements))
    self.assertEqual(json_statements['package'], "testing_inputs.maybe")

class RegexTests(unittest.TestCase):
  def setUp(self):
		self.test_file = open(os.path.join(TESTING_INPUTS, 'block.java'), 'rU').read()
		self.answers = yaml.load(open(os.path.join(TESTING_INPUTS, 'correct.yaml'), 'rU'))

  def test_remove_comments_and_strings(self):
    string = rewrite.remove_comments_and_strings(self.test_file).rstrip('\n')
    self.assertEqual(strip_quotes(strip_whitespace(string)), self.answers['is_block_test'])

if __name__ == '__main__':
  unittest.main()
