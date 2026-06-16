Cover art for the gallery. Two ways to drop in your own, both keyed by the hobby
name (keys live in tally/hobbies.py):

1. Palette-specific stock art (preferred for games, which recolour per palette):

       covers/<theme>/<hobby>.png

   where <theme> is one of: red orange yellow green blue indigo violet
   e.g.  covers/blue/quartiles.png   covers/red/quartiles.png

   The gallery shows the file matching the palette the viewer has selected.

2. One image used for every palette:

       covers/<hobby>.png
   e.g.  covers/movie.png

Resolution order for any cover: covers/<theme>/<hobby> first, then
covers/<hobby>, then a generated placeholder (tally/web/covers.py) drawn in the
active palette colour (games) or the hobby's own colour (everything else).

png, jpg, jpeg, webp, and svg all work. Posters look best at a 2:3 ratio.
