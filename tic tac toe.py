... import random
... 
... def print_board(board):
...     print()
...     for i in range(0, 9, 3):
...         row = board[i:i+3]
...         print(" " + " | ".join(row))
...         if i < 6:
...             print("---+---+---")
...     print()
... 
... def check_winner(board, player):
...     wins = [
...         (0,1,2), (3,4,5), (6,7,8),  # rows
...         (0,3,6), (1,4,7), (2,5,8),  # columns
...         (0,4,8), (2,4,6),           # diagonals
...     ]
...     return any(all(board[i] == player for i in line) for line in wins)
... 
... def is_full(board):
...     return " " not in board
... 
... def available_moves(board):
...     return [i for i, spot in enumerate(board) if spot == " "]
... 
... def minimax(board, is_maximizing):
...     if check_winner(board, "O"):
...         return 1
...     if check_winner(board, "X"):
...         return -1
...     if is_full(board):
        return 0

    if is_maximizing:
        best_score = -float("inf")
        for move in available_moves(board):
            board[move] = "O"
            score = minimax(board, False)
            board[move] = " "
            best_score = max(best_score, score)
        return best_score
    else:
        best_score = float("inf")
        for move in available_moves(board):
            board[move] = "X"
            score = minimax(board, True)
            board[move] = " "
            best_score = min(best_score, score)
        return best_score

def best_move(board):
    best_score = -float("inf")
    move = None
    moves = available_moves(board)
    random.shuffle(moves)  # avoid always picking the same square on ties
    for m in moves:
        board[m] = "O"
        score = minimax(board, False)
        board[m] = " "
        if score > best_score:
            best_score = score
            move = m
    return move

def get_player_move(board):
    while True:
        raw = input("Your move (1-9): ").strip()
        if not raw.isdigit() or not (1 <= int(raw) <= 9):
            print("Please enter a number from 1 to 9.")
            continue
        idx = int(raw) - 1
        if board[idx] != " ":
            print("That square is already taken.")
            continue
        return idx

def print_legend():
    legend = [str(i + 1) for i in range(9)]
    print("Squares are numbered like this:")
    print_board(legend)

def play():
    print("=" * 30)
    print("   TIC-TAC-TOE  (You: X, Computer: O)")
    print("=" * 30)
    print_legend()

    board = [" "] * 9
    player_turn = random.choice([True, False])
    print("You go first!" if player_turn else "Computer goes first!")

    while True:
        print_board(board)

        if player_turn:
            move = get_player_move(board)
            board[move] = "X"
        else:
            print("Computer is thinking...")
            move = best_move(board)
            board[move] = "O"

        if check_winner(board, "X"):
            print_board(board)
            print("You win! 🎉")
            break
        if check_winner(board, "O"):
            print_board(board)
            print("Computer wins! 🤖")
            break
        if is_full(board):
            print_board(board)
            print("It's a draw!")
            break

        player_turn = not player_turn

def main():
    while True:
        play()
        again = input("Play again? (y/n): ").strip().lower()
        if again != "y":
            print("Thanks for playing!")
            break

if __name__ == "__main__":
