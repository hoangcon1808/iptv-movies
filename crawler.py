# Xuất file M3U và ép cập nhật thời gian
    # Thêm 'all' vào danh sách để tạo file gộp
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
            if slug == "_meta": continue
            movie = detail.get('movie', detail.get('film', detail.get('item', {})))
            if not movie: continue
            
            # Logic: Nếu là 'all' thì nhận tất cả, ngược lại lọc theo loại
            if p_type != "all":
                if movie.get('type') != p_type and not (p_type == "series" and movie.get('type') == 'series'):
                    continue
            
            thumb = movie.get('thumb_url', movie.get('poster_url', ''))
            name = movie.get('name', 'Phim')
            episodes = detail.get('episodes', detail.get('list_episodes', []))
            
            for ep_group in episodes:
                eps = ep_group.get('server_data', ep_group.get('items', []))
                for ep in sorted(eps, key=lambda x: str(x['name']), reverse=True):
                    # group-title sẽ hiển thị tên danh mục trong app
                    group = movie.get('type', 'Phim')
                    content += f'#EXTINF:-1 tvg-logo="{thumb}" group-title="{group}",{name} - {ep["name"]}\n{ep["link_m3u8"]}\n'
        
        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)
        os.utime(filename, None)
