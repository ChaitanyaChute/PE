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

def drawSidePanel(screen, game_state, mode_label):
    px = panelX()
    p.draw.rect(screen, C_PANEL_BG, p.Rect(px, 0, SIDE_PANEL_WIDTH, WINDOW_HEIGHT))
    p.draw.line(screen, C_GOLD_DIM, (px, 0), (px, WINDOW_HEIGHT), 1)

    y = 18

    title = FONTS['title_s'].render("CHESS", True, C_GOLD)
    screen.blit(title, (px + SIDE_PANEL_WIDTH // 2 - title.get_width() // 2, y))
    y += title.get_height() + 4

    mode_lbl = FONTS['ui_xs'].render(mode_label.upper(), True, C_TEXT_DIM)
    screen.blit(mode_lbl, (px + SIDE_PANEL_WIDTH // 2 - mode_lbl.get_width() // 2, y))
    y += mode_lbl.get_height() + 14

    drawDivider(screen, y, px)
    y += 12

    if game_state.checkmate:
        winner = "Black" if game_state.white_to_move else "White"
        status, s_color = f"{winner} wins  ·  Checkmate", C_TEXT_WIN
    elif game_state.stalemate:
        status, s_color = "Draw  ·  Stalemate", C_TEXT_DRAW
    elif game_state.inCheck():
        who = "White" if game_state.white_to_move else "Black"
        status, s_color = f"{who} is in Check!", C_TEXT_CHECK
    else:
        who = "White" if game_state.white_to_move else "Black"
        status, s_color = f"{who} to move", C_TEXT_PRIMARY

    card = p.Rect(px + 10, y, SIDE_PANEL_WIDTH - 20, 34)
    drawCard(screen, card, radius=8)

    pip_x = card.x + 10
    pip_y = card.y + card.h // 2
    pip_col = (240,235,220) if (game_state.white_to_move) else (30,28,40)
    p.draw.circle(screen, pip_col,        (pip_x, pip_y), 6)
    p.draw.circle(screen, C_GOLD_DIM,     (pip_x, pip_y), 6, 1)

    lbl = FONTS['ui'].render(status, True, s_color)
    screen.blit(lbl, (card.x + 24, card.y + card.h // 2 - lbl.get_height() // 2))
    y += card.h + 14

    drawDivider(screen, y, px)
    y += 12

    cap_hdr = FONTS['ui_xs'].render("CAPTURED PIECES", True, C_TEXT_DIM)
    screen.blit(cap_hdr, (px + 12, y))
    y += cap_hdr.get_height() + 6

    white_cap, black_cap = getCaptured(game_state)
    cap_card = p.Rect(px + 10, y, SIDE_PANEL_WIDTH - 20, 68)
    drawCard(screen, cap_card)

    SZ = 26
   
    for row_idx, (side_label, caps) in enumerate([("▲", white_cap), ("▽", black_cap)]):
        ry = y + 6 + row_idx * (SZ + 4)
   
        if row_idx == 1 and caps:
            tile_w = min(len(caps), 9) * (SZ + 1) + 18
            tile = p.Rect(cap_card.x + 4, ry - 2, tile_w, SZ + 4)
            p.draw.rect(screen, C_PANEL_CARD_LT, tile, border_radius=4)
        slbl = FONTS['ui_xs'].render(side_label, True, C_TEXT_DIM)
        screen.blit(slbl, (cap_card.x + 6, ry + SZ // 2 - slbl.get_height() // 2))
        cx = cap_card.x + 20
        for piece in caps[:9]:
            mini = p.transform.smoothscale(IMAGES[piece], (SZ, SZ))
            screen.blit(mini, (cx, ry))
            cx += SZ + 1
    y += cap_card.h + 14

    drawDivider(screen, y, px)
    y += 12

    log_hdr = FONTS['ui_xs'].render("MOVE LOG", True, C_TEXT_DIM)
    screen.blit(log_hdr, (px + 12, y))
    y += log_hdr.get_height() + 4

    log_area_h = WINDOW_HEIGHT - y - 42
    log_surf   = p.Surface((SIDE_PANEL_WIDTH - 20, log_area_h), p.SRCALPHA)

    moves      = game_state.move_log
    ROW_H      = 22
    max_rows   = log_area_h // ROW_H
    total_rows = (len(moves) + 1) // 2
    start      = max(0, total_rows - max_rows)

    for i in range(start, total_rows):
        wi = i * 2
        bi = wi + 1
        ry = (i - start) * ROW_H
        is_last = (i == total_rows - 1)
        bg = C_LOG_ACTIVE if is_last else (C_LOG_A if i % 2 == 0 else C_LOG_B)
        p.draw.rect(log_surf, bg, p.Rect(0, ry, SIDE_PANEL_WIDTH - 20, ROW_H))

        num = FONTS['mono'].render(f"{i+1:>3}.", True, C_TEXT_DIM)
        log_surf.blit(num, (4, ry + ROW_H // 2 - num.get_height() // 2))

        if wi < len(moves):
            font = FONTS['mono_b'] if is_last and game_state.white_to_move == False else FONTS['mono']
            wl = font.render(moves[wi].getChessNotation(), True,
                             C_TEXT_GOLD if is_last and bi > len(moves) else C_TEXT_PRIMARY)
            log_surf.blit(wl, (40, ry + ROW_H // 2 - wl.get_height() // 2))

        if bi < len(moves):
            font = FONTS['mono_b'] if is_last else FONTS['mono']
            bl = font.render(moves[bi].getChessNotation(), True,
                             C_TEXT_GOLD if is_last else C_TEXT_PRIMARY)
            log_surf.blit(bl, (130, ry + ROW_H // 2 - bl.get_height() // 2))

    screen.blit(log_surf, (px + 10, y))

    hints_y = WINDOW_HEIGHT - 28
    hints = [("Z", "Undo"), ("R", "Restart"), ("ESC", "Menu")]
    total_w = 0
    rendered = []
    for k, v in hints:
        k_s = FONTS['ui_xs'].render(k, True, C_GOLD_DIM)
        v_s = FONTS['ui_xs'].render(f" {v}", True, C_TEXT_DIM)
        rendered.append((k_s, v_s))
        total_w += k_s.get_width() + v_s.get_width() + 18
    hx = px + SIDE_PANEL_WIDTH // 2 - total_w // 2
    for k_s, v_s in rendered:
        screen.blit(k_s, (hx, hints_y))
        hx += k_s.get_width()
        screen.blit(v_s, (hx, hints_y))
        hx += v_s.get_width() + 18


def getCaptured(game_state):
    white_cap, black_cap = [], []
    for mv in game_state.move_log:
        if mv.piece_captured != '--':
            if mv.piece_captured[0] == 'b':
                white_cap.append(mv.piece_captured)
            else:
                black_cap.append(mv.piece_captured)
    return white_cap, black_cap


