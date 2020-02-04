format:
		isort -rc .
		black -t py36 toughio

black:
		black -t py36 toughio