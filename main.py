import argparse
from datetime import datetime
import logging
from sys import stdout
import berserk
import pandas as pd


parser = argparse.ArgumentParser(
                    prog="Openmynings",
                    description="Program to export lichess games opening stats in excel format.")
parser.add_argument("api_token", metavar="api_token", type=str,
                    help="Lichess api token")
parser.add_argument("username", metavar="username", type=str,
                    help="Lichess account username")
parser.add_argument("output", metavar="output", type=str,
                    help="Output file name")
parser.add_argument("--games", "-n", type=int, required=False, default=1000,
                    help="Get last n(max) games")
parser.add_argument("--since", "-s", type=str, required=False, default=0,
                    help="Get games played since the given datetime. Format: dd-mm-yyyy")
parser.add_argument("--moves", "-m", type=int, required=False, default=4,
                    help="Extract first n moves from the opening. Default is 4")
args = vars(parser.parse_args())

logger = logging.getLogger(__name__)
logging.basicConfig(stream=stdout, encoding="utf-8", level=logging.DEBUG)


def connect(token: str) -> berserk.Client:
    """Connect to the Lichess api endpoint and return ready-to-use api client object.

    Args:
        token (str): Lichess api token

    Returns:
        berserk.Client: Api client object
    """
    try:
        session = berserk.TokenSession(token)
        logger.info("Connected")
        return berserk.Client(session)
    except Exception as error:
        logging.error(error)
        return None
    
def download_games(client: berserk.Client):
    """Downloads all games for the given user

    Args:
        client (berserk.Client): api client obj

    Returns:
        dict: downloaded games(as generator) or empty list on error
    """
    try:
        try:
            since = None if not args.get("since") else datetime.strptime(args.get("since"), "%d-%m-%Y")
        except ValueError:
            logging.error(f"Argument value '{args.get('since')}' does not match format 'dd-mm-yyyy'")
            exit(0)
        return client.games.export_by_player(
            args.get("username"),
            max=args.get("games"),
            opening=True, 
            rated=True,
            since=since
        )
    except Exception as error:
        logging.error(error)
        return []
    
def game_get_player_color(game: dict, player_name: str) -> str:
    """Returns color of the player in the given game

    Args:
        game (dict): Game dict
        player_name (str): Name of the player to get color of

    Returns:
        str: "white" or "black"
    """
    players = game.get("players")
    if players.get("white").get("user").get("name") == player_name:
        return "white"
    else:
        return "black"
    
def game_result_indicator(game: dict, player_name: str) -> int|float:
    """Returns whether the player won, drew or lost the game

    Args:
        game (dict): Game to check
        player_name (str): the player's name

    Returns:
        int: 1 if player won, 0.5 if player drew game and 0 if player lost
    """
    player_color = game_get_player_color(game, player_name)
    if game.get("winner") == player_color:
        return 1
    elif game.get("winner") != "black" and game.get("winner") != "white":
        return 0.5
    else:
        return 0
    
def game_get_first_n_moves(game: dict, color: str) -> list:
    """Returns list of first n moves of the player(depending on the `color`).

    Args:
        game (dict): The game 
        color (bool, optional): Player's color

    Returns:
        list: List of first n moves
    """
    moves: str = game.get("moves")
    moves = moves.split(" ", 2*args.get("moves"))[(0 if color == "white" else 1):(2*args.get("moves")):2]
    return " ".join(moves)

def encapsulate_data(games) -> pd.DataFrame:
    """Encapsulates data into pandas data frame

    Args:
        games (_type_): downloaded games generator

    Returns:
        pd.DataFrame: ready to export pandas data frame
    """
    data = []
    for game in games:
        data_entry = {}
        data_entry['id'] = game.get("id")
        data_entry['color'] = game_get_player_color(game, args.get("username"))
        data_entry['result'] = game_result_indicator(game, args.get("username"))
        data_entry['opening_tag'] = game.get("opening", {}).get("name")
        data_entry['first_moves'] = game_get_first_n_moves(game, data_entry.get('color'))
        data_entry['total_moves'] = len(game.get("moves").split(" "))
        data.append(data_entry)
    return pd.DataFrame(data)
    
def main():
    client = connect(args.get("api_token"))
    games = download_games(client)
    df = encapsulate_data(games)
    df.to_excel(args.get("output"), "data.xlsx")

if __name__ == "__main__":   
    main()