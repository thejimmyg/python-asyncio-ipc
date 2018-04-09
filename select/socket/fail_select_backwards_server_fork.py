# https://stackoverflow.com/questions/10788865/send-socket-object-to-forked-running-process-multiprocessing-queue
# ^ means that apparanetly it is really hard to send an open socket via a pipe, but that if each child accepts, the OS makes sure they aren't duplicated.
# You can read Advanced Programming in the UNIX environment to find out more

# Basic structure based on:
# https://steelkiwi.com/blog/working-tcp-sockets/

# See also how this is done using multiprocessing reduction send_handle() implementation to see if there is a good workaround
# https://gist.github.com/josiahcarlson/3723597


import os
import select
import socket
import sys


r, w = os.pipe()
print('pipe r,w:', r, w)
pid = os.fork()
if pid == 0:
    # We are now running the child process
    print('Child: {}'.format(os.getpid()), flush=True)
    # We can read from the child end of the pipe
    os.close(w)

    inputs = [r]
    outputs = []
    message_queue = {}
    
    while True:
        print(inputs)
        readable, writable, exceptional = select.select(inputs, outputs, inputs, 1)
        for fd in readable:
            if fd == r:
                # 512 bytes in one go should be guaranteed atomic by POSIX standard for a pipe
                data = os.read(r, 512)
                connection = int(data[:-1])
                print(connection)
                inputs.append(connection)
                message_queue[connection] = []
            else:
                data = os.read(fd, 1024)
                if data:
                    message_queue[fd].append(data[::-1])
                    if fd not in outputs:
                        outputs.append(fd)
                else:
                    if fd in outputs:
                        outputs.remove(fd)
                    inputs.remove(fd)
                    del message_queue[fd]
        for fd in writable:
            print('writable', fd)
            # Might have just been deleted
            if fd in message_queue:
                if message_queue[fd]:
                    next_msg = message_queue[fd].pop(0)
                    out = next_msg
                    num = os.write(fd, out)
                    if num == len(out):
                        outputs.remove(fd)
                    else:
                        print('Leftovers')
                        message_queue[fd].insert(0, out[num:])
                else:
                    outputs.remove(fd)
        for fd in exceptional:
            if fd == r:
                raise Exception('Error in main pipe')
            inputs.remove(fd)
            if fd in outputs:
                outputs.remove(fd)
            if fd in message_queue:
                del message_queue[fd]
else:
    # We are still running the parent process and `pid` is the child PID
    print('Parent: {}, Child: {}'.format(os.getpid(), pid), flush=True)
    # We can write to the parent end of the pipe
    os.close(r)
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.setblocking(0)
    server.bind(('localhost', 50000))
    server.listen(5)

    while True:
        readable, writable, exceptional = select.select([server], [], [])
        for s in readable:
            if s is server:
                connection, client_address = s.accept()
                print(connection.fileno(), client_address)
                os.set_blocking(connection.fileno(), False)
                print(os.write(w, str(connection.fileno()).encode('utf8')+b'\n'))
