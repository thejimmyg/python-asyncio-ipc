# Problem with this approach is that because the server is shared in processes, they all trigger that it is ready to accept a connection, then only one of them gets it.


import os
import select
import socket
import sys
import time


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.setblocking(0)
# os.set_blocking(server.fileno(), False)
server.bind(('localhost', 50000))
server.listen(5)

for x in range(3):
    pid = os.fork()
    if pid == 0:
        # We are now running the child process
        print('Child: {}'.format(os.getpid()), flush=True)
    
        inputs = [server]
        outputs = []
        message_queue = {}
        
        while True:
            try:
                readable, writable, exceptional = select.select(inputs, outputs, inputs, 1)
                for fd in readable:
                    if fd is server:
                        print(os.getpid(), fd, server, server.fileno())
                        # The server fd is shared in child processes, but we rely on the OS to only allow one process to accept each connection.
                        try:
                            connection, client_address = server.accept()
                        except BlockingIOError as e:
                            # Don't worry, another child process probably just got this connection first
                            # there is nothing to do now
                            pass
                        else:
                            print(connection.fileno(), client_address)
                            os.set_blocking(connection.fileno(), False)
                            inputs.append(connection.fileno())
                            message_queue[connection.fileno()] = []
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
                    print('writable', fd, flush=True)
                    # Might have just been deleted
                    if fd in message_queue:
                        if message_queue[fd]:
                            next_msg = message_queue[fd].pop(0)
                            out = next_msg
                            num = os.write(fd, out)
                            if num == len(out):
                                outputs.remove(fd)
                            else:
                                print('Leftovers', flush=True)
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
            except BaseException as e:
                print(os.getpid, e, flush=True)
                print('Continuing anyway after 1 second wait', flush=True)
                time.sleep(1)
        # If we ever get here, just exit
        raise Exception('End of for loop')

# We are still running the parent process and `pid` is the child PID
print('Parent: {}, Child: {}'.format(os.getpid(), pid), flush=True)
while True:
    print('.', flush=True)
    time.sleep(1)
