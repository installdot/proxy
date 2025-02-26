from flask import Flask, request, render_template_string, jsonify
from proxy_manager import proxy_manager
import os

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Store index.html as a string
INDEX_HTML = """ 
<!DOCTYPE html>
<html>
<head>
    <title>Rotating Proxy Server</title>
    <script>
        function updateProxyStatus() {
            fetch("/get_proxy")
                .then(response => response.json())
                .then(data => {
                    document.getElementById("current_proxy").innerText = data.current_proxy || "None";
                    document.getElementById("next_proxy").innerText = data.next_proxy || "None";
                    document.getElementById("time_remaining").innerText = data.time_until_rotation + "s";
                });
        }
        setInterval(updateProxyStatus, 1000);
        window.onload = updateProxyStatus;
    </script>
</head>
<body>
    <h2>Enter Proxies (One per line)</h2>
    <form method="POST">
        <textarea name="proxies" rows="10" cols="50"></textarea><br>
        <button type="submit">Submit</button>
    </form>

    <h2>Upload Proxy File</h2>
    <form method="POST" enctype="multipart/form-data">
        <input type="file" name="file">
        <button type="submit">Upload</button>
    </form>

    <h2>Reset Proxies</h2>
    <form method="POST">
        <input type="hidden" name="reset" value="1">
        <button type="submit">Reset</button>
    </form>

    <h2>Proxy Status</h2>
    <p><b>Current Proxy:</b> <span id="current_proxy">Loading...</span></p>
    <p><b>Next Proxy:</b> <span id="next_proxy">Loading...</span></p>
    <p><b>Time Until Next Rotation:</b> <span id="time_remaining">Loading...</span></p>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        if "proxies" in request.form:
            proxies = request.form.get("proxies").split("\n")
            proxy_manager.add_proxies([proxy.strip() for proxy in proxies if proxy.strip()])
        elif "reset" in request.form:
            proxy_manager.reset_proxies()
        elif "file" in request.files:
            file = request.files["file"]
            if file:
                filepath = os.path.join(UPLOAD_FOLDER, file.filename)
                file.save(filepath)
                with open(filepath, "r") as f:
                    proxy_list = [line.strip() for line in f if line.strip()]
                    proxy_manager.add_proxies(proxy_list)

    return render_template_string(INDEX_HTML, proxy_status=proxy_manager.get_proxy_status())

@app.route("/get_proxy")
def get_proxy():
    return jsonify(proxy_manager.get_proxy_status())

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
