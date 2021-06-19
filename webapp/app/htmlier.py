"""
Module for creating HTML pages.
"""


class HTMLier():
    def __init__(self):
        self.page =""


    def tag(self, name, body, **attrs):
        result = '<'+name
        for key, val in attrs.items():
            result += ' '+key+'="'+val+'"'
        result += '>'+body
        result += '</'+name+'>\n'
        return result

if __name__ == "__main__":
    htm = HTMLier()
    page = htm.tag('html',
        htm.tag('head', '') + 
        htm.tag('body', 
            htm.tag('h1', 'This is an HTML page.',style='color:#FF0000;')))
    print(page)
