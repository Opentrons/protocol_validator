import json


class Container(object):
    def __init__(self, json_data: dict):
        self.data = json_data

    def __contains__(self, key):
        return key in self.data.get('containers', {})

    def has_slot(self, labware: str, slot: str):
        container = self.data.get('containers', {}).get(labware)
        return slot in container.get('locations', {})


class JSONProtocolValidator(object):
    def __init__(self, protocol_file_path: str, containers_file_path: str):
        with open(protocol_file_path) as protocol_json:
            self.protocol = json.load(protocol_json)

        with open(containers_file_path) as containers_json:
            self.containers = Container(json.load(containers_json))

    def ensure_main_sections(self):
        errors = []
        if 'head' not in self.protocol:
            errors.append('Protocol JSON must define a "head" section')
        if 'deck' not in self.protocol:
            errors.append('Protocol JSON must define a "deck" section')
        return errors

    def validate(self) -> list:
        """Entry method
        """

        main_section_errors = self.ensure_main_sections()
        if main_section_errors:
            return main_section_errors

        deck_errors = self.validate_deck()
        head_errors = self.validate_head()
        ingredients_errors = self.validate_ingredients()
        instructions_errors = self.validate_instructions()

        return sum([
            deck_errors,
            head_errors,
            ingredients_errors,
            instructions_errors
        ], [])

    def validate_head(self) -> list:
        return []

    def validate_deck(self) -> list:
        """
        Verifies that all users labwares are defined in the containers
        data
        """
        errors = []

        deck_data = self.protocol.get('deck', {})

        for container_name, container_definition in deck_data.items():
            labware = container_definition.get('labware')
            slot = container_definition.get('slot')

            if not labware or not slot:
                errors.append(
                    'Container "{}" MUST define a "labware" and "slot" attribute'
                    .format(container_name)
                )
                continue

            if labware not in self.containers:
                errors.append(
                    'Labware "{}" was not found in containers data'
                    .format(labware)
                )
            else:
                if not self.containers.has_slot(labware, slot):
                    errors.append(
                        'Labware slot "{}" was not found in the "{}" container'
                        .format(slot, labware)
                    )
        return errors
