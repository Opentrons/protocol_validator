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
        #print('Head initiated')
        #print('head: ',json.dumps(self.data, indent=1))

    def __contains__(self, key):
        return key in list(self.data.keys())


class Deck(object):
    def __init__(self, json_data: dict):
        self.data = json_data
        #print('Deck initiated')
        #print('deck: ',json.dumps(self.data, indent=1))

    def __contains__(self, key):
        return key in list(self.data.keys())


class Protocol(object):
    def __init__(self, json_data: dict):
        self.data = json_data
        #print('inside Protocol init')
        #print('protocol data: ', json.dumps(self.data, indent=1))
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
            # 1. check if dictionary to load object directly
            if isinstance(containers, dict):
                self.containers = Containers(containers)
            # 2. otherwise, check if filepath to load from file
            elif os.path.exists(os.path.dirname(containers)):
                with open(containers) as containers_json:
                    self.containers = Containers(json.load(containers_json))
            # 3. otherwise, try loading directly from data entered as string
            else:
                self.containers = Containers(json.loads(containers))

            # 1. check if dictionary to load object directly
            if isinstance(protocol, dict):
                print('protocol is dict')
                self.protocol = Protocol(protocol)
            # 2. otherwise, check if filepath to load from file
            elif os.path.exists(os.path.dirname(protocol)):
                print('protocol is json file')
                with open(protocol) as protocol_json:
                    self.protocol = Protocol(json.load(protocol_json))
            # 3. otherwise, try loading directly from data entered as string
            else:
                print('protocol is string')
                self.protocol = Protocol(json.loads(protocol))
        except:
            print(sys.exc_info()[0]) # TODO: log this instead of print
            return
        #print('inside JSONProtocolValidator init')
        self.head = self.protocol.head
        self.deck = self.protocol.deck
        #print('head data: ', json.dumps(self.head.data))
        #print('deck data: ', json.dumps(self.deck.data))


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
        messages = {
            'info': '',
            'salient': '',
            'errors': errors,
            'warnings': warnings
        }

        main_section_errors = self.ensure_main_sections()
        if main_section_errors.get('errors'):
            messages['errors'].extend(main_section_errors.get('errors'))
            return messages

        info_dict = self.protocol.data.get('info',{})
        info_message = None
        if info_dict:
            info_message = json.dumps(info_dict)

        no_containers = len(list(self.deck.data.keys()))
        no_tools = len(list(self.head.data.keys()))
        instructions_list = self.protocol.data.get('instructions', [])
        no_instructions = len(instructions_list)

        head_data = self.protocol.data.get('head', {})
        deck_data = self.protocol.data.get('deck', {})
        ingredients_data = self.protocol.data.get('ingredients', {})


        deck_messages = self.validate_deck(deck_data)
        head_messages = self.validate_head(head_data)
        ingredients_messages = self.validate_ingredients(ingredients_data)
        instructions_messages = self.validate_instructions(instructions_list)

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


    def validate_head(self, head_data) -> dict:
        """
        Verifies that head is properly defined.
        """
        print('validating head') # TODO: use logger here instead
        errors = []
        warnings = []

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

            tool_belt = [
                ('tool',tool),
                ('tip-racks',tip_racks),
                ('trash-container',trash_container),
                ('multi-channel',multi_channel),
                ('axis',axis),
                ('volume',volume),
                ('down-plunger-speed',down_plunger_speed),
                ('up-plunger-speed',up_plunger_speed),
                ('tip-plunge',tip_plunge),
                ('extra-pull-volume',extra_pull_volume),
                ('extra_pull_delay',extra_pull_delay),
                ('distribute-percentage',distribute_percentage),
                ('points',points)
            ]

            for tool_key, tool_value in tool_belt:
                if tool_value is None:
                    errors.append(
                        'Head tool "{}" MUST define a "{}"'
                        .format(tool_name, tool_key)
                    )

            # tool
            if tool != 'pipette':
                errors.append(
                    'Head tool "{}"\'s tool MUST be "pipette"'
                    .format(tool_name)
                )
            # tip-racks
            if not isinstance(tip_racks, list):
                errors.append(
                    'Head tool "{}"\'s "tip-racks" MUST be a JSON array (hint: [ ] )'
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
                    'Head tool "{}"\'s "points" MUST be a JSON array (hint: [ ])'
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


    def validate_deck(self, deck_data) -> dict:
        """
        Verifies that all users labwares are defined in the containers
        data
        """
        print('validating deck'); # TODO: use logger here instead
        errors = []
        warnings = []

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


    def validate_ingredients(self, ingredients_data) -> list:
        """
        Verifies that the ingredients section is properly defined
        """
        print('validating ingredients') # TODO: user logger here instead
        errors = []
        warnings = []

        if ingredients_data:
            warnings.append(
                'Ingredients has elements, but Ingredients are not yet supported'
            )

        messages = {'errors': errors, 'warnings': warnings}
        return messages


# MAJOR SECTION
#
#   INSTRUCTIONS
#
    def validate_instructions(self, instructions_data) -> dict:
        """
        Verifies that instructions are properly defined
        """
        print('validating instructions')    # TODO: use logger here instead

        errors = []
        warnings = []

        instruction_number = 0
        for instruction in instructions_data:
            instruction_number += 1
            instruction_message = self.validate_instruction(instruction, instruction_number)
            errors.extend(instruction_message.get('errors'))
            warnings.extend(instruction_message.get('warnings'))

        messages = {'errors': errors, 'warnings': warnings}
        return messages

# INSTRUCTIONS -> Instruction
    def validate_instruction(self, instruction, instruction_number) -> dict:

        errors = []
        warnings = []

        if not isinstance(instruction, dict):
            errors.append(
                'Instructions should be JSON objects (hint: \{ \} ), at instruction number {}'
                .format(instruction_number)
            )
        else:
            tool = instruction.get('tool')
            groups = instruction.get('groups')

            if tool is None or groups is None:
                errors.append(
                    'Instructions MUST specify a "tool" and a "groups" attribute, at instruction number {}'
                    .format(instruction_number)
                )
            else:
                if tool not in self.head:
                    errors.append(
                        'Instructions tool "{}" not found in Head, at instruction number {}'
                        .format(tool, instruction_number)
                    )
            if not isinstance(groups, list):
                errors.append(
                    'Instructions "group" must be a JSON array (hint: [ ] ), at instruction number {}'
                    .format(instruction_number)
                )
            else:
                group_number = 0
                for group in groups:
                    group_number +=1
                    group_messages = self.validate_group(group, instruction_number, group_number)
                    errors.extend(group_messages.get('errors'))
                    warnings.extend(group_messages.get('warnings'))

        messages = {'errors': errors, 'warnings': warnings}
        return messages

# INSTRUCTIONS -> Instruction -> Group
    def validate_group(self, group, instruction_number, group_number) -> dict:
        errors = []
        warnings = []

        if len(group) != 1:
            errors.append(
                'Instructions "groups" group must have only one element, at instruction number {}, group number {}'
                .format(instruction_number, group_number)
            )
        else:
            command_name, command_value = list(group.items())[0]
            # Originally written for Transfer
            # Transfer -> [{to:{},from:{},volume:int,float}]
            # Distribute -> {from:{},[to's]}
            # Consolidate -> {to:{},[from's]}
            # Mix -> [{mix}]
            if command_name == self.COMMAND_TYPES[0]: # Transfer
                command_messages = self.validate_transfer(command_value, instruction_number, group_number)
            elif command_name == self.COMMAND_TYPES[1]: # Distribute
                command_messages = self.validate_dist_cons(command_value, instruction_number, group_number)
            elif command_name == self.COMMAND_TYPES[2]: # Consolidate
                command_messages = self.validate_dist_cons(command_value, instruction_number, group_number, False)
            elif command_name == self.COMMAND_TYPES[3]: # Mix
                command_messages = self.validate_mix(command_value, instruction_number, group_number)
            else:
                errors.append(
                    'Instructions command MUST be one of {}, at instruction number {}, group number {}'
                    .format(self.COMMAND_TYPES, instruction_number, group_number)
                )


            errors.extend(command_messages.get('errors'))
            warnings.extend(command_messages.get('warnings'))

        messages = {'errors': errors, 'warnings': warnings}
        return messages


    def validate_transfer(self, command_value, instruction_number, group_number) -> dict:
        errors = []
        warnings = []
        if not isinstance(command_value, list):
            errors.append(
                'Instructions Transfer MUST specify a JSON array (hint: [ ] ), at instruction number {}, group number {}'
                .format(instruction_number, group_number)
            )
        else:
            command_number = 0
            for command in command_value:
                command_number += 1
                command_from = command.get('from', {})
                command_to = command.get('to', {})
                volume = command.get('volume')

                if command_from is None or command_to is None or volume is None:
                    errors.append(
                        'Instructions Transfer MUST define "from" and "to" JSON objects, and "volume", at instruction number {}, group number {}, command number {}'
                        .format(instruction_number, group_number, command_number)
                    )
                else:
                    from_messages = self.validate_direction('from', command_from, instruction_number, group_number, 'Transfer', command_number)
                    to_messages = self.validate_direction('to', command_from, instruction_number, group_number, 'Transfer', command_number)

                    errors.extend(sum([
                        from_messages.get('errors'),
                        to_messages.get('errors')
                    ],[]))
                    warnings.extend(sum([
                        from_messages.get('warnings'),
                        to_messages.get('warnings')
                    ],[]))

                    # volume
                    if volume < 0:
                        errors.append(
                            'Instructions Transfer "volume" MUST be positive, but it is {}, at instruction number {}, group number {}, command number {}'
                            .format(volume, instruction_number, group_number, command_number)
                        )
                    if volume > 5000:
                        warnings.append(
                            'Instructions Transfer "volume" {} is  awfully high..., at instruction number {}, group number {}, command number {}'
                            .format(volume, instruction_number, group_number, command_number)
                        )

        messages = {'errors': errors, 'warnings': warnings}
        return messages


    def validate_dist_cons(self, command_value, instruction_number, group_number, dist_or_cons=True) -> dict:
        errors = []
        warnings = []
        dist_cons = 'Distribute'
        single_label = 'from'
        list_label = 'to'
        if dist_or_cons == False:
            dist_cons = 'Consolidate'
            single_label = 'to'
            list_label = 'from'

        if not isinstance(command_value, dict):
            errors.append(
                'Instructions {} MUST specify a JSON object (hint: {{}} ), at instruction number {}, group number {}'
                .format(dist_cons, instruction_number, group_number)
            )
        else:
            if dist_or_cons:
                direction_list = command_value.get('to')
                single_direction = command_value.get('from')
            else:
                direction_list = command_value.get('from')
                single_direction = command_value.get('to')
            blowout = command_value.get('blowout')

            if direction_list is None or single_direction is None:
                errors.append(
                    'Instructions {} MUST define "from" and "to" attributes, at instruction_number {}, group_number {}'
                    .format(dist_cons, instruction_number, group_number)
                )
            else:
                # Single Direction
                if not isinstance(single_direction, dict):
                    errors.append(
                        'Instructions {} "{}" must be a JSON object (hint: {{ }} ), at instruction number {}, group_number{}'
                        .format(dist_cons, single_label, instruction_number, group_number)
                    )
                else:
                    direction_message = self.validate_direction(single_label, single_direction, instruction_number, group_number, dist_cons, 'n/a')
                    errors.extend(direction_message.get('errors'))
                    warnings.extend(direction_message.get('warnings'))
                # Direction List
                if not isinstance(direction_list, list):
                    errors.append(
                        'Instructions {} "{}" must be a JSON array (hint: [ ] ), at instruction number {}, group_number{}'
                        .format(dist_cons, list_label, instruction_number, group_number)
                    )
                else:
                    direction_number = 0
                    for direction in direction_list:
                        direction_number += 1
                        direction_messages = self.validate_direction(list_label, direction, instruction_number, group_number, dist_cons, direction_number)
                        errors.extend(direction_messages.get('errors'))
                        warnings.extend(direction_messages.get('warnings'))

                if blowout != True and blowout != False:
                    errors.append(
                        'Instruction {} "blowout" MUST be "true" or "false", at instruction number {}, group number {}'
                        .format(dist_const, instruction_number, group_number)
                    )
        messages = {'errors': errors, 'warnings': warnings}
        return messages


    def validate_mix(self, mix_list, instruction_number, group_number) -> dict:
        errors = []
        warnings = []
        if not isinstance(mix_list, list):
            errors.append(
                'Instructions Mix MUST specify a JSON array (hint: [ ] ), at instruction number {}, group number {}, command "{}"'
                .format(instruction_number, group_number, 'Mix')
            )
        else:
            mix_number = 0
            for mix in mix_list:
                mix_number += 1
                mix_messages = self.validate_direction('mix', mix, instruction_number, group_number, 'mix', mix_number)
                errors.extend(mix_messages.get('errors'))
                warnings.extend(mix_messages.get('warnings'))
        messages = {'errors': errors, 'warnings': warnings}
        return messages

# INSTRUCTIONS -> Instruction -> Group -> Command Direction
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
                'Instructions {} "{}" MUST be an object (hint: \{ \} ), at instruction number {}, group number {}, command number {}'
                .format(command_name, direction,instruction_number, group_number, command_number)
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
            repetitions = None
            if direction == 'mix':
                repetitions = command_direction.get('repetitions')


            if direction_container is None or direction_location is None:
                errors.append(
                    'Instructions {} "{}" Must define a "container" and "location", at instruction number {}, group number {}, command number {}'
                    .format(command_name, direction, instruction_number, group_number, command_number)
                )
            else:
                # container -> location
                if direction_container not in self.deck:
                    print('DECK: ', list(self.deck.data.keys()))
                    errors.append(
                        'Instructions {} "{}"\'s container "{}" not found in Deck, at instruction number {}, group number {}, command number {}'
                        .format(command_name, direction, direction_container, instruction_number, group_number, command_number)
                    )
                else:
                    # location
                    labware = self.deck.data.get(direction_container).get('labware')
                    if not self.containers.has_location(labware, direction_location):
                        errors.append(
                            'Instruction {} "{}" container "{}" location "{}" not found in "{}", at instruction number {}, group number {}, command number {}'
                            .format(command_name, direction, direction_container, labware,instruction_number, group_number, command_number)
                        )
                # OPTIONAL
                # tip-offset
                if tip_offset:
                    if tip_offset < -30 or tip_offset > 30:
                        warnings.append(
                            'Instruction {} "{}" "tip-offset" has an unusually large magnitude, at instructions number {}, group number {}, command number {}'
                            .format(command_name, direction, instruction_number, group_number, command_number)
                        )
                # delay
                if delay:
                    if delay < 0:
                        errors.append(
                            'Instruction {} "{}" "delay" MUST be positive, at instruction number {}, group number {}, command number {}'
                            .format(command_name, direction, instruction_number, group_number, command_number)
                        )

                # touch-tip
                if touch_tip:
                    if touch_tip != True and touch_tip != False:
                        errors.append(
                            'Instruction {} "{}" "touch-tip" MUST be "true" or "false", at instruction number {}, group number {}, command number {}'
                            .format(command_name, direction, instruction_number, group_number, command_number)
                        )
                # blowout
                if blowout:
                    if blowout != True and blowout != False:
                        errors.append(
                            'Instruction {} "{}" "blowout" MUST be "true" or "false", at instruction number {}, group number {}, command number {}'
                            .format(command_name, direction, instruction_number, group_number, command_number)
                        )
                # extra-pull
                if extra_pull:
                    if extra_pull != True and blowout != False:
                        errors.append(
                            'Instruction {} "{}" "extra-pull" MUST be "true" or "false", at instruction number {}, group number {}, command number {}'
                            .format(command_name, direction, instruction_number, group_number, command_number)
                        )
                # liquid-tracking
                if liquid_tracking:
                    if liquid_tracking != True and liquid_tracking != False:
                        errors.append(
                            'Instruction {} "{}" "liquid-tracking" MUST be "true" or "false", at instruction number {}, group number {}, command number {}'
                            .format(command_name, direction, instruction_number, group_number, command_number)
                        )
                # mix->repetitions
                if direction == 'mix':
                    if repetitions is None:
                        warnings.append(
                            'Instruction {} "{}" "repetitions" could be set but is not, at instruction number {}, group number {}, command number {}'
                            .format(command_name, direction, instruction_number, group_number, command_number)
                        )


        messages = {'errors': errors, 'warnings': warnings}
        return messages
