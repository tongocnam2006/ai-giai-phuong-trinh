document.getElementById('exampleBtn').addEventListener('click',()=>{
  document.getElementById('problem').value="2x + 3 = 7";
});
document.getElementById('solveBtn').addEventListener('click', async ()=>{
  const problem = document.getElementById('problem').value.trim();
  const resultDiv = document.getElementById('result');
  resultDiv.innerHTML = 'Đang xử lý...';
  if(!problem){ resultDiv.innerHTML='Vui lòng nhập phương trình.'; return; }
  try{
    const res = await fetch('/api/solve', {
      method:'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({problem})
    });
    const data = await res.json();
    if(data.error){ resultDiv.innerText = 'Lỗi: ' + data.error; return; }
    if(data.response){
      const r = data.response;
      let html='';
      if(r.format) html += '<strong>Loại bài:</strong> '+ (r.format) + '<br/>';
      if(r.analysis) html += '<strong>Phân tích:</strong> '+ (r.analysis) + '<br/>';
      if(r.steps){
        html += '<strong>Các bước:</strong><ol>';
        for(const s of r.steps) html += '<li>'+s+'</li>';
        html += '</ol>';
      }
      if(r.final_answer) html += '<strong>Kết luận:</strong> '+ r.final_answer + '<br/>';
      if(r.raw) html += '<pre>'+r.raw+'</pre>';
      resultDiv.innerHTML = html;
    } else if(data.raw){
      resultDiv.innerHTML = '<pre>'+data.raw+'</pre>';
    } else {
      resultDiv.innerText = 'Không nhận được phản hồi hợp lệ.';
    }
  }catch(e){
    resultDiv.innerText = 'Lỗi kết nối: '+e;
  }
});

document.getElementById('uploadImageBtn').addEventListener('click', async ()=>{
  const input = document.getElementById('imageInput');
  const resultDiv = document.getElementById('result');
  if(!input.files || input.files.length===0){ resultDiv.innerText = 'Vui lòng chọn ảnh.'; return; }
  const file = input.files[0];
  resultDiv.innerHTML = 'Đang tải ảnh và chờ AI phân tích...';
  try{
    const form = new FormData();
    form.append('image', file);
    const res = await fetch('/api/solve_image', { method:'POST', body: form });
    const data = await res.json();
    if(data.error){ resultDiv.innerText = 'Lỗi: ' + data.error; return; }
    let html='';
    if(data.image_url) html += '<strong>Ảnh đã tải lên:</strong> <a href="'+data.image_url+'" target="_blank">Xem ảnh</a><br/>';
    if(data.response){
      const r = data.response;
      if(r.format) html += '<strong>Loại bài:</strong> '+ (r.format) + '<br/>';
      if(r.analysis) html += '<strong>Phân tích:</strong> '+ (r.analysis) + '<br/>';
      if(r.steps){
        html += '<strong>Các bước:</strong><ol>';
        for(const s of r.steps) html += '<li>'+s+'</li>';
        html += '</ol>';
      }
      if(r.final_answer) html += '<strong>Kết luận:</strong> '+ r.final_answer + '<br/>';
    } else if(data.raw){
      html += '<pre>'+data.raw+'</pre>';
    } else {
      html += 'Không nhận được phản hồi hợp lệ.';
    }
    resultDiv.innerHTML = html;
  }catch(e){
    resultDiv.innerText = 'Lỗi kết nối: '+e;
  }
});