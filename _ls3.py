# -*- coding: utf-8 -*-
import os
base = os.path.join(os.path.dirname(os.path.abspath(__file__)), '_live_verify3')
for d in [base, os.path.join(base, 'banks'), os.path.join(base, 'nks')]:
    try:
        items = [(x, os.path.getsize(os.path.join(d, x))) for x in os.listdir(d)]
        print(repr(d), '->', [(repr(n), s) for n, s in items])
    except Exception as e:
        print(repr(d), 'ERR', repr(e))
