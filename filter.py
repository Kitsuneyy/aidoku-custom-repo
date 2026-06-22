import json
import urllib.request

# Remplace ceci par l'URL du répertoire Aidoku officiel que tu utilisais
OFFICIAL_URL = "https://aidoku-community.github.io/sources/index.min.json" 

# Liste des mots-clés à bannir (basé sur ta demande)
BANNED_KEYWORDS = [
    "e-hentai", "hitomi.la", "myreadingmanga", "myrockmanga", 
    "simplyhentai", "nhentai", "armageddon", "athrea scans", 
    "dynasty scans", "hentai2read", "hentaifox", "hiperdex", 
    "lilymanga", "mangadistrict", "mangatx", "mangago", 
    "manhwax", "omegascans", "toonily", "toonily.me", "webtoonxyz"
]

def filter_sources():
    try:
        # 1. Télécharger le JSON officiel
        req = urllib.request.Request(OFFICIAL_URL, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode('utf-8'))

        # 2. Filtrer les sources
        filtered_sources = []
        for source in data.get("sources", []):
            name_lower = source.get("name", "").lower()
            id_lower = source.get("id", "").lower()
            
            # Vérifier si un des mots-clés bannis est dans le nom ou l'ID
            is_banned = any(banned in name_lower or banned in id_lower for banned in BANNED_KEYWORDS)
            
            if not is_banned:
                filtered_sources.append(source)
        
        data["sources"] = filtered_sources

        # 3. Sauvegarder dans le fichier index.json local
        with open("index.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, separators=(',', ':'))
            
        print("Mise à jour et filtrage terminés avec succès.")
        
    except Exception as e:
        print(f"Erreur lors du filtrage : {e}")

if __name__ == "__main__":
    filter_sources()
