import tkinter as tk
font = "Calibri"
kleur1 = "#ffc917"  # ns-geel
kleur2 = "#0063d3"  # ns-blauw

# Voorbeeldgegevens
berichten = [
    {"naam": "John", "datum_tijd": "2023-11-05 10:00", "zin": "Dit is het eerste bericht."},
    {"naam": "Alice", "datum_tijd": "2023-11-05 12:30", "zin": "Hallo, dit is Alice."},
    {"naam": "Bob", "datum_tijd": "2023-11-05 15:15", "zin": "Groeten van Bob!"},
    {"naam": "Eva", "datum_tijd": "2023-11-06 09:45", "zin": "Eva hier. Hoe gaat het?"},
    {"naam": "David", "datum_tijd": "2023-11-06 14:20",
     "zin": "Laatste bericht van David. De trein reed alweer nietr op tijd."}
]


# Functie om frames te maken voor elk bericht
def maak_bericht_frame(bericht_data):
    frame = tk.Frame(berichten_frame, bg="white", pady=30, padx=30)
    frame.pack(padx=10, pady=10, fill="both", expand=True)  # Padding wordt nu aan de rechterkant toegevoegd
    naam_label = tk.Label(frame, text=f"Naam: {bericht_data['naam']}", font=(font, 14), bg="white", fg="black")
    datum_tijd_label = tk.Label(frame, text=f"Datum en Tijd: {bericht_data['datum_tijd']}", font=(font, 12), bg="white",
                                fg="black")
    zin_label = tk.Label(frame, text=f"Bericht: {bericht_data['zin']}", font=(font, 14), bg="white", fg="black")
    naam_label.pack(anchor="w")
    datum_tijd_label.pack(anchor="w")
    zin_label.pack(anchor="w")


# Functie om het actuele weerbericht weer te geven
def toon_weerbericht():
    weer_frame = tk.Frame(root, bg=kleur2, pady=10, padx=10)
    weer_frame.pack(padx=30, pady=30, fill="both", expand=True)
    weer_label = tk.Label(weer_frame, text="Weerbericht", font=(font, 20, "bold"), bg=kleur2, fg="white")
    weer_label.pack(anchor="w")

    # Voeg een weericoontje toe
    weericoon = tk.Label(weer_frame, text="☁️ 20°C, Bewolkt", font=(font, 18), bg=kleur2, fg="white")
    weericoon.pack(anchor="w")


# Functie om het scherm te sluiten
def sluit_scherm():
    root.destroy()


# Tkinter hoofdvenster
root = tk.Tk()
root.title("Berichten")

# Aanpassen van de achtergrondkleur en beeldvullend maken
root.configure(bg=kleur1)
root.attributes("-fullscreen", True)

# Frame om berichten weer te geven
berichten_frame = tk.Frame(root, bg=kleur1, padx=20, pady=20)
berichten_frame.pack(side="left", fill="both", expand=True)

# Frame voor weerbericht
toon_weerbericht()

# Voeg een titel boven de berichten toe
berichten_titel = tk.Label(berichten_frame, text="Berichten van onze reizigers", font=(font, 26, "bold"), bg=kleur1,
                           fg=kleur2)
berichten_titel.pack(pady=20)

# Labels om alle berichten weer te geven
for bericht_data in berichten:
    maak_bericht_frame(bericht_data)

# Voeg een knop toe om het scherm te sluiten
sluit_knop = tk.Button(root, text="Sluiten", command=sluit_scherm, font=(font, 16), bg=kleur1, fg=kleur2)
sluit_knop.pack(side="bottom", pady=20)

root.mainloop()