import mysql.connector
import os
from dotenv import load_dotenv

# db_url = "server.oversight.co.il"
load_dotenv()  # Load environment variables from .env file

def connect_to_db():
    print(os.environ.get("DB_HOST"))
    try:
        connection = mysql.connector.connect(
            host=os.environ.get("DB_HOST"),
            user=os.environ.get("DB_USER"),
            password=os.environ.get("DB_PASSWORD"),
            database=os.environ.get("DB_NAME"),
        )
        return connection
    except Exception as e:
        print(e)

def calculate_score():
    try:
        connection = connect_to_db()
        curser = connection.cursor()

        # Games
        curser.execute("SELECT * FROM Games")
        games = curser.fetchall()

        curser.execute("SELECT * FROM Bets")
        bets = curser.fetchall()

        
        curser.execute("SELECT * FROM Users")
        users = curser.fetchall()

        for user in users:
            curr_points = 0
            user_id = -1
            for game in games:
                if(len(game) > 4):
                    game_id = game[0]
                    game_realA = game[3]
                    game_realB = game[4]
                    game_status = game[5]
                    for bet in bets:
                        if(len(bet) > 4 and bet[2] == game_id and bet[1] == user[0]):
                            user_id = bet[1]
                            user_scoreA = bet[3]
                            user_scoreB = bet[4]
                            new_points = calculate_game_points(game_realA, game_realB, user_scoreA, user_scoreB, game_status)
                            curr_points = curr_points + new_points
                            # print("game_id, new_points, curr_points", game_id, new_points, curr_points)
            query = "UPDATE Users SET points=%s WHERE id=%s"
            params = (curr_points, user_id)
            curser.execute(query, params)
            connection.commit()
    
    except Exception as e:
        print(str(e))


def calculate_game_points(game_realA, game_realB, user_scoreA, user_scoreB, game_status):
    bull_point = 3
    part_point = 1
    if game_status == 'Eighth':
        bull_point = 4
        part_point = 2
    elif game_status == 'Quarter':
        bull_point = 8
        part_point = 4
    elif game_status == 'Semi':
        bull_point = 10
        part_point = 5
    elif game_status == 'Final':
        bull_point = 15
        part_point = 8

    if game_realA == user_scoreA and game_realB == user_scoreB:
        return bull_point
    elif game_realA > game_realB and user_scoreA > user_scoreB:
        return part_point
    elif game_realB > game_realA and user_scoreB > user_scoreA:
        return part_point
    elif game_realA == game_realB and user_scoreA == user_scoreB:
        return part_point

    return 0

