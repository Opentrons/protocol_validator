import unittest

import protocol_verifier


class ProtocolVerifierTestCase(unittest.TestCase):
    def setUp(self):
        self.verifier = protocol_verifier.JSONProtocolVerifier(
            'test_data/p10s.json',
            'test_data/containers.json'
        )

    def test_deck_verify(self):
        self.verifier.protocol = {
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

        deck_errors = self.verifier.verify_deck()
        self.assertEqual(len(deck_errors), 4)

    def test_verify_head(self):
        pass


if __name__ == '__main__':
    unittest.main()
