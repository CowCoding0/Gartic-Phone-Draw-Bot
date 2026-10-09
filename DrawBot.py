import tkinter as tk
import time
import mouse
from mouse import LEFT, DOWN, get_position, wait
import threading
from Colors import *
from PIL import Image
from PIL import ImageEnhance
from PIL import ImageGrab
from io import BytesIO
import requests
from urllib.request import Request, urlopen
import keyboard
import os
import random
from tkinter import filedialog
from PixelData import *
from math import sqrt
import ctypes
import sys

scalingFactor = ctypes.windll.shcore.GetScaleFactorForDevice(0) / 100 # Gets windows screen scale
#drawingArea = (10,10)
corner1 = (2998, 304)
corner2 = (3707, 683)
fileName = str()
stopDrawing = False
strokeDelay = 0.01 # Seconds to wait around pressing and releasing so the browser keeps up
moveDelay = 0.002 # Seconds to wait between small moves inside a stroke
maxStepSize = 8 # Longest single mouse move inside a stroke, in pixels
minAreaSize = 6 # Areas with fewer pixels than this are merged into the color around them

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

        if (len(fileLines) != 36):
            statusLabel.config(text=f"Position load failed :( (Have you saved positions yet?)")
        else:
            statusLabel.config(text=f"Position load successful :)")

        file.close()

    except Exception as e:
        statusLabel.config(text=f"Position load failed :(Have you saved positions yet?{e}")

def LoadImage():
    if (imageMode.get() == 3):
        clipboard = ImageGrab.grabclipboard()

        # Copying an image file in File Explorer puts its path on the clipboard instead of the picture
        if (isinstance(clipboard, list) and clipboard):
            clipboard = Image.open(clipboard[0])

        if (not isinstance(clipboard, Image.Image)):
            raise ValueError("No image on the clipboard. Right click an image and pick Copy image first.")

        return ImageEnhance.Sharpness(clipboard.convert('RGBA')).image

    if (imageMode.get() == 1 or imageMode.get() == 0):
        response = requests.get(urlInput.get())
        return ImageEnhance.Sharpness(Image.open(BytesIO(response.content)).convert('RGBA')).image

    print(fileName)
    return ImageEnhance.Sharpness(Image.open(fileName).convert('RGBA')).image

def LoadColorGrid(gridSize):
    # The image as grid[y][x] of palette colors, None where nothing should be drawn
    img = LoadImage().resize((gridSize, gridSize))
    pix = img.load()
    maxColors = max(1, int(maxColorsEntry.get()))

    # Keep only the most used colors (plus the white background), and move every other pixel to the closest kept color
    counts = {}

    for y in range(gridSize):
        for x in range(gridSize):
            if (pix[x, y][3] != 0):
                color = allColors[FindClosestRGB(pix[x, y])]
                counts[color] = counts.get(color, 0) + 1

    keptColors = [color for color in sorted(counts, key=counts.get, reverse=True) if color is not white][:maxColors] + [white]
    print("Colors:", ", ".join(color.name for color in keptColors))

    grid = [[keptColors[FindClosestRGB(pix[x, y], keptColors)] if pix[x, y][3] != 0 else white
             for x in range(gridSize)] for y in range(gridSize)]

    RemoveSpecks(grid)
    return [[None if color is white else color for color in row] for row in grid]

def Neighbors(x, y, size):
    for nx in range(x - 1, x + 2):
        for ny in range(y - 1, y + 2):
            if ((nx, ny) != (x, y) and 0 <= nx < size and 0 <= ny < size):
                yield nx, ny

def RemoveSpecks(grid):
    # Repaint areas smaller than minAreaSize with the color around them, since each area costs a stroke
    size = len(grid)
    seen = [[False] * size for _ in range(size)]

    for y in range(size):
        for x in range(size):
            if (seen[y][x]):
                continue

            color = grid[y][x]
            area = [(x, y)]
            seen[y][x] = True
            borderColors = {}

            for ax, ay in area: # area grows while it is walked, like a flood fill
                for nx, ny in Neighbors(ax, ay, size):
                    if (grid[ny][nx] is color):
                        if (not seen[ny][nx]):
                            seen[ny][nx] = True
                            area.append((nx, ny))
                    else:
                        borderColors[grid[ny][nx]] = borderColors.get(grid[ny][nx], 0) + 1

            if (len(area) < minAreaSize and borderColors):
                fill = max(borderColors, key=borderColors.get)

                for ax, ay in area:
                    grid[ay][ax] = fill

