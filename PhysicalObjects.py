from cmu_112_graphics_mod import *
import math
import pygame
import time
import random
def inDrawRange(y,app):
    if y > app.ff.cy - app.height / 2:
        if y < app.ff.cy + app.height / 2:
            return True
    return False
class Wall(object):
    w = 10
    def __init__(self, x, y, r, ang):
        self.x = x
        self.y = y
        self.r = r
    def collisionY(self, cx, r):
        if self.ang > 0:
            cx -= r
        else:
            cx += r
        colY = self.y + (cx - self.x) * math.sin(self.ang)
        return colY    
    def drawWall(self, app, canvas):
        canvas.create_line(self.x - w, relativeY(app, self.y - r),
         self.x - w, relativeY(app, self.y + r), width = self.w * 1.5)
def relativeY(app, y):#convert y for drawing
    diff = y - app.ff.cy  
    return app.height / 2 + diff
class Platform(object):
    h = 10
    def __init__(self, x, y, r, ang):
        self.x = x
        self.y = y
        self.r = r
        self.ang = ang
        self.x0, self.x1 = x - r * math.cos(ang), x + r * math.cos(ang)
        self.y0, self.y1 = y - r * math.sin(ang), y + r * math.sin(ang)
        '''
        maxi = max(self.y0, self.y1)
        if maxi != self.y1:
            self.ang = -self.ang
        mini = min(self.y0, self.y1)
        self.y0, self.y1 = mini, maxi
        '''
    def collisionY(self, cx, r):
        if self.ang > 0:
            cx -= r
        else:
            cx += r
        colY = self.y + (cx - self.x) * math.sin(self.ang)
        return colY    
    def drawPlatform(self, app, canvas):
        adj = 8
        canvas.create_line(self.x0, relativeY(app, self.y0) + adj,
         self.x1, relativeY(app, self.y1) + adj, width = self.h * 1.5)

class IcePlatform(Platform):
    def __init__(self, x, y, r, ang):
        super().__init__(x, y, r, ang)
        self.hp = 3
    def drawPlatform(self, app, canvas):
        adj = 8
        canvas.create_line(self.x0, relativeY(app, self.y0) + adj,
         self.x1, relativeY(app, self.y1) + adj, width = self.h * 1.5, fill = 'cyan')
class Projectile(object):
    def __init__(self, x, y, ang):
        self.x = x
        self.y = y
        self.ang = ang
        self.remove = False
        
        self.reflectionAble = True
    def move(self, app):
        self.x += self.dx
        self.y += self.dy
        self.dy += 2
        if self.x > app.width or self.x < 0:
            self.dx *= -1
        self.reflectPlat(app)
        #self.reflectWall(app)
        if relativeY(app, self.y) > app.height * 1.5 or self.hp <= 0:
            self.remove = True
    def reflectPlat(self, app):
        if self.reflectionAble:
            i = 0
            while i < len(app.platforms):
                platform = app.platforms[i]
                if inDrawRange(platform.y, app):
                    y0 = min(platform.y0, platform.y1)
                    y1 = max(platform.y0, platform.y1)
                    if ((self.x > platform.x0 and self.x < platform.x1) or
                    (self.x > platform.x1 and self.x + self.dx < platform.x1)or
                    (self.x < platform.x0 and self.x + self.dx > platform.x0)):
                        if ((self.y > y0 and self.y < platform.y1) or
                        (self.y > platform.y and self.y + self.dy < platform.y) or
                        (self.y < platform.y and self.y + self.dy > platform.y)):
                            if self.dx > 0:
                                self.y += self.dy / 2
                                self.x += self.dx / 2
                                self.dy *= - 1 - math.sin(platform.ang)
                                self.dx -= 2 * self.dx * abs(math.sin(platform.ang))
                                self.hp -= 1
                            #self.dx *= math.cos(platform.ang)
                            else:
                                self.y += self.dy / 2
                                self.x += self.dx / 2
                                self.dy *= - 1 + math.sin(platform.ang)
                                self.dx += 2 * self.dx * abs(math.sin(platform.ang))
                                self.hp -= 1
                            if type(platform) == IcePlatform:
                                platform.hp -= 1
                                if platform.hp == 0:
                                    app.platforms.pop(i)
                                    i -= 1
                            self.reflectionAble = False
                i += 1
        else:
            self.reflectionAble = True  
    
