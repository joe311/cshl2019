from __future__ import print_function

from xml.etree import ElementTree as ET
import numpy as np
from qtpy import QtCore, QtGui, QtSvg
import qimage2ndarray
import svgwrite
from svgwrite import shapes
import cairosvg
from skimage.io import imread
from io import BytesIO

ET.register_namespace('', "http://www.w3.org/2000/svg")


def intensity_to_rgb(intensity):
    """
    Converts a float (0 to 1) into RGB str for SVG
    """
    assert 0 <= intensity <= 1
    return "({0:%}%, {0:%}%, {0:%}%)".format('test')


def generate_circle_svg(x=60, y=60, r=30, width=792, height=600, fill="white"):
    dwg = svgwrite.Drawing('temp.svg', profile='tiny', size=("%dpx" % width, "%dpx" % height))  # , style="background-color:black")
    dwg.add(shapes.Rect(insert=('-50%', '-50%'), size=('200%', '200%'), fill='black', ))
    dwg.add(shapes.Circle((x, y), r, fill=fill, stroke_width=0, stroke="red", shape_rendering="crispEdges"))
    return dwg.tostring()


def generate_circles_svg(xlist, ylist, rlist, width=792, height=600, colors=['white']):  # colorhexes=["ff"]):
    if len(colors) < len(xlist):
        colors = colors * len(xlist)
    assert len(xlist) == len(ylist) == len(rlist) == len(colors)
    dwg = svgwrite.Drawing('temp.svg', profile='tiny', size=("%dpx" % width, "%dpx" % height))  # , style="background-color:black")
    dwg.add(shapes.Rect(insert=('-50%', '-50%'), size=('200%', '200%'), fill='black', ))
    for x, y, r, fill in enumerate(xlist, ylist, rlist, colors):
        dwg.add(shapes.Circle((x, y), r, fill=fill, stroke_width=0, stroke="red", shape_rendering="crispEdges"))
    return dwg.tostring()


def empty_svg():
    return "<svg></svg>"


def add_background(svg):
    p = ET.ElementTree(ET.fromstring(svg))
    root = p.getroot()
    root.insert(0, ET.fromstring(shapes.Rect(insert=('-50%', '-50%'), size=('200%', '200%'), fill='black', ).tostring()))
    # root.set('style', "background-color:black") #this works in browser, but not for all renderers, eg cairo
    # root.set('viewport-fill', 'black') #this works in browser, but not for all renderers, eg cairo
    return ET.tostring(root)


def set_svg_bounds(svg, x, y, w, h):
    p = ET.ElementTree(ET.fromstring(svg))
    root = p.getroot()
    root.attrib['viewBox'] = '%.4f %.4f %.4f %.4f' % (x, y, w, h)
    root.attrib['height'] = '100%'
    root.attrib['width'] = '100%'
    return ET.tostring(root)


def set_svg_bounds_centered(svg, w, h):
    x = -w / 2
    y = -h / 2
    return set_svg_bounds(svg, x, y, w, h)


def surface_to_np(surface):
    """ Transforms a Cairo surface into a numpy array. """
    # Could also try: https://pycairo.readthedocs.io/en/latest/integration.html - but this is for cairo, not cairosvg

    temp_buf = BytesIO()
    surface.cairo.write_to_png(temp_buf)
    surface.finish()
    temp_buf.seek(0)
    return imread(temp_buf)  # WxHx4 - RGBA


def svg_to_np(svg_bytestring, dpi):
    """ Renders a svg bytestring as a RGB image in a numpy array """

    # svg_surface = cairo.SVGSurface(None, width, height)
    # svg_context = cairo.Context(svg_surface)
    # svg_context.save()
    # # svg_context.scale(width / unscaled_width, height / unscaled_height)
    # svg.render_cairo(svg_context)
    # svg_context.restore()

    tree = cairosvg.parser.Tree(bytestring=svg_bytestring)
    surf = cairosvg.surface.SVGSurface(tree, output=None, dpi=dpi, scale=1)  # , parent_width=400, parent_height=400)
    #sometimes this doesn't get size exactly right

    return surface_to_np(surf)
    # TODO detect if anything is clipped, ie any SVG elements are outside the viewBox
    # could use uDOM with SVGlocatable, http://www.w3.org/TR/SVGTiny12/svgudom.html#svg__SVGLocatable


def svg_to_np_qt(svg_bytestring, size):
    """ Renders a svg bytestring as a RGB image in a numpy array
    However, the QT backend seems to have some issues
    """
    if isinstance(svg_bytestring, str):
        svg_bytestring = bytes(svg_bytestring, 'ascii')
    ren = QtSvg.QSvgRenderer(svg_bytestring)
    assert ren.isValid(), "SVG rendering failed"

    qimg = QtGui.QImage(size[0], size[1], QtGui.QImage.Format_RGB32)  # QtGui.QImage.Format_ARGB32_Premultiplied)
    # TODO colors is wrong - maybe see https://doc.qt.io/qt-5/qimage.html
    # raise NotImplementedError #TODO handle size/dpi

    imagePainter = QtGui.QPainter(qimg)
    ren.render(imagePainter)
    imagePainter.end()
    arr = qimage2ndarray.byte_view(qimg)
    return arr


def insert_transform(svg, transform_matrix):
    transform_matrix = np.asarray(transform_matrix)

    p = ET.ElementTree(ET.fromstring(svg))
    root = p.getroot()
    elems = [elem for elem in root]
    for elem in elems:
        root.remove(elem)

    matrix_string = "matrix(%f, %f, %f, %f, %f, %f)" % tuple(transform_matrix[:2, :].ravel()[[0, 3, 1, 4, 2, 5]])
    g = ET.SubElement(root, 'g', transform=matrix_string)

    [g.append(elem) for elem in elems]
    return ET.tostring(root)


if __name__ == '__main__':
    # svg = generate_circle_svg(0, 0, fill='#ffffff')
    # print(svg)
    svg = b'<svg xmlns="http://www.w3.org/2000/svg" baseProfile="tiny" height="100%" style="background-color:black" version="1.2" viewBox="-200.0000 -200.0000 400.0000 400.0000" width="100%">\n<rect fill="black" height="200%" width="200%" x="-50%" y="-50%" /><defs>        <linearGradient id="MyGradient">\n            <stop offset="0%" stop-color="#000000" />\n            <stop offset="100%" stop-color="#ffffff" />\n        </linearGradient>\n</defs>\n    <rect fill="url(#MyGradient)" height="100" transform="translate(0) rotate(0 40 40)" width="80" x="10" y="-50" />\n\n</svg>'

    svg = add_background(svg)
    svg = set_svg_bounds_centered(svg, 400, 400)
    print(svg)

    arr = svg_to_np(svg, 15.0)
    print(arr.shape)
    from matplotlib import pyplot as plt

    plt.imshow(arr)
    # plt.axis('off')
    plt.show()
