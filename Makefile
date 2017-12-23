# Minimal makefile for Sphinx documentation
#

# You can set these variables from the command line.
SPHINXOPTS    =
SPHINXBUILD   = sphinx-build
SPHINXPROJ    = LambdaDecorators
SOURCEDIR     = .
BUILDDIR      = _build

README.rst:
	python3 -c 'import lambda_decorators;print(lambda_decorators.__doc__)' > README.rst
	sed -r -i'' -e 's|:meth:`(.*)`|`\1 <http://lambda-decorators.rtfd.io#lambda_decorators.\1>`_|g' README.rst
	echo '`Full API Documentation <http://lambda-decorators.readthedocs.io/en/latest/>`_' >> README.rst

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile README.rst

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
