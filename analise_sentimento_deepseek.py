"""
Classificação de sentimento de comentários usando DeepSeek.

A API do DeepSeek é compatível com o formato da API da OpenAI,
por isso reutiliza-se o mesmo cliente (openai), apontando para
o endpoint (base_url) do DeepSeek.

Requisitos:
    pip install pandas openai

Uso:
    export DEEPSEEK_API_KEY="sk-2fbdc0583c784405ad04856f50c5cb26"
    python analise_sentimento_deepseek.py entrada.csv saida_deepseek.csv
"""

import os
import sys
import json
import time
import pandas as pd
from openai import OpenAI

from prompt_comum import montar_prompt


# ---------------------------------------------------------------------------
# CONFIGURAÇÃO
# ---------------------------------------------------------------------------

COLUNA_COMENTARIO = "BOULOS"
MODELO = "deepseek-chat"  # ajuste para a versão exata avaliada no protocolo
PAUSA_ENTRE_CHAMADAS = 1.0

client = OpenAI(
    api_key=".....",
    base_url="https://api.deepseek.com",
)


# ---------------------------------------------------------------------------
# CHAMADA AO LLM
# ---------------------------------------------------------------------------

def classificar_comentario(comentario: str) -> dict:
    """Envia o comentário ao DeepSeek e retorna 'categoria' e 'justificativa'."""
    prompt = montar_prompt(comentario)

    try:
        resposta = client.chat.completions.create(
            model=MODELO,
            messages=[{"role": "user", "content": prompt}],
            temperature=0,  # determinístico, para comparação justa entre modelos
        )

        texto_resposta = resposta.choices[0].message.content.strip()
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
        print(f"[DeepSeek] Classificando comentário {i}/{total}...")

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
        print("Uso: python analise_sentimento_deepseek.py entrada.csv saida_deepseek.csv")
        sys.exit(1)

    processar_csv(sys.argv[1], sys.argv[2])
