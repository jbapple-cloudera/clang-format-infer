#!/usr/bin/env python2

# A script to find the best clang-format options for your source code.
#
# ./example-styles.exe | ./search.py --constants=... --clang-format=... --source-dir=...
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

parser = argparse.ArgumentParser()
parser.add_argument("--clang-format", dest="clangformat", help="location of clang-format")
parser.add_argument("--source-dir", dest="sourcedir", help="directory of source code")
parser.add_argument("--constants", dest="constants",
                    help="file of fixed config parameters")
args = parser.parse_args()

# A template is a dictionary that mimics a clang config, except in place of atomic values,
# there is a list. Each list has the set of valid values for that location.

def pick_random(template):
  """Given a template, pick randomly from it to create a clang config."""
  random.seed()
  result = {}
  for k, v in template.iteritems():
    if isinstance(v, dict):
      result[k] = pick_random(v)
    else:
      result[k] = random.choice(v)
  return result

def genericize(val):
  """Turn a value from a clang config into the value of a corresponding template."""
  if isinstance(val, bool):
    return [True, False]
  elif isinstance(val, dict):
    result = {}
    for k, v in val.iteritems():
      result[k] = genericize(v)
    return result
  else:
    return [val]

def expand_horizons(old, new):
  """Update a template to include the values from a clang config.

  Updates the template ('old') in place using the values from the config ('new').
  """
  for k, v in new.iteritems():
    if k not in old:
      old[k] = genericize(v)
    elif isinstance(v, dict):
      expand_horizons(old[k], v)
    elif v not in old[k]:
      old[k].append(v)


# Values in templates and clang configs can be referred to by paths of keys

def set_deep(config, key_seq, new_val):
  """Set a value in a clang config or template using the given sequence of keys."""
  if 1 == len(key_seq):
    config[key_seq[0]] = new_val
  else:
    set_deep(config[key_seq[0]], key_seq[1:], new_val)

def get_deep(config, key_seq):
  """Get a value from a clang config or template using the given sequence of keys."""
  if 1 == len(key_seq):
    return config[key_seq[0]]
  else:
    return get_deep(config[key_seq[0]], key_seq[1:])

def find_best(template, config, key_seq, metric):
  """Iterate through the possible values in from a key sequence and find the best one.

  metric is a function that returns lower values for better configs, or 0 if a config is
  invalid.
  """
  possibles = get_deep(template, key_seq)
  if 1 == len(possibles):
    return None
  best_score = 2**60
  best_val = None
  for val in possibles:
    set_deep(config, key_seq, val)
    score = metric(config)
    #print "FFFFFFFFF", score
    if score < best_score:
      best_score = score
      best_val = val
  set_deep(config, key_seq, best_val)
  return best_score

def save(config):
  """Save a clang config to a new file and returns the name of the file."""
  (fd, name) = tempfile.mkstemp()
  f = os.fdopen(fd, "a")
  f.write(yaml.dump(config))
  f.close()
  return name

# A cache of measures for clang configs:
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
  if 0 == val:
    val = 2**60
  measure_cache[cache_key] = val
  return val

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

def make_template(filenames):
  """Makes a template from a list of YAML clang config files.

  Infers valid values for different paths using the valid examples given.
  """
  result = {}
  for fn in filenames:
    with open(fn) as f:
      conf = yaml.load(f)
      expand_horizons(result, conf)
  return result

def main():
  # Make a template and key paths:
  configs = []
  for filename in sys.stdin:
    configs.append(filename.strip())
  template = make_template(configs)
  key_seqs = all_key_seqs(template)

  with open(args.constants) as f:
    constants = yaml.load(f)

  # Start searching for a config with a known value: the constants provided by the user
  best_config = constants
  best_score = measure(best_config)
  best_file = save(best_config)

  while True:
    # Hill climbing with random starting locations
    print best_score, "best config yet is stored in", best_file
    # Start at a random place
    config = pick_random(template)
    # Override the constants
    for k, v in constants.iteritems():
      config[k] = v
    # Set a baseline
    local_best_config = config
    local_best_score = measure(local_best_config)
    improved = True
    print local_best_score
    while improved:
      print "NEW ROUND"
      improved = False
      random.shuffle(key_seqs)
      for key_seq in key_seqs:
        if key_seq[0] not in constants:
          # Save the old value:
          oldval = copy.deepcopy(get_deep(config, key_seq))
          # Optimize the new value:
          new_score = find_best(template, config, key_seq, measure)
          if new_score is not None and new_score < local_best_score:
            local_best_config = copy.deepcopy(config)
            local_best_score = new_score
            improved = True
            print "IMPROVED", new_score, key_seq, oldval, get_deep(config, key_seq)
    print "END OF ROUND"
    if local_best_score < best_score:
      best_config = copy.deepcopy(local_best_config)
      best_score = local_best_score
      best_file = save(best_config)
      print "NEW BEST SCORE: ", best_score

if __name__ == "__main__":
  main()
