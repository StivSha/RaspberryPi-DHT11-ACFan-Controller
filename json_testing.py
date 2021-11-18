import json

hum = 43
temp = 3

data_set = {"temperature": temp, "humidity": hum}


json_dump = json.dumps(data_set)


print(json_dump)
