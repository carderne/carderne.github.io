#!/usr/bin/env bash
# Batch image resizer

# absolute path to image folder
FOLDER="."

# max height
WIDTH=1600

# max width
HEIGHT=1600

#resize png or jpg to either height or width, keeps proportions using imagemagick
#find ${FOLDER} -iname '*.jpg' -o -iname '*.png' -exec convert \{} -verbose -resize $WIDTHx$HEIGHT\> \{} \;

#resize png to either height or width, keeps proportions using imagemagick
#find ${FOLDER} -iname '*.png' -exec convert \{} -verbose -resize $WIDTHx$HEIGHT\> \{} \;

#resize jpg only to either height or width, keeps proportions using imagemagick
find ${FOLDER} -maxdepth 1 -iname '*.jpg' -exec convert \{} -verbose -quality 70 -resize $WIDTHx$HEIGHT\> \{} \;
