import pygame as pg
from settings_new import *
from blocks_new import *
import random, time
from pygame.locals import *

###### NOTESSS #######
#adjust WINDOWHEIGHT and WINDOWWIDTH constants, and BOARDHEIGHT and BOARDWIDTH 
#constants

#Format of the piece data structure:
#["shape", rotation, tuple color, int x, int y]
######################



#initialize pygame and set window
pg.init()
win = pg.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
pg.display.set_caption(GAME_NAME)
Clock = pg.time.Clock()

#trying new things
#self.current_block = square_block


class Game():
    def __init__(self):
        self.TITLE_FONT = pg.font.Font(pg.font.match_font("Comic Sans"), 100)
        self.STD_FONT = pg.font.Font(pg.font.match_font("Comic Sans"), 20)
        self.running = True
            
                 
    def runGame(self):
        board = getNewBoard()
        lastMoveDownTime = time.time()
        lastMoveSidewaysTime = time.time()
        lastFallTime = time.time()
        movingDown = False # note: there is no movingUp variable
        movingLeft = False
        movingRight = False
        score = 0
        level, fallFreq = calculateLevelAndFallFreq(score)
    
        fallingPiece = newPiece()
        nextPiece = newPiece()
    
        while True: # game loop
            if fallingPiece == None:
                # No falling piece in play, so start a new piece at the top
                fallingPiece = nextPiece
                nextPiece = getNewPiece()
                lastFallTime = time.time() # reset lastFallTime
    
                if not isValidPosition(board, fallingPiece):
                    return # can't fit a new piece on the board, so game over
    
            if self.checkForClose():
                return # The wndow has been closed, so game over.
            
            KEY = pg.key.get_pressed()
            
            for event in pg.event.get(): # event handling loop
                if KEY[pg.K_UP]:
                    fallingPiece['rotation'] = (fallingPiece['rotation'] + 1) % len(PIECES[fallingPiece['shape']])
                    if not isValidPosition(board, fallingPiece):
                        fallingPiece['rotation'] = (fallingPiece['rotation'] - 1) % len(PIECES[fallingPiece['shape']])
                        
                elif KEY[pg.K_LEFT] and time.time() - lastMoveSidewaysTime > MOVESIDEWAYSFREQ:
                    if isValidPosition(board, fallingPiece, adjX=-1):
                        fallingPiece['x'] -= 1
                    lastMoveSidewaysTime = time.time()      
                    
                elif KEY[pg.K_RIGHT] and time.time() - lastMoveSidewaysTime > MOVESIDEWAYSFREQ:
                    if isValidPosition(board, fallingPiece, adjX=1):
                        fallingPiece['x'] += 1
                    lastMoveSidewaysTime = time.time()    
                    
                elif KEY[pg.K_p]:
                    DISPLAYSURF.fill(BGCOLOR)
                    showTextScreen('Paused')
                    lastFallTime = time.time()
                    lastMoveDownTime = time.time()
                    lastMoveSidewaysTime = time.time()
                    
                # making the piece fall faster with the down key
                elif KEY[pg.K_DOWN] and time.time() - lastMoveDownTime > MOVEDOWNFREQ:
                    if isValidPosition(board, fallingPiece, adjY=1):
                        fallingPiece['y'] += 1
                    lastMoveDownTime = time.time()
                    
                        
                elif (event.key == K_p):
                    # Pausing the game
                    DISPLAYSURF.fill(BGCOLOR)
                    pg.mixer.music.stop()
                    showTextScreen('Paused') # pause until a key press
                    pg.mixer.music.play(-1, 0.0)
                    lastFallTime = time.time()
                    lastMoveDownTime = time.time()
                    lastMoveSidewaysTime = time.time()
                                   
            if time.time() - lastFallTime > fallFreq:
                # see if the piece has landed
                if not isValidPosition(board, fallingPiece, adjY=1):
                    # falling piece has landed, set it on the board
                    addToBoard(board, fallingPiece)
                    score += removeCompleteLines(board)
                    level, fallFreq = calculateLevelAndFallFreq(score)
                    fallingPiece = None
                else:
                    # piece did not land, just move the piece down
                    fallingPiece['y'] += 1
                    lastFallTime = time.time()            
    
               
    
                   

    
            # drawing everything on the screen
            win.fill(BGCOLOR)
            drawBoard(board)
            drawStatus(score, level)
            drawNextPiece(nextPiece)
            if fallingPiece != None:
                drawPiece(fallingPiece)
    
            pg.display.update()
            FPSCLOCK.tick(FPS)   
            
            
    def getNewBoard(self):
        board = []
        for i in range(BOARDWIDTH):
            board.append(["."] * BOARDHEIGHT)
        return board
    
    def getNewPiece(self):
        # return a random new piece in a random rotation and color
        allShapes = list(PIECES.keys())
        newShape = random.choice(allShapes)
        newColor = random.choice(range(0, len(COLORS)-1))
        newPiece = {'shape': newshape,
                    'rotation': 1,
                    'x': int(BOARDWIDTH / 2) - int(TEMPLATEWIDTH / 2),
                    'y': -2, # start it above the board (i.e. less than 0)
                    'color': newColor}
        return newPiece    
        
    
    def showScreen(self, text):
        # This function displays large text in the
        # center of the screen until a key is pressed.
        # Draw the text drop shadow
        
            
        #titleSurf, titleRect = makeTextObjs(text, TITLE_FONT, TEXTCOLOR)
        titleObj = self.TITLE_FONT.render(text, True, WHITE)
        titleRect = titleObj.get_rect()             
        titleRect.center = (int(WINDOWWIDTH / 2) , int(WINDOWHEIGHT / 2) )
        win.blit(titleObj, titleRect)            
        
        # Draw the additional "Press a key to play." text.
        bodyObj = self.STD_FONT.render("Press any key to continue", True, WHITE)
        bodyRect = bodyObj.get_rect()  
        bodyRect.center = (int(WINDOWWIDTH / 2), int(WINDOWHEIGHT / 2) + 100)
        win.blit(bodyObj, bodyRect)
    
        while self.senseAnyKey() == False:
            pg.display.update()
            Clock.tick()   
            
    """
    def makeTextObjs(self, text, font, color):
        surf = font.render(text, True, color)
        return surf, surf.get_rect()    
    """
    
    def senseAnyKey(self):
        for event in pg.event.get([KEYDOWN, KEYUP]):
            if event.type == KEYDOWN:
                return True
        return False
    
    def isValidPosition(self, board, piece, adjX=0, adjY=0):
        # Return True if the piece is within the board and not colliding
        for x in range(TEMPLATEWIDTH):
            for y in range(TEMPLATEHEIGHT):
                isAboveBoard = y + piece['y'] + adjY < 0
                isOnBoard = x + piece['x'] + adjX >= 0 and x +piece['x'] + adjX < BOARDWIDTH and y + piece['y'] + adjY < BOARDHEIGHT
                if isAboveBoard or PIECES[piece['shape']][piece['rotation']][y][x] == BLANK:
                    continue
                if not isOnBoard:
                    return False
                if board[x + piece['x'] + adjX][y + piece['y'] + adjY] != BLANK:
                    return False
        return True    
    
    def closeButtonPressed(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.running = False
                return True
            
    def addToBoard(self):
        for x in range(TEMPLATEWIDTH):
            for y in range(TEMPLATEHEIGHT):
                if PIECES[piece['shape']][piece['rotation']][y][x] != BLANK:
                    board[x + piece['x']][y + piece['y']] = piece['color']
        
        
g = Game()
g.showScreen('Start')
while g.running:
    Clock.tick(FPS)
    g.runGame()
    
self.showScreen('Game Over')
pg.quit()
