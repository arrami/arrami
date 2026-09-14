# plot/audit_arch.py
import argparse
import os
import sys
import numpy as np
import pandas as pd

def parse_args():
    parser = argparse.ArgumentParser(description="Audit architectural GSC/crawl")
    parser.add_argument("--input", required=True, help="Chemin du CSV d'entrée")
    parser.add_argument("--sigma", type=float, default=2.0, help="Seuil Z-score")
    parser.add_argument("--out", default="stdout", help="Chemin du fichier .md ou 'stdout'")
    return parser.parse_args()

def analyze(df, sigma):
    grouped = df.groupby('pillar_match')['Impressions_GSC']
    mean_p = grouped.transform('mean')
    std_p = grouped.transform('std').replace(0, np.nan)
    df['z_score'] = ((df['Impressions_GSC'] - mean_p) / std_p).fillna(0)

    q1 = grouped.transform(lambda x: x.quantile(0.25))
    q3 = grouped.transform(lambda x: x.quantile(0.75))
    iqr = q3 - q1
    df['is_iqr_outlier'] = (df['Impressions_GSC'] < (q1 - 1.5 * iqr)) | (df['Impressions_GSC'] > (q3 + 1.5 * iqr))

    df['diagnostic'] = np.select(
        [
            df['is_iqr_outlier'] & (df['z_score'] > sigma),
            df['is_iqr_outlier'] & (df['z_score'] < -sigma),
            (df['pillar_match'] == 'Hors-pilier-profond') & (df['Impressions_GSC'] < df['Impressions_GSC'].median())
        ],
        [
            'Surperformance contenu (Asset fort)',
            'Anomalie basse isolée',
            'Dérive structurelle (Bloc sous-exposé)'
        ],
        default='Conforme au standard du pilier'
    )
    return df

def to_markdown(df):
    lines = [
        "# Rapport d'audit architectural GSC\n",
        f"**Corpus** : {len(df)} URLs analysées | **Seuil $\\sigma$** : 2.0\n",
        "## Répartition des diagnostics\n"
    ]
    summary = df['diagnostic'].value_counts().reset_index()
    summary.columns = ['Diagnostic', 'Volume']
    lines.append(summary.to_markdown(index=False))

    lines.append("\n## Focus sur les écarts (hors standard)\n")
    subset = df[df['diagnostic'] != 'Conforme au standard du pilier'][['URL', 'pillar_match', 'Impressions_GSC', 'z_score', 'diagnostic']]
    lines.append(subset.to_markdown(index=False))
    return "\n".join(lines)

def main():
    args = parse_args()
    df = pd.read_csv(args.input)
    df_res = analyze(df, args.sigma)
    md = to_markdown(df_res)

    if args.out.lower() in ['stdout', 'markdown']:
        print(md)
    else:
        out_dir = os.path.dirname(args.out)
        if out_dir:
            os.makedirs(out_dir, exist_ok=True)
        with open(args.out, 'w', encoding='utf-8') as f:
            f.write(md)
        print(f"Rapport sauvegardé : {args.out}", file=sys.stderr)

if __name__ == '__main__':
    main()