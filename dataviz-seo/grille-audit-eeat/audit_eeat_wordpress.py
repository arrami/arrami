#!/usr/bin/env python3
"""
Audit E-E-A-T en lot pour un blog WordPress — version 2 (mêmes règles que la page interactive).

Récupère les articles publiés via l'API REST de WordPress (ou un fichier JSON),
applique les contrôles automatiques de la grille pondérée, puis exporte un
rapport Excel pré-rempli : notes suggérées, score, verdict et signaux détectés.
La note finale reste humaine : relisez et corrigez les cellules jaunes.

Nouveautés de la version 2
  - Outils et sources détectés par la structure des phrases (isToolNamed, isBrandCited),
    la liste du domaine n'est plus qu'un renfort.
  - Mode domaine : SEO / WordPress par défaut, désactivable (--domaine aucun) ou
    remplaçable par vos propres listes (--outils, --formules).
  - Qualité des liens : démonstration, interne, page d'accueil, recherche.
  - Formules creuses en deux niveaux (clichés pleins, connecteurs banals à 1/4).
  - Widgets retirés (articles similaires, partage, boîte auteur), légendes ignorées.
  - Signaux auteur lus dans l'API (nom, bio, lien de profil, catégorie).

Usage :
    python audit_eeat_wordpress.py https://monblog.fr
    python audit_eeat_wordpress.py https://monblog.fr --max 50 --out rapport.xlsx
    python audit_eeat_wordpress.py https://blog-cuisine.fr --domaine aucun
    python audit_eeat_wordpress.py https://monblog.fr --outils outils.txt --formules formules.txt
    python audit_eeat_wordpress.py --json articles.json          # hors ligne

Dépendances : Python 3.9+, openpyxl  (pip install openpyxl)

Limites : les règles sont écrites pour le français. Le script vérifie la forme, jamais le fond :
il ne visite pas les liens et ne sait pas si un chiffre existe chez la source citée.
"""
import argparse
import html
import json
import re
import sys
import time
import urllib.error
import urllib.request
from datetime import date, datetime
from html.parser import HTMLParser
from urllib.parse import urljoin, urlparse

# --------------------------------------------------------------------------
# Paramètres de la grille (modifiables aussi dans l'onglet « Paramètres »)
# --------------------------------------------------------------------------
CRITERIA = [
    ("exp", "Preuve d'expérience", 25),
    ("src", "Traçabilité des sources", 20),
    ("time", "Cohérence temporelle", 15),
    ("struct", "Intégrité de la structure", 15),
    ("dens", "Densité et valeur ajoutée", 15),
    ("auth", "Signaux auteur et site", 10),
]
SEUIL_FIABLE, SEUIL_VERIFIER, PLAFOND = 75, 50, 40

# --------------------------------------------------------------------------
# Listes (identiques à la page interactive)
# --------------------------------------------------------------------------
DOMAIN_SEO = [
    "elementor", "gutenberg", "block editor", "site editor", "wpbakery", "divi",
    "beaver builder", "bricks", "oxygen", "breakdance", "kadence", "brizy",
    "themify", "thrive architect", "siteorigin", "yoast", "rank math", "aioseo",
    "all in one seo", "seopress", "seokey", "the seo framework", "slim seo", "squirrly",
    "screaming frog", "sitebulb", "oncrawl", "semrush", "ahrefs", "moz",
    "surfer seo", "clearscope", "frase", "marketmuse", "ubersuggest", "answerthepublic",
    "google search console", "bing webmaster", "otterly", "profound", "peec ai", "scrunch ai",
    "athenahq", "wp rocket", "litespeed cache", "perfmatters", "flyingpress", "autoptimize",
    "updraftplus", "wordfence", "query monitor", "wpml", "polylang", "woocommerce",
    "jetpack", "cloudflare", "sparktoro", "backlinko", "hubspot", "similarweb",
    "statista", "sistrix", "http archive", "librecrawl", "serpbear", "serpapi",
    "dataforseo", "searxng", "crawl4ai", "firecrawl", "goaccess", "matomo",
    "plausible", "umami", "google analytics", "looker studio", "pagespeed insights", "lighthouse",
    "gtmetrix", "webpagetest", "ai engine", "jetpack ai", "rank math content ai", "elementor ai",
    "angie", "uncanny automator", "mcp adapter", "abilities api", "wordlift", "schema pro",
    "getgenie", "bertha ai", "chatgpt", "gemini", "perplexity", "mistral",
    "gptbot", "claudebot", "perplexitybot", "googlebot", "bingbot", "llms.txt"]
DOMAIN_SEO_CLICHES = [
    "le contenu est roi", "content is king", "contenu de qualité", "contenu pertinent et de qualité", "google adore", "google aime",
    "les moteurs de recherche adorent", "google récompense", "google privilégie", "google favorise", "signal fort pour google", "améliorer votre référencement",
    "booster votre seo", "boostez votre seo", "booster votre référencement", "propulser votre site", "grimper dans les serp", "en première page de google",
    "en tête des résultats", "une stratégie seo efficace", "une stratégie seo solide", "une stratégie seo gagnante", "les bonnes pratiques seo", "un site bien optimisé",
    "optimiser votre site pour les moteurs", "les algorithmes évoluent sans cesse", "google met régulièrement à jour", "le seo n'est pas mort", "le seo est mort", "le seo évolue sans cesse",
    "le geo est le nouveau seo", "l'avenir du seo", "l'ia change la donne", "l'ia bouleverse", "la révolution de l'ia", "gagner en visibilité",
    "augmenter votre trafic", "générer du trafic qualifié", "attirer plus de visiteurs", "des backlinks de qualité", "un maillage interne efficace", "le seo est un marathon",
    "travail de longue haleine", "les résultats ne se feront pas attendre", "l'expérience utilisateur est primordiale", "un référencement durable", "maximiser votre visibilité", "se démarquer de la concurrence",
    "prendre une longueur d'avance", "outil indispensable", "extension indispensable", "plugin indispensable", "must-have", "intuitif et puissant",
    "en quelques clics"]
NOT_TOOLS = set([
    "AI", "ALT", "AMP", "API", "AVIF", "B2B",
    "B2C", "CDN", "CEO", "CLS", "CMO", "CMS",
    "CPU", "CSS", "CTA", "CTO", "CWV", "DIY",
    "DNS", "E-E-A-T", "EEAT", "ETI", "FAQ", "FID",
    "FSE", "GDPR", "GEO", "HT", "HTML", "HTTP",
    "HTTPS", "IA", "INP", "JPEG", "JPG", "JS",
    "JSON", "KPI", "KPIS", "LCP", "LLM", "LLMS",
    "NB", "OK", "PDF", "PHP", "PME", "PNG",
    "PS", "PWA", "QR", "RAM", "RGAA", "RGPD",
    "ROI", "RSS", "SAAS", "SAV", "SEA", "SEO",
    "SERP", "SERPS", "SMO", "SMS", "SSD", "SSL",
    "SVG", "TLS", "TPE", "TTC", "TTFB", "TV",
    "TVA", "UE", "UI", "URL", "URLS", "USA",
    "USB", "UX", "WEBP", "WIFI", "XML"])
