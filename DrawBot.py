
import tkinter as tk
import time
import mouse
from mouse import LEFT, DOWN, get_position, wait
import threading
from Colors import *
from PIL import Image
from PIL import ImageEnhance
from io import BytesIO
import requests
from urllib.request import Request, urlopen
import keyboard
import os
import random
from tkinter import filedialog
from PixelData import *
#drawingArea = (10,10)
corner1 = (2998, 304)
corner2 = (3707, 683)
fileName = str()


def LoadColorPositions():
    try:
        lineNumber = 0
        file = open("positions.txt", "r")
        fileLines = file.readlines()
        for color in allColors:
            color.x = int(fileLines[lineNumber].split("\n")[0])
            lineNumber += 1
            color.y = int(fileLines[lineNumber].split("\n")[0])
            lineNumber += 1
        if(len(fileLines) != 36):
            statusLabel.config(
                text=f"Position load failed :( (Have you saved positions yet?)")
        else:
            statusLabel.config(text=f"Position load successful :)")

    except Exception as e:
        statusLabel.config(text=f"Position load failed :({e}")
    finally:
        file.close()


def DotPlace():
    img = 0
    detailLevel = 10-int(detailLevelEntry.get())+1
    pixelCount = 200
    drawingArea = (abs(corner1[0]-corner2[0]), abs(corner1[1]-corner2[1]))
    xAddAmount = drawingArea[0]/pixelCount*detailLevel
    yAddAmount = drawingArea[1]/pixelCount*detailLevel
    print(int(drawingArea[0]*drawingArea[1]/5))
    if(imageMode.get() == 1 or imageMode.get() == 0):
        response = requests.get(urlInput.get())
        #response = requests.get("https://cdn.discordapp.com/attachments/374695917170851840/895139808895205487/Screenshot-2021-10-05-205602.png")
        #img = Image.open(BytesIO(response.content))
        img = ImageEnhance.Sharpness(Image.open(
            BytesIO(response.content)).convert('RGBA')).image
    else:
        print(fileName)
        img = ImageEnhance.Sharpness(
            Image.open(fileName).convert('RGBA')).image
    #img = ImageEnhance.Sharpness (Image.open("unnamed.png").convert('RGBA')).image
    #edges = img.filter(ImageFilter.FIND_EDGES)
    img = img.resize((int(pixelCount/detailLevel),
                     int(pixelCount/detailLevel)))
    pix = img.load()
    xSize, ySize = img.size
    print(pix)
    lastColor = "Name"
    for x in range(int(xSize)):
        for y in range(int(ySize)):
            if(pix[x, y][3] == 0):
                continue
            colorIndex = FindClosestRGB(pix[x, y])
            if(allColors[colorIndex].name == "White"):
                continue

            colorPosition = (allColors[colorIndex].x, allColors[colorIndex].y)
            if(random.randint(1, 5) == 1 or slowMode.get() is True):
                time.sleep(0.0000000001)

            if(allColors[colorIndex].name != lastColor):
                mouse.move(colorPosition[0], colorPosition[1], duration=0)
                mouse.click(LEFT)

            # mouse.move(corner1[0]+x*detailLevel,corner1[1]+y*detailLevel,duration=0)
            mouse.move(corner1[0]+xAddAmount*x,
                       corner1[1]+y*yAddAmount, duration=0)
            mouse.click(LEFT)
            lastColor = allColors[colorIndex].name
    mouse.move(white.x, white.y)
    mouse.click(LEFT)
    pix[0, 0] = (75, 22, 255)


