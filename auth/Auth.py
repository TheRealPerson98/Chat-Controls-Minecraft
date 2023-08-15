class Auth:
    """Base Authentication class."""

    def get_live_broadcast_id(self):
        raise NotImplementedError

    def get_chat_messages(self):
        raise NotImplementedError
