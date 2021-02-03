DIR=~/.config/systemd/user/

JACK=sfx-start-jack.service

SERVICES=$(JACK)

all: install

install:
	mkdir -p $(DIR)
	cp $(SERVICES) $(DIR)
	systemctl --user enable $(SERVICES)

uninstall:
	systemctl --user disable $(SERVICES)