def LinePlace():
    img = 0
    detailLevel = 10-int(detailLevelEntry.get())+1
    pixelCount = 200
    drawingArea = (abs(corner1[0]-corner2[0]), abs(corner1[1]-corner2[1]))
    xAddAmount = drawingArea[0]/pixelCount*detailLevel
    yAddAmount = drawingArea[1]/pixelCount*detailLevel

    if(imageMode.get() == 1 or imageMode.get() == 0):
        response = requests.get(urlInput.get())
        #response = requests.get("https://cdn.discordapp.com/attachments/374695917170851840/895139808895205487/Screenshot-2021-10-05-205602.png")
        #img = Image.open(BytesIO(response.content))
        img = ImageEnhance.Sharpness(Image.open(
            BytesIO(response.content)).convert('RGBA')).image
    else:
        print(fileName)
        img = ImageEnhance.Sharpness(
            Image.open(fileName).convert('RGBA')).image
    #img = ImageEnhance.Sharpness (Image.open("unnamed.png").convert('RGBA')).image
    #edges = img.filter(ImageFilter.FIND_EDGES)
    img = img.resize((int(pixelCount/detailLevel),
                     int(pixelCount/detailLevel)))
    pix = img.load()
    xSize, ySize = img.size
    print(pix)
    lastColor = "Name"
    allPixelData = []
    for x in range(int(xSize)):
        for y in range(int(ySize)):
            if(pix[x, y][3] == 0):
                continue
            color = FindClosestRGB(pix[x, y])
            if(allColors[color].name == "White"):
                continue
            allPixelData.append(PixelData(x, y, allColors[color]))
    length = len(allPixelData)
    print(len(allPixelData))

    currentX = 0

    def DrawFromTo(start, end, color: Color):
        mouse.move(color.x, color.y)
        mouse.click()
        # mouse.drag(corner1[0]+xAddAmount*start[0],corner1[1]+yAddAmount*start[1],corner1[0]+xAddAmount*end[0],corner1[1]+yAddAmount*end[1])
        mouse.move(corner1[0]+xAddAmount*start[0],
                   corner1[1]+yAddAmount*start[1])
        mouse.hold()
        mouse.move(corner1[0]+xAddAmount*end[0], corner1[1]+yAddAmount*end[1])
        time.sleep(0.000001)
        mouse.release()

    def remove_values_from_list(the_list, val):
        return [value for value in the_list if value.x != val]

    while True:
        thisX = []
        for i in allPixelData:
            if(i.x != currentX):

                allPixelData = remove_values_from_list(allPixelData, currentX)

                currentX += 1
                break

            thisX.append(i)

        if(currentX == pixelCount/detailLevel-1):
            break
        startData: PixelData = PixelData
        for i in range(len(thisX)):

            if(i == 0):

                startData = thisX[i]

                continue
            if(thisX[i].color.name != startData.color.name) or i == len(thisX)-1:

                DrawFromTo((startData.x, startData.y),
                           (thisX[i-1].x, thisX[i-1].y), startData.color)
                startData = thisX[i]
        if(len(allPixelData) == 0):
            break


def DrawImage():
    if(drawMode.get() == 0):
        DotPlace()
    else:
        LinePlace()


def SetDrawingBoundary():
    global drawingArea
    global corner1, corner2
    statusLabel.config(text="Click corner 1")
    mouse.wait(LEFT, mouse.DOWN)
    corner1 = get_position()
    statusLabel.config(text="Click corner 2")
    mouse.wait(LEFT, mouse.DOWN)
    corner2 = get_position()
    x = abs(corner1[0]-corner2[0])
    y = abs(corner1[0]-corner2[1])
    drawingArea = (x, y)
    print(drawingArea)
    statusLabel.config(text="Set drawing area")


def FindClosestRGB(rgb: tuple):
    values = list()
    for color in allColors:
        number = 0
        number += abs(rgb[0]-color.RGB[0])
        number += abs(rgb[1]-color.RGB[1])
        number += abs(rgb[2]-color.RGB[2])
        values.append(number)

    index_min = min(range(len(values)), key=values.__getitem__)
    print(allColors[index_min].name)
    return index_min


def ChangeImageMode():
    if(imageMode.get() == 1):
        urlInput.pack()
        localFileButton.forget()
    elif(imageMode.get() == 2):
        urlInput.forget()
        localFileButton.pack()


def OpenFile():
    global fileName
    fileName = filedialog.askopenfilename(initialdir="", filetypes=[(
        "PNG", "*.png"), ("JPG", "*.jpg"), ("JPEG", "*.jpeg")])
    print(fileName)


def Exit():
    print("Exiting")
    os._exit(0)


root = tk.Tk()
slowMode = tk.BooleanVar()
imageMode = tk.IntVar()
drawMode = tk.IntVar()
root.geometry("800x600")
root.title("Gartic Drawbot")

tk.Radiobutton(root,
               text="URL",
               padx=20,
               variable=imageMode,
               command=ChangeImageMode,
               value=1).pack()
tk.Radiobutton(root,
               text="Local File",
               padx=20,
               command=ChangeImageMode,
               variable=imageMode,
               value=2).pack()
tk.Radiobutton(root,
               text="Dot Placement",
               padx=20,
               variable=drawMode,
               command=ChangeImageMode,
               value=0).pack()
tk.Radiobutton(root,
               text="Line Placement",
               padx=20,
               command=ChangeImageMode,
               variable=drawMode,
               value=1).pack()
tk.Button(root, text="Set drawing boundary", command=lambda: threading.Thread(
    target=SetDrawingBoundary).start()).pack()

tk.Button(root, text="Draw Image", command=DrawImage).pack()

detailLevelEntry = tk.Entry(root)
tk.Label(root, text="Detail Level 1-10").pack()

detailLevelEntry.insert(0, "9")
detailLevelEntry.pack()
slowModeCheck = tk.Checkbutton(text="Slow Mode", variable=slowMode)
slowModeCheck.pack()
statusLabel = tk.Label(text="Hello!")
statusLabel.pack()
LoadColorPositions()
urlInput = tk.Entry(root)
urlInput.pack()
localFileButton = tk.Button(root, text="Open File", command=OpenFile)
keyboard.add_hotkey("esc", Exit)
root.mainloop()
