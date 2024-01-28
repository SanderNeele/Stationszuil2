import csv
import json
import datetime
import random
import psycopg2
import requests
import os

# Onderdrukken van Tkinter-deprecated-waarschuwingen
os.environ['TK_SILENCE_DEPRECATION'] = '1'
import tkinter as tk
from tkinter import ttk
from tkinter import PhotoImage



# Lijst met stations
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

# Tabel berichten creëren als deze nog niet bestaat
cursor.execute('''
    CREATE TABLE IF NOT EXISTS berichten (
        berichten_id SERIAL PRIMARY KEY,
        bericht TEXT,
        datum_tijd TIMESTAMP,
        naam TEXT,
        station TEXT
    )
''')

# Tabel moderatie creëren als deze nog niet bestaat
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
    # Huidige tijd ophalen
    timestamp = datetime.datetime.now()
    timestamp = timestamp.strftime("%Y-%m-%d %H:%M:%S")

    # Als geen naam is opgegeven, wordt de naam anoniem
    if not naam:
        naam = 'anoniem'

    # Berichten opslaan in CSV-bestand
    with open('berichten.csv', mode='a', newline='') as bestand:
        schrijver = csv.writer(bestand)
        schrijver.writerow([bericht, timestamp, naam, station])

    # Gegevens naar berichten tabel in database sturen
    cursor.execute('''
        INSERT INTO berichten (bericht, datum_tijd, naam, station)
        VALUES (%s, %s, %s, %s)
    ''', (bericht, timestamp, naam, station))

    connection.commit()

# Functie voor goedkeuren van berichten
def goedkeuren_berichten(connection, m_mail, m_naam):
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
                        print('Geen ja, nee of overslaan ingevuld!')
                schrijver.writerow(regel)
            else:
                print('Alle berichten zijn doorlopen!')
        else:
            print('Uw naam of email-adres is niet goed ingevoerd!')

    return antwoord, mod_tijd

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

            cursor.execute('SELECT MAX(berichten_id) FROM berichten')
            latest_berichten_id = cursor.fetchone()[0]
        else:
            print("Bericht is te lang. Probeer opnieuw.")
        break


# Code voor het halen van het weer uit de plaatsen van mijn stations.
# Dit doe ik met openweather API
# Base url voor de API weather map
BASE_URL = "http://api.openweathermap.org/data/2.5/weather?"
# Mijn API_key
API_KEY = "d90ad5b45e629f53dfa4682ec814c3db"
# De basis stad.
CITY = "Utrecht"
# De unit is metric.
UNITS = "metric"

url = BASE_URL + "appid=" + API_KEY + "&q=" + CITY
# Response wordt in een json gezet.
response = requests.get(url).json()
# Functie om kelvin om te zetten naar celsius.
def kelvin_to_celsius(kelvin):
    celsius = kelvin - 273.15
    return celsius
# De temperatuur en de beschrijving wordt uit response gehaald.
temp_kelvin = response['main']['temp']
temp_celsius = kelvin_to_celsius(temp_kelvin)
temp_celsius = round(temp_celsius, 1)
Weer = response['weather'][0]['description']

font = "Calibri"
kleur1 = "#ffc917"  # ns-geel
kleur2 = "#0063d3" #ns-blauw

# Functie voor de laatste vijf berichten.
def laatste_5_berichten():
    # Uit mijn database maak ik een querry waar de laatste berichten uit het berichten tabel.
    cursor.execute('''
        SELECT bericht, naam, station, datum_tijd
        FROM berichten
        ORDER BY datum_tijd DESC
        LIMIT 5
    ''')
    # De resultaten van de uitslag van de querry wordt gereturned.
    resultaten = cursor.fetchall()
    return resultaten
berichten123 = laatste_5_berichten()
# Er wordt een berichten lijst gemaakt.
bericht_lijst = []
# Voor alle berichten in de laatste 5 berichten (berichten123).
for bericht in berichten123:
    # Worden de lijst gevuld met berichtje, naam, station, datum_tijd.
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
# Dit wordt omgezet naar een json bestand.
bericht_json = json.dumps(bericht_lijst)

# De functie om alle voorzienigen te halen die als boolean true zijn, uit het tabel station_service.
def haal_true_kolommen_op(connection, steden):
    cursor = connection.cursor()
    # Er wordt een dictionary gemaakt waar alle kolommen die true hebben.
    kolommen_met_true = {}
    # Voor stad in steden:
    for stad in steden:
        # Defineer in de querry waar de voorzienigen true zijn.
        query = """
        SELECT station_city, toilet, ov_bike, elevator, park_and_ride
        FROM station_service
        WHERE station_city = %s
        """
        cursor.execute(query, (stad,))
        resultaten = cursor.fetchall()


        for result in resultaten:
            station_name = result[0]
            services = result[1:]
            service_names = ['toilet', 'ov_bike', 'elevator', 'park_and_ride']
            true_services = [service_names[i] for i, service_available in enumerate(services) if service_available]

            # Voe de true voorzienigen toe aan de dictionary.
            kolommen_met_true[station_name] = true_services

    cursor.close()
    return kolommen_met_true


steden = ['Amersfoort', 'Utrecht', 'Zwolle']
true_kolommen = haal_true_kolommen_op(connection, steden)

# Functie om het scherm te kunnen sluiten.
def sluit_scherm():
    root.destroy()
