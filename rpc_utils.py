# Copyright (C) 2013, Carlo de Franchis <carlodef@gmail.com>
# Copyright (C) 2013, Gabriele Facciolo <gfacciol@gmail.com>
# Copyright (C) 2013, Enric Meinhardt-Llopis <ellopsis@gmail.com>

import numpy as np

import common


def find_corresponding_point(model_a, model_b, x, y, z):
    """
    Finds corresponding points in the second image, given the heights.

    Arguments:
        model_a, model_b: two instances of the rpc_model.RPCModel class, or of
            the projective_model.ProjModel class
        x, y, z: three 1D numpy arrrays, of the same length. x, y are the
        coordinates of pixels in the image, and z contains the altitudes of the
        corresponding 3D point.

    Returns:
        xp, yp, z: three 1D numpy arrrays, of the same length as the input. xp,
            yp contains the coordinates of the projection of the 3D point in image
            b.
    """
    t1, t2, t3 = model_a.direct_estimate(x, y, z)
    xp, yp, zp = model_b.inverse_estimate(t1, t2, z)
    return (xp, yp, z)


def geodesic_bounding_box(rpc, x, y, w, h):
    """
    Computes a bounding box on the WGS84 ellipsoid associated to a Pleiades
    image region of interest, through its rpc function.

    Args:
        rpc: instance of the rpc_model.RPCModel class
        x, y, w, h: four integers definig a rectangular region of interest
            (ROI) in the image. (x, y) is the top-left corner, and (w, h) are the
            dimensions of the rectangle.

    Returns:
        4 geodesic coordinates: the min and max longitudes, and the min and
        max latitudes.
    """
    # compute altitude coarse extrema from rpc data
    m = rpc.altOff - rpc.altScale
    M = rpc.altOff + rpc.altScale

    # build an array with vertices of the 3D ROI, obtained as {2D ROI} x [m, M]
    x = np.array([x, x,   x,   x, x+w, x+w, x+w, x+w])
    y = np.array([y, y, y+h, y+h,   y,   y, y+h, y+h])
    a = np.array([m, M,   m,   M,   m,   M,   m,   M])

    # compute geodetic coordinates of corresponding world points
    lon, lat, alt = rpc.direct_estimate(x, y, a)

    # extract extrema
    # TODO: handle the case where longitudes pass over -180 degrees
    # for latitudes it doesn't matter since for latitudes out of [-60, 60]
    # there is no SRTM data
    return np.min(lon), np.max(lon), np.min(lat), np.max(lat)


def sample_bounding_box(lon_m, lon_M, lat_m, lat_M):
    """
    Samples a geodetic "rectangular" region with regularly spaced points.
    The sampling distance is the srtm resolution, ie 3 arcseconds.

    Args:
        lon_m, lon_M: min and max longitudes, between -180 and 180
        lat_m, lat_M: min and max latitudes, between -60 and 60

    Returns:
        a numpy array, of size N x 2, containing the list of sample locations
        in geodetic coordinates.
    """
    # check parameters
    assert lon_m > -180
    assert lon_M < 180
    assert lon_m < lon_M
    assert lat_m > -60
    assert lat_M < 60
    assert lat_m < lat_M

    # width of srtm bin: 6000x6000 samples in a tile of 5x5 degrees, ie 3
    # arcseconds (in degrees)
    srtm_bin = 1.0/1200

    # round down lon_m, lat_m and round up lon_M, lat_M so they are integer
    # multiples of 3 arcseconds
    lon_m, lon_M = round_updown(lon_m, lon_M, srtm_bin)
    lat_m, lat_M = round_updown(lat_m, lat_M, srtm_bin)

    # compute the samples: one in the center of each srtm bin
    lons = np.arange(lon_m, lon_M, srtm_bin) + .5 * srtm_bin
    lats = np.arange(lat_m, lat_M, srtm_bin) + .5 * srtm_bin

    # put all the samples in an array. There should be a more pythonic way to
    # do this
    out = np.zeros((len(lons)*len(lats), 2))
    for i in xrange(len(lons)):
        for j in xrange(len(lats)):
            out[i*len(lats)+j, 0] = lons[i]
            out[i*len(lats)+j, 1] = lats[j]

    return out


