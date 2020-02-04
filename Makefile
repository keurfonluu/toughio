format:
		isort -rc toughio
		black -t py36 toughio

black:
		black -t py36 toughio