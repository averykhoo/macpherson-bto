# https://github.com/sumtype/CIEDE2000/blob/master/ciede2000.py
import math

import numpy as np


# Converts RGB pixel array to XYZ format.
# Implementation derived from http://www.easyrgb.com/en/math.php
def rgb2xyz(rgb):
    def format(c):
        c = c / 255.
        if c > 0.04045:
            c = ((c + 0.055) / 1.055) ** 2.4
        else:
            c = c / 12.92
        return c * 100

    rgb = list(map(format, rgb))
    xyz = [None, None, None]
    xyz[0] = rgb[0] * 0.4124 + rgb[1] * 0.3576 + rgb[2] * 0.1805
    xyz[1] = rgb[0] * 0.2126 + rgb[1] * 0.7152 + rgb[2] * 0.0722
    xyz[2] = rgb[0] * 0.0193 + rgb[1] * 0.1192 + rgb[2] * 0.9505
    return xyz


# Converts XYZ pixel array to LAB format.
# Implementation derived from http://www.easyrgb.com/en/math.php
def xyz2lab(xyz):
    def format(c):
        if c > 0.008856:
            c = c ** (1. / 3.)
        else:
            c = (7.787 * c) + (16. / 116.)
        return c

    xyz[0] = xyz[0] / 95.047
    xyz[1] = xyz[1] / 100.00
    xyz[2] = xyz[2] / 108.883
    xyz = list(map(format, xyz))
    lab = [None, None, None]
    lab[0] = (116. * xyz[1]) - 16.
    lab[1] = 300. * (xyz[0] - xyz[1])
    lab[2] = 200. * (xyz[1] - xyz[2])
    return lab


# Converts RGB pixel array into LAB format.
def rgb2lab(rgb):
    return xyz2lab(rgb2xyz(rgb))


# Returns CIEDE2000 comparison results of two LAB formatted colors.
# Implementation derived from the excel spreadsheet provided here: http://www2.ece.rochester.edu/~gsharma/ciede2000/
def ciede2000(lab1, lab2):
    L1 = lab1[0]
    A1 = lab1[1]
    B1 = lab1[2]
    L2 = lab2[0]
    A2 = lab2[1]
    B2 = lab2[2]
    C1 = np.sqrt((A1 ** 2.) + (B1 ** 2.))
    C2 = np.sqrt((A2 ** 2.) + (B2 ** 2.))
    aC1C2 = np.average([C1, C2])
    G = 0.5 * (1. - np.sqrt((aC1C2 ** 7.) / ((aC1C2 ** 7.) + (25. ** 7.))))
    a1P = (1. + G) * A1
    a2P = (1. + G) * A2
    c1P = np.sqrt((a1P ** 2.) + (B1 ** 2.))
    c2P = np.sqrt((a2P ** 2.) + (B2 ** 2.))
    if a1P == 0 and B1 == 0:
        h1P = 0
    else:
        if B1 >= 0:
            h1P = np.degrees(np.arctan2(B1, a1P))
        else:
            h1P = np.degrees(np.arctan2(B1, a1P)) + 360.
    if a2P == 0 and B2 == 0:
        h2P = 0
    else:
        if B2 >= 0:
            h2P = np.degrees(np.arctan2(B2, a2P))
        else:
            h2P = np.degrees(np.arctan2(B2, a2P)) + 360.
    dLP = L2 - L1
    dCP = c2P - c1P
    if h2P - h1P > 180:
        dhC = 1
    elif h2P - h1P < -180:
        dhC = 2
    else:
        dhC = 0
    if dhC == 0:
        dhP = h2P - h1P
    elif dhC == 1:
        dhP = h2P - h1P - 360.
    else:
        dhP = h2P + 360 - h1P
    dHP = 2. * np.sqrt(c1P * c2P) * np.sin(np.radians(dhP / 2.))
    aL = np.average([L1, L2])
    aCP = np.average([c1P, c2P])
    if c1P * c2P == 0:
        haC = 3
    elif np.absolute(h2P - h1P) <= 180:
        haC = 0
    elif h2P + h1P < 360:
        haC = 1
    else:
        haC = 2
    haP = np.average([h1P, h2P])
    if haC == 3:
        aHP = h1P + h2P
    elif haC == 0:
        aHP = haP
    elif haC == 1:
        aHP = haP + 180
    else:
        aHP = haP - 180
    lPa50 = (aL - 50) ** 2.
    sL = 1. + (0.015 * lPa50 / np.sqrt(20. + lPa50))
    sC = 1. + 0.045 * aCP
    T = 1. - 0.17 * np.cos(np.radians(aHP - 30.)) + 0.24 * np.cos(np.radians(2. * aHP)) + 0.32 * np.cos(
        np.radians(3. * aHP + 6.)) - 0.2 * np.cos(np.radians(4. * aHP - 63.))
    sH = 1. + 0.015 * aCP * T
    dTheta = 30. * np.exp(-1. * ((aHP - 275.) / 25.) ** 2.)
    rC = 2. * np.sqrt((aCP ** 7.) / ((aCP ** 7.) + (25. ** 7.)))
    rC = 2. * np.sqrt(aCP ** 7. / (aCP ** 7. + 25. ** 7.))
    rT = -np.sin(np.radians(2. * dTheta)) * rC
    fL = dLP / sL / 1.
    fC = dCP / sC / 1.
    fH = dHP / sH / 1.
    dE2000 = np.sqrt(fL ** 2. + fC ** 2. + fH ** 2. + rT * fC * fH)
    return dE2000


