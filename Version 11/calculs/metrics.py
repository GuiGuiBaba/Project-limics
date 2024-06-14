import os
import re
import pandas as pd
from ipydatagrid import DataGrid, TextRenderer, Expr
from .regex import *

def calculate_location_metrics(current_entity,ent_cat,path,df,other_categories):
    """
    Retrieves and sorts words from annotated texts into matching categories, then compares whether these words match any of the existing annotations. 
    
    Parameters : 
    current_entity (string) : the current selected entity.
    ent_cat (dict) : List of all the entities paired with their categories.
    path (string) : path of the current working directory.
    df (dataframe) : Dataframe containing the annotated words, their occurrences, places and related entity.
    other_categories (list) : contains all the annotations of the current entity that could belong to another category. 
    
    Return :
    (dict) : dictionnary containing the locations of each categorized word, and whether they are true positive, false positive or false negative. 
    """
    
    location_metrics={}
    locations = {}
    location_metrics[current_entity] = []
    
    txt_files = []
    for file_name in os.listdir(path):
        if file_name.endswith(".txt"):
            txt_files.append(file_name)
            locations[file_name]=[]
    
    # 1 -  storage of places of each annotations categorised in "locations"
    ent_cat2 = [cat for cat in ent_cat[current_entity] if cat != "category?"]
    for cat in ent_cat2:
        filtre = (df['entity'] == current_entity) & (df['category'] == cat)
        for index, row in df[filtre].iterrows():
            for place in row['places']:
                name_document = place[0]+".txt"
                place_document = [place[1],place[2]]
                
                if name_document in locations:
                    locations[name_document].append(place_document)
    
        # 2 - Verification by category : TP,FP and FN
        pattern = generate_regex(eval(cat))
        for file_name in txt_files:
            with open(os.path.join(path, file_name), 'r', newline='',encoding='utf-8') as file:
                text = file.read().lower()
                for match in re.finditer(pattern, text):
                    place_start = match.start()
                    place_end = match.end()
                    motif = text[match.start():match.end()]
                    long_motif = "..."+text[max(place_start-70,0):min(place_end+70,len(text))]+"..."
                    FP = True   
                    for location in locations[file_name]: 
                        if location[0]<=place_start and place_end <= location[1]: #place found (TP)
                            locations[file_name].remove(location)
                            location_metrics[current_entity].append([cat,"TP",long_motif,file_name,[place_start,place_end]]) 
                            FP = False
                            break  
                
                    if FP : #verification in other categories, if exist, we add in 'FP'
                        df_other_categories = pd.DataFrame(other_categories,columns=["entity", "category","text","file", "places"])
                        filtre2 = (df_other_categories['entity'] == current_entity) & (df_other_categories['category'] == cat) & (df_other_categories['file'] == file_name)
                        add_to_FP = True
                        for index, row in df_other_categories[filtre2].iterrows():
                            if row['places'][0]<=place_start and place_end <= row['places'][1]:
                                add_to_FP = False
                                break
                        
                        if add_to_FP: #location not found (FP)
                            location_metrics[current_entity].append([cat,"FP",long_motif,file_name,[place_start,place_end]]) 
                        
            if len(locations[file_name])!=0:#locations left (FN)
                for place in locations[file_name]:
                    location_metrics[current_entity].append([cat,"FN",motif,file_name,place]) 
                locations[file_name]=[] 
                
    return location_metrics

def calculate_df_metrics(df_location_metrics):
    """
    Calculate the precision and coverage score in each category. 
    
    Parameters : 
    df_location_metrics (dataframe) : contains the locations of each categorized word, and whether they are true positive, false positive or false negative.. 
    
    Return :
    (dataframe) : dataframe containing the precision and coverage score in each category. 
    """
    metrics = []
    for cat in df_location_metrics['category'].unique():
        TP = df_location_metrics[(df_location_metrics['category'] == cat) & (df_location_metrics['result'] == "TP")].shape[0]
        FP = df_location_metrics[(df_location_metrics['category'] == cat) & (df_location_metrics['result'] == "FP")].shape[0]
        FN = df_location_metrics[(df_location_metrics['category'] == cat) & (df_location_metrics['result'] == "FN")].shape[0]
        precision = 0
        if TP+FP !=0 :
            precision = round(TP/(TP+FP),2)
        coverage = 0   
        if TP+FN !=0 :
            coverage = round(TP/(TP+FN),2)
        
        metrics.append([cat,TP,FP,FN,precision,coverage])
    df_metrics = pd.DataFrame(metrics,columns=["category", "TP","FP","FN", "precision","coverage"])
    df_metrics["precision"] = df_metrics["precision"].round(2)
    df_metrics["coverage"] = df_metrics["coverage"].round(2)
    return df_metrics

def text_color(cell):
    if cell.value =="FN":
        return "#ff1414" 
    else : 
        return "#ffffff"
        
def background_color(cell):
    if cell.value in ("TP" ,"FN"):
        return "#006400"
    else:
        return "#500000"

def create_grid_metrics_locations(location_metrics,current_entity):
    """
    Create a grid with renderers from the location metrics dictionnary. 
    
    Parameters (dict) : dictionnary containing the locations of each categorized word, and whether they are true positive, false positive or false negative.
    current_entity (string) : the current selected entity.
    
    Return :
    (datagrid) : datagrid containing the locations of each categorized word, and whether they are true positive, false positive or false negative 
    """
    
    df_location_metrics = pd.DataFrame(location_metrics[current_entity],columns=["category", "result","text","file", "places"])
    dg_location_metrics = DataGrid(df_location_metrics,column_widths={"category":200,"result":80,"text":650,"file":100,"places":80},layout={"height":"350px"},base_row_size=25)    
    renderers = {
        "result": TextRenderer(
            text_color=Expr(text_color),
            background_color=Expr(background_color), 
            horizontal_alignment="center"),
        "text": TextRenderer(
            horizontal_alignment="left")
    }
    dg_location_metrics.renderers = renderers
    return dg_location_metrics

