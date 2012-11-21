vilay
=====

How to use
----------

 >>> from vilay.stimulus import Stimulus
 >>> from vilay.player import Player

 >>> stim=Stimulus('mymovie.mp4')
 >>> player = Player(stim)

 >>> player.set_movie_opacity(.8)
 >>> player.set_show_gaze_each(.3)
 >>> player.set_show_gaze_clustered(1)

 >>> player.play()



Requirements
------------

* OpenCV (incl. Python-bindings)
* PyQt
