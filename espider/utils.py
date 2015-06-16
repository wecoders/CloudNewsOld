# -*- coding: utf-8 -*-
#!/usr/bin/env python


import md5


def md5str(url):
    m = md5.new()
    m.update(url.strip())
    urlmd5 = m.hexdigest()
    return urlmd5 
