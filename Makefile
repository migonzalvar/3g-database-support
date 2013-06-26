clean:
	rm -rf .coverage coverage

.PHONY: .coverage

.coverage:
	coverage run --source modemconfiguration -m unittest discover -v

coverage: .coverage
	coverage html -d coverage
