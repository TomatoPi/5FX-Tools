DIR=~/.config/systemd/user/

JACK=sfx-start-jack.service
SERVER=sfx-start-server.service

SERVICES=$(JACK) $(SERVER)

all: install

install:
	mkdir -p $(DIR)
	cp $(SERVICES) $(DIR)
	systemctl --user enable $(SERVICES)

uninstall:
	rm $(addprefix $(DIR), $(SERVICES))
	systemctl --user disable $(SERVICES)