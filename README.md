# Python Client/Server problem

## Requirement:

No Python 3!

### Client:

Minimal 3 running at the same time.

Each run a configurable length of time.

Log start/stop mesgs. Send these mesgs to server too.

1 thread writing data chunk to files. Both chunk and file size are configurable. When file reaches pre-configured size, roll over.

1 thread reporting CPU and mem info to server per 10 secs.

1 thread beacon the server per 5 secs.

### Server:

Handle concurrent clients

Write client perf info into db.

Log clients' heartbeat and other mesgs to log file.

When all clients finished, write a report then exits.

## Implementation:

### Client:

Using threading module.

CPU from self-calculation. MEM info from /proc/{PID}/status.

We assume the data chunk size is larger than file size.

Initial speed test to decide if the provided time span is enough for files to roll over twice at least. *This however, won't be accurate.*

### Server:

Using sqlite3 as DB.

Handles Ctrl+C.

Using a seperate thread to handle each client.

## Run:

### Client:

./client *server* *server-port*

### Server:

./server.py

## Note:

It would be interesting to implement this with twisted. We could also use SocketServer.

The CPU and MEM usage we got here is of the process, not the thread. This is not accurate. But given that the other 2 threads in the client do not eat much CPU or MEM, the current solution isn't too bad after all. Thread profiling may take a little longer time to implement.
