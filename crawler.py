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
    # Load dữ liệu cũ
    db = json.load(open(DB_FILE, "r", encoding="utf-8")) if os.path.exists(DB_FILE) else {}
    if "_meta" not in db:
        db["_meta"] = {"OPhim_old": 3, "KKPhim_old": 3, "NguonC_old": 3}

    sources = [
        {"name": "OPhim", "list": "https://ophim1.com/danh-sach/phim-moi-cap-nhat?page=", "detail": "https://ophim1.com/phim", "meta": "OPhim_old"},
        {"name": "KKPhim", "list": "https://phimapi.com/danh-sach/phim-moi-cap-nhat?page=", "detail": "https://phimapi.com/phim", "meta": "KKPhim_old"},
        {"name": "NguonC", "list": "https://phim.nguonc.com/api/films/phim-moi?page=", "detail": "https://phim.nguonc.com/api/film", "meta": "NguonC_old"}
    ]

    # Cào dữ liệu
    for src in sources:
        curr = db["_meta"].get(src["meta"], 1)
        for page in range(1, curr + 3):
            data = fetch(f"{src['list']}{page}")
            if not data: continue
            items = data.get('items') if src['name'] != "NguonC" else data.get('films')
            if not items: continue
            for item in items:
                slug = item.get('slug')
                if slug not in db:
                    time.sleep(0.3)
                    detail = fetch(f"{src['detail']}/{slug}")
                    if detail: db[slug] = detail
        db["_meta"][src["meta"]] = curr + 3

    json.dump(db, open(DB_FILE, "w", encoding="utf-8"), ensure_ascii=False)

    # Xuất file M3U với logic gom nhóm chuẩn
    playlists = {
        "single": "phim_le.m3u", "series": "phim_bo.m3u", 
        "hoathinh": "hoat_hinh.m3u", "tvshows": "tv_shows.m3u", "all": "all.m3u"
    }

    for p_type, filename in playlists.items():
        content = "#EXTM3U\n"
        for slug, detail in db.items():
            if slug == "_meta": continue
            
            movie = detail.get('movie', detail.get('film', detail.get('item', {})))
            if not movie: continue
            
            if p_type != "all":
                if movie.get('type') != p_type and not (p_type == "series" and movie.get('type') == 'series'):
                    continue
            
            name = movie.get('name', 'Phim')
            thumb = movie.get('thumb_url', movie.get('poster_url', ''))
            group = movie.get('type', 'Phim').capitalize()
            
            # Gom tất cả tập phim
            episodes_list = detail.get('episodes', detail.get('list_episodes', []))
            all_eps = []
            for ep_group in episodes_list:
                all_eps.extend(ep_group.get('server_data', ep_group.get('items', [])))
            
            # Sắp xếp và ép định dạng tập phim
            all_eps.sort(key=lambda x: str(x.get('name', '')))
            
            for ep in all_eps:
                # tvg-id chính là chìa khóa để app gom các tập vào 1 đầu mục
                content += f'#EXTINF:-1 tvg-id="{slug}" tvg-logo="{thumb}" group-title="{group}",{name} - Tập {ep.get("name")}\n{ep.get("link_m3u8")}\n'
        
        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)
        os.utime(filename, None)
    
    os.utime(DB_FILE, None)

if __name__ == "__main__":
    main()
