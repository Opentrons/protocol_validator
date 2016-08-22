import unittest

import protocol_validator


class ProtocolvalidatorTestCase(unittest.TestCase):
    def setUp(self):
        self.validator = protocol_validator.JSONProtocolValidator(
            'data/p10s.json',
            'data/containers.json'
        )

    def test_validate_deck(self):
        self.validator.protocol = {
            "deck": {
                "p10-rack": {
                    "labware": "FAKE-LABWARE",
                    "slot": "A1"
                },
                "foo-bar": {
                    "slot": "A1"
                },
                "bar-foo": {
                    "labware": "unc_rack"
                },
                "trash": {
                    "labware": "point",
                    "slot": "FAKE-SLOT"
                }
            }
        }

        deck_errors = self.validator.validate_deck()
        print(deck_errors)
        self.assertEqual(len(deck_errors), 4)

    def test_validate_head(self):
        pass


if __name__ == '__main__':
    unittest.main()
