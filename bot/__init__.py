DEV_CHANNEL_ID = -1001422577723  # TODO: delete when not needed
# main group chat ID = -527173863


class ConfigHandler:
    """
    A convenience to have *entity.config_name* like access to configurations.

    Example:
        # create
        bot_config = ConfigHandler(
            name="bot",
            key="key",
        )
        # use
        start_bot(name=bot_config.name, key=bot_config.key)
        or
        start_bot(**bot_config.all)
    """
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
        self.all = self.__dict__
