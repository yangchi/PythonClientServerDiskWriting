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

### Server:

Using sqlite3 as DB.

Handles Ctrl+C.
