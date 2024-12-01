import sys
import secrets
import hmac
import hashlib
from typing import List, Tuple
import prettytable

class DiceParser:
    @staticmethod
    def parse_dice_configurations(args):
        if len(args) < 3:
            raise ValueError(
                "Error: Insufficient number of dice configurations.\n"
                "Usage: game.py DICE1 DICE2 DICE3 ...\n"
                "Example: python game.py 1,2,3,4,5,6 2,3,4,5,6,1 3,4,5,6,1,2"
            )
        try:
            dice_configs = []
            for arg in args:
                dice = [int(x) for x in arg.split(',')]
                if len(dice) != 6:
                    raise ValueError(f"Each dice must have exactly 6 faces. Invalid configuration: {arg}")
                dice_configs.append(dice)
            return dice_configs
        except ValueError as e:
            raise ValueError(f"Invalid dice configuration: {str(e)}\n"
                             "Ensure all arguments are comma-separated integers with exactly 6 values.")

class FairRandomGenerator:
    @staticmethod
    def generate_fair_random(range_max: int) -> Tuple[int, str, bytes]:
        secret_key = secrets.token_bytes(32)
        
        random_value = secrets.randbelow(range_max + 1)
        hmac_obj = hmac.new(secret_key, str(random_value).encode(), hashlib.sha3_256)
        hmac_hex = hmac_obj.hexdigest()

        return random_value, hmac_hex, secret_key

class ProbabilityCalculator:
    """
    A utility class for calculating win probabilities between different dice configurations.
    """

    @staticmethod
    def calculate_win_probabilities(dice_configs: List[List[int]]) -> List[List[float]]:
        def calculate_pair_probability(dice1: List[int], dice2: List[int]) -> float:
            wins = sum(1 for x in dice1 for y in dice2 if x > y)
            total = len(dice1) * len(dice2)
            return round(wins / total, 4)
        
        probabilities = []
        for i in range(len(dice_configs)):
            row = []
            for j in range(len(dice_configs)):
                if i == j:
                    row.append(0.3333)  # Probability for self-match
                else:
                    row.append(calculate_pair_probability(
                        dice_configs[i], dice_configs[j]
                    ))
            probabilities.append(row)
        
        return probabilities

