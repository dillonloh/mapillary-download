import requests
import os
import shutil

url = "https://graph.mapillary.com/images?access_token=MLY|9877462198983833|6f0fa2ae34c06cd69d64c64cbdf57e29&fields=thumb_original_url,computed_geometry,captured_at,computed_compass_angle,creator&bbox=101.04811,4.58693,101.09455,4.64234"

def get_data():
    response = requests.get(url)
    if response.status_code != 200:
        print("ERROR FUCK")
        exit(0)

    data = response.json()['data']

    names = {}

    for i, entry in enumerate(data):
        print(f'reading {i}/{len(data)} entries')
        # id = entry['creator']['id']
        name = entry['creator']['username']
        if names.get(name, None) is None:
            names[name] = entry['thumb_original_url']
        
        else:
            pass
    
    shutil.rmtree('images', ignore_errors=True)
    os.makedirs('images', exist_ok=True)

    for name, sample in names.items():
        print(f'{name}: {sample}')
        image = requests.get(sample)
        if image.status_code != 200:
            print(f"ERROR: {name}")
            continue
        with open(f'images/{name}.jpg', 'wb') as f:
            f.write(image.content)

get_data()