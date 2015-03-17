#!/usr/bin/env python

import re,os,argparse,csv,sys,json

NULL_PATTERN = re.compile(r""".*\bnull\b.*""")

def main(args):
  total_count, ignore_count, single_count, null_count = 0, 0, 0, 0
  file_count = {}
  writer = csv.writer(sys.stdout)
  with open(args.toparse, 'rb') as f:
    to_print = []
    reader = csv.reader(f)
    for row in reader:
      row_type = row[0]
      if row_type == 'I':
        ignore_count += 1
      elif row_type == 'C':
        total_count += 1
        path = row[4]
        if not file_count.has_key(path):
          file_count[path] = 0
        file_count[path] += 1
        
        alternative_count = int(row[6])
        if alternative_count == 1:
          single_count += 1
          continue
        
        content = row[-1]
        if NULL_PATTERN.search(content):
          null_count += 1
          continue

        to_print.append(row)

    writer.writerows(to_print)
    total_files = len(file_count.keys())
    file_average = float(sum(file_count.values())) / len(file_count.keys())
    file_median = sorted(file_count.values())[int(len(file_count.keys()) / 2.)]
    file_max = sorted(file_count.values())[-1]
    print >>sys.stderr, json.dumps({"total": total_count, "ignored": ignore_count, "null": null_count, "file_count": total_files, "file_average": file_average, "file_median": file_median, "file_max": file_max})

if __name__=='__main__':
  parser = argparse.ArgumentParser(description='Find if-else statements in AOSP.')
  parser.add_argument('toparse', type=str, help="List of files to parse, relative to current directory.")
  args = parser.parse_args()
  main(args)
