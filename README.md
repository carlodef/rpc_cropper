# RPC Cropper

## Usage
Suppose you have two images `im1.tif` and `im2.tif`, and the associated RPC
coefficients in `xml` files `rpc1.xml` and `rpc2.xml`. The call

    $ ./rpc_cropper.py out im1.tif rpc1.xml im2.tif rpc2.xml 12300 4200 800 600

will write in the folder `out` the cropped files.

To interactively select the region to crop, use the `rpc_cropper_gui.py`
script. A preview of the reference image is needed:

    $ ./rpc_cropper_gui.py outdir preview.jpg im1.tif rpc1.xml im2.tif rpc2.xml


## Installation
Nothing to do, the only needed binary will be compiled on the fly on the first
call to one of the python scripts.

## Known dependencies
python, gdal, libtiff, ...


## Authors
Gabriele Facciolo
Enric Meinhardt-Llopis
Carlo de Franchis
