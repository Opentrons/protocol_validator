import json
import os
import sys

class Containers(object):
    def __init__(self, json_data: dict):
        self.data = json_data

    def __contains__(self, key):
        return key in self.data.get('containers', {})

    def has_location(self, labware: str, location: str):
        container = self.data.get('containers', {}).get(labware)
        return location in container.get('locations', {})


class Head(object):
    def __init__(self, json_data: dict):
        self.data = json_data

    def __contains__(self, key):
        return key in list(self.data.keys())


class Deck(object):
    def __init__(self, json_data: dict):
        self.data = json_data

    def __contains__(self, key):
        return key in list(self.data.keys())


class Protocol(object):
    def __init__(self, json_data: dict):
        self.data = json_data
        self.head = Head(self.data.get('head', {}))
        self.deck = Deck(self.data.get('deck', {}))

    def __contains__(self, key):
        return key in list(self.data.keys())





class JSONProtocolValidator(object):

    COMMAND_TYPES = [
        'transfer',
        'distribute',
        'consolidate',
        'mix'
    ]

    DECK_SLOTS = [
        'A1','B1','C1','D1','E1',
        'A2','B2','C2','D2','E2',
        'A3','B3','C3','D3','E3'
    ]


    def __init__(self, containers='', protocol=''):
        self.containers = None
        self.protocol = None
        try:
            if isinstance(containers, dict):
                self.containers = Containers(containers)
            elif os.path.exists(os.path.dirname(containers)):
                with open(containers) as containers_json:
                    self.containers = Containers(json.load(containers_json))
            else:
                self.containers = Containers(json.loads(containers))
            if isinstance(protocol, dict):
                self.protocol = Protocol(protocol)
            elif os.path.exists(os.path.dirname(protocol)):
                with open(protocol) as protocol_json:
                    self.protocol = Protocol(json.load(protocol_json))
            else:
                self.protocol = Protocol(json.loads(protocol))
        except:
            print(sys.exc_info()[0]) # TODO: log this instead of print
            return
        self.head = self.protocol.head
        self.deck = self.protocol.deck

    def ensure_main_sections(self):
        errors = []
        warnings = []
        #required
        if 'head' not in self.protocol:
            errors.append('Protocol JSON must define a "head" section')
        if 'deck' not in self.protocol:
            errors.append('Protocol JSON must define a "deck" section')
        #optional, although instructions are needed to get anything done
        if 'ingredients' not in self.protocol:
            warnings.append('Protocol JSON should include an "ingredients" section for completeness')
        if 'instructions' not in self.protocol:
            warnings.append('Protocol JSON should include an "instructions" section to run')
        if 'info' not in self.protocol:
            warnings.append('Protocol JSON can include an "info" section, which is nice: "info": {"name":string,"description":string,"create-date":string,"version":string,"run-notes":string}')


        messages = {'errors': errors, 'warnings': warnings}
        return messages

    def validate(self) -> list:
        """Entry method
        """
        errors = []
        warnings = []

        info_dict = self.protocol.data.get('info',{})
        info_message = None
        if info_dict:
            info_message = json.dumps(info_dict)

        no_containers = len(list(self.deck.data.keys()))
        no_tools = len(list(self.head.data.keys()))
        instructions_list = self.protocol.data.get('instructions', [])
        no_instructions = len(instructions_list)

        main_section_errors = self.ensure_main_sections()
        if main_section_errors.get('errors'):
            message = {
                'info': info_message,
                'salient': {'no_containers':no_containers, 'no_tools':no_tools, 'no_instructions':no_instructions},
                'errors': errors,
                'warnings': warnings
            }
            return message

        deck_messages = self.validate_deck()
        head_messages = self.validate_head()
        ingredients_messages = self.validate_ingredients()
        instructions_messages = self.validate_instructions()

        warnings = sum([
            deck_messages.get('warnings'),
            head_messages.get('warnings'),
            ingredients_messages.get('warnings'),
            instructions_messages.get('warnings'),
            main_section_errors.get('warnings')
        ], [])

        errors = sum([
            deck_messages.get('errors'),
            head_messages.get('errors'),
            ingredients_messages.get('errors'),
            instructions_messages.get('errors'),
        ], [])

        message = {
            'info': info_message,
            'salient': {'no_containers':no_containers, 'no_tools':no_tools, 'no_instructions':no_instructions},
            'errors': errors,
            'warnings': warnings
        }

        return message

    def validate_head(self) -> list:
        """
        Verifies that head is properly defined.
        """
        print('validating head') # TODO: use logger here instead
        errors = []
        warnings = []
        head_data = self.protocol.data.get('head', {})

        for tool_name, tool_definition in head_data.items():
            tool = tool_definition.get('tool')
            tip_racks = tool_definition.get('tip-racks')
            trash_container = tool_definition.get('trash-container')
            multi_channel = tool_definition.get('multi-channel')
            axis = tool_definition.get('axis')
            volume = tool_definition.get('volume')
            down_plunger_speed = tool_definition.get('down-plunger-speed')
            up_plunger_speed = tool_definition.get('up-plunger-speed')
            tip_plunge = tool_definition.get('tip-plunge')
            extra_pull_volume = tool_definition.get('extra-pull-volume')
            extra_pull_delay = tool_definition.get('extra-pull-delay')
            distribute_percentage = tool_definition.get('distribute-percentage')
            points = tool_definition.get('points')
            if tool is None:
                errors.append(
                    'Head tool "{}" MUST define a "tool" attribute'
                    .format(tool_name)
                )
                continue
            if tip_racks is None:
                errors.append(
                    'Head tool "{}" MUST define a "tip-racks" attribute'
                    .format(tool_name)
                )
                continue
            if trash_container is None:
                errors.append(
                    'Head tool "{}" MUST define a "trash-container" attribute'
                    .format(tool_name)
                )
                continue
            if multi_channel is None:
                errors.append(
                    'Head tool "{}" MUST define a "multi-channel" attribute'
                    .format(tool_name)
                )
                continue
            if axis is None:
                errors.append(
                    'Head tool "{}" MUST define a "axis" attribute'
                    .format(tool_name)
                )
                continue
            if volume is None:
                errors.append(
                    'Head tool "{}" MUST define a "volume" attribute'
                    .format(tool_name)
                )
                continue
            if down_plunger_speed is None:
                errors.append(
                    'Head tool "{}" MUST define a "down-plunger-speed" attribute'
                    .format(tool_name)
                )
                continue
            if up_plunger_speed is None:
                errors.append(
                    'Head tool "{}" MUST define a "up-plunger-speed" attribute'
                    .format(tool_name)
                )
                continue
            if tip_plunge is None:
                errors.append(
                    'Head tool "{}" MUST define a "tip-plunge" attribute'
                    .format(tool_name)
                )
                continue
            if extra_pull_volume is None:
                errors.append(
                    'Head tool "{}" MUST define a "extra-pull-volume" attribute'
                    .format(tool_name)
                )
                continue
            if extra_pull_delay is None:
                errors.append(
                    'Head tool "{}" MUST define a "extra-pull-delay" attribute'
                    .format(tool_name)
                )
                continue
            if distribute_percentage is None:
                errors.append(
                    'Head tool "{}" MUST define a "distribute-percentage" attribute'
                    .format(tool_name)
                )
                continue
            if points is None:
                errors.append(
                    'Head tool "{}" MUST define a "points" attribute'
                    .format(tool_name)
                )
                continue
            # tool
            if tool != 'pipette':
                errors.append(
                    'Head tool "{}"\'s tool MUST be "pipette"'
                    .format(tool_name)
                )
            # tip-racks
            if not isinstance(tip_racks, list):
                errors.append(
                    'Head tool "{}"\'s "tip-racks" MUST be a list (hint: [ ] )'
                    .format(tool_name)
                )
            elif tip_racks is None:
                errors.append(
                    'Head tool "{}" MUST have a "tip-racks" attribute'
                    .format(tool_name)
                )
            else:
                for container in tip_racks:
                    tip_rack_container = container.get('container')
                    if tip_rack_container not in self.deck:
                        errors.append(
                            'Head tool "{}" tip-racks\' "{}" container not found in Deck'
                            .format(tool_name, tip_rack_container)
                        )
            # trash-container
            if not isinstance(trash_container, dict):
                errors.append(
                    'Head tool "{}"\'s "trash-container" MUST be a dict (hint: \{ \})'
                    .format(tool_name)
                )
            else:
                trash_container_container = trash_container.get('container')
                if trash_container_container not in self.deck:
                    errors.append(
                        'Head tool "{}"\'s "trash-container" "{}" not found in Deck'
                        .format(tool_name, trash_container_container)
                    )
            #multi-channel
            if multi_channel != True and multi_channel != False:
                errors.append(
                    'Head tool "{}"\'s "multi-channel" MUST be "true" or "false"'
                    .format(tool_name)
                )
            # axis
            if not (axis == 'a' or axis == 'b'):
                errors.append(
                    'Head tool "{}"\'s "axis" MUST be "a" or "b"'
                    .format(tool_name)
                )
            # volume
            if not isinstance(volume, (int,float)):
                errors.append(
                    'Head tool "{}"\'s "volume" MUST be an int or float'
                    .format(tool_name)
                )
            elif volume < 0.1 or volume > 10000:
                warnings.append(
                    'Head tool "{}"\'s "volume" is outside normal values'
                    .format(tool_name)
                )
            # down-plunger-speed
            if not isinstance(down_plunger_speed, (int, float)):
                errors.append(
                    'Head tool "{}"\'s "down-plunger-speed" MUST be an int or float'
                    .format(tool_name)
                )
            elif down_plunger_speed < 1 or down_plunger_speed > 900:
                warnings.append(
                    'Head tool "{}"\'s "down-plunger-speed" is outside normal values'
                    .format(tool_name)
                )
            # up_plunger_speed
            if not isinstance(up_plunger_speed, (int, float)):
                errors.append(
                    'Head tool "{}"\'s "up-plunger-speed" MUST be an int or float'
                    .format(tool_name)
                )
            elif up_plunger_speed < 1 or up_plunger_speed > 900:
                warnings.append(
                    'Head tool "{}"\'s "up-plunger-speed" is outside normal values'
                    .format(tool_name)
                )
            # tip_plunge
            if not isinstance(tip_plunge, (int, float)):
                errors.append(
                    'Head tool "{}"\'s "tip_plunge" MUST be an int or float'
                    .format(tool_name)
                )
            elif tip_plunge < 0.5 or tip_plunge > 15:
                warnings.append(
                    'Head tool "{}"\'s "tip-plunge" is outside normal values'
                    .format(tool_name)
                )
            # extra_pull_volume
            if not isinstance(extra_pull_volume, (int, float)):
                errors.append(
                    'Head tool "{}"\'s "extra-pull-volume" MUST be an int or float'
                    .format(tool_name)
                )
            elif extra_pull_volume < 0 or extra_pull_volume > 1000:
                warnings.append(
                    'Head tool "{}"\'s "extra-pull-volume" is outside normal values'
                    .format(tool_name)
                )
            # extra_pull_delay
            if not isinstance(extra_pull_delay, (int, float)):
                errors.append(
                    'Head tool "{}"\'s "extra-pull-delay" MUST be an int or float'
                    .format(tool_name)
                )
            elif extra_pull_delay < 0 or extra_pull_delay > 1000:
                warnings.append(
                    'Head tool "{}"\'s "extra-pull-delay" is outside noraml values'
                    .format(tool_name)
                )
            # distribute_percentage
            if not isinstance(distribute_percentage, float):
                errors.append(
                    'Head tool "{}"\'s "distribute-percentage" MUST be a float'
                    .format(tool_name)
                )
            elif distribute_percentage < 0.0 or distribute_percentage > 1.0:
                errors.append(
                    'Head tool "{}"\'s "distribute-percentage" MUST be between 0.0 and 1.0'
                    .format(tool_name)
                )
            # points
            if not isinstance(points, list):
                errors.append(
                    'Head tool "{}"\'s "points" MUST be a list (hint: [ ])'
                    .format(tool_name)
                )
            else:
                point_number = 0
                for point in points:
                    point_number += 1
                    f1 = point.get('f1')
                    f2 = point.get('f2')

                    if f1 is None or f2 is None:
                        errors.append(
                            'Head tool "{}"\'s "points" point number {} MUST define both an f1 and f2'
                            .append(tool_name, point_number)
                        )
                        continue
                    # f1
                    if not isinstance(f1, (int, float)):
                        errors.append(
                            'Head tool "{}"\'s "points" point number {} "f1" MUST be an int or float'
                            .format(tool_name, point_number)
                        )
                    elif f1 < 0 or f1 > 110:
                        warnings.append(
                            'Head tool "{}"\'s "points" point number {} "f1" is outside normal values'
                            .format(tool_name, point_number)
                        )
                    # f2
                    if not isinstance(f2, (int, float)):
                        errors.append(
                            'Head tool "{}"\'s "points" point number {} "f2" MUST be an int or float'
                            .format(tool_name, point_number)
                        )
                    elif f2 < 0 or f2 > 110:
                        warnings.append(
                            'Head tool "{}"\'s "points" point number {} "f2" is outside normal values'
                            .format(tool_name, point_number)
                        )

        messages = {'errors': errors, 'warnings': warnings}
        return messages

    def validate_deck(self) -> list:
        """
        Verifies that all users labwares are defined in the containers
        data
        """
        print('validating deck'); # TODO: use logger here instead
        errors = []
        warnings = []

        deck_data = self.protocol.data.get('deck', {})


        for container_name, container_definition in deck_data.items():
            labware = container_definition.get('labware')
            slot = container_definition.get('slot')

            if labware is None:
                errors.append(
                    'Deck container "{}" MUST define a "labware" attribute'
                    .format(container_name)
                )
                continue
            if slot is None:
                warnings.append(
                    'Deck container "{}" does not specify a "slot" attribute, but it is recommended'
                    .format(container_name)
                )

            if labware not in self.containers:
                errors.append(
                    'Deck container "{}"\'s labware "{}" was not found in containers data'
                    .format(container_name, labware)
                )
            else:
                if slot and slot not in self.DECK_SLOTS:
                    errors.append(
                        'Deck container "{}"\'s "slot" {} not a slot on Deck, MUST be one of {}'
                        .format(container_name, slot, self.DECK_SLOTS)
                    )
        messages = {'errors': errors, 'warnings': warnings}
        return messages

    def validate_ingredients(self) -> list:
        """
        Verifies that the ingredients section is properly defined
        """
        print('validating ingredients') # TODO: user logger here instead
        errors = []
        warnings = []

        ingredients_data = self.protocol.data.get('ingredients', {})

        if ingredients_data:
            warnings.append(
                'Ingredients has elements, but Ingredients are not yet supported'
            )

        messages = {'errors': errors, 'warnings': warnings}
        return messages


    def validate_instructions(self) -> list:
        """
        Verifies that instructions are properly defined
        """
        print('validating instructions')    # TODO: use logger here instead

        errors = []
        warnings = []

        instructions_data = self.protocol.data.get('instructions', [])

        instruction_number = 0
        for instruction in instructions_data:
            instruction_number += 1

            if not isinstance(instruction, dict):
                errors.append(
                    'Instructions should be JSON objects (hint: \{ \} ), at instruction number {}'
                    .format(instruction_number)
                )
                continue

            tool = instruction.get('tool')
            groups = instruction.get('groups')

            if tool is None or groups is None:
                errors.append(
                    'Instructions MUST specify a "tool" and a "groups" attribute, at instruction number {}'
                    .format(instruction_number)
                )
                continue

            if tool not in self.head:
                errors.append(
                    'Instructions tool "{}" not found in Head, at instruction number {}'
                    .format(tool, instruction_number)
                )
            if not isinstance(groups, list):
                errors.append(
                    'Instructions "group" must be a list (hint: [ ] ), at instruction number {}'
                    .format(instruction_number)
                )
            else:
                group_number = 0
                for group in groups:
                    group_number += 1
                    if len(group) != 1:
                        errors.append(
                            'Instructions "groups" group must have only one element, at instruction number {}, group number {}'
                            .format(instruction_number, group_number)
                        )
                    else:
                        command_name, command_list = list(group.items())[0]
                        if command_name not in self.COMMAND_TYPES:
                            errors.append(
                                'Instructions command MUST be one of {}, at instruction number {}, group number {}'
                                .format(self.COMMAND_TYPES, instruction_number, group_number)
                            )
                            continue
                        if not isinstance(command_list, list):
                            errors.append(
                                'Instructions command MUST specify a list (hint: [ ] ), at instruction number {}, group number {}, command "{}"'
                                .format(instruction_number, group_number, command_name)
                            )
                        else:
                            command_number = 0
                            for command in command_list:
                                command_number += 1
                                command_from = command.get('from', {})
                                command_to = command.get('to', {})
                                volume = command.get('volume')

                                if command_from is None or command_to is None or volume is None:
                                    errors.append(
                                        'Instructions Command MUST define "from", "to", and "volume", at instruction number {}, group number {}, command "{}", command number {}'
                                        .format(instruction_number, group_number, command_name, command_number)
                                    )
                                    continue

                                from_messages = self.validate_direction('from', command_from, instruction_number, group_number, command_name, command_number)

                                to_messages = self.validate_direction('to', command_from, instruction_number, group_number, command_name, command_number)

                                errors = sum([
                                    from_messages.get('errors'),
                                    to_messages.get('errors')
                                ],[])
                                warnings = sum([
                                    from_messages.get('warnings'),
                                    to_messages.get('warnings')
                                ],[])

                                # volume
                                if volume < 0:
                                    errors.append(
                                        'Instructions Command "volume" MUST be positive, but it is {}, at instruction number {}, group number {}, command "{}", command number {}'
                                        .format(volume, instruction_number, group_number, command_name, command_number)
                                    )
                                if volume > 5000:
                                    warnings.append(
                                        'Instructions Command "volume" {} awfully high..., at instruction number {}, group number {}, command "{}", command number {}'
                                        .format(volume, instruction_number, group_number, command_name, command_number)
                                    )

        messages = {'errors': errors, 'warnings': warnings}
        return messages




    def validate_direction(self, direction: "from or to dict",
                        command_direction,
                        instruction_number,
                        group_number,
                        command_name,
                        command_number):
        print('validating direction')   # TODO: use logger here instead
        errors = []
        warnings = []
        # direction (from or to)
        if not isinstance(command_direction, dict):
            errors.append(
                'Instructions Command "{}" MUST be an object (hint: \{ \} ), at instruction number {}, group number {}, command "{}", command number {}'
                .format(direction, instruction_number, group_number, command_name, command_number)
            )
        else:
            # required - direction attributes
            direction_container = command_direction.get('container')
            direction_location = command_direction.get('location')

            # optional - direction attributes
            tip_offset = command_direction.get('tip-offset')
            delay = command_direction.get('delay')
            touch_tip = command_direction.get('touch-tip')
            blowout = command_direction.get('blowout')
            extra_pull = command_direction.get('extra-pull')
            liquid_tracking = command_direction.get('liquid-tracking')


            if direction_container is None or direction_location is None:
                errors.append(
                    'Instructions Command "{}" Must define a "container" and "location", at instruction number {}, group number {}, command "{}", command number {}'
                    .format(direction, instruction_number, group_number, command_name, command_number)
                )
            else:
                # container -> location
                if direction_container not in self.deck:
                    errors.append(
                        'Instructions Command "{}"\'s container "{}" not found in Deck, at instruction number {}, group number {}, command "{}", command number {}'
                        .format(direction, direction_container, instruction_number, group_number, command_name, command_number)
                    )
                else:
                    # location
                    labware = self.deck.data.get(direction_container).get('labware')
                    if not self.containers.has_location(labware, direction_location):
                        errors.append(
                            'Instruction Command "{}" container "{}" location "{}" not found in "{}", at instruction number {}, group number {}, command "{}", command number {}'
                            .format(direction, direction_container, direction_location, labware, instruction_number, group_number, command_name, command_number)
                        )
                # OPTIONAL
                # tip-offset
                if tip_offset:
                    if tip_offset < -30 or tip_offset > 30:
                        warnings.append(
                            'Instruction Command "{}" "tip-offset" has an unusually large magnitude, at instructions number {}, group number {}, command "{}", command number {}'
                            .format(direction, instruction_number, group_number, command_name, command_number)
                        )
                # delay
                if delay:
                    if delay < 0:
                        errors.append(
                            'Instruction Command "{}" "delay" MUST be positive, at instruction number {}, group number {}, command "{}", command number {}'
                            .format(direction, instruction_number, group_number, command_name, command_number)
                        )

                # touch-tip
                if touch_tip:
                    if touch_tip != True and touch_tip != False:
                        errors.append(
                            'Instruction Command "{}" "touch-tip" MUST be "true" or "false", at instruction number {}, group number {}, command "{}", command number {}'
                            .format(direction, instruction_number, group_number, command_name, command_number)
                        )
                # blowout
                if blowout:
                    if blowout != True and blowout != False:
                        errors.append(
                            'Instruction Command "{}" "blowout" MUST be "true" or "false", at instruction number {}, group number {}, command "{}", command number {}'
                            .format(direction, instruction_number, group_number, command_name, command_name)
                        )
                # extra-pull
                if extra_pull:
                    if extra_pull != True and blowout != False:
                        errors.append(
                            'Instruction Command "{}" "extra-pull" MUST be "true" or "false", at instruction number {}, group number {}, command "{}", command number {}'
                            .format(direction, instruction_number, group_number, command_name, command_name)
                        )
                # liquid-tracking
                if liquid_tracking:
                    if liquid_tracking != True and liquid_tracking != False:
                        errors.append(
                            'Instruction Command "{}" "liquid-tracking" MUST be "true" or "false", at instruction number {}, group number {}, command "{}", command number {}'
                            .format(direction, instruction_number, group_number, command_name, command_name)
                        )
        messages = {'errors': errors, 'warnings': warnings}
        return messages
