

import csv
import datetime
import random
import psycopg2
import requests
# Definieer een lijst met stations
stations = ['Utrecht', 'Amersfoort', 'Zwolle']

# PostgreSQL databaseverbinding
connection = psycopg2.connect(
    database="Stationszuil2",
    user="postgres",
    password="21010412",
    host="20.224.100.97",
    port="5432"
)

cursor = connection.cursor()

# Maak de database en tabel aan als deze nog niet bestaan
cursor.execute('''
    CREATE TABLE IF NOT EXISTS berichten (
        berichten_id SERIAL PRIMARY KEY,
        bericht TEXT,
        datum_tijd TIMESTAMP,
        naam TEXT,
        station TEXT
    )
''')

# CREATE TABLE-query om de tabel "Moderatie" aan te maken
cursor.execute('''
    CREATE TABLE IF NOT EXISTS Moderatie (
        Moderatie_ID SERIAL PRIMARY KEY,
        berichten_ID SERIAL,
        Goedkeuring TEXT,
        Datum_Tijd_Moderatie TIMESTAMP,
        mail_moderator TEXT,
        naam_moderator TEXT,
        FOREIGN KEY (berichten_ID) REFERENCES berichten (berichten_id)
    )
''')


connection.commit()

# Functie om een bericht op te slaan in CSV en de database
def sla_bericht_op(bericht, naam, station):
    timestamp = datetime.datetime.now()
    if not naam:
        naam = 'anoniem'

    with open('berichten.csv', mode='a', newline='') as bestand:
        schrijver = csv.writer(bestand)
        schrijver.writerow([bericht, timestamp, naam, station])

    cursor.execute('''
        INSERT INTO berichten (bericht, datum_tijd, naam, station)
        VALUES (%s, %s, %s, %s)
    ''', (bericht, timestamp, naam, station))

    connection.commit()



def goedkeuren_berichten(connection, m_mail, m_naam):
    # Fetch the berichten_id based on the message content

        with open('berichten.csv', mode='r') as bestand:
            lezer = csv.reader(bestand)
            rijen = [regel for regel in lezer]

        with open('berichten.csv', 'w', newline='') as bestand:
            schrijver = csv.writer(bestand)
            if m_mail.lower() == '1' and m_naam.lower() == '2':
                antwoord = None
                mod_tijd = None



                for regel in rijen:
                    if 'Goedgekeurd' not in regel and 'Afgekeurd' not in regel:
                        antwoord = input(f'\nKeurt u dit goed (ja/nee/overslaan): {regel}')
                        if antwoord.lower() == 'ja':
                            mod_tijd = datetime.datetime.now()
                            regel.append('Goedgekeurd')
                            regel.append(mod_tijd)
                            regel.append(m_mail)
                            regel.append(m_naam)
                            cursor.execute('''
                                                    INSERT INTO Moderatie (Goedkeuring, Datum_Tijd_Moderatie, mail_moderator, naam_moderator)
                                                    VALUES (%s, %s, %s, %s)
                                                ''', (antwoord, mod_tijd, m_mail, m_naam))
                            connection.commit()
                        elif antwoord.lower() == 'nee':
                            mod_tijd = datetime.datetime.now()
                            regel.append('Afgekeurd')
                            regel.append(mod_tijd)
                            regel.append(m_mail)
                            regel.append(m_naam)
                            cursor.execute('''
                                                                            INSERT INTO Moderatie (Goedkeuring, Datum_Tijd_Moderatie, mail_moderator, naam_moderator)
                                                                            VALUES (%s, %s, %s, %s)
                                                                        ''', (antwoord, mod_tijd, m_mail, m_naam))
                            connection.commit()
                        elif antwoord.lower() == 'overslaan':
                            print('Bericht overgeslagen!')
                        else:
                            print('Geen ja of nee ingevuld!')
                    schrijver.writerow(regel)
                else:
                    print('Alle berichten zijn doorlopen!')
            else:
                print('Uw naam of email-adres is niet goed ingevoerd!')

        return antwoord, mod_tijd




# sander.neele@student.hu.nl
# sander neele






# Hoofdprogramma
bericht = ""
while True:
    naam = input("Voer uw naam in (druk op Enter voor anoniem): ")
    if naam.lower() == 'mod':
        m_mail = input('Vul uw mail in: ')
        m_naam = input('Vul uw naam in: ')
        result = goedkeuren_berichten(connection, m_mail, m_naam)
        break
    else:
        bericht = input("Voer uw bericht in (maximaal 140 tekens): ")

        if len(bericht) <= 140:
            station = random.choice(stations)
            sla_bericht_op(bericht, naam, station)
            print("Bericht opgeslagen.")
            # Retrieve the most recent berichten_id here
            cursor.execute('SELECT MAX(berichten_id) FROM berichten')
            latest_berichten_id = cursor.fetchone()[0]
        else:
            print("Bericht is te lang. Probeer opnieuw.")

        break












# Roep de functie aan om berichten goed te keuren en op te slaan in 'moderatie.csv'










BASE_URL = "http://api.openweathermap.org/data/2.5/weather?"
API_KEY = "d90ad5b45e629f53dfa4682ec814c3db"  # Replace with your actual OpenWeatherMap API key
CITY = station
UNITS = "metric"  # You can change this to "imperial" for Fahrenheit or "standard" for Kelvin

url = BASE_URL + "appid=" + API_KEY + "&q=" + CITY

response = requests.get(url).json()
print(response)



def kelvin_to_celsius(kelvin):
    celsius = kelvin - 273.15
    return celsius

temp_kelvin = response['main']['temp']
temp_celsius = kelvin_to_celsius(temp_kelvin)
temp_celsius = round(temp_celsius, 1)
Weer = response['weather'][0]['description']

print(f'Het is nu: {temp_celsius}°C')

from tkinter import *


def onclick():
    base = int(entry.get())
    square = base ** 2
    outcome = f"square: of {base} = {square}"
    label['text'] =outcome
### main:

root = Tk()

label = Label(master=root, text='Hello World', bg='yellow', width=200, height=100)

button = Button(master=root, text='press')
button.pack(pady=10)

entry = Entry(master=root)
entry.pack(padx=10, pady=10)


root.mainloop()