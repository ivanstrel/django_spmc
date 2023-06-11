import os
import shutil
import subprocess

from django.conf import settings
from django.contrib.gis.gdal import GDALRaster
from django.core.files.temp import NamedTemporaryFile


def handle_tiles_upload(f_obj, uuid):
    # Process upload
    tmp_file = NamedTemporaryFile()
    for chunk in f_obj.chunks():
        tmp_file.write(chunk)
    # Prepare tiles folder
    # Define the output directory name folder based on the provided uuid
    output_dir = f"{settings.MEDIA_ROOT}/tiles/{uuid}"

    # Check if output path exists, and create or recreate it
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    else:
        shutil.rmtree(output_dir)
        os.makedirs(output_dir)

    # Create tiles ====================================================================================================
    # Run gdal2tiles.py as a subprocess, passing in the input and output paths
    err = None
    try:
        subprocess.check_output(
            ["gdal2tiles.py", "-z", "10-18", "-w", "none", "-r", "bilinear", tmp_file.name, output_dir]
        )
    except subprocess.CalledProcessError:
        err = "Something wrong with the file provided"

    # Remove folder if there was an error
    if err is not None:
        shutil.rmtree(output_dir)
    # Get a bounding box ==============================================================================================
    rs = GDALRaster(tmp_file.name)
    bbox = rs.extent
    srid = rs.srid
    # Return folder path
    return output_dir, bbox, srid, err
