import random,sys,copy,os,pygame
from pygame.locals import *

FPS=30
WINWIDTH=800
WINHEIGHT=600
HALF_WINWIDTH=int(WINWIDTH/2)
HALF_WINHEIGHT=int(WINHEIGHT/2)

TILEWIDTH=50
TILEHEIGHT=85
TILEFLOORHEIGHT=45

CAM_MOVE_SPEED=5


OUTSIDE_DECORATION_PCT=20

BRIGHTBLUE=(0,170,255)
WHITE= (255,255,255)
BGCOLOR=BRIGHTBLUE
TEXTCOLOR=WHITE

UP='up'
DOWN='down'
RIGHT='right'
LEFT='left'

def main():
    global FPSCLOCK, DISPLAYSURF, IMAGESDICT, TILEMAPPING,OUTSIDEDECOMAPPING, BASICFONT, PLAYERIMAGES, currentImage

    pygame.init()
    FPSCLOCK = pygame.time.Clock()


    DISPLAYSURF=pygame.displat.set_mode((WINWIDTH,WINHEIGHT))

    pygame.display.set_caption('Star Pusher')
    BAISCFONT=pygame.font.Font(freesansbold.ttf,18)

    IMAGEDICT={'uncovered goal' : pygame.image.load('RedSelector.png'),
               'covered goal' : pygame.image.load('Selector.png'),
               'star': pygame.image.load('Star.png'),
                'corner': pygame.image.load('Wall Block Tall.png'),
                'wall': pygame.image.load('Wood Block Tall.png'),
                'inside floor': pygame.image.load('Plain Block.png'),
                'outside floor': pygame.image.load('Grass Block.png'),
                'title': pygame.image.load('star_title.png'),
                'solved': pygame.image.load('star_solved.png'),
                'princess': pygame.image.load('princess.png'),
                'boy': pygame.image.load('boy.png'),
                'catgirl': pygame.image.load('catgirl.png'),
                'horngirl': pygame.image.load('horngirl.png'),
                'pinkgirl': pygame.image.load('pinkgirl.png'),
                'rock': pygame.image.load('Rock.png'),
                'short tree': pygame.image.load('Tree_Short.png'),
                'tall tree': pygame.image.load('Tree_Tall.png'),
                'ugly tree': pygame.image.load('Tree_Ugly.png')}
    TILEMAPPING = {'x' : IMAGEDCT['corner'],
                   '#' : IMAGEDCT['wall'],
                   'o' : IMAGEDCT['inside floor'],
                   ' ' : IMAGEDCT['outside floor']}
    
    OUTSIDEDECOMAPPING = {'1':IMAGESDICT['rock'],
                          '2':IMAGESDICT['short tree'],
                          '3':IMAGESDICT['tall tree'],
                          '4':IMAGESDICT['ugly tree']}
    
    currentImage = 0                        
    PLAYERIMAGES =[IMAGESDICT['princess'],
                    IMAGESDICT['boy'],
                    IMAGESDICT['catgirl'],
                    IMAGESDICT['horngirl'],
                    IMAGESDICT['pinkgirl']]
                                
    startscreen()

    levels=readLevelsFile('starpusher.txt')
    currentLevelIndex=0

    while True:
        result=runLevel(levels,currentLevelIndex)

        if result in ('solved','next'):
            currentLevelIndex+=1
            if currentLevelIndex>= len(levels):
                currentLevelIndex=0
        elif result == 'back':
            currentLevelIndex-=1
            if currentLevelIndex<0:
                currentLevelIndex = len(levels)-1
        elif result == 'reset':
            pass
