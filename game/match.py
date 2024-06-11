
import random as r
from .utils import clear_log_file

import logging

# Configure logging
logging.basicConfig(
    filename='gamelogs.txt',  # Set the log file name
    filemode='a',             # Append mode, change to 'w' for overwrite
    format='%(asctime)s - %(levelname)s - %(message)s',  # Log message format
    datefmt='%Y-%m-%d %H:%M:%S',  # Date format
    level=logging.INFO       # Set the logging level
)

FACES = list(range(1,7))

def matchup(
        player1,
        player2,
        k_dice = 5,
        logs = True
):
    if logs: clear_log_file()
    logging.info("Setting up new matchup...")

    # Identify which player goes first (in overall matchup)
    first_player = r.choice([0,1])
    logging.info(f"Chose player {first_player + 1} as first player.")
    winning_index = None

    # Set game metadata
    p1_dice, p2_dice = k_dice, k_dice

    round_number = 0
    while(min(p1_dice,p2_dice) > 0):
        round_number += 1
        logging.info(f'Running round {round_number}:')
        start_index = first_player if not winning_index else winning_index
        # Run betting round
        p1_dice, p2_dice, end_index, winning_index = run_betting_round(
            player1 = player1,
            player2 = player2,
            p1_dice = p1_dice,
            p2_dice = p2_dice,
            start_index = start_index,
            round_number = round_number
        )
        logging.info(f"Done running betting round. Player {end_index+1} called Liar.")

def run_betting_round(
        player1,
        player2,
        p1_dice,
        p2_dice,
        start_index,
        round_number
):
    logging.info("Starting betting round:")
    logging.info(f"Player 1 dice: {p1_dice} | Player 2 dice: {p2_dice}")
    p1_hand = r.choices( population = FACES, k = p1_dice)
    p2_hand = r.choices( population = FACES, k = p2_dice)

    cur_index = start_index
    quantity, face, prior_quantity, prior_face = None, None, None, None
    while True:
        logging.info(f"Looking for a bet from player {cur_index + 1}")
        # Loop until break (someone calls liar)
        player = player1 if cur_index == 0 else player2
        hand = p1_hand if cur_index == 0 else p2_hand

        bet_quantity, bet_face = player.algo(
            quantity = quantity,
            face = face,
            hand = hand,
            round_number = round_number
        )

        # Update prior values
        prior_quantity, prior_face = quantity, face
        # Update current values
        quantity, face = bet_quantity, bet_face

        if not validate_bid(
            quantity = bet_quantity,
            face = bet_face,
            prior_quantity = prior_quantity,
            prior_face = prior_face
        ):
            logging.error(f'Invalid bid from Player {cur_index + 1}')
            break

        # If we get here, the bid was valid
        logging.info(f"Got valid bid: {bet_quantity} {bet_face}'s")

        if face == 7:
            # Liar was called, break
            break
        else:
            # Liar was not called, allow next player to go
            cur_index = 1 if cur_index == 0 else 0

    logging.info('Liar was called - no more betting for this round.')
    all_dice = p1_hand + p2_hand
    player_was_lying = evaluate_liar_bid(
        prior_quantity = prior_quantity,
        prior_face = prior_face,
        all_dice = all_dice
    )
    accuser_change = 0 if player_was_lying else -1
    bettor_change = -1 if player_was_lying else 0
    if cur_index == 0:
        # Player 1 called liar
        p1_dice += accuser_change
        p2_dice += bettor_change
    else:
        # Player 2 called liar
        p2_dice += accuser_change
        p1_dice += bettor_change

    winning_index = -1
    if cur_index == 0:
        winning_index = 0 if player_was_lying else 1
    if cur_index == 1:
        winning_index = 1 if player_was_lying else 0

    return p1_dice, p2_dice, cur_index, winning_index

def evaluate_liar_bid(
    prior_quantity,
    prior_face,
    all_dice
):
    logging.info(f"Evaluating liar call against prior bid of {prior_quantity} {prior_face}'s")
    count = all_dice.count(prior_face) + all_dice.count(1)
    if count >= prior_quantity:
        logging.info(f"{count} >= {prior_quantity}")
        logging.info(all_dice)
        logging.info("... player wasn't lying")
        return False
    else:
        logging.info(f"{count} < {prior_quantity}")
        logging.info(all_dice)
        logging.info("... player was lying")
        return True


def validate_bid(
    quantity,
    face,
    prior_quantity,
    prior_face
):
    if face not in list(range(2,8)):
        logging.error('Invalid face value - must be 2-6, or 7 for Liar')
        return False
    if prior_quantity is None:
        # This was the first bid
        if face > 6:
            logging.info('Liar was called on first bid')
            return False
    else:
        if quantity < prior_quantity:
            logging.info('Quantity decreased')
            return False
        elif quantity == prior_quantity:
            if face <= prior_face:
                logging.info('Quantity stayed the same and face did not increase.')
                return False

    return True
