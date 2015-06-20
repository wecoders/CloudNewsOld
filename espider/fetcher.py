# -*- coding: utf-8 -*-
#!/usr/bin/env python

import logging
import requests
#import chardet
from pyquery import PyQuery


def monkey_patch():
    prop = requests.models.Response.content
    def content(self):
        _content = prop.fget(self)
        #apparent_encoding = chardet.detect(_content)['encoding']
        #if apparent_encoding is None:
            
        apparent_encoding = 'UTF-8'
        logging.debug("encoding %s, %s, %s" % (self.encoding,apparent_encoding,requests.utils.get_encodings_from_content(_content)))
        if self.encoding == 'ISO-8859-1': # or self.encoding == 'gbk':
            encodings = requests.utils.get_encodings_from_content(_content)

            if encodings and (encodings[0] == 'UTF-8' or encodings[0] == 'UTF8' or encodings[0] == 'GB2312' or encodings[0] == 'GBK' or encodings[0] == 'gbk'):
                self.encoding = encodings[0]
            else:
                logging.debug("apparent_encoding: "+apparent_encoding)
                self.encoding = apparent_encoding
            _content = _content.decode(self.encoding, 'replace').encode('utf8', 'replace')
            self._content = _content
        
        return _content
    requests.models.Response.content = property(content)

monkey_patch()


class Fetcher(object):
    """docstring for Fetcher"""
    def __init__(self):
        super(Fetcher, self).__init__()
        
        
    def fetch(self, spider, task, headers={}):
        logging.debug("fetch ====== %s" % task)
        url = task.get('url')
        is_target = task.get('is_target')

        callback = None
        if 'callback' in task:
            callback = getattr(spider, task.get('callback'))
        
        response = self._fetch(url, headers)
        if response.get('code') == 200 and callback is not None:
            res = callback(response)
            if res is not None:
                #save res
                #insert into spider_result(task_id, url, result)
                pass
                    
        if task.get('type', None) == 'task':
            pass
            #update task status=response.get('code') where id=task['id']
        return response

    def _fetch(self, url, headers={}, timeout=60, proxies=None):
        logging.debug("start download ======== [%s], %s" % (url,type(url)))

        try:
            result = {}
            response = requests.get(url, headers=headers, timeout=timeout, proxies=proxies)
            logging.debug("requests response encoding =============== ************* %s" % response.encoding)
            if response.status_code != requests.codes.ok:
                return dict(code=response.status_code)

            html = response.content
            
            if 'Set-Cookie' in response.headers:
                cookies = response.headers['Set-Cookie']
                result['set-cookie'] = cookies
            content_type = response.headers.get('content-type')
            result['content-type'] = content_type
            result['code'] = 200
            result['content'] = html
            result['url'] = response.url
            result['origin_url'] = url
            result['doc'] = PyQuery(html)
            logging.debug("Download end ======== [%s]" % url)
            return result

        except Exception as e:
            logging.error("url:%s, %s" % (url,e))
            return dict(code=-1)

        return dict(code=-1)


