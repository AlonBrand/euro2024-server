from flask import Flask, request
from flask_cors import CORS
from utils.utils import *
import mysql.connector


api_tokken = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJfaWQiOiI2MzcyOGIwYmZkOWFhYzIyNjcwNDUwMTAiLCJpYXQiOjE2Njg0NTEwODMsImV4cCI6MTY2ODUzNzQ4M30.0G3IlX1E8S4XyDQLXieaArzjLTlsXFqpcG2iKCfb7yw"

app = Flask(__name__)
cors = CORS(app)
# app.config['SESSION_TYPE'] = 'filesystem'
# app.config['CORS_HEADERS'] = 'Content-Type'
app.config['SECRET_KEY'] = 'oh_so_secret'
db_url = "server.oversight.co.il"

def connect_to_db():
    try:
        connection = mysql.connector.connect(
            host=db_url,
            user="rotem_private",
            password="T$l3715ml",
            database="rotem_private"
        )
        return connection
    except Exception as e:
        print(e)

# Add CORS headers to all responses
@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response

@app.route('/')
def home():
    try:
        return {
            "msg": "Server is runnig..."
        }
    except Exception as e:
        print(e)
        return {
            'msg': 'Failed to run application',
        }
    # headers = {
    #     'Authorization': 'Bearer {token}'.format(token=api_tokken),
    #     'Content-Type': 'application/json',
    # }

    # json_data = {
    #     'name': 'Alon Brand',
    #     'email': 'aaa@gmail.com',
    #     'password': '123456',
    #     'passwordConfirm': '123456',
    # }

    # response = await requests.get('http://api.cup2022.ir/api/v1/team', headers=headers)
    # print(jsonify(response))



@app.route('/sign-up', methods=['GET', 'POST'])
def sign_up_func():
    user_name = request.get_json()['name']
    password = request.get_json()['password']
    return_msg = "{user_name} singed up!".format(user_name=user_name)
    user_id = None
    try:
        connection = connect_to_db()
        curser = connection.cursor()
        query = "INSERT INTO Users (name, password, points) VALUES (%s, %s, %s)"
        params = (user_name, password, 0)
        curser.execute(query, params)
        user_id = curser.lastrowid
        connection.commit()

    except Exception as e:
        print(e)
        return {
            'msg': 'Failed to join :(',
            'success': False
        }
     
    return {
        'user_name': user_name,
        'msg': '10X for joining!',
        'user_id': user_id,
        'success': True
    }

@app.route('/log-in', methods=['POST'])
def log_in_func():
    user_name = request.get_json()['name']
    user_password = request.get_json()['password']    
    try:
        connection = connect_to_db()
        curser = connection.cursor()
        query = "SELECT * FROM Users WHERE (name = %s AND password = %s)"
        curser.execute(query, (user_name, user_password))

        response = curser.fetchone()
        if response is not None:
            print("User exist")
            id, name, password, points = response
            return {
                'user_id': id,
                'msg': 'User connected',
                'user_name': name,
                'connect': True
            }
        else:
            return {
                'msg': 'Wrong user name or password!',
            }

    except Exception as e:
        print(e)
        return {
            'user_id': id,
            'msg': 'Failed to log in!',
            'user_name': user_name,
            'connect': False
        }


# @app.route('/users')
# def get_users():
#     users = get_table("users")
#     print(users)
#     return {
#         'users': users
#     }

    # return_msg = "{user_name} singed up!".format(user_name=user_name)
    # if insert_row("users", [user_name, password]) == False:
    #     return_msg = "{user_name} Failed to singed up!".format(user_name=user_name)
    
    # return {
    #     'user_name': user_name,
    #     'msg': return_msg
    # }


@app.route('/games/bet-on-game', methods=['GET', 'POST'])
def bet_on_game():
    print(request.get_json())
    game_id = request.get_json()['gameId']
    print("🚀 ~ game_id:", game_id)
    user_id = request.get_json()['userId']
    print("🚀 ~ user_id:", user_id)
    scoreA = request.get_json()['scoreA']
    print("🚀 ~ scoreA:", scoreA)
    scoreB = request.get_json()['scoreB']
    print("🚀 ~ scoreB:", scoreB)
    query = ''
    bet_id = None
    try:
        print(scoreA, scoreB)
        connection = connect_to_db()
        curser = connection.cursor()
        
        curser.execute("SELECT * FROM Bets WHERE (userId = %s AND gameId = %s)", (user_id, game_id))
        bets = curser.fetchall()
        if len(bets) > 0 and len(bets[0]) > 0:
            bet_id = bets[0][0]

        print(bet_id)

        if bet_id is not None:
            query = "UPDATE Bets SET scoreA=%s, scoreB=%s WHERE betId = %s"
            params = (scoreA, scoreB, bet_id)
        else:
            query = "INSERT INTO Bets (userId, gameId, scoreA, scoreB) VALUES (%s, %s, %s, %s)"
            params = (user_id, game_id, scoreA, scoreB)

        curser.execute(query, params)
        connection.commit()

    except Exception as e:
        print(e)
        return {
            'user_name': 'fake',
            'msg': str(e)
        }

    return {
        'msg': 'Nice Bet!'
    }


