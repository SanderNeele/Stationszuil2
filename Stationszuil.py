import csv
import json
import datetime
import random
import psycopg2
import requests
import os
os.environ['TK_SILENCE_DEPRECATION'] = '1'
import tkinter as tk
from tkinter import ttk
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
    timestamp = timestamp.strftime("%Y-%m-%d %H:%M:%S")
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
CITY = "Utrecht"
UNITS = "metric"  # You can change this to "imperial" for Fahrenheit or "standard" for Kelvin

url = BASE_URL + "appid=" + API_KEY + "&q=" + CITY

response = requests.get(url).json()

def kelvin_to_celsius(kelvin):
    celsius = kelvin - 273.15
    return celsius

temp_kelvin = response['main']['temp']
temp_celsius = kelvin_to_celsius(temp_kelvin)
temp_celsius = round(temp_celsius, 1)
Weer = response['weather'][0]['description']



font = "Calibri"
kleur1 = "#ffc917"  # ns-geel
kleur2 = "#0063d3" #ns-blauw

def laatste_5_berichten():
    cursor.execute('''
        SELECT bericht, naam, station, datum_tijd
        FROM berichten
        ORDER BY datum_tijd DESC
        LIMIT 5
    ''')

    resultaten = cursor.fetchall()
    return resultaten
berichten123 = laatste_5_berichten()

bericht_lijst = []

for bericht in berichten123:
    berichtje = bericht[0]
    naam = bericht[1]
    station = bericht[2]
    datum_tijd = bericht[3].strftime("%d %B %Y %H:%M:%S")  # Opmaak van datum & tijd
    bericht_variabele = {
        "datum_tijd": datum_tijd,
        "naam": naam,
        "station": station,
        "bericht": berichtje
    }
    bericht_lijst.append(bericht_variabele)
bericht_json = json.dumps(bericht_lijst)



def haal_true_kolommen_op(connection, steden):
    cursor = connection.cursor()
    kolommen_met_true = {}

    for stad in steden:
        # Define the query to select the services columns that are True
        query = """
        SELECT station_city, toilet, ov_bike, elevator, park_and_ride
        FROM station_service
        WHERE station_city = %s
        """
        cursor.execute(query, (stad,))
        resultaten = cursor.fetchall()

        # Iterate over the results and store the services that are True
        for result in resultaten:
            station_name = result[0]
            services = result[1:]
            service_names = ['toilet', 'ov_bike', 'elevator', 'park_and_ride']
            true_services = [service_names[i] for i, service_available in enumerate(services) if service_available]

            # Add the true services to the dictionary with the station name as the key
            kolommen_met_true[station_name] = true_services

    cursor.close()
    return kolommen_met_true


# Gebruik de functie
steden = ['Amersfoort', 'Utrecht', 'Zwolle']
true_kolommen = haal_true_kolommen_op(connection, steden)



def sluit_scherm():
    root.destroy()

def toon_berichten():
    for bericht in bericht_lijst:
        datum_tijd = bericht["datum_tijd"]
        naam = bericht["naam"]
        station = bericht["station"]
        bericht_text = bericht["bericht"]
        bericht_label = tk.Label(berichten_frame,
                                 text=f"Datum & tijd: {datum_tijd}\nNaam: {naam}\nStation: {station}\nBericht: {bericht_text}",
                                 wraplength=400, fg="black", bg="white") # Set text color to black

        bericht_label.pack(fill="x", pady=10, padx=5)

        # Voeg een gele lijn onder de berichten toe
        separator = ttk.Separator(berichten_frame, orient="horizontal")
        separator.pack(fill="x", pady=10, padx=5)
