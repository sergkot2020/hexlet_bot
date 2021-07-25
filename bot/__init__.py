DEV_CHANNEL_ID = -1001422577723  # TODO: delete when not needed


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
        start_bot(**bot_config.all())
    """
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def all(self):
        return self.__dict__
