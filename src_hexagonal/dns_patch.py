
# DNS TIMEOUT PATCH
import socket
import os

# Set conservative timeouts
socket.setdefaulttimeout(10)

# Configure DNS resolution
import urllib3
urllib3.disable_warnings()

# Patch requests library
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

def create_robust_session():
    session = requests.Session()
    retry = Retry(
        total=3,
        read=3,
        connect=3,
        backoff_factor=0.3,
        status_forcelist=(500, 502, 503, 504)
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    
    # Set timeouts
    session.timeout = (10, 60)  # (connect, read)
    return session

# Monkey-patch requests
original_get = requests.get
def patched_get(url, **kwargs):
    if 'timeout' not in kwargs:
        kwargs['timeout'] = (10, 60)
    return original_get(url, **kwargs)

requests.get = patched_get

print("[DNS PATCH] Applied robust DNS settings")
