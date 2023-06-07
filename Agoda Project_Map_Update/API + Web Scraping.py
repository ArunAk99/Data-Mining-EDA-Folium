#!/usr/bin/env python
# coding: utf-8

# In[29]:


def maps_plot():
    import folium
    from tqdm import tqdm
    import googlemaps
    import pandas as pd
    import os
    import base64
    import warnings
    from progressbar import ProgressBar
    warnings.filterwarnings("ignore")
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', None)
    pd.set_option("max_colwidth", None)

    location_list = pd.read_csv(input('Enter the csv location:').replace('"',''))
    api_key = 'AIzaSyB61NXowzufZRSL6G5oSPDXJ92rU2h6Ow0'
    def nearby(address, api_key):
        API_KEY = api_key
        map_client = googlemaps.Client(API_KEY)
        response = map_client.geocode(address)
        loc = str(list(response[0]['geometry']['location'].values())).replace('[','').replace(']','')
        places_result = map_client.places_nearby(location = loc, radius = 4000, open_now = False, type =['cafe', 'restaurant','food'],                                                page_token = None ) #places_result['next_page_token'])
        final = []

        for place in places_result['results']:
            my_place_id = place['place_id']
            # my_fields = ['name', 'formatted_phone_number','opening_hours','rating','type']
            place_details = map_client.place(place_id = my_place_id)
            final.append(place_details['result'])
        if 'next_page_token' in places_result:
            places_result = map_client.places_nearby(location = loc, radius = 4000, open_now = False, type =['cafe', 'restaurant','food'],                                                page_token = places_result['next_page_token'])
            for place in places_result['results']:
                my_place_id = place['place_id']
                # my_fields = ['name', 'formatted_phone_number','opening_hours','rating','type']
                place_details = map_client.place(place_id = my_place_id)
                final.append(place_details['result'])
            if 'next_page_token' in places_result:
                places_result = map_client.places_nearby(location = loc, radius = 4000, open_now = False, type =['cafe', 'restaurant','food'],                                                    page_token = places_result['next_page_token'])
                for place in places_result['results']:
                    my_place_id = place['place_id']
                    # my_fields = ['name', 'formatted_phone_number','opening_hours','rating','type']
                    place_details = map_client.place(place_id = my_place_id)
                    final.append(place_details['result'])
        x = pd.DataFrame.from_dict(final)
        x['Latitude'] = None
        x['Longitude'] = None
        x['weekday_text'] = None
        x['overview'] = None
        for i in range(len(x)):
            x['Latitude'][i] = x.iloc[i]['geometry']['location']['lat']
            x['Longitude'][i] = x.iloc[i]['geometry']['location']['lng']
            if type(x.iloc[i]['current_opening_hours']) == dict:
                x['weekday_text'][i] =  x.iloc[i]['current_opening_hours']['weekday_text']
            if type(x.iloc[i]['editorial_summary']) == dict:
                x['overview'][i] = x.iloc[i]['editorial_summary']['overview']
        x['monday'] = None
        x['tuesday'] = None
        x['wednesday'] = None
        x['thursday'] = None
        x['friday'] = None
        x['saturday'] = None
        x['sunday'] = None
        for i in range(len(x)):
            if type(x.iloc[i].weekday_text) == list:
                for j in range(len(x.iloc[i].weekday_text)):
                    s = x.iloc[i].weekday_text[j].encode("ascii", "replace").decode(encoding="utf-8", errors="ignore").replace("?"," ")
                    o =dict(item.replace('   ', ' - ').split(": ") for item in s.split("  ,  "))
                    if 'Monday' in o:
                        x['monday'][i] = o['Monday']
                    elif 'Tuesday' in o:
                        x['tuesday'][i] = o['Tuesday']
                    elif 'Wednesday' in o:
                        x['wednesday'][i] = o['Wednesday']
                    elif 'Thursday' in o:
                        x['thursday'][i] = o['Thursday']
                    elif 'Friday' in o:
                        x['friday'][i] =  o['Friday']
                    elif 'Saturday' in o:
                        x['saturday'][i] = o['Saturday']
                    elif 'Sunday' in o:
                        x['sunday'][i] =  o['Sunday']
        from progressbar import ProgressBar
        pbar = ProgressBar()
        for i in pbar(range(len(x))):
            if type(x.iloc[i]['photos']) == list:
                for j in range(len(x.iloc[i]['photos'])):
                    pr = x.iloc[i]['photos'][j]['photo_reference']
                    # height = x.iloc[i]['photos'][j]['height']
                    # width = x.iloc[i]['photos'][j]['width']
                    raw_image_data = map_client.places_photo(photo_reference = pr, max_height = 400, max_width = 400)
                    fp  = open(("D:/Agoda/Final_Images/" + x.iloc[i]['name'].replace("/","_") + '_' +str(j) + '.jpg'), "wb")
                    # with open('/work/images/' + x.iloc[0]['name'] + '_'+str(j) + '.jpg', "wb") as fp:
                    for chunk in raw_image_data:
                        fp.write(chunk)
                    fp.close()
        x['photos_count'] = None
        for i in range(len(x)):
            if type(x.iloc[i]['photos']) == list:
                x['photos_count'][i] = len(x.iloc[i].photos)
        columnss = ['name', 'formatted_address', 'Latitude', 'Longitude', 'international_phone_number', 'website',                 'overview', 'types', 'rating',  'user_ratings_total', 'price_level', 'monday', 'tuesday', 'wednesday', 'thursday',                'friday','saturday', 'sunday', 'photos_count', 'photos']
        y = x[columnss]
        return y
    import warnings
    warnings.filterwarnings("ignore")
    z = pd.DataFrame()
    for i in tqdm(range(len(location_list.locations))):
        temp_data = nearby(location_list.locations[i], api_key)
        z = pd.concat([z,temp_data], ignore_index=True)
    final_data = z.loc[z.astype(str).drop_duplicates(keep='first').index]

    m = folium.Map(location=[final_data.iloc[0]['Latitude'], final_data.iloc[0]['Longitude']], zoom_start=10)

    pbar = ProgressBar()

    for i in pbar(range(len(final_data))):
        if type(final_data.iloc[i]['photos']) == list:
            images = []

            table = '<table style="width:350px">'
            for j in range(len(final_data.iloc[i]['photos'])):
                # generate the path to the image file on your local disk
                filename = final_data.iloc[i]['name'].replace("/", "_") + '_' + str(j) + '.jpg'
                filepath = os.path.join('D:/Agoda/Final_Images/', filename)

                # check if the file exists
                if os.path.isfile(filepath):
                    with open(filepath, 'rb') as f:
                        # encode the image as base64 and add it to the images list
                        encoded = base64.b64encode(f.read()).decode()
                        images.append('<a href="{}" target="_blank"><img src="data:image/jpeg;base64,{}" width=100 height=100 style="border:1px;border-radius:25px;"></a>'.format(filepath, encoded))

                        if (j + 1) % 3 == 0:  # Add a new row every third image
                            table += '<tr><td style="padding: 5px">' + '</td><td style="padding: 5px">'.join(images) + '</td></tr>'
                            images = []

                else:
                    print("File not found:", filepath)
            if images:
                table += '<tr><td style="padding: 5px">' + '</td><td style="padding: 5px">'.join(images) + '</td></tr>'

            table += '</table>'

            popup_text = "<table style='font-size:12px; width:350px'>"                  "<tr><td style='width: 18%;padding:7px;'><b>Name:</b></td><td>{}</td></tr>"                  "<tr><td style='width: 18%;padding:7px;'><b>Address:</b></td><td>{}</td></tr>"                  "<tr><td style='width: 18%;padding:7px;'><b>Latitude:</b></td><td>{}</td></tr>"                  "<tr><td style='width: 18%;padding:7px;'><b>Longitude:</b></td><td>{}</td></tr>"                  "<tr><td style='width: 18%;padding:7px;'><b>Phone No.:</b></td><td>{}</td></tr>"                 "<tr><td style='width: 18%;padding:7px;'><b>Website:</b></td><td><a href='{}' target='_blank'>{}</a></td></tr>"                  "<tr><td style='width: 18%;padding:7px;'><b>Types:</b></td><td>{}</td></tr>"                  "<tr><td style='width: 18%;padding:7px;'><b>Rating:</b></td><td>{}</td></tr>"                  "</table>".format(final_data.iloc[i]['name'], final_data.iloc[i]['formatted_address'], final_data.iloc[i]['Latitude'], 
                                            final_data.iloc[i]['Longitude'], final_data.iloc[i]['international_phone_number'],
                                            final_data.iloc[i]['website'], final_data.iloc[i]['website'], final_data.iloc[i]['types'], final_data.iloc[i]['rating'])

            popup = folium.Popup(table + popup_text, max_width=900, max_height=900)
            marker = folium.Marker([final_data.iloc[i]['Latitude'], final_data.iloc[i]['Longitude']], popup=popup, icon=folium.Icon(color='black')).add_to(m)
            m.add_child(marker)
    def data_retrieval(database, user, password, host, port):
        import pandas as pd
        import psycopg2 as pg
        conn = pg.connect(database=database, user=user, password=password, host=host, port=port)
        cursor = conn.cursor()
        cursor.execute("select * from raw_data")

        rows = cursor.fetchall()

        # cursor.close()

        # cursor = conn.cursor()
        cursor.execute("""SELECT column_name, ordinal_position FROM information_schema.columns
                          WHERE table_name = 'raw_data'""")

        cols = cursor.fetchall()
        cols.sort(key=lambda col: col[1])
        column_names = [col[0] for col in cols]

        cursor.close()

        df = pd.DataFrame(rows)
        df.columns = column_names

        return df

    db_data = data_retrieval('Agoda', 'postgres', 'dsm@123', '192.168.0.44', '5432')
    pbar = ProgressBar()
    for i in pbar(range(len(db_data))):
        popup_text = "<table style='font-size:12px; width:430px'>"
        if not pd.isnull(db_data.iloc[i]['name']):
            popup_text += "<tr><td style='width: 18%;padding:7px;'><b>Name:</b></td><td>{}</td></tr>".format(db_data.iloc[i]['name'])
        if not pd.isnull(db_data.iloc[i]['instagram_id']):
            popup_text += "<tr><td style='width: 18%;padding:7px;'><b>Instagram:</b></td><td>{}</td></tr>".format(db_data.iloc[i]['instagram_id'])
        if not pd.isnull(db_data.iloc[i]['age_requirement']):
            popup_text += "<tr><td style='width: 18%;padding:7px;'><b>Age Requirement:</b></td><td>{}</td></tr>".format(db_data.iloc[i]['age_requirement'])
        if not pd.isnull(db_data.iloc[i]['must_try_dishes']):
            popup_text += "<tr><td style='width : 18%;padding:7px;'><b>Must Try Dishes:</b></td><td>{}</td></tr>".format(db_data.iloc[i]['must_try_dishes'])
        if not pd.isnull(db_data.iloc[i]['cuisine']):
            popup_text += "<tr><td style='width: 18%;padding:7px;'><b>Cuisine:</b></td><td>{}</td></tr>".format(db_data.iloc[i]['cuisine'])
        if not pd.isnull(db_data.iloc[i]['attractions']):
            popup_text += "<tr><td style='width: 18%;padding:7px;'><b>Attractions:</b></td><td>{}</td></tr>".format(db_data.iloc[i]['attractions'])
        if not pd.isnull(db_data.iloc[i]['dress_code']):
            popup_text += "<tr><td style='width: 18%;padding:7px;'><b>Dress Code:</b></td><td>{}</td></tr>".format(db_data.iloc[i]['dress_code'])
        if not pd.isnull(db_data.iloc[i]['how_to_reach']):
            popup_text += "<tr><td style='width: 18%;padding:7px;'><b>How to Reach:</b></td><td>{}</td></tr>".format(db_data.iloc[i]['how_to_reach'])
        if not pd.isnull(db_data.iloc[i]['things_to_do']):
            popup_text += "<tr><td style='width: 18%;padding:7px;'><b>Ratings:</b></td><td>{}</td></tr>".format(db_data.iloc[i]['things_to_do'])
        popup_text += "</table>"

        popup = folium.Popup(popup_text, max_width=900, max_height=900)
        marker = folium.Marker([db_data.iloc[i]['latitude'], db_data.iloc[i]['longitude']], popup=popup, icon=folium.Icon(color='red')).add_to(m)
        m.add_child(marker)
    path = "D:/test1.html"
    m.save(path)
    
maps_plot()


# In[ ]:




