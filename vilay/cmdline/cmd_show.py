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

import logging
lgr = logging.getLogger(__name__)
import argparse
from vilay import cfg

__docformat__ = 'restructuredtext'

# magic line for manpage summary
# man: -*- % main command

parser_args = dict(formatter_class=argparse.RawDescriptionHelpFormatter)

def setup_parser(parser):
    # ADD ME
    parser.add_argument('mediafile', help="path of media file")
    media_group = parser.add_argument_group('media')
    media_group.add_argument('--movie-opacity', type=float_zero_one, help="float value of opacity of movie")
    media_group.add_argument('--movie-gray', type=float_zero_one, help="[0,1] if movie should be gray")
    
    snippet_group = parser.add_argument_group('snippets')
    snippet_group.add_argument('--play-snippet', nargs=2, action='append', type=float, help="plays snippet with 'start' 'duration' (in seconds)")
    
    gaze_group = parser.add_argument_group('gazes')
    gaze_group.add_argument('--gazes', nargs='+', help="filenames of gaze files")
    gaze_group.add_argument('--fov', '--stimulus-field-of-view', dest='stim_fov', nargs=4, type=int, 
        help="specifies where the movie was set in gaze data: 'width' 'height' 'x_offset' 'y_offset'",
        default=[float(i) for i in cfg.get('video', 'field of view', default='').split()])
    
    gaze_group.add_argument('--show-gazes-each', type=float_zero_one, help="float value of opacity of each gaze overlay")
    gaze_group.add_argument('--show-gazes-clustered', type=float_zero_one, help="float value of opacity of clustered gaze overlay", default=1)
    gaze_group.add_argument('--show-aperture', type=bool, help="set 'true' to show aperture")

    timeseries_group = parser.add_argument_group('timeseries')
    timeseries_group.add_argument('--ts','--timeseries', dest='timeseries', nargs='+', help="filenames of timeseries files, format: timestamp, value (float)...")
    
    annotation_group = parser.add_argument_group('annotation')
    annotation_group.add_argument('--ann','--annotation', dest='annotation', nargs='+', help="filenames of annotation files, format: timestamp, data (string)...")
    annotation_group.add_argument('--ann-idx','--annotation_timestamp_idx', dest='annotation_timestamp_idx', type=int, help="index of timestamp information in annotation files", default=0)
    
def float_zero_one(x):
    try:
        x = float(x)
    except ValueError:
        raise argparse.ArgumentTypeError("'%s' cannot be converted to float" % x)
    if x < 0 or x > 1:
        raise argparse.ArgumentTypeError("'%f' not in interval [0,1]" % x)
    return x
    
def run(args):
    #print args
    from vilay.stimulus import Stimulus
    from vilay.player import Player
    from vilay.gazes import Gazes
    from vilay.snippet import Snippet
    import sys
    
    stim=Stimulus(args.mediafile)
    
    player = Player(stim)
    
    if not args.movie_gray is None:
        player.set_movie_gray(args.movie_gray)
    if not args.movie_opacity is None:
        player.set_movie_opacity(args.movie_opacity)
        
    
    if not args.gazes is None:
        lgr.debug("gaze display enabled (reading from %s)" % args.gazes)
        player.gazes = Gazes(args.gazes)

        if len(args.stim_fov) == 4:
            lgr.debug("set video field of view to %s" % args.stim_fov)
            player.gazes.calibration(*args.stim_fov)
        else:
            print "WARNING: gazes maybe not calibrated"
        
        if not args.show_gazes_each is None:
            player.set_show_gaze_each(args.show_gazes_each)
        
        if not args.show_gazes_clustered is None:
            player.set_show_gaze_clustered(args.show_gazes_clustered)

        if not args.show_aperture is None:
            player.set_show_aperture(args.show_aperture)
    
    if not args.timeseries is None:
        for ts in args.timeseries:
            player.add_timeseries(ts)
    
    if not args.annotation is None:
        for an in args.annotation:
            player.add_annotation(an, 'annotation', args.annotation_timestamp_idx)
    
    if not args.play_snippet is None:
        lgr.debug("limit playback to snippets")
        for i,snippet in enumerate(args.play_snippet):
            player.snippets.append(Snippet(snippet[0], snippet[1], "cmd-no-%i" % i))
        player.load_snippet(1) 
        
    player.play()
    print ""
    sys.exit(player.app.exec_())
