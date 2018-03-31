"""
python3 -u test_stdout_stderr.py 2>&1 | tee -a log.txt
"""

import sys

print('1 STDOUT', file=sys.stdout)
sys.stdout.flush()
print('2 STDERR', file=sys.stderr)
sys.stderr.flush()
print('3 STDOUT', file=sys.stdout)
sys.stdout.flush()
print('4 STDERR', file=sys.stderr)
sys.stderr.flush()
