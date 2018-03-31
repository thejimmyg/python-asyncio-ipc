import sys

while True:
    input_ = sys.stdin.readline()
    if input_ == '':
        break
    # Remove the newline
    input_ = input_[:-1]
    sys.stdout.write(input_[::-1]+'\n')
    sys.stdout.flush()
