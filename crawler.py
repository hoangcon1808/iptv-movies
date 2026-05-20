import requests, json, time, os

DB_FILE = "movies_database.json"

def fetch(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=15)
        return response.json() if response.status_code == 200 else None
    except:
        return None

def main():
    db = json.load(open(DB_FILE, "r", encoding="utf-8")) if os.path.exists(DB_FILE) else {}
    if "_meta" not in db:
        db["_meta"] = {"OPhim_old": 3, "KKPhim_old": 3, "NguonC_old": 3}

    sources = [
        {"name": "OPhim", "list": "https://ophim1.com/danh-sach/phim-moi-cap-nhat?page=", "detail": "https://ophim1.com/phim", "meta": "OPhim_old"},
        {"name": "KKPhim", "list": "https://phimapi.com/danh-sach/phim-moi-cap-nhat?page=", "detail": "https://phimapi.com/phim", "meta": "KKPhim_old"},
        {"name": "NguonC", "list": "https://phim.nguonc.com/api/films/phim-moi?page=", "detail": "https://phim.nguonc.com/api/film", "meta": "NguonC_old"}
    ]

    for src in sources:
        curr = db["_meta"].get(src["meta"], 1)
        for page in range(1, curr + 3):
            data = fetch(f"{src['list']}{page}")
            if not data:
                continue
            items = data.get('items') if src['name'] != "NguonC" else data.get('films')
            if not items:
                continue
            for item in items:
                slug = item.get('slug')
                if slug not in db:
                    time.sleep(0.3)
                    detail = fetch(f"{src['detail']}/{slug}")
                    if detail:
                        db[slug] = detail
        db["_meta"][src["meta"]] = curr + 3

    json.dump(db, open(DB_FILE, "w", encoding="utf-8"), ensure_ascii=False)

    playlists = {
        "single": "phim_le.m3u",
        "series": "phim_bo.m3u",
        "hoathinh": "hoat_hinh.m3u",
        "tvshows": "tv_shows.m3u",
        "all": "all.m3u"
    }

    for p_type, filename in playlists.items():
        content = "#EXTM3U\n"
        for slug, detail in db.items():
            if slug == "_meta":
                continue
            movie = detail.get('movie', detail.get('film', detail.get('item', {})))
            if not movie:
                continue
            
            if p_type != "all":
                if movie.get('type') != p_type and not (p_type == "series" and movie.get('type') == 'series'):
                    continue
            
            thumb = movie.get('thumb_url', movie.get('poster_url', ''))
            name = movie.get('name', 'Phim')
            episodes = detail.get('episodes', detail.get('list_episodes', []))
            
            for ep_group in episodes:
                eps = ep_group.get('server_data', ep_group.get('items', []))
                for ep in sorted(eps, key=lambda x: str(x['name']), reverse=True):
                    group = movie.get('type', 'Phim')
                    content += f'#EXTINF:-1 tvg-logo="{thumb}" group-title="{group}",{name} - {ep["name"]}\n{ep["link_m3u8"]}\n'
        
        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)
        os.utime(filename, None)
    
    os.utime(DB_FILE, None)

if __name__ == "__main__":
    main()
