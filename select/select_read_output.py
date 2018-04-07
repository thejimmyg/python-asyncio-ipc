# python3 select_read_output.py

import subprocess
import sys
import select
import time
import os


# Our target uses flush=True so we don't need env={'PYTHONUNBUFFERED': '1'} or python -u for the child process
p = subprocess.Popen([sys.executable, '../process_that_spits_out_four_lines.py'],
                     stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                     stdin=subprocess.PIPE)

print('stdout', p.stdout, p.stdout.fileno())
print('stderr', p.stderr, p.stderr.fileno())
print('stdin', p.stdin, p.stdin.fileno())
p.stdin.close()
print('stdin', p.stdin)

os.set_blocking(p.stdout.fileno(), False)
os.set_blocking(p.stderr.fileno(), False)

while p.poll() is None:
    rlist, wlist, xlist = select.select([p.stdout, p.stderr], [], [p.stdout, p.stderr], 10)
    print(rlist, wlist, xlist)
    print('Waiting for read')
    # Since we set non-blocking, this just reads what is in the buffer so far
    print([x.read() for x in rlist])
    # Otherwise we would have to use a low-level read that returns at most 1024 bytes like this:
    # print([os.read(x.fileno(), 1024) for x in rlist])
    time.sleep(1)

print(p.poll())
