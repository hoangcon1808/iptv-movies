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
        
        # 1. BẮT TREND (Quét 2 trang đầu)
        for page in range(1, 3):
            data = fetch(f"{src['list']}{page}")
            if not data: continue
            for item in data.get('items', []):
                slug = item['slug']
                if slug not in db:
                    time.sleep(0.3)
                    detail = fetch(f"{src['detail']}/{slug}")
                    if detail: db[slug] = detail

        # 2. KHẢO CỔ HỌC (Quét 5 trang cũ)
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

    # 3. TẠO TỪ ĐIỂN CHỨA 4 FILE M3U RIÊNG BIỆT
    playlists = {
        "single": {"filename": "phim_le.m3u", "content": "#EXTM3U\n"},
        "series": {"filename": "phim_bo.m3u", "content": "#EXTM3U\n"},
        "hoathinh": {"filename": "hoat_hinh.m3u", "content": "#EXTM3U\n"},
        "tvshows": {"filename": "tv_shows.m3u", "content": "#EXTM3U\n"},
        "other": {"filename": "phim_khac.m3u", "content": "#EXTM3U\n"} # Backup nếu web nguồn ghi sai loại phim
    }

    # 4. BÓC TÁCH VÀ PHÂN LOẠI
    for slug, detail in db.items():
        if slug == "_meta": continue 
        
        movie = detail.get('movie', detail.get('item', {}))
        thumb = movie.get('thumb_url', '')
        name = movie.get('name', 'Phim')
        
        # Lấy loại phim từ API (thường là single, series, hoathinh, tvshows)
        movie_type = movie.get('type', 'other')
        if movie_type not in playlists:
            movie_type = "other"
            
        for server in detail.get('episodes', []):
            server_name = server.get('server_name', 'Server')
            for ep in server.get('server_data', []):
                # Nhét link vào đúng file m3u của loại phim đó
                playlists[movie_type]["content"] += f'#EXTINF:-1 tvg-logo="{thumb}",{name} - {server_name} [{ep["name"]}]\n{ep["link_m3u8"]}\n'

    # 5. LƯU TẤT CẢ RA FILE
    for key, data in playlists.items():
        with open(data["filename"], "w", encoding="utf-8") as f:
            f.write(data["content"])

if __name__ == "__main__":
    main()
