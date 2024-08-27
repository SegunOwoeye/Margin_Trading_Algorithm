from json import load

def run():
    with open("0-Settings/config.json","r") as f:
        config = load(f)

    return config

#print(run())