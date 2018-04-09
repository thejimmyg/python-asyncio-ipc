# Problem with this approach is that because the server is shared in processes, they all trigger that it is ready to accept a connection, then only one of them gets it.


import os
import select
import socket
import sys
import time


class Loop:
    def __init__(self, server):    
        self.server = server
        self.inputs = [self.server]
        self.outputs = []
        self.message_queue = {}
        self.timers = []
        self.timeout = 0.00001

    def run_forever(self):
        while True:
            try:
                readable, writable, exceptional = select.select(self.inputs, self.outputs, self.inputs, self.timeout)
                for fd in readable:
                    if fd is self.server:
                        # The server fd is shared in child processes, but we rely on the OS to only allow one process to accept each connection.
                        try:
                            connection, client_address = self.server.accept()
                        except BlockingIOError as e:
                            # Don't worry, another child process probably just got this connection first
                            # there is nothing to do now
                            pass
                        else:
                            print(connection.fileno(), client_address)
                            os.set_blocking(connection.fileno(), False)
                            self.inputs.append(connection.fileno())
                            self.message_queue[connection.fileno()] = []
                    else:
                        data = os.read(fd, 1024)
                        if data:
                            self.message_queue[fd].append(data[::-1])
                            if fd not in self.outputs:
                                self.outputs.append(fd)
                        else:
                            if fd in self.outputs:
                                self.outputs.remove(fd)
                            self.inputs.remove(fd)
                            del self.message_queue[fd]
                for fd in writable:
                    print('writable', fd, flush=True)
                    # Might have just been deleted
                    if fd in self.message_queue:
                        if self.message_queue[fd]:
                            next_msg = self.message_queue[fd].pop(0)
                            out = next_msg
                            num = os.write(fd, out)
                            if num == len(out):
                                self.outputs.remove(fd)
                            else:
                                print('Leftovers', flush=True)
                                self.message_queue[fd].insert(0, out[num:])
                        else:
                            self.outputs.remove(fd)
                for fd in exceptional:
                    if fd == r:
                        raise Exception('Error in main pipe')
                    self.inputs.remove(fd)
                    if fd in self.outputs:
                        self.outputs.remove(fd)
                    if fd in self.message_queue:
                        del self.message_queue[fd]
                self.timeout = 10
                now = time.time()
                timed = []
                for i, timer in enumerate(self.timers):
                    secs_left = timer[0] - now
                    if secs_left <= 0:
                        timer[1](*timer[2], **timer[3])
                        timed.append(i)
                    elif secs_left < self.timeout:
                        self.timeout = secs_left
                count = 0
                for i in timed:
                    self.timers.pop(i-count)
                    count += 1
            except KeyboardInterrupt:
                sys.exit(0)
        # If we ever get here, just exit
        raise Exception('End of for loop')


    def add_timeout(self, secs, callback, *d, **p):
        self.timers.append((time.time() + secs, callback, d, p))


if __name__ == '__main__':
    host = 'localhost'
    port = 50000
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.setblocking(0)
    server.bind((host, port))
    server.listen(5)
    for x in range(3):
        pid = os.fork()
        if pid == 0:
            # We are now running the child process
            print('Child: {}'.format(os.getpid()), flush=True)
            loop = Loop(server)
            print(loop)
            def add_timer(loop, msg):
                print(msg)
                loop.add_timeout(3, add_timer, loop, msg)
            add_timer(loop, 'Now!')
            loop.run_forever()
    # We are still running the parent process and `pid` is the child PID
    print('Parent: {}, Child: {}'.format(os.getpid(), pid), flush=True)
    while True:
        sys.stdin.readline()
