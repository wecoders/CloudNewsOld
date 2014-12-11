import requests
import logging

def fetch(url, headers={}):
	logging.debug("fetch from url: %s" % url)
	response = requests.get(url, headers=headers, timeout=60)
	if response.status_code != requests.codes.ok:
	    return dict(code=response.status_code)
	# jsonres = json.loads(response.text)
	return dict(code=200, html=response.text)


