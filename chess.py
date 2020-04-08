import math
import pygame


# alphaValueOffset = 0x41

# returns position from index
# def index2pos(index):
#    return (index%8,math.floor(index/8)*8)

# returns index from position
def pos2index(pos):
    return pos[0] + pos[1] * 8


# returns index from a string
# def str2index(str):
#    return pos2index(str2pos(str))

# returns the position within the chessboard
# def str2pos(str):
#    return ((ord(str.upper()[0])-alphaValueOffset) % 8,int(str[1])-1)

# gives the string into a position
# def pos2str(pos):
#    return chr( (pos[0]-alphaValueOffset) % 8).upper() + str(pos[1]+1)

class piece:
    # basic parameters that every piece must have
    pos = (0, 0)
    board = None
    team = -1
    spritesheet = (pygame.image.load("chesspieces.png"), 75)
    spriteIndex = (0, 0)
    canRender = True
    hadLastMove = False
    hasMoved = False
    validMoves = []
    threat = []
    semiThreat = []
    char = ["?"]

    # initilalizer of the piece class. in java terms, the constructor.
    def __init__(self, board, pos, team):
        self.pos = pos
        self.team = team
        self.board = board
        self.hasMoved = False
        self.threat = []
        self.validMoves = []
        self.semiThreat = []
        self.hadLastMove = False
        self.canRender = True

    # renders the piece itself
    def render(self, surface):
        if (self.canRender):
            s = self.spritesheet
            # using the position the piece itself and it's spritesheet, draws the piece onto the board.
            surface.blit(s[0], (self.pos[0] * s[1], self.pos[1] * s[1]), (
            (self.spriteIndex[self.team] % 6) * s[1], math.floor(self.spriteIndex[self.team] / 6) * s[1], s[1], s[1]))

    # function that updates the piece location for the piece. updates the board.
    def moveTo(self, pos):
        if (self.canMoveTo(pos)):
            self.hasMoved = True
            p2 = self.board.getPieceAt(pos)  # other piece
            self.board.setPieceAt(pos, self)
            self.board.setPieceAt(self.pos, None)
            self.pos = pos
            if (p2):  # if the piece exists, kill it
                p2.kill()
                return True, True
            return True, False
        return False, False

    # function that shows all valid moves after there is a hover or click
    def canMoveTo(self, pos):
        return pos in self.validMoves

    def kill(self):
        pass;

    # updater for when after a piece moves, to add another valid move
    def update(self):
        self.validMoves = []
        for i in self.threat:
            s = self.board.getPieceAt(i)
            if ((not s) or (
                    s and s.team != self.team)):  # if the piece is not on same team, adds the tile to validMoves
                self.validMoves.append(i)

    def afterUpdate(self):
        pass;

    def __str__(self):
        return self.char[self.team % 2]


