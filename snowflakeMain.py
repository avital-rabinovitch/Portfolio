from tkinter import *
import snowflake
import tkinter.simpledialog
import tkinter.messagebox
import random
import copy
###FOR EXPORT
from tkinter import filedialog
import subprocess
import os
import io
from PIL import Image



class Gradient():
    '''A gradient which uses a canvas to draw the background'''
    def __init__(self, limit = 0.5):
        self.color1 = "steel blue"
        self.color2 = "light sky blue"
        self.color3 = "mint cream"
        self.limit = 0.5
        
class FallingFlake():
    
    def __init__(self, flake, color, rotSpeed, dx, dy):
        self.flake = flake
        self.color = color
        self.rotSpeed = rotSpeed
        self.dx = dx
        self.dy = dy    
        
    def getTransformSettings(self):
        return self.rotSpeed, (self.dx, self.dy)
        
    def getColor(self):
        return self.color
        

   
#randomly select if fl ake slow, med, fast and 
#generates movement settings within range
def flakeTransformSettings():
    speed = random.randint(1,3) # 1=slow 2= medium 3 = fast
    if speed == 1:
        rotSpeed = random.randint(1,3)
        dx = random.randint(-3,3)
        dy = random.randint(abs(dx), 6)
        #make sure dy not 0
        while (dy == 0):
            dy = random.randint(abs(dx), 6)
    elif speed == 2:
        rotSpeed = random.randint(3, 7)
        dx = random.randint(-5, 5)
        dy = random.randint(5, 10)
    else:  #fast
        rotSpeed = random.randint(7, 10)
        dx = random.randint(-7, 7)
        dy = random.randint(7, 12)
    return rotSpeed, dx, dy
        
# based off of events-example0.py from notes

