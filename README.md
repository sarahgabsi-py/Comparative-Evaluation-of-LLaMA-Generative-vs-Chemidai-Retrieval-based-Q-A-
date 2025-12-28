# 📘 Comparative Evaluation of LLaMA (Generative) vs Chemidai (Retrieval‑based Q&A)
This project presents a complete evaluation pipeline comparing two fundamentally different language models:
- LLaMA → a generative large language model
- Chemidai → a retrieval‑based question‑answering suite
The evaluation focuses on domain‑specific questions about artworks, exploring how each model performs in terms of accuracy, relevance, completeness, fluency, informativeness, and response coverage. The project was developed during my internship at Logogramma S.r.l. as part of my Master’s Degree in Digital Humanities and Text Sciences.

# 🎯 Objective
The goal of this work is to analyze and compare the behavior of LLaMA and Chemidai when answering complex questions about cultural heritage. The evaluation aims to determine:
- which model answers more accurately
- which model provides more complete and informative responses
- how often each model refuses to answer
- how the two models behave when compared directly on the same question

# 📊 Dataset & Evaluation Samples
To ensure robustness and consistency, the evaluation was conducted on three separate annotated samples:
- 50 question–answer pairs
- 100 question–answer pairs
- 200 question–answer pairs
Each sample contains:
- the question
- LLaMA’s answer
- Chemidai’s answer
- manual annotations for 5 qualitative metrics
- a binary no_answer flag for coverage analysis
This multi‑sample approach allows the comparison to be tested across increasing dataset sizes, improving reliability and highlighting performance trends.

# 🧩 Methodology
1. Data Preparation
- Cleaning and normalization of the dataset
- Manual annotation of each response using a 0–2 scale
- Construction of a gold‑standard evaluation set

2. Metrics
Each response was evaluated on five qualitative metrics:
- Accuracy
- Relevance
- Completeness
- Fluency
- Informativeness
Additionally, a no_answer flag identifies cases where the model refuses to answer.

3. Analysis Pipeline
The analysis includes:
- descriptive statistics
- score distribution
- non‑response rate
- response pattern analysis (L, C, LC, Ø) L=Llama C=CHEMIDAI LC=Llama/CHEMIDAI Ø= neither of the two
- direct row‑by‑row comparison
- global win/tie/loss summary
All visualizations were generated using pandas, matplotlib, and seaborn.

# 🧠 Key Findings
Chemidai consistently outperforms LLaMA in accuracy, relevance, and fluency. LLaMA provides broader coverage and more elaborate responses, but with higher variability and more hallucinations. Chemidai is more selective (higher no‑answer rate), while LLaMA attempts to answer more often. In direct comparison across 330 metric evaluations, Chemidai wins the majority of cases.

# 🛠️ Technologies Used
- Python
- Pandas
- Seaborn
- Matplotlib
- CSV annotation workflow
