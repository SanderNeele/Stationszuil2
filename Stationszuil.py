import csv
import datetime
import random
import psycopg2
import requests
# Stationslijst
stations = ['Utrecht', 'Amersfoort', 'Zwolle']

# PostgreSQL databaseverbinding
connection = psycopg2.connect(
    database="Stationszuil",
    user="postgres",
    password="210104",
    host="localhost",
    port="5433"
)

cursor = connection.cursor()

# Maak de database en tabel aan als deze nog niet bestaat
cursor.execute('''
    CREATE TABLE IF NOT EXISTS berichten (
        id SERIAL PRIMARY KEY,
        bericht TEXT,
        datum_tijd TIMESTAMP,
        naam TEXT,
        station TEXT,
        goedgekeurd BOOLEAN,
        datum_tijd_beoordeling TIMESTAMP,
        moderator_naam TEXT,
        moderator_email TEXT
    )
''')

connection.commit()

# Functie om bericht op te slaan in CSV en database
# Functie om bericht op te slaan in CSV en database
def opslaan_bericht(bericht, naam, station):
    timestamp = datetime.datetime.now()
    if not naam:
        naam = 'anoniem'

    moderator_naam = 'Sander Neele'  # De naam van de moderator
    moderator_email = 'sanderneele@student.hu.nl'  # Het e-mailadres van de moderator

    with open('berichten.csv', mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([bericht, timestamp, naam, station, False, None, moderator_naam, moderator_email])

    cursor.execute('''
        INSERT INTO berichten (bericht, datum_tijd, naam, station, goedgekeurd, datum_tijd_beoordeling, moderator_naam, moderator_email)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    ''', (bericht, timestamp, naam, station, False, None, moderator_naam, moderator_email))

    connection.commit()


# Functie om berichten te lezen en toe te voegen
# Functie om berichten te lezen en toe te voegen
def lees_berichten_en_voeg_toe():
    with open('berichten.csv', mode='r') as file:
        reader = csv.reader(file)
        for row in reader:
            bericht, datum_tijd, naam, station = row
            goedgekeurd = False  # Het bericht wordt nog niet beoordeeld, dus standaard ingesteld op False
            datum_tijd_beoordeling = datetime.datetime.now()  # Huidige datum en tijd
            moderator_naam = 'Sander Neele'  # De naam van de moderator
            moderator_email = 'sanderneele@student.hu.nl'  # Het e-mailadres van de moderator
            cursor.execute('''
                INSERT INTO berichten (bericht, datum_tijd, naam, station, goedgekeurd, datum_tijd_beoordeling, moderator_naam, moderator_email)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ''', (bericht, datum_tijd, naam, station, goedgekeurd, datum_tijd_beoordeling, moderator_naam, moderator_email))
            connection.commit()


# Hoofdprogramma
while True:
    bericht = input("Voer uw bericht in (maximaal 140 karakters): ")
    if len(bericht) <= 140:
        station = random.choice(stations)
        naam = input("Voer uw naam in (druk Enter voor anoniem): ")
        opslaan_bericht(bericht, naam, station)
        print("Bericht opgeslagen.")
    else:
        print("Bericht te lang. Probeer opnieuw.")
    break



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
print(Weer)
print(f'Het is nu: {temp_celsius}°C')