class Bullet(Projectile):
    def __init__(self, x, y, ang, app):
        super().__init__(x, y, ang)
        self.r = 4
        v = 50
        self.dx = v * math.cos(self.ang)
        self.dy = v * math.sin(self.ang)
        self.hp = 3
        self.dmg = 1 * app.ff.dmg
    def drawBullet(self, app, canvas):
        canvas.create_rectangle(self.x -self.r, relativeY(app, self.y) - 1, 
        self.x + self.r, relativeY(app, self.y) + 1)
class Grenade(Projectile):
    def __init__(self, x, y, ang, app):
        super().__init__(x, y, ang)
        self.r = 5
        v = 30
        self.dx = v * math.cos(self.ang)
        self.dy = v * math.sin(self.ang)
        self.hp = 5
        self.explode = False
        self.explodeCounter = 0
        self.dmg = 2 * app.ff.dmg
        self.explosion = Image.open("explosion.png")
        pygame.mixer.init()
        self.sound = pygame.mixer.Sound("explosionEffect.wav")
    def drawBullet(self, app, canvas):
        canvas.create_rectangle(self.x - self.r *2, relativeY(app, self.y) - self.r, 
        self.x + self.r * 2, relativeY(app, self.y) + self.r, fill = "gray")
        if self.explode:
            explosion = self.explosion.resize((self.explodeCounter*20 + 20, self.explodeCounter*20 + 20))
            im = ImageTk.PhotoImage(explosion)
            canvas.create_image(self.x, relativeY(app, self.y), image = im)
    def detonate(self, app):
        self.sound.play()
        for i in range (0, 20):
            ang = math.pi * 2 / 24 * i
            app.projectiles.append(Shrapnel(self.x, self.y, ang, app))
class Shrapnel(Projectile):
    def __init__(self, x, y, ang, app):
        super().__init__(x, y, ang)
        self.r = 5
        v = 30
        self.dx = v * math.cos(self.ang)
        self.dy = v * math.sin(self.ang)
        self.hp = 2
        self.dmg = 0.7 * app.ff.dmg
    def drawBullet(self, app, canvas):
        canvas.create_rectangle(self.x -1, relativeY(app, self.y) - 1, 
        self.x + 1, relativeY(app, self.y) + 1)
class Chaser(object):
    def __init__(self):
        self.y = 0
        self.dy = 0.20
    def move(self, app):
        self.y += self.dy
        self.dy += 0.0006 * self.y ** 0.15
        if self.y > app.ff.cy:
            app.gameStatus = 'over'
            if app.ff.cy > app.bestScore:
                app.bestScore = int(app.ff.cy)
    def drawChaser(self, app, canvas):
        canvas.create_line(0, relativeY(app, self.y), app.width, 
        relativeY(app, self.y), width = 4, fill = "red")
class Enemy(object):
    def __init__(self, x, y):
        self.hp = 40
        self.x = x
        self.y = y
        self.r = 40
        self.remove = False
        self.image = Image.open("enemy.png")
        self.image = self.image.resize((120,90))
        
    def drawEnemy(self, app, canvas):
        if inDrawRange(self.y, app):
            canvas.create_rectangle(0, relativeY(app, self.y) + 2,
            app.width, relativeY(app, self.y) - 2, fill = 'red')
            
            im = ImageTk.PhotoImage(self.image)
            canvas.create_image(self.x, relativeY(app, self.y), image = im)
            canvas.create_line(self.x - self.r, relativeY(app, self.y) - self.r * 1.5,
            self.x - self.r + self.hp * self.r / 20, relativeY(app, self.y) - self.r * 1.5,
            width = 2, fill = 'red')
        
    def checkCollide(self, app):
        i = 0
        while i < len(app.projectiles):
            if app.projectiles[i].x > self.x - self.r:
                if app.projectiles[i]. x < self.x + self.r:
                    if app.projectiles[i].y > self.y - self.r:
                        if app.projectiles[i].y < self.y + self.r:
                            self.hp -= app.projectiles[i].dmg
                            app.projectiles.pop(i)
                            i -= 1
            i += 1
        if self.hp <= 0:
            self.remove = True
            app.ff.ammoCount += 4
            app.ff.hp += app.ff.regen
        if not self.remove and self.y < app.ff.cy + 50 and type(self) != Bot:
            app.ff.hp -= 50
            self.remove = True
            if app.ff.hp <= 0:
                app.gameStatus = 'over'
                if app.ff.cy > app.bestScore:
                    app.bestScore = int(app.ff.cy)
