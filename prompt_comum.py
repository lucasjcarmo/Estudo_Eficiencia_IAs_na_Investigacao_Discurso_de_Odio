"""
Módulo compartilhado: contém o prompt único de classificação de sentimento,
utilizado por todos os scripts (OpenAI, Claude, Gemini, DeepSeek).

Manter o prompt centralizado aqui garante que todos os modelos comparados
recebam exatamente a mesma instrução — requisito importante para a validade
da comparação entre LLMs no protocolo da pesquisa.
"""


def montar_prompt(comentario: str) -> str:
    """Monta o prompt enviado ao LLM para classificar o sentimento do comentário."""
    return f"""Classifique o sentimento do comentário abaixo em uma das três categorias:

1  -> sentimento positivo
-1 -> sentimento negativo
0  -> neutro ou sem sentimento

Considere o contexto político e a língua portuguesa, incluindo ironia, sarcasmo,
emojis e onomatopeias (ex.: "kkk") como pistas para a classificação.

Responda APENAS em formato JSON, sem texto adicional, seguindo exatamente este formato:
{{"categoria": <1, -1 ou 0>, "justificativa": "<explicação breve em até 20 palavras>"}}

Comentário: "{comentario}"
"""
