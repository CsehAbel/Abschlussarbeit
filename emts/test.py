import re
import numpy

import urllib.request

import bs4
import html5lib

def get_text_bs(html):
    tree = bs4.BeautifulSoup(html, 'html5lib')

    body = tree.body
    if body is None:
        return None

    for tag in body.select('script'):
        tag.decompose()
    for tag in body.select('style'):
        tag.decompose()

    text = body.get_text(separator='\n')
    return text


html = urllib.request.urlopen('https://totalcar.hu/magazin/hirek/')
raw = get_text_bs(html)

tidy = lambda c: re.sub(
    r'(^\s*[\r\n]+|^\s*\Z)|(\s*\Z|\s*[\r\n]+)',
    lambda m: '\n' if m.lastindex == 2 else '',
    c)
print(tidy(raw))