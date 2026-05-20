import requests, json, time, os

DB_FILE = "movies_database.json"

def fetch(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=15)
        return response.json() if response.status_code == 200 else None
    except: return None

def main():
    db = json.load(open(DB_FILE, "r", encoding="utf-8")) if os.path.exists(DB_FILE) else {}
    if "_meta" not in db:
        db["_meta"] = {"OPhim_old_page": 3, "KKPhim_old_page": 3}

    sources = [
        {"name": "OPhim", "list": "https://ophim1.com/danh-sach/phim-moi-cap-nhat?page=", "detail": "https://ophim1.com/phim", "meta_key": "OPhim_old_page"},
        {"name": "KKPhim", "list": "https://phimapi.com/danh-sach/phim-moi-cap-nhat?page=", "detail": "https://phimapi.com/phim", "meta_key": "KKPhim_old_page"}
    ]

    for src in sources:
        print(f"--- Đang xử lý nguồn: {src['name']} ---")
        
        for page in range(1, 3):
            data = fetch(f"{src['list']}{page}")
            if not data: continue
            for item in data.get('items', []):
                slug = item['slug']
                if slug not in db:
                    time.sleep(0.3)
                    detail = fetch(f"{src['detail']}/{slug}")
                    if detail: db[slug] = detail

        current_old_page = db["_meta"][src["meta_key"]]
        next_old_page = current_old_page + 5
        for page in range(current_old_page, next_old_page):
            data = fetch(f"{src['list']}{page}")
            if not data or not data.get('items'): continue
            for item in data.get('items', []):
                slug = item['slug']
                if slug not in db:
                    time.sleep(0.3)
                    detail = fetch(f"{src['detail']}/{slug}")
                    if detail: db[slug] = detail
        
        db["_meta"][src["meta_key"]] = next_old_page

    print(f"--- Hoàn tất! Tổng số phim hiện có: {len(db) - 1} ---")
    json.dump(db, open(DB_FILE, "w", encoding="utf-8"), ensure_ascii=False)

    playlists = {
        "single": {"filename": "phim_le.m3u", "content": "#EXTM3U\n"},
        "series": {"filename": "phim_bo.m3u", "content": "#EXTM3U\n"},
        "hoathinh": {"filename": "hoat_hinh.m3u", "content": "#EXTM3U\n"},
        "tvshows": {"filename": "tv_shows.m3u", "content": "#EXTM3U\n"},
        "other": {"filename": "phim_khac.m3u", "content": "#EXTM3U\n"}
    }

    for slug, detail in db.items():
        if slug == "_meta": continue 
        
        movie = detail.get('movie', detail.get('item', {}))
        thumb = movie.get('thumb_url', '')
        name = movie.get('name', 'Phim')
        
        movie_type = movie.get('type', 'other')
        if movie_type not in playlists: movie_type = "other"
            
        for server in detail.get('episodes', []):
            server_name = server.get('server_name', 'Server')
            for ep in server.get('server_data', []):
                playlists[movie_type]["content"] += f'#EXTINF:-1 tvg-logo="{thumb}",{name} - {server_name} [{ep["name"]}]\n{ep["link_m3u8"]}\n'

    for key, data in playlists.items():
        with open(data["filename"], "w", encoding="utf-8") as f:
            f.write(data["content"])

    # --- ĐOẠN CODE MỚI THÊM: TẠO FILE PLUGINS.JSON ---
    # Thay 'trungnt3891-stack' bằng đúng tên username GitHub của bạn nếu cần
    base_cdn = "https://cdn.jsdelivr.net/gh/trungnt3891-stack/iptv-movies@main"
    
    plugins_data = [
        {"name": "🎬 KHO PHIM LẺ", "url": f"{base_cdn}/phim_le.m3u", "type": "m3u"},
        {"name": "📺 KHO PHIM BỘ", "url": f"{base_cdn}/phim_bo.m3u", "type": "m3u"},
        {"name": "🐻 KHO HOẠT HÌNH", "url": f"{base_cdn}/hoat_hinh.m3u", "type": "m3u"},
        {"name": "🎤 KHO TV SHOWS", "url": f"{base_cdn}/tv_shows.m3u", "type": "m3u"}
    ]
    
    with open("plugins.json", "w", encoding="utf-8") as f:
        json.dump(plugins_data, f, ensure_ascii=False, indent=4)
    print("Đã tạo thành công file plugins.json")

if __name__ == "__main__":
    main()
