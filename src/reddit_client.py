import asyncpraw


class Reddit:
    def __init__(self):
        self.client = None

    def set_client(self, client_id, client_secret, user_agent):
        self.client = asyncpraw.Reddit(client_id=client_id, client_secret=client_secret, user_agent=user_agent)

    def get_client(self):
        if self.client is None:
            raise Exception("No client set")
        else:
            return self.client
