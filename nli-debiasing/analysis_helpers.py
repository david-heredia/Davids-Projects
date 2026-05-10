import json
from typing import Dict, List

import numpy as np
import pandas as pd
from scipy import stats

from nltk import word_tokenize
import datasets

from tqdm import tqdm

def get_vocab_class_counts(dataset: str, split: str = 'train') -> Dict:
    if dataset.endswith('.json') or dataset.endswith('.jsonl'):
        with open(dataset, 'r') as file:
            data = [json.loads(line) for line in file]
    else:
        data = datasets.load_dataset(dataset, split=split)
        data = data.to_iterable_dataset()

    # get vocabulary and count of how many examples include each token for each class (entail, neutral, contradict)
    vocab_class_counts = dict()
    for _, ex in enumerate(tqdm(data)):
        tokens = word_tokenize(ex['premise'] + ' ' + ex['hypothesis'])
        row_to_add = np.array([0, 0, 0])
        row_to_add[ex['label']] = 1
        for word in set(tokens):
            lower_word = word.lower()
            if lower_word not in vocab_class_counts:
                vocab_class_counts[lower_word] = np.array(row_to_add)
            else:
                vocab_class_counts[lower_word] += row_to_add
    return vocab_class_counts

def get_token_statistics(dataset: str, split: str = 'train', base_alpha: float = 0.01) -> pd.DataFrame:
    data = get_vocab_class_counts(dataset, split)
    df = pd.DataFrame.from_dict(data, 'index')
    df = df.loc[df.index.str.isalpha()]
    df.rename(columns={0:'count_e', 1:'count_n', 2:'count_c'}, inplace=True)

    # calculate observed proportions, phat
    df['count_appearances'] = df.sum(axis=1)
    df[['phat_e', 'phat_n', 'phat_c']] = df[['count_e', 'count_n', 'count_c']].div(df.count_appearances, axis=0)
    

    # apply helper to calculate z scores for each word and class label
    df[['zscore_e', 'zscore_n', 'zscore_c']] = df[['count_e','count_n','count_c']].apply(lambda row: calc_z_score(row), axis=1)

    # calculate 1-sided p values using normal cdf
    df[['pval_e', 'pval_n', 'pval_c']]= 1 - df[['zscore_e', 'zscore_n', 'zscore_c']].apply(lambda x: stats.norm.cdf(x))
    df['max_z_class'] = df[['zscore_e', 'zscore_n', 'zscore_c']].idxmax(axis=1)
    df['max_z_score'] = df[['zscore_e', 'zscore_n', 'zscore_c']].max(axis=1)

    # add column for result of hypothesis test (i.e. is the token a data artifact)
    corrected_alpha = base_alpha / len(df)
    df['is_artifact'] = df[['pval_e', 'pval_n', 'pval_c']].min(axis=1) < corrected_alpha

    return df

def get_partitioned_tokens(token_zscores: pd.DataFrame, min_count=20, cohort_size=50) -> pd.DataFrame:
    # creating partitions of classes
    df = token_zscores.loc[token_zscores.count_appearances >= min_count].copy()

    df_ent = df.loc[df.max_z_class == 'zscore_e', 'zscore_e']
    df_ent = pd.concat([df_ent.nlargest(cohort_size), df_ent.nsmallest(cohort_size)]).to_frame()
    df_ent['class_partition'] = 0

    df_neu = df.loc[df.max_z_class == 'zscore_n', 'zscore_n']
    df_neu = pd.concat([df_neu.nlargest(cohort_size), df_neu.nsmallest(cohort_size)]).to_frame()
    df_neu['class_partition'] = 1

    df_con = df.loc[df.max_z_class == 'zscore_c', 'zscore_c']
    df_con = pd.concat([df_con.nlargest(cohort_size), df_con.nsmallest(cohort_size)]).to_frame()
    df_con['class_partition'] = 2

    df_all = pd.concat([df_ent, df_neu, df_con])
    df_all['zscore'] = df_all[['zscore_e', 'zscore_n', 'zscore_c']].bfill(axis=1).iloc[:, 0]
    df_all.drop(columns=['zscore_e', 'zscore_n', 'zscore_c'], inplace=True)
    return df_all

def unpack_predictions(predictions_json: str, partitioned_tokens: pd.DataFrame) -> pd.DataFrame:
    with open(predictions_json, 'r') as file:
        predictions = [json.loads(line) for line in file]

    df = pd.DataFrame.from_records(data=predictions, index=['premise', 'hypothesis']).reset_index()
    df['word'] = df.premise + df.hypothesis
    df = df.merge(partitioned_tokens, how='left', left_on='word', right_index=True)
    df['target_score'] = df.apply(lambda x: x.predicted_scores[int(x.class_partition)], axis=1)
    df['target_prob'] = df.apply(lambda x: np.exp(x.target_score) / np.sum(np.exp(x.predicted_scores)), axis=1)
    df = df.groupby(['word', 'class_partition'])[['target_prob', 'zscore']].mean().reset_index()
    return df
# helper function to calculate z scores for a given pandas series representing a word token
def calc_z_score(values: pd.Series, p_null = 1/3) -> float:
    n = values.sum()
    z = values / n
    z = z - p_null
    z = z / np.sqrt(p_null * (1 - p_null) / n)
    return z

# function to create a single token dataset json file from a list of words
# i.e. {'premise': word, 'hypothesis': '', label=2}
# and {'premise': '', 'hypothesis': 'word', label=2} for every word in list
def create_single_token_dataset(words: List, output_file_path: str) -> None:
    dataset = []
    for token in words:
        empty_hypothesis = {'premise': token, 'hypothesis': '', 'label': 2}
        empty_premise = {'premise': '', 'hypothesis': token, 'label': 2}
        dataset.append(empty_hypothesis)
        dataset.append(empty_premise)

    with open(output_file_path, 'w') as file:
        for ex in dataset:
            json.dump(ex, file)
            file.write('\n')
    file.close()

# function to calculate mean probability difference between high and low z score tokens for a given class label
def calc_delta_p(df: pd.DataFrame, class_partition: pd.DataFrame) -> float:
    df = df.loc[df.class_partition==class_partition]
    p_largest = df.nlargest(50, columns='zscore')
    p_smallest = df.nsmallest(50, columns='zscore')
    delta_p = (p_largest['target_prob'].sum() - p_smallest['target_prob'].sum())/50
    return delta_p

# function to filter a given dataset to include only examples that contain at least one of a given set of words
# writes the filtered examples to a json file
def filter_dataset_by_word(dataset: str, words: List, output_file_path: str, split='validation') -> None:
    words = set(words)
    if dataset.endswith('.json') or dataset.endswith('.jsonl'):
        with open(dataset, 'r') as file:
            data = [json.loads(line) for line in file]
    else:
        data = datasets.load_dataset(dataset, split=split)
        data = data.to_iterable_dataset()

    keep = []
    cnt = 0
    for _, ex in enumerate(tqdm(data)):
        cnt += 1
        tokens = set(word_tokenize(ex['premise'] + ' ' + ex['hypothesis']))
        if len(words.intersection(tokens)) > 0:
            keep.append(ex)

    with open(output_file_path, 'w') as file:
        for ex in keep:
            json.dump(ex, file)
            file.write('\n')
    file.close()
    print(f'{len(keep)} of {cnt} examples kept and written to {output_file_path}')