import pandas as pd
from PIL import Image
from PIL.ExifTags import TAGS
from datetime import datetime
import os

def getDateTime(imageName):
    img = Image.open(f'data/{imageName}')
    exifData = img._getexif()
    if exifData is not None:
        for tag, value in exifData.items():
            tagName = TAGS.get(tag, tag)
            if tagName == 'DateTime':
                DateTime = value.replace(':', '-', 2)
                return DateTime
    return None

def getTimeDelta(date1, date2):
    d1 = datetime.strptime(date1, '%Y-%m-%d %H:%M:%S')
    d2 = datetime.strptime(date2, '%Y-%m-%d %H:%M:%S')
    t = d2 - d1
    timeDelta = t.total_seconds() / 60
    return timeDelta

def registration():
    output_file = 'final_data.csv'

    # Создаем файл, если он не существует, и добавляем заголовки
    if not os.path.exists(output_file):
        cols = pd.DataFrame(columns=['name_folder', 'class', 'date_registration_start', 'date_registration_end', 'count'])
        cols.to_csv(output_file, index=False)

    # Считываем файл, который выдал детектор с классификатором
    procf = pd.read_csv('no_reg_table.csv')

    folder = int(input("Enter current folder name: "))

    reg = False
    max_count = 0
    reg_start = None
    reg_end = None

    # Проход по каждой строке таблицы
    for i in range(procf.shape[0]):
        date = getDateTime(procf.at[i, 'image_name'])
        current_class = procf.at[i, 'class_name']
        current_count = procf.at[i, 'count']

        if reg:
            time_delta = getTimeDelta(prev_date, date)
            if time_delta > 30:  # Если прошло больше 30 минут
                reg_end = prev_date
                # Добавляем запись о регистрации в итоговый файл
                reg_class = "Not enough data" if reg_class == "Empty" else reg_class
                dataline = {'name_folder': folder, 'class': reg_class, 'date_registration_start': reg_start, 'date_registration_end': reg_end, 'max_count': max_count}
                dataline = pd.DataFrame(dataline, index=[0])
                dataline.to_csv(output_file, mode='a', header=False, index=False)
                reg = False
                max_count = 0

        if not reg:
            reg_start = date
            reg_class = current_class
            reg = True

        max_count = max(max_count, current_count)
        prev_date = date

    # Добавляем последнюю запись, если регистрация не была завершена
    if reg:
        reg_end = prev_date
        reg_class = "данных недостаточно" if reg_class == "Empty" else reg_class
        dataline = {'name_folder': folder, 'class': reg_class, 'date_registration_start': reg_start, 'date_registration_end': reg_end, 'max_count': max_count}
        dataline = pd.DataFrame(dataline, index=[0])
        dataline.to_csv(output_file, mode='a', header=False, index=False)

    print(f"Data has been processed and saved to {output_file}")
