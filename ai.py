import time
import random
from board import *

class AI(Board):
    def __init__(self):
        super().__init__()
        self.total = 0
        self.hash_count = 0
        self.search_depth = 0
        self.time_left = 10000000
        self.timeout_turn = 5000
        self.timeout_match = 10000000
        self.think_time = 0
        self.best_point = Point()
        self.best_line = Line()
        self.start = 0
        self.stop_think = False
        # Evaluation values for different patterns
        self.eval = [0, 2, 12, 18, 96, 144, 800, 1200]

    def get_time(self):
        """Return elapsed search time in milliseconds"""
        return (time.time() - self.start) * 1000

    def stop_time(self):
        """Return available search time for this move"""
        return min(self.timeout_turn, self.time_left // 7)

    def probe_hash(self, depth, alpha, beta):
        """Query the transposition table"""
        p_hashe = self.hash_table[self.zobrist_key & (HASH_SIZE - 1)]
        if p_hashe.key == self.zobrist_key:
            if p_hashe.depth >= depth:
                if p_hashe.hashf == HASH_EXACT:
                    return p_hashe.val
                elif p_hashe.hashf == HASH_ALPHA and p_hashe.val <= alpha:
                    return p_hashe.val
                elif p_hashe.hashf == HASH_BETA and p_hashe.val >= beta:
                    return p_hashe.val
        return UNKNOWN

    def record_hash(self, depth, val, hashf):
        """Write to transposition table"""
        p_hashe = self.hash_table[self.zobrist_key & (HASH_SIZE - 1)]
        p_hashe.key = self.zobrist_key
        p_hashe.val = val
        p_hashe.hashf = hashf
        p_hashe.depth = depth

    def put_chess(self, next_pos):
        """Place a chess piece on the board (interface method)"""
        next_pos.x += 4
        next_pos.y += 4
        self.make_move(next_pos)

    def get_best_move(self):
        """Find and return the best move"""
        best = self.main_search()
        best.x -= 4
        best.y -= 4
        
        # Output thinking information
        print(f"MESSAGE depth={self.search_depth} NPS={self.total // (self.think_time + 1)}k")
        print(f"MESSAGE best: [{best.x},{best.y}] val={self.best_point.val}")
        print("MESSAGE bestLine:", end="")
        for i in range(self.best_line.n):
            print(f" [{self.best_line.moves[i].x - 4},{self.best_line.moves[i].y - 4}]", end="")
        print()
        
        return best

    def main_search(self):
        """Main search function to find the best move"""
        self.start = time.time()
        self.total = 0
        self.hash_count = 0
        
        best_move = Pos()
        
        # First move at center
        if self.step == 0:
            best_move.x = self.size // 2 + 4
            best_move.y = self.size // 2 + 4
            return best_move
        
        # Second and third moves randomly around first move
        if self.step == 1 or self.step == 2:
            rx, ry = 0, 0
            random.seed(time.time())
            while True:
                rx = self.rem_move[0].x + random.randint(-self.step, self.step)
                ry = self.rem_move[0].y + random.randint(-self.step, self.step)
                if self.check_xy(rx, ry) and self.cell[rx][ry].piece == Pieces.EMPTY.value:
                    break
            best_move.x = rx
            best_move.y = ry
            return best_move
        
        # Iterative deepening search
        self.stop_think = False
        self.best_point.val = 0
        self.ply = 0
        self.is_lose = [[False for _ in range(MAX_SIZE + 4)] for _ in range(MAX_SIZE + 4)]
        
        for i in range(MIN_DEPTH, MAX_DEPTH + 1, 2):
            if self.stop_think:
                break
            self.search_depth = i
            self.best_point = self.root_search(self.search_depth, -10001, 10000, self.best_line)
            if self.stop_think or (self.search_depth >= 10 and 
                                 self.get_time() >= 1000 and 
                                 self.get_time() * 12 > self.stop_time()):
                break
        
        self.think_time = self.get_time()
        best_move = self.best_point.p
        
        return best_move

    def root_search(self, depth, alpha, beta, pline):
        """Root node search with additional move ordering"""
        best = self.root_move[0]
        line = Line()
        
        if depth == MIN_DEPTH:
            moves = [Pos() for _ in range(64)]
            self.root_count = self.generate_move(moves)
            
            # Only one valid move, return directly
            if self.root_count == 1:
                self.stop_think = True
                best.p = moves[0]
                best.val = 0
                pline.n = 0
                return best
            
            for i in range(self.root_count):
                self.root_move[i].p = moves[i]
        else:
            # Sort moves by value
            for i in range(1, self.root_count):
                if self.root_move[i].val > self.root_move[0].val:
                    temp = self.root_move[0]
                    self.root_move[0] = self.root_move[i]
                    self.root_move[i] = temp
        
        # Traverse possible moves
        for i in range(self.root_count):
            # Search non-losing points
            p = self.root_move[i].p
            if not self.is_lose[p.x][p.y]:
                line.n = 0
                self.make_move(p)
                
                # PVS Search
                if i > 0 and alpha + 1 < beta:
                    val = -self.alpha_beta(depth - 1, -alpha - 1, -alpha, line)
                    if val > alpha and val < beta:
                        val = -self.alpha_beta(depth - 1, -beta, -alpha, line)
                else:
                    val = -self.alpha_beta(depth - 1, -beta, -alpha, line)
                
                self.del_move()
                
                self.root_move[i].val = val
                
                if self.stop_think:
                    break
                
                if val == -10000:
                    self.is_lose[p.x][p.y] = True
                
                if val > alpha:
                    alpha = val
                    best.p = p
                    best.val = val
                    
                    # Save best line
                    pline.moves[0] = p
                    for j in range(line.n):
                        pline.moves[j + 1] = line.moves[j]
                    pline.n = line.n + 1
                    
                    # Found winning move
                    if val == 10000:
                        self.stop_think = True
                        return best
        
        return best

    def get_next_move(self, move_list):
        """
        Phase 0: Hash table move
        Phase 1: Generate all moves
        Phase 2: Return moves from phase 1 one by one
        """
        if move_list.phase == 0:
            move_list.phase = 1
            e = self.pvs_table[self.zobrist_key % PVS_SIZE]
            if e.key == self.zobrist_key:
                move_list.hash_move = e.best
                return e.best
        
        if move_list.phase == 1:
            move_list.phase = 2
            move_list.n = self.generate_move(move_list.moves)
            move_list.index = 0
            if not move_list.first:
                for i in range(move_list.n):
                    if (move_list.moves[i].x == move_list.hash_move.x and 
                        move_list.moves[i].y == move_list.hash_move.y):
                        for j in range(i + 1, move_list.n):
                            move_list.moves[j - 1] = move_list.moves[j]
                        move_list.n -= 1
                        break
        
        if move_list.phase == 2 and move_list.index < move_list.n:
            move_list.index += 1
            return move_list.moves[move_list.index - 1]
        
        return Pos(-1, -1)

    def record_pvs(self, best):
        """Record PVS move"""
        e = self.pvs_table[self.zobrist_key % PVS_SIZE]
        e.key = self.zobrist_key
        e.best = best

    def alpha_beta(self, depth, alpha, beta, pline):
        """Alpha-beta search with PVS"""
        self.total += 1
        
        # Check time periodically
        if self.total % 1000 == 0:
            if self.get_time() + 50 >= self.stop_time():
                self.stop_think = True
                return alpha
        
        # Check if opponent has won
        if self.check_win():
            return -10000
        
        # Leaf node
        if depth <= 0:
            return self.evaluate()
        
        # Query hash table
        val = self.probe_hash(depth, alpha, beta)
        if val != UNKNOWN:
            self.hash_count += 1
            return val
        
        line = Line()
        move_list = MoveList()
        move_list.phase = 0
        move_list.first = True
        
        p = self.get_next_move(move_list)
        best = Point(p, -10000)
        hashf = HASH_ALPHA
        
        while p.x != -1:
            line.n = 0
            self.make_move(p)
            
            # PVS Search
            if not move_list.first and alpha + 1 < beta:
                val = -self.alpha_beta(depth - 1, -alpha - 1, -alpha, line)
                if val > alpha and val < beta:
                    val = -self.alpha_beta(depth - 1, -beta, -alpha, line)
            else:
                val = -self.alpha_beta(depth - 1, -beta, -alpha, line)
            
            self.del_move()
            
            if self.stop_think:
                return best.val
            
            if val >= beta:
                self.record_hash(depth, val, HASH_BETA)
                self.record_pvs(p)
                return val
            
            if val > best.val:
                best.val = val
                best.p = p
                if val > alpha:
                    hashf = HASH_EXACT
                    alpha = val
                    pline.moves[0] = p
                    for i in range(line.n):
                        pline.moves[i + 1] = line.moves[i]
                    pline.n = line.n + 1
            
            p = self.get_next_move(move_list)
            move_list.first = False
        
        self.record_hash(depth, best.val, hashf)
        self.record_pvs(best.p)
        
        return best.val

    def cut_move_list(self, move, cand, cand_count):
        """Prune the move list based on patterns"""
        # If there's a pattern with score >= 2400 (active four or better), return directly
        if cand[0].val >= 2400:
            move[0] = cand[0].p
            return 1
        
        move_count = 0
        
        # If opponent has an active three
        if cand[0].val == 1200:
            # Find points where opponent can make an active four
            for i in range(cand_count):
                if cand[i].val == 1200:
                    move[move_count] = cand[i].p
                    move_count += 1
                else:
                    break
            
            # Find points where either side can make a blocked four
            for i in range(move_count, cand_count):
                p = self.cell[cand[i].p.x][cand[i].p.y]
                if (self.is_type(p, self.who, BLOCK4) or 
                    self.is_type(p, self.opp, BLOCK4)):
                    move[move_count] = cand[i].p
                    move_count += 1
                    if move_count >= MAX_MOVES:
                        break
        
        return move_count

    def generate_move(self, move):
        """Generate valid moves for search"""
        cand_count = 0
        move_count = 0
        
        # Find all candidate moves
        for i in range(self.b_start, self.b_end):
            for j in range(self.b_start, self.b_end):
                if (self.cell[i][j].is_cand > 0 and 
                    self.cell[i][j].piece == Pieces.EMPTY.value):
                    val = self.evaluate_move(self.cell[i][j])
                    if val > 0:
                        self.cand[cand_count] = Point(Pos(i, j), val)
                        cand_count += 1
        
        # Sort by value
        self.sort(self.cand, cand_count)
        
        # Try pruning, if pruning fails, return 0
        move_count = self.cut_move_list(move, self.cand, cand_count)
        
        # If no pruning, copy the top MAX_MOVES moves
        if move_count == 0:
            for i in range(min(cand_count, MAX_MOVES)):
                move[i] = self.cand[i].p
                move_count += 1
        
        return move_count

    def sort(self, a, n):
        """Sort points by value (insertion sort)"""
        for i in range(1, n):
            key = a[i]
            j = i
            while j > 0 and a[j - 1].val < key.val:
                a[j] = a[j - 1]
                j -= 1
            a[j] = key

    def evaluate(self):
        """Evaluate board position"""
        who_type = [0] * 8
        opp_type = [0] * 8
        block4_temp = 0
        
        # Count patterns that can be formed at empty positions
        for i in range(self.b_start, self.b_end):
            for j in range(self.b_start, self.b_end):
                if (self.cell[i][j].is_cand > 0 and 
                    self.cell[i][j].piece == Pieces.EMPTY.value):
                    block4_temp = who_type[BLOCK4]
                    self.type_count(self.cell[i][j], self.who, who_type)
                    self.type_count(self.cell[i][j], self.opp, opp_type)
                    
                    # Two blocked fours = one active four
                    if who_type[BLOCK4] - block4_temp >= 2:
                        who_type[BLOCK4] -= 2
                        who_type[FLEX4] += 1
        
        # If own side has a winning pattern, win
        if who_type[WIN] >= 1:
            return 10000
        # If opponent has two winning patterns, lose
        if opp_type[WIN] >= 2:
            return -10000
        # If opponent cannot win and own side has an active four, win
        if opp_type[WIN] == 0 and who_type[FLEX4] >= 1:
            return 10000
        
        # Calculate score
        who_score = 0
        opp_score = 0
        for i in range(1, 8):
            who_score += who_type[i] * self.eval[i]
            opp_score += opp_type[i] * self.eval[i]
        
        # Own side's patterns are more powerful (multiplier 1.2)
        return who_score * 1.2 - opp_score

    def evaluate_move(self, c):
        """Evaluate a specific move"""
        score = [0, 0]
        score[self.who] = self.pval[c.pattern[self.who][0]][c.pattern[self.who][1]][c.pattern[self.who][2]][c.pattern[self.who][3]]
        score[self.opp] = self.pval[c.pattern[self.opp][0]][c.pattern[self.opp][1]][c.pattern[self.opp][2]][c.pattern[self.opp][3]]
        
        # If score >= 200 (double active three or better), return the higher score
        if score[self.who] >= 200 or score[self.opp] >= 200:
            return score[self.who] * 2 if score[self.who] >= score[self.opp] else score[self.opp]
        else:
            return score[self.who] * 2 + score[self.opp]