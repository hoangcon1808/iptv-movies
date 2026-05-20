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
        # 1. BẮT TREND
        for page in range(1, 3):
            data = fetch(f"{src['list']}{page}")
            if not data: continue
            for item in data.get('items', []):
                if item['slug'] not in db:
                    time.sleep(0.3)
                    detail = fetch(f"{src['detail']}/{item['slug']}")
                    if detail: db[item['slug']] = detail

        # 2. KHẢO CỔ HỌC
        current_page = db["_meta"][src["meta_key"]]
        for page in range(current_page, current_page + 5):
            data = fetch(f"{src['list']}{page}")
            if not data or not data.get('items'): continue
            for item in data.get('items', []):
                if item['slug'] not in db:
                    time.sleep(0.3)
                    detail = fetch(f"{src['detail']}/{item['slug']}")
                    if detail: db[item['slug']] = detail
        db["_meta"][src["meta_key"]] = current_page + 5

    json.dump(db, open(DB_FILE, "w", encoding="utf-8"), ensure_ascii=False)

    # 3. XUẤT FILE M3U VỚI GROUP-TITLE & SẮP XẾP TẬP
    playlists = {
        "single": "phim_le.m3u",
        "series": "phim_bo.m3u",
        "hoathinh": "hoat_hinh.m3u",
        "tvshows": "tv_shows.m3u"
    }

    for p_type, filename in playlists.items():
        m3u_content = "#EXTM3U\n"
        for slug, detail in db.items():
            if slug == "_meta": continue
            
            movie = detail.get('movie', detail.get('item', {}))
            if movie.get('type') != p_type and not (p_type == "series" and movie.get('type') == 'series'):
                continue
                
            thumb = movie.get('thumb_url', '')
            name = movie.get('name', 'Phim')
            
            for server in detail.get('episodes', []):
                # Sắp xếp tập mới nhất lên đầu
                sorted_eps = sorted(server.get('server_data', []), key=lambda x: x['name'], reverse=True)
                for ep in sorted_eps:
                    # group-title giúp APTV tự gom vào thư mục
                    m3u_content += f'#EXTINF:-1 tvg-logo="{thumb}" group-title="{name}",{name} - {ep["name"]}\n{ep["link_m3u8"]}\n'
        
        with open(filename, "w", encoding="utf-8") as f:
            f.write(m3u_content)

if __name__ == "__main__":
    main()
