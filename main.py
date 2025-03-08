#!/usr/bin/env python3
import sys
import time
import os
from ai import AI, Pos, Pieces, MAX_SIZE

# Initialize AI
wine = AI()

def clear_screen():
    """Clear the terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def toupper(s):
    """Convert a string to uppercase"""
    return s.upper()

# Console UI
class SimpleUI:
    def __init__(self):
        self.board = [[0 for _ in range(15)] for _ in range(15)]
        self.chess_type = 1  # 1 for black (player), 2 for white (AI)
        self.chess_count = 0
        self.is_end = False
    
    def draw_board(self):
        """Draw the game board in console"""
        clear_screen()
        print("\n===== GOMOKU (FIVE IN A ROW) =====\n")
        print("  Player: ● (Black)   Computer: ○ (White)\n")
        
        for i in range(15):
            for j in range(15):
                # Print row numbers at the start of each row
                if j == 0:
                    if i + 1 < 10:
                        print(" ", end="")
                    print(i + 1, end=" ")
                
                # Print board content
                if self.board[i][j] == 0:
                    if i == 0:
                        if j == 0:
                            print("┌─", end="")
                        elif j == 14:
                            print("┐", end="")
                        else:
                            print("┬─", end="")
                    elif i == 14:
                        if j == 0:
                            print("└─", end="")
                        elif j == 14:
                            print("┘", end="")
                        else:
                            print("┴─", end="")
                    else:
                        if j == 0:
                            print("├─", end="")
                        elif j == 14:
                            print("┤", end="")
                        else:
                            print("┼─", end="")
                elif self.board[i][j] == 1:
                    print("● ", end="")
                elif self.board[i][j] == 2:
                    print("○ ", end="")
            # New line at the end of each row
            print()
        print("   A B C D E F G H I J K L M N O")
        print("\nCommands: [coordinate] = make move (e.g. h8)")
        print("          'quit' = exit game, 'restart' = new game\n")
    
    def check_win(self):
        """Check if the game is over"""
        if wine.check_win():
            # When check_win() returns true, it means the player who made the PREVIOUS move has won
            # chess_type has already been switched, so the winner is the opposite of current chess_type
            winner = 3 - self.chess_type  # Convert from 1/2 to 2/1
            
            if winner == 1:  # Player (Black) won
                print("\n🎉 Congratulations! You win! 🎉\n")
            else:  # Computer (White) won
                print("\n😔 Computer wins! Better luck next time! 😔\n")
            
            while True:
                choice = input("Play again? (y/n): ").strip().lower()
                if choice == 'y' or choice == 'yes':
                    self.board = [[0 for _ in range(15)] for _ in range(15)]
                    self.chess_count = 0
                    self.chess_type = 1
                    wine.restart()
                    self.draw_board()
                    return
                elif choice == 'n' or choice == 'no':
                    self.is_end = True
                    return
                else:
                    print("Please enter 'y' for yes or 'n' for no.")
    
    def add_chess(self, x, y):
        """Add a chess piece to the board"""
        self.board[y][x] = self.chess_type
        self.chess_type = 3 - self.chess_type
        self.chess_count += 1
        self.draw_board()
    
    def run(self):
        """Main game loop"""
        wine.set_size(15)
        
        result = Pos()
        user_input = Pos()
        
        self.draw_board()
        
        while not self.is_end:
            if self.chess_type == 1:  # Human's turn
                try:
                    input_text = input("Your move: ").strip().lower()
                    
                    # Check for special commands
                    if input_text == "quit" or input_text == "exit":
                        print("Thanks for playing!")
                        self.is_end = True
                        continue
                    elif input_text == "restart" or input_text == "new":
                        self.board = [[0 for _ in range(15)] for _ in range(15)]
                        self.chess_count = 0
                        self.chess_type = 1
                        wine.restart()
                        self.draw_board()
                        continue
                    elif input_text == "help":
                        print("\nHow to play:")
                        print("- Enter coordinates like 'h8' to place your piece")
                        print("- Type 'restart' to start a new game")
                        print("- Type 'quit' to exit\n")
                        continue
                    
                    # Regular move input
                    if len(input_text) < 2:
                        print("Invalid input. Please use format like 'h8'.")
                        continue
                    
                    # Parse column (letter)
                    col = input_text[0]
                    if not ('a' <= col <= 'o'):
                        print("Column must be a letter from A to O.")
                        continue
                    user_input.x = ord(col) - ord('a')
                    
                    # Parse row (number)
                    row_text = input_text[1:]
                    try:
                        row = int(row_text)
                        if not (1 <= row <= 15):
                            print("Row must be a number from 1 to 15.")
                            continue
                        user_input.y = row - 1
                    except ValueError:
                        print("Row must be a number from 1 to 15.")
                        continue
                    
                    # Check if the move is valid
                    if self.board[user_input.y][user_input.x] != 0:
                        print("That position is already occupied. Try another position.")
                        continue
                    
                    self.add_chess(user_input.x, user_input.y)
                    wine.put_chess(user_input)
                    
                except KeyboardInterrupt:
                    print("\nGame interrupted. Exiting...")
                    self.is_end = True
                    continue
            else:  # AI's turn
                print("Computer is thinking...")
                result = wine.get_best_move()
                wine.put_chess(result)
                self.add_chess(result.x, result.y)
                print(f"Computer played: {chr(result.x + ord('a'))}{result.y + 1}")
            
            self.check_win()

def show_welcome():
    """Display welcome message and menu"""
    clear_screen()
    print("\n" + "=" * 50)
    print("               GOMOKU AI GAME                ")
    print("=" * 50)
    print("\nWelcome to Gomoku (Five in a Row)!")
    print("\nGame Modes:")
    print("1. Play against computer")
    print("2. Computer vs computer (demo)")
    print("3. Enter Gomocup protocol mode")
    print("4. Exit")
    
    while True:
        try:
            choice = input("\nSelect an option (1-4): ").strip()
            if choice == '1':
                ui = SimpleUI()
                ui.run()
                return
            elif choice == '2':
                print("\nComputer vs computer demo mode is not implemented yet.")
                input("Press Enter to return to menu...")
                show_welcome()
                return
            elif choice == '3':
                print("\nEntering Gomocup protocol mode...")
                print("Type commands according to the Gomocup protocol.")
                print("(Type 'END' to exit)\n")
                gomocup()
                return
            elif choice == '4':
                print("\nThanks for playing! Goodbye.")
                sys.exit(0)
            else:
                print("Invalid choice. Please enter a number from 1 to 4.")
        except KeyboardInterrupt:
            print("\nProgram interrupted. Exiting...")
            sys.exit(0)

def gomocup():
    """Handle Gomocup protocol"""
    print("Gomocup protocol mode. Enter commands:")
    while True:
        try:
            command = input().strip()
            command = toupper(command)
            
            if command == "START":
                size = int(input())
                if size > MAX_SIZE or size <= 5:
                    print("ERROR")
                else:
                    wine.set_size(size)
                    print("OK")
            
            elif command == "RESTART":
                wine.restart()
                print("OK")
            
            elif command == "TAKEBACK":
                wine.del_move()
                print("OK")
            
            elif command == "BEGIN":
                best = wine.get_best_move()
                wine.put_chess(best)
                print(f"{best.x},{best.y}")
            
            elif command == "TURN":
                pos_input = input().strip()
                parts = pos_input.split(',')
                if len(parts) != 2:
                    print("ERROR")
                    continue
                
                try:
                    input_x = int(parts[0])
                    input_y = int(parts[1])
                except ValueError:
                    print("ERROR")
                    continue
                
                input_pos = Pos(input_x, input_y)
                
                if (input_pos.x < 0 or input_pos.x >= wine.size or 
                    input_pos.y < 0 or input_pos.y >= wine.size or
                    wine.cell[input_pos.x + 4][input_pos.y + 4].piece != Pieces.EMPTY.value):
                    print("ERROR")
                else:
                    wine.put_chess(input_pos)
                    best = wine.get_best_move()
                    wine.put_chess(best)
                    print(f"{best.x},{best.y}")
            
            elif command == "BOARD":
                wine.restart()
                
                command = input().strip()
                command = toupper(command)
                
                while command != "DONE":
                    parts = command.split(',')
                    if len(parts) != 3:
                        print("ERROR")
                        break
                    
                    try:
                        m_x = int(parts[0])
                        m_y = int(parts[1])
                        c = int(parts[2])
                    except ValueError:
                        print("ERROR")
                        break
                    
                    m = Pos(m_x, m_y)
                    
                    if (m.x < 0 or m.x >= wine.size or 
                        m.y < 0 or m.y >= wine.size or
                        wine.cell[m.x + 4][m.y + 4].piece != Pieces.EMPTY.value):
                        print("ERROR")
                    else:
                        wine.put_chess(m)
                    
                    command = input().strip()
                    command = toupper(command)
                
                best = wine.get_best_move()
                wine.put_chess(best)
                print(f"{best.x},{best.y}")
            
            elif command == "INFO":
                key = input().strip()
                key = toupper(key)
                
                if key == "TIMEOUT_TURN":
                    value = int(input())
                    if value != 0:
                        wine.timeout_turn = value
                
                elif key == "TIMEOUT_MATCH":
                    value = int(input())
                    if value != 0:
                        wine.timeout_match = value
                
                elif key == "TIME_LEFT":
                    value = int(input())
                    if value != 0:
                        wine.time_left = value
                
                elif key == "MAX_MEMORY" or key == "GAME_TYPE" or key == "RULE":
                    # These parameters are ignored in the Python version
                    value = int(input())
                
                elif key == "FOLDER":
                    folder = input()
                    # Folder parameter is ignored
            
            elif command == "PLAY":
                ui = SimpleUI()
                ui.run()
                return
            
            elif command == "END":
                print("Exiting Gomocup mode.")
                return
            
            elif command == "HELP":
                print("Available commands: START, RESTART, TAKEBACK, BEGIN, TURN, BOARD, INFO, PLAY, END")
            
            # Unknown command - ignore silently
        
        except (EOFError, KeyboardInterrupt):
            print("\nExiting Gomocup mode.")
            break

if __name__ == "__main__":
    show_welcome()