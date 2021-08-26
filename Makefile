SECTION="NetPing modules"
CATEGORY="Base"
TITLE="EPIC3 OWRT_Notifications"

PKG_NAME="OWRT_Notifications"
PKG_VERSION="Epic3.V1.S1"
PKG_RELEASE=1

MODULE_FILES=smtpmail.py
MODULE_FILES_DIR=/usr/lib/python3.7/

.PHONY: all install

all: install

install:
	for f in $(MODULE_FILES); do cp $${f} $(MODULE_FILES_DIR); done

clean:
	for f in $(MODULE_FILES); do rm -f $(MODULE_FILES_DIR)$${f}; done
