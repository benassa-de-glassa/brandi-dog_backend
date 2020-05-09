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
        print(res.json())
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
        print(res.json())
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
        assert res.json()["uid"] == "AAAA"
        assert res.json()["hand"][0]["uid"] == 99
        
        self.cards += [res.json()["hand"]]
        

    def test_swap_cards(self):
        res = client.post(f'v1/games/{self.game_ids[0]}/swap_cards',
            json={
                "player": self.players[0],
                "card": self.cards[0][0]
            }
        )

        print(res.json())

        assert res.status_code == 200
        assert len(res.json()["hand"]) == 5