def round_updown(a, b, q):
    """
    Rounds down (resp. up) a (resp. b) to the closest multiple of q.

    Args:
        a: float value to round down
        b: float value to round up
        q: float value defining the targeted multiples

    Returns:
        the two modified values
    """
    a = q*np.floor(a/q)
    b = q*np.ceil(b/q)
    return a, b


def altitude_range_coarse(rpc):
    """
    Computes a coarse altitude range using the RPC informations only.

    Args:
        rpc: instance of the rpc_model.RPCModel class

    Returns:
        the altitude validity range of the RPC.
    """
    m = rpc.altOff - rpc.altScale
    M = rpc.altOff + rpc.altScale
    return m, M


def altitude_range(rpc, x, y, w, h, margin_top, margin_bottom):
    """
    Computes an altitude range using SRTM data.

    Args:
        rpc: instance of the rpc_model.RPCModel class
        x, y, w, h: four integers definig a rectangular region of interest
            (ROI) in the image. (x, y) is the top-left corner, and (w, h) are the
            dimensions of the rectangle.
        margin_top: margin (in meters) to add to the upper bound of the range
        margin_bottom: margin (usually negative) to add to the lower bound of
            the range

    Returns:
        lower and upper bounds on the altitude of the world points that are
        imaged by the RPC projection function in the provided ROI. To compute
        these bounds, we use SRTM data. The altitudes are computed with respect
        to the WGS84 reference ellipsoid.
    """
    # TODO: iterate the procedure used here to get a finer estimation of the
    # TODO: bounding box on the ellipsoid and thus of the altitude range. For flat
    # TODO: regions it will not improve much, but for mountainous regions there is a
    # TODO: lot to improve.

    # find bounding box on the ellipsoid (in geodesic coordinates)
    lon_m, lon_M, lat_m, lat_M = geodesic_bounding_box(rpc, x, y, w, h)

    # if bounding box is out of srtm domain, return coarse altitude estimation
    if (lat_m < -60 or lat_M > 60):
        print "Out of SRTM domain, returning coarse range from rpc"
        return altitude_range_coarse(rpc)

    # sample the bounding box with regular step of 3 arcseconds (srtm
    # resolution)
    ellipsoid_points = sample_bounding_box(lon_m, lon_M, lat_m, lat_M)

    # compute srtm height on all these points
    # these altitudes are computed with respect to the WGS84 ellipsoid
    import os
    srtm = common.run_binary_on_list_of_points(ellipsoid_points, 'srtm4',
          option=None, binary_workdir=os.path.dirname(__file__))
    srtm = np.ravel(srtm)

    # srtm data may contain 'nan' values (meaning no data is available there).
    # These points are most likely water (sea) and thus their height with
    # respect to geoid is 0. Thus we replace the nans with 0.
    srtm[np.isnan(srtm)] = 0

    # extract extrema (and add a +-100m security margin)
    h_m = np.round(srtm.min()) + margin_bottom
    h_M = np.round(srtm.max()) + margin_top

    return h_m, h_M


def corresponding_roi(rpc1, rpc2, x, y, w, h):
    """
    Uses RPC functions to determine the region of im2 associated to the
    specified ROI of im1.

    Args:
        rpc1, rpc2: two instances of the rpc_model.RPCModel class
        x, y, w, h: four integers defining a rectangular region of interest
            (ROI) in the first view. (x, y) is the top-left corner, and (w, h)
            are the dimensions of the rectangle.

    Returns:
        four integers defining a ROI in the second view. This ROI is supposed
        to contain the projections of the 3D points that are visible in the
        input ROI.
    """
    m, M = altitude_range(rpc1, x, y, w, h, 0, 0)

    # build an array with vertices of the 3D ROI, obtained as {2D ROI} x [m, M]
    a = np.array([x, x,   x,   x, x+w, x+w, x+w, x+w])
    b = np.array([y, y, y+h, y+h,   y,   y, y+h, y+h])
    c = np.array([m, M,   m,   M,   m,   M,   m,   M])

    # corresponding points in im2
    xx, yy = find_corresponding_point(rpc1, rpc2, a, b, c)[0:2]

    # return coordinates of the bounding box in im2
    return common.bounding_box2D(np.vstack([xx, yy]).T)