# ... (eerder gedeelte van je code)
def toon_weerbericht():
    weer_frame = tk.Frame(root, bg=kleur2, pady=10, padx=10)
    weer_frame.pack(padx=30, pady=30, fill="both", expand=True)
    weer_label = tk.Label(weer_frame, text="Weerbericht\n", font=(font, 32, "bold"), bg=kleur2, fg="white")
    weer_label.pack(anchor="w")

    # Voeg een weericoontje toe
    weericoon = tk.Label(weer_frame, text=f"{temp_celsius}°C", font=(font, 28), bg=kleur2, fg="white")
    weericoon.pack(anchor="w")

    # Get the selected city from the dropdown menu
    geselecteerde_stad = var_dropdown.get()

    # Retrieve the available services for the selected city
    beschikbare_voorzieningen = true_kolommen.get(geselecteerde_stad, [])

    # Update the weather label with the weather and available services
    weerbericht_label = tk.Label(weer_frame, text=f"Weerbericht voor {geselecteerde_stad}: {temp_celsius}°C\n" +
                                                   f"Beschikbare voorzieningen: {', '.join(beschikbare_voorzieningen)}",
                                 font=(font, 24), bg=kleur2, fg="white")
    weerbericht_label.pack(anchor="w")

# Remember to call toon_weerbericht() somewhere in your code where appropriate

    def toon_geselecteerde_optie():
        # Haal de geselecteerde optie op uit de dropdownmenu-widget
        geselecteerde_optie = var_dropdown.get()

        if geselecteerde_optie == 'Amersfoort':
            CITY = 'Amersfoort'  # Stel de stad in op Amersfoort
        elif geselecteerde_optie == 'Utrecht':
            CITY = 'Utrecht'  # Stel de stad in op Utrecht
        elif geselecteerde_optie == 'Zwolle':
            CITY = 'Zwolle'  # Stel de stad in op Zwolle
        else:
            CITY = 'Utrecht'  # Als de optie onbekend is, gebruik standaard Utrecht

        url = BASE_URL + "appid=" + API_KEY + "&q=" + CITY
        response = requests.get(url).json()

        if 'main' in response and 'temp' in response['main']:
            temp_kelvin = response['main']['temp']
            temp_celsius = kelvin_to_celsius(temp_kelvin)
            temp_celsius = round(temp_celsius, 1)
            weer_in_de_stad = response['weather'][0]['description']

            # Retrieve the available services for the selected city
            beschikbare_voorzieningen = true_kolommen.get(CITY, [])

            # Update the label to include weather information and available services
            weerbericht_label.config(text=f"Weerbericht in {CITY}: {temp_celsius}°C, {weer_in_de_stad}\n\n\n\n" +
                                          f"Beschikbare voorzieningen: {', '.join(beschikbare_voorzieningen)}")
        else:
            weerbericht_label.config(text=f"Weerbericht in {CITY} niet beschikbaar")

    # Voeg de button toe
    toon_optie_button = tk.Button(berichten_frame, text="Toon Geselecteerde Optie", command=toon_geselecteerde_optie)
    toon_optie_button.pack()


root = tk.Tk()
root.title("Stationshalscherm")
berichten_frame = tk.Frame(root, bg=kleur1, padx=20, pady=20)
berichten_frame.pack(side="left", fill="both", expand=True)
var_dropdown = tk.StringVar()
dropdown_menu = ttk.Combobox(berichten_frame, textvariable=var_dropdown, values=('Amersfoort', 'Utrecht', 'Zwolle'))
dropdown_menu.pack()

root.configure(bg=kleur1)
root.attributes("-fullscreen", True)
root.title("Stationshalscherm")

berichten_frame = tk.Frame(root, bg=kleur1, padx=20, pady=20)
berichten_frame.pack(side="left", fill="both", expand=True)
berichten_titel = tk.Label(berichten_frame, text="Berichten van onze reizigers", font=(font, 26, "bold"), bg=kleur1,
                           fg=kleur2)
berichten_titel.pack(pady=20)
# Maak een binnenste frame voor de berichten

# Roep de functie om berichten weer te geven op bij het maken van het venster

toon_berichten()
toon_weerbericht()

sluit_knop = tk.Button(root, text="Sluiten", command=sluit_scherm, font=(font, 16), bg=kleur1, fg=kleur2)
sluit_knop.pack(side="bottom", pady=20)

root.mainloop()