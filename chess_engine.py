import pygame as p
import chess_board
from chess_board import Move

WIDTH = HEIGHT = 512
DIMENSION = 8
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 15
IMAGES = {}

"""
Load images for pieces at once.
"""
def load_images():
    pieces = ['bB', 'bN', 'bR', 'bQ', 'bK', 'bp', 'wB', 'wN', 'wR', 'wQ', 'wK', 'wp']
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("images/" + piece + ".png"), (SQ_SIZE, SQ_SIZE))

"""
Main driver function, this will handle input and graphics.
"""
def main():
    p.init()
    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    cb = chess_board.ChessBoard()
    load_images()
    running = True
    sq_selected = ()
    clicks = []
    valid_moves = cb.get_valid_moves()
    move_made = False
    while running:
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            elif e.type == p.MOUSEBUTTONDOWN:
                location = p.mouse.get_pos() #x, y coord. of mouse
                col = location[0] // SQ_SIZE
                row = location[1] // SQ_SIZE
                if sq_selected == (row, col):
                    sq_selected = ()
                    clicks = []
                else:
                    sq_selected = (row, col)
                    clicks.append(sq_selected)
                if len(clicks) == 2:
                    m = Move(clicks[0], clicks[1], cb.board)
                    for move in valid_moves:
                        if m == move:    
                            cb.make_move(move)
                            move_made = True
                            sq_selected = ()
                            clicks = [] 
                    if not move_made:
                        clicks = [sq_selected]

            elif e.type == p.KEYDOWN and e.key == p.K_z:
                cb.undo_move()
                move_made = True
                
        if move_made:
            valid_moves = cb.get_valid_moves()
            move_made = False
        if len(valid_moves) == 0:
            print("Checkmate")
            break

        draw_game_state(screen, cb)
        clock.tick(MAX_FPS)
        p.display.flip()

"""
This function will handle all in game graphics.
"""
def draw_game_state(screen, cb):
    draw_board(screen) #this function will draw sqaures on the board
    draw_pieces(screen, cb.board) #this function will draw pieces on the board at their respective positions.

"""
This function will draw 8x8 chess board.
"""
def draw_board(screen):
    colors = [p.Color("white"), p.Color("gray")]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[(r+c)%2]
            p.draw.rect(screen, color, p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))

def draw_pieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            if board[r][c] == "--":
                continue
            else:
                screen.blit(IMAGES[board[r][c]], p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))

if __name__ == "__main__":
    main()