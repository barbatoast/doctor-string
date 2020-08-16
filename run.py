#!/usr/bin/env python3

import os
import re

DOC_HEADER = \
"""
<!DOCTYPE HTML PUBLIC "-//IETF//DTD HTML//EN">
<html>
<head>
<title>Foo Client API</title>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
<link rel="stylesheet" type="text/css" media="screen,print" href="style.css" />
<meta name="viewport" content="width=device-width, initial-scale=1">
</head>
<body onload="displayDesc(event,'Introduction')">
<div class="header">
  <a href="https://google.com" class="normal"><img src="name.svg" width="240"></a><span class="api">v0.1.0 API Documentation</span>
</div>
<div class="page">
  <div class="index">
    <button class="item level1" onclick="displayDesc(event,'Introduction')">Introduction</button>

    <span class="cat">Types</span>
"""

DOC_FOOTER = \
"""
</div>
</div>
    <script>
function displayDesc(e,d){
    var all = document.getElementsByClassName('desc');
    for (var i = all.length - 1; 0 <= i; i--) {
        all[i].style.display = 'none';
    }
    all = document.getElementsByClassName('item');
    for (var i = all.length - 1; 0 <= i; i--) {
        all[i].className = all[i].className.replace(' selected', '');
    }
    document.getElementById(d).style.display = 'block';  
    e.currentTarget.className += ' selected';
}
    </script>
</body>
</html>
"""

DOC_BUTTON = '<button class="item level2" onclick="displayDesc(event,\'%s\')">%s</button>\n'

DOC_DIV_CLOSE = '</div>\n'

DOC_INTRO = \
"""
<! -- Introduction -->

<div class="desc-pane">
  <div id="Introduction" class="desc">
    <div class="title">Introduction</div>
      <p class="desc-text">
        Foo is a library.
      </p>
      <p class="desc-text">
        Foo needs a better name.
      </p>
      <p class="desc-text">
        Feedback is appreciated.
      </p>
  </div>
"""

DOC_PAGE_ID = \
"""
<div id="%s" class="desc">
  <div class="title">%s</div>
  <div class="synopsis">//TODO</div>
"""

DOC_PAGE_DESC = '<p class="desc-text">%s</p>\n'

DOC_TABLE = '<table class="params">\n'
DOC_TABLE_ROW = '<tr><td><span class="param">%s</span></td><td>%s</td></tr>\n'
DOC_TABLE_ROW_RETURN = '<tr><td class="returns">Returns:</td><td>%s</td></tr>'
DOC_TABLE_CLOSE = '</table>\n'

def remove_lines(lines, value):
    while True:
        try:
            lines.remove(value)
        except ValueError:
            break
    return  lines

def strip_lines(lines, value):
    ret = []
    for line in lines:
        ret.append(line.replace(value, ''))
    return ret

def parse_javadoc(javadoc):
    lines = javadoc.split('\n')
    lines = remove_lines(lines, '')
    lines = remove_lines(lines, ' ')
    lines = remove_lines(lines, ' *')
    lines = remove_lines(lines, ' * ')
    lines = strip_lines(lines, ' * ')

    brief_tag = ''
    desc_tag = ''
    param_tags = []
    return_tag = ''

    for line in lines:
        if '@brief' in line:
            ret = line.split(maxsplit=1)
            brief_tag = ret[1]
        elif '@param' in line:
            ret = line.split(maxsplit=2)
            del ret[0]
            param_tags.append(tuple(ret))
        elif '@return' in line:
            ret = line.split(maxsplit=1)
            return_tag = ret[1]
        else:
            if desc_tag == '':
                desc_tag = line
            else:
                desc_tag = desc_tag + ' ' + line

    javadoc_tags = {
        'brief_tag': brief_tag,
        'desc_tag': desc_tag,
        'param_tags': param_tags,
        'return_tag': return_tag,
    }

    return javadoc_tags

class Doctor:
    def __init__(self, file_list):
        self.file_list = file_list
        self.doc = open('doc/index.html', 'w')
        self.doc.write(DOC_HEADER)

    def parse_javadoc(self):
        headers = (f for f in self.file_list if '.h' in f)
        for header in headers:
            f = open(header, 'r')
            header_text = f.read()
            f.close()
            match = re.findall(r'/\*\*((.|\n)*?)\*/', header_text)

            if match is None:
                return

            tags_list = []
            javadocs = (f for f in match if '@file' not in f[0])
            for javadoc in javadocs:
                tags_list.append(parse_javadoc(javadoc[0]))

            # add buttons
            for tags in tags_list:
                self.doc.write(DOC_BUTTON % (tags['brief_tag'], tags['brief_tag']))
            self.doc.write('  ' + DOC_DIV_CLOSE)

            # add intorduction
            self.doc.write(DOC_INTRO)

            # add pages
            for tags in tags_list:
                self.doc.write(DOC_PAGE_ID % (tags['brief_tag'], tags['brief_tag']))
                self.doc.write('  ' + (DOC_PAGE_DESC % (tags['desc_tag'])))
                if len(tags['param_tags']) > 0:
                    # add params
                    self.doc.write('  ' + DOC_TABLE)
                    for param_tuple in tags['param_tags']:
                        self.doc.write('    ' + (DOC_TABLE_ROW % param_tuple))
                    if tags['return_tag'] != '':
                        self.doc.write('    ' + (DOC_TABLE_ROW_RETURN % (tags['return_tag'])))
                    self.doc.write('  ' + DOC_TABLE_CLOSE)
                self.doc.write(DOC_DIV_CLOSE)

        self.doc.write(DOC_FOOTER)

    def cleanup(self):
        self.doc.close()


def main():
    doctor = Doctor(os.listdir('.'))
    doctor.parse_javadoc()
    doctor.cleanup()

if __name__ == '__main__':
    main()
