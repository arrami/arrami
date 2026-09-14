"""
plot-seo.py - CLI d'audit SEO 4D (GSC + Crawl + Piliers avec découplage mode demo/prod & fallback résilient)
"""

import argparse
from pathlib import Path
import pandas as pd
from utils import load_gsc_data, load_crawl_data, merge_gsc_crawl, load_pillars_config, tag_pillar_deviations
from visualizer import generate_seo_matrix


def resolve_sample_path(cli_arg: str, default_sub: str, root_fallback: str, is_demo: bool) -> str:
    if cli_arg:
        return cli_arg
    p_sub = Path(default_sub)
    if p_sub.exists():
        return str(p_sub)
    p_root = Path(root_fallback)
    if p_root.exists():
        return str(p_root)
    return str(p_sub)  # Lève l'erreur explicite habituelle si introuvable


def main():
    parser = argparse.ArgumentParser(description="Matrice SEO 4D & Audit d'architecture")
    parser.add_argument("--mode", choices=["demo", "prod"], default="demo", help="Mode d'exécution (demo ou prod)")
    parser.add_argument("--gsc", help="Chemin vers le CSV GSC (auto selon --mode si omis)")
    parser.add_argument("--crawl", help="Chemin vers le CSV Crawl (auto selon --mode si omis)")
    parser.add_argument("--config", help="Chemin vers la config des piliers (auto selon --mode si omis)")
    parser.add_argument("--min-impressions", type=int, default=0, help="Filtrer les impressions min")
    parser.add_argument("--output", default="output/seo-matrix.png", help="Fichier de sortie principal (png/svg)")
    parser.add_argument("--export-deviations", action="store_true", help="Exporter un CSV des déviations d'architecture")
    parser.add_argument("--verbose", action="store_true", help="Mode verbeux")
    args = parser.parse_args()

    is_demo = args.mode == "demo"
    default_config_path = Path("config/pillars.demo.json" if is_demo else "config/pillars.json")

    gsc_path = resolve_sample_path(
        args.gsc,
        "data/samples/sample-gsc.csv" if is_demo else "data/private/gsc-pages.csv",
        "sample-gsc.csv",
        is_demo
    )
    crawl_path = resolve_sample_path(
        args.crawl,
        "data/samples/sample-crawl.csv" if is_demo else "data/private/freecrawl.csv",
        "sample-crawl.csv",
        is_demo
    )
    config_path = Path(args.config) if args.config else default_config_path

    if args.verbose:
        print(f"[*] Mode : {args.mode.upper()}")
        print(f"[*] Chargement GSC : {gsc_path}")
    df_gsc = load_gsc_data(gsc_path, verbose=args.verbose)

    if args.verbose:
        print(f"[*] Chargement Crawl : {crawl_path}")
    df_crawl = load_crawl_data(crawl_path, verbose=args.verbose)

    if args.min_impressions > 0:
        df_gsc = df_gsc[df_gsc['Impressions_GSC'] >= args.min_impressions]

    merged = merge_gsc_crawl(df_gsc, df_crawl, verbose=args.verbose)

    # Chargement config piliers & tag des déviations avec fallback démo
    if not config_path.exists() and is_demo:
        pillars_cfg = {
            "max_allowed_depth": 2,
            "pillars": [
                {"name": "Blog", "patterns": ["/blog"], "max_depth_target": 2},
                {"name": "Services", "patterns": ["/services"], "max_depth_target": 2}
            ]
        }
    else:
        pillars_cfg = load_pillars_config(str(config_path))

    merged = tag_pillar_deviations(merged, pillars_cfg)

    if args.export_deviations:
        devs = merged[merged.get('pillar_deviation', False)].copy()
        if devs.empty and is_demo:
            # Fallback pédagogique mode démo si profondeur > 2 dans le sample
            devs = merged[merged['Profondeur_Crawl'] > 2].copy()
            devs['pillar_deviation'] = True
            devs['pillar_match'] = devs['pillar_match'].fillna('Hors-prof-cible')

        dev_path = Path("output/arch_deviations.csv")
        dev_path.parent.mkdir(parents=True, exist_ok=True)
        export_cols = [c for c in ['URL', 'pillar_match', 'Profondeur_Crawl', 'Impressions_GSC'] if c in devs.columns]
        devs[export_cols].to_csv(dev_path, index=False, encoding='utf-8-sig')
        if args.verbose:
            print(f"  ✓ {len(devs)} déviations exportées vers {dev_path}")

    # Double rendu (PNG + HTML interactif Plotly)
    generate_seo_matrix(merged, output_path=args.output, verbose=args.verbose, generate_html=True)


if __name__ == "__main__":
    main()