def is_min_ratio_toilets_to_people_met(ratio):
    ratio_parts = ratio.split('/')
    toilets = int(ratio_parts[0].replace('t', ''))
    people = int(ratio_parts[1].replace('p', ''))
    if toilets/people >= 1/20:
        return True
    else:
        return False

print(is_min_ratio_toilets_to_people_met('1t/37p'))
print(is_min_ratio_toilets_to_people_met('1t/12p'))

def is_population_disabled(disabled, pop):
    if disabled/pop >= 0.10:
        return True
    else:
        return False

print(is_population_disabled(0, 32))
print(is_population_disabled(52, 392))

def is_gp_religious_or_academic(gp):
    aca_rel = set(['Mosque', 'Church', 'School', 'Institute', 'Education', 'Faculty'])
    gp_words = set(gp.split())
    intersection_gp_aca_rel = gp_words.intersection(aca_rel)
    if intersection_gp_aca_rel:
        return True
    return False

    """
    #BETTER CODING
    words = ['Mosque', 'Church', 'School', 'Institute', 'Education', 'Faculty']
    return any(word in gp for word in words)
    
    # BAD CODING
    if 'Mosque' in gp:
        return True
    elif 'Church' in gp:
        return True
    elif 'School' in gp:
        return True
    elif 'Institute' in gp:
        return True
    elif 'Education' in gp:
        return True
    elif 'Faculty' in gp:
        return True
    else:
        return False
    """

print(is_gp_religious_or_academic('Faculty Of Earth Sciences and Mining'))
print(is_gp_religious_or_academic('Almorada Church'))
print(is_gp_religious_or_academic('Health Insulation Building'))

def get_sanitation_priority(ratio, disabled, pop, gp):
    if not is_min_ratio_toilets_to_people_met(ratio) and is_population_disabled(disabled, pop) and is_gp_religious_or_academic(gp):
        return 'High Priority'
    elif is_min_ratio_toilets_to_people_met(ratio) and not is_population_disabled(disabled, pop) and not is_gp_religious_or_academic(gp):
        return 'Low Priority'
    else:
        return 'Medium Priority'

print(get_sanitation_priority(ratio='1t/49p', disabled=52, pop=392, gp='Faculty - Students Dwelling'))
print(get_sanitation_priority(ratio='1t/29p', disabled=0, pop=178, gp='Mohamed Ali Abbas Secondary School For Girls'))
print(get_sanitation_priority(ratio='1t/17p', disabled=0, pop=52, gp='Alsalam Old Mosque'))
print(get_sanitation_priority(ratio='1t/6p', disabled=0, pop=12, gp='Nile Club'))
print(get_sanitation_priority(ratio='1t/395p', disabled=0, pop=1580, gp='(Almuntazah)'))