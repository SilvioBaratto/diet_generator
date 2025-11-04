class TipoPasto {
  tipo "colazione" | "pranzo" | "cena" | "spuntino"
  orario string? @description("Orario opzionale del pasto, ad esempio '08:00'")
  ricetta string @description(#"
    Ricetta dettagliata per il pasto
  "#)
}

class Ingrediente {
  nome string @description("Nome dell'ingrediente")
  quantita float @description("Quantità necessaria dell'ingrediente")
  unita string @description("Unità di misura, ad esempio grammi, ml, pezzi")
}

class Pasto {
  tipoPasto TipoPasto
  ingredienti Ingrediente[]
  calorie int @description("Calorie stimate per questo pasto")
}

class DietaSettimanale {
  nome string
  dataInizio string @description("Data di inizio nel formato AAAA-MM-GG")
  dataFine string @description("Data di fine nel formato AAAA-MM-GG")
  pasti Pasto[] @description("Elenco completo dei pasti previsti per la settimana")
}

function GeneraDietaSettimanale(
  dataInizio: string,
  peso: float,
  altezza: float,
  obiettivo: string,
  altri_dati: string
) -> DietaSettimanale {
  client DietModel
  prompt #"
    Genera un piano alimentare settimanale personalizzato basato sui dati antropometrici e obiettivi dell'utente.

    - Calcola il fabbisogno calorico giornaliero in base a peso, altezza e obiettivo
    - Distribuisci i pasti su 7 giorni: colazione, pranzo, cena e 2 spuntini per ogni giorno
    - Varia gli ingredienti giornalmente per garantire equilibrio nutrizionale
    - Rispetta le preferenze alimentari e restrizioni indicate in "Altri Dati"
    - Specifica ingredienti con quantità precise e unità di misura (grammi, ml, pezzi)
    - Fornisci calorie stimate per ogni pasto
    - Includi ricette dettagliate per ogni tipologia di pasto

    {{ ctx.output_format }}

    {{ _.role("user") }}

    Data inizio: {{ dataInizio }}
    Peso: {{ peso }} kg
    Altezza: {{ altezza }} cm
    Obiettivo: {{ obiettivo }}
    Altri Dati: {{ altri_dati }}
  "#
}

class ListaSpesa {
  ingredienti Ingrediente[] @description("Elenco aggregato di tutti gli ingredienti da acquistare per l'intera settimana, con quantità sommate e unità di misura coerenti")
}

function GeneraListaSpesa(
  pasti: Pasto[]
) -> ListaSpesa {
  client ReceipeModel
  prompt #"
    Genera una lista della spesa aggregata per l'intera settimana a partire dai pasti forniti.

    - Aggrega tutti gli ingredienti dei pasti forniti
    - Somma le quantità degli ingredienti identici
    - Mantieni l'unità di misura originale per ogni ingrediente
    - Ordina alfabeticamente la lista finale per nome ingrediente
    - Elimina duplicati assicurandoti che ogni ingrediente compaia una sola volta
    - Arrotonda le quantità a valori pratici per la spesa (es. 520g → 500g)

    {{ ctx.output_format(prefix="Formato JSON di risposta:") }}

    {{ _.role("user") }}

    Ingredienti dai pasti settimanali:
    {% for pasto in pasti %}
      {% for ingrediente in pasto.ingredienti %}
        - {{ ingrediente.nome }}: {{ ingrediente.quantita }} {{ ingrediente.unita }}
      {% endfor %}
    {% endfor %}
  "#
}

class HtmlStructure {
  h1 string 
  h2 string[]
  p string[] 
  ul string[] 
  ol string[] 
}

function GeneraRicetta(
  pasto: Pasto
) -> HtmlStructure {
  client ReceipeModel
  prompt #"
    Crea una ricetta dettagliata e appetitosa utilizzando esclusivamente gli ingredienti forniti nel pasto.

    - Utilizza SOLO gli ingredienti elencati senza aggiungerne altri
    - Struttura la ricetta in modo chiaro e accessibile anche per principianti
    - Fornisci istruzioni passo-passo numerate e sequenziali
    - Indica tempi di preparazione e cottura stimati
    - Suggerisci tecniche di cottura appropriate per il momento della giornata
    - Usa un tono amichevole e incoraggiante

    {{ ctx.output_format(prefix="Formato di html:") }}

    {{ _.role("user") }}

    Tipo di pasto: {{ pasto.tipoPasto.tipo }}
    Nome ricetta: {{ pasto.tipoPasto.ricetta }}

    Ingredienti disponibili:
    {% for ingrediente in pasto.ingredienti %}
      - {{ ingrediente.nome }}: {{ ingrediente.quantita }} {{ ingrediente.unita }}
    {% endfor %}
  "#
}