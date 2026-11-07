# IMPORTANDO BIBLIOTECAS
import pandas as pd
import os
from openai import OpenAI
#nunes a ordem esta trocada
# LENDO ARQUIVO EXCEL
# for C: or any  system operation its the data excel\directory\archive.xlsx (some, if take other extension, it's not work) 
# or /home/directory/archive.xlsx it's the same 
file_path = r'/home/lucas-jose/Desktop/IC_26/Recomeço/Pablo Marçal/tabata3.xlsx'
# TRANSFORMANDO EM ESTRUTURA PANDAS
df = pd.read_excel(file_path)
count = 1;
for index, row in df.iterrows():
    for i in range(len(df.columns)):
        if df.columns[i] == "NOME_CANDITADO":
            resultado = ''
            frase = str(row[i])
            print(frase)

            # DEFININDO A CHAVE DE ACESSO AO CHATGPT
            client = OpenAI(api_key="....")

            # FORMANDO A ESTRUTURA DA FRASE DE COMUNICAÇÃO COM O CHATGPT
            response = client.chat.completions.create(
                model="gpt-5", # gpt-5.5
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Você é um especialista em análise de sentimentos."
                            "Classifique o comentário em apenas uma das três categorias abaixo. Definições:"
                            "1  -> sentimento positivo"
                            "-1 -> sentimento negativo"
                            "0  -> neutro ou sem sentimento"
                            "Considere o contexto político e a língua portuguesa, incluindo ironia, sarcasmo, emojis e onomatopeias (ex.: kkk) como pistas para a classificação."
                            "Retorne  um dos seguintes valores: -1 ou 0 ou 1 e coloque dois espaços em branco antes explicar de forma resumida"
                        )
                    },
                    {
                        "role": "user",
                        "content": frase
                    }
                ],
            )

            resultado = str(response.choices[0].message.content)
            capturar_resultado = resultado.split("  ")
            

            df.loc[index, 'Classificacao'] = capturar_resultado[0]
            df.loc[index, 'Resposta'] = capturar_resultado[1]
            df.to_excel(file_path, index=False)

print('Processamento e análise realizados com sucesso.')
 
