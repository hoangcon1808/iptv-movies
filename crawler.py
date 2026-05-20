import requests, json, time, os

DB_FILE = "movies_database.json"

def fetch(url):
    try: return requests.get(url, timeout=10).json()
    except: return None

def main():
    # 1. Load database cũ (để giữ phim cũ)
    db = json.load(open(DB_FILE, "r", encoding="utf-8")) if os.path.exists(DB_FILE) else {}

    sources = [
        {"name": "OPhim", "list": "https://ophim1.com/danh-sach/phim-moi-cap-nhat?page=", "detail": "https://ophim1.com/phim"},
        {"name": "KKPhim", "list": "https://phimapi.com/danh-sach/phim-moi-cap-nhat?page=", "detail": "https://phimapi.com/phim"}
    ]

    # 2. Quét trang 1-10 để lấy phim mới nhất và phim chưa có trong DB
    for src in sources:
        for page in range(1, 11):
            data = fetch(f"{src['list']}{page}")
            if not data: continue
            for item in data.get('items', []):
                slug = item['slug']
                if slug not in db: # Nếu phim này chưa từng được cào
                    detail = fetch(f"{src['detail']}/{slug}")
                    if detail:
                        db[slug] = detail
                        print(f"Đã nạp vào kho: {item['name']}")
    
    # 3. Lưu lại kho phim
    json.dump(db, open(DB_FILE, "w", encoding="utf-8"), ensure_ascii=False)

    # 4. Xuất ra file M3U cho VAX Player
    m3u = "#EXTM3U\n"
    for slug, detail in db.items():
        movie = detail.get('movie', {})
        for ep in detail.get('episodes', [{}])[0].get('server_data', []):
            m3u += f'#EXTINF:-1 tvg-logo="{movie.get("thumb_url")}",{movie.get("name")} - {ep["name"]}\n{ep["link_m3u8"]}\n'
    open("movies.m3u", "w", encoding="utf-8").write(m3u)

if __name__ == "__main__":
    main()
