#!/usr/bin/env python

import re,unittest,os,yaml,rewrite,json,lib,ifelse,glob,sys,timers

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
    cleaned_content = lib.clean_string(self.test_file)
    matches = ifelse.find_blocks(cleaned_content)
    self.assertEqual(self.answers['statement_count'], len(matches))
    for match in matches:
      self.assertEqual(match.group()[-1], "(")

  def test_match_blocks(self):
    statements = ifelse.record_blocks(self.test_file)
    self.assertEqual(ifelse.IfElseStatement.ignored_count(statements), self.answers['ignore_count'])
    self.assertEqual(ifelse.IfElseStatement.correct_count(statements), self.answers['correct_count'])
    self.assertEqual(sorted([S.line for S in ifelse.IfElseStatement.ignored(statements)]),
                     sorted(self.answers['ignored_lines']))
    self.assertEqual(sorted([S.line for S in ifelse.IfElseStatement.correct(statements)]),
                     sorted(self.answers['correct_lines']))

  def test_aosp_sources(self):
    for i, java_file in enumerate(glob.glob(os.path.join(TESTING_INPUTS, "ifelse", "*.java"))):
      contents = open(java_file, 'rU').read()
      statements = ifelse.record_blocks(contents)
      filename = os.path.basename(java_file)
      if not self.answers.has_key(filename):
        continue
      answers = self.answers[filename]
      ignored_count = ifelse.IfElseStatement.ignored_count(statements)
      self.assertEqual(ignored_count, answers['ignored_count'])
      if ignored_count > 0:
        self.assertEqual(sorted([S.line for S in ifelse.IfElseStatement.ignored(statements)]),
                         sorted(answers['ignored_lines']))
      self.assertEqual(ifelse.IfElseStatement.correct_count(statements), answers['correct_count'])
      self.assertEqual(sorted([S.line for S in ifelse.IfElseStatement.correct(statements)]),
                       sorted(answers['correct_lines']))
      if answers.has_key('correct_alternative_count'):
        self.assertEqual([len(S.alternatives) for S in ifelse.IfElseStatement.correct(statements)],
                         answers['correct_alternative_count'])

  def test_main(self, verbose=False):
    class Args(object):
      def __init__(self, toparse, projects):
        self.toparse = toparse
        self.projects = projects
    
    old_stdout = sys.stdout
    try:
      if not verbose:
        sys.stdout = open(os.devnull, 'w')
      ifelse.main(Args('testing_inputs/ifelse.in', 'testing_inputs/projects.txt'))
    finally:
      sys.stdout = old_stdout

class TimerTests(unittest.TestCase):
  def setUp(self):
		self.test_file = open(os.path.join(TESTING_INPUTS, 'timers.java'), 'rU').read()
		self.answers = yaml.load(open(os.path.join(TESTING_INPUTS, 'correct.yaml'), 'rU'))['timers']
  
  def test_match_timers(self):
    cleaned_content = lib.clean_string(self.test_file)
    matches = list(timers.TIMER_PATTERN.finditer(cleaned_content))
    self.assertEqual(self.answers['statement_count'], len(matches))
  
  def test_aosp_sources(self):
    for i, java_file in enumerate(glob.glob(os.path.join(TESTING_INPUTS, "timers", "*.java"))):
      contents = open(java_file, 'rU').read()
      statements = timers.record_timers(contents)
  
  def test_main(self, verbose=False):
    class Args(object):
      def __init__(self, toparse, projects):
        self.toparse = toparse
        self.projects = projects
    
    old_stdout = sys.stdout
    try:
      if not verbose:
        sys.stdout = open(os.devnull, 'w')
      timers.main(Args('testing_inputs/timers.in', 'testing_inputs/projects.txt'))
    finally:
      sys.stdout = old_stdout

class ProjectsTests(unittest.TestCase):
  def test(self):
    projects = lib.ProjectsMap(os.path.join(TESTING_INPUTS, 'aosp_projects.txt'))
    self.assertEqual(projects.map_file("doesnt/exist"), None)
    self.assertEqual(projects.map_file("bionic/whatever")['name'], 'platform/bionic')
    self.assertEqual(projects.map_file("prebuilts/clang/linux-x86/host/3.3")['groups'], 'linux')
  
if __name__ == '__main__':
  unittest.main()