@app.route('/games/bet-real-score', methods=['GET', 'POST'])
def bet_real_score():
    game_id = request.get_json()['gameId']
    scoreA = request.get_json()['scoreA']
    scoreB = request.get_json()['scoreB']
    teamA = request.get_json()['teamA']
    teamB = request.get_json()['teamB']
    status = request.get_json()['status']
    query = ''
    try:
        connection = connect_to_db()
        curser = connection.cursor()
        
        curser.execute("SELECT * FROM Games WHERE gameId = %s", (game_id, ))
        games = curser.fetchall()

        if len(games) > 0:
            query = "UPDATE Games SET scoreA=%s, scoreB=%s WHERE gameId = %s"
            params = (scoreA, scoreB, game_id)
        else:
            query = "INSERT INTO Games (gameId, teamA, teamB, scoreA, scoreB, status) VALUES (%s, %s, %s, %s, %s, %s)"
            params = (game_id, teamA, teamB, scoreA, scoreB, status)

        curser.execute(query, params)
        connection.commit()

        calculate_score()
        connection.close()

    except Exception as e:
        print(e)
        return {
            'msg': str(e)
        }

    return {
        'msg': 'Nice Bet!'
    }

@app.route('/side-bets', methods=['GET', 'POST'])
def side_bets():
    user_id = request.get_json()['userId']
    top_scorer = request.get_json()['topScorer']
    winning_team = request.get_json()['winningTeam']
    query = ''
    bet_id = None
    try:
        connection = connect_to_db()
        curser = connection.cursor()

        curser.execute("SELECT * FROM SideBets WHERE userId=%s", (user_id,))
        bets = curser.fetchall()
        print("🚀 ~ bets:", bets)

        if len(bets) > 0 and len(bets[0]) > 0:
            bet_id = bets[0][0]

        if bet_id is not None:
            query = "UPDATE SideBets SET team=%s, player=%s WHERE id=%s"
            params = (winning_team, top_scorer, bet_id)
        else:
            query = "INSERT INTO SideBets (userId, team, player) VALUES (%s, %s, %s)"
            params = (user_id, winning_team, top_scorer)

        curser.execute(query, params)
        connection.commit()
    except Exception as e:
        return {
            'msg': str(e)
        }

    return {
        'users': 'Server recieved your bets, good luck! '
    }

@app.route('/get-side-bets', methods=['GET', 'POST'])
def get_side_bets():
    try:
        connection = connect_to_db()
        curser = connection.cursor()

        curser.execute("SELECT * FROM SideBets")
        side_bets = curser.fetchall()
        print("🚀 ~ side_bets:", side_bets)

        # if len(bets) > 0 and len(bets[0]) > 0:
        #     bet_id = bets[0][0]

        # if bet_id is not None:
        #     query = "UPDATE SideBets SET team=%s, player=%s WHERE id=%s"
        #     params = (winning_team, top_scorer, bet_id)
        # else:
        #     query = "INSERT INTO SideBets (userId, team, player) VALUES (%s, %s, %s)"
        #     params = (user_id, winning_team, top_scorer)

        # curser.execute(query)
        # connection.commit()
    except Exception as e:
        return {
            'msg': str(e)
        }

    return {
        'side_bets': side_bets
    }


@app.route('/users')
def get_games():
    try:
        connection = connect_to_db()
        curser = connection.cursor()
        curser.execute("SELECT * FROM Users")
        users = curser.fetchall()
        print("🚀 ~ users:", users)
    except Exception as e:
        return {
            'msg': e
        }

    return {
        'users': users
    }

@app.route('/userBets/<user_id>')
def get_user_bets(user_id):
    try:
        connection = connect_to_db()
        curser = connection.cursor()
        curser.execute("SELECT * FROM Bets WHERE userId=%s", (user_id,))
        bets = curser.fetchall()
        curser.execute("SELECT * FROM Games")
        games = curser.fetchall()
    except Exception as e:
        return {
            'msg': e 
        }

    return {
        'userBets': bets,
        'games': games
    }

@app.route('/get-side-bets/<user_id>') 
def get_user_side_bets(user_id):
    print(user_id)
    side_bets = None
    try:
        connection = connect_to_db()
        curser = connection.cursor()
        curser.execute("SELECT * FROM SideBets WHERE userId=%s", (user_id,))
        # if len(curser.fetchall()) > 0:
        side_bets = curser.fetchall()[0]

        if side_bets is not None and len(side_bets) > 2:
            return {
                'winningTeam': side_bets[2],
                'topScorer': side_bets[3]
            }
        else:
            return {
                'msg': 'No side bets!' 
            }
    except Exception as e:
        return {
            'msg': str(e) 
        }


@app.route('/get-bets/<game_id>') 
def get_bets(game_id):
    try:
        connection = connect_to_db()
        curser = connection.cursor()
        curser.execute("SELECT * FROM Bets WHERE gameId=%s", (game_id,))
        game_bets = curser.fetchall()
        curser.execute("SELECT * FROM Users")
        users = curser.fetchall()
        print(users)
    except Exception as e:
        return {
            'msg': e 
        }
    return {
        'game_bets': game_bets,
        'users': users
    }

@app.route('/games')
def games():
    return {
        "msg": "refresh games!"
    }

@app.route('/clean_users', methods=['POST'])
def clean_users():
    try:
        connection = connect_to_db()
        curser = connection.cursor()
        curser.execute("DELETE FROM Bets;")
        connection.commit()
        return {
            "msg": "Users were deleted!"
        }
    except Exception as e:       
        print(e)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)