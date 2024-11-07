# include OCI Images support
include .make/oci.mk

# include k8s support
include .make/k8s.mk

# include Helm Chart support
include .make/helm.mk

# Include Python support
include .make/python.mk

# include raw support
include .make/raw.mk

# include core make support
include .make/base.mk

# include your own private variables for custom deployment configuration
-include PrivateRules.mak

dev-all:
	python src/ska_jama_jira_integration/main.py --sync all

dev-l1:
	python src/ska_jama_jira_integration/main.py --sync l1

dev-l2:
	python src/ska_jama_jira_integration/main.py --sync l2

dev-test-cases:
	python src/ska_jama_jira_integration/main.py --sync test_cases

dev-interfaces:
	python src/ska_jama_jira_integration/main.py --sync interfaces

PYTHON_LINE_LENGTH = 88