test_data = [
    [50.0000, 2.6772, -79.7751, 50.0000, 0.0000, -82.7485, 2.0425],
    [50.0000, 3.1571, -77.2803, 50.0000, 0.0000, -82.7485, 2.8615],
    [50.0000, 2.8361, -74.0200, 50.0000, 0.0000, -82.7485, 3.4412],
    [50.0000, -1.3802, -84.2814, 50.0000, 0.0000, -82.7485, 1.0000],
    [50.0000, -1.1848, -84.8006, 50.0000, 0.0000, -82.7485, 1.0000],
    [50.0000, -0.9009, -85.5211, 50.0000, 0.0000, -82.7485, 1.0000],
    [50.0000, 0.0000, 0.0000, 50.0000, -1.0000, 2.0000, 2.3669],
    [50.0000, -1.0000, 2.0000, 50.0000, 0.0000, 0.0000, 2.3669],
    [50.0000, 2.4900, -0.0010, 50.0000, -2.4900, 0.0009, 7.1792],
    [50.0000, 2.4900, -0.0010, 50.0000, -2.4900, 0.0010, 7.1792],
    [50.0000, 2.4900, -0.0010, 50.0000, -2.4900, 0.0011, 7.2195],
    [50.0000, 2.4900, -0.0010, 50.0000, -2.4900, 0.0012, 7.2195],
    [50.0000, -0.0010, 2.4900, 50.0000, 0.0009, -2.4900, 4.8045],
    [50.0000, -0.0010, 2.4900, 50.0000, 0.0010, -2.4900, 4.8045],
    [50.0000, -0.0010, 2.4900, 50.0000, 0.0011, -2.4900, 4.7461],
    [50.0000, 2.5000, 0.0000, 50.0000, 0.0000, -2.5000, 4.3065],
    [50.0000, 2.5000, 0.0000, 73.0000, 25.0000, -18.0000, 27.1492],
    [50.0000, 2.5000, 0.0000, 61.0000, -5.0000, 29.0000, 22.8977],
    [50.0000, 2.5000, 0.0000, 56.0000, -27.0000, -3.0000, 31.9030],
    [50.0000, 2.5000, 0.0000, 58.0000, 24.0000, 15.0000, 19.4535],
    [50.0000, 2.5000, 0.0000, 50.0000, 3.1736, 0.5854, 1.0000],
    [50.0000, 2.5000, 0.0000, 50.0000, 3.2972, 0.0000, 1.0000],
    [50.0000, 2.5000, 0.0000, 50.0000, 1.8634, 0.5757, 1.0000],
    [50.0000, 2.5000, 0.0000, 50.0000, 3.2592, 0.3350, 1.0000],
    [60.2574, -34.0099, 36.2677, 60.4626, -34.1751, 39.4387, 1.2644],
    [63.0109, -31.0961, -5.8663, 62.8187, -29.7946, -4.0864, 1.2630],
    [61.2901, 3.7196, -5.3901, 61.4292, 2.2480, -4.9620, 1.8731],
    [35.0831, -44.1164, 3.7933, 35.0232, -40.0716, 1.5901, 1.8645],
    [22.7233, 20.0904, -46.6940, 23.0331, 14.9730, -42.5619, 2.0373],
    [36.4612, 47.8580, 18.3852, 36.2715, 50.5065, 21.2231, 1.4146],
    [90.8027, -2.0831, 1.4410, 91.1528, -1.6435, 0.0447, 1.4441],
    [90.9257, -0.5406, -0.9208, 88.6381, -0.8985, -0.7239, 1.5381],
    [6.7747, -0.2908, -2.4247, 5.8714, -0.0985, -2.2286, 0.6377],
    [2.0776, 0.0795, -1.1350, 0.9033, -0.0636, -0.5514, 0.9082],
]


def euclidean(x, y):
    a, b, c = x
    d, e, f = y
    return ((a - d) ** 2 + (b - e) ** 2 + (c - f) ** 2) ** 0.5


def linear_srgb_to_srgb(x):
    if x >= 0.0031308:
        return (1.055) * x ** (1.0 / 2.4) - 0.055
    else:
        return 12.92 * x


