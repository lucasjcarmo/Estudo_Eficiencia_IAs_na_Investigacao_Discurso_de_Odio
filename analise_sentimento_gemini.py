"""
Classificação de sentimento de comentários usando Gemini (Google).

Requisitos:
    pip install pandas google-genai

Uso:
    "Via cmd"
    python analise_sentimento_gemini.py entrada.csv saida_gemini.csv
"""

import sys
import json
import time
import pandas as pd
from google import genai
import os
from prompt_comum import montar_prompt
os.environ["GEMINI_API_KEY"] = "...."
# ---------------------------------------------------------------------------
# CONFIGURAÇÃO
# ---------------------------------------------------------------------------

COLUNA_COMENTARIO = "NOME_CANDITADO"
MODELO = "gemini-2.5-pro"  # ajuste para a versão exata avaliada no protocolo
PAUSA_ENTRE_CHAMADAS = 1.0

client = genai.Client()  # usa GEMINI_API_KEY do ambiente


# ---------------------------------------------------------------------------
# CHAMADA AO LLM
# ---------------------------------------------------------------------------

def classificar_comentario(comentario: str) -> dict:
    """Envia o comentário ao Gemini e retorna 'categoria' e 'justificativa'."""
    prompt = montar_prompt(comentario)

    try:
        resposta = client.models.generate_content(
            model=MODELO,
            contents=prompt,
            config={"temperature": 0},  # determinístico, para comparação justa entre modelos
        )

        texto_resposta = resposta.text.strip()
        texto_resposta = texto_resposta.replace("```json", "").replace("```", "").strip()

        resultado = json.loads(texto_resposta)

        if resultado.get("categoria") not in (1, -1, 0):
            raise ValueError(f"Categoria inválida retornada: {resultado.get('categoria')}")

        return {
            "categoria": resultado["categoria"],
            "justificativa": resultado.get("justificativa", "")
        }

    except Exception as e:
        return {
            "categoria": 0,
            "justificativa": f"Erro ao classificar: {e}"
        }


# ---------------------------------------------------------------------------
# PROCESSAMENTO DO CSV
# ---------------------------------------------------------------------------

def processar_csv(caminho_entrada: str, caminho_saida: str):
    df = pd.read_csv(caminho_entrada)

    if COLUNA_COMENTARIO not in df.columns:
        raise ValueError(
            f"Coluna '{COLUNA_COMENTARIO}' não encontrada no CSV. "
            f"Colunas disponíveis: {list(df.columns)}"
        )

    categorias, justificativas = [], []
    total = len(df)

    for i, comentario in enumerate(df[COLUNA_COMENTARIO], start=1):
        print(f"[Gemini] Classificando comentário {i}/{total}...")

        if pd.isna(comentario) or str(comentario).strip() == "":
            categorias.append(0)
            justificativas.append("Comentário vazio")
            continue

        resultado = classificar_comentario(str(comentario))
        categorias.append(resultado["categoria"])
        justificativas.append(resultado["justificativa"])

        time.sleep(PAUSA_ENTRE_CHAMADAS)

    df["categoria"] = categorias
    df["justificativa"] = justificativas

    df.to_csv(caminho_saida, index=False, encoding="utf-8-sig")
    print(f"\nConcluído. Resultado salvo em: {caminho_saida}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Uso: python analise_sentimento_gemini.py entrada.csv saida_gemini.csv")
        sys.exit(1)

    processar_csv(sys.argv[1], sys.argv[2])
