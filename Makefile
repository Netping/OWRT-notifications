SECTION="NetPing modules"
CATEGORY="Base"
TITLE="EPIC3 OWRT_Notifications"

PKG_NAME="OWRT_Notifications"
PKG_VERSION="Epic3.V1.S1"
PKG_RELEASE=5

MODULE_FILES=notify.py
MODULE_FILES_DIR=/usr/lib/python3.7/

CONF_FILE=notifyconf
CONF_DIR=/etc/config/

.PHONY: all install

all: install

install:
	cp $(CONF_FILE) $(CONF_DIR)
	for f in $(MODULE_FILES); do cp $${f} $(MODULE_FILES_DIR); done

clean:
	rm -f $(CONF_DIR)$(CONF_FILE)
	for f in $(MODULE_FILES); do rm -f $(MODULE_FILES_DIR)$${f}; done