class Game:
    def __init__(self, dice_configs):
        self.dices = dice_configs
        self.probability_matrix = ProbabilityCalculator.calculate_win_probabilities(dice_configs)
        self.computer_score = 0
        self.user_score = 0
        self.computer_dice = None
        self.user_dice = None
        self.turn = None
    
    def determine_first_move(self) -> None:
        computer_value, hmac_value, secret_key = FairRandomGenerator.generate_fair_random(1)
        
        print("Let's determine who makes the first move.")
        print(f"I selected a random value in the range 0..1 (HMAC={hmac_value}).")
        print("Try to guess my selection.")
        print("0 - 0")
        print("1 - 1")
        print("X - exit")
        print("? - help")
        
        while True:
            user_guess = input("Your selection: ")
            
            if user_guess == 'X':
                sys.exit(0)
            elif user_guess == '?':
                self.display_help()
                continue
            try:
                user_guess = int(user_guess)
                if user_guess not in [0, 1]:
                    print("Please select 0 or 1.")
                    continue
                
                print(f"My selection: {computer_value} (KEY={secret_key.hex()}).")
                
                if computer_value == user_guess:
                  self.turn = "user"
                else:
                  self.turn = "computer"
                break
            except ValueError:
                print("Invalid input. Please enter 0, 1, X, or ?")
    
    def select_dice(self) -> None:
        # Computer Selects dice first
        if self.turn == "computer":
            computer_index = FairRandomGenerator.generate_fair_random(len(self.dices) - 1)[0]
            self.computer_dice = self.dices.pop(computer_index)
            print(f"I choose the {self.computer_dice} dice.")
            
            # Show remaining dice for user
            print("Choose your dice:")
            for i, dice in enumerate(self.dices):
                print(f"{i} - {dice}")
            print("X - exit")
            print("? - help")
            
            while True:
                user_input = input("Your selection: ")
                
                if user_input == 'X':
                    sys.exit(0)
                elif user_input == '?':
                    self.display_help()
                    continue
                
                try:
                    user_index = int(user_input)
                    if 0 <= user_index < len(self.dices):
                        self.user_dice = self.dices[user_index]
                        print(f"You choose the {self.user_dice} dice.")
                        break
                    print("Invalid dice selection.")
                except ValueError:
                    print("Invalid input. Please enter a valid number, X, or ?")
        
        # User selects first dice
        else:
            print("Choose your dice:")
            for i, dice in enumerate(self.dices):
                print(f"{i} - {dice}")
            print("X - exit")
            print("? - help")
            
            while True:
                user_input = input("Your selection: ")
                
                if user_input == 'X':
                    sys.exit(0)
                elif user_input == '?':
                    self.display_help()
                    continue
                
                try:
                    user_index = int(user_input)
                    if 0 <= user_index < len(self.dices):
                        self.user_dice = self.dices.pop(user_index)
                        print(f"You choose the {self.user_dice} dice.")

                        computer_index = FairRandomGenerator.generate_fair_random(len(self.dices) - 1)[0]
                        self.computer_dice = self.dices.pop(computer_index)
                        print(f"I choose the {self.computer_dice} dice.")
                        break
                    print("Invalid dice selection.")
                except ValueError:
                    print("Invalid input. Please enter a valid number, X, or ?")
    
    def play_turn(self) -> None:
        computer_value, computer_hmac, computer_key = FairRandomGenerator.generate_fair_random(5)
        print("It's time to throw the dice.")
        print(f"I selected a random value in the range 0..5 (HMAC={computer_hmac}).")
        print("Add your number module 6")
        print("0 - 0")
        print("1 - 1")
        print("2 - 2")
        print("3 - 3")
        print("4 - 4")
        print("5 - 5")
        print("X - exit")
        print("? - help")
        
        while True:
            user_input = input("Your selection: ")
            
            if user_input == 'X':
                sys.exit(0)
            elif user_input == '?':
                self.display_help()
                continue
            
            try:
                user_value = int(user_input)
                if user_value not in range(6):
                    print("Please select a number between 0 and 5.")
                    continue
                
                result = (computer_value + user_value) % 6
                print(f"My number is {computer_value} (KEY={computer_key.hex()}).")
                print(f"The result is {computer_value} + {user_value} = {result} (mod 6).")
                
                # Throw dice based on turn
                if self.turn == "computer":
                    print(f"My throw is {self.computer_dice[result]}")
                    self.computer_score = self.computer_dice[result]
                    self.turn = "user"
                else:
                    print(f"Your throw is {self.user_dice[result]}")
                    self.user_score = self.user_dice[result]
                    self.turn = "computer"
                
                break
            except ValueError:
                print("Invalid input. Please enter a number between 0 and 5, X, or ?")
    
    def final_scores(self):
        if self.computer_score > self.user_score:
            print(f"I win! ({self.computer_score} > {self.user_score})")
        elif self.user_score > self.computer_score:
            print(f"You win! ({self.computer_score} < {self.user_score})")
        else:
            print(f"It's a tie ({self.user_score} = {self.computer_score})")
        
      
    def display_help(self):
        table = prettytable.PrettyTable()
        table.field_names = ["User dice ▼"] + [f"{dice}" for dice in self.dices]
        
        for i, dice in enumerate(self.dices):
            row = [f"{dice}"]
            row.extend([f"- ({self.probability_matrix[i][j]})" if i == j else str(self.probability_matrix[i][j]) for j in range(len(self.dices))])
            table.add_row(row)
        
        print("\nProbability of the win for the user:")
        print(table)

def main():
    try:
        dice_configs = DiceParser.parse_dice_configurations(sys.argv[1:])
        
        game = Game(dice_configs)
        
        game.determine_first_move()
        
        game.select_dice()
        
        game.play_turn() # for the first player
        game.play_turn() # for the second player

        game.final_scores()
    
    except ValueError as e:
        print(str(e))
        sys.exit(1)

if __name__ == "__main__":
    main()
