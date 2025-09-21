# -*- coding: utf-8 -*-
import os, time, socket, json, sys
import requests

API_KEY = os.environ.get('DEEPSEEK_API_KEY', '')
BASE_URL = 'https://api.deepseek.com/v1/chat/completions'
HEADERS = {
    'Authorization': f'Bearer {API_KEY}',
    'Content-Type': 'application/json',
}

def dns_check():
    t0=time.time()
    try:
        ip = socket.gethostbyname('api.deepseek.com')
        return {'ok': True, 'ip': ip, 'ms': int((time.time()-t0)*1000)}
    except Exception as e:
        return {'ok': False, 'error': str(e), 'ms': int((time.time()-t0)*1000)}


def call_deepseek(read_timeout: float, max_tokens: int, prompt: str):
    payload = {
        'model': 'deepseek-chat',
        'messages': [{'role': 'user', 'content': prompt}],
        'max_tokens': max_tokens,
        'temperature': 0.2,
        'stream': False,
    }
    t0=time.time()
    try:
        resp = requests.post(BASE_URL, headers=HEADERS, json=payload, timeout=(5, read_timeout))
        dt = time.time()-t0
        return {
            'ok': resp.status_code==200,
            'status': resp.status_code,
            'elapsed_s': round(dt,3),
            'body': (resp.text[:200] if not resp.ok else resp.json().get('choices',[{}])[0].get('message',{}).get('content','')[:200])
        }
    except Exception as e:
        dt = time.time()-t0
        return {'ok': False, 'error': f'{type(e).__name__}: {e}', 'elapsed_s': round(dt,3)}


def main():
    out = {'dns': dns_check(), 'calls': []}
    if not API_KEY:
        out['error'] = 'DEEPSEEK_API_KEY not set'
        print(json.dumps(out, indent=2)); return
    short = 'Ping. Return OK.'
    longp = 'Explain Maxwell equations briefly.' + ' Lorem ipsum'*400
    tests = [
        ('short_rt10', 10, 64, short),
        ('short_rt45', 45, 64, short),
        ('long_rt10', 10, 256, longp),
        ('long_rt45', 45, 256, longp),
    ]
    for name, rt, mt, p in tests:
        res = call_deepseek(rt, mt, p)
        out['calls'].append({'name': name, **res})
    print(json.dumps(out, indent=2))

if __name__=='__main__':
    main()
