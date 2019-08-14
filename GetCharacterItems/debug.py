hero_object = {}
rank = 123

name = "troyel"
account = "halvar"

hero_object['rank'] = rank
hero_object['character'] = {}
hero_object['account'] = {}
hero_object['character']['name'] = name
hero_object['account']['name'] = account

if hero_object['equiped']['error'] :
    print("error")
else:
    print("no.errpr")