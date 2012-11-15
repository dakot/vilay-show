# emacs: -*- mode: python; py-indent-offset: 4; indent-tabs-mode: nil -*-
# vi: set ft=python sts=4 ts=4 sw=4 et:
### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
#
#   See COPYING file distributed along with the testkraut package for the
#   copyright and license terms.
#
### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
"""Here come the docs....

"""

import argparse

__docformat__ = 'restructuredtext'

# magic line for manpage summary
# man: -*- % main command

parser_args = dict(formatter_class=argparse.RawDescriptionHelpFormatter)

def setup_parser(parser):
    # ADD ME
    #parser.add_argument('specs', nargs=2, metavar='SPEC',
    #        help="SPEC name/identifier")
    pass

def run(args):
    print args
