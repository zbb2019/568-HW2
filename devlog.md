# Development Log
## 1. dummy proxy
This proxy returns "Hello World" to the client. It is single-threaded. Use the following commands to test it:
```bash
python3 dummy_proxy.py
# in another terminal:
wget http://www.google.com/ -e use_proxy=yes -e http_proxy=127.0.0.1:12345
```