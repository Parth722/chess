
class ChessBoard(object):
    def __init__(self):
        """ A chess board representation, 0 stands for an empty square.
            Chess notation examples:
            - b: Black
            - w: White
            - R: Rook
            - B: Bishop
            - N: Knight
            - Q: Queen
            - K: King
            - p: Pawn
        """
        self.board = [['bR','bN','bB','bQ','bK','bB','bN','bR'],
                      ['bp','bp','bp','bp','bp','bp','bp','bp'],
                      ["--"]*8,
                      ["--"]*8,
                      ["--"]*8,
                      ["--"]*8,
                      ['wp','wp','wp','wp','wp','wp','wp','wp'],
                      ['wR','wN','wB','wQ','wK','wB','wN','wR']]  
        #if turn is True, then it is white's turn else it is black's turn
        self.turn = True 
        self.moveLog = [] 
        self.movepair = []
        self.moveFunctions = {'p': self.get_pawn_moves, 'B': self.get_bishop_moves,
                              'R': self.get_rook_moves, 'K': self.get_king_moves,
                              'Q': self.get_queen_moves, 'N': self.get_knight_moves}
        self.in_check = False
        self.pins = []
        self.checks = []
        #both king's location on the board.
        self.black_king = (0,4)
        self.white_king = (7,4)
        #a tuple that holds the position of row and col where a pawn perform en-passant.
        self.en_passant = ()
        #castling rights at current gamestate
        self.current_castling_rights = CastlingRights(True, True, True, True)
        self.castle_log = [CastlingRights(self.current_castling_rights.wks, self.current_castling_rights.wqs,
                                          self.current_castling_rights.bks, self.current_castling_rights.bqs)]

    """
    This function handles all the moves, except castling, en-passant and pawn promotion.
    """
    def make_move(self, move):
        self.board[move.startrow][move.startcol] = "--"
        self.board[move.endrow][move.endcol] = move.piece_moved
        self.moveLog.append(move)
        #updating king positions in the gamestate.
        if move.piece_moved == 'wK':
            self.white_king = (move.endrow, move.endcol)
        elif move.piece_moved == 'bK':
            self.black_king = (move.endrow, move.endcol)

        #if move is castling.
        if move.is_castle:
            if move.piece_moved == "wK" or move.piece_moved == "bK":
                if move.endcol == 6 or move.endcol == 7:
                    self.board[move.endrow][4] = "--"
                    self.board[move.endrow][5] = move.piece_moved[0]+"R"
                    self.board[move.endrow][6] = move.piece_moved[0]+"K"
                    self.board[move.endrow][7] = "--"
                    if move.piece_moved == 'wK':
                        self.white_king = (7, 6)
                    elif move.piece_moved == 'bK':
                        self.black_king = (0, 6)
                if move.endcol == 2 or move.endcol == 1 or move.endcol == 0:
                    self.board[move.endrow][0] = "--"
                    self.board[move.endrow][1] = "--"
                    self.board[move.endrow][2] = move.piece_moved[0]+"R"
                    self.board[move.endrow][3] = move.piece_moved[0]+"K"
                    self.board[move.endrow][4] = "--"
                    if move.piece_moved == 'wK':
                        self.white_king = (7, 2)
                    elif move.piece_moved == 'bK':
                        self.black_king = (0, 2)

        #if move is pawn promotion.
        if move.pawn_promotion:
            self.board[move.endrow][move.endcol] = move.piece_moved[0]+"Q"
        
        if move.is_en_passant:
            move.piece_captured = self.board[move.startrow][move.endcol]
            self.board[move.startrow][move.endcol] = "--"

        #if pawn moves 2 squares ahead, it can be captured with en-passant.
        if move.piece_moved[1] == 'p' and abs(move.startrow - move.endrow) == 2:
            self.en_passant = ((move.startrow + move.endrow)//2, move.startcol)
        else: self.en_passant = ()

        #update castling rights:
        self.update_castling_rights(move)
        self.castle_log.append(CastlingRights(self.current_castling_rights.wks, self.current_castling_rights.wqs,
                                          self.current_castling_rights.bks, self.current_castling_rights.bqs))
        self.turn = not self.turn
        
    def update_castling_rights(self, move):
        #if white king moved.
        if move.piece_moved == 'wK':
            self.current_castling_rights.wks = False
            self.current_castling_rights.wqs = False
        #if black king moved.
        elif move.piece_moved == 'bK':
            self.current_castling_rights.bks = False
            self.current_castling_rights.bqs = False
        #if white rook moved.
        elif move.piece_moved == 'wR':
            if move.startrow == 7:
                if move.startcol == 0:
                    self.current_castling_rights.wqs = False
                elif move.startcol == 7:
                    self.current_castling_rights.wks = False
        #if black rook moved.
        elif move.piece_moved == 'bR':
            if move.startrow == 0:
                if move.startcol == 0:
                    self.current_castling_rights.bqs = False
                elif move.startcol == 7:
                    self.current_castling_rights.bks = False

    """
    This function undos the last move.
    """
    def undo_move(self):
        if len(self.moveLog) > 0:
            self.turn = not self.turn
            m = self.moveLog.pop()
            self.board[m.startrow][m.startcol] = m.piece_moved
            self.board[m.endrow][m.endcol] = m.piece_captured
            #if m is castle move.
            if m.is_castle:
                if m.piece_moved == 'wK' or m.piece_moved == 'bK':
                    if m.endcol == 6 or m.endcol == 7:
                        self.board[m.endrow][4] = m.piece_moved[0]+"K"
                        self.board[m.endrow][5] = "--"
                        self.board[m.endrow][6] = "--"
                        self.board[m.endrow][7] = m.piece_moved[0]+"R"
                        if m.piece_moved == 'wK':
                            self.white_king = (m.endrow, 4)
                        else:
                            self.black_king = (m.endrow, 4)
                    if m.endcol == 2 or m.endcol == 1 or m.endcol == 0:
                        self.board[m.endrow][4] = m.piece_moved[0]+"K"
                        self.board[m.endrow][1] = "--"
                        self.board[m.endrow][2] = "--"
                        self.board[m.endrow][3] = "--"
                        self.board[m.endrow][0] = m.piece_moved[0]+"R"
                        if m.piece_moved == 'wK':
                            self.white_king = (m.endrow, 4)
                        else:
                            self.black_king = (m.endrow, 4)
            #if m is en-passant.
            if m.is_en_passant:
                self.board[m.endrow][m.endcol] = '--'
                self.board[m.startrow][m.endcol] = m.piece_captured
                self.board[m.startrow][m.startcol] = m.piece_moved
                self.en_passant = (m.endrow, m.endcol)
            #if piece moved is pawn and it moved 2 squares, set en-passant = ()
            if m.piece_moved[1] == 'p' and abs(m.startrow-m.endrow) == 2:
                self.en_passant = ()
            
            #if pawn is promoting.
            if m.pawn_promotion:
                if m.piece_moved[0] == "w":
                    self.board[m.startrow][m.startcol] = "wp"
                    self.board[m.endrow][m.endcol] = m.piece_captured
                else:
                    self.board[m.startrow][m.startcol] = "bp"
                    self.board[m.endrow][m.endcol] = m.piece_captured
            
            #updating king's position.
            if m.piece_moved == 'wK':
                self.white_king = (m.endrow, m.endcol)
            elif m.piece_moved == 'bK':
                self.black_king = (m.endrow, m.endcol)
            
            #undo castling rights log.
            if len(self.castle_log) > 0:
                self.castle_log.pop()
                self.current_castling_rights = self.castle_log[-1]

            

    """
    This function generates all valid moves in current gamestate including checks as well.
    """
    def get_valid_moves(self):
        self.in_check, self.pins, self.checks = self.pins_and_checks()
        if self.turn:
            king_row = self.white_king[0]
            king_col = self.white_king[1]
        else:
            king_row = self.black_king[0]
            king_col = self.black_king[1]

        if self.in_check:
            if len(self.checks) == 1:
                moves = self.all_possible_moves()
                check = self.checks[0]
                r = check[0]
                c = check[1]
                piece = self.board[r][c][1]
                if piece == 'N':
                    valid_squares = [(r,c)]
                else:
                    valid_squares = []
                for i in range(1, 8):
                    valid_square = (king_row + check[2]*i, king_col + check[3]*i)
                    valid_squares.append(valid_square)
                    if valid_square[0] == r and valid_square[1] == c:
                        break

                for i in range(len(moves)-1, -1, -1):
                    if moves[i].piece_moved[1] != 'K':
                        if not (moves[i].endrow, moves[i].endcol) in valid_squares:
                            moves.remove(moves[i])
                return moves
            elif len(self.checks) == 2:
                moves = []
                self.get_king_moves(king_row, king_col, moves)
                return moves
        else:
            return self.all_possible_moves()

    """
    This function generates all possible pins and checks after a given move.
    """
    def pins_and_checks(self):
        pins = [] #list to hold pinned pieces.
        checks = [] #list to hold checks.
        in_check = False #boolean to represent wether king is under check or not.

        if self.turn:
            enemy = "b"
            ally = "w"
            king_row = self.white_king[0]
            king_col = self.white_king[1]
        else:
            enemy = "w"
            ally = "b"
            king_row = self.black_king[0]
            king_col = self.black_king[1]

        #left-down, right-up, left-up, right-down, up, down, left, right
        directions = [(1, -1), (-1, 1), (-1, -1), (1, 1), (-1, 0), (1, 0), (0, -1), (0, 1)]

        for j in range(len(directions)):
            d = directions[j]
            possible_pin = ()
            for i in range(1,8):
                row = king_row + d[0]*i
                col = king_col + d[1]*i
                
                #break the loop if any of the square is out of the board.
                if row < 0 or row > 7 or col < 0 or col > 7:
                    break
                piece = self.board[row][col] 
                if piece[0] == ally:
                    if piece[1] == 'K':
                        continue
                    #if an ally piece is found, it is a potential pinned piece.
                    if possible_pin == ():
                        possible_pin = (row, col, d[0], d[1])
                    #however if more than 1 ally piece are found in same direction there can't be any checks
                    #in same direction.
                    else:
                        break
                elif piece[0] == enemy:
                    #if an enemy piece is found, find all its possible moves
                    t = piece[1]
                    #possibilities for different pieces:
                    # 1) if t == 'R', then check all orthogonal directions
                    # 2) if t == 'B', then check all diagonal directions.
                    # 3) if t == 'Q, then check both diagonal and orthogonal directions.
                    # 4) if t == 'p', then check direction in which pawn captures.
                    # 5) if t == 'K' then check all direction.
                    if (0 <= j <= 3 and t == 'B') or (4 <= j <= 7 and t == 'R') or \
                        ((i == 1 and t == 'p') and ((enemy == 'b' and (j == 1 or j == 2)) or \
                        (enemy == 'w' and (j == 0 or j == 3)))) or \
                        (t == 'Q') or (i == 1 and t=='K'):
                        if possible_pin == ():
                            in_check = True
                            checks.append((row, col, d[0], d[1]))
                            break
                        else:
                            pins.append(possible_pin)
                            break
                    break
        #knight can check if it is at following positions away from the king
        knight_checks = [[king_row+1,king_col-2], [king_row+2,king_col-1], [king_row+2,king_col+1], 
                         [king_row+1,king_col+2], [king_row-1,king_col+2], [king_row-2,king_col+1], 
                         [king_row-2,king_col-1], [king_row-1,king_col-2]]
                         
        for check in knight_checks:
            row = check[0]
            col = check[1]
            if row < 0 or row > 7 or col < 0 or col > 7:
                continue
            if self.board[row][col][0] == enemy \
                and self.board[row][col][1] == 'N':
                in_check = True
                c = (row, col, check[0], check[1])
                checks.append(c)
        return in_check, pins, checks

    """
    This function gets all the possible moves at current game-state.
    """
    def all_possible_moves(self):
        moves = []
        for i in range(8):
            for j in range(8):
                turn = self.board[i][j][0]
                piece = self.board[i][j][1]
                if (turn == 'w' and self.turn) or (turn == 'b' and not self.turn):
                    self.moveFunctions[piece](i, j, moves)
        return moves

    """
    This function gets all the pawn moves from a given position i and j.
    """
    def get_pawn_moves(self, i, j, moves):
        pinned = False
        pin_direction = ()
        for r in range(len(self.pins)-1, -1, -1):
            if self.pins[r][0] == i and self.pins[r][1] == j:
                pinned = True
                pin_direction = (self.pins[r][2], self.pins[r][3])
                self.pins.remove(self.pins[r])
                break

        if self.turn:
            if self.board[i-1][j] == '--':
                if not pinned or pin_direction == (-1, 0):
                    moves.append(Move([i, j], [i-1, j], self.board))
                    if i == 6 and self.board[i-2][j] == '--':
                        moves.append(Move([i, j], [i-2, j], self.board))
            if j-1 >= 0:
                if self.board[i-1][j-1][0] == 'b':
                    if not pinned or pin_direction == (-1, -1):
                        moves.append(Move([i, j], [i-1, j-1], self.board))
                elif (i-1, j-1) == self.en_passant and not pinned:
                    moves.append(Move([i, j], [i-1, j-1], self.board, ep=True))
            if j+1 <= 7:
                if self.board[i-1][j+1][0] == 'b':
                    if not pinned or pin_direction == (-1, 1):
                        moves.append(Move([i, j], [i-1, j+1], self.board))
                elif (i-1, j+1) == self.en_passant and not pinned:
                    moves.append(Move([i, j], [i-1, j+1], self.board, ep=True))
        else:
            if self.board[i+1][j] == '--':
                if not pinned or pin_direction == (1, 0):
                    moves.append(Move([i, j], [i+1, j], self.board))
                    if i == 1 and self.board[i+2][j] == '--':
                        moves.append(Move([i, j], [i+2, j], self.board))
            if j-1 >= 0:
                if self.board[i+1][j-1][0] == 'w':
                    if not pinned or pin_direction == (1, -1):
                        moves.append(Move([i, j], [i+1, j-1], self.board))
                elif (i+1, j-1) == self.en_passant and not pinned:
                    moves.append(Move([i, j], [i+1, j-1], self.board, ep=True))
            if j+1 <= 7:
                if self.board[i+1][j+1][0] == 'w':
                    if not pinned or pin_direction == (1, 1):
                        moves.append(Move([i, j], [i+1, j+1], self.board))
                elif (i+1, j+1) == self.en_passant and not pinned:
                    moves.append(Move([i, j], [i+1, j+1], self.board, ep=True))


    """
    This function gets all the bishop moves from a given position i and j.
    """
    def get_bishop_moves(self, i, j, moves):
        pinned = False
        pin_direction = ()
        for r in range(len(self.pins)-1, -1, -1):
            if self.pins[r][0] == i and self.pins[r][1] == j:
                pinned = True
                pin_direction = (self.pins[r][2], self.pins[r][3])
                self.pins.remove(self.pins[r])
                break
        #bishop can have at most 7 possible move in one direction, so upperbound in for-loop is 7.
        #up-left, up-right, down-left, down-right
        directions = [(-1,-1),(-1,1),(1,-1),(1,1)]
        
        if pinned:
            pin_directions = [pin_direction, (-pin_direction[0], -pin_direction[1])]
            for p in pin_directions:
                if p in directions:
                    for r in range(1,8):
                        row = i + p[0]*r
                        col = j + p[1]*r
                        if col < 0 or col > 7 or row < 0 or row > 7:
                            break
                        if self.board[row][col] == "--":
                            moves.append(Move([i, j], [row, col], self.board))
                        elif (self.board[i][j][0] == 'w' and self.board[row][col][0] == 'b') or \
                            (self.board[i][j][0] == 'b' and self.board[row][col][0] == 'w'):
                            moves.append(Move([i, j], [row, col], self.board))
                            break
                        else:
                            break
        else:
            for d in directions:
                for r in range(1,8):
                    row = i + d[0]*r
                    col = j + d[1]*r
                    if col < 0 or col > 7 or row < 0 or row > 7:
                        break
                    if self.board[row][col] == "--":
                        moves.append(Move([i, j], [row, col], self.board))
                    elif (self.board[i][j][0] == 'w' and self.board[row][col][0] == 'b') or \
                        (self.board[i][j][0] == 'b' and self.board[row][col][0] == 'w'):
                        moves.append(Move([i, j], [row, col], self.board))
                        break
                    else:
                        break
            
    """
    This function gets all the rook moves from a given position i and j.
    """
    def get_rook_moves(self, i, j, moves):
        pinned = False
        pin_direction = ()
        for r in range(len(self.pins)-1, -1, -1):
            if self.pins[r][0] == i and self.pins[r][1] == j:
                pinned = True
                pin_direction = (self.pins[r][2], self.pins[r][3])
                self.pins.remove(self.pins[r])
                break
        #rook can have at most 7 possible move in one direction, so upperbound in for-loop is 7.
        #left, right, up, down respectively.
        directions = [(0,-1),(0,1),(-1,0),(1,0)]
        if pinned:
            pin_directions = [pin_direction, (-pin_direction[0], -pin_direction[1])]
            for p in pin_directions:
                if p in directions:
                    for r in range(1,8):
                        row = i + p[0]*r
                        col = j + p[1]*r
                        if col < 0 or col > 7 or row < 0 or row > 7:
                            break
                        if self.board[row][col] == "--":
                            moves.append(Move([i, j], [row, col], self.board))
                        elif (self.board[i][j][0] == 'w' and self.board[row][col][0] == 'b') or \
                            (self.board[i][j][0] == 'b' and self.board[row][col][0] == 'w'):
                            moves.append(Move([i, j], [row, col], self.board))
                            break
                        else:
                            break
        else:
            for d in directions:
                for r in range(1,8):
                    row = i + d[0]*r
                    col = j + d[1]*r
                    if col < 0 or col > 7 or row < 0 or row > 7:
                        break
                    if self.board[row][col] == "--":
                        moves.append(Move([i, j], [row, col], self.board))
                    elif (self.board[i][j][0] == 'w' and self.board[row][col][0] == 'b') or \
                        (self.board[i][j][0] == 'b' and self.board[row][col][0] == 'w'):
                        moves.append(Move([i, j], [row, col], self.board))
                        break
                    else:
                        break

    """
    This function gets all the king moves from a given position i and j.
    """
    def get_king_moves(self, i, j, moves):
        possible_moves = [[i-1,j-1], [i-1,j], [i-1,j+1], [i, j-1], [i, j+1], 
                          [i+1,j-1], [i+1,j], [i+1,j+1]]
        ally = "w" if self.turn else "b" 
        for (row, col) in possible_moves:
            if row < 0 or col < 0 or row > 7 or col > 7:
                continue
            piece = self.board[row][col]
            if piece[0] != ally:
                if ally == 'w':
                    self.white_king = (row, col)
                else: self.black_king = (row, col)
                in_check, pins, checks = self.pins_and_checks()
                if not in_check:
                    moves.append(Move([i, j], [row, col], self.board))
                if ally == 'w':
                    self.white_king = (i, j)
                else:
                    self.black_king = (i, j)
        self.get_castling_moves(i, j, moves, ally)

    """
    This is a helper function that finds possible castling moves.
    """
    def get_castling_moves(self, i, j, moves, ally):
        in_check, pins, checks = self.pins_and_checks()
        if in_check:
            return
        if (ally == 'w' and self.current_castling_rights.wks) or (ally == 'b' and self.current_castling_rights.bks):
            self.get_king_side(i, j, moves, ally)
        if (ally == 'w' and self.current_castling_rights.wqs) or (ally == 'b' and self.current_castling_rights.bqs):
            self.get_queen_side(i, j, moves, ally)


    """
    This is a helper function that finds king side castling moves.
    """
    def get_king_side(self, i, j, moves, ally):
        if self.board[i][j+1] == '--' and self.board[i][j+2] == '--':
            if ally == 'w':
                (row, col) = (self.white_king[0], self.white_king[1])
                self.white_king = (i, j+1)
                in_check, pins, checks = self.pins_and_checks()
                if in_check:
                    self.white_king = (row, col)
                    return
                else:
                    self.white_king = (i, j+2)
                    in_check, pins, checks = self.pins_and_checks()
                    if in_check:
                        self.white_king = (row, col)
                        return
                    else:
                        moves.append(Move([i, j], [i, j+2], self.board, is_castle=True))
                        moves.append(Move([i, j], [i, j+3], self.board, is_castle=True))
                        self.white_king = (row, col)
            elif ally == 'b':
                (row, col) = (self.black_king[0], self.black_king[1])
                self.black_king = (i, j+1)
                in_check, pins, checks = self.pins_and_checks()
                if in_check:
                    self.black_king = (row, col)
                    return
                else:
                    self.black_king = (i, j+2)
                    in_check, pins, checks = self.pins_and_checks()
                    if in_check:
                        self.black_king = (row, col)
                        return
                    else:
                        moves.append(Move([i, j], [i, j+2], self.board, is_castle = True))
                        moves.append(Move([i, j], [i, j+3], self.board, is_castle = True))
                        self.black_king = (row, col)

    """
    This is a helper function that finds queen side castling moves.
    """
    def get_queen_side(self, i, j, moves, ally):
        if self.board[i][j-1] == '--' and self.board[i][j-2] == '--' and self.board[i][j-3] == '--':
            if ally == 'w':
                (row, col) = (self.white_king[0], self.white_king[1])
                self.white_king = (i, j-1)
                in_check, pins, checks = self.pins_and_checks()
                if in_check:
                    self.white_king = (row, col)
                    return
                else:
                    self.white_king = (i, j-2)
                    in_check, pins, checks = self.pins_and_checks()
                    if in_check:
                        self.white_king = (row, col)
                        return
                    else:
                        self.white_king = (i, j-3)
                        in_check, pins, checks = self.pins_and_checks()
                        if in_check:
                            self.white_king = (row, col)
                            return
                        else:
                            moves.append(Move([i, j], [i, j-2], self.board, is_castle=True))
                            moves.append(Move([i, j], [i, j-3], self.board, is_castle=True))
                            moves.append(Move([i, j], [i, j-4], self.board, is_castle=True))
                            self.white_king = (row, col)
            elif ally == 'b':
                (row, col) = (self.black_king[0], self.black_king[1])
                self.black_king = (i, j-1)
                in_check, pins, checks = self.pins_and_checks()
                if in_check:
                    self.black_king = (row, col)
                    return
                else:
                    self.black_king = (i, j-2)
                    in_check, pins, checks = self.pins_and_checks()
                    if in_check:
                        self.black_king = (row, col)
                        return
                    else:
                        self.black_king = (i, j-3)
                        in_check, pins, checks = self.pins_and_checks()
                        if in_check:
                            self.black_king = (row, col)
                            return
                        else:
                            moves.append(Move([i, j], [i, j-2], self.board, is_castle=True))
                            moves.append(Move([i, j], [i, j-3], self.board, is_castle=True))
                            moves.append(Move([i, j], [i, j-4], self.board, is_castle=True))
                            self.black_king = (row, col)

    """
    This function gets all queen moves from given position i an j.
    """
    def get_queen_moves(self, i, j, moves):
        pinned = False
        pin_direction = ()
        for r in range(len(self.pins)-1, -1, -1):
            if self.pins[r][0] == i and self.pins[r][1] == j:
                pinned = True
                pin_direction = (self.pins[r][2], self.pins[r][3])
                self.pins.remove(self.pins[r])
                break
        #if queen is pinned, it can only move in direction of pin.
        if pinned:
            pin_directions = [pin_direction, (-pin_direction[0], -pin_direction[1])]
            directions = [(0,-1),(0,1),(-1,0),(1,0),(-1,-1),(-1,1),(1,-1),(1,1)]
            for p in pin_directions:
                if p in directions:
                    for r in range(1,8):
                        row = i + p[0]*r
                        col = j + p[1]*r
                        if col < 0 or col > 7 or row < 0 or row > 7:
                            break
                        if self.board[row][col] == "--":
                            moves.append(Move([i, j], [row, col], self.board))
                        elif (self.board[i][j][0] == 'w' and self.board[row][col][0] == 'b') or \
                            (self.board[i][j][0] == 'b' and self.board[row][col][0] == 'w'):
                            moves.append(Move([i, j], [row, col], self.board))
                            break
                        else:
                            break
        else:
            #queen has all possible moves of a rook and a bishop at position [i,j]
            self.get_bishop_moves(i, j, moves)
            self.get_rook_moves(i, j, moves)

    """
    This function gets all possible knight moves from given position i and j.
    """
    def get_knight_moves(self, i, j, moves):
        pinned = False
        pin_direction = ()
        for r in range(len(self.pins)-1, -1, -1):
            if self.pins[r][0] == i and self.pins[r][1] == j:
                pinned = True
                pin_direction = (self.pins[r][2], self.pins[r][3])
                self.pins.remove(self.pins[r])
                break
        #if knight is pinned, it can not move so return.
        if pinned:
            return
        #else following are the possible knight moves.
        possible_moves = [[i+1,j-2], [i+2,j-1], [i+2,j+1], [i+1,j+2], [i-1,j+2], [i-2,j+1], [i-2,j-1], [i-1,j-2]]  
        for move in possible_moves:
            if move[0] < 0 or move[1] < 0 or move[0] > 7 or move[1] > 7:
                continue
            if self.board[move[0]][move[1]] == "--":
                moves.append(Move([i,j], move, self.board))
            elif (self.board[i][j][0] == 'w' and self.board[move[0]][move[1]][0] == 'b') or \
                 (self.board[i][j][0] == 'b' and self.board[move[0]][move[1]][0] == 'w'):
                moves.append(Move([i,j], move, self.board))


class Move(object):
    """
    These are mappings to convert chess notations to array indexes.
    """
    file_to_col = {'a' : 0, 'b' : 1, 'c' : 2, 'd' : 3, 'e' : 4,
                   'f' : 5, 'g' : 6, 'h' : 7 }

    col_to_file = {0 : 'a', 1 : 'b', 2 : 'c', 3 : 'd', 4 : 'e',
                   5 : 'f', 6 : 'g', 7 : 'h' }

    row_to_rank = {0 : '8', 1 : '7', 2 : '6', 3 : '5', 4 : '4',
                   5 : '3', 6 : '2', 7 : '1' }

    rank_to_row = {'8': 0, '7': 1, '6': 2, '5': 3, '4': 4,
                   '3': 5, '2': 6, '1': 7 }
    
    def __init__(self, startsq, endsq, board, ep=False, is_castle=False):
        self.startrow = startsq[0]
        self.startcol = startsq[1]
        self.endrow = endsq[0]
        self.endcol = endsq[1]
        self.piece_moved = board[self.startrow][self.startcol]
        self.piece_captured = board[self.endrow][self.endcol]
        #pawn promotion
        self.pawn_promotion = (self.piece_moved == "wp" and self.endrow == 0) or (self.piece_moved == "bp" and self.endrow == 7)
        self.is_en_passant = ep
        self.is_castle = is_castle
        self.move_id = 1000*self.startrow + 100*self.startcol + 10*self.endrow + self.endcol
    
    """
    Override equals method. 
    """
    def __eq__(self, other):
        if isinstance(other, Move):
            return self.move_id == other.move_id

    def __str__(self):
        return self.generate_notation()
    
    def generate_notation(self):
        name = self.piece_moved[1]
        if name == 'p':
            name = ''
        notation = name + self.col_to_file[self.endcol] + self.row_to_rank[self.endrow]
        if self.piece_captured != "--":
            notation = (self.col_to_file[self.startcol] + self.row_to_rank[self.startrow] 
                       + 'x' + self.col_to_file[self.endcol] + self.row_to_rank[self.endrow])
        return notation


class CastlingRights(object):
    def __init__(self, wks, wqs, bks, bqs):
        self.wks = wks
        self.wqs = wqs
        self.bks = bks
        self.bqs = bqs
