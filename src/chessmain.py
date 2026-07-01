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

def squareRect(row, col):
    ox, oy = boardOrigin()
    return p.Rect(ox + col * SQ, oy + row * SQ, SQ, SQ)

def drawBoard(screen):
    ox, oy = boardOrigin()

    frame = p.Rect(ox - 6, oy - 6, BOARD_SIZE + 12, BOARD_SIZE + 12)
    p.draw.rect(screen, C_BOARD_BORDER, frame, border_radius=2)
    gold_frame = p.Rect(ox - 2, oy - 2, BOARD_SIZE + 4, BOARD_SIZE + 4)
    p.draw.rect(screen, C_GOLD_DIM, gold_frame, 1)

    # Squares
    for row in range(DIMENSION):
        for col in range(DIMENSION):
            color = C_LIGHT_SQ if (row + col) % 2 == 0 else C_DARK_SQ
            p.draw.rect(screen, color, squareRect(row, col))

    files = "abcdefgh"
    for col in range(DIMENSION):
        is_light = (7 + col) % 2 == 0
        color = C_COORD_DARK if is_light else C_COORD_LIGHT
        lbl = FONTS['coord'].render(files[col], True, color)
        x = ox + col * SQ + SQ - lbl.get_width() - 3
        y = oy + BOARD_SIZE - lbl.get_height() - 2
        screen.blit(lbl, (x, y))

    for row in range(DIMENSION):
        is_light = (row + 0) % 2 == 0
        color = C_COORD_DARK if is_light else C_COORD_LIGHT
        lbl = FONTS['coord'].render(str(8 - row), True, color)
        x = ox + 3
        y = oy + row * SQ + 3
        screen.blit(lbl, (x, y))

def drawPieces(screen, board):
    for row in range(DIMENSION):
        for col in range(DIMENSION):
            piece = board[row][col]
            if piece != "--":
                screen.blit(IMAGES[piece], squareRect(row, col))

def drawHighlights(screen, game_state, valid_moves, sq_selected):

    if game_state.move_log:
        last = game_state.move_log[-1]
        for (r, c) in [(last.start_row, last.start_col), (last.end_row, last.end_col)]:
            s = p.Surface((SQ, SQ), p.SRCALPHA)
            s.fill(C_LAST_MOVE)
            screen.blit(s, squareRect(r, c))

    if game_state.inCheck():
        king_loc = game_state.white_king_location if game_state.white_to_move \
                   else game_state.black_king_location
        s = p.Surface((SQ, SQ), p.SRCALPHA)
        s.fill(C_CHECK_SQ)
        screen.blit(s, squareRect(*king_loc))

    if sq_selected:
        r, c = sq_selected
        if 0 <= r < 8 and 0 <= c < 8:
            piece = game_state.board[r][c]
            if piece != '--' and piece[0] == ('w' if game_state.white_to_move else 'b'):

                sel = p.Surface((SQ, SQ), p.SRCALPHA)
                sel.fill(C_SELECT)
                screen.blit(sel, squareRect(r, c))

                for mv in valid_moves:
                    if mv.start_row == r and mv.start_col == c:
                        er, ec = mv.end_row, mv.end_col
                        is_dark = (er + ec) % 2 == 1
                        ds = p.Surface((SQ, SQ), p.SRCALPHA)

                        if game_state.board[er][ec] != '--':
                            # Capture: gold ring instead of dot
                            p.draw.circle(ds, C_CAPTURE_RING,
                                          (SQ//2, SQ//2), SQ//2 - 4, 6)
                        else:
                            dot_c = C_DOT_DARK if is_dark else C_DOT_LIGHT
                            p.draw.circle(ds, dot_c, (SQ//2, SQ//2), SQ // 8)

                        screen.blit(ds, squareRect(er, ec))

def panelX():
    return COORD_MARGIN + BOARD_SIZE + COORD_MARGIN

def drawDivider(screen, y, px):
    p.draw.line(screen, C_DIVIDER, (px + 12, y), (px + SIDE_PANEL_WIDTH - 12, y), 1)

def drawCard(screen, rect, radius=6):
    p.draw.rect(screen, C_PANEL_CARD, rect, border_radius=radius)
    p.draw.rect(screen, C_PANEL_EDGE, rect, 1, border_radius=radius)

def renderCentered(screen, text, font, color, rect):
    lbl = font.render(text, True, color)
    screen.blit(lbl, (rect.x + rect.w // 2 - lbl.get_width() // 2,
                       rect.y + rect.h // 2 - lbl.get_height() // 2))

