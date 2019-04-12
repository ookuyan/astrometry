# astrometry
An astrometric solution tool which use 'astrometry.net'.

## Usage

Perform astrometric transformation on input image.

To find wcs transformation this method is use 'astrometry.net' app.
If the image center coordinates, image size and pixel scale are
entered, the solution will be reached quickly.

### Parameters

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

### Returns

result : list
    Returns created images.

### Examples

```python
from astrometry import solve_field


imgs = sorted(glob('*.fits'))

h = fits.getheader(imgs[0])
ra = h['OBJCTRA']
dec = h['OBJCTDEC']
radius = 0.35
scale = (0.6, 0.65)

for img in imgs:
    solve_field(img, ra=ra, dec=dec, radius=radius, scale=scale)
```
