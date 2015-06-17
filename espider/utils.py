# -*- coding: utf-8 -*-
#!/usr/bin/env python


import md5


def md5str(url):
    m = md5.new()
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
        return "; ".join(['%s=%s'%(key,value) for (key,value) in cookie_header.items()])
    else:
        old_cookie_headers = split_cookie(old_cookie)
        new_cookies = dict(old_cookie_headers.items()+cookie_headers.items())
        return "; ".join(['%s=%s'%(key,value) for (key,value) in new_cookies.items()])