class Bot(Enemy):
    def __init__(self, x, y):
        super().__init__(x,y)
        self.dy = 0
        self.dx = 5
        self.direction = 1
        self.isJumping = False
        self.jx, self.jy = 0, 0
        self.firstStep = (0, 0)
        self.counter = 0
        self.lastTarget = (0, 0)
        self.target = (0, 0)
        self.activated = False
        self.explode = False
        self.explodePointer = 1
        self.hp = 20
        self.explosion = Image.open("explosion.png")
        self.image = Image.open("bot.png")
        self.image = self.image.resize((100,80))
        pygame.mixer.init()
        self.sound = pygame.mixer.Sound("explosionEffect.wav")
    def drawEnemy(self, app, canvas):
        
        if inDrawRange(self.y, app):
            im = ImageTk.PhotoImage(self.image)
            canvas.create_image(self.x, relativeY(app, self.y), image = im)
            canvas.create_line(self.x - self.r, relativeY(app, self.y) - self.r * 1.5,
                self.x - self.r + self.hp * self.r / 20, relativeY(app, self.y) - self.r * 1.5,
                width = 2, fill = 'red')
            #canvas.create_text(self.x, self.y - self.r, text = f"{self.x},{self.y}")
            if self.explode:
                r = self.explodePointer * self.r * 1.8
                explosion = self.explosion.resize((int(r),int(r)))
                im = ImageTk.PhotoImage(explosion)
                canvas.create_image(self.x, relativeY(app, self.y), image = im)
    def onPlatform(self, app):#if char stands on platforms
        for platform in app.platforms:
            r = self.r
            if self.x + r/3 > platform.x0:
                if self.x - r/3 < platform.x1:
                    if self.y + self.r / 2 > platform.collisionY(self.x, self.r/3) - platform.h * 3:
                        if self.y + self.r / 2 < platform.collisionY(self.x, self.r/3) + platform.h * 3:
                            self.y = platform.collisionY(self.x, self.r/3) - r/ 2
                            return True
        return False
    def jump(self):
        self.isJumping = True
        if self.jy > 0:
            t = (4 * self.jy) ** 0.5
            self.dx = self.jx / t
            self.dy = 0
        else:
            self.dy = - (2.1 * abs(self.jy)) ** 0.5
            t = -self.dy / 2
            self.dx = self.jx / t
    def move(self, app):
        if self.explode:
            self.explodePointer += 0.5
            if self.explodePointer > 3:
                app.ff.hp -= 25
                self.sound.play()
                self.remove = True
                if app.ff.hp <= 0:
                    app.gameStatus = 'over'
                    if app.ff.cy > app.bestScore:
                        app.bestScore = int(app.ff.cy)
            return False
        if (self.x - app.ff.cx) ** 2 + (self.y - app.ff.cy)**2 < 100 ** 2:
            self.explode = True
            return False  
        self.counter += 1
        if self.counter > 5:
            self.counter = 0
        if self.isJumping == False and self.onPlatform(app):
            self.dy = 0
            self.dx = 5 * self.direction
        else:
            self.dy += 2
            if self.dy > 20:
                self.dy = 20
            self.y += self.dy
            if self.counter == 0 and self.isJumping == False:
                self.findPath2(app, (self.x, self.y))
                self.jump()
        self.y += self.dy
        if self.x > 860 and self.dx > 0 or self.x < 100 and self.dx < 0:
            self.dx *= -1
        self.x += self.dx
        if self.isJumping and self.dy > 0 and self.onPlatform(app):
            self.isJumping = False
        
   
    def findPath2(self, app, cord):
        x, y = cord
        steps = []
        for platform in app.platforms:
            if inDrawRange(platform.y, app):
                if (platform.x, platform.y) != self.lastTarget:
                    dist = (platform.x - app.ff.cx) ** 2 + (platform.y - app.ff.cy) ** 2
                    (lx, ly) = self.lastTarget
                    lastDist = (lx - app.ff.cx) ** 2 + (ly - app.ff.cy) ** 2
                    if dist < lastDist:
                        steps.append((platform.x, platform.y))
        minDist = 99999999
        bestStep = (0, 0)
        for step in steps:
            x, y = step
            dx, dy = x - self.x, y - self.y
            dist = dx ** 2 + dy ** 2
            if dist < minDist:
                minDist = dist
                bestStep = step
        self.lastTarget = bestStep
        if minDist != 99999999:
            x, y = bestStep
            self.target = bestStep
            self.jx = x - self.x
            self.jy = y - self.y - self.r * 1
        if x < app.ff.cx:
            self.direction = 1
        else:
            self.direction = -1
        

