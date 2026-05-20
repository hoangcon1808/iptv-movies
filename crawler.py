import requests
import json
import time
import os

# Tên file lưu trữ phim
STORAGE_FILE = "movies_database.json"

def fetch_data(url):
    try:
        response = requests.get(url, timeout=15)
        if response.status_code == 200:
            return response.json()
    except: return None

def main():
    # Load database cũ nếu có
    if os.path.exists(STORAGE_FILE):
        with open(STORAGE_FILE, "r", encoding="utf-8") as f:
            database = json.load(f)
    else:
        database = {}

    sources = [
        {"name": "OPhim", "list_url": "https://ophim1.com/danh-sach/phim-moi-cap-nhat?page=", "detail_url": "https://ophim1.com/phim"},
        {"name": "KKPhim", "list_url": "https://phimapi.com/danh-sach/phim-moi-cap-nhat?page=", "detail_url": "https://phimapi.com/phim"}
    ]

    for src in sources:
        # Mỗi lần chạy chỉ quét 2 trang đầu để lấy phim mới nhất bổ sung vào DB
        for page in range(1, 3):
            data = fetch_data(f"{src['list_url']}{page}")
            if not data: continue
            items = data.get('items', [])
            for item in items:
                slug = item['slug']
                if slug not in database: # Chỉ quét chi tiết nếu chưa có trong DB
                    time.sleep(0.5)
                    detail = fetch_data(f"{src['detail_url']}/{slug}")
                    if detail:
                        database[slug] = detail
                        print(f"Đã thêm phim mới: {item['name']}")

    # Ghi lại database
    with open(STORAGE_FILE, "w", encoding="utf-8") as f:
        json.dump(database, f, ensure_ascii=False)

    # Sinh file M3U từ database
    m3u_content = "#EXTM3U\n"
    for slug, detail in database.items():
        movie_info = detail.get('movie', detail.get('item', {}))
        thumb = movie_info.get('thumb_url', '')
        name = movie_info.get('name', 'Phim')
        for server in detail.get('episodes', []):
            for ep in server.get('server_data', []):
                m3u_content += f'#EXTINF:-1 tvg-logo="{thumb}",{name} - {ep["name"]}\n{ep["link_m3u8"]}\n'

    with open("movies.m3u", "w", encoding="utf-8") as f:
        f.write(m3u_content)

if __name__ == "__main__":
    main()
