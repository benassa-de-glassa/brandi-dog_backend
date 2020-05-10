from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

class TestGame:
    def setup_class(self):
        self.players = [
            {
                "name": "Thilo",
                "uid": "AAAA",
            }, 
            {
                "name": "Lara",
                "uid": "BBBB",
            }, 
            {
                "name": "Bibi",
                "uid": "CCCC",
            }, 
            {
                "name": "Bene",
                "uid": "DDDD",
            }
        ]
        self.game_ids = []
        self.cards = []

    def test_request_initialize_game(self):
        res = client.post('v1/games?seed=1',
            json=self.players[0]
        )

        assert res.status_code == 200
        assert res.json()["players"][0]["name"] == "Thilo"
        self.game_ids += [res.json() ["game_id"]]

        res = client.post('v1/games',
            json=self.players[1]
        )

    def test_request_get_game_list(self):
        res = client.get('v1/games')

        assert res.status_code == 200
        assert len(res.json()) == 2
        for idx, game_id in enumerate(self.game_ids):
            assert game_id == res.json()[idx]["game_id"]

    def test_get_individual_game_data(self):
        res = client.get(f'v1/games/{self.game_ids[0]}',
            json=self.players[0]
        )
        assert res.status_code == 200

        assert res.json()["game_id"] == self.game_ids[0]
        assert len(res.json()["players"]) == len(res.json()["order"])
        assert res.json()["active_player_index"] == 0

    def test_join_game(self):
        res = client.post(f'v1/games/{self.game_ids[0]}/join',
            json=self.players[0]
        )
        # should fail as the player is already in that game
        assert res.status_code == 400
        res = client.post(f'v1/games/{self.game_ids[0]}/join',
            json=self.players[1]
        )

        assert res.status_code == 200
        assert len(res.json()["players"]) == 2
        res = client.post(f'v1/games/{self.game_ids[0]}/join',
            json=self.players[2]
        )
        res = client.post(f'v1/games/{self.game_ids[0]}/join',
            json=self.players[3]
        )
        assert len(res.json()["players"]) == 4

    def test_change_team(self):
        res = client.post(f'v1/games/{self.game_ids[0]}/teams',
            json={
                "player": self.players[0],
                "teams": [self.players[i] for i in [0, 2, 1, 3]]
            }
        )
        assert res.status_code == 200
        assert res.json()["order"] == [self.players[i]["uid"] for i in [0, 2, 1, 3]]


        # reset the game order
        res = client.post(f'v1/games/{self.game_ids[0]}/teams',
            json={
                "player": self.players[1],
                "teams": [self.players[i] for i in [0, 1, 2, 3]]
            }
        )
    
    def test_start_game_and_check_cards(self):
        res = client.post(f'v1/games/{self.game_ids[0]}/start',
            json=self.players[0],
        )

        assert res.status_code == 200

        for i in range(4):
            for j in range(4):
                assert res.json()["players"][i]["marbles"][j]["position"] == -1
        
        res = client.get(f'v1/games/{self.game_ids[0]}/cards',
            json=self.players[0],
        )
        assert res.status_code == 200

        assert res.json()["uid"] == "AAAA"
        assert res.json()["hand"][0]["uid"] == 99
        self.cards.append(res.json()["hand"])
        
        for i in range(1, 4):
            res = client.get(f'v1/games/{self.game_ids[0]}/cards',
                json=self.players[i],
            )	
            assert res.status_code == 200

            self.cards.append(res.json()["hand"])
        

    def test_swap_cards(self):
        res = client.post(f'v1/games/{self.game_ids[0]}/swap_cards',
            json={
                "player": self.players[0],
                "card": self.cards[0][0]
            }
        )
        assert res.status_code == 200

        for i in range(1, 4):
            res = client.post(f'v1/games/{self.game_ids[0]}/swap_cards',
                json={
                    "player": self.players[i],
                    "card": self.cards[i][0]
                }
            )
            assert res.status_code == 200

        for i in range(4):
            res = client.get(f'v1/games/{self.game_ids[0]}/cards',
                json=self.players[i],
            )	
            assert res.status_code == 200
            self.cards[i] = res.json()["hand"]
            assert len(self.cards[i]) == 6
            
        assert any([card["uid"] == 99 for card in self.cards[2]])

    """
    Cards at this point given seed 1
    [
        [ # player 0
            {'uid': 84, 'value': '4', 'color': 'hearts', 'actions': [-4, 4]}, 
            {'uid': 68, 'value': '6', 'color': 'hearts', 'actions': [6]}, 
            {'uid': 10, 'value': 'K', 'color': 'diamonds', 'actions': [0, 13]}, 
            {'uid': 105, 'value': 'Jo', 'color': 'Jo', 'actions': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 'switch', -4]}, 
            {'uid': 9, 'value': 'K', 'color': 'clubs', 'actions': [0, 13]}, 
            {'uid': 89, 'value': '3', 'color': 'clubs', 'actions': [3]}
        ], 
        [ # player 1
            {'uid': 92, 'value': '3', 'color': 'hearts', 'actions': [3]}, 
            {'uid': 88, 'value': '3', 'color': 'clubs', 'actions': [3]}, 
            {'uid': 4, 'value': 'A', 'color': 'hearts', 'actions': [0, 1, 11]}, 
            {'uid': 73, 'value': '5', 'color': 'clubs', 'actions': [5]}, 
            {'uid': 33, 'value': '10', 'color': 'clubs', 'actions': [10]}, 
            {'uid': 5, 'value': 'A', 'color': 'hearts', 'actions': [0, 1, 11]}
        ], 
        [ # player 2
            {'uid': 87, 'value': '4', 'color': 'spades', 'actions': [-4, 4]}, 
            {'uid': 52, 'value': '8', 'color': 'hearts', 'actions': [8]}, 
            {'uid': 38, 'value': '10', 'color': 'spades', 'actions': [10]}, 
            {'uid': 43, 'value': '9', 'color': 'diamonds', 'actions': [9]}, 
            {'uid': 20, 'value': 'Q', 'color': 'hearts', 'actions': [12]}, 
            {'uid': 99, 'value': '2', 'color': 'diamonds', 'actions': [2]}
        ], 
        [ # player 3
            {'uid': 74, 'value': '5', 'color': 'diamonds', 'actions': [5]}, 
            {'uid': 16, 'value': 'Q', 'color': 'clubs', 'actions': [12]}, 
            {'uid': 14, 'value': 'K', 'color': 'spades', 'actions': [0, 13]}, 
            {'uid': 36, 'value': '10', 'color': 'hearts', 'actions': [10]}, 
            {'uid': 59, 'value': '7', 'color': 'diamonds', 'actions': [7]}, 
            {'uid': 78, 'value': '5', 'color': 'spades', 'actions': [5]}
        ]
    ]
    """

    def test_move_marble(self):
        # player 0 makes a move
        res = client.post(f'v1/games/{self.game_ids[0]}/action',
            json={
                "player": self.players[0],
                "action": {
                    "card": {
                        'uid': 10, 
                        'value': 'K', 
                        'color': 'diamonds', 
                        'actions': [0, 13]
                    },
                    "action": 0,
                    "mid": 0 
                }
            }
        )

        assert res.status_code == 200
        assert res.json()["players"][0]["marbles"][0]["position"] == 0
        
        # player 1 makes a move
        res = client.post(f'v1/games/{self.game_ids[0]}/action',
            json={
                "player": self.players[1],
                "action": {
                    "card": {
                        'uid': 4, 
                        'value': 'A', 
                        'color': 'hearts', 
                        'actions': [0, 1, 11]
                    },
                    "action": 0,
                    "mid": 4 
                }
            }
        )
        assert res.status_code == 200
        assert res.json()["players"][1]["marbles"][0]["position"] == 16

        # player 2 has to fold
        res = client.post(f'v1/games/{self.game_ids[0]}/fold',
            json=self.players[2],
        )
        assert res.json()['hand'] == []

        # player 3 makes a move
        res = client.post(f'v1/games/{self.game_ids[0]}/action',
            json={
                "player": self.players[3],
                "action": {
                    "card": {
                        'uid': 14, 
                        'value': 'K', 
                        'color': 'spades', 
                        'actions': [0, 13]
                    }, 
                    "action": 0,
                    "mid": 12
                }
            }
        )

        assert res.json()["players"][3]["marbles"][0]["position"] == 48

        """
        Current state of game
        [
            {
                'uid': 'AAAA', 
                'name': 'Thilo', 
                'marbles': [
                    {'mid': 0, 'position': 0, 'color': None}, 
                    {'mid': 1, 'position': -1, 'color': None}, 
                    {'mid': 2, 'position': -1, 'color': None}, 
                    {'mid': 3, 'position': -1, 'color': None}
                ]
            }, 
            {
                'uid': 'BBBB', 
                'name': 'Lara', 
                'marbles': [
                    {'mid': 4, 'position': 16, 'color': None}, 
                    {'mid': 5, 'position': -1, 'color': None}, 
                    {'mid': 6, 'position': -1, 'color': None}, 
                    {'mid': 7, 'position': -1, 'color': None}
                ]
            }, 
            {
                'uid': 'CCCC', 
                'name': 'Bibi', 
                'marbles': [
                    {'mid': 8, 'position': -1, 'color': None}, 
                    {'mid': 9, 'position': -1, 'color': None}, 
                    {'mid': 10, 'position': -1, 'color': None}, 
                    {'mid': 11, 'position': -1, 'color': None}
                ]
            }, 
            {
                'uid': 'DDDD', 
                'name': 'Bene', 
                'marbles': [
                    {'mid': 12, 'position': 48, 'color': None}, 
                    {'mid': 13, 'position': -1, 'color': None}, 
                    {'mid': 14, 'position': -1, 'color': None}, 
                    {'mid': 15, 'position': -1, 'color': None}
                ]
            }
        ]
        """

        res = client.post(f'v1/games/{self.game_ids[0]}/action',
            json={
                "player": self.players[0],
                "action": {
                    "card": {
                        'uid': 84, 
                        'value': '4', 
                        'color': 'hearts', 
                        'actions': [-4, 4]
                    }, 
                    "action": -4,
                    "mid": 0 
                }
            }
        )

        assert res.status_code == 200
        assert res.json()["players"][0]["marbles"][0]["position"] == 60

        res = client.post(f'v1/games/{self.game_ids[0]}/action',
            json={
                "player": self.players[1],
                "action": {
                    "card": {
                        'uid': 92, 
                        'value': '3', 
                        'color': 'hearts', 
                        'actions': [3]
                    }, 
                    "action": 3,
                    "mid": 4
                }
            }
        )

        assert res.status_code == 200
        assert res.json()["players"][1]["marbles"][0]["position"] == 19

        res = client.post(f'v1/games/{self.game_ids[0]}/action',
            json={
                "player": self.players[3],
                "action": {
                    "card": {
                        'uid': 16, 
                        'value': 'Q', 
                        'color': 'clubs', 
                        'actions': [12]
                    },
                    "action": 12,
                    "mid": 12
                }
            }
        )

        assert res.json()["players"][3]["marbles"][0]["position"] == 60
        assert res.json()["players"][0]["marbles"][0]["position"] == -1
