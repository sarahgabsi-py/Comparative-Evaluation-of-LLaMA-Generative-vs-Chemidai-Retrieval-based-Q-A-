#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""


@author: sarahgabsi
"""

import pandas as pd
import requests
import json
import time
import os




# URL dell'API
url = "https://api.example.com/endpoint"

# Intestazioni dell'API
headers = {
    'Content-Type': 'application/json',
    'Authorization': '"YOUR_API_TOKEN_HERE"'  # Rimosso per ragioni di riservatezza aziendale
}

# Carica il file CSV delle opere
file_path = '/file path'  
df_opere = pd.read_csv(file_path)
#print(df_opere.head())

# Pulizia delle virgolette e degli spazi bianchi
for column in df_opere.columns:
    if df_opere[column].dtype == 'object':
        df_opere[column] = df_opere[column].str.replace('"', '', regex=False)
        df_opere[column] = df_opere[column].str.replace(r'\s+', ' ', regex=True).str.strip()

# Dopo il caricamento del CSV
print(df_opere.head())  # Mostra le prime 5 righe del DataFrame

# Pulizia delle virgolette e degli spazi bianchi
for column in df_opere.columns:
    if df_opere[column].dtype == 'object':
        df_opere[column] = df_opere[column].str.replace('"', '', regex=False)
        df_opere[column] = df_opere[column].str.replace(r'\s+', ' ', regex=True).str.strip()

# Configurazione della funzione per inviare richieste con retry
MAX_RETRY = 5
INITIAL_BACKOFF = 2  

def invia_richiesta(payload):
    tentativi = 0
    backoff = INITIAL_BACKOFF
    while tentativi < MAX_RETRY:
        try:
            response = requests.post(url, headers=headers, data=json.dumps(payload), timeout=120)
            if response.status_code == 200:
                return response.json()
            elif response.status_code in [503, 504]:
                time.sleep(backoff)
                backoff *= 2
                tentativi += 1
            else:
                print(f"Errore {response.status_code}: {response.text}")
                return None
        except requests.exceptions.RequestException as e:
            time.sleep(backoff)
            backoff *= 2
            tentativi += 1

    print("Tentativi esauriti. Impossibile completare la richiesta.")
    return None

# Funzione per generare le domande
PROMPTS_DOMANDE = {
    'base': "Genera una domanda in italiano come se fossi un esperto d'arte. Il dato su cui generare la domanda è '{dato}' relativo all'opera '{opera}', realizzata da '{autore}', e alla sua {descrizione}.",
    'bambino': "Genera una domanda in italiano come se fossi un bambino di 6 anni. Il dato su cui generare la domanda è '{dato}' relativo all'opera '{opera}', fatta da '{autore}', e alla sua {descrizione}."
}

def genera_domande(row, tipo_prompt):   
    domande = []
    campi = {
        'w_name': 'nome dell\'opera',
        'a_name': 'autore',
        'start_date': 'anno di creazione',
        'loc_names': 'collocazione',
        'c_names': 'categorie',
        'd_names': 'descrizione',
        'e_names': 'eventi associati/contesto',
        'coll_names': 'collezioni',
        'g_names': 'materiali usati',
        'i_names': 'informazioni aggiuntive'
    }

    prompt_domanda = PROMPTS_DOMANDE.get(tipo_prompt, PROMPTS_DOMANDE['base'])

    for campo, descrizione in campi.items():
        if pd.notna(row.get(campo)):
            domanda_payload = {
                "max_tokens": 300,
                "messages": [{"content": prompt_domanda.format(dato=row[campo], opera=row['w_name'], autore=row['a_name'],data=row['start_date'],luogo=row['loc_names'],materiali=['g_names'],collezione=row['coll_names'],descrizione=descrizione), "role": "user"}],
                "model": "Meta-Llama-3_1-70B-Instruct",
                "temperature": 1.0
            }

            response = invia_richiesta(domanda_payload)
            if response:
                domanda = response['choices'][0]['message']['content']
                print(f"Domanda generata per {row['w_name']}: {domanda}")  # Stampa la domanda generata
                domande.append(domanda)
            else:
                print(f"Domanda non generata per {row['w_name']}.")

    return domande

# Prendi la prima riga del DataFrame
#riga_test = df_opere.iloc[0]
# Chiamata alla funzione per la prima riga con prompt "base"
#domande_generate = genera_domande(riga_test, "base")
#print("Domande generate:", domande_generate)

# Funzione per ottenere risposte
PROMPTS_RISPOSTA = {
    'base': """Sei un critico esperto d'arte che fornisce solo informazioni attendibili. 
    La domanda è: {domanda}. Rispondi in italiano e in modo accurato, attenendoti esclusivamente ai dati forniti. 
    Se nella domanda viene citata un'opera e un autore, verifica che l'associazione sia corretta rispetto alle informazioni che conosci.
    Se noti un errore nell'attribuzione dell'opera all'autore, specifica il dato corretto in modo chiaro.
    Se non conosci la risposta, rispondi onestamente e indica che non lo sai.""",
    
    'creativa': """Sei un artista creativo e informativo. 
    La domanda è: {domanda}. Rispondi in italiano e in modo interessante spiegando l'opera in maniera accurata. 
    Se nella domanda viene citata un'opera e un autore, verifica che l'associazione sia corretta rispetto alle informazioni disponibili. 
    Se noti un errore, correggilo educatamente nella tua risposta. 
    Se non conosci la risposta o sei indeciso, rispondi onestamente e fornisci un elenco di possibili opzioni basandoti su fonti attendibili."""
}

def ottieni_risposta(domanda, tipo_prompt):
    prompt_risposta = PROMPTS_RISPOSTA.get(tipo_prompt, PROMPTS_RISPOSTA['base'])
    risposta_payload = {
        "max_tokens": 800,
        "messages": [{"content": prompt_risposta.format(domanda=domanda), "role": "user"}],
        "model": "Meta-Llama-3_1-70B-Instruct",
        "temperature": 1.0
    }

    response = invia_richiesta(risposta_payload)
    return response['choices'][0]['message']['content'] if response else None

# Test della funzione
#domanda_test = "In che sala del Museo archeologico nazionale di Napoli possiamo trovare la famosa scultura in marmo raffigurante un fauno danzante?"
#tipo_prompt_test = "base"
#risposta = ottieni_risposta(domanda_test, tipo_prompt_test)
#print("Risposta ottenuta:", risposta)

# Funzione aggiornata per salvare domande, risposte e prompt completi
def salva_domande_e_risposte(df, tipo_prompt_domanda='base', tipo_prompt_risposta='base', output_file='output/domande_risposte.csv'):
    risultati = []

    for index, row in df.iterrows():
        domande = genera_domande(row, tipo_prompt_domanda)

        for domanda in domande:
            risposta = ottieni_risposta(domanda, tipo_prompt_risposta)

            prompt_domanda_completo = PROMPTS_DOMANDE[tipo_prompt_domanda].format(dato=row.get('dato', ''),opera=row['w_name'], autore=row['a_name'],data=row['start_date'],luogo=row['loc_names'],materiali=row['g_names'],collezione=row['coll_names'],descrizione=row.get('descrizione', ''))
            prompt_risposta_completo = PROMPTS_RISPOSTA[tipo_prompt_risposta].format(domanda=domanda)

            risultati.append({
                'opera': row['w_name'],
                'domanda': domanda,
                'risposta': risposta,
                'prompt_domanda': prompt_domanda_completo,
                'prompt_risposta': prompt_risposta_completo
            })
# Stampa alcuni dei risultati da salvare
    print(f"Risultati da salvare: {risultati[:5]}") 
    df_risultati = pd.DataFrame(risultati)

    try:
        df_risultati.to_csv(output_file, index=False, encoding="utf-8")
        print(f"File salvato con successo in: {output_file}")
    except Exception as e:
        print(f"Errore nel salvataggio del file: {e}")

# Salva le domande e risposte
print("Inizio generazione domande e risposte...")
salva_domande_e_risposte(df_opere, tipo_prompt_domanda='base', tipo_prompt_risposta='base', output_file='output/domande_risposte.csv')
print("Funzione di salvataggio completata.")

# Verifica che il file sia stato creato
if os.path.exists('output/domande_risposte.csv'):
    print("Il file è stato creato correttamente!")
else:
    print("Il file non è stato creato.")



