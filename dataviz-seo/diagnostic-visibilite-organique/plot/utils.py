"""
utils.py - Normalisation universelle (path-first), fusion GSC/Crawl et détection de conformité pilier/préfixe
"""

import pandas as pd
from urllib.parse import urlparse
import json
from pathlib import Path


def normalize_url(url: str) -> str:
    if pd.isna(url):
        return "/"
    u = str(url).strip()
    if not u or u == 'nan':
        return "/"
    if u.startswith(('http://', 'https://')):
        parsed = urlparse(u.lower())
        path = parsed.path
    else:
        path = u.split('?')[0].split('#')[0]
        if not path.startswith('/'):
            path = '/' + path

    cleaned = path.rstrip('/') if path != '/' else '/'
    return cleaned.lower() if cleaned else '/'


def prepare_gsc_data(filepath: str, verbose: bool = False, **kwargs) -> pd.DataFrame:
    df = pd.read_csv(filepath, encoding='utf-8-sig')
    rename_map = {
        'Pages les plus populaires': 'URL',
        'Top pages': 'URL',
        'Page': 'URL',
        'url': 'URL',
        'Clics': 'Clicks_GSC',
        'Clicks': 'Clicks_GSC',
        'Impressions': 'Impressions_GSC',
        'Position moyenne': 'Position_Moyenne',
        'Position': 'Position_Moyenne',
        'Average position': 'Position_Moyenne'
    }
    df = df.rename(columns={c: rename_map.get(c, c) for c in df.columns})
    required = ['URL', 'Clicks_GSC', 'Impressions_GSC', 'Position_Moyenne']
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Colonnes manquantes GSC: {missing}. Présentes: {list(df.columns)}")

    df['Clicks_GSC'] = pd.to_numeric(df['Clicks_GSC'], errors='coerce').fillna(0)
    df['Impressions_GSC'] = pd.to_numeric(df['Impressions_GSC'], errors='coerce').fillna(0)
    df['Position_Moyenne'] = pd.to_numeric(df['Position_Moyenne'], errors='coerce').fillna(100)
    df['norm_url'] = df['URL'].apply(normalize_url)
    return df


def prepare_crawl_data(filepath: str, verbose: bool = False, **kwargs) -> pd.DataFrame:
    df = pd.read_csv(filepath, encoding='utf-8-sig')
    rename_map = {
        'Address': 'URL',
        'address': 'URL',
        'url': 'URL',
        'Crawl Depth': 'Profondeur_Crawl',
        'Depth': 'Profondeur_Crawl',
        'depth': 'Profondeur_Crawl',
        'level': 'Profondeur_Crawl',
        'Status': 'Status_Code',
        'Status Code': 'Status_Code',
        'status_code': 'Status_Code',
        'status': 'Status_Code'
    }
    df = df.rename(columns={c: rename_map.get(c, c) for c in df.columns})
    required = ['URL', 'Profondeur_Crawl']
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Colonnes manquantes Crawl: {missing}. Présentes: {list(df.columns)}")

    df['Profondeur_Crawl'] = pd.to_numeric(df['Profondeur_Crawl'], errors='coerce').fillna(5)
    df['norm_url'] = df['URL'].apply(normalize_url)
    return df


def merge_datasets(df_gsc: pd.DataFrame, df_crawl: pd.DataFrame, verbose: bool = False, **kwargs) -> pd.DataFrame:
    df_gsc['norm_url'] = df_gsc['URL'].apply(normalize_url)
    df_crawl['norm_url'] = df_crawl['URL'].apply(normalize_url)

    cols_crawl = ['norm_url', 'Profondeur_Crawl']
    if 'Status_Code' in df_crawl.columns:
        cols_crawl.append('Status_Code')

    merged = pd.merge(
        df_gsc,
        df_crawl[cols_crawl].drop_duplicates(subset=['norm_url']),
        on='norm_url',
        how='left'
    )

    default_depth = int(df_crawl['Profondeur_Crawl'].max() + 1) if len(df_crawl) > 0 else 5
    merged['Profondeur_Crawl'] = merged['Profondeur_Crawl'].fillna(default_depth).astype(float)

    return merged


def load_pillars_config(config_path):
    with open(config_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if isinstance(data, list):
        return {
            "pillars": data,
            "max_allowed_depth": 2
        }
    return {
        "pillars": data.get("pillars", []),
        "max_allowed_depth": data.get("max_allowed_depth", 2)
    }


def tag_pillar_deviations(merged_df: pd.DataFrame, pillars_config: dict) -> pd.DataFrame:
    df = merged_df.copy()
    df['pillar_match'] = None
    df['pillar_deviation'] = False

    pillars_list = pillars_config.get("pillars", []) if isinstance(pillars_config, dict) else (pillars_config if isinstance(pillars_config, list) else [])
    max_d_sample = int(df['Profondeur_Crawl'].max()) if len(df) > 0 else 2
    global_max_depth = pillars_config.get("max_allowed_depth", 1 if max_d_sample <= 2 else 2)

    for idx, row in df.iterrows():
        url = row['norm_url']
        depth = row['Profondeur_Crawl']

        matched_pillar = None
        target_max_depth = global_max_depth

        for p_item in pillars_list:
            p_name = p_item.get('name', 'Pillar')
            p_patterns = p_item.get('patterns', [])
            p_max_depth = p_item.get('max_depth_target', global_max_depth)

            for pat in p_patterns:
                pat_clean = normalize_url(pat)
                if pat_clean == '/' and url == '/':
                    matched_pillar = p_name
                    target_max_depth = p_max_depth
                    break
                elif pat_clean != '/' and (url == pat_clean.rstrip('/') or url.startswith(pat_clean.rstrip('/') + '/')):
                    matched_pillar = p_name
                    target_max_depth = p_max_depth
                    break
                elif pat.lower() in url.lower():
                    matched_pillar = p_name
                    target_max_depth = p_max_depth
                    break
            if matched_pillar:
                break

        if not matched_pillar and depth > global_max_depth:
            matched_pillar = 'Hors-pilier-profond'
            target_max_depth = global_max_depth

        if matched_pillar:
            df.at[idx, 'pillar_match'] = matched_pillar
            if depth > target_max_depth:
                df.at[idx, 'pillar_deviation'] = True

    return df

load_gsc_data = prepare_gsc_data
load_crawl_data = prepare_crawl_data
merge_gsc_crawl = merge_datasets