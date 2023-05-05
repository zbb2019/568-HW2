# Development Log

## 1. dummy proxy

This proxy returns "Hello World" to the client. It is single-threaded. Use the following commands to test it:

```bash
python3 proxy.py
# in another terminal:
wget http://www.google.com/ -e use_proxy=yes -e http_proxy=127.0.0.1:12345
```

## 2. multi-thread

This proxy is multi-threaded now.

## 3. recognize HTTP request type

Parse the request header and extract the HTTP verb.  
> **⚠️Danger**  
>
> - the client may send a malformed HTTP request:
> - the client may close the connection before sending a whole HTTP request
> - the HTTP header may be too long to fit in a single TCP packet  
> Solution: close the connection if any of the above happens

## 4. Support HTTP CONNECT

The proxy now supports HTTPS tunnels. Tested with curl and browser. YouTube works fine.
> **⚠️Danger**
>
> - the client may send an invalid path
>   - Send a 400 Bad Request response to the client
> - the remote server may not be reachable:
>   - Send a 502 Bad Gateway response to the client

## 5. Support HTTP GET

Basically the same as CONNECT. At the first request, instead of responding to the client, the proxy will send the request to the remote server and start bi-directional forwarding.

POST can be supported in the same way.

## 6. Support Logging

Used the Python logging module to log. It is thread-safe.
