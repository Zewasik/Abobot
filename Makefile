bot-build-dev:
	DOCKER_BUILDKIT=1 docker build \
		--tag discord-music-bot-dev \
		--secret id=bot_env,src=./.env \
		.

bot-run-dev:
	docker run -d --rm --name=bot_container-dev discord-music-bot-dev:latest

bot-stop-dev:
	docker stop bot_container-dev

bot-attach-dev:
	docker attach --detach-keys="ctrl-x" bot_container-dev

bot-rebuild-dev:
	make bot-stop-dev
	make bot-build-dev
	docker run --rm --name=bot_container-dev discord-music-bot-dev:latest

bot-build:
	DOCKER_BUILDKIT=1 docker build \
			--tag discord-music-bot \
			--secret id=bot_env,src=./.env \
			.

bot-run:
	docker run -d --restart=always --name=bot_container discord-music-bot:latest

bot-stop:
	docker stop bot_container

bot-attach:
	docker attach --detach-keys="ctrl-x" bot_container
