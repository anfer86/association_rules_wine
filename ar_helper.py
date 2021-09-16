import numpy as np
import pandas as pd
from apyori import apriori

from collections import namedtuple
Rule = namedtuple('Rule', ('antecedent', 'consequent', 'support', 'support_antecedent', 'confidence', 'lift'))

def get_rules(df, min_support=0.10, min_confidence=0.8, min_lift=1.5, max_length=2, pre_text_groups = None, groups = None):    
    # To trasnform df to a set of transactions
    t = []
    for id in df.id.unique():
        t.append(list(df[df.id == id].item.values))
    # To run association rules algorithm
    arules = apriori(t, min_support = min_support, min_confidence = min_confidence, min_lift = min_lift, max_length = max_length)
    # To extract the rules from the native format, records.
    from ar_helper import get_all_rules_from_relation_records
    rules = get_all_rules_from_relation_records( list(arules) )      
    # To create a data frame from rules 
    df = pd.DataFrame(rules)
    from ar_helper import rules_to_str, rules_to_html
    # To extract abusolute values of covering
    if ( len(df) > 0):
        df['n_transactions'] = len(t)
        df['n_support_antecedent'] = (df['support_antecedent'] * len(t)).astype(int)    
        df['n_confidence'] = (df['support_antecedent'] * df['confidence'] * len(t)).astype(int)
        # To extract the string format of the rules    
        df['str'] = rules_to_str(rules, pre_text_groups, groups)
        # To extract the html format of the rules    
        df['html'] = rules_to_html(df, pre_text_groups, groups)
        #df['scl_rank_sum'] = df['support_antecedent'].rank() + df['confidence'].rank() + df['lift'].rank()

    return df


def get_all_rules_from_relation_records ( records ):    
    rules = []    
    for record in records:
        print(record)
        for rule in get_all_rules_from_relation_record(record):
            rules.append(rule)    
    return rules

def rule_to_str (rule, pre_text_groups = None, groups = None):    
    antecedente_str = ', '.join(rule.antecedent)
    consequente_str = ', '.join(rule.consequent)
    text_group = ' '
    if groups:
        text_group += ' '.join([pre_text_groups[i] + groups[i] for i in range(len(groups)) ]) + ' '
    rule_str =  '{:.0%}{}responderam que <b>{}</b>, dos quais {:.0%} também responderam que <b>{}</b>' \
                .format(                    
                    rule.support_antecedent,
                    text_group,
                    antecedente_str,
                    rule.confidence,
                    consequente_str,
                )                
    return rule_str

def rule_to_html (rule, pre_text_groups = None, groups = None):    
    antecedente_str = ', '.join(rule.antecedent)
    consequente_str = ', '.join(rule.consequent)    
    
    # Parte 1: antecedente grupo selecionado (se houver)
    text_group = "<span class='rule_grupo'>Geral</span>: "
    if groups:
        text_group = "Grupo <span class='rule_grupo'>" + ' - '.join(groups) + '</span>: '    
    # Parte 2: percentual e valor absoluto do antecedente   
    text_antecedente_p = "<span class='rule_ant_perc'>{:.0%}</span><span class='rule_ant_frac'>({}/{})</span> ".format(rule.support_antecedent, str(rule.n_support_antecedent), str(rule.n_transactions) )
    # Parte 3: antecedente
    text_antecedente_str = "responderam que <span class='rule_ant_str'>{}</span>, dos quais ".format(antecedente_str)
    # Parte 4: percentual do antecedente
    text_consequente_p = "<span class='rule_con_perc'>{:.0%}</span><span class='rule_con_frac'>({}/{})</span>".format(rule.confidence, str(rule.n_confidence), str(rule.n_support_antecedent) )
    text_consequente_str = " também responderam que <span class='rule_con_str'>{}</span>.".format(consequente_str)
    # Parte 3:
    rule_str = text_group + text_antecedente_p + text_antecedente_str + text_consequente_p + text_consequente_str
    return rule_str

def rules_to_html(df_rules, pre_text_groups = None, groups = None):
    return df_rules.apply( lambda x : rule_to_html(x, pre_text_groups, groups), axis = 1 )

def rules_to_str(rules, pre_text_groups = None, groups = None):
    return [rule_to_str(rule, pre_text_groups, groups) for rule in rules]


def get_all_rules_from_relation_record( record ):
    rules = []    
    for item_rule in record.ordered_statistics:
        rule = Rule(
            item_rule.items_base,
            item_rule.items_add,
            record.support,            
            item_rule.support_base,
            item_rule.confidence,
            item_rule.lift
        )
        rules.append(rule)
    return rules;