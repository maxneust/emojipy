# -*- coding: utf-8; -*-

from __future__ import unicode_literals
import re
import six
if six.PY3:
    from html import escape, unescape
else:
    from cgi import escape
    from HTMLParser import HTMLParser
    import struct
    unescape = HTMLParser.unescape
    chr = unichr

from .ruleset import unicode_replace,\
    shortcode_replace, ascii_replace


class Emoji(object):

    ascii = False
    unicode_alt = True
    image_type = 'png'
    cache_bust_param = '?v=1.2.5'
    sprites = False
    image_png_path = 'https://cdn.jsdelivr.net/emojione/assets/png/'
    image_svg_path = 'https://cdn.jsdelivr.net/emojione/assets/svg/'
    image_path_svg_sprites = './../../assets/sprites/emojione.sprites.svg'
    ignored_regexp = '<object[^>]*>.*?<\/object>|<span[^>]*>.*?<\/span>|<(?:object|embed|svg|img|div|span|p|a)[^>]*>'
    unicode_regexp = "(" + '|'.join([re.escape(x.decode("utf-8")) for x in sorted(unicode_replace.keys(), key=lambda k: len(k), reverse=True)]) + ")"
    shortcode_regexp = ':([-+\\w]+):'
    ascii_regexp = '(\\<3|&lt;3|\\<\\/3|&lt;\\/3|\\:\'\\)|\\:\'\\-\\)|\\:D|\\:\\-D|\\=D|\\:\\)|\\:\\-\\)|\\=\\]|\\=\\)|\\:\\]|\'\\:\\)|\'\\:\\-\\)|\'\\=\\)|\'\\:D|\'\\:\\-D|\'\\=D|\\>\\:\\)|&gt;\\:\\)|\\>;\\)|&gt;;\\)|\\>\\:\\-\\)|&gt;\\:\\-\\)|\\>\\=\\)|&gt;\\=\\)|;\\)|;\\-\\)|\\*\\-\\)|\\*\\)|;\\-\\]|;\\]|;D|;\\^\\)|\'\\:\\(|\'\\:\\-\\(|\'\\=\\(|\\:\\*|\\:\\-\\*|\\=\\*|\\:\\^\\*|\\>\\:P|&gt;\\:P|X\\-P|x\\-p|\\>\\:\\[|&gt;\\:\\[|\\:\\-\\(|\\:\\(|\\:\\-\\[|\\:\\[|\\=\\(|\\>\\:\\(|&gt;\\:\\(|\\>\\:\\-\\(|&gt;\\:\\-\\(|\\:@|\\:\'\\(|\\:\'\\-\\(|;\\(|;\\-\\(|\\>\\.\\<|&gt;\\.&lt;|\\:\\$|\\=\\$|#\\-\\)|#\\)|%\\-\\)|%\\)|X\\)|X\\-\\)|\\*\\\\0\\/\\*|\\\\0\\/|\\*\\\\O\\/\\*|\\\\O\\/|O\\:\\-\\)|0\\:\\-3|0\\:3|0\\:\\-\\)|0\\:\\)|0;\\^\\)|O\\:\\-\\)|O\\:\\)|O;\\-\\)|O\\=\\)|0;\\-\\)|O\\:\\-3|O\\:3|B\\-\\)|B\\)|8\\)|8\\-\\)|B\\-D|8\\-D|\\-_\\-|\\-__\\-|\\-___\\-|\\>\\:\\\\|&gt;\\:\\\\|\\>\\:\\/|&gt;\\:\\/|\\:\\-\\/|\\:\\-\\.|\\:\\/|\\:\\\\|\\=\\/|\\=\\\\|\\:L|\\=L|\\:P|\\:\\-P|\\=P|\\:\\-p|\\:p|\\=p|\\:\\-Þ|\\:\\-&THORN;|\\:Þ|\\:&THORN;|\\:þ|\\:&thorn;|\\:\\-þ|\\:\\-&thorn;|\\:\\-b|\\:b|d\\:|\\:\\-O|\\:O|\\:\\-o|\\:o|O_O|\\>\\:O|&gt;\\:O|\\:\\-X|\\:X|\\:\\-#|\\:#|\\=X|\\=x|\\:x|\\:\\-x|\\=#)'
    shortcode_compiled = re.compile(ignored_regexp+"|("+shortcode_regexp+")",
                                    re.IGNORECASE)
    unicode_compiled = re.compile(ignored_regexp+"|("+unicode_regexp+")",
                                  re.UNICODE)
    ascii_compiled = re.compile(ignored_regexp+"|("+ascii_regexp+")",
                                re.IGNORECASE)

    unicode_compiled_single_group = re.compile(unicode_regexp)

    @classmethod
    def match(cls, text):
        return re.search(cls.unicode_compiled, text)

    @classmethod
    def split_emojis(cls, text):
        return re.split(cls.unicode_compiled_single_group, text)

    @classmethod
    def to_image(cls, text, **kwargs):
        text = cls.unicode_to_image(text, **kwargs)
        text = cls.shortcode_to_image(text, **kwargs)

        return text

    @classmethod
    def unicode_to_image(cls, text, **kwargs):
        def replace_unicode(match):
            unicode_char = text[match.start():match.end()]
            unicode_encoded = unicode_char.encode('utf-8')
            if not unicode_encoded or unicode_encoded not in unicode_replace:
                return unicode_char  # unsupported unicode char
            shortcode = unicode_replace[unicode_encoded]
            if cls.unicode_alt:
                alt = unicode_char
            else:
                alt = shortcode
            filename = shortcode_replace[shortcode]
            css = kwargs.get('css')
            style = kwargs.get('style', '')
            if style:
                style='style="%s"' % (style,)

            if cls.image_type == 'png':
                if cls.sprites:
                    return '<span %s class="emojione emojione-%s %s" title="%s">%s</span>'\
                        % (style, filename, css, escape(shortcode), alt)
                else:
                    return '<img %s class="emojione %s" alt="%s" src="%s"/>' % (
                        style, css, alt,
                        cls.image_png_path+filename+'.png'+cls.cache_bust_param
                    )
            else:
                if cls.sprites:
                    return '<svg %s class="emojione %s"><description>%s</description>\
                    <use xlink:href="%s#emoji-%s"</use></svg>' % (
                        style, css, alt, cls.image_path_svg_sprites, filename
                    )
                else:
                    return '<object %s class="emojione %s" data="%s" \
                    type="image/svg+xml" standby="%s"> %s</object>' % (
                        style, css,
                        cls.image_svg_path+filename+'.svg'+cls.cache_bust_param, alt, alt
                    )

        text = re.sub(cls.unicode_compiled, replace_unicode, text)
        return text

    @classmethod
    def unicode_to_shortcode(cls, text):
        def replace_unicode(match):
            unicode_char = text[match.start():match.end()]
            unicode_encoded = unicode_char.encode('utf-8')
            if not unicode_encoded or unicode_encoded not in unicode_replace:
                return unicode_char  # unsupported unicode char
            return unicode_replace[unicode_encoded]

        text = re.sub(cls.unicode_compiled, replace_unicode, text)
        return text

    @classmethod
    def shortcode_to_image(cls, text, **kwargs):
        def replace_shortcode(match):
            shortcode = text[match.start():match.end()]
            if not shortcode or shortcode not in shortcode_replace:
                return shortcode
            unicode = shortcode_replace[shortcode]
            if cls.unicode_alt:
                alt = cls.convert(unicode)
            else:
                alt = shortcode
            filename = shortcode_replace[shortcode]
            css = kwargs.get('css', '')
            style = kwargs.get('style', '')
            if style:
                style='style="%s"' % (style,)
            if cls.image_type == 'png':
                if cls.sprites:
                    return '<span %s class="emojione emojione-%s %s" title="%s">%s</span>'\
                        % (style, css, filename, escape(shortcode), alt)
                else:
                    return '<img %s class="emojione %s" alt="%s" src="%s"/>' % (
                        style, css, alt,
                        cls.image_png_path+filename+'.png'+cls.cache_bust_param
                    )
            else:
                if cls.sprites:
                    return '<svg %s class="emojione %s"><description>%s</description>\
                    <use xlink:href="%s#emoji-%s"</use></svg>' % (
                        style, css, alt, cls.image_path_svg_sprites, filename)
                else:
                    return '<object %s class="emojione %s" data="%s" \
                    type="image/svg+xml" standby="%s"> %s</object>' % (
                        style, css, cls.image_svg_path+filename+'.svg'+cls.cache_bust_param, alt, alt)

        text = re.sub(cls.shortcode_compiled, replace_shortcode, text)
        if cls.ascii:
            return cls.ascii_to_image(text)
        return text

    @classmethod
    def shortcode_to_ascii(cls, text, **kwargs):
        def replace_shortcode(match):
            shortcode = text[match.start():match.end()]
            if not shortcode or shortcode not in shortcode_replace:
                return shortcode
            unicode = shortcode_replace[shortcode]
            reverse_ascii_unicode = {v: k for k, v in ascii_replace.items()}
            if unicode in reverse_ascii_unicode:
                return reverse_ascii_unicode[unicode]
            return shortcode

        return re.sub(cls.shortcode_compiled, replace_shortcode, text)

    @classmethod
    def shortcode_to_unicode(cls, text, **kwargs):
        def replace_shortcode(match):
            shortcode = text[match.start():match.end()]
            if not shortcode or shortcode not in shortcode_replace:
                return shortcode
            flipped_unicode_replace = {v: k for k, v in unicode_replace.items()}
            if shortcode in flipped_unicode_replace:
                return flipped_unicode_replace[shortcode].decode('utf8')
            return shortcode
        text = re.sub(cls.shortcode_compiled, replace_shortcode, text)
        if cls.ascii:
            return cls.ascii_to_unicode(text)
        return text

    @classmethod
    def ascii_to_unicode(cls, text, **kwargs):
        def replace_ascii(match):
            ascii = text[match.start():match.end()]
            ascii = unescape(ascii)  # convert escaped HTML entities back to original chars
            if not ascii or ascii not in ascii_replace:
                return ascii
            return cls.convert(ascii_replace[ascii])
        return re.sub(cls.ascii_compiled, replace_ascii, text)

    @classmethod
    def ascii_to_image(cls, text, **kwargs):
        def replace_ascii(match):
            ascii = text[match.start():match.end()]
            ascii = unescape(ascii)  # convert escaped HTML entities back to original chars
            if not ascii or ascii not in ascii_replace:
                return ascii
            unicode = ascii_replace[ascii]
            if cls.unicode_alt:
                alt = cls.convert(unicode)
            else:
                alt = escape(ascii)
            css = kwargs.get('css')
            style = kwargs.get('style', '')
            if style:
                style='style="%s"' % (style,)
            if cls.image_type == 'png':
                if cls.sprites:
                    return '<span %s class="emojione %s emojione-%s" title="%s">%s</span>'\
                        % (style, css, unicode, escape(ascii), alt)
                else:
                    return '<img %s class="emojione %s" alt="%s" src="%s"/>' % (
                        style, css, alt,
                        cls.image_png_path+unicode+'.png'+cls.cache_bust_param
                    )
            else:
                if cls.sprites:
                    return '<svg %s class="emojione %s"><description>%s</description>\
                    <use xlink:href="%s#emoji-%s"</use></svg>' % (
                        style, css, alt, cls.image_path_svg_sprites, unicode)
                else:
                    return '<object %s class="emojione %s" data="%s" \
                    type="image/svg+xml" standby="%s"> %s</object>' % (
                        style, css, cls.image_svg_path+unicode+'.svg'+cls.cache_bust_param,
                        alt, alt)
        return re.sub(cls.ascii_compiled, replace_ascii, text)

    @classmethod
    def convert(cls, hex_unicode):

        def char(i):
            try:
                return chr(i)
            except ValueError:
                return struct.pack('i', i).decode('utf-32')

        """
        Convert a unicode in hex string to actual unicode char
        """

        if '-' not in hex_unicode:
            return char(int(hex_unicode, 16))
        parts = hex_unicode.split('-')
        return ''.join(char(int(x, 16)) for x in parts)
