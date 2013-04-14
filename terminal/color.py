# -*- coding: utf-8 -*-

# http://en.wikipedia.org/wiki/ANSI_escape_code
# http://en.wikipedia.org/wiki/Web_colors
# https://gist.github.com/MicahElliott/719710

import os
import sys

# Python 3
if sys.version_info[0] == 3:
    string_type = str
    unicode = str
else:
    string_type = basestring


def check_color_support():
    "Find out if your terminal environment supports color."
    # shinx.util.console
    if not hasattr(sys.stdout, 'isatty'):
        return False

    if not sys.stdout.isatty():
        return False

    if sys.platform == 'win32':
        try:
            import colorama
            colorama.init()
            return True
        except ImportError:
            return False

    if 'COLORTERM' in os.environ:
        return True

    term = os.environ.get('TERM', 'dumb').lower()
    return term in ('xterm', 'linux') or 'color' in term


_is_color_supported = check_color_support()


def check_256color_support():
    "Find out if your terminal environment supports 256 color."
    if not _is_color_supported:
        return False
    term = os.environ.get('TERM', 'dumb').lower()
    return '256' in term


_is_256color_supported = check_256color_support()


def rgb2ansi(r, g, b):
    """
    Convert an RGB color to 256 ansi graphics.
    """

    # Thanks to
    # https://github.com/tehmaze/ansi/blob/master/ansi/colour/rgb.py

    grayscale = False
    poss = True
    step = 2.5

    while poss:
        if min(r, g, b) < step:
            grayscale = max(r, g, b) < step
            poss = False

        step += 42.5

    if grayscale:
        return 232 + int(float(sum((r, g, b)) / 33.0))

    m = ((r, 36), (g, 6), (b, 1))
    return 16 + sum(int(6 * float(val) / 256) * mod for val, mod in m)


def hex2ansi(code):
    """
    Convert hex code to ansi.
    """

    if code.startswith('#'):
        code = code[1:]

    if len(code) == 3:
        # efc -> eeffcc
        return rgb2ansi(*map(lambda o: int(o * 2, 16), code))

    if len(code) != 6:
        raise ValueError('invalid color code')

    rgb = (code[:2], code[2:4], code[4:])
    return rgb2ansi(*map(lambda o: int(o, 16), rgb))


_reset = '\x1b[0;39;49m'
_styles = (
    'bold', 'faint', 'italic', 'underline', 'blink',
    'overline', 'inverse', 'conceal', 'strike',
)
_colors = (
    'black', 'red', 'green', 'yellow', 'blue',
    'magenta', 'cyan', 'white'
)


def _color2ansi(color):
    if color in _colors:
        return _colors.index(color)

    if isinstance(color, string_type):
        return hex2ansi(color)
    elif isinstance(color, (tuple, list)):
        return rgb2ansi(*color)

    raise ValueError('invalid color: %s' % color)


