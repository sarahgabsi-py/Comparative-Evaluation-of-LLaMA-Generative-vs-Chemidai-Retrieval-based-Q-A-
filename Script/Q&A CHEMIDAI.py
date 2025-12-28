#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun 20 14:59:49 2025

@author: sarahgabsi
"""



import csv
import requests
import json
import time
import re

# --- API CHEMIDAI ---
url_chemidai = "https://api.example.com/endpoint" #rimosso per ragioni di riservatezza aziendale
headers_chemidai = {
    'Calling-App': 'chemidai',
    'Calling-Company': '1',
    'Content-Type': 'application/json',
    'Authorization': 'YOUR_API_TOKEN_HERE' #rimosso per ragioni di riservatezza aziendale
}

# --- Mappa dei context fornita manualmente ---
mappa_context = {
    "Tomba del Tuffatore": "Q464384",
    "Accademia di Platone": "Q12886301",
    "Achille e Briseide": "Q4673755",
    "Adorazione dei Magi": "Q109498149",
    "Adorazione dei pastori": "Q1183111",
    "Agar e Ismaele nel deserto confortati dall'angelo": "Q115057293",
    "Antea": "Q771980",
    "Apollo e Marsia": "Q97185664",
    "Catalogo di pesci su sfondo nero": "Q54571667",
    "Consegna della regola francescana": "Q3687198",
    "Consultazione della fattucchiera": "Q12884117",
    "Cratere del Vesuvio con l'eruzione del 1820": "Q117857170",
    "Crocifissione": "Q128783366",
    "Diana": "Q132543",
    "Doriforo": "Q1136305",
    "Dànae": "Q99509318",
    "Europa sul toro": "Q126192741",
    "Fauno danzante": "Q117836319",
    "Ferdinando IV a caccia di folaghe sul lago di Fusaro": "Q19984726",
    "Flagellazione di Cristo": "Q131557338",
    "Flora": "Q131449",
    "Giocatrici di astragali": "Q127424840",
    "Il Battesimo di Cristo": "Q16564738",
    "Il Prevetariello": "Q116968761",
    "Inaugurazione della ferrovia Napoli-Portici, l'arrivo a Portici": "Q116968488",
    "La cantatrice": "Q54998747",
    "La terrazza": "Q647282",
    "La traversata degli Appennini - Ricordo": "Q110404250",
    "La zingara": "Q464514",
    "Largo Mercatello a Napoli durante la peste del 1656.": "Q116533379",
    "Leda": "Q182019",
    "Liberazione di san Pietro": "Q2719737",
    "Madonna col Bambino e due angeli": "Q3842505",
    "Madonna con Bambino": "Q118314687",
    "Madonna con il Bambino in trono con i Santi Domenico e Gennaro (già Sant'Anselmo e Sant'Ugo o San Bruno)": "Q117834793",
    "Madonna del Divino amore": "Q96623678",
    "Madonna dell'Umiltà": "Q3949757",
    "Madonna dell'Umiltà con San Domenico e donatore": "Q117537719",
    "Martirio di sant'Orsola": "Q131675983",
    "Medea": "Q1982137",
    "Memento mori": "Q273383",
    "Morte di S. Giuseppe": "Q111609519",
    "Musici ambulanti": "Q12881271",
    "Natura morta con asparagi, pere e uova": "Q117829102",
    "Natura morta con testa di caprone": "Q19923762",
    "Pappagalli che si abbeverano ad un bacino di porfido rosso con gatto in agguato": "Q53998043",
    "Parabola dei ciechi": "Q1192570",
    "Pietà": "Q223689",
    "Ritorno del figliol prodigo": "Q117304805",
    "Ritratto della Principessa di Sant'Antimo": "Q117539703",
    "Ritratto di Canonico": "Q116974222",
    "Ritratto di Ferdinando IV": "Q19060568",
    "Ritratto di Galeazzo Sanvitale": "Q3937542",
    "Rivolta di Masaniello": "Q112666872",
    "Sacrificio di Ifigenia": "Q3795661",
    "Sacrificio di Isacco": "Q125775115",
    "San Gennaro nell'anfiteatro di Pozzuoli": "Q3947174",
    "San Girolamo nello studio": "Q131694288",
    "San Ludovico di Tolosa che incorona il fratello Roberto d'Angiò": "Q3947520",
    "San Michele Arcangelo": "Q3671312",
    "Sant'Alessio Morente": "Q16600212",
    "Santa Maria de Flumine": "Q112585763",
    "Sette opere di Misericordia": "Q15616133",
    "Sposalizio mistico di Santa Caterina": "Q133460762",
    "Tavola Strozzi": "Q3516299",
    "Templi di Paestum": "Q28020792",
    "Trasfigurazione di Cristo": "Q107273382",
    "ritratto di Paquio Proculo": "Q3399457",
    "tomba del Tuffatore": "Q464384"
}

# --- Funzione per ottenere il context associato a un'opera ---
def get_context_for_opera(opera, mappa_context):
    return mappa_context.get(opera.strip(), None)

# --- Funzione robusta per estrarre risposta da JSON ---
def estrai_risposta_chemidai(data):
    try:
        predictions = data.get("predictions", {})

        qa_output = predictions.get("qa_output", "")

        # Caso 1: risposta diretta come stringa
        if isinstance(qa_output, str):
            return qa_output.strip()

        # Caso 2: dict con "text"
        if isinstance(qa_output, dict):
            return qa_output.get("text", "").strip()

        # Caso 3: fallback: converte tutto in stringa e ripulisce
        return str(qa_output).strip()

    except Exception as e:
        print(f"[ERRORE ESTRAZIONE RISPOSTA]: {e}")
        return "Errore nell'estrazione"

# --- Pulizia di testo opzionale per confronti ---
def normalizza_testo(testo):
    testo = testo.lower()
    testo = re.sub(r'\s+', ' ', testo)
    testo = re.sub(r'[^\w\sàèéìòù]', '', testo)
    return testo.strip()

# --- Funzione per ottenere la risposta da Chemidai ---
def ottieni_risposta_chemidai(domanda, opera):
    context = get_context_for_opera(opera, mappa_context)
    if not context:
        print(f"[✗] Nessun context trovato per '{opera}'.")
        return None

    payload = {
        "input": domanda,
        "context": context,
        "debug": True,
        "non_intent": False
    }

    print(f"\n🔎 PAYLOAD INVIATO:\n{json.dumps(payload, indent=2, ensure_ascii=False)}")

    try:
        response = requests.post(url_chemidai, headers=headers_chemidai, data=json.dumps(payload), timeout=20)
        data = response.json()

        # Debug: mostra la risposta JSON intera
        print(f"\n RISPOSTA CHEMIDAI:\n{json.dumps(data, indent=2, ensure_ascii=False)}")

        risposta_estratta = estrai_risposta_chemidai(data)
        print(f" RISPOSTA ESTRATTA: {risposta_estratta}")
        return risposta_estratta

    except Exception as e:
        print(f"[ERRORE] Domanda '{domanda}' per '{opera}' - {e}")
        return None

# --- Percorsi file ---
file_input = "data/opere.csv"
file_output = "output/domande_risposte.csv"

# --- MAIN ---
def main():
    # Step 1: Trova opere uniche (debug/info opzionale)
    opere_uniche = set()
    with open(file_input, newline='', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            opere_uniche.add(row['opera'].strip())

    # Step 2: Elabora riga per riga e salva output
    with open(file_input, newline='', encoding='utf-8') as infile, open(file_output, mode='w', newline='', encoding='utf-8') as outfile:
        reader = csv.DictReader(infile)
        fieldnames = ['opera', 'domanda', 'risposta_llama', 'risposta_chemidai']
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()

        for row in reader:
            opera = row['opera'].strip()
            domanda = row['domanda']
            risposta_llama = row['risposta']
            context = get_context_for_opera(opera, mappa_context)

            print(f"\n Opera: {opera} | Context: {context} | Domanda: {domanda}")
            risposta_chemidai = ottieni_risposta_chemidai(domanda, opera)

            writer.writerow({
                'opera': opera,
                'domanda': domanda,
                'risposta_llama': risposta_llama,
                'risposta_chemidai': risposta_chemidai or "Nessuna risposta"
            })

            time.sleep(0.5)  # Rispetta limiti API

if __name__ == "__main__":
    main()