def srgb_to_linear_srgb(x):
    if x >= 0.04045:
        return ((x + 0.055) / (1 + 0.055)) ** 2.4
    else:
        return x / 12.92


def srgb_to_oklab(r, g, b):
    r = srgb_to_linear_srgb(r / 255)
    g = srgb_to_linear_srgb(g / 255)
    b = srgb_to_linear_srgb(b / 255)

    l = 0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b
    m = 0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b
    s = 0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b

    l_ = math.pow(l, 1 / 3)
    m_ = math.pow(m, 1 / 3)
    s_ = math.pow(s, 1 / 3)

    return (0.2104542553 * l_ + 0.7936177850 * m_ - 0.0040720468 * s_,
            1.9779984951 * l_ - 2.4285922050 * m_ + 0.4505937099 * s_,
            0.0259040371 * l_ + 0.7827717662 * m_ - 0.8086757660 * s_,
            )


def oklab_to_linear_srgb(L, a, b):
    l_ = L + 0.3963377774 * a + 0.2158037573 * b
    m_ = L - 0.1055613458 * a - 0.0638541728 * b
    s_ = L - 0.0894841775 * a - 1.2914855480 * b

    l = l_ * l_ * l_
    m = m_ * m_ * m_
    s = s_ * s_ * s_

    r = +4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s
    g = -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s
    b = -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s

    r = linear_srgb_to_srgb(r) * 255
    g = linear_srgb_to_srgb(g) * 255
    b = linear_srgb_to_srgb(b) * 255

    return r, g, b


def ok_distance(rgb_1, rgb_2):
    l1, a1, b1 = srgb_to_oklab(*rgb_1)
    l2, a2, b2 = srgb_to_oklab(*rgb_2)
    # return 400 * ((1 - (1 - (l1 - l2) ** 2) ** 0.5) + (a1 - a2) ** 2 + (b1 - b2) ** 2) ** 0.5
    return 200 * (((l1 - l2)/2) ** 2 + (a1 - a2) ** 2 + (b1 - b2) ** 2) ** 0.5


if __name__ == '__main__':
    white = (255, 255, 255)
    black = (0, 0, 0)
    red = (255, 0, 0)
    green = (0, 255, 0)
    blue = (0, 0, 255)
    aqua = (0, 255, 255)
    teal = (0, 128, 128)

    white_lab = rgb2lab(white)
    black_lab = rgb2lab(black)
    red_lab = rgb2lab(red)
    green_lab = rgb2lab(green)
    blue_lab = rgb2lab(blue)
    aqua_lab = rgb2lab(aqua)
    teal_lab = rgb2lab(teal)

    print('white_lab', white_lab)
    print('black_lab', black_lab)
    print('red_lab', red_lab)
    print('green_lab', green_lab)
    print('blue_lab', blue_lab)
    print('aqua_lab', aqua_lab)
    print('teal_lab', teal_lab)

    print('white_ok', srgb_to_oklab(*white))
    print('black_ok', srgb_to_oklab(*black))
    print('red_ok', srgb_to_oklab(*red))
    print('green_ok', srgb_to_oklab(*green))
    print('blue_ok', srgb_to_oklab(*blue))
    print('aqua_ok', srgb_to_oklab(*aqua))
    print('teal_ok', srgb_to_oklab(*teal))

    print('lab white, black', ciede2000(white_lab, black_lab), euclidean(white_lab, black_lab)/2)
    print('lab blue, red', ciede2000(blue_lab, red_lab), euclidean(blue_lab, red_lab)/2)
    print('lab red, green', ciede2000(red_lab, green_lab), euclidean(red_lab, green_lab)/2)
    print('lab blue, green', ciede2000(blue_lab, green_lab), euclidean(blue_lab, green_lab)/2)

    print('lab blue, aqua', ciede2000(blue_lab, aqua_lab), euclidean(blue_lab, aqua_lab)/2)
    print('lab blue, teal', ciede2000(blue_lab, teal_lab), euclidean(blue_lab, teal_lab)/2)
    print('lab teal, aqua', ciede2000(teal_lab, aqua_lab), euclidean(teal_lab, aqua_lab)/2)

    print('ok white, black', euclidean(white, black)/3.6, ok_distance(white, black))
    print('ok blue, red', euclidean(blue, red)/3.6, ok_distance(blue, red))
    print('ok red, green', euclidean(red, green)/3.6, ok_distance(red, green))
    print('ok blue, green', euclidean(blue, green)/3.6, ok_distance(blue, green))

    print('ok blue, aqua', euclidean(blue, aqua)/3.6, ok_distance(blue, aqua))
    print('ok blue, teal', euclidean(blue, teal)/3.6, ok_distance(blue, teal))
    print('ok teal, aqua', euclidean(teal, aqua)/3.6, ok_distance(teal, aqua))
