# cluewords
Game server for cluewords.

* [Install Guide](#install-guide)
  * [Ubuntu 16.04](#ubuntu-16.04)
* [API Documentation](#api-documentation)
  * [REST API](#rest-api)
  * [Websockets API](#websockets-api)

## Install guide
### Ubuntu 16.04
install mysql:
````sh
sudo apt-get update
sudo apt-get install mysql-server
````

clone code base:
````sh
git clone https://github.com/doublepeaks619/cluewords.git && cd cluewords
````

install pip:
````sh
sudo apt-get install python-pip`
````

install python dependencies:
````sh
cd server
sudo pip install -r python_dependencies.txt
````

install mysql-client:
````sh
sudo apt-get install mysql-client
````

setup database:
````sh
mysql --host localhost --user root --password < create_database.txt
````

forward port 80 to port 5000 (optional, do this if you want to access it via port 80):
````sh
sudo sysctl -w net.ipv4.ip_forward=1
sudo /etc/init.d/procps restart
sudo iptables -t nat -A POSTROUTING -j MASQUERADE
sudo iptables -t nat -A PREROUTING -p tcp --dport 80 -j REDIRECT --to-port 5000
````

run web app:
````sh
python app.py
````

## API Documentation

### REST API
See [example game client pages](templates/) for use of REST API.

#### Log in a user to access the restricted APIs
````    
POST /login
{player_id: "aplayerid", password: "pwrd"}

Response Codes:
200 - OK
401 - Not authorised: username/password incorrect
500 - Server Error

Notes:
If the player_id is not found, a new login is created for this player with the given password.
If the player_id is already known the password is verified against the held details.
````

#### Create a new game
````    
POST /game
{
    game_name: "any game name",
    player1a: "blue-team-clue-giver ID",
    player1b: "blue team guesser ID",
    player2a: "red team clue giver ID",
    player2b: "red team guesser ID"
}

Response Codes:
200 - OK
400 - Client error: bad supplied data
500 - Server Error

Response body:
{"game_id":1}
````

#### End a game
````    
DELETE /game
{player_id: "player id"}

Response Codes:
200 - OK
400 - Client error: bad supplied data
500 - Server Error
````

#### Supply a guess
````    
POST /game/<game_id>/guess
{player_id: "playerid", guess_word: "WORD"}

Response Codes:
200 - OK
400 - Client error: bad supplied data
500 - Server Error

Response body:
{"turn_id":1}
````

#### Supply a clue
````    
POST /game/<game_id>/clue
{player_id: "playerid", clue_word: "word", clue_number: "1"}

Response Codes:
200 - OK
400 - Client error: bad supplied data
500 - Server Error

Response body:
{"turn_id":1}
````

#### List games
````    
GET /player/<player_id>/games

Response Codes:
200 - OK
400 - Client error: bad supplied data
500 - Server Error

Response body:
[{"id":1,"name":"game name"}, ...]
````

### Websockets API
See [example game client](templates/game_board.html) for use of websockets.

#### Sign up for notifications for a game
````
Sender: client
Event name: join_game
{"player_id":"playerid","game_id":2}
````

#### Stop receiving notifications for a game
````
Sender: client
Event name: leave_game
{"player_id":"playerid","game_id":2}
````

#### The current state of the game
````
Sender: server
Event name: gamestate
["gamestate", {
	"expected_team": 1,
	"guess": "WORD",
	"guess_remaining": 1,
	"expected_player": "playerid",
	"cluers": ["blue team clue give", "red team clue giver"],
	"clue": "word",
	"ended": 1,
	"board": [{
		"actual": card_value,
		"guess": card_value,
		"word": "WORD"
	  }, ...
    ],
	"clue_number": 1,
	"game_id": 2,
	"guessers": ["blue team guesser", "red team guesser"],
	"remaining_blue": 9,
	"remaining_red": 8
}]
````
