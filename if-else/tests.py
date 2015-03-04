#!/usr/bin/env python

import yaml,os,unittest,re,findifelse

TESTING_INPUTS = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                'testing_inputs')

def strip_whitespace(string):
  return re.sub(r"""\s+""","",string)

class ExtractTests(unittest.TestCase):
  def setUp(self):
    self.test_input = open(os.path.join(TESTING_INPUTS, 'blocks.java'), 
                            'rU').read()
    self.answers = yaml.load(open(os.path.join(TESTING_INPUTS, 'correct.yaml'),
                                  'rU'))

  def test_extract_simple_block(self):
    blocks = findifelse.extract_blocks(self.test_input)
    self.assertEqual(blocks[0]['content'],
                      self.answers['if_else_test']['output'].rstrip('\n'))

  def test_extract_if_else_if_block(self):
    blocks = findifelse.extract_blocks(self.test_input)
    self.assertEqual(blocks[1]['condition_len'], 10)
    self.assertEqual(blocks[1]['condition'], '(value == 1)')
    self.assertEqual(blocks[1]['content'],
                      self.answers['if_else_if_test']['output'].rstrip('\n'))

  def test_extract_nested_if_else_block(self):
    blocks = findifelse.extract_blocks(self.test_input)
    self.assertEqual(blocks[2]['content'],
                      self.answers['nested_if_else']['output'].rstrip('\n'))

  def test_extract_aosp_code_block(self):
    blocks = findifelse.extract_blocks(self.test_input)
    self.assertEqual(blocks[5]['condition_len'], 11)
    self.assertEqual(strip_whitespace(blocks[5]['content']),
                       strip_whitespace(self.answers['aosp_code']['output'] \
                       .rstrip('\n')))

  def test_extract_long_condition(self):
    blocks = findifelse.extract_blocks(self.test_input)
    self.assertEqual(blocks[7]['condition_len'], 119)


if __name__ == '__main__':
  unittest.main()
    
