import json

class FileManager:
    def loadJson(self, file):
        with open(file, "r") as f:
            config = json.load(f)

        return config