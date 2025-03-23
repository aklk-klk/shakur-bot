from agents.agent import Agent
from gym_env import PokerEnv
import random

action_types = PokerEnv.ActionType


class PlayerAgent(Agent):
    def __name__(self):
        return "IT"

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
        valid = observation["valid_actions"]
        can_fold     = valid[action_types.FOLD.value]
        can_raise    = valid[action_types.RAISE.value]
        can_check    = valid[action_types.CHECK.value]
        can_call     = valid[action_types.CALL.value]
        can_discard  = valid[action_types.DISCARD.value]
        street = observation["street"]
        my_cards = observation["my_cards"]

        def get_rank(card):  # 0–8
         return card % 9

        def get_suit(card):  # 0–2
         return card // 9
    
        def is_pair(cards):
            ranks = [get_rank(c) for c in cards]
            return len(set(ranks)) < len(ranks)
       
        def has_two_pair(cards):
            ranks = [get_rank(c) for c in cards]
            rank_counts = {r: ranks.count(r) for r in set(ranks)}
            return list(rank_counts.values()).count(2) >= 2
        def has_trips(cards):
            ranks = [get_rank(c) for c in cards]
            return any(ranks.count(r) == 3 for r in set(ranks))
        def has_flush_draw(cards):
            suits = [get_suit(c) for c in cards]
            return any(suits.count(s) >= 4 for s in set(suits))
        def has_made_flush(cards):
            suits = [get_suit(c) for c in cards]
            return any(suits.count(s) >= 5 for s in set(suits))
        
        if street == 1:
            community_cards = observation["community_cards"]
            all_cards = my_cards + community_cards

            if has_made_flush(all_cards) or has_trips(all_cards) or has_two_pair(all_cards):
                if can_raise:
                    raise_amount = random.randint(0, 9) * get_rank(my_cards[0])+ observation["min_raise"]
                    return (action_types.RAISE.value, raise_amount, -1)

                elif can_call:
                    return (action_types.CALL.value, 0, -1)

            elif has_flush_draw(all_cards):
                if can_call:
                    return (action_types.CALL.value, 0, -1)
                elif can_check:
                    return (action_types.CHECK.value, 0, -1)

            elif is_pair(all_cards):
                if can_check:
                    return (action_types.CHECK.value, 0, -1)
                elif can_call:
                    return (action_types.CALL.value, 0, -1)

            elif can_check:
                return (action_types.CHECK.value, 0, -1)
            
            # Fallback
            return (action_types.FOLD.value, 0, -1)

    

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