def init(data, canvas):
    data.time = 0
    data.play = True
    data.grad = Gradient(0.5)
    data.mode = "start"
    data.oldMode = None
    data.layers = 25
    data.iterations = 500
    data.pixSize = 2
    data.alpha = 1
    data.generatedFlakes = [] #for memoization
    data.fAuto = None #flake being generated randomly in background
    
    
    ###FOR GENERATE
    data.beta = 0.5
    data.gamma = 0.0005
    data.f = None
    
    ###FOR CATCH
    data.initCatchCount = 5
    data.paramCatchAndSavedFlakes = set()
    data.catchIteration = 0
    #flakes made in background, cannot be on screen, cannot be saved
    data.autoFlakes = [] 
    data.fallDelay = 10
    #data.makeFlake = True

    
    ###FOR SAVE SCREEN
    data.savedFlakes = []
    data.flakesToDraw = []
    data.toSave = False #true when need to save current flake
    data.saveSize = 200
    data.saveRows = (data.height - data.height//9)//data.saveSize
    data.saveCols = data.width//data.saveSize
    data.saveMarX = (data.width  - (data.saveSize * data.saveRows))//2
    data.saveMarY = (data.height - (data.saveSize * data.saveRows))//2
    data.savePgCapacity = data.saveRows * data.saveCols
   
    ###FOR PAINT
    data.menuPages = 1
    data.curMenuPage = 0
    data.paintFlakes = []
    
#whenever return to generate
def initGenerate(data):
    #set generated flake on screen
    if data.f != None:
       data.f.setPosition(data.width//2, data.height//3, 0)
       
#whenever return to catch
def initCatch(data):
    data.catchTimer = 0
    data.f = None
    data.fallingFlakes = [] #will take from autoFlakes
    random.shuffle(data.autoFlakes)

#wheneever return to save pages screen
def initSave(data):
    data.savePages = len(data.savedFlakes) // (data.saveRows * data.saveCols)
    data.curPage = 0
    
#given a flake and data, runs the iterations for the flake    
def generateFlake(flake, data, canvas):
   
    i = 0
    while(i < data.iterations and not flake.edgeReached):
        flake.mainAlgorithm()
        i += 1
        
def mousePressed(event, data):
    if data.mode in ["catch", "paramScreen"]: mousePressedCatch(event, data)
    elif data.mode == "saveScreenPaint": mousePressedSaveScreenPaint(event, data)
    elif data.mode in ["paint","paint-add", "paint-rotate", "paint-del"]:
        mousePressedPaint(event, data)
    
def mousePressedCatch(event, data):
    for fl in data.fallingFlakes:
        #check if click inside flake
        if inPoly(event, fl.flake.boundaryPoints):
            oldCX, oldCY, oldAngle = fl.flake.getPosition()
        
            #move flake to param box
            newCX = data.width//2 - data.saveSize//2 - 10
            newCY = data.height//2
            newAngle = 0
            fl.flake.setPosition(newCX, newCY, newAngle)
            
            #set param to display
            data.pressedFlake =  copy.deepcopy(fl.flake.boundaryPoints)
            data.beta = fl.flake.beta
            data.gamma = fl.flake.gamma
            if fl.flake not in data.savedFlakes:
                data.showSave = True
            
            #revert fl.flake
            fl.flake.setPosition(oldCX, oldCY, oldAngle)
            data.f = fl.flake
            
            #update mode
            data.mode = "paramScreen"

def mousePressedPaint(event, data):
    print(data.mode)
    if data.mode == "paint-add":
        size = data.f.getSize()
        #make sure x and y on screen if moved
        if( event.x > -size and event.x < data.width + size and
            event.y > -size and event.y < data.height*8//9 +size):
                #make a "copy" of flake
                cX, cY = data.f.getGlobalOrigin()
                newF = snowflake.Snowflake(data.pixSize, data.layers, data.alpha,
                                            data.f.beta, data.f.gamma, cX, cY)
                newF.setBoundaryPoints(data.f.boundaryPoints)
                #add "copy" to paint flakes
                data.paintFlakes.append(newF)
                data.mode = "paint"
              
                data.f = None
    #rotate is active
    elif data.mode == "paint-rotate":
        print(len(data.paintFlakes))
        for f in range(len(data.paintFlakes)):
            #check if clicked
            if inPoly(event, data.paintFlakes[f].boundaryPoints):
                txt = "Input integer angle (positive --> CW, negative --> CCW)"
                angle = tkinter.simpledialog.askinteger("Angle Input", txt)
                if angle != None:
                    data.paintFlakes[f].transform(angle) #rotate flake
    #delete is active
    elif data.mode == "paint-del":
        i = 0
        for f in data.paintFlakes:
            if inPoly(event, f.boundaryPoints):
                data.paintFlakes.pop(i) #remove deleted flake
            i += 1
            
def mousePressedSaveScreenPaint(event, data):
    for f in data.flakesToDraw:
        #check if click inside flake
        if inPoly(event, f.boundaryPoints):
            data.f = f
            data.mode = "paint-add"
            
    
    
#########################################################
### from https://stackoverflow.com/questions/30136270/
### checking-if-clicks-are-within-a-graphic-object-python
### -graphics-module  -- modified to be flake compatible
#########################################################


#given event and flake boundary points
#returns true if point in polygon
#comments come from creator
def inPoly(event, points):
    nvert = len(points) #the number of vertices in the polygon

    #get x and y of pt1
    x = event.x
    y = event.y

    # I don't know why this works
    # See the link I provided for details
    result = False
    for i in range(nvert):

        # note: points[-1] will give you the last element
        # convenient!
        j = i - 1

        #get x and y of vertex at index i
        vix = points[i][0]
        viy = points[i][1]

        #get x and y of vertex at index j
        vjx = points[j][0]
        vjy = points[j][1]

        if ((viy > y) != (vjy > y) and 
            (x < (vjx - vix) * (y - viy) / (vjy - viy) + vix)):
                result = not result

    return result
    
def keyPressed(event, data):
    #go to instruct from every screen
    if event.keysym == "i":
        #do not go to instruct if in instruct
        if data.mode != "instruct":
            data.oldMode, data.mode = data.mode, "instruct"
    if data.mode == "paramScreen": keyPressedParamScreen(event, data)
    
#makes so user can exit parameter screen
def keyPressedParamScreen(event, data):
    print(event.keysym)
    if event.keysym == "Escape":
        #reset
        data.f = None
        data.mode = "catch"
    
#given data and size of flake returns a new position for flake
#to start at top of screen 
def randomlyPositionFlake(data, size):
    #randomly get position
    xPos = random.randint(size + 1, data.width - size - 1)
    yPos = - size
    angle = random.randint(0, 30)
    
    return xPos, yPos, angle

def timerFired(data):
    data.time += 1
    
    #if time to make new flake
    if data.fAuto == None:
        beta   = random.uniform(0.45, 0.9) 
        beta  -= beta % 0.001 #formatting
        gamma  = random.uniform(0.000005, 0.001) 
        gamma -= gamma % 0.000001 #formatting
        #ensure new parameters
        #if beta gamma in current set of pre made flakes
        while((beta, gamma) in data.paramCatchAndSavedFlakes):
            beta   = random.uniform(0.45, 0.9)
            bea   -= beta % 0.001
            gamma  = random.uniform(0.000005, 0.001)
            gamm  -= gamma % 0.000001
        #make new flake
        data.fAuto = snowflake.Snowflake( data.pixSize, data.layers, 
                                              data.alpha, beta, gamma, 
                                              data.width/2, data.height/3)
                                              
    #generate 10 iterations
    for i in range(10):
        #see if further generating needed
        if(data.catchIteration < data.iterations and not data.fAuto.edgeReached):
            #generate and increment
            data.fAuto.mainAlgorithm()
            data.catchIteration += 1
        else:
            size = data.fAuto.getGridSize()
            #random location
            xPos, yPos, angle = randomlyPositionFlake(data, size)
            data.fAuto.setPosition(xPos, yPos, angle)
            data.autoFlakes.append(data.fAuto) #ready to use
            data.generatedFlakes.append(data.fAuto) #in universal set
            
            #reset flake generating values
            data.fAuto = None
            data.catchIteration = 0
            break #stop iterating
            
    if data.mode == "catch" or data.mode == "paramScreen":
        timerFiredCatch(data)
        
#checks if  falling flake is off screen
def flakeOffScreen(f, data):
    cX, cY = f.flake.getGlobalOrigin()
    size = f.flake.getGridSize()
    xMax = data.width + size #upper bound
    xMin = -size             #lower bound
    yMax = data.height + size#upper bound
    #check bounds
    if cX > xMax or cX < xMin or cY > yMax:
        return True
    return False
        
#removes falling flake from screen and adds it to
#autoFlakes with new position unless it was saved
#save flakes deleted
def removeFallingFlake(f, data):
    if f.flake not in data.savedFlakes:
        size = f.flake.getGridSize()
        #reset start positon randomly
        xPos, yPos, angle = randomlyPositionFlake(data, size)
        f.flake.setPosition(xPos, yPos, angle)
        #remove flake from current place
        data.fallingFlakes.remove(f)
        
        #insert flake randomly in data.autoFlakes
        i = random.randint(0, len(data.autoFlakes))  
        data.autoFlakes.insert(i, f.flake)
    else: #delete save flakes 
        data.fallingFlakes.remove(f)
        
def timerFiredCatch(data):
    #check if need to/can add flake
    if data.catchTimer % data.fallDelay == 0:
        #check if there are flakes to add
        if len(data.autoFlakes) != 0:
            #append next made flake
            rotSpeed, dx, dy = flakeTransformSettings()
            newFallingFlake = FallingFlake( data.autoFlakes.pop(0),
                                            "white", rotSpeed, dx, dy)
            data.fallingFlakes.append(newFallingFlake)
            #print("added to falling flakes
    data.catchTimer += 1
    
    #transform flakes on screen
    for f in data.fallingFlakes:
        rot, translate = f.getTransformSettings()
        f.flake.transform(rot, translate)
        
        if flakeOffScreen(f, data):
            removeFallingFlake(f, data)
            ### what is this
            if f.flake == data.f:
                data.f = None
                data.mode = "catch"
        
    
#add current flagged (data.f) flake to savedFlakes
def saveFlake(data):
    #make "copy"
    cX, cY = data.f.getGlobalOrigin()
    saveF = snowflake.Snowflake(data.pixSize, data.layers, data.alpha,
                                data.f.beta, data.f.gamma, cX, cY)
    saveF.setBoundaryPoints(data.f.boundaryPoints)
    saveF.transform(-(data.f.angle))
    saveF.redefineAngle(0)
    #add to savedFlake
    data.savedFlakes.append(saveF)
    data.paramCatchAndSavedFlakes.add((data.f.beta, data.f.gamma))
    
def redrawAll(canvas, data):
    canvas.create_rectangle(0,0,data.width, data.height,fill = "SteelBlue1")
    if data.mode == "start": redrawAllStart(canvas,data)
    elif data.mode == "instruct": redrawInstruct(canvas, data)
    elif data.mode == "generate": redrawAllGenerate(canvas, data)
    elif data.mode == "catch": redrawAllCatch(canvas, data)
    elif data.mode == "paramScreen": redrawAllParamScreen(canvas, data)
    elif data.mode in ["saveScreen-generate", "saveScreen-catch"]:
        redrawAllSaveScreen(canvas, data)
    elif data.mode in ["paint","paint-add", "paint-rotate","paint-del"]: 
        redrawAllPaint(canvas, data)
    elif data.mode == "saveScreenPaint": redrawAllSaveScreenPaint(canvas, data)

def redrawAllStart(canvas, data):
    #title and background
    canvas.create_text(  data.width//-1, data.height//3-1, 
                        text = "Welcome to Snowflake Swirl!!!",
                        fill="white", 
                        font="Palatino 45 bold italic",
                        anchor = N)
    canvas.create_text(  data.width//2+1, data.height//3+1, 
                        text = "Welcome to Snowflake Swirl!!!",
                        fill="white", font="Palatino 45 bold italic",
                        anchor = N)
    canvas.create_text(  data.width//2, data.height//3, 
                        text = "Welcome to Snowflake Swirl!!!",
                        fill="midnight blue", font="Palatino 45 bold italic",
                        anchor = N)
 
    #change mode to instruct
    def clickInstruct(*args):
        data.oldMode = "start"
        data.mode = "instruct"
    
    #change mode to generate    
    def clickGenerate(*args):
        data.oldMode = "start"
        data.mode = "generate"
        initGenerate(data)
    
    #change mode to catch    
    def clickCatch(*args):
        initCatch(data)
        data.oldMode = "start"
        data.mode = "catch"
        
    def clickDraw(*args):
        data.oldMode = "start",
        data.mode = "paint"
        
                           
    instructText = canvas.create_text( data.width//2, data.height//2,
                        text = "Instructions",
                        fill = "midnight blue",
                        activefill = "mint cream",
                        font = "Palatino 20 bold",
                        tag = "instructText")
            
    generateText = canvas.create_text( data.width//4, data.height*5//9,
                        text = "Generate",
                        fill = "midnight blue",
                        activefill = "mint cream",
                        font = "Palatino 20 bold",
                        tag = "generateText")
    
                  
            
    catchText = canvas.create_text( data.width//2, data.height*5//9,
                        text = "Catch",
                        fill = "midnight blue",
                        activefill = "mint cream",
                        font = "Palatino 20 bold",
                        tag = "catchText")
                        
    drawText = canvas.create_text( data.width*3//4, data.height*5//9,
                        text = "Draw",
                        fill = "midnight blue",
                        activefill = "mint cream",
                        font = "Palatino 20 bold",
                        tag = "drawText")
                        
    canvas.tag_bind("instructText", "<Button-1>",clickInstruct)
    canvas.tag_bind("generateText", "<Button-1>", clickGenerate)
    canvas.tag_bind("catchText", "<Button-1>", clickCatch)
    canvas.tag_bind("drawText", "<Button-1>", clickDraw)
    
    #tell user to click option
    canvas.create_text( data.width//2, data.height*6//9,
                        text = "Click Option Above",
                        fill = "midnight blue",
                        font = "Palatino 20 bold italic",
                        anchor = N)
    
def redrawInstruct(canvas, data):
    canvas.create_text( data.width//2, data.height//9,
        text = "Press 'i' on any screen to get back to the insctructions",
        font = "Palatino 20 bold",
        fill = "midnight blue",
        anchor = S)
    instructions = """
How it works:
Based on an algorithm by Cliford A. Reiter, there are three parameters that 
define a snowflake: alpha, beta, and gamma coefficients. In Snowflake Swirl you
get to see how the parametes determine the shape of the snowflake.

Generate:
In the Generate mode you can select and change beta and gamma values and click 
the "Generate" button to generate a snowflake. Snowflakes take around 5-6 seconds 
to generate. After generating you can save your snowflake. At any time, you can 
see all the snowflakes you have saved in the app by clicking on the
"See Saved Snowflakes" button.

Catch:
In the Catch mode,  snowflakes are auto generated and fall down the screen. 
You can click on the snowflakes to learn more about their beta or gamma values 
with the option to save them. At anytime you can see all the snowflakes you have
saved in the app by clicking the "See Saved Snowflakes" button. If no snowflakes
are on the screen wait for 5-6 seconds for the computer to generate a new one.

Draw:
In the Draw mode, you can choose from snowflakes you have saved and draw with 
them on a screen. After placed on the screen, they can be rotated and deleted by
clicking "Rotate" or  "Delete" buttons, respectively, and then clicking on the 
snowflake you wish to rotate or delete. To save your image click on the "Export"
button and you will be prompted to a file saving screen.
"""
    canvas.create_text(data.width//2, data.height//2, text = instructions,
                        font = "Palatino 12 bold",
                        fill = "midnight blue",
                        tag = "instructions")

    
    #return to previous screen
    def clickReturn(*args):
        data.oldMode, data.mode = data.mode, data.oldMode
        print(data.mode)
        
                           
    returnText = canvas.create_text( data.width//2, data.height*8//9,
                        text = "Return",
                        fill = "midnight blue",
                        activefill = "mint cream",
                        font = "Palatino 20 bold",
                        anchor = N,
                        tag = "returnText")

    canvas.tag_bind("returnText", "<Button-1>",clickReturn)
    

#return true if input of beta not of right specifications
# 0.45 <= beta <= 0.9 and persion of 0.001
def betaNotValid(beta):
    if beta < 0.45 or beta > 0.9: 
        tkinter.messagebox.showinfo("Beta Out of Range", "Beta must be between 0.45 and 0.9")
        return True
    return False

#return true if input of gamma not of right specifications
#0.000005 <= gamma <= 0.001 and at most 3 non-zero digits
def gammaNotValid(gamma):
    if gamma < 0.000005 or gamma > 0.001:
        tkinter.messagebox.showinfo("Gamma Out of Range", "Gamma must be between 0.000005 and 0.001")
        return True
    return False
    
                        
def redrawAllGenerate(canvas, data):
    
    #return to previous screen
    def clickReturn(*args):
        data.oldMode, data.mode = data.mode, "start"
        if data.mode == "generate":
            initGenerate(data)
        elif data.mode == "catch":
            pass
        elif data.mode == "draw":
            pass
            
    
    goBack = canvas.create_text( data.width/2, data.height*8//9,
                        text = "Return",
                        fill = "midnight blue",
                        activefill = "mint cream",
                        font = "Palatino 20 bold",
                        anchor = N,
                        tag = "returnText")
                        
    canvas.tag_bind("returnText", "<Button-1>", clickReturn)
    
    canvas.create_text( data.width//2,
                        data.height*11//18,
                        text ="  Current Parameters:  ",
                        fill = "midnight blue",
                        font = "Palatino 20 bold",
                        tag = "paramText")
    currentBeta = ("Beta = %0.3f" % (data.beta))
    currentGamma = ("Gamma = %0.7f" % (data.gamma))
    canvas.create_text( data.width//2, data.height*2//3,
                        text = currentBeta,
                        fill = "midnight blue",
                        font = "Palatino 20 bold",
                        tag = "paramText")
    canvas.create_text( data.width//2, data.height*13//18,
                        text = currentGamma,
                        fill = "midnight blue",
                        font = "Palatino 20 bold",
                        tag = "paramText")
                        
    bbox = canvas.bbox("paramText")
    rectItem = canvas.create_rectangle(bbox, outline = "midnightblue", fill = "mint cream")
    canvas.tag_raise("paramText",rectItem)
    
    #save generated flake
    def clickSave(*args):
        saveFlake(data)
    
    if data.f != None and data.gamma == data.f.gamma and data.beta == data.f. beta:
        data.f.drawHex(canvas)
        data.f.transform(2)
        #have option to save if not currently saved
        if data.f not in data.savedFlakes:                
                                                    #y0 of bbox
            save = canvas.create_text(  data.width//2, bbox[1]- 45,
                                        text = "Save Flake",
                                        anchor = S,
                                        fill = "red",
                                        activefill = "mint cream",
                                        font = "Palatino 20 bold",
                                        tag = "saveText")
        
        canvas.tag_bind("saveText", "<Button-1>", clickSave)
        
    #see saved flakes
    def clickSaveScreen(*args):
        initSave(data)
        data.oldMode = "generate"
        data.mode = "saveScreen-generate"
        print("save clicked")
   
    #change beta
    def clickBeta(*args):
        txt = "Input beta value between 0.45 and 0.9:"
        tempbeta = tkinter.simpledialog.askfloat("Beta Input", txt)
        while(tempbeta != None and betaNotValid(tempbeta)):
            tempbeta = tkinter.simpledialog.askfloat("Beta Input", txt)
        if tempbeta != None:
            data.beta = round(tempbeta, 3)
    
    #change famma
    def clickGamma(*args):
        txt = "Input gamma value between 0.000005 and 0.001"
        tempgamma = tkinter.simpledialog.askfloat("Gamma Input", txt)
        while(tempgamma != None and gammaNotValid(tempgamma)):
            tempgamma = tkinter.simpledialog.askfloat("Gamma Input", txt)
        if tempgamma != None:
            data.gamma = round(tempgamma, 7)
        
    #generate flake
    def clickGenerate(*args):
        #if f is empty and parameters changed
        if (data.f == None   
            or data.beta != data.f.beta 
            or data.gamma != data.f.gamma):
                data.f = snowflake.Snowflake( data.pixSize, data.layers, 
                                              data.alpha, data.beta, data.gamma, 
                                              data.width/2, data.height/3)
                if data.f in data.generatedFlakes:
                    data.f = data.generatedFlakes[data.generatedFlakes.index(data.f)]
                    data.f.setPosition(data.width/2, data.height/3, 0)
                else:
        #canvas.create_text(data.width//2, data.height//3,
        #                    text = "Generating...",
        #                    font = "Palatino 25 bold italic",
        #                    fill = "midnight blue")
                    generateFlake(data.f, data, canvas)
                    data.generatedFlakes.append(data.f)
        
    beta = canvas.create_text( data.width//3, data.height*7//9,
                        text = "Change Beta",
                        fill = "midnight blue",
                        activefill = "mint cream",
                        font = "Palatino 20 bold",
                        anchor = E,
                        tag = "betaText")
                        
    canvas.tag_bind("betaText", "<Button-1>",clickBeta)
            
    gamma = canvas.create_text( data.width/2, data.height*7//9,
                        text = "Change Gamma",
                        fill = "midnight blue",
                        activefill = "mint cream",
                        font = "Palatino 20 bold",
                        tag = "gammaText")
    
    canvas.tag_bind("gammaText", "<Button-1>", clickGamma)
    
                  
           
    catchText = canvas.create_text( data.width*2//3, data.height*7//9,
                        text = "Generate",
                        fill = "midnight blue",
                        activefill = "mint cream",
                        font = "Palatino 20 bold",
                        anchor = W,
                        tag = "generateText")
    
    canvas.tag_bind("generateText", "<Button-1>", clickGenerate)
    
    saveScreenText = canvas.create_text(data.width//2, bbox[1]- 15,
                                        text = "See Saved Snowflakes",
                                        fill = "midnight blue",
                                        activefill = "mint cream",
                                        font = "Palatino 20 bold italic",
                                        anchor = S,
                                        tag = "saveScreenText")
                                        
    canvas.tag_bind("saveScreenText", "<Button-1>", clickSaveScreen)
    
def redrawAllParamScreen(canvas, data):
    redrawAllCatch(canvas,data)
    
    #escape option
    canvas.create_text( data.width//2, data.height*2//3,
                        text = "Press 'Esc' to Exit",
                        fill = "red",
                        font = "Palatino 20 bold",
                        anchor = N)
    margin = 10
    
    #show beta/gamma params
    canvas.create_text( data.width//2,
                        data.height*8//18,
                        text ="Current Parameters:",
                        fill = "midnight blue",
                        font = "Palatino 20 bold",
                        tag = "param")
    currentBeta = ("Beta = %0.3f" % (data.beta))
    currentGamma = ("Gamma = %0.7f" % (data.gamma))
    canvas.create_text( data.width//2, data.height*1//2,
                        text = currentBeta,
                        fill = "midnight blue",
                        font = "Palatino 20 bold",
                        tag = "param")
    canvas.create_text( data.width//2, data.height*10//18,
                        text = currentGamma,
                        fill = "midnight blue",
                        font = "Palatino 20 bold",
                        tag = "param")
    
    #box around param text                    
    bbox = canvas.bbox("param")
    x0 = bbox[0] - margin
    y0 = bbox[1] - margin
    x1 = bbox[2] + margin
    y1 = bbox[3] + margin
    rectItem = canvas.create_rectangle( x0, y0, x1, y1,
                                        outline = "midnightblue", 
                                        fill = "mint cream")
    canvas.tag_raise("param",rectItem)
    
    #save data.f flake
    def clickSave(*args):
        saveFlake(data)
        data.showSave = False
        print("save clicked")
    #if snowflake isnt save show option to save
    if data.showSave:
                                                #y0 of bbox
        save = canvas.create_text(  data.width//2, bbox[1]- 45,
                                    text = "Save Flake",
                                    anchor = S,
                                    fill = "red",
                                    activefill = "mint cream",
                                    font = "Palatino 20 bold",
                                    tag = "saveText")
    
    canvas.tag_bind("saveText", "<Button-1>", clickSave)

#given flake draws it on screen with hover ability
def drawFallingFlake(canvas, f):
    
    canvas.create_polygon(  f.flake.boundaryPoints, 
                            fill = f.color,
                            outline = "SteelBlue1",
                            activefill = "snow3",
                            activeoutline = "snow3")
                            
    
def redrawAllCatch(canvas, data):
    #draw flakes in data.fallingFlakes
    for f in data.fallingFlakes:
        #no param chosen
        if data.f == None:
             drawFallingFlake(canvas, f)
        #param chosen
        else:
            #draw non-param
            if f.flake != data.f:
                canvas.create_polygon(  f.flake.boundaryPoints,
                                    fill = "white",
                                    activefill = "snow3")
            #draw param
            else:
                canvas.create_polygon(  f.flake.boundaryPoints,
                                    fill = "snow3",
                                    outline = "midnightblue")
    #returns to main menu
    def clickReturn(*args):
        data.oldMode, data.mode = data.mode, "start"
        #reset
        data.f = None
        data.beta = 0.5
        data.gamma = 0.0005
        
        
    #see saved flakes        
    def clickSaveScreen(*args):
        initSave(data)
        data.oldMode = "generate"
        data.mode = "saveScreen-catch"
        print("save clicked")
    
    saveScreenText = canvas.create_text(data.width//2, data.height*15//18,
                                        text = "See Saved Snowflakes",
                                        fill = "midnight blue",
                                        activefill = "mint cream",
                                        font = "Palatino 20 bold italic",
                                        anchor = N,
                                        tag = "saveScreenText")
                                        
                                        
    canvas.tag_bind("saveScreenText", "<Button-1>", clickSaveScreen)
    
    goBack = canvas.create_text( data.width/2, data.height*8//9,
                            text = "Return",
                            fill = "midnight blue",
                            activefill = "mint cream",
                            font = "Palatino 20 bold",
                            anchor = N,
                            tag = "returnText")
                            
    canvas.tag_bind("returnText", "<Button-1>", clickReturn)
    
    
def redrawAllSaveScreen(canvas, data):
    canvas.create_rectangle(0,0, data.width, data.height, 
                            fill = "gold", width = 0)
    
    #return to previous page
    def clickReturn(*args):
        data.mode = data.mode[data.mode.find("-")+1:]
        print(data.mode)
        if data.mode == "generate":
            initGenerate(data)
        if data.mode == "catch":
            data.f = None
            print(data.f)
    
    goBack = canvas.create_text( data.width/2, data.height*8//9,
                        text = "Return ",
                        fill = "midnight blue",
                        activefill = "mint cream",
                        font = "Palatino 20 bold",
                        anchor = N,
                        tag = "returnText")
    canvas.tag_bind("returnText", "<Button-1>", clickReturn)
                         
    margin = 125
    topY = data.height//2 - margin
    bottomY = data.height//2 + margin
    
    #done saving
    if(data.toSave == False):
        #calculate start indices
        #inclusive index
        startFlake = data.curPage * data.savePgCapacity
        if data.curPage == data.savePages:
            #display last page
            data.flakesToDraw = data.savedFlakes[startFlake:]                
        else:
            #exclusive index
            endFlake  = startFlake + data.savePgCapacity
            #display interval of snowflakes for current page
            data.flakesToDraw =  copy.deepcopy(data.savedFlakes[startFlake:endFlake])
        countFlakes = len(data.flakesToDraw)
        row = 0
        col = 0   
        #drawFlakes
        i = 0
        while(i < countFlakes):
            cY= (row + 1/2)* data.saveSize
            cX = (col + 1/2)* data.saveSize
            #update col
            col = (col + 1) % data.saveCols
            #update row if reached end of cols
            if col == 0:
                row = row + 1
            #update position if not in right position
            if (cX, cY,0) != data.flakesToDraw[i].getPosition:
                data.flakesToDraw[i].setPosition(cX, cY, 0)
                        
            canvas.create_polygon(data.flakesToDraw[i].boundaryPoints,
                                    fill = "white")
                                    
            #snowflake beta/gamma label underneath
            beta, gamma = data.flakesToDraw[i].beta, data.flakesToDraw[i].gamma
            txt = ("β: %0.3f\nγ:%0.7f" % (beta, gamma))
            canvas.create_text(cX - data.saveSize//4, cY + data.saveSize*5//12,
                                text = txt,
                                fill = "midnight blue",
                                font = "Palatino 15 bold",
                                anchor = NW)
            i += 1
    #if no saved flakes show message       
    if(len(data.savedFlakes)==0):
        canvas.create_text( data.width//2, data.height//2,
                            text = "Looks like you haven't saved any snowflakes...",
                            font = "Palatino 35 bold italic",
                            fill = "midnight blue")
    #turn to next page
    def clickNextPage(*args):
        data.curPage += 1
            
    #show right button on all but last page
    if data.curPage < data.savePages:
        right = canvas.create_text( data.width - margin, data.height*8//9,
                                    text = ">>>",
                                    fill = "midnight blue",
                                    font = "Palatino 20 bold",
                                    activefill = "mint cream",
                                    tag = "nextPage",
                                    anchor = NE)
    
        canvas.tag_bind("nextPage", "<Button-1>", clickNextPage)
    
    #turn to previous page        
    def clickPrevPage(*args):
        data.curPage -= 1
            
    #show right button on all but 0th page
    if data.curPage > 0:
        left = canvas.create_text(  margin, data.height*8//9,
                                    text = "<<<",
                                    fill = "midnight blue",
                                    font = "Palatino 20 bold",
                                    activefill = "mint cream",
                                    tag = "prevPage",
                                    anchor = NW)
    
        canvas.tag_bind("prevPage", "<Button-1>", clickPrevPage)
        
def redrawAllSaveScreenPaint(canvas, data):
    canvas.create_rectangle(0,0, data.width, data.height, 
                            fill = "gold", width = 0)
    
    #go to previous screen
    def clickReturn(*args):
        data.oldMode, data.mode = data.mode, "paint"
            
    goBack = canvas.create_text( data.width/2, data.height*8//9,
                        text = "Return",
                        fill = "midnight blue",
                        activefill = "mint cream",
                        font = "Palatino 20 bold",
                        anchor = N,
                        tag = "returnText")
    canvas.tag_bind("returnText", "<Button-1>", clickReturn)
                         
    margin = 125
    topY = data.height//2 - margin
    bottomY = data.height//2 + margin
    
    #if done saving
    if(data.toSave == False):
        #calculate start indices
        #inclusive index
        startFlake = data.curPage * data.savePgCapacity
        if data.curPage == data.savePages:
            #display last page
            data.flakesToDraw = data.savedFlakes[startFlake:]                
        else:
            #exclusive index
            endFlake  = startFlake + data.savePgCapacity
            #display interval of snowflakes for current page
            data.flakesToDraw =  data.savedFlakes[startFlake:endFlake]
        countFlakes = len(data.flakesToDraw)
        row = 0
        col = 0   
        #drawFlakes
        i = 0
        while(i < countFlakes):
            cY= (row + 1/2)* data.saveSize
            cX = (col + 1/2)* data.saveSize
            #update col
            col = (col + 1) % data.saveCols
            #update row if reached end of cols
            if col == 0:
                row = row + 1
            #update position if not in right position
            if (cX, cY,0) != data.flakesToDraw[i].getPosition:
                data.flakesToDraw[i].setPosition(cX, cY, 0)
                        
            canvas.create_polygon(data.flakesToDraw[i].boundaryPoints,
                                fill = "white",
                                activefill = "snow3")
            #snowflake beta/gamma label underneath
            beta, gamma = data.flakesToDraw[i].beta, data.flakesToDraw[i].gamma
            txt = ("β: %0.3f\nγ:%0.7f" % (beta, gamma))
            canvas.create_text(cX - data.saveSize//4, cY + data.saveSize*5//12,
                                text = txt,
                                fill = "midnight blue",
                                font = "Palatino 15 bold",
                                anchor = NW)
            
            i += 1
    #if empty show message
    if(len(data.savedFlakes)==0):
        canvas.create_text( data.width//2, data.height//2,
                            text = "Looks like you haven't saved any snowflakes...",
                            font = "Palatino 35 bold italic",
                            fill = "midnight blue")
    #turn to next page
    def clickNextPage(*args):
        data.curPage += 1
            
    #show right button on all but last page
    if data.curPage < data.savePages:
        right = canvas.create_text( data.width - margin, data.height*8//9,
                                    text = ">>>",
                                    fill = "midnight blue",
                                    font = "Palatino 20 bold",
                                    activefill = "mint cream",
                                    tag = "nextPage",
                                    anchor = NE)
    
        canvas.tag_bind("nextPage", "<Button-1>", clickNextPage)
    #turn to previous page        
    def clickPrevPage(*args):
        data.curPage -= 1
            
    #show right button on all but 0th page
    if data.curPage > 0:
        left = canvas.create_text(  margin, data.height*8//9,
                                    text = "<<<",
                                    fill = "midnight blue",
                                    font = "Palatino 20 bold",
                                    activefill = "mint cream",
                                    tag = "prevPage",
                                    anchor = NW)
    
        canvas.tag_bind("prevPage", "<Button-1>", clickPrevPage)
    
    
def redrawAllPaint(canvas, data):
    
    for f in data.paintFlakes:
        #flake in modification
        if (data.mode == "paint-rotate" and data.f != None
            and f.getGlobalOrigin() == data.f.getGlobalOrigin()):
            #use global origin because flake == returns true based on beta gamma
                canvas.create_polygon(  f.boundaryPoints,
                                        fill = "snow4") #darkest and no active
        #hovering mode
        elif data.mode in ["paint-rotate", "paint-del"]:
            canvas.create_polygon(  f.boundaryPoints,
                                    fill = "white", outline = "SteelBlue1",
                                    activefill = "snow3", activeoutline = "")
        #non-hovering mode
        else:
            canvas.create_polygon(  f.boundaryPoints,
                                    fill = "white", outline = "SteelBlue1")
        
    #adding flake
    if data.mode == "paint-add":
        #orientation is at right position because either at 0 from
        #save screen or user-set position
        size = data.f.getGridSize()
        
        ######################################################
        ###from https://stackoverflow.com/questions/44534868/
        ###tkinter-widget-to-follow-mouse-movement
        ######################################################
        #have flake follow mouse until presse
        cX = canvas.winfo_pointerx() - canvas.winfo_rootx()
        cY=canvas.winfo_pointery() - canvas.winfo_rooty()
        #make sure flake on screen if moved
        if( cX > 0 and cX < (data.width) and
            cY > 0 and cY < (data.height*8//9)):
            data.f.setPosition(cX, cY)
        canvas.create_polygon(  data.f.boundaryPoints,
                                fill = "white", outline = "SteelBlue1")
                                
    
    canvas.create_rectangle(0, data.height*8//9, data.width, data.height,
                            fill = "NavajoWhite2",
                            width = 0)
    margin = 125
    
    #return to previous screen
    def clickReturn(*args):
        data.oldMode, data.mode = data.mode, "start"
    
    #add a flake
    def clickAdd(*args):
        initSave(data)
        data.mode = "saveScreenPaint"
        
    #delete a flake    
    def clickDelete(*args):
        if data.paintFlakes == []:
            tkinter.messagebox.showinfo("No Flakes On Screen", "You must add flakes first!")
        else:
            data.mode = "paint-del"
    
    #export drawing
    def clickExport(*args):
        #######################################################################
        ### from https://stackoverflow.com/questions/34777676/how-to-convert-a-
        ### python-tkinter-canvas-postscript-file-to-an-image-file-readable
        #######################################################################
        data.path = tkinter.filedialog.asksaveasfilename(initialdir = "/",
            title = "Select file",defaultextension = ".png")
        if (data.path != ""):
            margin = 50
            #save as postscript through Ghostscript
            ps = canvas.postscript(colormode='color',
                width = data.width, height = data.height*8//9-1)
            #convert to png
            img = Image.open(io.BytesIO(ps.encode('utf-8')))
            img.save(data.path)
            
    #rotate is active
    def clickRotate(*args):
        if data.paintFlakes == []:
            tkinter.messagebox.showinfo("No Flakes On Screen", "You must add flakes first!")
        else:
            data.mode = "paint-rotate"
            
    canvas.create_text( data.width//2, data.height*35/36,
                        text = "Return",
                        fill = "midnight blue",
                        font = "Palatino 20 bold",
                        activefill = "mint cream",
                        tag = "return")
    canvas.tag_bind("return", "<Button-1>", clickReturn)
        
    canvas.create_text( data.width//8, data.height*17//18,
                        text = "Add",
                        fill = "midnight blue",
                        font = "Palatino 20 bold",
                        activefill = "mint cream",
                        anchor = S,
                        tag = "add")
    canvas.tag_bind("add", "<Button-1>", clickAdd)
    #keep rotate highlighted when rotating
    if data.mode == "paint-rotate":
        rotateColor = "mint cream"
    else:
        rotateColor = "midnight blue"
    canvas.create_text( data.width*3//8, data.height*17//18,
                        text = "Rotate",
                        fill = rotateColor,
                        font = "Palatino 20 bold",
                        activefill = "mintcream",
                        anchor = S,
                        tag = "rotate")
    canvas.tag_bind("rotate", "<Button-1>", clickRotate)
    #keep delete highlighted while deleting
    if data.mode == "paint-del":
        delColor = "mint cream"
    else:
        delColor = "midnight blue"
    canvas.create_text( data.width*5//8, data.height*17//18,
                        text = "Delete",
                        fill = delColor,
                        font = "Palatino 20 bold",
                        activefill = "mintcream",
                        anchor = S,
                        tag = "delete")
    canvas.tag_bind("delete", "<Button-1>", clickDelete)
    canvas.create_text( data.width*7//8, data.height*17//18,
                        text = "Export",
                        fill = "midnight blue",
                        font = "Palatino 20 bold",
                        activefill = "mintcream",
                        anchor = S,
                        tag = "export")
    canvas.tag_bind("export", "<Button-1>", clickExport)
    
####################################
# use the run function as-is
####################################

def run(width=300, height = 400):
    def redrawAllWrapper(canvas, data):
        canvas.delete(ALL)
        canvas.create_rectangle(0, 0, data.width, data.height,
                                fill='white', width=0)
        redrawAll(canvas, data)
        canvas.update()    

    def mousePressedWrapper(event, canvas, data):
        mousePressed(event, data)
        redrawAllWrapper(canvas, data)

    def keyPressedWrapper(event, canvas, data):
        keyPressed(event, data)
        redrawAllWrapper(canvas, data)

    def timerFiredWrapper(canvas, data):
        timerFired(data)
        redrawAllWrapper(canvas, data)
        # pause, then call timerFired again
        canvas.after(data.timerDelay, timerFiredWrapper, canvas, data)
    # Set up data and call init
    class Struct(object): pass
    data = Struct()
    data.width = width
    data.timerDelay = 1 # milliseconds
    
    # create the root and the canvas
    root = Tk()
    if height > (root.winfo_screenheight() - 75):
        height = root.winfo_screenheight() - 75
    data.height = height
    #####################################################
    ###from https://stackoverflow.com/questions/14910858/
    ###how-to-specify-where-a-tkinter-window-opens
    #####################################################
    
    # get screen width and height
    ws = root.winfo_screenwidth() # width of the screen
    hs = root.winfo_screenheight() # height of the screen
    
    # calculate x and y coordinates for the Tk root window
    data.x0 = (ws/2) - (width/2)
    data.y0 = 0
    data.x1 = data.x0 + width
    data.y1 = data.y0 + height
    root.geometry('%dx%d+%d+%d' % (width, height, data.x0, 0))
    canvas = Canvas(root, width=data.width, height=data.height)
    canvas.pack()
    init(data, canvas)
    # set up events
    root.bind("<Button-1>", lambda event:
                            mousePressedWrapper(event, canvas, data))
    root.bind("<Key>", lambda event:
                            keyPressedWrapper(event, canvas, data))
    timerFiredWrapper(canvas, data)
    # and launch the app
    root.mainloop()  # blocks until window is closed
    print("bye!")

run(1000, 1000)