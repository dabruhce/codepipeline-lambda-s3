release:
	pep8 --exclude=libs/* .
	nosetests

verify:
	git diff --exit-code
push: release verify
	git push
