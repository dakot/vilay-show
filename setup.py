# emacs: -*- mode: python; py-indent-offset: 4; indent-tabs-mode: nil -*-
# vi: set ft=python sts=4 ts=4 sw=4 et:
### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
#
#   See COPYING file distributed along with the vilay package for the
#   copyright and license terms.
#
### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
""""""

import os
import sys
from os.path import join as opj
import vilay
from distutils.core import setup
from glob import glob


__docformat__ = 'restructuredtext'

extra_setuptools_args = {}
if 'setuptools' in sys.modules:
    extra_setuptools_args = dict(
        tests_require=['nose'],
        test_suite='nose.collector',
        zip_safe=False
    )

def main(**extra_args):
    setup(name         = 'vilay',
          version      = vilay.__version__,
          author       = 'Daniel Kottke and the vilay developers',
          author_email = 'daniel@kottke.eu',
          license      = 'GPL',
          url          = 'https://github.com/dakot/vilay',
          download_url = 'https://github.com/dakot/vilay/tags',
          description  = '',
          long_description = open('README.rst').read(),
          classifiers  = ["Development Status :: 3 - Alpha",
                          "Environment :: GUI",
                          "Intended Audience :: Science/Research",
                          "License :: OSI Approved :: GPL",
                          "Operating System :: OS Independent",
                          "Programming Language :: Python",
                          "Topic :: Scientific/Engineering"],
          platforms    = "OS Independent",
          provides     = ['vilay'],
          # please maintain alphanumeric order
          packages     = [ 'vilay',
                           'vilay.qt_ui',
                           'vilay.cmdline',
                           ],
          package_data = {
              'vilay': ['icons/*', 'vilay.cfg']
            },
          scripts      = glob(os.path.join('bin', '*'))
          )

if __name__ == "__main__":
    main(**extra_setuptools_args)
