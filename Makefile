.PHONY: docs build

project = abjadext
errors = E203,E266,E501,W503
origin := $(shell git config --get remote.origin.url)
formatPaths = ${project}/ tests/ *.py
testPaths = ${project}/ tests/

black-check:
	black --check --diff --target-version py38 ${formatPaths}

black-reformat:
	black --target-version py38 ${formatPaths}

build:
	python setup.py sdist

clean:
	find . -name '*.pyc' | xargs rm
	rm -Rif *.egg-info/
	rm -Rif .cache/
	rm -Rif .tox/
	rm -Rif __pycache__
	rm -Rif build/
	rm -Rif dist/
	rm -Rif htmlcov/
	rm -Rif prof/

docs:
	make -C docs/ html

flake8-check:
	flake8 --ignore=${errors} --isolated --max-line-length=88 ${formatPaths}

gh-pages:
	rm -Rf gh-pages/
	git clone $(origin) gh-pages/
	cd gh-pages/ && \
		git checkout gh-pages || git checkout --orphan gh-pages
	rsync -rtv --del --exclude=.git docs/build/html/ gh-pages/
	cd gh-pages && \
		touch .nojekyll && \
		git add --all . && \
		git commit --allow-empty -m "Update docs" && \
		git push -u origin gh-pages
	rm -Rf gh-pages/

isort-check:
	isort \
		--apply \
		--case-sensitive \
		--check-only \
		--diff \
		--force-grid-wrap=0 \
		--line-width=88 \
		--multi-line=3 \
		--project=abjad \
		--recursive \
		--thirdparty=uqbar \
		--trailing-comma \
		--use-parentheses \
		${formatPaths}

isort-reformat:
	isort \
		--apply \
		--case-sensitive \
		--force-grid-wrap=0 \
		--line-width=88 \
		--multi-line=3 \
		--project=abjad \
		--recursive \
		--thirdparty=uqbar \
		--trailing-comma \
		--use-parentheses \
		${formatPaths}

mypy:
	mypy ${project}/

pytest:
	rm -Rf htmlcov/
	pytest \
		--cov-config=.coveragerc \
		--cov-report=html \
		--cov-report=term \
		--cov=${project}/ \
		--durations=20 \
		${testPaths}

pytest-x:
	rm -Rf htmlcov/
	pytest \
		-x \
		--cov-config=.coveragerc \
		--cov-report=html \
		--cov-report=term \
		--cov=${project}/ \
		--durations=20 \
		${testPaths}

reformat:
	make isort
	make black-reformat

release:
	make clean
	make build
	twine upload dist/*.tar.gz

check:
	make black-check
	make flake8-check
	make isort-check

test:
	make black-check
	make flake8-check
	make isort-check
	make mypy
	make pytest
