# Server

```
python3 select_backwards_server_thread.py 
```

Then:

```
python3 backwards_client.py ; python3 backwards_client.py
```

Try killing it mid read to cause problems for the server.


Also, see this to see how to do file locking. Can use a timer with select rather than a sleep.

http://tilde.town/~cristo/file-locking-in-python.html
