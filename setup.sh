#!/usr/bin/env sh
URLBASE=https://github.com/marianoguerra/DRY/raw/master/scripts/

wget --no-check-certificate $URLBASE/web-skel.sh
wget --no-check-certificate $URLBASE/python-web.sh
wget --no-check-certificate $URLBASE/gae-setup.sh

sh gae-setup.sh .

rm web-skel.sh
rm python-web.sh
rm gae-setup.sh

wget -O src/feedparser.py http://feedparser.googlecode.com/svn/trunk/feedparser/feedparser.py
wget -O src/pubsubhubbub_publish.py http://pubsubhubbub.googlecode.com/svn/trunk/publisher_clients/python/pubsubhubbub_publish.py

svn checkout http://pubsubhubbub.googlecode.com/svn/trunk/ pubsubhubbub
