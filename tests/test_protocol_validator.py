import unittest
import json
import copy

import protocol_validator.protocol_validator as pvalid




class ProtocolvalidatorTestCase(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(ProtocolvalidatorTestCase, self).__init__(*args, **kwargs)
        self.dummy_direction = {
            #required
            'container': 'plate A',
            'location': 'A1',
            #optional
            'tip-offset': 0,
            'delay': 0,
            'touch-tip': False,
            'blowout': False,
            'extra-pull': False,
            'liquid-tracking': False
        }

        self.dummy_direction_mix = copy.deepcopy(self.dummy_direction)
        self.dummy_direction_mix['repetitions'] = 4

        self.dummy_mix = [
            copy.deepcopy(self.dummy_direction_mix),
            copy.deepcopy(self.dummy_direction_mix)
        ]

        self.dummy_distribute = {
            'from': copy.deepcopy(self.dummy_direction),
            'to': [
                copy.deepcopy(self.dummy_direction),
                copy.deepcopy(self.dummy_direction)
            ],
            'blowout': False
        }

        self.dummy_consolidate = {
            'to': copy.deepcopy(self.dummy_direction),
            'from': [
                copy.deepcopy(self.dummy_direction),
                copy.deepcopy(self.dummy_direction)
            ],
            'blowout': False
        }

        self.dummy_transfer = {
            'from': copy.deepcopy(self.dummy_direction),
            'to': copy.deepcopy(self.dummy_direction)
        }

        self.dummy_transfers = [
            copy.deepcopy(self.dummy_transfer),
            copy.deepcopy(self.dummy_transfer)
        ]
        # GROUPS
        self.dummy_group_transfer = {
            'transfer': copy.deepcopy(self.dummy_transfer)
        }

        self.dummy_group_distribute = {
            'distribute': copy.deepcopy(self.dummy_distribute)
        }

        self.dummy_group_consolidate = {
            'consolidate': copy.deepcopy(self.dummy_consolidate)
        }

        self.dummy_group_mix = {
            'mix': copy.deepcopy(self.dummy_mix)
        }
        # INSTRUCTIONS
        self.dummy_instruction = {
            'tool': 'p10',
            'groups': [
                copy.deepcopy(self.dummy_group_transfer),
                copy.deepcopy(self.dummy_group_distribute),
                copy.deepcopy(self.dummy_group_consolidate),
                copy.deepcopy(self.dummy_group_mix)
            ]
        }

        self.dummy_instructions = [
            copy.deepcopy(self.dummy_instruction),
            copy.deepcopy(self.dummy_instruction)
        ]


    def setUp(self):
        self.validator = pvalid.JSONProtocolValidator(
            'tests/fixtures/containers.json',
            'tests/fixtures/protocol.json'
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
        deck_data = dummy_protocol.get('deck')
        deck_errors = self.validator.validate_deck(deck_data).get('errors')
        print(json.dumps(deck_errors, sort_keys=True, indent=4))
        self.assertEqual(len(deck_errors), 4)


    def test_validate_ingredients_allpassing(self):
        pass


    def test_1_direction_allpassing(self):
        messages = self.validator.validate_direction('from',self.dummy_direction,0,0,'Transfer',0)
        print('DIRECTION TEST: ',json.dumps(messages, indent=1))
        self.assertEqual(len(messages['errors']),0)

    def test_2_direction_mix_allpassing(self):
        messages = self.validator.validate_direction('mix',self.dummy_direction_mix,0,0,'Mix',0)
        print('DIRECTION MIX TEST: ',json.dumps(messages, indent=1))
        self.assertEqual(len(messages['errors']),0)

    def test_3_mix_all_passing(self):
        messages = self.validator.validate_mix(self.dummy_mix,0,0)
        print('MIX TEST: ',json.dumps(messages, indent=1))
        self.assertEqual(len(messages['errors']),0)

    def test_4_distribute_all_passing(self):
        messages = self.validator.validate_dist_cons(self.dummy_distribute, 0, 0)
        print('DISTRIBUTE TEST: ',json.dumps(messages, indent=1))
        self.assertEqual(len(messages['errors']),0)

    def test_5_consolidate_allpassing(self):
        messages = self.validator.validate_dist_cons(self.dummy_consolidate, 0, 0, False)
        print('CONSOLIDATE TEST: ',json.dumps(messages, indent=1))
        self.assertEqual(len(messages['errors']),0)

    def test_6_transfer_allpassing(self):
        messages = self.validator.validate_transfer(self.dummy_transfer, 0, 0)
        print('TRANSFER TEST: ',json.dumps(messages, indent=1))
        self.assertEqual(len(messages['errors']),0)

    def test_7_group_transfers_allpassing(self):
        messages = self.validator.validate_group(self.dummy_group_transfer, 0, 0)
        print('GROUP TRANSFER TEST: ',json.dumps(messages, indent=1))
        self.assertEqual(len(messages['errors']),0)

    def test_8_group_distribute_allpassing(self):
        messages = self.validator.validate_group(self.dummy_group_distribute, 0, 0)
        print('GROUP DISTRIBUTE TEST: ',json.dumps(messages, indent=1))
        self.assertEqual(len(messages['errors']),0)

    def test_9_group_consolidate_allpassing(self):
        messages = self.validator.validate_group(self.dummy_group_consolidate, 0, 0)
        print('GROUP CONSOLIDATE TEST: ',json.dumps(messages, indent=1))
        self.assertEqual(len(messages['errors']),0)

    def test_91_group_mix_allpassing(self):
        messages = self.validator.validate_group(self.dummy_group_mix, 0, 0)
        print('GROUP MIX TEST: ',json.dumps(messages, indent=1))
        self.assertEqual(len(messages['errors']),0)

    def test_92_instruction_allpassing(self):
        messages = self.validator.validate_instruction(self.dummy_instruction, 0)
        print('INDIV. INSTRUCTION TEST: ',json.dumps(messages, indent=1))
        self.assertEqual(len(messages['errors']),0)

    def test_93_instructions_allpassing(self):
        messages = self.validator.validate_instructions(self.dummy_instructions)
        print('INSTRUCTIONS TRANSFER TEST: ',json.dumps(messages, indent=1))
        self.assertEqual(len(messages['errors']),0)

if __name__ == '__main__':
    unittest.main()