# king class
class king(piece):
    char = ['K', 'k']
    spriteIndex = (6, 0)  # the index of the sprite within spritesheet itself

    # different render fucntion for a king. this is because check is not the same as damage.
    def render(self, surface):
        if (self.board.isThreatend(self.pos, self.team)):
            pygame.draw.rect(surface, (200, 100, 0), (self.pos[0] * 75, self.pos[1] * 75, 75, 75))
        super(king, self).render(surface)

    # move method for king. special because it need to check for the threatened after
    def moveTo(self, pos):
        i2 = self.board.getPieceAt(pos)
        if (i2 and isinstance(i2, rook) and (not isinstance(i2, queen))):
            if (i2.canMoveTo(self.pos)):
                return i2.moveTo(self.pos)
            else:
                return False, False
        else:
            return super(king, self).moveTo(pos)

    def afterUpdate(self):
        threats = self.board.threatenedBy(self.pos, self.team)
        semi = self.board.threatenedBy(self.pos, self.team, True)
        vM = self.validMoves
        self.validMoves = []
        anyMove = False
        for i in vM:
            tS = self.board.threatenedBy(i, self.team)

            if (len(tS) <= 0):
                sM = self.board.threatenedBy(i, self.team, True)
                if (len(sM) > 0):
                    for k in sM:
                        if (not k in threats):
                            self.validMoves += [i]
                            break
                else:
                    self.validMoves += [i]

        if (len(self.validMoves) > 0):
            anyMove = True
        for i in self.board.board:
            if (i != self):
                if (i and i.team == self.team):
                    if (len(threats) == 1):
                        rC = self.board.raycast(self.pos, threats[0].pos)
                        vM = i.validMoves
                        i.validMoves = []
                        for j in vM:
                            if (j in rC):
                                i.validMoves += [j]
                    elif (len(threats) > 1):
                        i.validMoves = []
                    elif (len(semi) > 0):
                        for j in semi:
                            if (not len(i.validMoves) > 0):
                                break
                            if (i.pos in j.threat):
                                rCast = self.board.raycast(i.pos, j.pos)
                                vM = i.validMoves
                                i.validMoves = []
                                for v in vM:
                                    if ((v in j.threat and v in rCast) or v == j.pos):
                                        i.validMoves += [v]
                    if (len(i.validMoves) > 0):
                        anyMove = True

        if (not anyMove):
            if (len(threats) > 0):
                self.board.winner = ((self.team + 1) % 2)
            else:
                self.board.winner = 2

    def update(self):
        s = self.pos
        self.threat = []
        self.validMoves = []
        for i in range(9):
            nPos = (s[0] + (i % 3) - 1, s[1] + (int(i / 3)) - 1)
            if (nPos == s or nPos[0] < 0 or nPos[1] < 0 or nPos[0] > 7 or nPos[1] > 7):
                continue
            self.threat.append(nPos)
        super(king, self).update()
        if (not self.board.isThreatend(self.pos, self.team)):
            posT = [self.board.firstEncounter(self.pos, (self.pos[0] - 8, self.pos[1])),
                    self.board.firstEncounter(self.pos, (self.pos[0] + 8, self.pos[1]))]
            for p in posT:
                if (p):
                    i1 = self.board.getPieceAt(p)
                    if (i1):
                        i1.update()
                        if i1.canMoveTo(self.pos):
                            self.validMoves += [p]


class bishop(piece):
    char = ["B", "b"]
    spriteIndex = (8, 2)

    def update(self):
        self.threat = []
        self.threat += self.board.raycast(self.pos, (self.pos[0] + 8, self.pos[1] + 8))
        self.threat += self.board.raycast(self.pos, (self.pos[0] - 8, self.pos[1] + 8))
        self.threat += self.board.raycast(self.pos, (self.pos[0] + 8, self.pos[1] - 8))
        self.threat += self.board.raycast(self.pos, (self.pos[0] - 8, self.pos[1] - 8))
        self.semiThreat = []
        self.semiThreat += self.board.raycast(self.pos, (self.pos[0] + 8, self.pos[1] + 8), 2)
        self.semiThreat += self.board.raycast(self.pos, (self.pos[0] - 8, self.pos[1] + 8), 2)
        self.semiThreat += self.board.raycast(self.pos, (self.pos[0] + 8, self.pos[1] - 8), 2)
        self.semiThreat += self.board.raycast(self.pos, (self.pos[0] - 8, self.pos[1] - 8), 2)

        piece.update(self)


