#!/usr/bin/env python

import unittest,os,yaml
from maybe import rewrite

TESTING_INPUTS = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'testing_inputs')

class RegexTests(unittest.TestCase):
  def setUp(self):
    self.test_input = open(os.path.join(TESTING_INPUTS, 'maybe.java'), 'rU').read()
    self.correct_answers = yaml.load(open(os.path.join(TESTING_INPUTS, 'correct.yaml'), 'rU'))

  def test_maybe_assignment(self):
    matches = rewrite.ASSIGNMENT_PATTERN.findall(self.test_input)
    print matches
    
if __name__ == '__main__':
  unittest.main()
