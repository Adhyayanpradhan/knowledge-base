class BasicScenario:
    def __init__(self, client):
        self.client = client

    def run(self):
        self.client.get("/")
        self.client.get("/health")
        self.client.get("/stats")