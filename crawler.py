import requests, json, time, os

DB_FILE = "movies_database.json"
M3U_FILE = "movies.m3u"

def fetch(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(url, headers=headers, timeout=15)
        return response.json() if response.status_code == 200 else None
    except: return None

def main():
    # 1. Load database cũ (nếu có) để giữ phim cũ lại
    db = json.load(open(DB_FILE, "r", encoding="utf-8")) if os.path.exists(DB_FILE) else {}

    sources = [
        {"name": "OPhim", "list": "https://ophim1.com/danh-sach/phim-moi-cap-nhat?page=", "detail": "https://ophim1.com/phim"},
        {"name": "KKPhim", "list": "https://phimapi.com/danh-sach/phim-moi-cap-nhat?page=", "detail": "https://phimapi.com/phim"}
    ]

    print("--- Bắt đầu quy trình cào phim thông minh ---")
    
    # 2. Quét trang 1-10 để cập nhật phim mới
    for src in sources:
        print(f"Đang quét nguồn: {src['name']}")
        for page in range(1, 11):
            data = fetch(f"{src['list']}{page}")
            if not data or not data.get('items'): continue
            
            for item in data.get('items', []):
                slug = item['slug']
                # Chỉ gọi API chi tiết nếu phim này chưa có trong DB (tiết kiệm API & thời gian)
                if slug not in db:
                    time.sleep(0.5)
                    detail = fetch(f"{src['detail']}/{slug}")
                    if detail:
                        db[slug] = detail
                        print(f" + Đã thêm: {item['name']}")

    # 3. Lưu lại database
    json.dump(db, open(DB_FILE, "w", encoding="utf-8"), ensure_ascii=False)

    # 4. Xuất file M3U mới nhất
    m3u_content = "#EXTM3U\n"
    for slug, detail in db.items():
        movie = detail.get('movie', detail.get('item', {}))
        thumb = movie.get('thumb_url', '')
        name = movie.get('name', 'Phim')
        
        episodes = detail.get('episodes', [])
        for server in episodes:
            server_name = server.get('server_name', 'Server')
            for ep in server.get('server_data', []):
                m3u_content += f'#EXTINF:-1 tvg-logo="{thumb}",{name} - {server_name} [{ep["name"]}]\n{ep["link_m3u8"]}\n'

    with open(M3U_FILE, "w", encoding="utf-8") as f:
        f.write(m3u_content)
    
    print(f"Hoàn thành! Tổng số phim trong kho: {len(db)}")

if __name__ == "__main__":
    main()
