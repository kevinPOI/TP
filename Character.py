from cmu_112_graphics_mod import *
import math
from PhysicalObjects import *
import sys
from playsound import playsound
import time
import random
import pygame

def inDrawRange(y,app):
    if y > app.ff.cy - app.height / 2:
        if y < app.ff.cy + app.height / 2:
            return True
    return False
class Character(object):
    def __init__(self):
        self.charStatus, self.charHeadingLeft = 'idle', False
        self.pointerF = self.pointerR = self.pointerI = 0
        self.charF, self.charR, self.charI = [], [], []
        self.cx, self.cy, self.dx, self.dy = 480, 50, 0, 0
        self.tickCount = 0
        self.onGround = False
        self.loadResources()
        self.hp = 100
        self.isSliding = False
        self.ammoCount = 30
        self.outOfFiringArc = False
        self.launcherOutOfFiringArc = False
        self.standingOn = (0, 0)
        self.grenadeCount = 5
        self.regen = 0
        self.dmg = 10
        pygame.mixer.init()
        self.fireSound = pygame.mixer.Sound("fire.wav")
    def loadResources(self):
        fFrame, rFrame, iFrame = 5, 13, 11
        self.charSize = (80,120)
        for i in range (0, fFrame):
            self.charF.append(Image.open(f"Characters/45F{i}.png"))
            self.charF[i] = self.charF[i].resize(self.charSize)
        for i in range (0, rFrame):
            self.charR.append(Image.open(f"Characters/45R{i}.png"))
            self.charR[i] = self.charR[i].resize(self.charSize)
        for i in range (0, iFrame):
            self.charI.append(Image.open(f"Characters/45I{i}.png"))
            self.charI[i] = self.charI[i].resize(self.charSize)     
    def move(self):
        self.cx += self.dx
        self.cy += self.dy
    def fire(self, app, ang):
        if self.tickCount == 0 and self.ammoCount > 0:
            self.fireSound.play()
            self.ammoCount -= 1
            if self.charHeadingLeft:
                app.projectiles.append(Bullet(self.cx, self.cy, math.pi + ang, app))
            else:
                app.projectiles.append(Bullet(self.cx, self.cy, ang, app))
        self.tickCount += 1
        if self.tickCount > 6:#rof control (7 frames per shot)
            self.tickCount = 0
    def launch(self, app, ang):
        if self.grenadeCount > 0:
            self.grenadeCount -= 1
            if self.charHeadingLeft:
                app.projectiles.append(Grenade(self.cx, self.cy, math.pi + ang, app))
            else:
                app.projectiles.append(Grenade(self.cx, self.cy, ang, app))
    def drawChar(self, app, canvas):
        if app.ff.charStatus == 'fire':
            if app.ff.charHeadingLeft:
                leftChar = app.ff.charF[app.ff.pointerF].transpose(Image.FLIP_LEFT_RIGHT)
                im_tk = ImageTk.PhotoImage(leftChar)
            else:
                im_tk = ImageTk.PhotoImage(app.ff.charF[app.ff.pointerF])
        elif app.ff.charStatus == 'run':
            if app.ff.charHeadingLeft:
                leftChar = app.ff.charR[app.ff.pointerR].transpose(Image.FLIP_LEFT_RIGHT)
                im_tk = ImageTk.PhotoImage(leftChar)
            else:
                im_tk = ImageTk.PhotoImage(app.ff.charR[app.ff.pointerR])
        else:
            if app.ff.charHeadingLeft:
                leftChar = app.ff.charI[app.ff.pointerI].transpose(Image.FLIP_LEFT_RIGHT)
                im_tk = ImageTk.PhotoImage(leftChar)
            else:
                im_tk = ImageTk.PhotoImage(app.ff.charI[app.ff.pointerI])
        canvas.create_image(app.ff.cx, app.height/2, image = im_tk)
    def nextCharFrame(self):#update pointers pointing to the next frame of char
        fFrame, rFrame, iFrame = 5, 13, 11
        self.pointerF += 1
        if self.pointerR % 2 == 0:
            self.pointerI += 1
        self.pointerR += 1
        if self.pointerF >= fFrame:
            self.pointerF = 0
        if self.pointerI >= iFrame:
            self.pointerI = 0
        if self.pointerR >= rFrame:
            self.pointerR = 0
    def drawStats(self, app, canvas):
        canvas.create_text(app.width / 2, app.height * 0.95, 
        text = f"HP: {self.hp} / 100", font = "Arial 16 bold")
        if self.ammoCount <= 0:
            canvas.create_text(app.width * 0.5, app.height * 0.75,
            text = "Out Of Ammo", font = "Arial 24 bold", fill  = "red")
        elif self.outOfFiringArc:
            canvas.create_text(app.width * 0.5, app.height * 0.75,
            text = "Main Weapon Out Of Firing Arc", font = "Arial 24 bold", fill  = "red")
        if self.grenadeCount <= 0:
            canvas.create_text(app.width * 0.5, app.height * 0.82,
            text = "Out Of Grenades", font = "Arial 24 bold", fill  = "red")
        elif self.launcherOutOfFiringArc:
            canvas.create_text(app.width * 0.5, app.height * 0.82,
            text = "Grenade Launcher Out Of Firing Arc", font = "Arial 20 bold", fill  = "orange")
        
        
        canvas.create_text(app.width / 6, app.height * 0.95, 
        text = f"Ammo: {self.ammoCount}\nGrenades: {self.grenadeCount}", font = "Arial 14 bold")
        if app.chaser.y < self.cy - app.height / 2:
            canvas.create_text(app.width * 0.5, app.height * 0.05,
            text = str(int(self.cy - app.chaser.y)) + "m", font = "Arial 20", fill  = "orange")
        canvas.create_text(app.width * 0.85, app.height * 0.05, text = "Score:"
        + str(int(self.cy)) + "m", font = "Arial 14 bold")