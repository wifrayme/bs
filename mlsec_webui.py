import os
import time
import threading
from flask import Flask, render_template_string, request, flash, redirect, url_for

app = Flask(__name__)
app.secret_key = 'mlsec_secret_key'

HTML = """
<!DOCTYPE html>
<html lang="zh">
<head>
    <meta charset="UTF-8">
    <title>DeepExploit Web 控制台</title>
    <style>
        body { font-family: monospace; background: #f2f2f2;}
        .container { width:600px; margin:auto; background:#fff; padding:32px; border-radius:8px; box-shadow:0 2px 10px #bbb;}
        input[type=text] { width:80%; padding:5px; }
        button { padding:6px 12px; }
        .msg { color: #206020; font-weight: bold; margin: 10px 0;}
        textarea { width:100%; min-height:220px; background:#222; color:#b3ffb3; font-size:15px; border-radius:4px; border:1px solid #ccc; padding:12px;}
    </style>
    <script>
    function pollLog(logfile) {
        if (!logfile) return;
        fetch('/log?file='+encodeURIComponent(logfile)+'&_t='+Date.now())
            .then(resp => resp.text())
            .then(txt => {
                document.getElementById("logbox").value = txt;
                setTimeout(function(){ pollLog(logfile); }, 2000);
            });
    }
    window.onload = function() {
        var logfile = "{{ logfile }}";
        if (logfile) pollLog(logfile);
    }
    </script>
</head>
<body>
<div class="container">
    <h2>DeepExploit 一键渗透测试</h2>
    <form method="post">
        <label>目标IP:</label>
        <input type="text" name="target_ip" value="{{target_ip or ''}}" required>
        <button type="submit">启动训练</button>
    </form>
    {% with messages = get_flashed_messages() %}
      {% if messages %}
        <div class="msg">{{ messages[0] }}</div>
      {% endif %}
    {% endwith %}
    <hr>
    <div>
        <small>只需输入目标ip即可运行自动化渗透测试<br>
        输出结果保存在/report/train目录下一个 DeepExploit_train_report.html 的HTML报告文件<br>
        黑龙江工程学院 智能21-2 钱以晨 制作</small>
    </div>
    <hr>
    <label>运行输出：</label>
    <textarea id="logbox" readonly>{{ logcontent or '' }}</textarea>
</div>
</body>
</html>
"""

DEEP_DIR = "/root/machine_learning_security/DeepExploit"

def run_deepexploit(ip, logfile):
    # 后台直接运行命令并输出到日志（也可以用 gnome-terminal -- bash -c "xxx | tee logfile; exec bash"）
    # 这里推荐用 tee, 这样网页和终端都可看日志
    cmd = f'cd {DEEP_DIR} && gnome-terminal -- bash -c "python3 DeepExploit.py -t {ip} -m train 2>&1 | tee {logfile}; exec bash"'
    os.system(cmd)

@app.route('/', methods=['GET', 'POST'])
def index():
    target_ip = ""
    logfile = ""
    logcontent = ""
    if request.method == "POST":
        target_ip = request.form.get("target_ip", "")
        if target_ip:
            # 日志文件名建议唯一，防止多用户覆盖
            logfile = f"deepexploit_{target_ip.replace('.', '_')}_{int(time.time())}.log"
            abs_logfile = os.path.join(DEEP_DIR, logfile)
            # 用线程防止阻塞
            t = threading.Thread(target=run_deepexploit, args=(target_ip, logfile))
            t.daemon = True
            t.start()
            flash(f"已启动训练，目标IP: {target_ip}，日志文件: {logfile}")
            return redirect(url_for('index', logfile=logfile))
        else:
            flash("请输入目标IP")
    else:
        logfile = request.args.get("logfile", "")
        if logfile:
            log_path = os.path.join(DEEP_DIR, logfile)
            if os.path.exists(log_path):
                with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
                    logcontent = f.read()
    return render_template_string(HTML, target_ip=target_ip, logfile=logfile, logcontent=logcontent)

@app.route('/log')
def getlog():
    logfile = request.args.get("file", "")
    if logfile and all(c.isalnum() or c in "._-" for c in logfile):  # 简单防止目录穿越
        log_path = os.path.join(DEEP_DIR, logfile)
        if os.path.exists(log_path):
            with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()
    return ""

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)