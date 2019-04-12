#!/usr/bin/env python

__all__ = ['solve_field']

import os
import subprocess
from multiprocessing.pool import ThreadPool
from multiprocessing import cpu_count
from glob import glob

import numpy as np


def worker(cmd):
    """Basic worker."""

    p = subprocess.Popen(cmd)
    p.wait()


def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    
    for i in range(0, len(l), n):
        yield l[i:i + n]


def solve_field(name, ra=None, dec=None, radius=None, scale=None,
                suffix='_ast', wcs_output=False):

    """Perform astrometric transformation on input image.

    To find wcs transformation this method is use 'astrometry.net' app.
    If the image center coordinates, image size and pixel scale are
    entered, the solution will be reached quickly.

    Parameters
    ----------
    name : str or list
        The name of the image (fits).

    ra : str or None
        Right ascension of center of image.
        '13:55:45.12' in [hms]

    dec : str or None
        Declination of center of image.
        '36:49:27.13' in [dms]

    radius : float or None
        Radius of image in degrees.

    scale : tuple, list or None
        Scale of image pixel in arcsecond. (lower_bound, upper_bound)

    suffix : str
        Suffix for finale image. Default is '_ast'.
        star.fits will be like star_ast.fits when processes finished.

    wcs_output : bool
        Write wcs header of each image to folder with suffix '.wcs'.
        Default is False.

    Returns
    -------
        result : list
        Returns created images.

    Examples
    --------

    >>> imgs = sorted(glob('*.fits'))
    >>>
    >>> h = fits.getheader(imgs[0])
    >>> ra = h['OBJCTRA']
    >>> dec = h['OBJCTDEC']
    >>> radius = 0.35
    >>> scale = (0.6, 0.65)
    >>>
    >>> for img in imgs:
            solve_field(img, ra=ra, dec=dec, radius=radius, scale=scale)
    """

    if not isinstance(name, (str, list)):
        raise TypeError("'name' should be 'str' or 'list' object.")

    if ra is not None:
        if not isinstance(ra, str):
            raise TypeError("'ra' should be a 'str' object.")

    if dec is not None:
        if not isinstance(dec, str):
            raise TypeError("'dec' should be a 'str' object.")

    if radius is not None:
        if not isinstance(radius, float):
            raise TypeError("'radius' should be a 'float' object.")

    if scale is not None:
        if not isinstance(scale, (tuple, list)):
            raise TypeError("'scale' should be a 'tuple' object.")

    if not isinstance(suffix, str):
        raise TypeError("'suffix' should be a 'str' object.")

    cmd = ['solve-field', '-p', '-O', '--no-verify', '--no-remove-lines',
           '--depth', '20,30,40', '--resort', '--downsample', '2',
           '--match', 'none', '--rdls', 'none', '--corr', 'none',
           '--index-xyls', 'none', '--solved', 'none', '--temp-axy']

    if ra is not None:
        cmd.append('--ra')
        cmd.append(str(ra))

    if dec is not None:
        cmd.append('--dec')
        cmd.append(str(dec))

    if radius is not None:
        cmd.append('--radius')
        cmd.append(str(radius))

    if scale is not None:
        tmp = ['--scale-low', str(scale[0]), '--scale-high',
               str(scale[1]), '--scale-unit', 'arcsecperpix']
        cmd += tmp

    if isinstance(name, str):
        name = [name]

    cmds = list()
    for item in np.array_split(name, cpu_count()):
        if len(item) > 0:
            cmds.append(cmd + list(item))

    tp = ThreadPool(cpu_count())

    for cmd in cmds:
        tp.apply_async(worker, (cmd,))

    tp.close()
    tp.join()

    result = list()
    imgs = glob('*.new')
    for img in imgs:
        base = os.path.splitext(img)[0]
        filename = base + suffix + '.fits'
        result.append(filename)
        os.rename(img, filename)

    if not wcs_output:
        wcss = glob('*.wcs')
        for wcs in wcss:
            subprocess.run(['rm', wcs])

    return result
