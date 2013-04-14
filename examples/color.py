# -*- coding: utf-8 -*-

import sys
from terminal import color

text = u'Lorem 中 Ipsum 文'.encode(sys.stdout.encoding)

print '\nColors:\n'
for color_name in color._colors:
    print getattr(color, color_name)(text), ' <- ' + color_name

print '\n\nStyles:\n'
for style_name in color._styles:
    print getattr(color, style_name)(text), ' <- ' + style_name

print '\n\nStyles(Colors):\n'
for style_name in color._styles:
    style_func = getattr(color, style_name)
    for color_name in color._colors:
        color_func = getattr(color, color_name)
        print style_func(color_func(text)), ' <- %s(%s)' % (style_name, color_name)

print '\n\nColors(Styles):\n'
for color_name in color._colors:
    color_func = getattr(color, color_name)
    for style_name in color._styles:
        style_func = getattr(color, style_name)
        print color_func(style_func(text)), ' <- %s(%s)' % (color_name, style_name)

print '\n\nComplex combinations\n'
print color.italic(color.bold(color.red(text))), ' <- italic+bold+red'