STOP_CAPS = set([
    "Le", "La", "Les", "L", "Un", "Une",
    "Des", "Du", "De", "D", "Ce", "Cet",
    "Cette", "Ces", "Il", "Elle", "Ils", "Elles",
    "On", "Je", "J", "Nous", "Vous", "Tu",
    "Mon", "Ma", "Mes", "Notre", "Nos", "Votre",
    "Vos", "Son", "Sa", "Ses", "Leur", "Leurs",
    "Selon", "Après", "Avant", "En", "Dans", "Pour",
    "Par", "Sur", "Sous", "Avec", "Sans", "Mais",
    "Et", "Ou", "Donc", "Or", "Ni", "Car",
    "Si", "Quand", "Comme", "Puis", "Enfin", "Ensuite",
    "Aussi", "Bref", "Oui", "Non", "Voici", "Voilà",
    "Chez", "Entre", "Vers", "Depuis", "Pendant", "Lorsque",
    "Parce", "Afin", "Tout", "Tous", "Toute", "Toutes",
    "Chaque", "Certains", "Certaines", "Plusieurs", "Aucun", "Aucune",
    "Même", "Encore", "Déjà", "Ici", "Là", "Qui",
    "Que", "Quoi", "Où", "Comment", "Pourquoi", "Combien",
    "Quel", "Quelle", "Quels", "Quelles", "Étape", "Astuce",
    "Conseil", "Attention", "Note", "Exemple", "Résultat", "Conclusion",
    "Introduction", "Source", "Sources", "Bonus"])
HEDGES = [
    "varie selon les études", "ordre de grandeur", "n'est pas détaillée", "ne sont pas détaillés", "selon certaines études", "selon plusieurs études",
    "selon des experts", "on estime que", "les études montrent", "certaines sources", "il semblerait", "selon les sources",
    "à titre indicatif"]
CLICHES = [
    "dans le paysage actuel", "il est crucial", "il est essentiel", "en constante évolution", "à l'ère de", "à l'ère du numérique",
    "à l'heure du tout-numérique", "levier incontournable", "game changer", "n'est plus une option", "plus que jamais", "pierre angulaire",
    "au cœur de", "dans un monde où", "il convient de", "force est de constater", "optimiser votre visibilité", "transforme la stratégie en acte",
    "véritable atout", "booster votre", "boostez", "incontournable", "révolutionne", "sans plus attendre",
    "le saviez-vous", "il est important de noter", "jouer un rôle clé", "clé du succès", "à l'heure où", "dans un contexte où",
    "dans le monde d'aujourd'hui", "il est indéniable que", "nul ne peut ignorer", "il va sans dire", "comme chacun sait", "il convient de souligner",
    "il est à noter que", "solution clé en main", "gagner en efficacité", "optimiser vos performances", "améliorer votre productivité", "booster votre croissance",
    "décupler vos résultats", "libérer tout le potentiel", "passer au niveau supérieur", "franchir un cap", "tirer son épingle du jeu", "il est important de",
    "il est primordial de", "il est fondamental de", "il faut garder à l'esprit", "n'oublions pas que", "il ne faut pas perdre de vue", "la clé réside dans",
    "le secret réside dans", "l'essentiel est de", "le plus important est de", "des résultats concrets", "des résultats mesurables", "un impact réel",
    "un véritable levier", "un atout majeur", "un facteur clé de succès", "une étape cruciale", "une étape incontournable", "un passage obligé",
    "une condition sine qua non", "à l'heure de l'intelligence artificielle", "dans un monde de plus en plus digital", "dans un environnement en mutation", "face aux nouveaux enjeux", "face aux défis actuels",
    "pour rester compétitif", "pour ne pas se laisser distancer", "dans cet article, nous allons", "nous allons découvrir ensemble", "explorons ensemble", "plongeons dans le vif du sujet",
    "découvrons sans plus attendre"]
FILLERS = [
    "en effet", "par ailleurs", "de plus", "qui plus est", "cela étant dit", "ceci étant",
    "soulignons que", "précisons que", "notons que", "rappelons que", "de nos jours", "face à",
    "en résumé", "pour résumer", "en synthèse", "en conclusion", "pour conclure", "au final",
    "en fin de compte", "tout bien considéré", "en somme", "en définitive", "faire la différence", "sortir du lot",
    "il est vrai que", "certes", "bien entendu", "évidemment", "naturellement", "bien sûr",
    "voyons maintenant", "passons à présent"]
TOOL_WORDS = "extension|plugin|outil|logiciel|thème|theme|builder|constructeur|application|appli|app|service|plateforme|module|solution|robot|machine|appareil|modèle|marque|perceuse|visseuse|four|mixeur|blender|capteur|caméra|imprimante|smartphone|ordinateur|site"

MONTHS = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août", "septembre",
          "octobre", "novembre", "décembre"]
UP = "A-ZÀ-ÖØ-Ý"  # majuscules, accents compris

RE_FIRST = re.compile(
    r"\b(j'(ai|utilise|recommande|installe|teste|mesure|conseille)|je (n'utilise plus|recommande|conseille|teste|mesure)|"
    r"nous avons (testé|utilisé|installé|mesuré|constaté|migré|comparé)|nous utilisons|dans mon expérience|"
    r"chez mes clients|sur mes sites?|sur un de mes sites|mon client|ma cliente|dans ma cuisine|dans mon atelier)", re.I)
RE_STAT = re.compile(r"\d+[,.]?\d*\s?%|\b\d+\s?(fois|millions?|milliards?)\b|\bx\d+\b", re.I)
RE_METRIC = re.compile(r"\d+[,.]?\d*\s?(s|ms|%|secondes?|minutes?|min|heures?|clics|visites|positions?|€|euros?|kg|g|°C|W|mAh|Go|Mo)\b"
                       r"|passé de|avant.*après|de \d+[,.]?\d* à \d+", re.I)
RE_STUDY = re.compile(r"\b(étude|données|rapport|baromètre|enquête|tendances?|statistiques?|analyse|bilan|chiffres)\b", re.I)
RE_FULLYEAR = re.compile(r"(sur l'ensemble (des données|de l'année)|consolidé|bilan (annuel|de l'année)|"
                         r"sur toute l'année|année complète|sur l'année)", re.I)
RE_WORD = re.compile(r"[\w'-]+", re.U)
RE_TOKEN = re.compile(r"[^\W_][\w.+&-]*", re.U)
RE_VERSION = re.compile(r"\bv?\d+\.\d+(\.\d+)?\b")
RE_TOOL_KW = re.compile(r"\b(?:" + TOOL_WORDS + r")s?\s+«?\s*([" + UP + r"0-9][\w.+&-]*)")
RE_PLACE_BEFORE = re.compile(r"(?:^|\s)(à|au|aux|en|vers|près de|depuis)\s*$", re.I)
RE_HEAD_SKIP = re.compile(r"^(sommaire|table des mati|publications? similaires?|articles? (similaires|r[ée]cents?|li[ée]s)|"
                          r"à lire aussi|commentaires?|laisser un commentaire|partager|r[ée]sum[ée] de l'article|"
                          r"[àa] propos de l'auteur)", re.I)
