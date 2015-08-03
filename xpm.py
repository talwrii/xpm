# make code as python 3 compatible as possible
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import sys
import collections
import itertools
import math
import string

COLOUR_DIGITS = (string.digits + string.ascii_lowercase).encode('ansii')

def pil_save(pil_image, variable_name=b'picture'):
    formatter = XpmImage.from_pil(pil_image, variable_name)
    return formatter.make_image()


class XpmImage(object):
    @classmethod
    def from_pil(cls, pil_image, variable_name=b'picture'):
        pil_image = pil_image.convert('RGB')
        transparent_colour = pil_image.info.get('transparency')
        return cls(pil_image.size, pil_image.load(), variable_name, transparent_colour)

    def __init__(self, size, pixels, variable_name=b'picture', transparent_colour=None):
        "Pixels is a dictionary mapping x,y coordinates to rgba tuples"
        self.xsize, self.ysize = size
        self.variable_name = variable_name
        self.pixels = pixels
        self.transparent_colour = transparent_colour
        colour_counts = collections.Counter(
            self.pixels[x, y]
            for x in range(self.xsize)
            for y in range(self.ysize))

        self.colours = [x
            for x, _ in sorted(
                colour_counts.items(), key=lambda x: -x[1])]

        self.colour_width = int(
            math.log(len(self.colours)) //
            math.log(len(COLOUR_DIGITS))) + 1

        self.colour_table = dict(
            zip(
                self.colours,
                enumerate_colours(self.colour_width)))

        self.add_pretty_colour_names()

    def add_pretty_colour_names(self):
        """Simple and varying characters
        make it a lot easier to see an image"""
        colours = list(self.colours)

        if self.transparent_colour:
            colours.remove(self.transparent_colour)
            colours = [self.transparent_colour] + colours

        PRETTY_NAMES = u' X+.|/'

        for colour, char in zip(
                colours[:len(PRETTY_NAMES)],
                PRETTY_NAMES):
            self.colour_table[colour] = (
                char.encode('ascii') * self.colour_width)


    def make_header(self):
        return b'\n'.join([
            b"/* XPM */",
            "static char* {}[] = {{".format(
                self.variable_name.decode('ascii')).encode('ascii'),
            b""])

    def make_footer(self):
        return b'};'

    def make_info(self):
        return ['"{} {} {} {}"'.format(
            self.xsize, self.ysize,
            len(self.colours), 1).encode('ascii')]

    def make_colour_table(self):
        for colour in self.colours:
            yield self.make_colour_entry(colour)

    def make_colour_entry(self, colour):
        return '"{}\tc {}"'.format(
            self.colour_table[colour].decode('ascii'),
            self.format_colour(colour)).encode('ascii')

    def format_colour(self, colour):
        if colour == self.transparent_colour:
            return 'None'
        else:
            return '#{}{}{}'.format(
                *['{:02x}'.format(c) for c in colour]
                ).encode('ascii')

    def make_pixels(self):
        for y in range(self.ysize):
            line = []
            for x in range(self.xsize):
                line.append(
                    self.colour_table[self.pixels[x, y]])
            yield b'"' + b''.join(line) + b'"'

    def make_image(self):
        return (
            self.make_header() +
            b',\n'.join(itertools.chain(
                    self.make_info(),
                    self.make_colour_table(),
                    self.make_pixels())) +
            self.make_footer())

def enumerate_colours(width):
    for x in itertools.product(*((COLOUR_DIGITS,) * width)):
        yield bytes(x)

if __name__ == '__main__':
    import PIL.Image
    import argparse

    PARSER = argparse.ArgumentParser(description=
        'Turn an image into an XPM assuming PIL can open it')
    PARSER.add_argument('file', type=str, help='file to convert')
    PARSER.add_argument('--variable-name', '-v', type=str,
        help='XPM files are valid C code creating a variable representing an image. The name of this variable', default='picture')
    args = PARSER.parse_args()
    image = PIL.Image.open(args.file)
    xpm_bytes = pil_save(
        image,
        variable_name=args.variable_name.encode('ascii'))

    if sys.version_info.major >= 3:
        sys.stdout.buffer.write(xpm_bytes)
    else:
        sys.stdout.write(xpm_bytes)
