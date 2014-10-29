# coding: utf-8

from __future__ import division
from __future__ import print_function

import dit
import numpy as np

from nose.tools import *

module = dit.math.pmfops

def test_perturb_one():
    # Smoke test
    d = np.array([0, .5, .5])
    d2 = module.perturb(d, .00001)
    d3 = d2.round(2)
    np.testing.assert_allclose(d, d3)

def test_perturb_many():
    # Smoke test
    d = np.array([[0, .5, .5], [.5, .5, .0]])
    d2 = module.perturb(d, .00001)
    print(d2)
    d3 = d2.round(2)
    np.testing.assert_allclose(d, d3)

def test_convex_combination():
    d1 = np.array([0, .5, .5])
    d2 = np.array([.5, .5, 0])
    d3_= np.array([.25, .5, .25])
    d3 = module.convex_combination(np.array([d1, d2]))
    np.testing.assert_allclose(d3, d3_)

def test_convex_combination_weights():
    d1 = np.array([0, .5, .5])
    d2 = np.array([.5, .5, 0])
    weights = [1, 0]
    d3 = module.convex_combination(np.array([d1, d2]), weights)
    np.testing.assert_allclose(d3, d1)

def test_downsample_onepmf():
    # One pmf
    d1 = np.array([0, .51, .49])
    d2_ = np.array([0, .5, .5])
    d2 = module.downsample(d1, 2)
    np.testing.assert_allclose(d2, d2_)

def test_downsample_twopmf():
    # Two pmf
    d1 = np.array([[0, .51, .49], [.6, .3, .1]])
    d2_ = np.array([[0, .5, .5], [.5, .5, 0]])
    d2 = module.downsample(d1, 2)
    np.testing.assert_allclose(d2, d2_)

def test_downsample_badmethod():
    d1 = np.array([0, .51, .49])
    assert_raises(
        NotImplementedError, module.downsample, d1, 2**3, method='whatever'
    )

def test_projections1():
    d = np.array([ 0.03231933,  0.89992681,  0.06775385])
    d2_ = np.array([
        [ 0.03231933,  0.89992681,  0.06775385],
        [ 0.        ,  0.92998325,  0.07001675],
        [ 0.        ,  0.875     ,  0.125     ]
    ])
    d2 = module.projections(d, 2**3)
    np.testing.assert_allclose(d2, d2_)

def test_projections2():
    d = np.array([ 0.51,  0.48,  0.01])
    d2_ = np.array([
        [ 0.51      ,  0.48      ,  0.01      ],
        [ 0.5       ,  0.48979592,  0.01020408],
        [ 0.5       ,  0.5       ,  0.        ]
    ])
    d2 = module.projections(d, 2**3)
    np.testing.assert_allclose(d2, d2_, rtol=1e-7, atol=1e-8)

def test_projections_max():
    d = np.array([ 0.51,  0.48,  0.01])
    d2_ = np.array([
        [ 0.51      ,  0.48      ,  0.01      ],
        [ 0.625     ,  0.36734694,  0.00765306],
        [ 0.625     ,  0.25      ,  0.125     ]
    ])
    d2 = module.projections(d, 2**3, [np.argmax, np.argmax, np.argmax])
    np.testing.assert_allclose(d2, d2_, rtol=1e-7, atol=1e-8)

def test_projections_0element():
    # During projections, if an element is equal to 0, then searchsorted
    # returns 0, and `lower - 1` gives it index -1...which incorrectly
    # compares locs[-1] instead of locs[0]. So without the line:
    #    lower[lower == -1] = 0
    # we would have an error.
    d = np.array([ 0.23714859,  0.35086749,  0.01870522,
                   0.32914084,  0.05896644,  0.00517141])
    ops = [np.argmin, np.argmin, np.argmin, np.argmin, np.argmax]
    x = dit.math.pmfops.projections(d, 2**3, ops)
    # We would have had:
    x_bad = np.array([
        [ 0.23714859,  0.35086749,  0.01870522,  0.32914084,  0.05896644, 0.00517141],
        [ 0.25      ,  0.34495659,  0.0183901 ,  0.32359596,  0.05797306, 0.00508429],
        [ 0.25      ,  0.375     ,  0.01702605,  0.29959378,  0.05367301, 0.00470717],
        [ 0.25      ,  0.375     ,  0.        ,  0.31384313,  0.05622582, 0.00493105],
        [ 0.25      ,  0.375     ,  0.        ,  0.375     ,  0.        , 0.        ],
        [ 0.25      ,  0.375     ,  0.        ,  0.375     ,  1.        , np.nan]
    ])
    # Since the error has been fixed. We get:
    x_good = np.array([
        [ 0.23714859,  0.35086749,  0.01870522,  0.32914084,  0.05896644, 0.00517141],
        [ 0.25      ,  0.34495659,  0.0183901 ,  0.32359596,  0.05797306, 0.00508429],
        [ 0.25      ,  0.375     ,  0.01702605,  0.29959378,  0.05367301, 0.00470717],
        [ 0.25      ,  0.375     ,  0.        ,  0.31384313,  0.05622582, 0.00493105],
        [ 0.25      ,  0.375     ,  0.        ,  0.375     ,  0.        , 0.        ],
        [ 0.25      ,  0.375     ,  0.        ,  0.375     ,  0.        , 0.        ],
    ])
    np.testing.assert_allclose(x, x_good, rtol=1e-7, atol=1e-8)




def test_clamps():
    d = np.array([.51, .48, .01])
    out_ = (np.array([[4, 3, 0], [5, 4, 1]]),
            np.array([ 0., 0.125, 0.25, 0.375, 0.5, 0.625, 0.75, 0.875, 1.]))
    out = module.clamped_indexes(d, 2**3)
    np.testing.assert_allclose(out[0], out_[0])
    np.testing.assert_allclose(out[1], out_[1], rtol=1e-7, atol=1e-8)
