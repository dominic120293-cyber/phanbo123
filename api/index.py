from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse, HTMLResponse
import io
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ALLOCATION import run_optimization

app = FastAPI(title="HỆ THỐNG PHÂN BỔ TỐI ƯU TỰ ĐỘNG")

@app.get("/", response_class=HTMLResponse)
async def root():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Hệ thống phân bổ tối ưu tự động</title>
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                margin: 0;
                padding: 0;
                display: flex;
                justify-content: center;
                align-items: center;
                min-height: 100vh;
            }
            .container {
                background: white;
                border-radius: 16px;
                padding: 40px 50px;
                box-shadow: 0 20px 40px rgba(0,0,0,0.2);
                max-width: 500px;
                width: 100%;
                text-align: center;
            }
            h1 {
                margin-top: 0;
                color: #333;
                font-size: 28px;
                font-weight: 600;
            }
            .subtitle {
                color: #666;
                margin-bottom: 30px;
                font-size: 16px;
            }
            .file-upload-wrapper {
                margin-bottom: 25px;
                text-align: left;
            }
            .file-upload-wrapper label {
                display: block;
                font-weight: 500;
                margin-bottom: 8px;
                color: #444;
            }
            .file-upload-wrapper input[type="file"] {
                width: 100%;
                padding: 10px;
                border: 2px dashed #ccc;
                border-radius: 8px;
                background: #fafafa;
                cursor: pointer;
                transition: border-color 0.3s ease;
            }
            .file-upload-wrapper input[type="file"]:hover {
                border-color: #667eea;
            }
            .btn {
                background: #667eea;
                color: white;
                border: none;
                padding: 14px 28px;
                font-size: 18px;
                font-weight: 500;
                border-radius: 8px;
                cursor: pointer;
                transition: background 0.3s ease, transform 0.1s ease;
                width: 100%;
                margin-top: 10px;
            }
            .btn:hover {
                background: #5a6fd6;
            }
            .btn:active {
                transform: scale(0.97);
            }
            .btn:disabled {
                background: #aaa;
                cursor: not-allowed;
            }
            .loading {
                display: none;
                margin-top: 20px;
                color: #667eea;
                font-weight: 500;
            }
            .loading.active {
                display: block;
            }
            .result {
                display: none;
                margin-top: 20px;
                padding: 15px;
                background: #e8f5e9;
                border-radius: 8px;
                color: #2e7d32;
            }
            .result.active {
                display: block;
            }
            .result a {
                color: #1b5e20;
                font-weight: bold;
                text-decoration: underline;
                cursor: pointer;
            }
            .footer {
                margin-top: 30px;
                font-size: 12px;
                color: #aaa;
            }
            .spinner {
                display: inline-block;
                width: 20px;
                height: 20px;
                border: 3px solid #f3f3f3;
                border-top: 3px solid #667eea;
                border-radius: 50%;
                animation: spin 0.8s linear infinite;
                vertical-align: middle;
                margin-right: 10px;
            }
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚢 HỆ THỐNG PHÂN BỔ TỐI ƯU TỰ ĐỘNG</h1>
            <p class="subtitle">Tải lên file <strong>DATA.xlsx</strong> để tiến hành phân bổ container</p>

            <form id="uploadForm">
                <div class="file-upload-wrapper">
                    <label for="fileInput">📂 Chọn file Excel (định dạng .xlsx)</label>
                    <input type="file" id="fileInput" name="file" accept=".xlsx,.xls" required>
                </div>
                <button type="submit" class="btn" id="submitBtn">⚡ Chạy phân bổ</button>
            </form>

            <div class="loading" id="loading">
                <span class="spinner"></span> Đang xử lý, vui lòng chờ...
            </div>

            <div class="result" id="result">
                ✅ Phân bổ hoàn tất! <br>
                <a id="downloadLink" download="ketqua.xlsx">📥 Tải kết quả xuống</a>
            </div>

            <div class="footer">© 2026 - Hệ thống tối ưu container</div>
        </div>

        <script>
            document.getElementById('uploadForm').addEventListener('submit', async function(e) {
                e.preventDefault();

                const fileInput = document.getElementById('fileInput');
                const file = fileInput.files[0];
                if (!file) {
                    alert('Vui lòng chọn file!');
                    return;
                }

                const submitBtn = document.getElementById('submitBtn');
                const loading = document.getElementById('loading');
                const result = document.getElementById('result');

                // Reset trạng thái
                result.classList.remove('active');
                loading.classList.add('active');
                submitBtn.disabled = true;
                submitBtn.textContent = '⏳ Đang xử lý...';

                const formData = new FormData();
                formData.append('file', file);

                try {
                    const response = await fetch('/optimize', {
                        method: 'POST',
                        body: formData
                    });

                    if (!response.ok) {
                        const errorText = await response.text();
                        throw new Error(errorText || 'Lỗi không xác định');
                    }

                    // Lấy blob từ response
                    const blob = await response.blob();
                    const url = window.URL.createObjectURL(blob);

                    // Tạo link tải
                    const downloadLink = document.getElementById('downloadLink');
                    downloadLink.href = url;
                    // Đặt tên file dựa trên Content-Disposition hoặc mặc định
                    const contentDisposition = response.headers.get('Content-Disposition');
                    let filename = 'ketqua.xlsx';
                    if (contentDisposition) {
                        const match = contentDisposition.match(/filename=(.+)/);
                        if (match) filename = match[1].replace(/["']/g, '');
                    }
                    downloadLink.download = filename;

                    // Hiển thị kết quả
                    result.classList.add('active');
                    // Tự động click để tải về (tuỳ chọn)
                    // downloadLink.click();

                } catch (error) {
                    alert('❌ Lỗi: ' + error.message);
                } finally {
                    loading.classList.remove('active');
                    submitBtn.disabled = false;
                    submitBtn.textContent = '⚡ Chạy phân bổ';
                }
            });
        </script>
    </body>
    </html>
    """

# Các endpoint khác giữ nguyên (upload, optimize)
@app.get("/upload", response_class=HTMLResponse)
async def upload_form():
    # Có thể redirect về root hoặc trả về cùng HTML
    return await root()

@app.post("/optimize")
async def optimize(file: UploadFile = File(...)):
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="Chỉ chấp nhận file Excel (.xlsx, .xls)")

    try:
        contents = await file.read()
        file_like = io.BytesIO(contents)

        excel_buffer, total_rows, total_clashes = run_optimization(file_like)

        response = StreamingResponse(
            io.BytesIO(excel_buffer.getvalue()),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": f"attachment; filename=optimized_{file.filename}"
            }
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
