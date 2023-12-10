version:
	bumpver init

update-patch:
	bumpver update --patch

update-minor:
	bumpver update --minor

update-major:
	bumpver update --major

build:
	pip-compile pyproject.toml
	python -m build
	twine check dist/*

upload:
	twine upload -r testpypi dist/*