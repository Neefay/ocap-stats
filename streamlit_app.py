import json
import math
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import streamlit as st


def read_file(path):
    with open(path, 'r') as f:
        return json.load(f)


def calc_euclidian_distance(positions):
    total_movement = 0
    for i in range(1, len(positions)):
        pos_vec = positions[i][0]
        pos_vec2 = positions[i - 1][0]

        cX, cY, cZ = pos_vec
        pX, pY, pZ = pos_vec2

        dx = cX - pX
        dy = cY - pY
        dz = cZ - pZ

        total_movement += math.sqrt(dx * dx + dy * dy + dz * dz)

    return total_movement


def build_entity_list(data, key="id"):
    entity_dict = {}
    for entity in data['entities']:
        entityKey = entity[key]
        entity_dict[entityKey] = {
            'id': entity.get('id'),
            'name': entity.get('name'),
            'isPlayer': bool(entity.get('isPlayer')),
            'side': entity.get('side'),
            'type': entity.get('type'),
            'totalMovement': round(calc_euclidian_distance(entity.get('positions', []))),
            'shotsFired': len(entity.get('framesFired', []))
        }
    return entity_dict


def parse_events(data):
    return [
        {
            'eventType': eventType,
            'victim': victim,
            'source': killerInfo[0] if killerInfo else None,
            'distance': distance
        } 
        for event in data['events'] 
        if len(event) >= 5 and (eventType := event[1]) in ["hit", "killed"]
        and (victim := event[2]) is not None
        and (killerInfo := event[3]) is not None
        and (distance := event[4]) is not None
    ]


def build_event_dict(events):
    event_dict = {}
    for event in events:
        eventType, victim, source, distance = event.values()

        event_dict.setdefault(source, {}).setdefault(eventType, []).append({
            'victim': victim,
            'distance': distance
        })
    return event_dict


def merge_events(event_dict, entity_dict):
    merged_dict = {
        'ai': [],
        'player': []
    }
    for key in event_dict.keys():
        events = event_dict[key]
        entity = entity_dict.get(key)
        
        if entity is None:
            continue

        ai_player_key = 'player' if entity.get('isPlayer') else 'ai'
        entity_hits = len(events.get('hit', []))
        accuracy_calc = (entity_hits / entity.get('shotsFired', 0)) * 100 if entity.get('shotsFired', 0) > 0 else 0

        average_hit_distance = sum(hit.get('distance', 0) for hit in events.get('hit', [])) / max(len(events.get('hit', [])), 1)

        merged_dict[ai_player_key].append({
            **entity,
            'totalMovement': int(entity.get('totalMovement', 0)),
            'shotsFired': int(entity.get('shotsFired', 0)),
            'hits': int(entity_hits),
            'avgHitDistance': int(round(average_hit_distance)),
            'kills': int(len(events.get('killed', []))),
            'accuracy': min(int(round(accuracy_calc)), 100),
            **events,
        })
    return merged_dict

def process_data(data):
    data = json.load(data)
    entity_dict_id = build_entity_list(data)
    events = parse_events(data)
    event_dict = build_event_dict(events)
    
    merged_events_dict = merge_events(event_dict, entity_dict_id)
    
    mission_meta = {
        'name': data['missionName'],
        'author': data['missionAuthor'],
        'worldName': data['worldName'],
        'time': datetime.fromisoformat(data['times'][0]['systemTimeUTC']).strftime("%m/%d/%Y, %H:%M:%S"),
    }
    
    output_data = {
        'stats': merged_events_dict,
        'mission': mission_meta,
    }
    return output_data

def plot_data(output_data):
    ai_stats = output_data["stats"]["ai"]
    
    mission = output_data["mission"]
    
    df = pd.DataFrame(ai_stats)
    
    # Set a color palette
    sns.set_palette('Set3')
    
    fig, axs = plt.subplots(3, 4, figsize=(18, 20))
    
    fig.suptitle(
        f"AI Eval - {mission['name']} ({mission['worldName']}) by {mission['author']} @ {mission['time']}", fontsize=27, y=0.9)
    
    # Histogram for 'totalMovement'
    sns.histplot(df['totalMovement'], bins=20, ax=axs[0, 0])
    axs[0, 0].set_title('Total Movement (meters)')
    
    # Histogram for 'shotsFired'
    sns.histplot(df['shotsFired'], bins=20, ax=axs[1, 0])
    axs[1, 0].set_title('Shots Fired')
    
    # Histogram for 'hits'
    sns.histplot(df['hits'], bins=20, ax=axs[2, 0])
    axs[2, 0].set_title('Hits')
    
    # Histogram for 'avgHitDistance'
    sns.histplot(df['avgHitDistance'], bins=20, ax=axs[0, 1])
    axs[0, 1].set_title('Average Hit Distance')
    
    # Histogram for 'kills'
    sns.histplot(df['kills'], bins=20, ax=axs[1, 1])
    axs[1, 1].set_title('Kills')
    
    # Histogram for 'accuracy'
    sns.histplot(df['accuracy'], bins=20, ax=axs[2, 1])
    axs[2, 1].set_title('Accuracy')
    
    # Scatter plot to understand the relationship between accuracy and mobility
    sns.scatterplot(x='accuracy', y='totalMovement', data=df, ax=axs[0, 2])
    axs[0, 2].set_title('Accuracy and Mobility')
    
    # Scatter plot to check if units with fewer shots are more accurate
    sns.scatterplot(x='shotsFired', y='accuracy', data=df, ax=axs[1, 2])
    axs[1, 2].set_title('Number of Shots Fired and Accuracy')
    
    # Scatter plot of total movement vs average hit distance
    sns.scatterplot(x='totalMovement', y='avgHitDistance', data=df, ax=axs[0, 3])
    axs[0, 3].set_title('Total Movement vs Average Hit Distance')
    
    # Scatter plot of shots fired vs kills
    sns.scatterplot(x='shotsFired', y='kills', data=df, ax=axs[1, 3])
    axs[1, 3].set_title('Shots Fired vs Kills')
    
    # Scatter plot of accuracy vs average hit distance
    sns.scatterplot(x='accuracy', y='avgHitDistance', data=df, ax=axs[2, 2])
    axs[2, 2].set_title('Accuracy vs Average Hit Distance')
    
    
    plt.subplots_adjust(left=0.1,
                        bottom=0.1,
                        right=0.9,
                        top=0.85,
                        wspace=0.5,
                        hspace=0.3)
    
    # plt.show()
    st.pyplot(plt.gcf())

def app():
    st.title('OCAP AI Evaluator')

    uploaded_file = st.file_uploader("Choose an OCAP JSON file", type="json")
    if uploaded_file is not None:
        data = process_data(uploaded_file)
        plot_data(data)
        # st.json(data)

if __name__ == "__main__":
    app()