def DotPlace():
    global stopDrawing
    stopDrawing = False
    detailLevel = 10 - int(detailLevelEntry.get()) + 1
    pixelCount = 200
    gridSize = int(pixelCount / detailLevel)
    left = min(corner1[0], corner2[0])
    top = min(corner1[1], corner2[1])
    xAddAmount = abs(corner1[0] - corner2[0]) / gridSize
    yAddAmount = abs(corner1[1] - corner2[1]) / gridSize

    grid = LoadColorGrid(gridSize)
    lastColor = None

    for x in range(gridSize):
        for y in range(gridSize):
            if (stopDrawing): # if esc is pushed, quit drawing
                return

            color = grid[y][x]

            if (color is None):
                continue

            time.sleep(0.001) # Pause before drawing again

            if (color is not lastColor):
                # Account for windows screen scaling when moving
                mouse.move(color.x / scalingFactor, color.y / scalingFactor, duration=0)
                mouse.click(LEFT)

            mouse.move(left + xAddAmount * x, top + y * yAddAmount, duration=0)
            mouse.click(LEFT)
            lastColor = color

    mouse.move(white.x, white.y)
    mouse.click(LEFT)

def LinePlace():
    global stopDrawing
    stopDrawing = False
    detailLevel = 10 - int(detailLevelEntry.get()) + 1
    pixelCount = 200
    gridSize = int(pixelCount / detailLevel)
    left = min(corner1[0], corner2[0])
    top = min(corner1[1], corner2[1])
    xAddAmount = abs(corner1[0] - corner2[0]) / gridSize
    yAddAmount = abs(corner1[1] - corner2[1]) / gridSize

    grid = LoadColorGrid(gridSize)

    # Split each row into runs of the same color, grouped by color so each color is only selected once
    runsByColor = {}

    for y in range(gridSize):
        runStart = 0
        runColor = None

        for x in range(gridSize + 1):
            color = grid[y][x] if x < gridSize else None

            if (color is not runColor):
                if (runColor is not None):
                    runsByColor.setdefault(runColor, []).append((runStart, x - 1, y))

                runStart = x
                runColor = color

    strokesByColor = {color: BuildStrokes(runs) for color, runs in runsByColor.items()}
    print("Strokes:", sum(len(strokes) for strokes in strokesByColor.values()))

    for color, strokes in strokesByColor.items():
        if (stopDrawing):
            return

        # Account for windows screen scaling when selecting the color
        mouse.move(color.x / scalingFactor, color.y / scalingFactor)
        mouse.click(LEFT)
        time.sleep(strokeDelay)

        for stroke in strokes:
            if (stopDrawing):
                return

            points = [(left + (x + 0.5) * xAddAmount, top + (y + 0.5) * yAddAmount) for x, y in stroke]

            # Turn a lone pixel into a short line, since Gartic drops dots when submitting
            if (len(set(points)) == 1):
                points.append((points[0][0] + max(2, xAddAmount / 2), points[0][1]))

            DrawPath(points)

def BuildStrokes(runs):
    # One stroke per connected area: walk every run in the area and step back over already painted runs
    # to reach the rest, so the pen never has to lift or cross another color
    runsByRow = {}

    for run in runs:
        runsByRow.setdefault(run[2], []).append(run)

    visited = set()
    strokes = []
    sys.setrecursionlimit(max(sys.getrecursionlimit(), len(runs) + 1000))

    for run in runs:
        if (run in visited):
            continue

        visited.add(run)
        path = [(run[0], run[2])]
        lastNewPoint = [0]
        TourRun(run, run[0], runsByRow, visited, path, lastNewPoint)
        strokes.append(path[:lastNewPoint[0] + 1]) # the walk back after the last new run paints nothing

    return strokes