def runLevel(levels,levelNum):
    global currentImage
    levelObj = levels[levelnum]
    mapObj= decorateMap(levelObj['mapObj'],levelObj['startstate']['playeer'])
    gameStateObj=copy.deepcopy(levelObj['startstate'])
    mapNeedsRedraw = True
    levelSurf = BASICFONT.render('Level %s of %s' % (levelObj['levelNum']+ 1, totalNumOfLevels), 1, TEXTCOLOR)

    levelRect = levelSurf.get_rect()
    levelRect.bottomleft = (20, WINHEIGHT - 35)
    mapWidth = len(mapObj) * TILEWIDTH
    mapHeight = (len(mapObj[0]) - 1) * (TILEHEIGHT - TILEFLOORHEIGHT) +TILEHEIGHT

    MAX_CAM_X_PAN = abs(HALF_WINHEIGHT - int(mapHeight / 2)) + TILEWIDTH
    MAX_CAM_Y_PAN = abs(HALF_WINWIDTH - int(mapWidth / 2)) + TILEHEIGHT
    levelIsComplete = False
    cameraOffsetX = 0
    cameraOffsetY = 0
    cameraUp = False

    cameraDown = False
    cameraLeft = False
    cameraRight = False

    while True:
        playerMoveTo = None
        keyPressed = False

        for event in pygame.event.get():
            if event.type == QUIT:
                terminate()     
            elif event.type == KEYDOWN:
                keyPressed = True
                if event.key == K_LEFT:
                    playerMoveTo = LEFT
                elif event.key == K_RIGHT:
                    playerMoveTo = RIGHT
                elif event.key == K_UP:
                    playerMoveTo = UP
                elif event.key == K_DOWN:
                    playerMoveTo = DOWN
                elif event.key == K_a:
                    cameraLeft = True
                elif event.key == K_d:
                    cameraRight = True
                elif event.key == K_w:
                    cameraUp = True
                elif event.key == K_s:
                    cameraDown = True
                elif event.key == K_n:
                    return 'next'
                elif event.key == K_b:
                    return 'back'
                elif event.key == K_ESCAPE:
                    terminate()
                elif event.key == K_BACKSPACE:
                    return 'reset'
                elif event.key == K_p:
                    currentImage += 1
                    if currentImage >= len(PLAYERIMAGES):
                        currentImage = 0
                    mapNeedsRedraw = True
            elif event.type == KEYUP:
                if event.key == K_a:
                    cameraLeft = False
                elif event.key == K_d:
                    cameraRight = False
                elif event.key == K_w:
                    cameraUp = False
                elif event.key == K_s:
                    cameraDown = False
                    
        if playerMoveTo != None and not levelIsComplete:
            moved = makeMove(mapObj, gameStateObj, playerMoveTo)
            if moved:
                gameStateObj['stepCounter'] += 1
                mapNeedsRedraw = True

            if isLevelFinished(levelObj, gameStateObj):
                levelIsComplete = True
                keyPressed = False
        DISPLAYSURF.fill(BGCOLOR)
        
        if mapNeedsRedraw:
            mapSurf = drawMap(mapObj, gameStateObj, levelObj['goals'])
            mapNeedsRedraw = False

        if cameraUp and cameraOffsetY < MAX_CAM_X_PAN:
            cameraOffsetY += CAM_MOVE_SPEED
        elif cameraDown and cameraOffsetY > -MAX_CAM_X_PAN:
            cameraOffsetY -= CAM_MOVE_SPEED
        if cameraLeft and cameraOffsetX < MAX_CAM_Y_PAN:
            cameraOffsetX += CAM_MOVE_SPEED
        elif cameraRight and cameraOffsetX > -MAX_CAM_Y_PAN:
            cameraOffsetX -= CAM_MOVE_SPEED


        mapSurfRect = mapSurf.get_rect()    

        mapSurfRect.center = (HALF_WINWIDTH + cameraOffsetX,HALF_WINHEIGHT + cameraOffsetY)

        DISPLAYSURF.blit(mapSurf, mapSurfRect)
        DISPLAYSURF.blit(levelSurf, levelRect)
        stepSurf = BASICFONT.render('Steps: %s' %(gameStateObj['stepCounter']), 1, TEXTCOLOR)
        stepRect = stepSurf.get_rect()
        stepRect.bottomleft = (20, WINHEIGHT - 10)
        DISPLAYSURF.blit(stepSurf, stepRect)
        if levelIsComplete: 

            solvedRect = IMAGESDICT['solved'].get_rect()
            solvedRect.center = (HALF_WINWIDTH, HALF_WINHEIGHT)
            DISPLAYSURF.blit(IMAGESDICT['solved'], solvedRect)
            
            if keyPressed:
                return 'solved'

        pygame.display.update()
        FPSCLOCK.tick()

        
def decorateMap(mapObj, startxy):
    startx, starty = startxy

    mapObjCopy = copy.deepcopy(mapObj)

    for x in range(len(mapObjCopy)):
        for y in range(len(mapObjCopy[0])):

            if mapObjCopy[x][y] in ('$', '.', '@', '+', '*'):
                mapObjCopy[x][y] = ' '      

    floodFill(mapObjCopy, startx, starty, ' ', 'o')

    for x in range(len(mapObjCopy)):
        for y in range(len(mapObjCopy[0])):

            if mapObjCopy[x][y] == '#':
                if (isWall(mapObjCopy, x, y-1) and isWall(mapObjCopy, x+1,y)) or (isWall(mapObjCopy, x+1, y) and isWall(mapObjCopy, x,y+1)) or (isWall(mapObjCopy, x, y+1) and isWall(mapObjCopy, x-1,y)) or (isWall(mapObjCopy, x-1, y) and isWall(mapObjCopy, x,y-1)):
                    mapObjCopy[x][y] = 'x'

            elif mapObjCopy[x][y] == ' ' and random.randint(0, 99) < OUTSIDE_DECORATION_PCT:
                mapObjCopy[x][y]=random.choice(list(OUTSIDEDECOMAPPING.keys()))
                
    return mapObjCopy
def isBlocked(mapObj, gameStateObj,x,y):
    if isWall(mapObj,x,y):
        return True
    elif x<0 or x>=len(mapObj) or y<0 or y>=len(mapObj[x]):
        return True
    elif (x,y) in gameStateObj['stars']:
        return  True

    return False

def makeMove(mapObj, gameStateObj,playerMoveTo):
    playerx,playery= gameStateObj['player']
    stars = gameStateObj['stars']

    if playerMoveTo == UP:
        xOffset=0
        yOffset=-1
    elif playerMoveTo == RIGHT:
        xOffset=1
        yOffset=0
    elif playerMoveTo == DOWN:
        xOffset=0
        yOffset=1
    elif playerMoveTo == LEFT:
        xOffset=-1
        yOffset=0

    if isWall(mapObj,playerx+xOffset,playery+yOffset):
        return False
    else:
        if(playerx + xOffset,playery+yOffset) in stars:
            if not isBlocked(mapObj, gameStateObj,playerx+(xOffset*2),playery+(yOffset*2)):
                ind = stars.index((playerx+xOffset,playery + yOffset))
                stars[ind]= (stars[ind][0]+xOffset,stars[ind][1]+yOffset)
            else:
                return False
        gameStateObj['player'] = (playerx+xOffset,playery+yOffset)
        return True
    
