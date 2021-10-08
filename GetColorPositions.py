from Colors import *
import mouse
from mouse import LEFT
import pyautogui
import tkinter as tk
import threading
def SetColorPositions():
    colorToChange = black
    labelText = "Click the black Color"
    for i in range(3):
        if(i == 1):
            labelText = "Click the gray Color (to the right of black)"
            colorToChange=gray
        if(i == 2):
            labelText = "Click the white Color (below black)"
            colorToChange=white
            print("Checking for white")
        statusLabel.config(text=labelText)
        mouse.wait(LEFT, mouse.DOWN)
        position = pyautogui.position()
        statusLabel.config(text=position)
        colorToChange.x = position.x
        colorToChange.y = position.y

    xOffset = abs(black.x - gray.x)
    yOffset = 0
    for color, loopCount in zip(allColors, range(3, len(allColors)+3)):
        if(loopCount % 3 == 0):
            color.x = black.x
            color.y = black.y + yOffset
        if(loopCount % 3 == 1):
            color.x = black.x + xOffset
            color.y = black.y + yOffset
        if(loopCount % 3 == 2):
            color.x = black.x + xOffset * 2
            color.y = black.y + yOffset
            print("Offset is: ",black.y - white.y)
            yOffset += abs(black.y - white.y)
    for color in allColors:
        color.printData()


def GetPosition():
    mouse.wait(LEFT, mouse.DOWN)
    print(pyautogui.position())
def DrawTest():
    for color in allColors:
        mouse.move(color.x,color.y)
        mouse.click()
        mouse.move(color.x+227,color.y)
        mouse.click()
def SaveColorPositions():
    try:
        LB = "\n"
        file = open("positions.txt","w")
        for color in allColors:
            file.write(str(color.x) +"\n" + str(color.y)+"\n")
        statusLabel.config(text="Save successful :)")
    except Exception as e:
        statusLabel.config(text=f"Save failed :({e}")
    finally:
        file.close()
def LoadColorPositions():
    try:
        lineNumber = 0
        file = open("positions.txt","r")
        fileLines = file.readlines()
        for color in allColors:
            color.x = int(fileLines[lineNumber].split("\n")[0])
            lineNumber +=1
            color.y = int(fileLines[lineNumber].split("\n")[0])
            lineNumber +=1       
        if(len(fileLines) != 36):
            statusLabel.config(text=f"Position load failed :( (Have you saved positions yet?)")
        else:
            statusLabel.config(text=f"Position load successful :)")
        
    except Exception as e:
        statusLabel.config(text=f"Position load failed :({e}")
    finally:
        file.close()
root = tk.Tk()
root.geometry("800x600")
root.title("Set Color Positions")

tk.Button(root, text="Set Color Positions", command=lambda: threading.Thread(
    target=SetColorPositions).start()).pack()
tk.Button(root, text="Get mouse position",
          command=lambda: threading.Thread(target=GetPosition).start()).pack()

tk.Button(root, text="Do color test",command=lambda: threading.Thread(target=DrawTest).start()).pack()
tk.Button(root, text="Save color positions",command=lambda: threading.Thread(target=SaveColorPositions).start()).pack()
tk.Button(root, text="Load color positions",command=lambda: threading.Thread(target=LoadColorPositions).start()).pack()
statusLabel = tk.Label(text="Hello!")
statusLabel.pack()
root.mainloop()
