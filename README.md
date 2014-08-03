Helangor
========

This is just a simple game to find the best ways to handle a hexagon grid
system and how to organize your pygame files, objects, ...

I try to do something cool with asyncio, and therefore this game will only
run on python version 3.3+.

Requirements
------------

pygame
pyyaml


Install pygame for python3 (Mint/Ubuntu)
----------------------------------------

	virtualenv -p python3 py3

	. ./py3/bin/activate

	sudo apt-get install python3-dev libsdl-image1.2-dev libsdl-mixer1.2-dev libsdl-ttf2.0-dev libsdl1.2-dev libsmpeg-dev python-numpy subversion libportmidi-dev libfreetype6-dev

	svn co svn://seul.org/svn/pygame/trunk pygame
	cd pygame
	python setup.py build
	python setup.py install

	pip install pyyaml

How to start the game
---------------------

Download everything and run:

   python3 game.py


Helpful links
-------------

very interesting blogpost about hexagons. Helped me alot with some aspects.

http://www.redblobgames.com/grids/hexagons/

License
-------

GPL V2