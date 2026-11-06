import json
import urllib.request
import urllib.parse

# URL officielle du JSON source
OFFICIAL_URL = "https://aidoku-community.github.io/sources/index.min.json"
# URL de base officielle pour retrouver les fichiers .aix et icônes d'origine
OFFICIAL_BASE_URL = "https://aidoku-community.github.io/sources/"

# On garde ta liste pour bloquer des sources spécifiques (au cas où elles ne seraient pas taguées 18+)
BANNED_KEYWORDS = [
    "e-hentai", "hitomi", "myreadingmanga", "myrockmanga", 
    "simplyhentai", "nhentai", "armageddon", "athrea scans", 
    "dynasty scans", "hentai2read", "hentaifox", "hiperdex", 
    "lilymanga", "mangadistrict", "mangatx", "mangago", 
    "manhwax", "omegascans", "toonily", "toonily.me", "webtoonxyz",
    "danke fürs lesen"
]

# Listes tierces ajoutées : seules les sources tout public (rating 0) sont reprises
EXTRA_LISTS = [
    "https://moomooo95.github.io/aidoku-french-sources/index.min.json",
    "https://raw.githubusercontent.com/suiyuran/aidoku-zh-sources/refs/heads/main/public/index.min.json",
]

# Doublons d'un site déjà couvert par la liste officielle sous un autre id
EXTRA_SKIP_IDS = {"zh.baozimh1", "zh.baozimh2", "zh.bilicomic", "zh.zerobywns"}


def fetch_json(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=30) as response:
        return json.loads(response.read().decode('utf-8'))


def is_banned(source):
    name_lower = source.get("name", "").lower()
    id_lower = source.get("id", "").lower()
    return any(banned in name_lower or banned in id_lower for banned in BANNED_KEYWORDS)


def extra_sources(known_ids):
    """Récupère les sources tout public des listes tierces, converties au format 0.7+."""
    result = []
    for list_url in EXTRA_LISTS:
        try:
            data = fetch_json(list_url)
        except Exception as e:
            print(f"Liste ignorée ({list_url}) : {e}")
            continue
        base = list_url.rsplit("/", 1)[0] + "/"
        entries = data.get("sources", []) if isinstance(data, dict) else data
        for s in entries:
            sid = s.get("id", "")
            rating = s.get("contentRating", s.get("nsfw", 0))
            if rating != 0 or sid in known_ids or sid in EXTRA_SKIP_IDS or is_banned(s):
                continue
            if "file" in s:  # ancien format -> nouveau format
                s = {
                    "id": sid,
                    "name": s.get("name", sid),
                    "version": s.get("version", 1),
                    "iconURL": urllib.parse.urljoin(base, "icons/" + s["icon"]),
                    "downloadURL": urllib.parse.urljoin(base, "sources/" + s["file"]),
                    "languages": [s.get("lang", "multi")],
                    "contentRating": 0,
                }
            else:
                for key in ("downloadURL", "iconURL"):
                    if key in s and not s[key].startswith("http"):
                        s[key] = urllib.parse.urljoin(base, s[key])
            known_ids.add(sid)
            result.append(s)
    return result

def filter_sources():
    try:
        # 1. Télécharger le JSON officiel
        req = urllib.request.Request(OFFICIAL_URL, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode('utf-8'))

        # 2. Filtrer les sources et rendre les liens absolus
        filtered_sources = []
        for source in data.get("sources", []):
            name_lower = source.get("name", "").lower()
            id_lower = source.get("id", "").lower()
            
            # Récupérer la note de contenu (0 par défaut si elle n'existe pas)
            rating = source.get("contentRating", 0)
            
            # Vérifier si c'est dans la liste noire OU si c'est tagué 18+ (rating == 2)
            is_banned = any(banned in name_lower or banned in id_lower for banned in BANNED_KEYWORDS)
            is_18_plus = (rating == 2)
            
            # On n'ajoute la source que si elle n'est ni bannie, ni 18+
            if not is_banned and not is_18_plus:
                # Transformer les liens relatifs en liens absolus
                if "downloadURL" in source and not source["downloadURL"].startswith("http"):
                    source["downloadURL"] = urllib.parse.urljoin(OFFICIAL_BASE_URL, source["downloadURL"])
                if "iconURL" in source and not source["iconURL"].startswith("http"):
                    source["iconURL"] = urllib.parse.urljoin(OFFICIAL_BASE_URL, source["iconURL"])
                    
                filtered_sources.append(source)
        
        known_ids = {s.get("id") for s in data.get("sources", [])}
        filtered_sources.extend(extra_sources(known_ids))
        filtered_sources.sort(key=lambda s: s.get("id", ""))
        data["sources"] = filtered_sources

        # 3. Sauvegarder dans le fichier index.json local
        with open("index.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, separators=(',', ':'))
            
        print("Mise à jour et filtrage terminés avec succès.")
        
    except Exception as e:
        print(f"Erreur lors du filtrage : {e}")

if __name__ == "__main__":
    filter_sources()