class rook(piece):
    char = ["R", "r"]
    spriteIndex = (10, 4)

    # move function that accomodates for castling
    def moveTo(self, pos):
        i2 = self.board.getPieceAt(pos)  # other piece at position.
        if (i2 and (not isinstance(self, queen)) and isinstance(i2, king) and i2.team == self.team):  # if it's a king
            if (self.canMoveTo(pos)):  # castle
                nPosK = (int(i2.pos[0] + 2 * math.copysign(1, self.pos[0] - i2.pos[0])), self.pos[1])
                nPosS = (int(nPosK[0] + math.copysign(1, -self.pos[0] + i2.pos[0])), self.pos[1])
                self.board.swapPieces(self.pos, nPosS)
                self.board.swapPieces(i2.pos, nPosK)
                self.pos = nPosS
                i2.pos = nPosK
                self.hasMoved = True
                i2.hasMoved = True
                return True, False
        else:
            return super(rook, self).moveTo(pos)
        return False, False

    def update(self):
        self.threat = []
        self.threat += self.board.raycast(self.pos, (self.pos[0] + 8, self.pos[1]))
        self.threat += self.board.raycast(self.pos, (self.pos[0] - 8, self.pos[1]))
        self.threat += self.board.raycast(self.pos, (self.pos[0], self.pos[1] - 8))
        self.threat += self.board.raycast(self.pos, (self.pos[0], self.pos[1] + 8))
        self.semiThreat = []
        self.semiThreat += self.board.raycast(self.pos, (self.pos[0] + 8, self.pos[1]), 2)
        self.semiThreat += self.board.raycast(self.pos, (self.pos[0] - 8, self.pos[1]), 2)
        self.semiThreat += self.board.raycast(self.pos, (self.pos[0], self.pos[1] - 8), 2)
        self.semiThreat += self.board.raycast(self.pos, (self.pos[0], self.pos[1] + 8), 2)

        piece.update(self)
        if ((not self.hasMoved) and (not isinstance(self, queen))):
            p2 = self.board.firstEncounter(self.pos, (self.pos[0] + 8, self.pos[1])) or self.board.firstEncounter(
                self.pos, (self.pos[0] - 8, self.pos[1]))
            if (p2 and not self.board.isThreatend(p2, self.team)):
                i2 = self.board.getPieceAt(p2)
                if (i2 and isinstance(i2, king) and (not i2.hasMoved)):
                    tTest = self.board.raycast(p2, (p2[0] - 2 * math.copysign(1, -self.pos[0] + p2[0]), p2[1]))
                    for i in tTest:
                        if (self.board.isThreatend(i, self.team)):
                            return
                    self.validMoves += [p2]


class pawn(piece):
    char = ["P", "p"]
    spriteIndex = (11, 5)
    movedTwice = False  # for the initial move. has capability to move twice

    def __init__(self, board, pos, team):
        piece.__init__(self, board, pos, team)
        self.movedTwice = False

    def moveTo(self, pos):
        xDiff = -self.pos[0] + pos[0]
        yDiff = -self.pos[1] + pos[1]

        r, r2 = super(pawn, self).moveTo(pos)
        self.movedTwice = r and abs(yDiff) > 1
        if (r and not r2 and abs(yDiff) == 1 and abs(xDiff) == 1):
            p2 = (pos[0], pos[1] + (self.team * 2 - 1))
            i2 = self.board.getPieceAt(p2)
            self.board.setPieceAt(p2, None)
            i2.kill()
        if (r and ((pos[1] + 1) % 8) == self.team):  # team is integer, so if it's in the row, it can promote
            while (True):
                try:
                    piece_in = int(input("Pawn Promotion. 1: queen, 2: knight, 3: bishop, 4: rook: "))
                    obj = queen(self.board, pos, self.team)
                    if (piece_in == 2):
                        obj = knight(self.board, pos, self.team)
                    if (piece_in == 3):
                        obj = bishop(self.board, pos, self.team)
                    if (piece_in == 4):
                        obj = rook(self.board, pos, self.team)

                    self.board.setPieceAt(pos, obj)
                    break
                except Exception:  # random thing
                    pass
        return r, r2

    def update(self):
        pos = self.pos
        self.threat = [(pos[0] - 1, pos[1] - (self.team * 2 - 1)),
                       (pos[0] + 1, pos[1] - (self.team * 2 - 1))]  # the squares it can attack
        self.validMoves = []

        for i in self.threat:
            p = self.board.getPieceAt(i)
            if (p and p.team != self.team):  # if square is threatening has enemy piece.
                self.validMoves += [i]  # add to valid moves

        p1 = (pos[0], self.pos[1] - (self.team * 2 - 1))
        p2 = (pos[0], self.pos[1] - (self.team * 2 - 1) * 2)

        if (not self.board.getPieceAt(p1)):  # if there isn't a piece there
            self.validMoves += [p1]
        if (not self.hasMoved):
            if (not self.board.firstEncounter(pos, p2)):
                self.validMoves += [p2]  # pawn jumping

        p3 = (pos[0] - 1, pos[1])
        p4 = (pos[0] + 1, pos[1])
        i3 = self.board.getPieceAt(p3)
        i4 = self.board.getPieceAt(p4)

        # en passant
        if (i3 and i3.hadLastMove and isinstance(i3, pawn) and i3.movedTwice and i3.team != self.team):
            self.validMoves += [(pos[0] - 1, pos[1] - (self.team * 2 - 1))]
        elif (i4 and i4.hadLastMove and isinstance(i4, pawn) and i4.movedTwice and i4.team != self.team):
            self.validMoves += [(pos[0] + 1, pos[1] - (self.team * 2 - 1))]


