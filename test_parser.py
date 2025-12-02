import unittest

from main import Lexer, Parser  # Импортируем ваш парсер из main.py

# python -m unittest test_parser.py
class TestConfigParser(unittest.TestCase):

    def parse_and_compare(self, input_text, expected_dict):
        # Создаём лексер и парсер
        lexer = Lexer(input_text)
        parser = Parser(lexer)
        result = parser.parse()
        self.assertEqual(result, expected_dict)

    def test_network_config(self):
        input_text = """
        name = q(ProStrelok);
        server = q(localhost);
        
        network -> {
            name -> ^[name].
            server -> ^[server].
            game -> {
                name -> q(WoTB).
            }.
        }.

        """
        expected = {
            "name": "ProStrelok",
            "server": "localhost",
            "network": {
                "name": "ProStrelok",
                "server": "localhost",
                "game": {
                    "name": "WoTB",
                }
            }
        }
        self.parse_and_compare(input_text, expected)

    def test_user_config(self):
        input_text = """
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
        }.
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
        self.parse_and_compare(input_text, expected)

    def test_game_config(self):
        input_text = """
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
            здфн
        }.
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
        self.parse_and_compare(input_text, expected)


if __name__ == "__main__":
    unittest.main()
