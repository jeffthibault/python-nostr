# python-nostr
A Python library for making Nostr clients

# Details
This library can handle basic [Nostr](https://github.com/nostr-protocol/nips) operations described in NIP-01.

It leverages [websocket-client](https://github.com/websocket-client/websocket-client) for websocket operations and [secp256k1-py](https://github.com/rustyrussell/secp256k1-py) for key operations.

# Installation
1. Clone repository \
```git clone https://github.com/jeffthibault/python-nostr.git```
2. Install dependencies in repo \
```python -m venv venv``` \
```pip install -r requirements.txt```

Note 1: I wrote this with Python 3.9.5.<br />
Note 2: If the pip install fails, you might need to install wheel. Try ```pip install wheel```.

# Disclaimer
This library is in very early development and still a WIP.<br />
There are probably bugs.<br />
I need to add tests.<br />
I will try to create a [PyPI](https://pypi.org/) package at some point.<br />
