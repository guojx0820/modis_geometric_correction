'''
For:Combine MODIS three channel data to generate true color image and save the image.

Time:10/19/2021
Author:Guo Jiaxiang
Email：guojiaxiang0820@gmail.com
GitHubBlog:https://github.com/guojx0820
'''

from osgeo import gdal
import numpy as np
import matplotlib.pyplot as plt

# Set a function which read image file
def read_img(filename):
    # Opening dateset file.
    dataset = gdal.Open(filename)
    # Number of columns in grid matrix.
    width = dataset.RasterXSize
    # Number of rows of grid matrix.
    height = dataset.RasterYSize
    # Set a affine matrix.
    geo_trans = dataset.GetGeoTransform()
    # Set the projection information.
    proj = dataset.GetProjection()
    # Writing the data into an array corresponding to the grid matrix.
    data = dataset.ReadAsArray(0, 0, width, height).astype(np.float)
    # print(proj, geo_trans, data)
    # Close object:dataset
    del dataset
    # Return multi-values.
    return proj, geo_trans, data, height, width


# Set a function which write image file
def write_img(filename, proj, geotrans, data):
    # Determine the data type of raster data:int8,int16,uint16,float32.
    if 'int8' in data.dtype.name:
        datatype = gdal.GDT_Byte
    elif 'int16' in data.dtype.name:
        datatype = gdal.GDT_UInt16
    else:
        datatype = gdal.GDT_Float32

    # Detect the array dimension.
    if len(data.shape) == 3:
        # Order of data：im_bands, im_height, im_width.
        bands, height, width = data.shape
    else:
        im_bands, (height, width) = 1, data.shape

    # Calling GetDriverByName() function of GDAL lib.
    driver = gdal.GetDriverByName("GTiff")
    dataset = driver.Create(filename, width, height, bands, datatype)
    # Write affine transformation parameters.
    dataset.SetGeoTransform(geotrans)
    # Write projection
    dataset.SetProjection(proj)

    if bands == 1:
        # Write array data
        dataset.GetRasterBand(1).WriteArray(data)
    else:
        for i in range(bands):
            dataset.GetRasterBand(i + 1).WriteArray(data[i])
    # Close object:dataset
    del dataset
    return filename

# Set a function which stretch the image by linear.
def two_perc_linear(gray, maxout, minout):
    # Get the corresponding gray level at 95% histogram.
    high_value = np.percentile(gray, 95)
    low_value = np.percentile(gray, 5)
    truncated_gray = np.clip(gray, a_min=low_value, a_max=high_value)
    # Linear stretching.
    processed_gray = ((truncated_gray - low_value) / (high_value - low_value)) * (maxout - minout)
    return processed_gray

# Set a function which save the image file.
def save_RGB_img(ds_2bands, ds_5bands):
    max_out = 255
    min_out = 0
    # Take out bands 1, 4, 3 and 3 in MODIS data,
    # corresponding to RGB three bands respectively.
    R = ds_2bands[0]
    G = ds_5bands[1]
    B = ds_5bands[0]
    r = two_perc_linear(R, max_out, min_out)
    g = two_perc_linear(G, max_out, min_out)
    b = two_perc_linear(B, max_out, min_out)
    # Stored in the same array.
    data = np.array((r, g, b), dtype=r.dtype)
    # Write as 3-band true color data：Red，Green，Blue.
    write_img(output_file, proj, geotrans, data)


if __name__ == '__main__':
    # Set the path of the input and output files with the *.tiff postfix.
    # Set the output file name of ture color image.
    file_path2b = '/Users/leo/Desktop/Data/Results/20190817-b12_geo.tiff'
    file_path5b = '/Users/leo/Desktop/Data/Results/20190817-b34567_geo.tiff'
    output_file = '/Users/leo/Desktop/Data/Results/RGB_color5.tiff'
    # Calling the read_img() to read the 2 datasets.
    proj, geotrans, values2b, row, col = read_img(file_path2b)
    proj, geotrans, values5b, row, col = read_img(file_path5b)
    # Calling the save_RGB_img() function to save the ture color image.
    img = save_RGB_img(values2b, values5b)
    print(values2b[0], values5b[1], values5b[0])
