#!/usr/bin/env python

import re,unittest,os,yaml
from maybe import rewrite

TESTING_INPUTS = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'testing_inputs')

def strip_quotes(string):
  m = re.match(r"""^"(?P<unquoted>.*?)"$""", string)
  if not m:
    return string
  else:
    return m.group('unquoted')

def strip_whitespace(string):
  return re.sub(r"""\s+""", "", string)

class MaybeTests(unittest.TestCase):
  def setUp(self):
		self.test_input = open(os.path.join(TESTING_INPUTS, 'maybe.java'), 'rU').read()
		self.answers = yaml.load(open(os.path.join(TESTING_INPUTS, 'correct.yaml'), 'rU'))

  def test_assignment(self):
    unused, labels = rewrite.assignment(self.test_input)
    for label, output in labels.items():
      output = strip_whitespace(output)
      answer = strip_whitespace(self.answers[strip_quotes(label)])
      self.assertEqual(output, answer)

class RegexTests(unittest.TestCase):
  def setUp(self):
		self.test_file = open(os.path.join(TESTING_INPUTS, 'block.java'), 'rU').read()
		self.answers = yaml.load(open(os.path.join(TESTING_INPUTS, 'correct.yaml'), 'rU'))

  def test_is_block(self):
    string = rewrite.is_block(self.test_file).rstrip('\n')
    self.assertEqual(strip_whitespace(string), self.answers['is_block_test'])

if __name__ == '__main__':
  unittest.main()
