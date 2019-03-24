def json_to_packed(json_team):
    def from_json(j):
        return "{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{},{},{}".format(
            j['name'],
            j['species'],
            j['item'],
            j['ability'],
            ",".join(j['moves']),
            j.get('nature', ''),
            ','.join(str(x) for x in j['evs'].values()),
            j.get('gender', ''),
            j.get('ivs', ''),
            j.get('shiny', ''),
            j['level'],
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
        j['ivs'] = items[8]
        j['shiny'] = items[9]
        j['level'] = items[10]
        final = items[11].split(',')
        if final[0]:
            j['happiness'] = final[0]
            j['pokeball'] = final[1]
            j['hiddenpowertype'] = final[2]
        return j

    json_team = []
    for pkmn in packed_team.split(']'):
        json_team.append(from_string(pkmn))
    return json_team