class knight(piece):
    char = ["N", "n"]

    spriteIndex = (9, 3)
    '''
    def canMoveTo(self,pos):
        p2 = self.board.getPieceAt(pos);
        if((not p2) or (p2.team != self.team)):
            return (abs(self.pos[0]-pos[0]) == 2 and
                    abs(self.pos[1]-pos[1]) == 1) or (
                    abs(self.pos[1]-pos[1]) == 2 and
                    abs(self.pos[0]-pos[0]) == 1);
    '''

    def update(self):
        self.threat = []
        cPos = [(self.pos[0] + 2, self.pos[1] + 1),
                (self.pos[0] + 2, self.pos[1] - 1),
                (self.pos[0] - 2, self.pos[1] + 1),
                (self.pos[0] - 2, self.pos[1] - 1),
                (self.pos[0] + 1, self.pos[1] + 2),
                (self.pos[0] + 1, self.pos[1] - 2),
                (self.pos[0] - 1, self.pos[1] + 2),
                (self.pos[0] - 1, self.pos[1] - 2)]

        for i in cPos:
            if (i[0] >= 0 and i[0] < 8 and i[1] < 8 and i[1] >= 0):  # case work for it movement is off board.
                self.threat.append(i)  # appends all threats.
                o = self.board.getPieceAt(i)

        super(knight, self).update()


class queen(rook, bishop):  # queen is a subclass of both the rook and bishop
    char = ["Q", "q"]
    spriteIndex = (7, 1)

    def update(self):
        rook.update(self)
        a = self.threat
        b = self.validMoves
        c = self.semiThreat
        bishop.update(self)
        self.threat += a
        self.validMoves += b
        self.semiThreat += c


