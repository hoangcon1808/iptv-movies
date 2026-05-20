import requests
import json
import time

def fetch_data(url):
    """Hàm gọi API chung có xử lý chống block (Timeout & Headers)"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print(f"Lỗi khi truy cập {url}: {e}")
    return None

def main():
    # Danh sách các nguồn phát dùng chung cấu trúc OPhim CMS và NguonC
    # Lưu ý: Các site cấu trúc OPhim thường dùng link phimapi.com hoặc ophim1.com làm kho chứa
    sources = [
        {
            "name": "NguonC",
            "list_url": "https://phim.nguonc.com/api/films/phim-moi-cap-nhat?page=1",
            "detail_url": "https://phim.nguonc.com/api/film"
        },
        {
            "name": "OPhim",
            "list_url": "https://ophim1.com/danh-sach/phim-moi-cap-nhat?page=1",
            "detail_url": "https://ophim1.com/phim"
        },
        {
            "name": "KKPhim",
            "list_url": "https://phimapi.com/danh-sach/phim-moi-cap-nhat?page=1",
            "detail_url": "https://phimapi.com/phim"
        },
        # Bạn có thể bật các nguồn dưới đây nếu tìm được chính xác đường dẫn API của chúng
        # (Thông thường thêm /api/ trước đường dẫn hoặc dùng /danh-sach/...)
        {
            "name": "YanHH3D",
            "list_url": "https://yanhh3d.io/api/danh-sach/phim-moi-cap-nhat?page=1", 
            "detail_url": "https://yanhh3d.io/api/phim"
        }
    ]
    
    m3u_content = "#EXTM3U\n"
    count_tracks = 0

    for src in sources:
        print(f"--- Đang quét dữ liệu từ: {src['name']} ---")
        data = fetch_data(src['list_url'])
        
        if not data:
            continue
            
        # OPhim và NguonC đều trả danh sách trong mảng 'items' hoặc 'data.items'
        items = data.get('items', data.get('data', {}).get('items', []))
        
        for movie in items:
            slug = movie.get('slug')
            if not slug:
                continue
                
            # Tránh spam request quá nhanh làm sập API của họ
            time.sleep(0.5) 
            
            detail_data = fetch_data(f"{src['detail_url']}/{slug}")
            if not detail_data:
                continue
                
            movie_info = detail_data.get('movie', detail_data.get('item', {}))
            if not movie_info:
                continue
                
            movie_name = movie_info.get('name', 'Phim Ẩn Danh')
            thumb_url = movie_info.get('thumb_url', movie_info.get('poster_url', ''))
            
            # Phân loại nhóm phim
            category = "Phim"
            if movie_info.get('category'):
                category = movie_info['category'][0].get('name', 'Phim')
            elif movie_info.get('type'):
                category = movie_info['type'].capitalize()
                
            group_title = f"{src['name']} - {category}"
            
            # Lấy danh sách tập phim
            episodes = detail_data.get('episodes', [])
            for server in episodes:
                server_name = server.get('server_name', 'Server')
                server_data = server.get('server_data', [])
                
                for ep in server_data:
                    ep_name = ep.get('name', '1')
                    stream_url = ep.get('link_m3u8', '')
                    
                    if stream_url and "m3u8" in stream_url:
                        display_name = f"{movie_name} - {server_name} [Tập {ep_name}]"
                        m3u_content += f'#EXTINF:-1 tvg-logo="{thumb_url}" group-title="{group_title}",{display_name}\n'
                        m3u_content += f'{stream_url}\n'
                        count_tracks += 1

    with open("movies.m3u", "w", encoding="utf-8") as f:
        f.write(m3u_content)
        
    print(f"Hoàn thành! Tổng cộng: {count_tracks} tập phim.")

if __name__ == "__main__":
    main()
