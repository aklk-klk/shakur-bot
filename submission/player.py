from agents.agent import Agent
from gym_env import PokerEnv
import random

action_types = PokerEnv.ActionType


class PlayerAgent(Agent):
    def __name__(self):
        return "Pre-Flop Flop"

    def __init__(self, stream: bool = True):
        super().__init__(stream)
        # Initialize any instance variables here
        self.hand_number = 0
        self.last_action = None
        self.won_hands = 0

    def act(self, observation, reward, terminated, truncated, info):
        # Example of using the logger
        if observation["street"] == 0 and info["hand_number"] % 50 == 0:
            self.logger.info(f"Hand number: {info['hand_number']}")

        # First, get the list of valid actions we can take
        valid_actions = observation["valid_actions"]
        
        # Get indices of valid actions (where value is 1)
        valid_action_indices = [i for i, is_valid in enumerate(valid_actions) if is_valid]
        
        # Randomly choose one of the valid action indices
        action_type = random.choice(valid_action_indices)
        
        # Set up our response values
        raise_amount = 0
        card_to_discard = -1  # -1 means no discard
        
        # If we chose to raise, pick a random amount between min and max
        if action_type == action_types.RAISE.value:
            if observation["min_raise"] == observation["max_raise"]:
                raise_amount = observation["min_raise"]
            else:
                raise_amount = random.randint(
                    observation["min_raise"],
                    observation["max_raise"]
                )
        
        # If we chose to discard, randomly pick one of our two cards (0 or 1)
        if action_type == action_types.DISCARD.value:
            card_to_discard = random.randint(0, 1)
        
        return action_type, raise_amount, card_to_discard

    def observe(self, observation, reward, terminated, truncated, info):
        # Log interesting events when observing opponent's actions
        pass
        if terminated:
            self.logger.info(f"Game ended with reward: {reward}")
            self.hand_number += 1
            if reward > 0:
                self.won_hands += 1
            self.last_action = None
        else:
            # log observation keys
            self.logger.info(f"Observation keys: {observation}")

    def preFlopAction(self, observation):
        my_hand = observation["my_cards"]
        num1 = my_hand[0] % 9
        num2 = my_hand[1] % 9
        highCard = max(num1, num2)
        # less than 3 folding condition
        if(highCard <= 3 and (num1 != num2 and (num1 != 8 and num2 != 8))):
           if observation["valid_actions"][action_types.FOLD.value]:
               return action_types.FOLD.value, 0, -1
        #less than 4 condition
        if(highCard <= 4 and (num1 != num2 and (num1 != 5 and num2 != 5 and num1!= 8 and num2 != 8))):
            if observation["valid_actions"][action_types.FOLD.value]:
               return action_types.FOLD.value, 0, -1
        if(num1 == 5 or num2 == 5 and (num1 != num2)):
            if(num1 != 8 and num2 != 8 and num1 != 4 and num2 != 4 and num1 != 6 and num2 != 6 and num1 != 7 and num2 != 7):
                if observation["valid_actions"][action_types.FOLD.value]:
                    return action_types.FOLD.value, 0, -1
        if(num1 == num2):
            raise_amount = observation["min_raise"] + random.randint(0, highCard)
            return action_types.RAISE.value, raise_amount, -1
        if observation["valid_actions"][action_types.CHECK.value]:
            return action_types.CHECK.value, 0, -1
        if observation["valid_actions"][action_types.CALL.value]:
            return action_types.CALL.value, 0, -1