class Color(object):
    """
    Color object that holds the text and relevant color and style settings.

    You should always use the high-level API of colors and styles,
    such as :class:`red` and :class:`bold`.

    But if you are so interested in this module, you are welcome to
    use some advanced features::

        s = Color('text')
        print(s.bold.red.italic)

    All ANSI colors and styles are available on Color.
    """
    default_encoding = sys.stdout.encoding

    def __init__(self, raw, fgcolor=None, bgcolor=None, styles=None):
        if isinstance(raw, str):
            self.unicode_text = self.str_to_unicode(raw)
        elif isinstance(raw, unicode):
            self.unicode_text = raw
        elif isinstance(raw, Color):
            self.unicode_text = raw.unicode_text
            # Merge colors and styles
            if fgcolor is None:
                fgcolor = raw.fgcolor
            if bgcolor is None:
                bgcolor = raw.bgcolor
            if styles is None:
                styles = raw.styles
            else:
                styles = list(set(styles + raw.styles))
        else:
            raise ValueError('Only unicode and str types'
                             'or instance of Color are allowed')

        if fgcolor and not isinstance(fgcolor, int):
            fgcolor = _color2ansi(fgcolor)

        if bgcolor and not isinstance(bgcolor, int):
            bgcolor = _color2ansi(bgcolor)

        self.fgcolor = fgcolor
        self.bgcolor = bgcolor
        self.styles = styles or []

    def str_to_unicode(self, s):
        return s.decode(self.default_encoding)

    def unicode_to_str(self, u):
        return u.encode(self.default_encoding)

    def __getattr__(self, key):
        if key.endswith('_bg'):
            name = key[:-3]
            if name not in _colors:
                raise AttributeError("Color has no attribute '%s'" % key)
            self.bgcolor = _colors.index(name)
            return self

        if key in _colors:
            self.fgcolor = _colors.index(key)
            return self

        if key in _styles:
            code = _styles.index(key)
            self.styles.append(code + 1)
            return self
        try:
            return super(Color, self).__getattr__(key)
        except AttributeError:
            raise AttributeError("Color has no attribute '%s'" % key)

    def __str__(self):
        return self.unicode_to_str(self.__unicode__())

    def __unicode__(self):
        if not _is_color_supported:
            return self.unicode_text

        decorated = self.unicode_text

        if _is_256color_supported:
            if self.fgcolor is not None:
                decorated = '\x1b[38;5;%im%s%s' % (self.fgcolor, decorated, _reset)
            if self.bgcolor is not None:
                decorated = '\x1b[48;5;%im%s%s' % (self.bgcolor, decorated, _reset)
        else:
            if self.fgcolor is not None and self.fgcolor < 8:
                decorated = '\x1b[%im%s%s' % (30 + self.fgcolor, decorated, _reset)
            if self.bgcolor is not None and self.bgcolor < 8:
                decorated = '\x1b[%im%s%s' % (40 + self.bgcolor, decorated, _reset)

        if self.styles:
            code = ';'.join(str(i) for i in self.styles)
            decorated = '\x1b[%sm%s%s' % (code, decorated, _reset)

        return decorated

    def __repr__(self):
        return 'Color(%s, fgcolor=%s, bgcolor=%s, styles=%s)' %\
               (repr(self.unicode_text), self.fgcolor, self.bgcolor, self.styles)


def colorize(text, color):
    """
    Colorize text with hex code.

    :param text: the text you want to paint
    :param color: a hex color or rgb color

    ::

        colorize('hello', 'ff0000')
        colorize('hello', '#ff0000')
        colorize('hello', (255, 0, 0))

    """

    if color in _styles:
        c = Color(text)
        c.styles = [_styles.index(color) + 1]
        return c

    c = Color(text)
    c.fgcolor = _color2ansi(color)
    return c


def _create_color_func(fgcolor=None, bgcolor=None, styles=None):
    def color_func(text):
        c = Color(text, fgcolor=fgcolor, bgcolor=bgcolor, styles=styles)
        return c
    return color_func


# Style functions

bold = _create_color_func(styles=[1])

faint = _create_color_func(styles=[2])

italic = _create_color_func(styles=[3])

underline = _create_color_func(styles=[4])

blink = _create_color_func(styles=[5])

overline = _create_color_func(styles=[6])

inverse = _create_color_func(styles=[7])

conceal = _create_color_func(styles=[8])

strike = _create_color_func(styles=[9])


# Color functions

black = _create_color_func(fgcolor=0)

red = _create_color_func(fgcolor=1)

green = _create_color_func(fgcolor=2)

yellow = _create_color_func(fgcolor=3)

blue = _create_color_func(fgcolor=4)

magenta = _create_color_func(fgcolor=5)

cyan = _create_color_func(fgcolor=6)

white = _create_color_func(fgcolor=7)

if _is_256color_supported:
    gray = _create_color_func(fgcolor=8)
else:
    gray = _create_color_func(fgcolor=0, styles=[8])

grey = gray


# Background functions

black_bg = _create_color_func(bgcolor=0)

red_bg = _create_color_func(bgcolor=1)

green_bg = _create_color_func(bgcolor=2)

yellow_bg = _create_color_func(bgcolor=3)

blue_bg = _create_color_func(bgcolor=4)

magenta_bg = _create_color_func(bgcolor=5)

cyan_bg = _create_color_func(bgcolor=6)

white_bg = _create_color_func(bgcolor=7)

if _is_256color_supported:
    gray_bg = _create_color_func(bgcolor=8)
else:
    gray_bg = _create_color_func(bgcolor=0, styles=[1])

grey_bg = gray_bg
