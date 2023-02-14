bot-build-dev:
	docker build . -t discord-music-bot-dev

bot-run-dev:
	docker run -d --env-file=./.env --name=bot_container-dev discord-music-bot-dev:latest

bot-stop-dev:
	docker stop bot_container-dev
	docker rm bot_container-dev

bot-attach-dev:
	docker attach --detach-keys="ctrl-x" bot_container-dev

bot-rebuild-dev:
	make bot-stop-dev
	make bot-build-dev
	docker run --env-file=./.env --name=bot_container-dev discord-music-bot-dev:latest

bot-build:
	docker build . -t discord-music-bot

bot-run:
	docker run -d --restart=always --env-file=./.env --name=bot_container discord-music-bot:latest

bot-stop:
	docker stop bot_container
	docker rm bot_container

bot-attach:
	docker attach --detach-keys="ctrl-x" bot_container
