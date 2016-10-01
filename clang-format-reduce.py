#!/usr/bin/env python2

# ./clang-format-reduce.py --config=...
#
# uses python 2, pyyaml-3.12, subprocess32-3.2.7

import yaml
import random
import tempfile
import subprocess32
import os
import sys
import copy
import argparse
import shutil

parser = argparse.ArgumentParser()
parser.add_argument("--config", dest="config", help="configuration file to shrink")
parser.add_argument("--source-dir", dest="sourcedir", help="directory of source code")
parser.add_argument("--clang-format", dest="clangformat", help="location of clang-format")
parser.add_argument("--constants", dest="constants",
                    help="file of fixed config parameters")
args = parser.parse_args()

def all_key_seqs(template):
  """Returns a list of all valid key paths from a template."""
  result = []
  for k, v in template.iteritems():
    if isinstance(v, dict):
      for suffix in all_key_seqs(v):
        result.append([k] + suffix)
    else:
      result.append([k])
  return result

def get_deep(config, key_seq):
  """Get a value from a clang config or template using the given sequence of keys."""
  if 1 == len(key_seq):
    return config[key_seq[0]]
  else:
    return get_deep(config[key_seq[0]], key_seq[1:])

def unset_deep(config, key_seq):
  """Set a value in a clang config or template using the given sequence of keys."""
  if 1 == len(key_seq):
    del config[key_seq[0]]
  else:
    unset_deep(config[key_seq[0]], key_seq[1:])

def set_deep(config, key_seq, new_val):
  """Set a value in a clang config or template using the given sequence of keys."""
  if 1 == len(key_seq):
    config[key_seq[0]] = new_val
  else:
    set_deep(config[key_seq[0]], key_seq[1:], new_val)

with open(args.constants) as f:
  constants = yaml.load(f)

def remove_unused(config):
  print >> sys.stderr, "#", config["BasedOnStyle"]
  baseline = measure(config)
  for key_seq in all_key_seqs(config):
    if key_seq <> ["BreakBeforeBraces"] and (key_seq[0] in constants or key_seq == ["BasedOnStyle"]):
      continue
    temp = get_deep(config, key_seq)
    unset_deep(config, key_seq)
    test = measure(config)
    if test > baseline:
      set_deep(config, key_seq, temp)
    else:
      print >> sys.stderr, "REMOVED ", key_seq, test, baseline
      baseline = test
  for key, value in config.items():
    if {} == value:
      print >> sys.stderr, "EMPTY ", key
      del(config[key])
  return baseline

measure_cache = {}

def measure(config):
  """Measure a clang config using distance.sh."""
  cache_key = yaml.dump(config)
  if cache_key in measure_cache:
    return measure_cache[cache_key]
  (fd, name) = tempfile.mkstemp()
  f = os.fdopen(fd, "a")
  f.write(yaml.dump(config))
  f.close()
  val = int(subprocess32.check_output(
      [os.path.dirname(os.path.realpath(sys.argv[0])) + "/distance.sh",
       args.clangformat, name, args.sourcedir]))
  os.remove(name)
  #if 0 == val:
  #  val = 2**60
  measure_cache[cache_key] = val
  return val

def main():
  # read config into yaml
  with open(args.config) as config_file:
    config = yaml.load(config_file)
  print >> sys.stderr, "# Started from", len(config)
  key_seqs = all_key_seqs(config)
  results = []
  # read list of config files
  for filename in sys.stdin:
    # for each style file sf, parse it into style config sc
    with open(filename.strip()) as style_config_file:
      style_config = yaml.load(style_config_file)
    # if sc has same language as config:
    if style_config['Language'] == config['Language']:
      # Make a clone of config, config-2
      min_config = copy.deepcopy(config)
      # Add to config-2 the BasedOnStyle
      min_config["BasedOnStyle"] = style_config["BasedOnStyle"]
      for key_seq in key_seqs:
        if key_seq != ["Language"] and get_deep(
                style_config, key_seq) == get_deep(
                min_config, key_seq):
          unset_deep(min_config, key_seq)
      score = remove_unused(min_config)
      score = remove_unused(min_config)
      print >> sys.stderr, "# Found", len(min_config)
      results.append((score, len(min_config), min_config))
  smallest = min(results)
  print >> sys.stderr, "#", smallest[0]
  print >> sys.stderr, "#", smallest[1]
  print yaml.dump(smallest[2], default_flow_style=False)

if __name__ == "__main__":
  main()
