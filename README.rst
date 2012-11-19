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



PyQt usability
-----------------
To compile Qt files (.ui) run:
  pyuic4 ui_control.ui > ui_control.py
  pyuic4 ui_stimulus.ui > ui_stimulus.py

To compile Qt ressource files run:
  pyrcc4 icons.qrc > icons_rc.py


