import pygame as pg
from settings import *
from blocks import *
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
        self.SCORE_FONT = pg.font.Font(pg.font.match_font("Comic Sans"), 40)
        self.running = True
            
                 
    def runGame(self):
        board = self.getNewBoard()
        lastMoveDownTime = time.time()
        lastMoveSidewaysTime = time.time()
        lastFallTime = time.time()
        movingDown = False # note: there is no movingUp variable
        movingLeft = False
        movingRight = False
        score = 0
        fallFreq = 0.3
    
    
        fallingPiece = self.getNewPiece()
        nextPiece = self.getNewPiece()
    
        while True: # game loop
            if fallingPiece == None:
                # No falling piece in play, so start a new piece at the top
                fallingPiece = nextPiece
                nextPiece = self.getNewPiece()
                lastFallTime = time.time() # reset lastFallTime
    
                if not self.isValidPosition(board, fallingPiece):
                    return # can't fit a new piece on the board, so game over
    
            if self.closeButtonPressed():
                return # The wndow has been closed, so game over.

            
 #           for event in pg.event.get(): # event handling loop
                
            KEY = pg.key.get_pressed()                
            if KEY[pg.K_UP]:
                fallingPiece['rotation'] = (fallingPiece['rotation'] + 1) % len(PIECES[fallingPiece['shape']])
                if not self.isValidPosition(board, fallingPiece):
                    fallingPiece['rotation'] = (fallingPiece['rotation'] - 1) % len(PIECES[fallingPiece['shape']])
                    
            elif KEY[pg.K_LEFT] and time.time() - lastMoveSidewaysTime > MOVESIDEWAYSFREQ:
                if self.isValidPosition(board, fallingPiece, adjX=-1):
                    fallingPiece['x'] -= 1
                lastMoveSidewaysTime = time.time()      
                
            elif KEY[pg.K_RIGHT] and time.time() - lastMoveSidewaysTime > MOVESIDEWAYSFREQ:
                if self.isValidPosition(board, fallingPiece, adjX=1):
                    fallingPiece['x'] += 1
                lastMoveSidewaysTime = time.time()    
                
            elif KEY[pg.K_p]:
                win.fill(BGCOLOR)
                showTextScreen('Paused')
                lastFallTime = time.time()
                lastMoveDownTime = time.time()
                lastMoveSidewaysTime = time.time()
                
            # making the piece fall faster with the down key
            elif KEY[pg.K_DOWN] and time.time() - lastMoveDownTime > MOVEDOWNFREQ:
                if self.isValidPosition(board, fallingPiece, adjY=1):
                    fallingPiece['y'] += 1
                lastMoveDownTime = time.time()
                
                        
            elif (KEY[pg.K_p]):
                # Pausing the game
                win.fill(BGCOLOR)
                pg.mixer.music.stop()
                self.showTextScreen('Paused') # pause until a key press
                pg.mixer.music.play(-1, 0.0)
                lastFallTime = time.time()
                lastMoveDownTime = time.time()
                lastMoveSidewaysTime = time.time()
                                   
            if time.time() - lastFallTime > fallFreq:
                # see if the piece has landed
                if not self.isValidPosition(board, fallingPiece, adjY=1):
                    # falling piece has landed, set it on the board
                    self.addToBoard(board, fallingPiece)
                    score += self.removeAllLines(board)
                    fallingPiece = None
                else:
                    # piece did not land, just move the piece down
                    fallingPiece['y'] += 1
                    lastFallTime = time.time()            
    
               
    
                   

    
            # drawing everything on the screen
            win.fill(BGCOLOR)
            self.drawBoard(board)
            pg.draw.rect(win, GREY, (XMARGIN - 3, TOPMARGIN - 7, (BOARDWIDTH * BOXSIZE) + 8, (BOARDHEIGHT * BOXSIZE) + 8), 5)
            self.drawScore(score)
            #self.drawNextPiece(nextPiece)
            if fallingPiece != None:
                self.drawPiece(fallingPiece)
    
            pg.display.update()
            Clock.tick(FPS)   
            
            
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
        newPiece = {'shape': newShape,
                    'rotation': 0,
                    'x': int(BOARDWIDTH / 2) - int(TEMPLATEWIDTH / 2),
                    'y': -2, # start it above the board (i.e. less than 0)
                    'color': newColor}
        return newPiece    
        
    
    def showScreen(self, text):
        # This function displays large text in the
        # center of the screen until a key is pressed.
        
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
                isOnTopBoard = y + piece['y'] + adjY < 0
                isOnBoard = x + piece['x'] + adjX >= 0 and x +piece['x'] + adjX < BOARDWIDTH and y + piece['y'] + adjY < BOARDHEIGHT
                if isOnTopBoard or PIECES[piece['shape']][piece['rotation']][y][x] == BLANK:
                    continue
                if not isOnBoard:
                    return False
                if board[x + piece['x'] + adjX][y + piece['y'] + adjY] != BLANK:
                    return False
        return True    
    
    def closeButtonPressed(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                
                
    def addToBoard(self, board, piece):
        for x in range(TEMPLATEWIDTH):
            for y in range(TEMPLATEHEIGHT):
                if PIECES[piece['shape']][piece['rotation']][y][x] != BLANK:
                    board[x + piece['x']][y + piece['y']] = piece['color']
                    
    def removeAllLines(self, board):
        linesRemoved = 0
        y = BOARDHEIGHT - 1 
        while True:
            if self.lineExists(board, y):
                self.shiftPiecesAboveDown(board, y)
                for x in range(0, BOARDWIDTH):
                    board[x][0] = BLANK
                linesRemoved += 1
            else:
                y = y-1
                if y < 0:
                    break
        return linesRemoved
                
    def lineExists(self, board, y):
        for x in range(0, BOARDWIDTH):
            if board[x][y] == BLANK:
                return False
        return True
    
    def shiftPiecesAboveDown(self, board, y):
        for y in range(y, 0 ,-1):
            for x in range(0, BOARDWIDTH):
                board[x][y] = board[x][y-1]
                
    def drawBoard(self, board):
        for x in range(BOARDWIDTH):
            for y in range(BOARDHEIGHT):
                pixelx, pixely = (XMARGIN + (x * BOXSIZE)), (TOPMARGIN + (y * BOXSIZE))
                self.drawCell(board[x][y], pixelx, pixely)   
                
    def drawPiece(self, piece):
        pixelx, pixely = (XMARGIN + (piece['x'] * BOXSIZE)), (TOPMARGIN + (piece['y'] * BOXSIZE))
        
        for x in range(0, TEMPLATEWIDTH):
            for y in range(0, TEMPLATEHEIGHT):
                if PIECES[piece['shape']][piece['rotation']][y][x] != BLANK:
                    self.drawCell(piece['color'], pixelx + (x * BOXSIZE), pixely + (y * BOXSIZE))   
                    
    def drawScore(self, score):
        bodyObj = self.SCORE_FONT.render("Score: " + str(score), True, WHITE)
        bodyRect = bodyObj.get_rect()  
        bodyRect.center = (int(WINDOWWIDTH / 2) + 180, int(WINDOWHEIGHT / 2))
        win.blit(bodyObj, bodyRect)        
        
        
    def drawCell(self, color, pixelx, pixely):
        if color == BLANK:
            return
        pg.draw.rect(win, COLORS[color], (pixelx + 1, pixely + 1, BOXSIZE - 1, BOXSIZE - 1))
                
        
        
        
g = Game()
g.showScreen('Start')

Clock.tick(FPS)
g.runGame()
    
g.showScreen('Game Over')
pg.quit()
