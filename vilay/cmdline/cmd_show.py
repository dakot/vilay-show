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
    
    parser.add_argument('--play-snippet', nargs=2, action='append', type=float, help="start, duration")
    
    gaze_group = parser.add_argument_group('gazes')
    gaze_group.add_argument('--gazes', nargs='+', help="SPEC name/identifier")
    gaze_group.add_argument('--fov', '--stimulus-field-of-view', dest='stim_fov', nargs=4, type=int,
        help="""width, height, x_offset, y_offset""")
    
    gaze_group.add_argument('--show-gazes-each', type=float_zero_one, help="float value of opacity of each gaze overlay")
    gaze_group.add_argument('--show-gazes-clustered', type=float_zero_one, help="float value of opacity of clustered gaze overlay")

def float_zero_one(x):
    try:
        x = float(x)
    except ValueError:
        raise argparse.ArgumentTypeError("'%s' cannot be converted to float" % x)
    if x < 0 or x > 1:
        raise argparse.ArgumentTypeError("'%f' not in interval [0,1]" % x)
    return x
    
def run(args):
    print args
    from vilay.stimulus import Stimulus
    from vilay.player import Player
    from vilay.gazes import Gazes
    from vilay.snippet import Snippet
    import sys
    
    stim=Stimulus(args.mediafile)
    
    player = Player(stim)
    
    if not args.gazes is None:
        player.gazes = Gazes(args.gazes)
    
        if not args.stim_fov is None:
            player.gazes.calibration(*args.stim_fov)
        
        if not args.show_gazes_each is None:
            player.set_show_gaze_each(args.show_gazes_each)
        
        if not args.show_gazes_clustered is None:
            player.set_show_gaze_clustered(args.show_gazes_clustered)
    
    if not args.play_snippet is None:
        for i,snippet in enumerate(args.play_snippet):
            player.snippets.append(Snippet(snippet[0], snippet[1], "cmd-no-%i" % i))
        player.load_snippet(1) 
        
    player.play()
    
    sys.exit(player.app.exec_())