RE_SRC_SIGNAL = re.compile(r"\b(selon|d'après|une étude (?:de|d'|du|publiée par|menée par)|l'étude (?:de|d'|du)|"
                           r"un rapport (?:de|d'|du)|le rapport (?:de|d'|du)|des données (?:de|d'|du)|"
                           r"les données (?:de|d'|du)|compilées par|publiée? par|source\s*:)\s*", re.I)
RE_NAME = re.compile(r"^([" + UP + r"0-9][\w.&+-]*(?:\s+[" + UP + r"0-9][\w.&+-]*){0,3})")
RE_PAREN = re.compile(r"\((?:source\s*:\s*)?([" + UP + r"][\w.&+-]+(?:\s+[" + UP + r"][\w.&+-]+){0,3})(?:,?\s*\d{4})?\)")
RE_SUBJ = re.compile(r"^(?:l'|le |la |les )?(\S+(?:\s+\S+){0,3}?)\s+(?:a\s+)?(estime|estiment|indique|indiquent|affirme|rapporte|"
                     r"révèle|révèlent|montre|montrent|constate|note|publie|mesure|chiffre|évalue|observe|annonce)\b", re.I)

# Classes et balises des widgets injectés dans le contenu (articles similaires, partage, auteur…)
NOISE_TAGS = {"nav", "aside", "footer", "header", "script", "style", "noscript", "form"}
NOISE_CLASSES = ["yarpp", "related-posts", "post-navigation", "ogeeat-author-box", "ogeeat-share",
                 "ast-post-social-sharing", "ast-social-inner-wrap", "entry-meta", "comments-area", "wp-block-buttons",
                 "sharedaddy", "jp-relatedposts", "author-box", "post-author", "breadcrumb", "sidebar", "share"]


class Rules:
    """Règles actives : générique + renfort du domaine éventuel."""

    def __init__(self, domain_terms=(), domain_cliches=()):
        self.terms = [t.strip().lower() for t in domain_terms if t.strip()]
        self.cliches = [(p, phrase_re(p)) for p in CLICHES]
        self.fillers = [(p, phrase_re(p)) for p in FILLERS]
        self.dom_cliches = [(p, phrase_re(p)) for p in domain_cliches if p.strip()]
        self.all_seo_terms = [t.lower() for t in DOMAIN_SEO]

    @property
    def domain_on(self):
        return bool(self.terms)


def phrase_re(p):
    return re.compile(r"(?<![^\W\d_])" + re.escape(p.strip()) + r"(?![^\W\d_])", re.I)


def in_text(term, low):
    return re.search(r"(?<![\w])" + re.escape(term) + r"(?![\w])", low) is not None


# --------------------------------------------------------------------------
# Détection structurelle des outils et des sources
# --------------------------------------------------------------------------
def tokens(text):
    out = []
    for m in RE_TOKEN.finditer(text):
        tok = m.group(0).rstrip(".-")
        before = text[:m.start()].rstrip()
        start = before == "" or before[-1] in ".:;!?«([\"" or bool(re.search(r"(^|\s)(—|–|-)$", before))
        out.append({"t": tok, "start": start, "pos": m.start()})
    return out


def is_acronym(t):
    letters = [c for c in t if c.isalpha()]
    return (len(t) >= 3 and t[0].isupper() and len(letters) >= 2 and all(c.isupper() for c in letters)
            and re.fullmatch(r"[\w-]+", t) is not None and t.upper() not in NOT_TOOLS)


def is_camel(t):
    return bool(re.fullmatch(r"[a-z]+[A-Z]\w*", t) or re.fullmatch(r"[A-Z][a-z]+[A-Z]\w*", t))


def is_model(t):
    return (len(t) >= 2 and t.isalnum() and any(c.isalpha() for c in t) and any(c.isdigit() for c in t)
            and not re.fullmatch(r"\d+(e|er|ère|ème|s|h|min|ms|px|ko|mo|go|k|m|€)", t, re.I))


def is_proper(tk):
    t = tk["t"]
    return (not tk["start"] and len(t) > 1 and t[0].isupper() and (t[1].islower() or t[1].isdigit())
            and t not in STOP_CAPS and t.upper() not in NOT_TOOLS)


def part_of_name(t):
    return t not in STOP_CAPS and (t[0].isupper() or is_model(t) or re.fullmatch(r"v?\d+(\.\d+)+", t) is not None)


def full_name(toks, i):
    a = b = i
    while a > 0 and not toks[a]["start"] and part_of_name(toks[a - 1]["t"]):
        a -= 1
    while b < len(toks) - 1 and not toks[b + 1]["start"] and part_of_name(toks[b + 1]["t"]):
        b += 1
    return " ".join(x["t"] for x in toks[a:b + 1])


def is_tool_named(text, rules):
    """Renvoie (nom, règle) si un outil ou produit identifiable est nommé, sinon None.
    Signaux structurels d'abord, liste du domaine en dernier. Casse d'origine conservée."""
    toks = tokens(text)
    kw = RE_TOOL_KW.search(text)
    if kw and kw.group(1).upper() not in NOT_TOOLS and kw.group(1) not in STOP_CAPS:
        i = next((j for j, x in enumerate(toks) if x["t"] == kw.group(1)), -1)
        return (full_name(toks, i) if i >= 0 else kw.group(1)), "type + nom"
    for i, x in enumerate(toks):
        if is_acronym(x["t"]):
            return full_name(toks, i), "nom en capitales"
        if is_camel(x["t"]):
            return full_name(toks, i), "nom de marque"
        if is_model(x["t"]):
            return full_name(toks, i), "modèle ou version"
    v = RE_VERSION.search(text)
    if v and not re.search(r"\d+[.,]\d+\s?(%|s|ms|€|m|km|kg|g|cm|mm)\b", text):
        i = next((j for j, x in enumerate(toks) if x["t"] == v.group(0)), -1)
        return (full_name(toks, i) if i >= 0 else v.group(0)), "numéro de version"
    for i, x in enumerate(toks):
        if is_proper(x) and not RE_PLACE_BEFORE.search(text[:x["pos"]]):
            return full_name(toks, i), "nom propre"
    low = text.lower()
    hit = next((t for t in rules.terms if in_text(t, low)), None)
    if hit:
        return hit, "liste du domaine"
    return None


