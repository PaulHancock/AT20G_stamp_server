#! python
import random
import string

from astropy.coordinates import SkyCoord
from astropy.io import fits
from astropy.nddata import Cutout2D
from astropy import units as u
from astropy.wcs import WCS

import os
localDir = os.path.dirname(__file__)
absDir = os.path.join(os.getcwd(), localDir)

import cherrypy
from cherrypy.lib import static

__author__ = 'Paul Hancock'
__date__ = ''


def cut_image(image, ra, dec, radius, outfile=None):
    """
    Make a cutout of a fits image and save it to the given file
    :param image: filename of fits image
    :param ra: ra in degrees
    :param dec: dec in degrees
    :param radius: radius in arcmin
    :param outfile: the output filename
    """
    position = SkyCoord(ra*u.degree, dec*u.degree, frame='icrs')
    hdu = fits.open(image)
    wcs = WCS(hdu[0].header)
    size = u.Quantity((radius, radius), u.arcmin)
    cutout = Cutout2D(hdu[0].data, position, size, wcs=wcs)
    hdu[0].header.update(dict(cutout.wcs.to_header().iteritems()))
    hdu[0].data = cutout.data
    if outfile is not None:
        hdu.writeto(outfile, overwrite=True)
    return hdu


class StringGenerator(object):
    @cherrypy.expose
    def index(self):
        return """<html>
          <head></head>
          <body>
            <form method="get" action="generate">
              <input type="text" value="8" name="length" />
              <button type="submit">Give it now!</button>
            </form>
            <form method="get" action="cutout">
              <p>Filename:</p>
                <input type="text" value="AT20G_trimmed/DEC-15-30_RA01.fits" name="image"/>
              <p>RA/Dec (dec degrees)</p>
                <input type="float" value=20 name="ra"/>
                <input type="float" value=-25 name="dec"/>
              <p>Radius (arcmin):</p>
                <input type="radius" value=15 name="radius"/>
              <button type="submit"> GO! </button>
            </form>
          </body>
        </html>"""

    @cherrypy.expose
    def generate(self, length=8):
        return ''.join(random.sample(string.hexdigits, int(length)))

    @cherrypy.expose
    def cutout(self, image, ra, dec, radius):
        # TODO:
        # parse ra/dec to accept various formats
        # check ra/dec is within the area covered
        # put min/max limits on radius and clip where required
        # remove the need to supply image name and calculate it automagically
        # instead of just d/l the file, go to a new page with a link to the download
        im = cut_image(image, 20, -30, 15, "temp/out.fits")
        path = os.path.join(absDir, "temp/out.fits")
        return static.serve_file(path, "application/x-download",
                                 "attachment", os.path.basename(path))


if __name__ == '__main__':
    cherrypy.quickstart(StringGenerator())

