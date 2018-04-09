# https://steelkiwi.com/blog/working-tcp-sockets/


import os
import select
import socket
import sys
import threading


def run(pipeout):
    inputs = [pipeout]
    outputs = []
    message_queue = {}
    
    while True:
        readable, writable, exceptional = select.select(inputs, outputs, inputs, 1)
        for fd in readable:
            if fd == pipeout:
                # 512 bytes in one go should be guaranteed atomic by POSIX standard for a pipe
                data = os.read(pipeout, 512)
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
            if fd == pipeout:
                raise Exception('Error in main pipe')
            inputs.remove(fd)
            if fd in outputs:
                outputs.remove(fd)
            if fd in message_queue:
                del message_queue[fd]


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.setblocking(0)
server.bind(('localhost', 50000))
server.listen(5)

r, w = os.pipe()
print('pipe r,w:', r, w)

t = threading.Thread(target=run, args=(r,))
# Terminate when the main thread ends
t.setDaemon(True)
t.start()

while True:
    readable, writable, exceptional = select.select([server], [], [])
    for s in readable:
        if s is server:
            connection, client_address = s.accept()
            print(connection.fileno(), client_address)
            os.set_blocking(connection.fileno(), False)
            # thread_queue.put_nowait(connection.fileno())
            print(os.write(w, str(connection.fileno()).encode('utf8')+b'\n'))




        #     while True:
        #         connection = thread_queue.get_nowait()
        #         inputs.append(connection)
        #         message_queue[connection] = []
        # except queue.Empty:
        #     pass


# https://www.python-course.eu/pipes.php

# https://www.python-course.eu/forking.php

# https://stackoverflow.com/questions/5060350/unix-pipes-between-child-processes
# https://stackoverflow.com/questions/9255425/writing-to-a-pipe-with-a-child-and-parent-process	
# https://stackoverflow.com/questions/2784500/how-to-send-a-simple-string-between-two-programs-using-pipes

# https://stackoverflow.com/questions/2989823/how-to-pass-file-descriptors-from-parent-to-child-in-python
# fd = _multiprocessing.recvfd(self.child_pipe.fileno())
# # rebuild the socket object from fd
# received_socket = socket.fromfd(fd, socket.AF_INET, socket.SOCK_STREAM)
# # socket.fromfd() duplicates fd, so we can close the received one
# os.close(fd)
# # and now you can communicate using the received socket
# received_socket.send("hello from the worker process\r\n")

