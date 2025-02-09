"""Download SRTM data."""

import os
from zipfile import ZipFile

try:
    from urllib.request import urlretrieve  # Python 3
except ImportError:
    from urllib import urlretrieve  # urlretrieve with Python 2
try:
    from urllib.error import HTTPError  # Python 3
except ImportError:
    from urllib2 import HTTPError  # HTTPError with Python 2

from ...misc import make_dir
from ..extent_shp import extent_shp
from .tiles_srtm import tiles_srtm


def download_srtm(iso3, output_dir="."):
    """Download SRTM data for a country.

    Download SRTM data (Shuttle Radar Topographic Mission v4.1) from
    CSI-CGIAR for a specific country. This function uses the iso3 code
    to download the country borders (as a shapefile) from `GADM
    <https://gadm.org>`_. Download is skipped if the shapefile is
    already present. Country borders are used to identify the SRTM
    tiles to be downloaded.

    :param iso3: Country ISO 3166-1 alpha-3 code.

    :param output_dir: Directory where data is downloaded. Default to
        current working directory.

    """

    # Create directory
    make_dir(output_dir)

    # Check for existing data
    shp_name = os.path.join(output_dir, "gadm36_" + iso3 + "_0.shp")
    if os.path.isfile(shp_name) is not True:

        # Download the zipfile from gadm.org
        fname = os.path.join(output_dir, iso3 + "_shp.zip")
        url = (
            "https://biogeo.ucdavis.edu/data/gadm3.6/"
            "shp/gadm36_" + iso3 + "_shp.zip"
        )
        urlretrieve(url, fname)

        # Extract files from zip
        with ZipFile(fname) as file:
            file.extractall(output_dir)

    # Compute extent and SRTM tiles
    extent_latlong = extent_shp(shp_name)
    tiles_long, tiles_lat = tiles_srtm(extent_latlong)
    tiles_long = tiles_long.split("-")
    tiles_lat = tiles_lat.split("-")
    # Convert to list of integers
    tiles_long = [int(i) for i in tiles_long]
    tiles_lat = [int(j) for j in tiles_lat]
    tlong_seq = list(range(tiles_long[0], tiles_long[1] + 1))
    tlat_seq = list(range(tiles_lat[0], tiles_lat[1] + 1))

    # Download SRTM data from CSI CGIAR
    for (i, tlong_i) in enumerate(tlong_seq):
        for (j, tlat_j) in enumerate(tlat_seq):
            # Convert to string
            tlong = str(tlong_i).zfill(2)
            tlat = str(tlat_j).zfill(2)
            # Check for existing data
            fname = os.path.join(
                output_dir,
                "SRTM_V41_" + tlong + "_" + tlat + ".zip"
            )
            if os.path.isfile(fname) is not True:
                # Download
                url = [
                    "http://srtm.csi.cgiar.org/",
                    "wp-content/uploads/files/srtm_5x5/TIFF/srtm_",
                    tlong,
                    "_",
                    tlat,
                    ".zip",
                ]
                url = "".join(url)
                try:
                    urlretrieve(url, fname)
                except HTTPError as err:
                    if err.code == 404:
                        msg = [
                            "SRTM not existing for tile: ",
                            tlong,
                            "_",
                            tlat
                        ]
                        msg = "".join(msg)
                        print(msg)
                    else:
                        raise


# End