class chessboard:
    board = [None] * (8 * 8)  # board of size 64
    currentTeam = 0  # determines which side goes first
    background = pygame.image.load("chessbg2.png")
    winner = -1  # sentinel
    lastPiece = None

    # constructor
    def __init__(self):

        self.board = [None] * (8 * 8)
        self.winner = -1
        self.lastPiece = None
        self.currentTeam = 1
        pass

    def regularBoard(self):
        # white pieces
        self.board[0:7] = [rook(self, (0, 0), 0), knight(self, (1, 0), 0), bishop(self, (2, 0), 0),
                           queen(self, (3, 0), 0),
                           king(self, (4, 0), 0), bishop(self, (5, 0), 0), knight(self, (6, 0), 0),
                           rook(self, (7, 0), 0)]
        self.board[8:15] = [pawn(self, (i, 1), 0) for i in range(8)]

        # black pieces
        self.board[pos2index((0, 7)) - 1:pos2index((7, 7)) - 1] = [rook(self, (0, 7), 1), knight(self, (1, 7), 1),
                                                                   bishop(self, (2, 7), 1), queen(self, (3, 7), 1),
                                                                   king(self, (4, 7), 1), bishop(self, (5, 7), 1),
                                                                   knight(self, (6, 7), 1), rook(self, (7, 7), 1)]
        self.board[pos2index((0, 6)):pos2index((7, 6))] = [pawn(self, (i, 6), 1) for i in range(8)]

    # casteling method.
    def castelingTestBoard(self):
        self.board[0:7] = [rook(self, (0, 0), 0), None, None, None,
                           king(self, (4, 0), 0), None, None, rook(self, (7, 0), 0)]
        self.board[pos2index((0, 7)):pos2index((7, 7)) - 1] = [rook(self, (0, 7), 1), None, None, None,
                                                               queen(self, (4, 7), 1), None, None,
                                                               rook(self, (7, 7), 1)]

    def updateAll(self):
        for i in self.board:
            if (i):
                i.update()

    def afterUpdate(self):
        for i in self.board:
            if (i):
                i.afterUpdate()

    def setBoard(self, board):
        for i, v in enumerate(board):
            board[i] = v

    def move(self, pos1, pos2):
        # not the same position, no winner
        if not (pos1 == pos2 and self.winner == -1):
            try:
                b1 = self.board[pos2index(pos1)]
                if (b1 and (b1.team == self.currentTeam or b1.team == -1)):
                    if (b1.moveTo(pos2)[0]):
                        if (self.lastPiece):
                            self.lastPiece.hadLastMove = False
                        self.lastPiece = b1
                        b1.hadLastMove = True
                        self.currentTeam = (self.currentTeam + 1) % 2
                        self.updateAll()
                        self.updateAll()
                        self.afterUpdate()
                        if (self.winner != -1):
                            print("Game over!")
                            if (self.winner < 2):
                                print("The winner is {}".format(("white", "black")[self.winner]))
                            else:
                                print("The game was a draw")
                        return True
                    else:
                        return False
            except IndexError:
                return False

    # setter ,emthod for the pieece
    def setPieceAt(self, pos, piece):
        self.board[pos2index(pos)] = piece

    # switches pieces around
    def swapPieces(self, pos1, pos2):
        self.board[pos2index(pos1)], self.board[pos2index(pos2)] = self.board[pos2index(pos2)], self.board[
            pos2index(pos1)]

    # returns piece
    def getPieceAt(self, pos):
        return self.board[pos2index(pos)]

    # used in castleing and en passant
    def firstEncounter(self, pos, pos2, maxOcc=1):
        diffX = -pos[0] + pos2[0]
        diffY = -pos[1] + pos2[1]
        cPos = pos
        first = True

        for i in self.raycast(pos, pos2, maxOcc):
            if (self.getPieceAt(i)):
                return i

    # king function. shows which piece it is the one that is threatening
    def threatenedBy(self, pos, team, semi=False):
        t = []
        for i in self.board:
            if (i and i.team != team):
                if (semi and pos in i.semiThreat):
                    t += [i]
                elif (pos in i.threat):
                    t += [i]
        return t

    def isThreatend(self, pos, team, semi=False):
        for i in self.board:
            if (i and i.team != team):
                if (semi and pos in i.semiThreat):
                    return True
                if (pos in i.threat):
                    return True

        return False

    # attack move. ray of where it can move.
    def raycast(self, pos, pos2, maxocc=1):
        diffX = -pos[0] + pos2[0]  # difference in x-coord
        diffY = -pos[1] + pos2[1]  # diff in y-coord
        cPos = pos
        cells = []  # all of the cells that the ray contains
        first = True

        try:
            inc = diffY / diffX
        except ZeroDivisionError:
            inc = "inf"

        for i in range(8):
            if (not first and self.getPieceAt((int(cPos[0]), int(cPos[1])))):
                maxocc -= 1  # maximum occurence

            if (cPos == pos2 or maxocc <= 0):
                return cells
            cPos = (cPos[0] + (0 if inc == "inf" else math.copysign(1, diffX)),
                    cPos[1] + (math.copysign(1, diffY) if inc == "inf" else inc * math.copysign(1, diffX)))
            if (not (cPos[0] < 0 or cPos[0] > 7 or cPos[1] < 0 or cPos[1] > 7)):  # if it's within bounds
                cells.append((int(cPos[0]), int(cPos[1])))  # adds tile to the cells being casted on
            else:
                return cells

            first = False

    def renderBG(self, surface):  # renders the bg, simple
        surface.blit(self.background, (0, 0), (0, 0, 600, 600))

    def renderPieces(self, surface):
        for i in self.board:
            if (i):
                i.render(surface)


