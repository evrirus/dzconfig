import unittest
from lark import Lark
from main import GRAMMAR, AST, tree_to_plain, clean_tree

class TestConfigParser(unittest.TestCase):

    def parse_and_compare(self, text, expected):
        parser = Lark(GRAMMAR, parser="lalr", transformer=AST())
        result = parser.parse(text)
        plain_result = tree_to_plain(result)
        clean_result = clean_tree(plain_result)

        # main.py возвращает список верхнеуровневых словарей
        # объединяем все словари в один для удобного сравнения
        merged_result = {}
        if isinstance(clean_result, list):
            for d in clean_result:
                if isinstance(d, dict):
                    merged_result.update(d)
        else:
            merged_result = clean_result

        self.assertEqual(merged_result, expected)

    def test_network_game_config(self):
        text = """
        name = q(ProStrelok);
        server = q(localhost);

        network -> {
            name -> ^[name].
            server -> ^[server].
            game -> {
                name -> q(WoTB).
                players -> {
                    player -> {
                        name -> q(player1).
                        level -> q(odin).
                    }.
                }.
            }.
        }
        """
        expected = {
            "name": "ProStrelok",
            "server": "localhost",
            "network": {
                "name": "ProStrelok",
                "server": "localhost",
                "game": {
                    "name": "WoTB",
                    "players": {
                        "player": {
                            "name": "player1",
                            "level": "odin"
                        }
                    }
                }
            }
        }
        self.parse_and_compare(text, expected)

    def test_user_preferences_config(self):
        text = """
        defaultAge = 18;
        defaultRole = q(User);

        user -> {
            name -> q(Alex).
            age -> ^[defaultAge].
            role -> ^[defaultRole].
            preferences -> {
                theme -> q(Dark).
                notifications -> q(Enabled).
            }.
        }
        """
        expected = {
            "defaultAge": 18,
            "defaultRole": "User",
            "user": {
                "name": "Alex",
                "age": 18,
                "role": "User",
                "preferences": {
                    "theme": "Dark",
                    "notifications": "Enabled"
                }
            }
        }
        self.parse_and_compare(text, expected)

    def test_weapon_rpg_config(self):
        text = """
        baseDamage = 50;
        baseWeight = 12;

        weapon -> {
            title -> q(Sword).
            stats -> {
                damage -> ^[baseDamage].
                weight -> ^[baseWeight].
                rarity -> q(Rare).
            }.
            owner -> {
                name -> q(Player1).
                level -> 5.
            }.
        }
        """
        expected = {
            "baseDamage": 50,
            "baseWeight": 12,
            "weapon": {
                "title": "Sword",
                "stats": {
                    "damage": 50,
                    "weight": 12,
                    "rarity": "Rare"
                },
                "owner": {
                    "name": "Player1",
                    "level": 5
                }
            }
        }
        self.parse_and_compare(text, expected)

if __name__ == "__main__":
    unittest.main()
