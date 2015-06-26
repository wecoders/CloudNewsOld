# -*- coding: utf-8 -*-
#!/usr/bin/env python


import hashlib

class TestClass(object):
    """docstring for TestClass"""
    def __init__(self, arg):
        super(TestClass, self).__init__()
        self.arg = arg
        

def md5str(url):
    if type(url) == str:
        url = url.encode('utf-8')
    m = hashlib.md5()
    m.update(url.strip())
    urlmd5 = m.hexdigest()
    return urlmd5 

def split_cookie(cookies):
    cookie_headers = {}
    c_arr = cookies.split(';')
    for i in c_arr:
        i = i.strip()
        s = i.split('=')
        if len(s)==2:
            k = s[0]
            v = s[1]
            if k == 'path' or k == 'HttpOnly':
                continue
            cookie_headers[k] = v
    return cookie_headers

def merge_cookie(new_cookie, old_cookie):
    cookie_headers = split_cookie(new_cookie)

    if old_cookie is None:
        return "; ".join(['%s=%s'%(key,value) for (key,value) in cookie_headers.items()])
    else:
        old_cookie_headers = split_cookie(old_cookie)
        new_cookies = dict(old_cookie_headers)
        new_cookies.update(cookie_headers)# dict(old_cookie_headers.items()+cookie_headers.items())
        return "; ".join(['%s=%s'%(key,value) for (key,value) in new_cookies.items()])



def import_object(name, arg=None):
    
    if '.' not in name:
        return __import__(name)
    parts = name.split('.')
    #try:
    print('.'.join(parts[:-1]))
    obj = __import__('.'.join(parts[:-1]), None, None, [parts[-1]], 0)
    #except ImportError:
    #    obj = None
    o = getattr(obj, parts[-1], arg)
    print(name, o, obj, o())
    return o

