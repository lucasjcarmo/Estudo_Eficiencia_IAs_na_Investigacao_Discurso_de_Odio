import sys
import json
import time
import pandas as pd
import anthropic
import os
from prompt_comum import montar_prompt
os.environ["ANTHROPIC_API_KEY"] = "...."
# ---------------------------------------------------------------------------
# CONFIGURAÇÃO
# ---------------------------------------------------------------------------

COLUNA_COMENTARIO = "BOULOS"
MODELO = "claude-sonnet-5"  # ajuste para a versão exata avaliada no protocolo
PAUSA_ENTRE_CHAMADAS = 1.0

client = anthropic.Anthropic()  # usa ANTHROPIC_API_KEY do ambiente


# ---------------------------------------------------------------------------
# CHAMADA AO LLM
# ---------------------------------------------------------------------------

def classificar_comentario(comentario: str) -> dict:
    """Envia o comentário ao Claude e retorna 'categoria' e 'justificativa'."""
    prompt = montar_prompt(comentario)

    try:
        resposta = client.messages.create(
            model=MODELO,
            max_tokens=16000,
            #thinking={"type": "disabled"},
            messages=[{"role": "user", "content": prompt}],
        )

        texto_resposta = resposta.content[0].text.strip()
        texto_resposta = texto_resposta.replace("```json", "").replace("```", "").strip()

        resultado = json.loads(texto_resposta)

        if resultado.get("categoria") not in (1, -1, 0):
            raise ValueError(f"Categoria inválida retornada: {resultado.get('categoria')}")

        return {
            "categoria": resultado["categoria"],
            "justificativa": resultado.get("justificativa", ""),
        }

    except Exception as e:
        #os._exit(0)
        return {
            "categoria": -2,
            "justificativa": f"Erro ao classificar: {e}",
            
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

    j=0
    for i, comentario in enumerate(df[COLUNA_COMENTARIO], start=1):
        print(f"[Claude] Classificando comentário {i}/{total}...")

        if pd.isna(comentario) or str(comentario).strip() == "":
            categorias.append(0)
            justificativas.append("Comentário vazio")
            continue

        resultado = classificar_comentario(str(comentario))
        categorias.append(resultado["categoria"])
        justificativas.append(resultado["justificativa"])
        df.loc[i,'categoria'] = categorias[j]
        df.loc[i,'justificativa'] = justificativas[j]
        j+=1
        if(resultado["categoria"] == -2):
            print("Aconteceu algum erro, verifique")
            break;

        time.sleep(PAUSA_ENTRE_CHAMADAS)
        

    df.to_csv(caminho_saida, index=False, encoding="utf-8-sig")
    print(f"\nConcluído. Resultado salvo em: {caminho_saida}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Uso: python analise_sentimento_claude.py entrada.csv saida_claude.csv")
        sys.exit(1)

    processar_csv(sys.argv[1], sys.argv[2])
