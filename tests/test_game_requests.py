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

                          json={
                              'player': self.players[0],
                              'game_name': 'test_game'
                          }
                          )

        assert res.status_code == 200

        self.game_ids += [res.json()["game_id"]]

        res = client.post('v1/games',
                          json={
                              'player': self.players[1],
                              'game_name': 'test_game_2'
                          }
                          )
        assert res.status_code == 200

    def test_join_game(self):
        for player in self.players:
            res = client.post(f'v1/games/{self.game_ids[0]}/join',
                              json=player
                              )
            print(res.json())
            assert res.status_code == 200
            assert res.json()["players"][player["uid"]
                                         ]["name"] == player["name"]

    def test_request_get_game_list(self):
        res = client.get('v1/games')

        print(res.json())
        assert res.status_code == 200
        assert len(res.json()) == 2
        for idx, game_id in enumerate(self.game_ids):
            assert game_id == res.json()[idx]["game_id"]

    def test_get_individual_game_data(self):
        res = client.get(f'v1/games/{self.game_ids[0]}',
                         json=self.players[0]
                         )
        print(res.json())
        assert res.status_code == 200

        assert res.json()["game_id"] == self.game_ids[0]
        assert len(res.json()["players"]) == len(res.json()["order"])
        assert res.json()["active_player_index"] == 0

    def test_change_team(self):
        res = client.post(f'v1/games/{self.game_ids[0]}/teams',
                          json={
                              "player": self.players[0],
                              "teams": [self.players[i] for i in [0, 2, 1, 3]]
                          }
                          )
        assert res.status_code == 200
        assert res.json()["order"] == [self.players[i]["uid"]
                                       for i in [0, 2, 1, 3]]

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
                assert res.json()["players"][self.players[i]["uid"]
                                             ]["marbles"][j]["position"] == - i*4 - j - 1

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

    def test_0_player_0_moves_from_house(self):
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
        assert res.json()["players"][self.players[0]["uid"]
                                     ]["marbles"][0]["position"] == 0

    def test_1_player_1_moves_from_house(self):
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
        assert res.json()["players"][self.players[1]["uid"]
                                     ]["marbles"][0]["position"] == 16

    def test_2_player_2_folds(self):
        # player 2 has to fold
        res = client.post(f'v1/games/{self.game_ids[0]}/fold',
                          json=self.players[2],
                          )
        assert res.json()['hand'] == []

    def test_3_player_3_moves_from_house(self):
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

        assert res.json()["players"][self.players[3]["uid"]
                                     ]["marbles"][0]["position"] == 48

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

    def test_4_player_0_moves_back_four(self):
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
        assert res.json()["players"][self.players[0]["uid"]
                                     ]["marbles"][0]["position"] == 60
    
    def test_5_player_1_moves_up_three(self):
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
        assert res.json()["players"][self.players[1]["uid"]
                                     ]["marbles"][0]["position"] == 19

        """
        {
            'game_id': 'MQLS', 
            'game_name': 'test_game', 
            'host': {
                'uid': 'AAAA', 'name': 'Thilo', 'marbles': []
                }, 
            'game_state': 2, 
            'round_state': 3, 
            'round_turn': 0, 
            'order': ['AAAA', 'BBBB', 'CCCC', 'DDDD'], 
            'active_player_index': 3, 
            'players': {
                'AAAA': {
                    'uid': 'AAAA', 'name': 'Thilo', 
                    'marbles': [
                        {'mid': 0, 'position': 60, 'color': 'red'}, 
                        {'mid': 1, 'position': -2, 'color': 'red'}, 
                        {'mid': 2, 'position': -3, 'color': 'red'}, 
                        {'mid': 3, 'position': -4, 'color': 'red'}
                    ]
                }, 
                'BBBB': {
                    'uid': 'BBBB', 'name': 'Lara', 
                    'marbles': [
                        {'mid': 4, 'position': 19, 'color': 'yellow'}, 
                        {'mid': 5, 'position': -6, 'color': 'yellow'}, 
                        {'mid': 6, 'position': -7, 'color': 'yellow'}, 
                        {'mid': 7, 'position': -8, 'color': 'yellow'}
                    ]
                }, 
                'CCCC': {
                    'uid': 'CCCC', 'name': 'Bibi', 
                    'marbles': [
                        {'mid': 8, 'position': -9, 'color': 'green'}, 
                        {'mid': 9, 'position': -10, 'color': 'green'}, 
                        {'mid': 10, 'position': -11, 'color': 'green'}, 
                        {'mid': 11, 'position': -12, 'color': 'green'}
                    ]
                }, 
                'DDDD': {
                    'uid': 'DDDD', 'name': 'Bene', 
                    'marbles': [
                        {'mid': 12, 'position': 48, 'color': 'blue'}, 
                        {'mid': 13, 'position': -14, 'color': 'blue'}, 
                        {'mid': 14, 'position': -15, 'color': 'blue'}, 
                        {'mid': 15, 'position': -16, 'color': 'blue'}
                    ]
                }
            }
        }
        """

    def test_6_player_3_moves_up_12_and_kicks_player_0(self):
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

        assert res.json()["players"][self.players[3]["uid"]
                                     ]["marbles"][0]["position"] == 60
        assert res.json()["players"][self.players[0]["uid"]
                                     ]["marbles"][0]["position"] == -1

    def test_7_player_0_moves_from_house(self):
        res = client.post(f'v1/games/{self.game_ids[0]}/action',
                          json={
                              "player": self.players[0],
                              "action": {
                                  "card": {
                                      'uid': 9,
                                      'value': 'K',
                                      'color': 'clubs',
                                      'actions': [0, 13]
                                  },
                                  "action": 0,
                                  "mid": 1
                              }
                          }
                          )

        assert res.status_code == 200
        assert res.json()["players"][self.players[0]["uid"]
                                     ]["marbles"][1]["position"] == 0

    def test_8_player_1_bad_request(self):
        # make bad request by trying to start a marble which is not in a starting postion
        res = client.post(f'v1/games/{self.game_ids[0]}/action',
                          json={
                              "player": self.players[1],
                              "action": {
                                  "card": {
                                      'uid': 5,
                                      'value': 'A',
                                      'color': 'hearts',
                                      'actions': [0, 1, 11]
                                  },
                                  "action": 0,
                                  "mid": 4
                              }
                          }
                          )
        assert res.status_code == 400

    def test_10_player_1_moves_from_house(self):
        res = client.post(f'v1/games/{self.game_ids[0]}/action',
                          json={
                              "player": self.players[1],
                              "action": {
                                  "card": {
                                      'uid': 5,
                                      'value': 'A',
                                      'color': 'hearts',
                                      'actions': [0, 1, 11]
                                  },
                                  "action": 0,
                                  "mid": 5
                              }
                          }
                          )

        assert res.status_code == 200
        assert res.json()["players"][self.players[1]["uid"]
                                     ]["marbles"][0]["position"] == 19
        assert res.json()["players"][self.players[1]["uid"]
                                     ]["marbles"][1]["position"] == 16

    def test_11_player_3_marble_blocked(self):
        # bad request should fail as there is a marble blocking
        res = client.post(f'v1/games/{self.game_ids[0]}/action',
                          json={
                              "player": self.players[3],
                              "action": {
                                  "card": {
                                      'uid': 78,
                                      'value': '5',
                                      'color': 'spades',
                                      'actions': [5]
                                  },
                                  "action": 5,
                                  "mid": 12
                              }
                          }
                          )
        assert res.status_code == 400

    def test_12_player_3_folds(self):
        # player 3 has to fold as he has no viable cards
        res = client.post(f'v1/games/{self.game_ids[0]}/fold',
                          json=self.players[3],
                          )
        assert res.status_code == 200
        assert res.json()['hand'] == []

    def test_13_player_0_moves_back_four(self):
        res = client.post(f'v1/games/{self.game_ids[0]}/action',
                          json={
                              "player": self.players[0],
                              "action": {
                                  "card": {
                                      'uid': 105,
                                      'value': 'Jo',
                                      'color': 'Jo',
                                      'actions': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 'switch', -4]
                                  },
                                  "action": -4,
                                  "mid": 1
                              }
                          }
                          )

        assert res.status_code == 200
        assert res.json()["players"][self.players[0]["uid"]
                                     ]["marbles"][1]["position"] == 60

    def test_14_player_1_kicks_himself(self):
        # player 1 decides to kick his own marble at position 19
        res = client.post(f'v1/games/{self.game_ids[0]}/action',
                          json={
                              "player": self.players[1],
                              "action": {
                                  "card": {
                                      'uid': 88,
                                      'value': '3',
                                      'color': 'clubs',
                                      'actions': [3]
                                  },
                                  "action": 3,
                                  "mid": 5
                              }
                          }
                          )
        assert res.status_code == 200
        assert res.json()["players"][self.players[1]["uid"]
                                     ]["marbles"][0]["position"] == -5
        assert res.json()["players"][self.players[1]["uid"]
                                     ]["marbles"][1]["position"] == 19

    def test_15_player_0_moves_to_home(self):
        # player 0 moves 6 steps ahead, thereby entering his own goal
        res = client.post(f'v1/games/{self.game_ids[0]}/action',
                          json={
                              "player": self.players[0],
                              "action": {
                                  "card": {
                                      'uid': 68,
                                      'value': '6',
                                      'color': 'hearts',
                                      'actions': [6]},
                                  "action": 6,
                                  "mid": 1
                              }
                          }
                          )

        assert res.status_code == 200
        assert res.json()["players"][self.players[0]["uid"]
                                     ]["marbles"][1]["position"] == 1002

        # player 0 and 1 fold. this should not be possible, but I
        # haven't implemented a check whether a player still has
        # playable cards
        #
        # also its easier this way as I don't have to write more
        # requests to finish this round

    def test_16_player_1_folds(self):
        # player 1 folds
        res = client.post(f'v1/games/{self.game_ids[0]}/fold',
                          json=self.players[1],
                          )
        assert res.status_code == 200

    def test_17_player_1_folds(self):
        # player 0 folds
        res = client.post(f'v1/games/{self.game_ids[0]}/fold',
                          json=self.players[0],
                          )

        assert res.status_code == 200

    def test_18_player_0_view_cards(self):
        # player 0 requests to view his new cards
        res = client.get(f'v1/games/{self.game_ids[0]}/cards',
                         json=self.players[0],
                         )

        assert res.status_code == 200
        assert len(res.json()['hand']) == 5
