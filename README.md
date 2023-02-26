# Abobot

## Description

This project is a music-playing bot written in Python, mainly using the youtube-dl and yt-dlp libraries. 
It allows you to play music from various sources, with full support currently only for YouTube. 
To use the bot, you need to create a .env file at the root of the project to specify the bot token. 
List of required environment variables is provided in .env_example file. For convenient program launching, Docker can be used with the make command. 
The following list shows the available commands that the bot supports:
1. Play: Used to connect and start playing. It accepts a link or a set of words. If the bot is already connected, it adds new tracks to the queue.
2. Disconnect: Used to disconnect the bot and clear the queue.
3. Stop: Clears the queue and stops the current playback.
4. Skip: Skips the current track and moves on to the next one.
5. Pause: Puts the connected bot on pause.
6. Resume: Continues playing tracks that have been paused.
7. List: Displays the queue of remaining tracks.
8. Shuffle: Shuffles the queue randomly.
9. NowPlaying: Displays the currently playing track with its time.

## Prerequisites

- Python 3.9
- youtube-dl and yt-dlp libraries
- discord.py library
- python-dotenv library
- dacite library
- A bot token from Discord

## Installation
1. Clone the repository using git clone https://github.com/Zewasik/Abobot.git
2. Install the dependencies using pip install -r requirements.txt
3. Create a .env file at the root of the project and add the following lines: 
    1. BOT_TOKEN=<your_token>
    2. JSON_CONFIG_PATH=./config.json

## Usage
1. Run the bot using `python bot.py` or to use docker:
    1. `make bot build` to build image
    2. `make bot run` to run container
3. Invite the bot to your Discord server using the invite link
4. Use the available commands to play music, skip tracks, shuffle the queue, etc.

## Contributing

1. Fork the project using the Fork button
2. Create a new branch with your changes: git checkout -b my-feature
3. Commit your changes: git commit -am 'Add some feature'
4. Push to the branch: git push origin my-feature
5. Submit a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
