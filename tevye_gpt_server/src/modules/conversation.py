class Conversation:

    def __init__(self):
        self.developer_message = None
        self.messages = []

    async def request(self, data):
        print(data)


chat = Conversation()
