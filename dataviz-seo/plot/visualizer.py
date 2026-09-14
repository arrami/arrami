"""
visualizer.py - Moteur de dataviz SEO 4D (Matplotlib statique + Plotly interactif avec surbrillance des déviations & slugs)
"""

import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import numpy as np

try:
    import plotly.express as px
    HAS_PLOTLY = True
except ImportError:
    HAS_PLOTLY = False


def extract_slug(url: str) -> str:
    if pd.isna(url):
        return 'home'
    parts = [p for p in str(url).split('/') if p and not p.startswith('http') and not p.startswith('https') and ':' not in p]
    return parts[-1] if parts else 'home'


def validate_df(df: pd.DataFrame) -> None:
    required_cols = ['Position_Moyenne', 'Clicks_GSC', 'Impressions_GSC', 'Profondeur_Crawl', 'URL']
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        raise ValueError(f"Colonnes manquantes: {missing}")
    if len(df) == 0:
        raise ValueError("DataFrame vide après filtrage!")


def generate_seo_matrix(
    df: pd.DataFrame,
    output_path: str = 'output/seo-matrix.png',
    format: str = 'png',
    verbose: bool = False,
    generate_html: bool = True
) -> None:
    validate_df(df)

    df = df.copy()
    if 'Slug' not in df.columns:
        df['Slug'] = df['URL'].apply(extract_slug)

    if verbose:
        print(f"  ✓ Données validées: {len(df)} URLs")

    # 1. Rendu Matplotlib (statique / publication)
    fig, ax = plt.subplots(figsize=(14, 8))

    min_imp = df['Impressions_GSC'].min()
    max_imp = df['Impressions_GSC'].max()
    sizes = 50 + 250 * np.sqrt((df['Impressions_GSC'] - min_imp) / max(max_imp - min_imp, 1))

    scatter = ax.scatter(
        df['Position_Moyenne'],
        df['Clicks_GSC'],
        s=sizes,
        c=df['Profondeur_Crawl'],
        cmap='magma_r',
        alpha=0.75,
        edgecolors='black',
        linewidth=0.5,
        zorder=3
    )

    if 'pillar_deviation' in df.columns and df['pillar_deviation'].any():
        dev_df = df[df['pillar_deviation']]
        dev_sizes = 50 + 250 * np.sqrt((dev_df['Impressions_GSC'] - min_imp) / max(max_imp - min_imp, 1))
        ax.scatter(
            dev_df['Position_Moyenne'],
            dev_df['Clicks_GSC'],
            s=dev_sizes * 1.3,
            facecolors='none',
            edgecolors='#e63946',
            linewidth=1.8,
            linestyle='--',
            zorder=5,
            label='Dérive pilier (depth > target)'
        )
        ax.legend(loc='upper right', frameon=True, fontsize=9)

    median_clicks = df['Clicks_GSC'].median()
    linthresh = max(1.0, median_clicks * 0.1) if pd.notna(median_clicks) else 1.0
    ax.set_yscale('symlog', linthresh=linthresh)

    if len(df) <= 15:
        df_annot = df
    else:
        top_clicks = df.sort_values(by='Clicks_GSC', ascending=False).head(10)
        outliers = df[(df['Profondeur_Crawl'] >= 3) & (df['Clicks_GSC'] > df['Clicks_GSC'].quantile(0.5))]
        df_annot = pd.concat([top_clicks, outliers]).drop_duplicates().head(12)

    texts = []
    annotated_points = set()
    for _, row in df_annot.iterrows():
        pos_key = round(row['Position_Moyenne'], 1)
        clicks_key = round(row['Clicks_GSC'], 0)
        if (pos_key, clicks_key) in annotated_points:
            continue
        annotated_points.add((pos_key, clicks_key))

        short_url = row.get('Slug', extract_slug(row['URL']))

        txt = ax.text(
            row['Position_Moyenne'],
            row['Clicks_GSC'],
            f" {short_url}",
            fontsize=8,
            alpha=0.92,
            zorder=4,
            bbox=dict(
                boxstyle='round,pad=0.25',
                facecolor='white',
                edgecolor='#ccc',
                alpha=0.9,
                linewidth=0.5
            )
        )
        texts.append(txt)

    try:
        from adjustText import adjust_text
        adjust_text(
            texts,
            ax=ax,
            arrowprops=dict(arrowstyle='-', color='#888', lw=0.4, alpha=0.5),
            expand_points=(1.6, 1.6),
            force_points=(1.1, 1.1)
        )
    except ImportError:
        pass

    ax.axvline(3.0, color='green', linestyle='--', alpha=0.3, zorder=1)
    ax.axvline(10.0, color='orange', linestyle='--', alpha=0.3, zorder=1)

    ax.set_title(
        'Matrice SEO 4D: Position SERP vs Clics (SymLog) × Impressions (Taille) × Profondeur (Couleur)',
        fontsize=12,
        fontweight='bold',
        pad=18
    )
    ax.set_xlabel("Position Moyenne SERP (plus c'est bas, meilleur c'est)", fontsize=10, fontweight='bold')
    ax.set_ylabel('Clics GSC (Échelle SymLog)', fontsize=10, fontweight='bold')

    cbar = plt.colorbar(scatter, ax=ax)
    cbar.set_label('Profondeur de Crawl (clair = proche de la racine)', fontsize=9)

    ax.grid(True, which='both', linestyle=':', alpha=0.4, linewidth=0.6, zorder=0)
    ax.set_axisbelow(True)

    ax.axvspan(1.0, 3.0, color='green', alpha=0.03, zorder=0)
    y_top_limit = df['Clicks_GSC'].max() if len(df) > 0 else 100
    ax.text(1.1, y_top_limit * 0.75, '✓ Zone Jackpot (Top 3)', fontsize=8, color='green', alpha=0.5, fontweight='bold')

    plt.tight_layout()

    out_p = Path(output_path)
    if not out_p.suffix:
        out_p = out_p.with_suffix(f'.{format}')

    out_p.parent.mkdir(parents=True, exist_ok=True)

    if format == 'svg':
        fig.savefig(str(out_p.resolve()), format='svg', bbox_inches='tight')
    else:
        fig.savefig(str(out_p.resolve()), dpi=300, format='png', bbox_inches='tight')
    plt.close(fig)

    if verbose:
        file_size = out_p.stat().st_size / 1024
        print(f"  ✓ Fichier statique sauvegardé: {out_p} ({file_size:.1f} KB)")

    # 2. Rendu Plotly (interactif / exploration Web)
    if generate_html and HAS_PLOTLY:
        out_dir = out_p.parent
        out_dir.mkdir(parents=True, exist_ok=True)
        html_path = out_dir / out_p.with_suffix('.html').name

        hover_cols = ['URL', 'Clicks_GSC', 'Impressions_GSC', 'Position_Moyenne', 'Profondeur_Crawl']
        if 'pillar_deviation' in df.columns:
            hover_cols.extend(['pillar_match', 'pillar_deviation'])

        fig_px = px.scatter(
            df,
            x='Position_Moyenne',
            y='Clicks_GSC',
            size='Impressions_GSC',
            color='Profondeur_Crawl',
            hover_name='Slug',
            hover_data=hover_cols,
            color_continuous_scale='magma_r',
            title='Matrice SEO 4D Interactive — Exploration fine (Slug & Survol URL)'
        )
        fig_px.update_layout(
            height=850,
            template='plotly_white',
            xaxis=dict(autorange=True),
            yaxis=dict(type='linear')
        )
        fig_px.write_html(str(html_path.resolve()))
        if verbose:
            print(f"  ✓ Rapport interactif HTML généré : {html_path.resolve()}")