# Functie om de berichten te tonen.
def toon_berichten():
    # Uit mijn database maak ik een query waar de laatste goedgekeurde berichten uit het berichten tabel worden opgehaald.
    cursor.execute('''
        SELECT b.bericht, b.naam, b.station, b.datum_tijd
        FROM berichten b
        JOIN Moderatie m ON b.berichten_id = m.berichten_id
        WHERE m.Goedkeuring = 'ja'
        ORDER BY b.datum_tijd DESC
        LIMIT 5
    ''')
    # De resultaten van de uitslag van de query worden opgehaald.
    resultaten = cursor.fetchall()

    for bericht in resultaten:
        datum_tijd = bericht[3].strftime("%d %B %Y %H:%M:%S")  # Opmaak van datum & tijd
        naam = bericht[1]
        station = bericht[2]
        bericht_text = bericht[0]
        bericht_label = tk.Label(berichten_frame,
                                 text=f"Datum & tijd: {datum_tijd}\nNaam: {naam}\nStation: {station}\nBericht: {bericht_text}",
                                 wraplength=400, fg="black", bg="white") # Set text color to black
        print(bericht_label)
        bericht_label.pack(fill="x", pady=10, padx=5)

        # Een gele lijn wordt onder de berichten toegevoegd.
        separator = ttk.Separator(berichten_frame, orient="horizontal")
        separator.pack(fill="x", pady=10, padx=5)


# Functie om het weer te tonen.
def toon_weerbericht():
    weer_frame = tk.Frame(root, bg=kleur2, pady=10, padx=10)
    weer_frame.pack(padx=30, pady=30, fill="both", expand=True)

    weer_label = tk.Label(weer_frame, text="Weerbericht\n", font=(font, 32, "bold"), bg=kleur2, fg="white")
    weer_label.pack(anchor="w")

    weericoon = tk.Label(weer_frame, text=f"{temp_celsius}°C", font=(font, 28, "bold"), bg=kleur2, fg="white")
    weericoon.pack(anchor="w")

    # Pak de geselcteerde stad van de dropdownmenu.
    geselecteerde_stad = var_dropdown.get()
    # Haal de beschikbare diensten op voor de geselecteerde stad.
    beschikbare_voorzieningen = true_kolommen.get(geselecteerde_stad, [])

    # Update het weerslabel met het weer en de beschikbare diensten.
    weerbericht_label = tk.Label(
        weer_frame,
        text=f"Weerbericht voor {geselecteerde_stad}: {temp_celsius}°C\n"
             f"Beschikbare voorzieningen: {', '.join(beschikbare_voorzieningen)}",
        font=(font, 24, "bold"),  # Making the text bold
        bg=kleur2,
        fg="white"
    )
    weerbericht_label.pack(anchor="w")
    if geselecteerde_stad == 'Zwolle':
        img_label = tk.Label(weer_frame, image=img_toilet, bg=kleur2)
        img_label.pack(anchor="w")

    # Functie om de geselecteerde optie uit het dropdown menu te halen.
    def toon_geselecteerde_optie():
        # Haal de geselecteerde optie op uit de dropdownmenu-widget
        geselecteerde_optie = var_dropdown.get()
        # Als de geselecteerde optie x Stad is.
        # Dan wordt de stad voor het weer x Stad.
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

            # Haal de beschikbare diensten op voor de geselecteerde stad.
            beschikbare_voorzieningen = true_kolommen.get(CITY, [])

            # Werk het label bij met informatie over het weer en de beschikbare diensten.
            weerbericht_label.config(text=f"Weerbericht in {CITY}: {temp_celsius}°C, {weer_in_de_stad}\n\n\n\n" +
                                          f"Beschikbare voorzieningen: {', '.join(beschikbare_voorzieningen)}")
            if CITY == 'Zwolle':
                img_label = tk.Label(weer_frame, image=img_toilet, bg=kleur2)
                img_label.place(relx=0.5, rely=0.5, anchor="center")
                img_ovfiets_label = tk.Label(weer_frame, image=img_ovfiets, bg=kleur2)
                img_ovfiets_label.pack(side="left", anchor="w")
                # Center the image in the frame
            elif CITY == 'Utrecht':
                img_label = tk.Label(weer_frame, image=img_toilet, bg=kleur2)
                img_label.place(relx=0.5, rely=0.5, anchor="center")
                img_ovfiets_label = tk.Label(weer_frame, image=img_ovfiets, bg=kleur2)
                img_ovfiets_label.pack(side="left", anchor="w")
                # Center the image in the frame
            elif CITY == 'Amersfoort':
                img_label = tk.Label(weer_frame, image=img_toilet, bg=kleur2)
                img_label.place(relx=0.5, rely=0.5, anchor="center")
                img_ovfiets_label = tk.Label(weer_frame, image=img_ovfiets, bg=kleur2)
                img_ovfiets_label.pack(side="left", anchor="w")
                # Center the image in the frame


        else:
            weerbericht_label.config(text=f"Weerbericht in {CITY} niet beschikbaar")


    # Voeg de button toe
    toon_optie_button = tk.Button(berichten_frame, text="Toon Geselecteerde Optie", command=toon_geselecteerde_optie)
    toon_optie_button.pack()


root = tk.Tk()

# Titel voor het hoofdscherm.
root.title("Stationshalscherm")
# Maak een frame widget.
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

# foto's
img_toilet_path = "img_toilet.png"
img_toilet = PhotoImage(file=img_toilet_path)
img_ovfiets_path = "img_ovfiets.png"
img_ovfiets = PhotoImage(file=img_ovfiets_path)
toon_berichten()
toon_weerbericht()

sluit_knop = tk.Button(root, text="Sluiten", command=sluit_scherm, font=(font, 16), bg=kleur1, fg=kleur2)
sluit_knop.pack(side="bottom", pady=20)

root.mainloop()