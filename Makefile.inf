SECTION="NetPing modules"
CATEGORY="Base"
TITLE="EPIC3 OWRT_Notifications"

PKG_NAME="OWRT_Notifications"
PKG_VERSION="Epic3.V1.S1"
PKG_RELEASE=11

MODULE_FILES=notify.py
MODULE_FILES_DIR=/etc/netping_notifications/

CONF_FILE=notifyconf
CONF_DIR=/etc/config/

.PHONY: all install

all: install

install:
	mkdir $(MODULE_FILES_DIR)
	cp $(CONF_FILE) $(CONF_DIR)
	for f in $(MODULE_FILES); do cp $${f} $(MODULE_FILES_DIR); done

clean:
	rm -f $(CONF_DIR)$(CONF_FILE)
	rm -rf $(MODULE_FILES_DIR)
