from flask import Flask, request, jsonify, send_from_directory, url_for
import os, openai, uuid, json
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"png","jpg","jpeg","gif"}

app = Flask(__name__, static_folder=None)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

openai.api_key = os.getenv("OPENAI_API_KEY")

SYSTEM_PROMPT = """Bạn là một trợ lý Toán bằng tiếng Việt chuyên giải và hướng dẫn từng bước các phương trình bậc nhất một ẩn cho học sinh lớp 8.
Khi nhận bài toán (dưới dạng văn bản hoặc dưới dạng ảnh có chữ viết tay/viết máy), hãy:
1) Xác định dạng bài (ví dụ: phương trình bậc nhất).
2) Nếu là ảnh, đọc nội dung trong ảnh (bằng khả năng nhận diện hình ảnh của model) và trích xuất bài làm/hệ số/bước làm.
3) Kiểm tra từng bước học sinh đã làm (nếu có) và chỉ ra lỗi cụ thể nếu có.
4) Trình bày lời giải chi tiết từng bước, đơn giản, dễ hiểu cho học sinh (dùng ngôn ngữ thân mật nhưng chuẩn xác).
5) Nếu học sinh sai ở bước nào, giải thích lỗi và đưa ví dụ tương tự để luyện tập.
Trả về JSON gồm các trường: 'format','analysis','steps' (list),'final_answer'."""

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.',1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/api/solve", methods=["POST"])
def solve():
    data = request.get_json() or {}
    problem = data.get("problem","").strip()
    if not problem:
        return jsonify({"error":"No problem provided"}),400
    user_prompt = f"Giải bài toán sau và hướng dẫn từng bước cho học sinh: {problem}\nTrả về JSON."
    try:
        resp = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role":"system","content": SYSTEM_PROMPT},
                {"role":"user","content": user_prompt}
            ],
            max_tokens=800,
            temperature=0.2,
        )
        content = resp['choices'][0]['message']['content'].strip()
        try:
            parsed = json.loads(content)
            return jsonify({"ok":True,"response":parsed})
        except Exception:
            return jsonify({"ok":True,"raw":content})
    except Exception as e:
        return jsonify({"error":str(e)}),500

@app.route("/api/solve_image", methods=["POST"])
def solve_image():
    # Accept multipart/form-data with file 'image' and optional 'note' (additional text)
    if 'image' not in request.files:
        return jsonify({"error":"No image file part"}),400
    file = request.files['image']
    if file.filename == "":
        return jsonify({"error":"No selected file"}),400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # make unique
        filename = f"{uuid.uuid4().hex}_{filename}"
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(filepath)
        # Construct public URL for the uploaded file (served by this app)
        image_url = request.url_root.rstrip('/') + url_for('uploaded_file', filename=filename)
        # Build prompt to allow model to inspect image via URL
        user_prompt = f"Đây là ảnh chứa bài làm: {image_url}\\nHãy đọc nội dung trong ảnh, trích xuất bài toán và các bước học sinh đã làm (nếu có). Kiểm tra lỗi và hướng dẫn sửa: trả về CHUẨN JSON như mô tả."
        try:
            resp = openai.ChatCompletion.create(
                model="gpt-4o-mini",
                messages=[
                    {"role":"system","content": SYSTEM_PROMPT},
                    {"role":"user","content": user_prompt}
                ],
                max_tokens=1200,
                temperature=0.2,
            )
            content = resp['choices'][0]['message']['content'].strip()
            try:
                parsed = json.loads(content)
                return jsonify({"ok":True,"response":parsed,"image_url":image_url})
            except Exception:
                return jsonify({"ok":True,"raw":content,"image_url":image_url})
        except Exception as e:
            return jsonify({"error":str(e)}),500
    else:
        return jsonify({"error":"File type not allowed"}),400

@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename, as_attachment=False)

from flask import send_from_directory
import os

# ---- Các route để hiển thị giao diện web ----
@app.route('/')
def home():
    return send_from_directory(os.path.join(os.path.dirname(__file__), '../website_app'), 'index.html')

@app.route('/<path:path>')
def static_files(path):
    return send_from_directory(os.path.join(os.path.dirname(__file__), '../website_app'), path)


# ---- Chạy Flask server ----
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
