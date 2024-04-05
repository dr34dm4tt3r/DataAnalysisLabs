"""
Лабораторна робота No3
ФБ-21 Хав'юк Андрій

Мета роботи: ознайомитися з системою контролю версій GitHub, навчитися
створювати прості веб-додатки для обміну результатами досліджень із
використанням модуля spyre.

Основні поняття: система контролю версій, репозитoрій, інтерактивний
веб-додаток.
"""

import pandas as pd
from spyre import server
import matplotlib.pyplot as plt
import seaborn as sns
import os
# import time
# from datetime import datetime
# import urllib.requestear

# def downloader(i):
#     # download cvs files
#     download_dir = "/home/andrii/kpi/course_2/data_analysis/DataAnalysisLabs/frames"
#     url=f"https://www.star.nesdis.noaa.gov/smcd/emb/vci/VH/get_TS_admin.php?country=UKR&provinceID={i}&year1=1981&year2=2020&type=Mean".format(i)
#     vhi_url = urllib.request.urlopen(url)
#     now = datetime.now()
#     date = now.strftime("%Y-%m-%d_%H-%M-%S")
#     filename = f"vhi_{i}_{date}.csv"
#     filepath = os.path.join(download_dir, filename)
#     with open(filepath, "wb") as file:
#         file.write(vhi_url.read())
        
def framer():
    # concatenate data frame
    headers = ['Year', 'Week', 'SMN', 'SMT', 'VCI', 'TCI', 'VHI', 'area']
    # files_dir = "/home/andrii/kpi/course_2/data_analysis/DataAnalysisLabs/frames"
    files_dir = "/home/remnux/dalabs/frames"
    dataframe = pd.DataFrame()
    files = os.listdir(files_dir)
    for i, file in enumerate(files):
        path = os.path.join(files_dir, file)  # Get the full path to the file
        try:
            df = pd.read_csv(path, header=1, names=headers)
            df = df.drop(df.loc[df["VHI"] == -1].index)
            df["area"] = file.split("/")[-1].split("_")[1]
            df["Year"] = df["Year"].str.replace("<tt><pre>", "")
            df = df[~df['Year'].str.contains('</pre></tt>')]
            #df.drop('empty', axis=1, inplace=True)
            df['Year'] = df['Year'].astype(int)
            df['Week'] = df['Week'].astype(int)
            df['area'] = df['area'].astype(int)
            dataframe = pd.concat([dataframe, df]).drop_duplicates().reset_index(drop=True)
        except Exception as e:
            print(f"Error reading file {file}: {e}")
    return dataframe

cities =  {1: "Cherkasy", 2: "Chernihiv", 3: "Chernivtsi", 4: "Crimea", 5: "Dnipropetrovs'k", 6: "Donets'k", 
            7: "Ivano-Frankivs'k", 8: "Kharkiv", 9: "Kherson", 10: "Khmel'nyts'kyy", 11: "Kyiv", 12: "Kiev City", 
            13: "Kirovohrad", 14: "Luhans'k", 15: "L'viv", 16: "Mykolayiv", 17: "Odessa", 18: "Poltava", 19: "Rivne",
            20: "Sevastopol'", 21: "Sumy", 22: "Ternopil'", 23: "Transcarpathia", 24: "Vinnytsya", 25: "Volyn", 
            26: "Zaporizhzhya", 27: "Zhytomyr"}
    
class Vegetation(server.App):
    title = "LAB 3"
    
    inputs = [
        {
            "type": 'dropdown',
            "label": 'Time raw',
            "options": [
                {"label": "VCI", "value": "VCI"},
                {"label": "TCI", "value": "TCI"},
                {"label": "VHI", "value": "VHI"}
            ],
            "key": 'index',
            "action_id": "update_data"
        },
        {
            "type": 'dropdown',
            "label": 'Region',
            "options": [
                {"label": cities[i], "value": i} for i in range(1, 28)
            ],
            "key": 'region',
            "action_id": "update_data"
        },
        {
            "type": 'text',
            "label": 'Range of weeks',
            "value": "1-52",
            "key": 'week_interval',
            "action_id": "update_data"
        },
        {
            "type": 'text',
            "label": 'Date [yyyy-yyyy]',
            "value": '2000-2021',
            "key": 'date_range',
            "action_id": "update_data"
        }
    ]

    controls = [{"type": "button", "label": "Update", "id": "update_data"}]

    tabs = ["Table", "Plot"]

    outputs = [
        {"type": "table", "id": "table", "control_id": "update_data", "tab": "Table"},
        {"type": "plot", "id": "plot", "control_id": "update_data", "tab": "Plot"}
    ]

    def getData(self, params):
        index = params['index']
        region = int(params['region'])
        week_interval = params['week_interval'].split('-')
        date_range = params['date_range'].split('-')

        dataframe = framer()

        data_filtered = dataframe[(dataframe['area'] == region) & 
                                (dataframe['Year'].between(int(date_range[0]), int(date_range[1]))) &
                                (dataframe['Week'].between(int(week_interval[0]), int(week_interval[1])))]
        
        data_filtered = data_filtered[['Year', 'Week', index]]

        return data_filtered

    def getPlot(self, params):
        index = params['index']
        region = int(params['region'])
        week_interval = params['week_interval'].split('-')
        date_range = params['date_range'].split('-')

        data_filtered = self.getData(params)

        filtered_data = data_filtered[(data_filtered['Year'].between(int(date_range[0]), int(date_range[1]))) &
                                      (data_filtered['Week'].between(int(week_interval[0]), int(week_interval[1])))]

        # Creating a heatmap
        pivot_data = filtered_data.pivot(index='Year', columns='Week', values=index)
        plt.figure(figsize=(20, 15))
        sns.heatmap(pivot_data, cmap="YlGnBu", annot=True)
        plt.title(f'Heatmap {index} for region: {cities[region]}')
        plt.xlabel('Week')
        plt.ylabel('Year')

        plot = plt.gcf()
        return plot

def main():
    # executing downloader
    # start_time = time.time()
    # for i in range(1,28):
    #     downloader(i)
    # end_time = time.time()
    # print(f"After {end_time-start_time} VHIs have been downloaded successfully...")
        
    df = framer()
    # print(df)
    
    app = Vegetation()
    app.launch()

if __name__ == "__main__":
    main()