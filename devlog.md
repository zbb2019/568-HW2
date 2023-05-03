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