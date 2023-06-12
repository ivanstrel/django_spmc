import json
import os
import shutil
import subprocess
import uuid

from django.conf import settings
from django.contrib.gis.gdal import GDALRaster
from django.contrib.gis.geos import GEOSGeometry, Polygon
from django.core.exceptions import ValidationError
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
            # ["gdal2tiles.py", "-z", "10-18", "-w", "none", "-r", "bilinear", tmp_file.name, output_dir]
            ["gdal2tiles.py", "-z", "1", "-w", "none", "-r", "bilinear", tmp_file.name, output_dir]
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


def check_geojson(file_upload, bbox, im_file):
    # If it is a new object, it does not have bbox yet, therefore, try to estimate bbox from raster
    if bbox is None:
        try:
            tmp_file = NamedTemporaryFile()
            for chunk in im_file.chunks():
                tmp_file.write(chunk)

            rs = GDALRaster(tmp_file.name)
            bbox = rs.extent
            srid = rs.srid
            poly = Polygon.from_bbox(bbox)
            poly.srid = srid
            bbox = poly
        except Exception as e:
            raise ValidationError(f"Could not get bounding box from raster: {e}")
    # Process upload
    try:
        json_str = file_upload.read().decode("utf-8")
        geojson_data = json.loads(json_str)
        # Ensure the geometry type is "Polygon"
        for feature in geojson_data.get("features", []):
            if feature.get("geometry", {}).get("type") != "Polygon":
                raise ValidationError("GeoJSON file must contain only Polygon features.")
            # Ensure the file can be read as a GeoDjango object
            feature_str = feature.get("geometry")
            feature_str.update({"crs": geojson_data.get("crs")})
            tmp_geom = GEOSGeometry(json.dumps(feature_str))
            tmp_geom.transform(bbox.srid)
            # Check if each poly intersects with scene bbox
            if not tmp_geom.intersects(bbox):
                raise ValidationError("Some of provided polygons are outside the scene bounding box")
    except Exception as e:
        raise ValidationError(f"Error reading geojson file: {e}")
    return True


def check_raster(file_upload):
    """
    Read uploaded file to tmp location, then try to perform gdal2tiles with small zoom in order to check
    for problems with raster
    :param file_upload:
    :return:
    """
    # Process upload
    tmp_file = NamedTemporaryFile()
    for chunk in file_upload.chunks():
        tmp_file.write(chunk)
    # Define temporary output directory name folder based on the provided uuid
    output_dir = f"/tmp/{uuid.uuid4()}"
    # Check if output path exists, and create or recreate it
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    else:
        shutil.rmtree(output_dir)
        os.makedirs(output_dir)
    # Try to generate tiles
    try:
        GDALRaster(tmp_file.name)  # Just in case it could not be read
        subprocess.check_output(["gdal2tiles.py", "-z", "1", "-w", "none", tmp_file.name, output_dir])
        shutil.rmtree(output_dir)
    except subprocess.CalledProcessError:
        shutil.rmtree(output_dir)
        raise ValidationError(
            "Problem with raster. The raster should be of a Bytes type, check it. "
            + "Or simply convert the file into some RGB representation with gdal"
        )
