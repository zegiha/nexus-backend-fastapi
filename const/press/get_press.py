import json

def get_press():
    with open('const/press/press.json', 'r', encoding='utf-8') as f:
        press_res = json.load(f)
        return press_res