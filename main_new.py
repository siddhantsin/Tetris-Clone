import pygame as pg
from settings_new import *
from blocks_new import *
import random, time

###### NOTESSS #######
#adjust WINDOWHEIGHT and WINDOWWIDTH constants, and BOARDHEIGHT and BOARDWIDTH 
#constants

#Format of the piece data structure:
#["shape", rotation, tuple color, int x, int y]
######################



#initialize pygame and set window
pg.init()
win = pg.display.set_mode((WIDTH, HEIGHT))
pg.display.set_caption(GAME_NAME)
Clock = pg.time.Clock()

#trying new things
#self.current_block = square_block


class Game():
    def __init__(self):
        TITLE_FONT = pg.font.Font(pg.font.match_font("Comic Sans"), 100)
        STD_FONT = pg.font.Font(pg.font.match_font("Comic Sans"), 20)
        running = True
            
                 
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
    
        fallingPiece = getNewPiece()
        nextPiece = getNewPiece()
    
        while True: # game loop
            if fallingPiece == None:
                # No falling piece in play, so start a new piece at the top
                fallingPiece = nextPiece
                nextPiece = getNewPiece()
                lastFallTime = time.time() # reset lastFallTime
    
                if not isValidPosition(board, fallingPiece):
                    return # can't fit a new piece on the board, so game over
    
            checkForQuit()
            for event in pygame.event.get(): # event handling loop
                if event.type == KEYUP:
                    if (event.key == K_p):
                        # Pausing the game
                        DISPLAYSURF.fill(BGCOLOR)
                        pygame.mixer.music.stop()
                        showTextScreen('Paused') # pause until a key press
                        pygame.mixer.music.play(-1, 0.0)
                        lastFallTime = time.time()
                        lastMoveDownTime = time.time()
                        lastMoveSidewaysTime = time.time()
                    elif (event.key == K_LEFT or event.key == K_a):
                        movingLeft = False
                    elif (event.key == K_RIGHT or event.key == K_d):
                        movingRight = False
                    elif (event.key == K_DOWN or event.key == K_s):
                        movingDown = False
    
                elif event.type == KEYDOWN:
                    # moving the piece sideways
                    if (event.key == K_LEFT or event.key == K_a) and isValidPosition(board, fallingPiece, adjX=-1):
                        fallingPiece['x'] -= 1
                        movingLeft = True
                        movingRight = False
                        lastMoveSidewaysTime = time.time()
    
                    elif (event.key == K_RIGHT or event.key == K_d) and isValidPosition(board, fallingPiece, adjX=1):
                        fallingPiece['x'] += 1
                        movingRight = True
                        movingLeft = False
                        lastMoveSidewaysTime = time.time()
    
                    # rotating the piece (if there is room to rotate)
                    elif (event.key == K_UP or event.key == K_w):
                        fallingPiece['rotation'] = (fallingPiece['rotation'] + 1) % len(PIECES[fallingPiece['shape']])
                        if not isValidPosition(board, fallingPiece):
                            fallingPiece['rotation'] = (fallingPiece['rotation'] - 1) % len(PIECES[fallingPiece['shape']])
                    elif (event.key == K_q): # rotate the other direction
                        fallingPiece['rotation'] = (fallingPiece['rotation'] - 1) % len(PIECES[fallingPiece['shape']])
                        if not isValidPosition(board, fallingPiece):
                            fallingPiece['rotation'] = (fallingPiece['rotation'] + 1) % len(PIECES[fallingPiece['shape']])
    
                    # making the piece fall faster with the down key
                    elif (event.key == K_DOWN or event.key == K_s):
                        movingDown = True
                        if isValidPosition(board, fallingPiece, adjY=1):
                            fallingPiece['y'] += 1
                        lastMoveDownTime = time.time()
    
                    # move the current piece all the way down
                    elif event.key == K_SPACE:
                        movingDown = False
                        movingLeft = False
                        movingRight = False
                        for i in range(1, BOARDHEIGHT):
                            if not isValidPosition(board, fallingPiece, adjY=i):
                                break
                        fallingPiece['y'] += i - 1
    
            # handle moving the piece because of user input
            if (movingLeft or movingRight) and time.time() - lastMoveSidewaysTime > MOVESIDEWAYSFREQ:
                if movingLeft and isValidPosition(board, fallingPiece, adjX=-1):
                    fallingPiece['x'] -= 1
                elif movingRight and isValidPosition(board, fallingPiece, adjX=1):
                    fallingPiece['x'] += 1
                lastMoveSidewaysTime = time.time()
    
            if movingDown and time.time() - lastMoveDownTime > MOVEDOWNFREQ and isValidPosition(board, fallingPiece, adjY=1):
                fallingPiece['y'] += 1
                lastMoveDownTime = time.time()
    
            # let the piece fall if it is time to fall
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
            DISPLAYSURF.fill(BGCOLOR)
            drawBoard(board)
            drawStatus(score, level)
            drawNextPiece(nextPiece)
            if fallingPiece != None:
                drawPiece(fallingPiece)
    
            pygame.display.update()
            FPSCLOCK.tick(FPS)   
            
            
    def getNewBoard(self):
        board = []
        for i in range(BOARDWIDTH):
            board.append(["."] * BOARDHEIGHT)
        return board        
        
    
    def showScreen(self, text):
        # This function displays large text in the
        # center of the screen until a key is pressed.
        # Draw the text drop shadow
        
            
        #titleSurf, titleRect = makeTextObjs(text, TITLE_FONT, TEXTCOLOR)
        titleObj = TITLE_FONT.render(text, True, color)
        titleRect = titleObj.get_rect()             
        titleRect.center = (int(WINDOWWIDTH / 2) , int(WINDOWHEIGHT / 2) )
        win.blit(titleObj, titleRect)            
        
        # Draw the additional "Press a key to play." text.
        bodyObj = STD_FONT.render("Press any key to continue", True, color)
        bodyRect = bodyObj.get_rect()  
        bodyRect.center = (int(WINDOWWIDTH / 2), int(WINDOWHEIGHT / 2) + 100)
        win.blit(bodyObj, bodyRect)
    
        while self.senseAnyKey() == False:
            pygame.display.update()
            Clock.tick()   
            
    """
    def makeTextObjs(self, text, font, color):
        surf = font.render(text, True, color)
        return surf, surf.get_rect()    
    """
    
    def senseAnyKey(self):
        for event in pygame.event.get([KEYDOWN, KEYUP]):
            if event.type == KEYDOWN:
                return True
        return False
    
    def isValidPosition(board, piece, adjX=0, adjY=0):
        # Return True if the piece is within the board and not colliding
        for x in range(TEMPLATEWIDTH):
            for y in range(TEMPLATEHEIGHT):
                isAboveBoard = y + piece['y'] + adjY < 0
                if isAboveBoard or PIECES[piece['shape']][piece['rotation']][y][x] == BLANK:
                    continue
                if not isOnBoard(x + piece['x'] + adjX, y + piece['y'] + adjY):
                    return False
                if board[x + piece['x'] + adjX][y + piece['y'] + adjY] != BLANK:
                    return False
        return True    
        
        
g = Game()
g.showScreen('Start')
while g.running:
    CLock.tick(FPS)
    g.runGame()
    
self.showScreen('Game Over') 