from showdown.engine.helpers import normalize_name


def json_to_packed(json_team):
    def from_json(j):
        return "{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{},{},{}".format(
            j['name'],
            j.get('species', ""),
            j['item'],
            j['ability'],
            ",".join(j['moves']),
            j.get('nature', ''),
            ','.join(str(x) for x in j['evs'].values()),
            j.get('gender', ''),
            ','.join(str(x) for x in j.get('ivs', {}).values()),
            j.get('shiny', ''),
            j.get('level', ''),
            j.get('happiness', ''),
            j.get('pokeball', ''),
            j.get('hiddenpowertype', '')
        )

    packed_team_string = "]".join(
        (from_json(p) for p in json_team)
    )
    return packed_team_string


def packed_to_json(packed_team):
    def from_string(s):
        # NICKNAME|SPECIES|ITEM|ABILITY|MOVES|NATURE|EVS|GENDER|IVS|SHINY|LEVEL|HAPPINESS,POKEBALL,HIDDENPOWERTYPE
        j = {}
        items = s.split('|')
        j['name'] = items[0]
        j['species'] = items[1]
        j['item'] = items[2]
        j['ability'] = items[3]
        j['moves'] = items[4].split(',')
        j['nature'] = items[5]
        j['evs'] = dict()
        evs = items[6].split(',')
        j['evs']['hp'] = evs[0]
        j['evs']['atk'] = evs[1]
        j['evs']['def'] = evs[2]
        j['evs']['spa'] = evs[3]
        j['evs']['spd'] = evs[4]
        j['evs']['spe'] = evs[5]
        j['gender'] = items[7]
        j['ivs'] = dict()
        ivs = items[8].split(',')
        if len(ivs) == 6:
            j['ivs']['hp'] = ivs[0]
            j['ivs']['atk'] = ivs[1]
            j['ivs']['def'] = ivs[2]
            j['ivs']['spa'] = ivs[3]
            j['ivs']['spd'] = ivs[4]
            j['ivs']['spe'] = ivs[5]
        j['shiny'] = items[9]
        j['level'] = items[10]
        final = items[11].split(',')
        if len(final) == 3:
            j['happiness'] = final[0]
            j['pokeball'] = final[1]
            j['hiddenpowertype'] = final[2]
        return j

    json_team = []
    for pkmn in packed_team.split(']'):
        json_team.append(from_string(pkmn))
    return json_team


def single_pokemon_export_to_dict(pkmn_export_string):
    def get_species(s):
        if '(' in s and ')' in s:
            species = s[s.find("(")+1:s.find(")")]
            return species
        return None

    pkmn_dict = {
        "name": "",
        "species": "",
        "level": "",
        "gender": "",
        "item": "",
        "ability": "",
        "moves": [],
        "nature": "",
        "evs": {
            "hp": "",
            "atk": "",
            "def": "",
            "spa": "",
            "spd": "",
            "spe": "",
        },
    }
    pkmn_info = pkmn_export_string.split('\n')
    name = pkmn_info[0].split('@')[0]
    if "(M)" in name:
        pkmn_dict["gender"] = "M"
        name = name.replace('(M)', '')
    if "(F)" in name:
        pkmn_dict["gender"] = "F"
        name = name.replace('(F)', '')
    species = get_species(name)
    if species:
        pkmn_dict["species"] = normalize_name(species)
        pkmn_dict["name"] = name.split('(')[0].strip()
    else:
        pkmn_dict["name"] = normalize_name(name.strip())
    if '@' in pkmn_info[0]:
        pkmn_dict["item"] = normalize_name(pkmn_info[0].split('@')[1])
    for line in map(str.strip, pkmn_info[1:]):
        if line.startswith('Ability: '):
            pkmn_dict["ability"] = normalize_name(line.split('Ability: ')[-1])
        elif line.startswith('Level: '):
            pkmn_dict["level"] = normalize_name(line.split('Level: ')[-1])
        elif line.startswith('EVs: '):
            evs = line.split('EVs: ')[-1]
            for ev in evs.split('/'):
                ev = ev.strip()
                amount = normalize_name(ev.split(' ')[0])
                stat = normalize_name(ev.split(' ')[1])
                pkmn_dict['evs'][stat] = amount
        elif line.endswith('Nature'):
            pkmn_dict["nature"] = normalize_name(line.split('Nature')[0])
        elif line.startswith('-'):
            pkmn_dict["moves"].append(normalize_name(line[1:]))
    return pkmn_dict


def export_to_packed(export_string):
    team_dict = list()
    team_members = export_string.split('\n\n')
    for pkmn in filter(None, team_members):
        pkmn_dict = single_pokemon_export_to_dict(pkmn)
        team_dict.append(pkmn_dict)

    return json_to_packed(team_dict)
