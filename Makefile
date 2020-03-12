format:
		make isort
		make black
		make docstring

isort:
		isort -rc toughio
		isort -rc test

black:
		black -t py27 toughio
		black -t py27 test

docstring:
		docformatter -r -i --blank --wrap-summaries 88 --wrap-descriptions 88 --pre-summary-newline toughio

clean:
		find . -name '__pycache__' -delete -print -o -name '*.pyc' -delete -print
		rm -rf *.egg-info/ build/ dist/