def is_brand_cited(text, rules):
    """Renvoie (nom, règle) si une source nommée est citée, sinon None."""
    for m in RE_SRC_SIGNAL.finditer(text):
        after = text[m.end():]
        after = re.sub(r"^(l'|le |la |les |un |une |du |des |de l'|«\s*)", "", after, flags=re.I)
        after = re.sub(r"^(étude|rapport|enquête|baromètre|analyse|données|chiffres|sondage)\s+(de l'|de la |de |d'|du |des )?",
                       "", after, flags=re.I)
        nm = RE_NAME.match(after)
        if nm and nm.group(1).split()[0] not in STOP_CAPS and nm.group(1).upper() not in NOT_TOOLS:
            return nm.group(1), "signal de source"
    par = RE_PAREN.search(text)
    if par and par.group(1).upper() not in NOT_TOOLS and par.group(1) not in STOP_CAPS:
        return par.group(1), "parenthèse"
    subj = RE_SUBJ.match(text)
    if subj:
        name = subj.group(1)
        if name[0].isupper() and name.split()[0] not in STOP_CAPS and name.upper() not in NOT_TOOLS \
                and all(w[0].isupper() or w[0].isdigit() for w in name.split()):
            return name, "sujet + verbe de source"
    low = text.lower()
    hit = next((t for t in rules.terms if in_text(t, low)), None)
    if hit:
        return hit, "liste du domaine"
    return None


def link_quality(href, site_host):
    """(poids manquant, niveau, libellé) : 0 = source valable, 0.5 = faible, 1 = ne compte pas."""
    h = (href or "").strip()
    if not h or h == "#" or re.match(r"^(javascript|mailto|tel):", h, re.I):
        return 1, "alerte", "lien vide"
    if re.match(r"^https?://([^/]*\.)?(example\.(com|org|net)|localhost|127\.0\.0\.1|[^/]+\.(test|local|invalid|example))(:\d+)?(/|$)", h, re.I) \
            or re.search(r"(votre-?site|mon-?site|nom-?de-?domaine|lorem)", h, re.I):
        return 1, "alerte", "lien de démonstration"
    u = urlparse(urljoin(f"https://{site_host or 'article.invalid'}/", h))
    host = (u.hostname or "").removeprefix("www.")
    if not re.match(r"^https?:", h, re.I) or (site_host and host == site_host):
        return 0.5, "moyen", "lien interne, pas une source externe"
    if re.search(r"(^|\.)(google|bing|duckduckgo|qwant|ecosia)\.[a-z.]+$", host) and re.search(r"/search|[?&]q=", u.path + "?" + u.query):
        return 0.5, "moyen", "lien vers une recherche"
    if u.path in ("", "/") and not u.query:
        return 0.5, "moyen", "lien vers une page d'accueil, pas vers l'étude"
    return 0, "ok", "lien vers la source"


