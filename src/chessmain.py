import pygame as p
import chessengine, ChessAI, HighlightArea, MoveLog
import sys, math
from multiprocessing import Process, Queue

BOARD_SIZE       = 576          
COORD_MARGIN     = 32
SIDE_PANEL_WIDTH = 300
WINDOW_WIDTH     = COORD_MARGIN + BOARD_SIZE + COORD_MARGIN + SIDE_PANEL_WIDTH
WINDOW_HEIGHT    = COORD_MARGIN + BOARD_SIZE + COORD_MARGIN
DIMENSION        = 8
SQ               = BOARD_SIZE // DIMENSION   
MAX_FPS          = 60

#color Pallete
C_BG             = ( 24,  21,  18)   
C_BG2            = ( 34,  30,  25)   
C_LIGHT_SQ       = (235, 211, 175)   
C_DARK_SQ        = (165, 117,  75)   
C_BOARD_BORDER   = ( 90,  68,  42)   
C_COORD_LIGHT    = (210, 182, 140)   
C_COORD_DARK     = (120,  88,  55)   

C_GOLD           = (212, 175,  55)   
C_GOLD_DIM       = (140, 110,  35)
C_GOLD_BRIGHT    = (255, 215,  90)
C_SILVER         = (192, 192, 192)

C_SELECT         = (100, 165, 255, 130)
C_LAST_MOVE      = (212, 175,  55,  90)
C_CHECK_SQ       = (220,  60,  60, 160)
C_DOT_LIGHT      = ( 50,  38,  20, 110)
C_DOT_DARK       = (255, 245, 220,  70)
C_CAPTURE_RING   = (212, 175,  55,  90)

C_PANEL_BG       = ( 28,  25,  21)  
C_PANEL_EDGE     = ( 60,  50,  38)  
C_PANEL_CARD     = ( 38,  33,  27)   
C_PANEL_CARD_LT  = ( 58,  52,  43)   
C_DIVIDER        = ( 55,  47,  36)   

C_TEXT_PRIMARY   = (232, 225, 210)
C_TEXT_DIM       = (148, 132, 108)   
C_TEXT_GOLD      = (212, 175,  55)
C_TEXT_CHECK     = (230,  85,  75)
C_TEXT_WIN       = ( 90, 210, 120)
C_TEXT_DRAW      = (160, 155, 175)

C_BTN_BG         = ( 40,  35,  28)   
C_BTN_HOVER      = ( 58,  50,  38)   
C_BTN_BORDER     = ( 90,  75,  55)   
C_BTN_ACTIVE_BG  = ( 65,  55,  40)
C_BTN_ACTIVE_BDR = (212, 175,  55)

C_LOG_A          = ( 36,  31,  25)   
C_LOG_B          = ( 28,  24,  19)   
C_LOG_ACTIVE     = ( 55,  46,  32)   

IMAGES = {}

FONTS = {}

def initFonts():
    FONTS['title']   = p.font.SysFont("Georgia",    48, bold=True)
    FONTS['title_s'] = p.font.SysFont("Georgia",    22, bold=False)
    FONTS['ui']      = p.font.SysFont("Arial",      14, bold=True)
    FONTS['ui_sm']   = p.font.SysFont("Arial",      12, bold=False)
    FONTS['ui_xs']   = p.font.SysFont("Arial",      11, bold=False)
    FONTS['coord']   = p.font.SysFont("Georgia",    12, bold=False)
    FONTS['btn']     = p.font.SysFont("Georgia",    17, bold=True)
    FONTS['mono']    = p.font.SysFont("Courier New",12, bold=False)
    FONTS['mono_b']  = p.font.SysFont("Courier New",12, bold=True)

def loadImages():
    pieces = ['wp','wR','wN','wB','wK','wQ','bp','bR','bN','bB','bK','bQ']
    for piece in pieces:
        IMAGES[piece] = p.transform.smoothscale(
            p.image.load("images/" + piece + ".png"), (SQ, SQ))


def drawBG(screen):
    cx = WINDOW_WIDTH // 2
    for y in range(WINDOW_HEIGHT):
        t = y / WINDOW_HEIGHT
        r = int(C_BG[0] + t * (C_BG2[0] - C_BG[0]))
        g = int(C_BG[1] + t * (C_BG2[1] - C_BG[1]))
        b = int(C_BG[2] + t * (C_BG2[2] - C_BG[2]))
        p.draw.line(screen, (r, g, b), (0, y), (WINDOW_WIDTH, y))


def boardOrigin():
    return (COORD_MARGIN, COORD_MARGIN)

