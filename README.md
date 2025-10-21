AI hỗ trợ giải phương trình - Repo mẫu cho THCS Nguyễn Huệ

Cấu trúc:
- backend/: Flask API có hai endpoint:
   - POST /api/solve  -> nhận {'problem':'2x+3=7'} JSON
   - POST /api/solve_image -> multipart/form-data file 'image'
- website_app/: frontend tĩnh, gọi API backend

Hướng dẫn nhanh (Deploy to Render):
1) Fork hoặc tải repo này về tài khoản GitHub của thầy (hoặc tạo repo mới `ai-giai-phuong-trinh` và push toàn bộ nội dung).
2) Tạo tài khoản Render.com và kết nối GitHub.
3) Tạo Web Service mới trên Render:
   - Repository: chọn repo `ai-giai-phuong-trinh`
   - Branch: main
   - Root Directory: (để trống)
   - Build Command: pip install -r backend/requirements.txt
   - Start Command: gunicorn backend.server:app
4) Trong phần Environment variables của service trên Render, thêm:
   - OPENAI_API_KEY = <api key của thầy>
5) Deploy. Render sẽ cung cấp URL dạng https://<your-service>.onrender.com
6) Trên GitHub, bật GitHub Pages cho branch main (root) để host frontend: hoặc
   - Copy toàn bộ thư mục website_app/* vào root của repo (index.html at root), commit và enable GitHub Pages (Settings -> Pages -> Branch: main, folder: / (root)).
   - Hoặc dùng Render để serve frontend cùng backend (cần chỉnh server để serve static files).

Lưu ý quan trọng:
- Không commit OPENAI_API_KEY lên GitHub công khai.
- Để AI hiểu ảnh, Render phải có URL public (server sẽ phục vụ ảnh trên /uploads/<filename>).
- Mọi vấn đề, mình sẽ hỗ trợ từng bước.
