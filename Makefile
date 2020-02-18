format:
		isort -rc toughio
		isort -rc test
		black -t py27 toughio
		black -t py27 test

black:
		black -t py27 test