# useless function for text
# def getMove():
#     while(True):
#         try:
#             in1 = input("Next move: ").split(" ");
#             p1 = str2pos(in1[0])
#             p2 = str2pos(in1[1])
#             return p1,p2
#         except Exception:
#             print("Bad input")

def main():
    screenSize = 600, 600  # screen
    chessGame = chessboard()
    chessGame.regularBoard()
    chessGame.updateAll()
    chessGame.updateAll()
    chessGame.afterUpdate()
    display = pygame.display.set_mode(screenSize)
    pygame.display.set_caption("chowChess")
    runGame = True
    time = 0
    clock = pygame.time.Clock()
    pieceInHand = None  # variable for piece in hand
    mPos = (0, 0)  # mouse position
    mOffset = (0, 0)  # mouse offset
    while (runGame):
        mPos = pygame.mouse.get_pos()  # tracks position of mouse
        for event in pygame.event.get():  # all events
            if (event.type == pygame.QUIT):
                runGame = False

            if (chessGame.winner == -1):  # no winner
                if (event.type == 5):
                    # Mouse click
                    piceaz = chessGame.getPieceAt((int(mPos[0] / 75), int(mPos[1] / 75)))
                    if (piceaz and piceaz.team == chessGame.currentTeam):  # only if it's the current team
                        mOffset = (int(mPos[0] % 75), int(mPos[1] % 75))  # offset for mouse
                        if (pieceInHand):  # if the piece is in hand, allows to render piece while dragging
                            pieceInHand.canRender = True
                        piceaz.canRender = False
                        pieceInHand = piceaz
                        # pieceInHand.update()

            if (event.type == 6):  # if mousebutton up, place the piece down.
                if (pieceInHand):
                    if (chessGame.move(pieceInHand.pos, (int(mPos[0] / 75), int(mPos[1] / 75)))):
                        pieceInHand.canRender = True
                        pieceInHand = None
        display.fill((0, 0, 0))

        chessGame.renderBG(display)

        if (pieceInHand):
            dPm = pieceInHand
        else:
            dPm = chessGame.getPieceAt((int(mPos[0] / 75), int(mPos[1] / 75)))
        if (
                dPm and dPm.team == chessGame.currentTeam):  # if there is a piece in hand and the piece is same as the current team
            for i in dPm.validMoves:  # for all validmoves, shows them
                c = (0, 200, 80)
                pAt = chessGame.getPieceAt(i)  # get the peice on the valid move
                if (pAt):
                    if (pAt.team != dPm.team):  # if peice on valid move is not same as own team
                        c = (200, 0, 80)
                    else:
                        c = (0, 0, 220)
                pygame.draw.rect(display, c, (i[0] * 75, i[1] * 75, 75, 74
                                              ))

        chessGame.renderPieces(display)
        if (pieceInHand):  # allowing dragging function
            p = pieceInHand
            s = pieceInHand.spritesheet
            display.blit(s[0], (mPos[0] - mOffset[0], mPos[1] - mOffset[1]),
                         ((p.spriteIndex[p.team] % 6) * s[1], math.floor(p.spriteIndex[p.team] / 6) * s[1], s[1], s[1]))
        clock.tick(60)
        pygame.display.update()
        time += 0.1
