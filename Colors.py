allColors = []
class Color:
    def __init__(self,name,r,g,b):
        self.name = name
        self.R = r
        self.G = g
        self.B = b
        self.RGB = (self.R,self.G,self.B)
        self.x = int()
        self.y = int()
        allColors.append(self)
    def printData(self):
        print(f"{self.name}: X: {self.x} Y: {self.y}")
black = Color("Black",0,0,0)
gray = Color("Gray",102,102,102)
blue = Color("Blue",0,80,205)
white = Color("White",255,255,255)
lightGray = Color("Light Gray",170,170,170)
lightBlue = Color("Light Blue",38,201,201)
green = Color("Green",1,116,32)
brown = Color("Brown",105,21,6)
lightBrown = Color("Light Blue",150,65,18)
lightGreen = Color("Light Green",17, 176, 60)
red = Color("Red",255,0,19)
orange = Color("Orange",255,120,41)
uglyBrown = Color("Ugly Brown",176,112,28)
purple = Color("Pruple",153,0,78)
skin = Color("Skin Color",203,90,87)
yellow = Color("Yellow",255,193,38)
pink = Color("Pink",255,0,143)
lightPink = Color("Light Pink",254,175,168)