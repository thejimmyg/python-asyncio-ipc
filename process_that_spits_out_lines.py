import time
import signal
import sys


def sig_handler(signal, frame):
    print("Got signal", signal, ". Exiting.")
    sys.exit(0)


signal.signal(signal.SIGINT, sig_handler)


count = 0
while True:
    count += 1
    print(f'Line {count}')
    time.sleep(1)
