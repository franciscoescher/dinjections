test:
	python -m unittest tests/test_*.py

update-patch:
	bumpver update --patch

update-minor:
	bumpver update --minor

update-major:
	bumpver update --major

build:
	rm -rf dist
	pip-compile pyproject.toml
	python -m build
	twine check dist/*

upload:
	twine upload dist/*