# --------------------------------------------------------------------------
# Récupération des articles
# --------------------------------------------------------------------------
def fetch_posts(site, max_posts=50, pause=0.5):
    """Récupère les articles publiés via /wp-json/wp/v2/posts (pagination incluse)."""
    base = site.rstrip("/") + "/wp-json/wp/v2/posts"
    posts, page = [], 1
    while len(posts) < max_posts:
        per_page = min(100, max_posts - len(posts))
        url = f"{base}?per_page={per_page}&page={page}&status=publish&_embed=author,wp:term"
        req = urllib.request.Request(url, headers={"User-Agent": "audit-eeat/2.0", "Accept": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                batch = json.loads(r.read().decode("utf-8"))
                total_pages = int(r.headers.get("X-WP-TotalPages", page))
        except urllib.error.HTTPError as e:
            if e.code == 400 and page > 1:
                break  # page au-delà de la dernière
            sys.exit(f"Erreur HTTP {e.code} sur {url}. L'API REST est-elle désactivée ou protégée ?")
        except urllib.error.URLError as e:
            sys.exit(f"Impossible de joindre {site} : {e.reason}")
        if not batch:
            break
        posts.extend(batch)
        print(f"  page {page}/{total_pages} : {len(batch)} article(s)")
        if page >= total_pages:
            break
        page += 1
        time.sleep(pause)  # politesse envers le serveur
    return posts[:max_posts]


def normalize_post(p):
    """Ramène un article de l'API (ou d'un JSON simplifié) à un format commun."""
    def val(x):
        return x.get("rendered", "") if isinstance(x, dict) else (x or "")
    emb = p.get("_embedded", {}) or {}
    a = (emb.get("author") or [{}])[0] if isinstance((emb.get("author") or [{}])[0], dict) else {}
    cats = [t.get("name", "") for grp in (emb.get("wp:term") or []) for t in (grp or []) if isinstance(t, dict)]
    return {
        "url": p.get("link", ""),
        "title": html.unescape(re.sub(r"<[^>]+>", "", val(p.get("title")))).strip(),
        "date": (p.get("date") or "")[:10],
        "modified": (p.get("modified") or "")[:10],
        "author": a.get("name", "") or p.get("author_name", "") or "",
        "author_bio": a.get("description", "") or "",
        "author_url": a.get("url", "") or "",
        "categories": cats,
        "html": val(p.get("content")),
    }


# --------------------------------------------------------------------------
# Découpage du HTML en blocs (titres / paragraphes / légendes / liens)
# --------------------------------------------------------------------------
class BlockParser(HTMLParser):
    BLOCKS = {"h1", "h2", "h3", "h4", "h5", "h6", "p", "li", "td", "blockquote", "figcaption"}
    VOID = {"br", "img", "hr", "input", "meta", "link", "source", "wbr", "area", "col", "embed", "param", "track"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.blocks, self.stack, self.cur = [], [], None
        self.a_href, self.a_text, self.in_a = None, "", False
        self.skip_depth, self.open_tags = 0, []

    def _noise(self, tag, attrs):
        cls = (dict(attrs).get("class") or "") + " " + (dict(attrs).get("id") or "")
        return tag in NOISE_TAGS or any(n in cls for n in NOISE_CLASSES)

    def handle_starttag(self, tag, attrs):
        if tag in self.VOID:
            if tag == "br" and self.cur is not None and not self.skip_depth:
                self.cur["text"] += " "
            return
        self.open_tags.append(tag)
        if self.skip_depth:
            self.skip_depth += 1
            return
        if self._noise(tag, attrs):
            self.skip_depth = 1
            return
        if tag in self.BLOCKS:
            if self.cur is not None:
                self.stack.append(self.cur)
            t = "h" if tag[0] == "h" and tag[1:].isdigit() else ("cap" if tag == "figcaption" else "p")
            self.cur = {"type": t, "text": "", "links": []}
        elif tag == "a" and dict(attrs).get("href") is not None:
            self.in_a, self.a_text, self.a_href = True, "", dict(attrs).get("href")

    def handle_endtag(self, tag):
        if tag in self.VOID:
            return
        if self.open_tags and self.open_tags[-1] == tag:
            self.open_tags.pop()
        if self.skip_depth:
            self.skip_depth -= 1
            return
        if tag == "a" and self.in_a:
            self.in_a = False
            txt = re.sub(r"\s+", " ", self.a_text).strip()
            if self.cur is not None and txt:
                self.cur["links"].append({"text": norm(txt), "href": self.a_href})
        elif tag in self.BLOCKS and self.cur is not None:
            self.cur["text"] = norm(re.sub(r"\s+", " ", self.cur["text"]).strip())
            if self.cur["text"]:
                self.blocks.append(self.cur)
            self.cur = self.stack.pop() if self.stack else None

    def handle_data(self, data):
        if self.skip_depth:
            return
        if self.cur is not None:
            self.cur["text"] += data
        if self.in_a:
            self.a_text += data


def norm(s):
    return s.replace("’", "'").replace("‘", "'").replace("`", "'").replace("´", "'") \
            .replace(" ", " ").replace(" ", " ")


def parse_blocks(content):
    content = norm(content)
    if re.search(r"</?(p|h[1-6]|li|div|a|ul|ol)[\s>/]", content, re.I):
        bp = BlockParser()
        bp.feed(content)
        return bp.blocks
    # Texte brut : on devine les titres (lignes courtes sans ponctuation finale)
    lines, blocks = content.split("\n"), []
    for i, l in enumerate(lines):
        t = l.strip()
        if not t:
            continue
        nxt = next((x for x in lines[i + 1:] if x.strip()), "")
        heading = t.startswith("#") or (len(RE_WORD.findall(t)) <= 12 and not re.search(r"[.!?:;,…]$", t)
                                        and not re.match(r"^[-*•\d]", t) and bool(nxt))
        blocks.append({"type": "h" if heading else "p", "text": t.lstrip("# "),
                       "links": [{"text": u, "href": u} for u in re.findall(r"https?://\S+", t)]})
    return blocks


def sentences(text):
    return [s.strip() for s in re.split(r"(?<=[.!?…])\s+|\n+", text) if len(s.strip()) > 2]


def words(s):
    return RE_WORD.findall(s)


# --------------------------------------------------------------------------
# Contrôles automatiques (mêmes règles que la page interactive)
# --------------------------------------------------------------------------
def analyze(post, rules):
    blocks = parse_blocks(post["html"])
    sents = [(s, b) for b in blocks if b["type"] == "p" for s in sentences(b["text"])]
    body = "\n".join(b["text"] for b in blocks)
    n_words = len(words(body))
    site_host = (urlparse(post.get("url") or "").hostname or "").removeprefix("www.")
    try:
        pub = datetime.strptime(post["date"], "%Y-%m-%d").date()
    except ValueError:
        pub = date.today()
    F = {k: [] for k, _, _ in CRITERIA}  # signaux par critère : (niveau, signal, extrait)
    S, why = {}, {}

    # 1. Expérience
    anon = named = metric = missed = 0
    for i, (s, _) in enumerate(sents):
        if not RE_FIRST.search(s):
            continue
        ctx = s + " " + (sents[i + 1][0] if i + 1 < len(sents) else "")
        tool = is_tool_named(ctx, rules)
        has_metric = RE_METRIC.search(ctx)
        if tool:
            named += 1
            metric += bool(has_metric)
            F["exp"].append(("ok" if has_metric else "moyen",
                             ("Expérience nommée et chiffrée" if has_metric else "Outil nommé, sans mesure")
                             + f" · {tool[0]} ({tool[1]})", s))
        else:
            anon += 1
            F["exp"].append(("alerte", "Première personne, rien d'identifiable", s))
            if not rules.domain_on and any(in_text(t, ctx.lower()) for t in rules.all_seo_terms):
                missed += 1
                F["exp"].append(("info", "Outil en minuscules que seule la liste SEO reconnaît", s))
    if not anon and not named:
        S["exp"], why["exp"] = 1, ("Aucun témoignage à la première personne : pas un défaut, un manque "
                                   "d'information. Chercher captures, cas clients, données propres.")
    elif anon and not named:
        S["exp"], why["exp"] = 0, f"{anon} témoignage(s) sans outil, produit ni site identifiable."
    elif metric and not anon:
        S["exp"], why["exp"] = 2, "Outils nommés et résultats chiffrés."
    else:
        S["exp"], why["exp"] = 1, f"{named} expérience(s) nommée(s), {anon} anonyme(s), {metric} chiffrée(s)."

    # 2. Sources
    stats, unlinked, hedges_bad = 0, 0.0, 0

    def best_link(s, b):
        q = [link_quality(a["href"], site_host) for a in b["links"] if a["text"] and a["text"] in s]
        return min(q, key=lambda x: x[0]) if q else None

    for i, (s, b) in enumerate(sents):
        low = s.lower()
        lq = best_link(s, b)
        linked = lq is not None and lq[0] < 1
        if any(h in low for h in HEDGES):
            nq = best_link(*sents[i + 1]) if i + 1 < len(sents) else None
            next_linked = nq is not None and nq[0] < 1
            if (linked or next_linked) and re.search(r"\d", s):
                F["src"].append(("moyen", "Nuance méthodologique (source liée)", s))
            else:
                hedges_bad += 1
                F["src"].append(("alerte", "Formule d'auto-protection", s))
        if RE_STAT.search(s):
            stats += 1
            if lq and lq[0] == 0:
                F["src"].append(("ok", "Chiffre avec lien vers la source", s))
                continue
            if lq and lq[0] == 0.5:
                unlinked += 0.5
                F["src"].append(("moyen", f"Chiffre avec {lq[2]} (compte pour moitié)", s))
                continue
            unlinked += 1
            src = is_brand_cited(s, rules)
            pre = f"Chiffre avec {lq[2]}" if lq else "Chiffre"
            if src:
                F["src"].append(("alerte" if lq else "moyen",
                                 f"{pre} : attribué à {src[0]}{'' if lq else ' sans lien'} ({src[1]})", s))
            else:
                F["src"].append(("alerte", f"{pre}, sans source nommée" if lq else "Chiffre sans source nommée", s))
    u = f"{unlinked:g}".replace(".", ",")
    if not stats:
        S["src"], why["src"] = 1, "Aucun chiffre détecté : vérifier les affirmations à la main."
    elif unlinked == 0 and hedges_bad == 0:
        S["src"], why["src"] = 2, f"{stats} chiffre(s), tous liés à leur source."
    elif unlinked / stats > 0.5 or hedges_bad >= 2:
        S["src"], why["src"] = 0, f"{u}/{stats} chiffre(s) sans lien valable, {hedges_bad} formule(s) d'auto-protection."
    else:
        S["src"], why["src"] = 1, f"{u}/{stats} chiffre(s) sans lien valable, {hedges_bad} formule(s) d'auto-protection."

    # 3. Temporel
    impossible = risky = 0
    for s, _ in sents:
        low = s.lower()
        for y in map(int, re.findall(r"\b((?:19|20)\d{2})\b", s)):
            if y > pub.year:
                impossible += 1
                F["time"].append(("alerte", f"Année {y} postérieure à la publication", s))
            elif y == pub.year:
                m = next((i for i, mo in enumerate(MONTHS) if re.search(mo + r"\s+" + str(y), low)), None)
                if m is not None and m + 1 > pub.month:
                    impossible += 1
                    F["time"].append(("alerte", f"{MONTHS[m]} {y} est après la publication", s))
                elif RE_FULLYEAR.search(s):
                    impossible += 1
                    F["time"].append(("alerte", f"Données « annuelles » {y} avant la fin de l'année", s))
                elif RE_STUDY.search(s):
                    risky += 1
                    F["time"].append(("moyen", f"Étude de {y} à vérifier", s))
    S["time"] = 0 if impossible else (1 if risky else 2)
    why["time"] = (f"{impossible} date(s) impossible(s)." if impossible else
                   f"{risky} étude(s) de {pub.year} à vérifier." if risky else "Aucune incohérence temporelle.")

    # 4. Structure
    heads = []
    for i, b in enumerate(blocks):
        if b["type"] == "h":
            w = 0
            for nb in blocks[i + 1:]:
                if nb["type"] == "h":
                    break
                w += len(words(nb["text"]))
            if not RE_HEAD_SKIP.search(b["text"].strip()):
                heads.append((b["text"], w))
    thin = 0
    for t, w in heads[1:]:
        if w < 50 and not re.search(r"conclusion", t, re.I):
            thin += 1
            F["struct"].append(("alerte", f"Section de {w} mots", t))
    for t, w in heads:
        m = re.search(r"\b(\d+)\s+(outils|extensions|plugins|étapes|astuces|conseils|erreurs|recettes|modèles|produits)\b", t, re.I)
        if m:
            F["struct"].append(("moyen", f"Promet {m.group(1)} {m.group(2)} : compter les éléments", t))
        if re.search(r"\b(liste|top|comparatif)\b", t, re.I) and w < 80:
            F["struct"].append(("alerte", "Liste annoncée quasi vide", t))
    if body.strip() and not re.search(r"[.!?…»)\]]$", body.strip()):
        F["struct"].append(("alerte", "Fin de texte tronquée", body.strip()[-120:]))
    bad = sum(1 for f in F["struct"] if f[0] == "alerte")
    S["struct"] = 1 if not heads else (0 if bad >= 2 else (1 if F["struct"] else 2))
    why["struct"] = f"{len(heads)} section(s), {thin} de moins de 50 mots." if heads else "Aucun titre de contenu détecté."

    # 5. Densité
    cl = fill = 0
    for s, _ in sents:
        hit = next((p for p, r in rules.cliches if r.search(s)), None)
        if hit:
            cl += 1
            F["dens"].append(("moyen", f"Formule creuse : {hit}", s))
            continue
        dh = next((p for p, r in rules.dom_cliches if r.search(s)), None)
        if dh:
            cl += 1
            F["dens"].append(("moyen", f"Formule creuse du domaine : {dh}", s))
            continue
        fh = next((p for p, r in rules.fillers if r.search(s)), None)
        if fh:
            fill += 1
            F["dens"].append(("info", f"Connecteur banal (1/4 de poids) : {fh}", s))
    long_s = [s for s, _ in sents if len(words(s)) >= 8]
    sets = [{w for w in words(s.lower()) if len(w) > 3} for s in long_s]
    rep = 0
    for i in range(len(sets)):
        for j in range(i + 1, len(sets)):
            inter = len(sets[i] & sets[j])
            union = len(sets[i] | sets[j]) or 1
            if inter / union >= 0.5:
                rep += 1
                F["dens"].append(("alerte", f"Phrase répétée ({round(inter / union * 100)} %)", long_s[j]))
    per1k = (cl + fill * 0.25 + rep * 2) / n_words * 1000 if n_words else 0
    S["dens"] = 1 if not n_words else (0 if per1k >= 12 else (1 if per1k >= 4 else 2))
    why["dens"] = (f"{cl} formule(s) creuse(s), {fill} connecteur(s) banal(s), {rep} répétition(s) "
                   f"pour {n_words} mots (indice {per1k:.1f} pour 1 000 mots).".replace(".", ",", 1))

    # 6. Auteur : lu dans l'API (la note reste à confirmer)
    name = (post.get("author") or "").strip()
    bio = post.get("author_bio") or ""
    checks = [
        bool(name) and name.lower() not in {"admin", "administrator", "administrateur", "rédaction", "redaction", "webmaster"},
        len(bio) >= 40,
        bool(post.get("author_url")) or bool(re.search(r"linkedin\.com/in/|profiles\.wordpress\.org", bio, re.I)),
        bool(post.get("categories")) and (not rules.domain_on or any(
            re.search(r"seo|wordpress|référencement|web", c, re.I) for c in post.get("categories", []))),
    ]
    c = sum(checks)
    S["auth"] = 2 if c >= 4 else (1 if c >= 2 else 0)
    labels = ["auteur nommé", "bio", "lien de profil", "catégorie cohérente"]
    why["auth"] = ("Signaux trouvés dans l'API : " + (", ".join(l for l, ok in zip(labels, checks) if ok) or "aucun")
                   + ". Mentions légales et réputation à vérifier sur le site.")

    return {"scores": S, "why": why, "findings": F, "words": n_words, "impossible": impossible,
            "headings": len(heads), "missed": missed}


# --------------------------------------------------------------------------
# Export Excel
# --------------------------------------------------------------------------
def export_xlsx(rows, out, site, mode_label):
    from openpyxl import Workbook
    from openpyxl.comments import Comment
    from openpyxl.formatting.rule import CellIsRule, FormulaRule
    from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
    from openpyxl.utils import get_column_letter as L
    from openpyxl.worksheet.datavalidation import DataValidation

    FN, TEAL = "Arial", "0E6B63"
    f = lambda **k: Font(name=FN, **k)
    side = Side(style="thin", color="D5DDDB")
    box = Border(left=side, right=side, top=side, bottom=side)
    head = PatternFill("solid", fgColor=TEAL)
    inp = PatternFill("solid", fgColor="FFF7D6")
    red, amb, grn = (PatternFill("solid", fgColor=c) for c in ("F7E0DD", "F7ECD9", "E3F1E4"))
    ctr = Alignment(horizontal="center", vertical="top", wrap_text=True)
    wrap = Alignment(wrap_text=True, vertical="top")

    wb = Workbook()
    A = wb.active
    A.title = "Audit"

    # Paramètres
    P = wb.create_sheet("Paramètres")
    P["A1"] = "Paramètres de la grille"; P["A1"].font = f(bold=True, size=14, color=TEAL)
    P["A2"] = "Modifiez les cellules jaunes : tout le classeur se recalcule."; P["A2"].font = f(italic=True, color="586866")
    for c, h in enumerate(["Critère", "Poids"], 1):
        P.cell(4, c, h).font = f(bold=True, color="FFFFFF"); P.cell(4, c).fill = head
    for i, (_, name, w) in enumerate(CRITERIA):
        P.cell(5 + i, 1, name).font = f()
        P.cell(5 + i, 2, w).font = f(color="0000FF"); P.cell(5 + i, 2).fill = inp
    P["A11"] = "Total des poids"; P["B11"] = "=SUM(B5:B10)"
    for r, (lab, v) in enumerate([("Seuil « Fiable » (≥)", SEUIL_FIABLE), ("Seuil « À vérifier » (≥)", SEUIL_VERIFIER),
                                  ("Plafond si critère éliminatoire", PLAFOND),
                                  ("Note par défaut « Auteur / site » si la cellule est vide", 1)], 13):
        P.cell(r, 1, lab).font = f(); P.cell(r, 2, v).font = f(color="0000FF"); P.cell(r, 2).fill = inp
    P.column_dimensions["A"].width = 58; P.column_dimensions["B"].width = 10

    # Audit
    A["A1"] = "Audit E-E-A-T en lot"; A["A1"].font = f(bold=True, size=16, color=TEAL)
    A["A2"] = (f"Source : {site} · extrait le {date.today():%d/%m/%Y} · mode {mode_label}. Notes pré-remplies par le "
               "script : relisez et corrigez les cellules jaunes. « Stat introuvable » et « Faux témoignage » "
               "demandent une vérification humaine. Le script vérifie la forme, jamais le fond.")
    A["A2"].font = f(italic=True, color="586866"); A.merge_cells("A2:U2"); A["A2"].alignment = wrap
    A.row_dimensions[2].height = 32
    heads = ["N°", "URL", "Titre", "Publié le", "Modifié le", "Auteur", "Mots",
             "Expérience", "Sources", "Temporel", "Structure", "Densité", "Auteur / site",
             "Date impossible", "Stat introuvable", "Faux témoignage",
             "Score /100", "Verdict", "Statut", "Action", "Principaux signaux"]
    for c, h in enumerate(heads, 1):
        cell = A.cell(4, c, h)
        cell.font = f(bold=True, color="FFFFFF"); cell.fill = head; cell.alignment = ctr; cell.border = box
    A["H3"] = "Notes 0-2 (suggérées, à confirmer)"; A.merge_cells("H3:M3")
    A["N3"] = "Éliminatoires (Oui / Non)"; A.merge_cells("N3:P3")
    for c in ("H3", "N3"):
        A[c].font = f(bold=True, color=TEAL); A[c].alignment = Alignment(horizontal="center")

    first = 5
    last = first + max(len(rows), 1) - 1
    for i, (post, res) in enumerate(rows):
        r = first + i
        sc = res["scores"]
        top = [x for k, _, _ in CRITERIA for x in res["findings"][k] if x[0] == "alerte"][:3]
        vals = [i + 1, post["url"], post["title"], _d(post["date"]), _d(post["modified"]), post["author"],
                res["words"], sc["exp"], sc["src"], sc["time"], sc["struct"], sc["dens"], sc["auth"],
                "Oui" if res["impossible"] else "Non", None, None]
        for c, v in enumerate(vals, 1):
            A.cell(r, c, v)
        brut = (f'ROUND((H{r}*Paramètres!$B$5+I{r}*Paramètres!$B$6+J{r}*Paramètres!$B$7+K{r}*Paramètres!$B$8'
                f'+L{r}*Paramètres!$B$9+IF(M{r}="",Paramètres!$B$16,M{r})*Paramètres!$B$10)'
                f'/2/Paramètres!$B$11*100,1)')
        A.cell(r, 17, f'=IF(COUNTIF(N{r}:P{r},"Oui")>0,MIN(Paramètres!$B$15,{brut}),{brut})')
        A.cell(r, 18, f'=IF(Q{r}>=Paramètres!$B$13,"Fiable",IF(Q{r}>=Paramètres!$B$14,"À vérifier","Suspect"))')
        A.cell(r, 19, f'=IF(OR(O{r}="",P{r}=""),"Provisoire","Validé")')
        A.cell(r, 20, f'=IF(R{r}="Fiable","Conserver",IF(R{r}="À vérifier","Enrichir : preuve d\'expérience + liens",'
                      f'"Réécrire ou dépublier"))')
        signals = " | ".join(k for _, k, _ in top) or "Aucune alerte automatique"
        if res["missed"]:
            signals += f" | Mode générique : {res['missed']} outil(s) en minuscules non reconnu(s)"
        A.cell(r, 21, signals)
        for c in range(1, 22):
            cell = A.cell(r, c)
            cell.border = box; cell.font = f(size=10)
            cell.alignment = ctr if 4 <= c <= 20 else wrap
            if 8 <= c <= 16:
                cell.fill = inp
        A.cell(r, 4).number_format = A.cell(r, 5).number_format = "DD/MM/YYYY"
        A.cell(r, 17).number_format = "0.0"; A.cell(r, 17).font = f(size=10, bold=True)
        for j, (k, _, _) in enumerate(CRITERIA):
            if res["why"][k]:
                A.cell(r, 8 + j).comment = Comment(res["why"][k], "Script")

    dv_n = DataValidation(type="whole", operator="between", formula1="0", formula2="2", allow_blank=True,
                          showErrorMessage=True, error="Saisissez 0, 1 ou 2.")
    dv_y = DataValidation(type="list", formula1='"Oui,Non"', allow_blank=True)
    A.add_data_validation(dv_n); A.add_data_validation(dv_y)
    dv_n.add(f"H{first}:M{last}"); dv_y.add(f"N{first}:P{last}")
    rng = f"H{first}:M{last}"
    A.conditional_formatting.add(rng, FormulaRule(formula=[f'AND(H{first}<>"",H{first}=0)'], fill=red,
                                                  font=Font(name=FN, bold=True, color="B63326")))
    A.conditional_formatting.add(rng, CellIsRule(operator="equal", formula=["1"], fill=amb))
    A.conditional_formatting.add(rng, CellIsRule(operator="equal", formula=["2"], fill=grn))
    A.conditional_formatting.add(f"N{first}:P{last}", CellIsRule(operator="equal", formula=['"Oui"'], fill=red,
                                                                 font=Font(name=FN, bold=True, color="B63326")))
    for label, fill, col in (("Suspect", red, "B63326"), ("À vérifier", amb, "9A6414"), ("Fiable", grn, "2E7D32")):
        A.conditional_formatting.add(f"Q{first}:R{last}", FormulaRule(formula=[f'$R{first}="{label}"'], fill=fill,
                                                                      font=Font(name=FN, bold=True, color=col)))
    for c, w in enumerate([5, 34, 40, 11, 11, 14, 7, 10, 9, 9, 10, 9, 10, 10, 10, 10, 9, 11, 11, 22, 50], 1):
        A.column_dimensions[L(c)].width = w
    A.freeze_panes = "D5"
    A.auto_filter.ref = f"A4:U{last}"

    # Signaux (détail)
    D = wb.create_sheet("Signaux")
    for c, h in enumerate(["N°", "Titre", "Critère", "Niveau", "Signal", "Extrait"], 1):
        D.cell(1, c, h).font = f(bold=True, color="FFFFFF"); D.cell(1, c).fill = head
    r = 2
    for i, (post, res) in enumerate(rows):
        for k, name, _ in CRITERIA:
            for lvl, sig, txt in res["findings"][k]:
                for c, v in enumerate([i + 1, post["title"], name, lvl, sig, txt[:300]], 1):
                    D.cell(r, c, v).font = f(size=10); D.cell(r, c).alignment = wrap
                r += 1
    for val, fill in (("alerte", red), ("moyen", amb), ("ok", grn)):
        D.conditional_formatting.add(f"D2:D{max(r, 2)}", CellIsRule(operator="equal", formula=[f'"{val}"'], fill=fill))
    for c, w in enumerate([5, 36, 24, 9, 44, 80], 1):
        D.column_dimensions[L(c)].width = w
    D.freeze_panes = "A2"
    D.auto_filter.ref = f"A1:F{max(r - 1, 1)}"

    # Synthèse
    S = wb.create_sheet("Synthèse", 1)
    S["A1"] = "Rapport de conformité E-E-A-T"; S["A1"].font = f(bold=True, size=16, color=TEAL)
    S["A2"] = f"{site} · {date.today():%d/%m/%Y} · mode {mode_label}"; S["A2"].font = f(italic=True, color="586866")
    rg = lambda col: f"Audit!{col}{first}:{col}{last}"
    items = [("Articles audités", f"=COUNT({rg('Q')})", "0"),
             ("Score moyen /100", f'=IFERROR(AVERAGE({rg("Q")}),"-")', "0.0"),
             ("Fiables", f'=COUNTIF({rg("R")},"Fiable")', "0"),
             ("À vérifier", f'=COUNTIF({rg("R")},"À vérifier")', "0"),
             ("Suspects", f'=COUNTIF({rg("R")},"Suspect")', "0"),
             ("Part de suspects", "=IFERROR(B8/B4,0)", "0.0%"),
             ("Avec au moins un critère éliminatoire",
              f'=SUMPRODUCT(--((({rg("N")}="Oui")+({rg("O")}="Oui")+({rg("P")}="Oui"))>0))', "0"),
             ("Audits encore provisoires", f'=COUNTIF({rg("S")},"Provisoire")', "0")]
    for c, h in enumerate(["Indicateur", "Valeur"], 1):
        S.cell(3, c, h).font = f(bold=True, color="FFFFFF"); S.cell(3, c).fill = head
    for i, (lab, fm, nf) in enumerate(items, 4):
        S.cell(i, 1, lab).font = f(); S.cell(i, 2, fm).number_format = nf; S.cell(i, 2).font = f()
    for c, h in enumerate(["Critère", "Moyenne /2", "Articles à 0"], 1):
        S.cell(13, c, h).font = f(bold=True, color="FFFFFF"); S.cell(13, c).fill = head
    for j, col in enumerate("HIJKLM"):
        S.cell(14 + j, 1, f"=Paramètres!A{5 + j}").font = f()
        S.cell(14 + j, 2, f'=IFERROR(AVERAGE({rg(col)}),"-")').number_format = "0.00"
        S.cell(14 + j, 3, f"=COUNTIF({rg(col)},0)")
    S.conditional_formatting.add("B14:B19", CellIsRule(operator="lessThan", formula=["1"], fill=red))
    S["A21"] = ("Limites : le script vérifie la forme (outils nommés, liens, dates, structure, formules creuses), "
                "jamais le fond. Un texte bien imité peut obtenir un bon score ; seule la vérification des sources "
                "et de l'auteur tranche. Règles écrites pour le français.")
    S["A21"].font = f(italic=True, color="586866"); S.merge_cells("A21:C23"); S["A21"].alignment = wrap
    S.column_dimensions["A"].width = 42; S.column_dimensions["B"].width = 12; S.column_dimensions["C"].width = 13

    wb.save(out)


def _d(s):
    try:
        return datetime.strptime(s, "%Y-%m-%d").date()
    except (TypeError, ValueError):
        return None


def _read_list(path):
    with open(path, encoding="utf-8") as fh:
        return [l.strip() for l in fh if l.strip() and not l.startswith("#")]


# --------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(description="Audit E-E-A-T en lot d'un blog WordPress.")
    ap.add_argument("site", nargs="?", help="URL du site WordPress, ex. https://monblog.fr")
    ap.add_argument("--json", help="Fichier JSON d'articles (format de l'API WordPress) au lieu du site")
    ap.add_argument("--max", type=int, default=50, help="Nombre maximum d'articles (défaut : 50)")
    ap.add_argument("--out", default=f"audit-eeat-{date.today():%Y-%m-%d}.xlsx", help="Fichier Excel de sortie")
    ap.add_argument("--domaine", choices=["seo", "aucun"], default="seo",
                    help="Renfort de domaine : seo (SEO / WordPress, défaut) ou aucun (mode générique)")
    ap.add_argument("--outils", help="Fichier texte : vos outils et marques, un par ligne (remplace la liste SEO)")
    ap.add_argument("--formules", help="Fichier texte : vos formules creuses de domaine, une par ligne")
    a = ap.parse_args()
    if not a.site and not a.json:
        ap.error("indiquez l'URL du site ou --json fichier.json")

    if a.outils or a.formules:
        rules = Rules(_read_list(a.outils) if a.outils else [], _read_list(a.formules) if a.formules else [])
        mode = "domaine personnalisé"
    elif a.domaine == "seo":
        rules, mode = Rules(DOMAIN_SEO, DOMAIN_SEO_CLICHES), "renfort SEO / WordPress"
    else:
        rules, mode = Rules(), "générique"

    if a.json:
        with open(a.json, encoding="utf-8") as fh:
            raw = json.load(fh)[: a.max]
        source = a.json
    else:
        print(f"Récupération des articles de {a.site} …")
        raw = fetch_posts(a.site, a.max)
        source = a.site
    if not raw:
        sys.exit("Aucun article trouvé.")

    rows = []
    for p in raw:
        post = normalize_post(p)
        rows.append((post, analyze(post, rules)))

    export_xlsx(rows, a.out, source, mode)
    print(f"\n{len(rows)} article(s) audité(s) en mode {mode} → {a.out}")
    print("Notes les plus basses (suggestions, avant relecture humaine) :")
    ranked = sorted(rows, key=lambda x: sum((x[1]["scores"][k] or 0) * w for k, _, w in CRITERIA))
    for post, res in ranked[:5]:
        flag = " [date impossible]" if res["impossible"] else ""
        print(f"  - {post['title'][:70]}{flag}")
    missed = sum(r["missed"] for _, r in rows)
    if missed:
        print(f"\nMode générique : {missed} témoignage(s) citent un outil en minuscules que seule la liste SEO "
              "reconnaît. Relancez avec --domaine seo pour en tenir compte.")


if __name__ == "__main__":
    main()