def TourRun(run, entryX, runsByRow, visited, path, lastNewPoint):
    # Sweep the run left to right, detouring into each unvisited touching run (diagonals included) and back,
    # then return to entryX so the caller can carry on from where it entered
    startX, endX, y = run

    def AddPoint(x, y, isNew):
        path.append((x, y))

        if (isNew):
            lastNewPoint[0] = len(path) - 1

    touching = [r for row in (y - 1, y + 1) for r in runsByRow.get(row, []) if r[0] <= endX + 1 and startX - 1 <= r[1]]
    touching.sort(key=lambda r: max(r[0], startX))
    AddPoint(startX, y, True)

    for nextRun in touching:
        if (nextRun in visited):
            continue

        visited.add(nextRun)
        leaveX = min(max(nextRun[0], startX), endX)
        enterX = min(max(leaveX, nextRun[0]), nextRun[1])
        AddPoint(leaveX, y, True)
        AddPoint(enterX, nextRun[2], True)
        TourRun(nextRun, enterX, runsByRow, visited, path, lastNewPoint)
        AddPoint(leaveX, y, False)

    AddPoint(endX, y, True)
    AddPoint(entryX, y, False)

def DrawPath(points):
    mouse.move(*points[0])
    mouse.press(LEFT)
    time.sleep(strokeDelay)

    for (fromX, fromY), (toX, toY) in zip(points, points[1:]):
        # Move in small steps so the browser draws a straight line instead of smoothing a long jump
        steps = max(1, int(max(abs(toX - fromX), abs(toY - fromY)) / maxStepSize))

        for step in range(1, steps + 1):
            mouse.move(fromX + (toX - fromX) * step / steps, fromY + (toY - fromY) * step / steps)
            time.sleep(moveDelay)

    time.sleep(strokeDelay)
    mouse.release(LEFT)
    time.sleep(strokeDelay)

def DrawImage():
    try:
        if(drawMode.get() == 0):
            DotPlace()
        else:
            LinePlace()

    except Exception as e:
        statusLabel.config(text=f"Draw failed :( {e}")

def SetDrawingBoundary():
    global drawingArea
    global corner1, corner2
    statusLabel.config(text="Click top left corner")
    mouse.wait(LEFT, mouse.DOWN)
    corner1 = get_position()
    statusLabel.config(text="Click bottom right corner")
    mouse.wait(LEFT, mouse.DOWN)
    corner2 = get_position()
    x = abs(corner1[0] - corner2[0])
    y = abs(corner1[0] - corner2[1])
    drawingArea = (x, y)
    print("Drawing Area:", drawingArea)
    statusLabel.config(text="Drawing Area Set")

def FindClosestRGB(rgb: tuple, colors=allColors):
    values = list()

    for color in colors:
        number = 0
        number += abs(rgb[0] - color.RGB[0])
        number += abs(rgb[1] - color.RGB[1])
        number += abs(rgb[2] - color.RGB[2])
        
        red = pow(rgb[0] - color.RGB[0], 2)
        green = pow(rgb[1] - color.RGB[1], 2)
        blue = pow(rgb[2] - color.RGB[2], 2)
        number = sqrt(red + green + blue)
        values.append(number)

    index_min = min(range(len(values)), key=values.__getitem__)
    #print(allColors[index_min].name)
    return index_min

def ChangeImageMode():
    if(imageMode.get() == 1):
        urlInput.pack()
        localFileButton.forget()
    elif(imageMode.get() == 2):
        urlInput.forget()
        localFileButton.pack()
    elif(imageMode.get() == 3):
        urlInput.forget()
        localFileButton.forget()

def OpenFile():
    global fileName
    fileName = filedialog.askopenfilename(initialdir="", filetypes=[(
        "PNG", "*.png"), ("JPG", "*.jpg"), ("JPEG", "*.jpeg")])
    print(fileName)

def Exit():
    global stopDrawing
    stopDrawing = True
    print("Exiting")
    #os._exit(0)

# GUI
root = tk.Tk()
#slowMode = tk.BooleanVar()
slowMode = True
imageMode = tk.IntVar(value=3)
drawMode = tk.IntVar()
root.geometry("800x600")
root.title("Gartic Drawbot")

tk.Radiobutton(root,
               text="Clipboard",
               padx=20,
               variable=imageMode,
               command=ChangeImageMode,
               value=3).pack()

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
maxColorsEntry = tk.Entry(root)
tk.Label(root, text="Max Colors 1-17").pack()
maxColorsEntry.insert(0, "4")
maxColorsEntry.pack()
#slowModeCheck = tk.Checkbutton(text="Slow Mode", variable=slowMode)
#slowModeCheck.pack()
statusLabel = tk.Label(text="Hello!")
statusLabel.pack()
LoadColorPositions()
urlInput = tk.Entry(root)
localFileButton = tk.Button(root, text="Open File", command=OpenFile)
keyboard.add_hotkey("esc", Exit)
root.mainloop()