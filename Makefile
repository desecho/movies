.PHONY: create-venv
create-venv:
	dev_scripts/create_venv.sh

.PHONY: install-deps
install-deps:
	# Install Python
	sudo apt install python3.7 python3.7-venv python3.7-dev -y
	# Install MySQL dependencies
	sudo apt install libmysqlclient-dev -y

.PHONY: pydiatra
pydiatra:
	dev_scripts/pydiatra.sh
