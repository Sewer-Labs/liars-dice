
class Player:

    def __init__(self):
        pass

    def algo(
        self,
        quantity,
        face,
        hand,
        round_number,
        game_data = None
    ):
        if quantity is None:
            return 6,6
        if quantity > (11 - round_number) / 2:
            return quantity, 7

        return quantity + 1, face + 1