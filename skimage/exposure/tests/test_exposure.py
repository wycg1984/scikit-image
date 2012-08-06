import numpy as np
from numpy.testing import assert_array_almost_equal as assert_close

import skimage
from skimage import data
from skimage import exposure
from skimage.color import rgb2gray


# Test histogram equalization
# ===========================

# squeeze image intensities to lower image contrast
test_img = exposure.rescale_intensity(data.camera() / 5. + 100)


def test_equalize_ubyte():
    img = skimage.img_as_ubyte(test_img)
    img_eq = exposure.equalize(img)

    cdf, bin_edges = exposure.cumulative_distribution(img_eq)
    check_cdf_slope(cdf)


def test_equalize_float():
    img = skimage.img_as_float(test_img)
    img_eq = exposure.equalize(img)

    cdf, bin_edges = exposure.cumulative_distribution(img_eq)
    check_cdf_slope(cdf)


def check_cdf_slope(cdf):
    """Slope of cdf which should equal 1 for an equalized histogram."""
    norm_intensity = np.linspace(0, 1, len(cdf))
    slope, intercept = np.polyfit(norm_intensity, cdf, 1)
    assert 0.9 < slope < 1.1


# Test rescale intensity
# ======================

def test_rescale_stretch():
    image = np.array([51, 102, 153], dtype=np.uint8)
    out = exposure.rescale_intensity(image)
    assert out.dtype == np.uint8
    assert_close(out, [0, 127, 255])


def test_rescale_shrink():
    image = np.array([51., 102., 153.])
    out = exposure.rescale_intensity(image)
    assert_close(out, [0, 0.5, 1])


def test_rescale_in_range():
    image = np.array([51., 102., 153.])
    out = exposure.rescale_intensity(image, in_range=(0, 255))
    assert_close(out, [0.2, 0.4, 0.6])


def test_rescale_in_range_clip():
    image = np.array([51., 102., 153.])
    out = exposure.rescale_intensity(image, in_range=(0, 102))
    assert_close(out, [0.5, 1, 1])


def test_rescale_out_range():
    image = np.array([-10, 0, 10], dtype=np.int8)
    out = exposure.rescale_intensity(image, out_range=(0, 127))
    assert out.dtype == np.int8
    assert_close(out, [0, 63, 127])


# Test rescale intensity
# ======================

def test_adapthist_ubyte():
    '''Test a scalar uint8 image
    '''
    img = skimage.img_as_ubyte(data.moon())
    adapted = exposure.adapthist(img, clip_limit=0.02)
    assert adapted.min() == 0
    assert adapted.max() == 255
    assert img.shape == adapted.shape
    assert peak_snr(img, adapted) > 22
    assert norm_brightness_err(img, adapted) < 0.05
    return img, adapted


def test_adapthist_float():
    '''Test an RGB float image
    '''
    img = skimage.img_as_float(data.lena())
    adapted = exposure.adapthist(img, nx=10, ny=9, clip_limit=0.01,
                        nbins=128, out_range='original')
    assert_almost_equal(adapted.min() , img.min())
    assert_almost_equal(adapted.min(), img.min())
    assert img.shape == adapted.shape
    assert peak_snr(img, adapted) > 136
    assert norm_brightness_err(img, adapted) < 0.02
    return data, adapted


def peak_snr(img1, img2):
    '''Peak signal to noise ratio of two images

    Parameters
    ----------
    img1 : array-like
    img2 : array-like

    Returns
    -------
    peak_snr : float
        Peak signal to noise ratio
    '''
    if img1.ndim == 3:
        img1, img2 = rgb2gray(img1.copy()), rgb2gray(img2.copy())
    mse = 1. / img1.size * np.square(img1 - img2).sum()
    _, max_ = dtype_range[img1.dtype.type]
    return 20 * np.log(max_ / mse)


def norm_brightness_err(img1, img2):
    '''Normalized Absolute Mean Brightness Error between two images

    Parameters
    ----------
    img1 : array-like
    img2 : array-like

    Returns
    -------
    norm_brightness_error : float
        Normalize absolute mean brightness error
    '''
    if img1.ndim == 3:
        img1, img2 = rgb2gray(img1), rgb2gray(img2)
    ambe = np.abs(img1.mean() - img2.mean())
    nbe = ambe / dtype_range[img1.dtype.type][1]
    return nbe


if __name__ == '__main__':
    from numpy import testing
    testing.run_module_suite()
