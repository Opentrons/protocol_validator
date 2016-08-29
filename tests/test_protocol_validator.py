import unittest
import json

import protocol_validator.protocol_validator as pvalid




class ProtocolvalidatorTestCase(unittest.TestCase):
    def setUp(self):
        self.validator = pvalid.JSONProtocolValidator(
            'tests/fixtures/protocol.json',
            'tests/fixtures/containers.json'
        )

    def test_init_with_string(self):
        # string containers & protocol
        self.validator_string = pvalid.JSONProtocolValidator('','')
        # assert something showing whether init with string worked


    def test_init_with_object(self):
        # object (dict) containers & protocol
        self.validator_object = pvalid.JSONProtocolValidator({},{})
        # assert something showing whether init with object (dict) worked


    def test_validate_deck(self):
        dummy_protocol = {
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
        self.validator.protocol = pvalid.Protocol(dummy_protocol)
        deck_errors = self.validator.validate_deck().get('errors')
        print(json.dumps(deck_errors, sort_keys=True, indent=4))
        self.assertEqual(len(deck_errors), 4)

    def test_validate_head(self):
        pass


    def test_validate_instructions(self):
        pass


    def test_validate_ingredients(self):
        pass


if __name__ == '__main__':
    unittest.main()
