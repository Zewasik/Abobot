from discord.ext import commands


class AppContext(commands.Context):
    """
    Extended Discord Context. Provides additional methods
    """

    def is_client_connected(self) -> bool:
        """
        :return: True - client (bot) is connected
        """
        return self.voice_client is not None

    def is_client_playing(self) -> bool:
        """
        :return: True - client (bot) is playing
        """
        return self.is_client_connected() and (self.voice_client.is_playing() or self.voice_client.is_paused())

    def is_author_connected(self) -> bool:
        """
        Checks whether message author is connected to any voice channel where client is presented
        :return: True - message author is connected
        """
        return self.author.voice and self.author.voice.channel

    def is_same_channel(self) -> bool:
        """
        :return: True - client & author are on the same voice channel
        """
        return self.is_author_connected() and self.voice_client.channel == self.author.voice.channel
