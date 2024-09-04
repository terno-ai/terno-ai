class Step():
    def __init__(self):
        pass

    def execute(self, llm, messages):
        return llm.get_response(messages)
