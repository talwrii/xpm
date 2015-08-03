# xpm

A native python library for producing XPM files from raster images.
For parsing XPM files I recommend PIL.

## Usage

### Command line

    python -m xpm image.bpm > image.xpm

Though for this use case you might prefer imagemagick.

### Python code

Using PIL:

    image = PIL.Image.open(args.file)
    xpm_string = pil_save(image, variable_name=args.variable_name)
    print(xpm_string)

Given a dictionary mapping pixels to RGB colours:

    black = (0, 0, 0)
    white = (255, 255, 255)
    image = [
          [black, white, black],
          [white, black, white],
          [black, white, black]]
    pixels = dict( ((i, j), colour)
        for j, row in enumerate(image)
            for i, colour in enumerate(row))
    xpm_im = xpm.XpmImage((3, 3), pixels).make_image
