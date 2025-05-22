class PixelData:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color

    def print(self):
        print(self.x, self.y, self.color)