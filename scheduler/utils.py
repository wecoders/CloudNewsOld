


def simple_escape(html):
    if html:
        html = html.replace('<', '&lt;').replace('>', '&gt;')
    else:
        html = ""
    return html

