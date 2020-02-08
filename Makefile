format:
		isort -rc toughio
		black -t py27 toughio

black:
		black -t py27 toughio