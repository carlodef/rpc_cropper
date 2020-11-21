# RPC Cropper

A small standalone tool to crop satellite images and their RPC.

## Usage
Suppose you have two images `im1.tif` and `im2.tif`, and the associated RPC
coefficients in the files `rpc1.xml` and `rpc2.xml`. The call

    $ ./rpc_crop.py out im1.tif rpc1.xml im2.tif rpc2.xml 12300 4200 800 600

will write in the folder `out` the cropped files. The cropped region is defined
in the first image by the last four arguments. In the example above, `12300
4200` are the column and the row of the top-left corner of the region, and `800
600` are the width and the height of the region. The second image is cropped in
such a way that the region visible in the first crop is still visible in the
second crop. This is done using SRTM data.

To interactively select the region to crop, use the `rpc_crop_gui.py`
script. A preview of the reference image is needed:

    $ ./rpc_crop_gui.py outdir preview.jpg im1.tif rpc1.xml im2.tif rpc2.xml


## Installation
Nothing to do, the only needed binary will be compiled on the fly during the first
call to one of the python scripts.

## Known dependencies
* python 2.7 or 2.6
* numpy
* pyopengl
* gdal
* g++
* libtiff
* pillow

On Ubuntu 13.10, all the needed dependencies can be installed through the
package manager:

    $ sudo apt-get install python-opengl python-numpy gdal-bin libtiff4-dev g++

Note that the use of SRTM data requires an internet connection, at least the
first time you run this tool on a dataset.


## Authors
Gabriele Facciolo, Enric Meinhardt-Llopis, Carlo de Franchis
