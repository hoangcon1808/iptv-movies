import requests, json, time, os

DB_FILE = "movies_database.json"
M3U_FILE = "movies.m3u"

def fetch(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=15)
        return response.json() if response.status_code == 200 else None
    except: return None

def main():
    db = json.load(open(DB_FILE, "r", encoding="utf-8")) if os.path.exists(DB_FILE) else {}
    
    # Tạo bộ nhớ để theo dõi tiến độ "đào lùi" quá khứ
    if "_meta" not in db:
        db["_meta"] = {"OPhim_old_page": 3, "KKPhim_old_page": 3}

    sources = [
        {"name": "OPhim", "list": "https://ophim1.com/danh-sach/phim-moi-cap-nhat?page=", "detail": "https://ophim1.com/phim", "meta_key": "OPhim_old_page"},
        {"name": "KKPhim", "list": "https://phimapi.com/danh-sach/phim-moi-cap-nhat?page=", "detail": "https://phimapi.com/phim", "meta_key": "KKPhim_old_page"}
    ]

    for src in sources:
        print(f"--- Đang xử lý nguồn: {src['name']} ---")
        
        # 1. QUÉT PHIM MỚI (Trang 1 - 2) để bắt trend
        print(">> Nhiệm vụ 1: Cập nhật phim mới...")
        for page in range(1, 3):
            data = fetch(f"{src['list']}{page}")
            if not data: continue
            for item in data.get('items', []):
                slug = item['slug']
                if slug not in db:
                    time.sleep(0.3)
                    detail = fetch(f"{src['detail']}/{slug}")
                    if detail: db[slug] = detail

        # 2. ĐÀO LÙI QUÁ KHỨ (Quét 5 trang cũ tiếp theo)
        current_old_page = db["_meta"][src["meta_key"]]
        next_old_page = current_old_page + 5
        print(f">> Nhiệm vụ 2: Khảo cổ học từ trang {current_old_page} đến {next_old_page - 1}...")
        
        for page in range(current_old_page, next_old_page):
            data = fetch(f"{src['list']}{page}")
            if not data or not data.get('items'): continue
            for item in data.get('items', []):
                slug = item['slug']
                if slug not in db:
                    time.sleep(0.3)
                    detail = fetch(f"{src['detail']}/{slug}")
                    if detail: db[slug] = detail
        
        # Cập nhật lại cột mốc quá khứ cho lần chạy 3 tiếng sau
        db["_meta"][src["meta_key"]] = next_old_page

    print(f"--- Hoàn tất! Tổng số phim hiện có: {len(db) - 1} ---")
    json.dump(db, open(DB_FILE, "w", encoding="utf-8"), ensure_ascii=False)

    # XUẤT FILE M3U
    m3u_content = "#EXTM3U\n"
    for slug, detail in db.items():
        if slug == "_meta": continue # Bỏ qua dòng ghi nhớ hệ thống
        
        movie = detail.get('movie', detail.get('item', {}))
        thumb = movie.get('thumb_url', '')
        name = movie.get('name', 'Phim')
        
        for server in detail.get('episodes', []):
            server_name = server.get('server_name', 'Server')
            for ep in server.get('server_data', []):
                m3u_content += f'#EXTINF:-1 tvg-logo="{thumb}",{name} - {server_name} [{ep["name"]}]\n{ep["link_m3u8"]}\n'

    with open(M3U_FILE, "w", encoding="utf-8") as f:
        f.write(m3u_content)

if __name__ == "__main__":
    main()
