#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep  9 16:33:06 2025

@author: sarahgabsi
"""

"""
Script di analisi per il task di valutazione LLaMA vs Chemidai.
Il dataset originale non è incluso nella repository per motivi di riservatezza.
Questo script mostra la pipeline di analisi, metriche e visualizzazioni.
"""



#TASK DI VALUTAZIONE
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import csv
sns.set(style="whitegrid", context="talk")
plt.rcParams["figure.figsize"] = (10, 6)


#STEP 1 CARICO IL CAMPIONE ANNOTATO
df = pd.read_csv("campione_200_annotato.csv", sep=';',quotechar='"',encoding='utf-8', engine='python')
df.columns = df.columns.str.strip()
#VERIFICO COME SI PRESENTA IL CAMPIONE
print("Colonne:", df.columns.tolist())
print("Valori unici in no_answer_LLaMA:", df['no_answer_LLaMA'].unique())
print("Valori unici in no_answer_Chemidai:", df['no_answer_Chemidai'].unique())
print(df.head(6))
print(df[["acc_LLaMA", "pert_LLaMA", "comp_LLaMA", "flu_LLaMA", "info_LLaMA"]].head(20))



#pulizia colonne no_answer dai possibili spazi e caratteri strani
for col in ['no_answer_LLaMA','no_answer_Chemidai']:
    df[col] = df[col].astype(str).str.strip()  # rimuovo spazi
    df[col] = pd.to_numeric(df[col], errors='coerce')  # converto in numerico
    df[col] = df[col].replace(2, pd.NA)  # sostituisco 2 con NA


# conversione  colonne numeriche
numeric_cols = ["acc_LLaMA", "pert_LLaMA", "comp_LLaMA", "flu_LLaMA", "info_LLaMA",
                "acc_Chemidai", "pert_Chemidai", "comp_Chemidai", "flu_Chemidai", "info_Chemidai"]
df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric, errors='coerce')


# rimuovo righe che hanno NaN in colonne chiave
df = df.dropna(subset=['no_answer_LLaMA', 'no_answer_Chemidai'] + numeric_cols)

# pulizia colonne stringa (solo quelle oggetto)
str_cols = df.select_dtypes(include='object').columns
df[str_cols] = df[str_cols].applymap(lambda x: x.strip() if isinstance(x, str) else x)



# Verifica
print(df[['no_answer_LLaMA','no_answer_Chemidai']].head(20))
print(df['no_answer_LLaMA'].unique())
print(df['no_answer_Chemidai'].unique())

print(df.isna().sum())
print(df.count())

#STEP 2:ANALISI DISTRIBUTIVA ED EVENTUALE PULIZIA DATI
# 1. Conto quanti valori NaN ci sono in ogni colonna
print("\n Conteggio valori NaN per colonna:")
print(df.isna().sum())
# 2. Visualizzo solo le colonne che hanno almeno un NaN
print("\n Colonne con almeno un NaN:")
print(df.isna().sum()[df.isna().sum() > 0])
print(df.shape)
print(df.info())


#STEP 3:ANALISI SATTISTICA DI BASE: MEDIA, DEVIAZIONE STANDARD, MINIMO E MASSIMO PER OGNI METRICA E MODELLO SU TUTTE LE RIGHE 
# 2.1 — Definisco liste utili
metriche = ["acc", "pert", "comp", "flu", "info"]
modelli = ["LLaMA", "Chemidai"]
print("\n Statistiche descrittive per ciascun modello e metrica:")
for modello in modelli:
    print(f"\n--- {modello} ---")
    for m in metriche:
        col = f"{m}_{modello}"
        serie = df[col]
        media = serie.mean()
        std = serie.std()
        minimo = serie.min()
        massimo = serie.max()
        print(f"{m}: media={media:.2f}, std={std:.2f}, min={minimo}, max={massimo}")

#.CREAZIONE DI UNA BAR CHAR: MEDIA PER METRICA E MODELLO 
# Creo una lista di dizionari con le medie per ogni metrica e modello
media_data = []
for modello in modelli:
    for m in metriche:
        col = f"{m}_{modello}"
        media_data.append({
            "modello": modello,
            "metrica": m,
            "media": df[col].mean()
        })

# Converto in DataFrame per visualizzazione
media_df = pd.DataFrame(media_data)

# Grafico a barre
sns.barplot(data=media_df, x="metrica", y="media", hue="modello", palette=["#00bfff", "#e440a2"])
plt.title("Media dei punteggi per metrica e modello")
plt.ylabel("Media (0–2)")
plt.ylim(0, 2)
plt.legend(title="Modello")
plt.tight_layout()
plt.show()


#CALCOLO LA DISTRIBUZIONE DEI PUNTEGGI PER VEDERE QUANTI PUNTEGGI 0,1,2 ci sono per ogni metrica
print("\n Distribuzione dei punteggi (conteggio 0, 1, 2):")
for modello in modelli:
    print(f"\n--- {modello} ---")
    for m in metriche:
        col = f"{m}_{modello}"
        distribuzione = df[col].value_counts().sort_index()
        print(f"{m}:\n{distribuzione.to_string()}")
        

#GRAFICO A BARRE: DISTRIBUZIONE DEI PUNTEGGI(0, 1, 2)
# Creo una lista di dizionari con la distribuzione dei punteggi
distribuzione_data = []
for modello in modelli:
    for m in metriche:
        col = f"{m}_{modello}"
        distribuzione = df[col].value_counts().sort_index()
        for punteggio, conteggio in distribuzione.items():
            distribuzione_data.append({
                "modello": modello,
                "metrica": m,
                "punteggio": punteggio,
                "conteggio": conteggio
            })

# Converto in DataFrame
distribuzione_df = pd.DataFrame(distribuzione_data)

# Grafico a barre raggruppato
sns.catplot(
    data=distribuzione_df,
    x="metrica", y="conteggio", hue="punteggio", col="modello",
    kind="bar", palette="Set1", height=5, aspect=1.2
)
plt.subplots_adjust(top=0.85)
plt.suptitle("Distribuzione dei punteggi (0, 1, 2) per metrica e modello")
plt.show()


# STEP 4 — Comportamento globale: tassi di non-risposta e pattern
#Obiettivo: misurare quanto spesso ciascun modello si astiene e come si combinano i comportamenti.
#Perché? La copertura è fondamentale quanto la qualità.

#calcolo la media dei valori 1 (cioè no_answer di entrambi i modelli)
rate_na_llama = (df["no_answer_LLaMA"] == 1).mean()
rate_na_chemidai = (df["no_answer_Chemidai"] == 1).mean()


print("\n Tasso di non-risposta:")
print(f"LLaMa: {rate_na_llama*100:.1f}%") #Moltiplica la media per 100 per ottenere la percentuale .1f=mostra solo una cifra decimale
print(f"Chemidai:{rate_na_chemidai*100:.1f}%")

#GRAFICO A BARRE DEL TASSO DI NON RISPOSTA
tasso_df= pd.DataFrame({
    "Modello":["LLaMA","Chemidai"],
    "Tasso di non risposta(%)":[rate_na_llama*100,rate_na_chemidai*100]
})

sns.barplot(data=tasso_df,x="Modello",y="Tasso di non risposta(%)",palette=["#00bfff", "#e440a2"])
plt.title("Tasso di non risposta per modello")
plt.ylabel("Percentuale(%)")
plt.ylim(0,100)
plt.tight_layout()
plt.show()


#CALCOLO I PATTERN COMBINATI DI RISPOSTA NO_ANSWER=0 ----> risposta data

#definisco una funzione che costruisce ipattern per ogni riga
def pattern_risposta(r):
    l = "L" if r["no_answer_LLaMA"] == 0 else""
    c = "C" if r["no_answer_Chemidai"]== 0 else ""
    return l + c if (l or c) else "Ø" # Ø = nessuno ha risposto

#applico la funzione ad ogni rifa
df["pattern_risposta"]= df.apply(pattern_risposta, axis=1)

#conteggio dei pattern
print("\n Pattern di risposta (conteggi):")
print(df["pattern_risposta"].value_counts())

#percentuali dei pattern
print("\n Pattern di risposta (percentuali):")
print((df["pattern_risposta"].value_counts(normalize=True)*100).round(1))

#Questo mostra quante volte ho avuto(sia in percentuale che in conteggio):
#"LC" → entrambi hanno risposto
#"L" → solo LLaMA
#"C" → solo Chemidai
#"Ø" → nessuno ha risposto

# GRAFICO A BARRE DEI PATTERN
pattern_counts = df["pattern_risposta"].value_counts().reset_index()
pattern_counts.columns = ["pattern", "conteggio"]

sns.barplot(data=pattern_counts, x="pattern", y="conteggio", palette=["#00bfff", "#e440a2", "#FFD700", "#999999"])
plt.title("Distribuzione dei pattern di risposta")
plt.ylabel("Numero di occorrenze")
plt.xlabel("Pattern")
plt.tight_layout()
plt.show()


#STEP 5: CONFRONTO DIRETTO: Finora ho analizzato qualità media e copertura. 
#Adesso  misuro prestazioni comparative
#Voglio misurare: 
# - Quante volte Chemidai batte LLaMA (Win Llama)
# - Quante volte LLaMA batte Chemidai (Win Chemidai)
# - Quante volte pareggiano (Tie)


df_confronto= df[df["pattern_risposta"]== "LC"] #filtro solo le righe dove entrambi hanno risposto cosi evito di confrontare una risposta con un'assenza

def confronto_riga(r,metrica): #Funzione per confrontare i punteggi riga per riga
    val_llama=r[f"{metrica}_LLaMA"]
    val_chemidai= r[f"{metrica}_Chemidai"]
    if val_chemidai > val_llama:
        return "Win Chemidai"
    elif val_llama > val_chemidai:
        return "Win LLaMA"
    else:
        return "Tie"
        
#applico la funzione per ogni metrica
risultati_confronto={}

for metrica in ["acc","pert","comp","flu","info"]:
    colonna = f"confronto_{metrica}"
    df_confronto[colonna]= df_confronto.apply(lambda r: confronto_riga(r, metrica), axis=1)
    
    #conteggio risultati
    conteggio = df_confronto[colonna].value_counts()
    risultati_confronto[metrica]= conteggio
    
print("\n Confronto diretto tra modelli (Win/Tie/Loss):")
for metrica, conteggio in risultati_confronto.items():
    print(f"\n {metrica.upper()}")
    print(conteggio.to_string())
    
   
#STEP 6: VISIONE GLOBALE DEL CONFRONTO TRA MODELLI     

#Riepilogo globale delle vittorie ---> chi ha vinto più spesso in totale
totali = {"Win Chemidai": 0, "Win LLaMA": 0, "Tie": 0} # Inizializzo contatori globali

for metrica, conteggio in risultati_confronto.items():
    for categoria in ["Win Chemidai", "Win LLaMA", "Tie"]:
        totali[categoria] += conteggio.get(categoria, 0)

print("\nRiepilogo globale delle vittorie:")
for k, v in totali.items():
    print(f"{k}: {v}")

#COSTRUISCO IL DATAFRAME PER IL GRAFICO    
riepilogo_df = pd.DataFrame([
    {"Categoria": "Win Chemidai", "Conteggio": totali["Win Chemidai"]},
    {"Categoria": "Win LLaMA", "Conteggio": totali["Win LLaMA"]},
    {"Categoria": "Tie", "Conteggio": totali["Tie"]}
])

#GRAFICO FINALE
sns.barplot(data=riepilogo_df, x="Categoria", y="Conteggio", palette=["#e440a2", "#00bfff", "#999999"])
plt.title("Confronto globale tra modelli")
plt.ylabel("Numero di vittorie")
plt.tight_layout()
plt.show()

 
   
    