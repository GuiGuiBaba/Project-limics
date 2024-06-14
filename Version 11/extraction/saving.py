import json
import os

def save_progress(path,ent_cat):
    
    json_file_path = os.path.join(path, 'progress.json')
    if os.path.isfile(json_file_path):
        with open(json_file_path, 'r', encoding='utf-8') as file:
            try:
                data = json.load(file)
            except json.JSONDecodeError:
                data = {}
    else : data = {}

    data.update(ent_cat)

    with open(json_file_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)
        
def load_progress(path):
    
    json_file_path = os.path.join(path, 'progress.json')
    progress_ent_cat = None
    
    if os.path.isfile(json_file_path):
        with open(json_file_path, 'r', encoding='utf-8') as file:
            try:
                progress_ent_cat = json.load(file)
            except (json.JSONDecodeError,FileNotFoundError):
                pass
    
    return progress_ent_cat