import numpy as np
import pandas as pd

from ar_helper import get_rules

print('Criando as tabelas para extração de regras...', end='')
df = pd.read_csv('wine_dados.csv', encoding='UTF-8')
to_drop = ["Carimbo de data/hora","Você reside na região da Serra Catarinense?"]
df = df.drop(to_drop,axis=1)
df = df.reset_index()
df = pd.melt(df.reset_index(), id_vars = ['index'], value_vars = df.columns[1:],var_name='pergunta', value_name='resposta')
df.rename(columns={'index' : 'id'}, inplace=True)

# Pré-processamento de respostas
# Transformar de 5 para 3
to_replace = {
    'Muito importante' : 'Importante ou muito importante',
    'Importante' : 'Importante ou muito importante',
    'Nada importante' : 'Nada ou pouco importante',
    'Pouco importante' : 'Nada ou pouco importante',
    'Sempre' : 'Muitas vezes ou sempre',
    'Muitas vezes' : 'Muitas vezes ou sempre',
    'Nunca' : 'Nunca ou raramente',
    'Raramente' : 'Nunca ou raramente',
}
df['resposta'].replace(to_replace=to_replace, inplace=True)
df['item'] = df['pergunta'] + " " + df['resposta']
df.to_csv('partial.csv')

rules = get_rules(df, min_support=0.20, min_confidence=0.4, min_lift=1.3, max_length=2)

rules[["support","support_antecedent","confidence","lift"]] = rules[["support","support_antecedent","confidence","lift"]].round(2)
rules.to_csv('regras.csv', decimal=",")
rules.to_json('regras.json', orient="records")

print(len(rules))
exit()

print('Regras de Campus')
for campus in df1.campus.unique():   
    df_campus = df[ df.id.isin( df1[df1.campus == campus].token.values )]
    rules = get_rules(df_campus, min_support=0.20, min_confidence=0.8, min_lift=2.5, max_length=2, pre_text_groups= [''], groups=[campus])
    df_all_rules = pd.concat([df_all_rules,rules])

print('Regras de Campus / Curso')
for campus in df1.campus.unique():   
    df1_campus = df1[df1.campus == campus]
    for curso in df1_campus.curso.unique():
        df_campus_curso = df[ df.id.isin( df1_campus[df1_campus.curso == curso].token.values )]
        rules = get_rules(df_campus_curso, min_support=0.20, min_confidence=0.8, min_lift=2.5, max_length=2, pre_text_groups = ['de ','de '], groups=[campus, curso])
        df_all_rules = pd.concat([df_all_rules,rules])

df_all_rules[['html','support_antecedent','confidence','lift']].to_csv('alunos_ar_rules.csv', index=False, sep=';')
print('Regras: ' + str(len(df_all_rules)))