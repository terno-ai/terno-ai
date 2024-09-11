class Step():
    def __init__(self, llm, messages):
        self.llm = llm
        self.messages = messages

    def execute(self):
        return self.llm.get_response(self.messages)
