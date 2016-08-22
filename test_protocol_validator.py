import unittest

import protocol_validator


class ProtocolvalidatorTestCase(unittest.TestCase):
    def setUp(self):
        self.validator = protocol_validator.JSONProtocolvalidator(
            'test_data/p10s.json',
            'test_data/containers.json'
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
        self.assertEqual(len(deck_errors), 4)

    def test_validate_head(self):
        pass


if __name__ == '__main__':
    unittest.main()
