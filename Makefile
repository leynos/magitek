.PHONY: markdownlint nixie

SHELL := bash
MDLINT ?= markdownlint-cli2
NIXIE ?= nixie

# Documentation gates are available while the baseline import plan is reviewed.
markdownlint:
	$(MDLINT) '**/*.md'

nixie:
	$(NIXIE) --no-sandbox
