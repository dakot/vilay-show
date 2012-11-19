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
    parser.add_argument('mediafile', help="SPEC name/identifier")
    parser.add_argument('--gazes', action='append', help="SPEC name/identifier")
    parser.add_argument('--show_gazes_each', type=float, choices=[0,1], help="float value of opacity of each gaze overlay")
    parser.add_argument('--show_gazes_clustered', type=float, choices=[0,1], help="float value of opacity of clustered gaze overlay")

def run(args):
    print args
    from vilay.stimulus import Stimulus
    from vilay.player import Player
    from vilay.gazes import Gazes
    import sys
    
    stim=Stimulus(args.mediafile)
    
    player = Player(stim)
    player.gazes = Gazes(args.gazes)
    
    """if args.show_gazes_each is not None:
        player.set_show_gaze_each(args.show_gazes_each)
    
    if args.show_gazes_clustered is not None:
        player.set_show_gaze_clustered(args.show_gazes_clustered)
    """
    sys.exit(player.app.exec_())
