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
    if "build_py" in sys.argv:
        from subprocess import call
        for uifile in glob(opj('vilay', 'qt_ui', '*.ui')):
            uipyfile = '%s%s' % (uifile[:-2], 'py')
            command = ["pyuic4", "-o", uipyfile, uifile]
            try:
                exitcode = call(command)
                print command, exitcode
            except OSError, err:
                exitcode = 1
            if exitcode:
                if os.path.exists(uipyfile):
                    print >> sys.stderr, \
                        """Warning: unable to recompile '%s' to '%s' using
                        pyuic4 (using existing file).""" % (uifile, uipyfile)
                else:
                    print >> sys.stderr, \
                        """ERROR: unable to compile '%s' to '%s' using
                        pyuic4. pyuic4 is included in the PyQt4 development
                        package.""" % (uifile, uipyfile)
                    sys.exit(1)
        for rcfile in glob(opj('vilay', 'qt_ui', '*.qrc')):
            rcpyfile = '%s%s' % (rcfile[:-4], '_rc.py')
            command = ["pyrcc4", "-o", rcpyfile, rcfile]
            try:
                exitcode = call(command)
                print command, exitcode
            except OSError, err:
                exitcode = 1
            if exitcode:
                if os.path.exists(rcpyfile):
                    print >> sys.stderr, \
                        """Warning: unable to recompile '%s' to '%s' using
                        pyrcc4 (using existing file).""" % (rcfile, rcpyfile)
                else:
                    print >> sys.stderr, \
                        """ERROR: unable to compile '%s' to '%s' using
                        pyrcc4. pyrcc4 is included in the PyQt4 development
                        package.""" % (rcfile, rcpyfile)
                    sys.exit(1)

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
