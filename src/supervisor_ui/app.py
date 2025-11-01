from flask import Flask, render_template_string, request, redirect, flash
from database.db_manager import get_db, resolve_help_request
from agent.knowledge_base import add_answer
from dotenv import load_dotenv
import shutil
load_dotenv(dotenv_path=".env.local")

app = Flask(__name__)
app.secret_key = "somethingsecret"

HTML = '''
<!doctype html>
<html>
<head>
<title>Supervisor Panel</title>
<link rel="icon" type="image/png" href="https://cdn-icons-png.flaticon.com/128/4712/4712009.png">
<style>
body {
    background-color: #f6f8fa;
    font-family: 'Segoe UI', Verdana, Arial, sans-serif;
    color: #222;
    margin: 24px;
}
h1, h2, h3 {
    color: #375a7f;
}
.logo {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 18px;
}
.logo img {
    height: 46px;
    vertical-align: middle;
}
table { 
    border-collapse: collapse;
    width: 96%;
    background: #fff;
    margin: 16px 0;
    border-radius: 5px;
    overflow: hidden;
    box-shadow: 0 3px 14px #ddd;
}
th, td {
    padding: 12px;
    border-bottom: 1px solid #e7e7e7;
    text-align: left;
}
th {
    background-color: #375a7f;
    color: white;
}
button {
    background: #4a90e2;
    color: white;
    border: none;
    border-radius: 4px;
    padding: 6px 14px;
    cursor: pointer;
    font-weight: bold;
    transition: background 0.2s;
    margin-right: 4px;
}
button[style*="background-color:#faa"] {
    background: #e74c3c !important;
    color: white;
}
button[style*="background-color:#faa"]:hover {
    background: #c0392b !important;
}
button:hover {
    background: #155bb5;
}
input[type='text'], input[type='search'], input[type='answer'], textarea {
    padding: 8px;
    border: 1px solid #bbb;
    border-radius: 3px;
    box-sizing: border-box;
    background: #fcfcfc;
}
.flashes li.success { color: green; }
.flashes li.danger, .flashes li.info { color: #c0392b; }
a { color: #375a7f; text-decoration: none; font-weight: bold; }
a:hover { text-decoration: underline; }
.stats {
    font-size: 1.09em;
    margin-bottom: 10px;
    background: #e7f2fa;
    padding: 7px 13px;
    border-radius: 4px;
    display: inline-block;
    font-weight: bold;
}
.emoji-btn {
    font-size: 1.1em;
    vertical-align: middle;
    margin-right: 3px;
}
</style>
</head>
<body>
<div class="logo">
    <img src="https://cdn-icons-png.flaticon.com/128/4712/4712009.png" alt="Frontdesk AI Logo">
    <span style="font-size:1.5em;font-weight:bold;color:#375a7f;">Frontdesk AI Supervisor System</span>
</div>
<p><a href="/kb">🗄️ Knowledge Base Admin</a></p>

{% with messages = get_flashed_messages(with_categories=true) %}
{% if messages %}
    <ul class="flashes">
    {% for category, message in messages %}
        <li class="{{ category }}" style="font-weight:bold;color:{{ 'green' if category == 'success' else '#c0392b' }};">{{ message }}</li>
    {% endfor %}
    </ul>
{% endif %}
{% endwith %}

<div id="notification" style="display:none;padding:10px;color:green;font-weight:bold;margin-bottom:10px;"></div>
<div id="spinner" style="display:none;padding:10px;">
    <img src="https://i.imgur.com/llF5iyg.gif" height="30"> Processing...
</div>

<div class="stats">
    <span style="color:orange">🕒 Pending: {{ stats.pending }}</span>
    | <span style="color:green">✅ Resolved: {{ stats.resolved }}</span>
    | <span style="color:red">❌ Declined: {{ stats.declined }}</span>
</div>

<form method="get" style="margin-bottom:10px;">
    <input name="q" placeholder="🔍 Search questions..." value="{{ request.args.get('q', '') }}" style="width:220px;">
    <button type="submit" class="emoji-btn">🔎 Search</button>
</form>

<h2>🕒 Pending Help Requests</h2>
<table border="1" cellpadding="5" style="margin-bottom:12px;">
    <tr>
        <th>ID</th><th>Question</th><th>Caller</th><th>Created At</th><th>Respond</th><th>Decline</th>
    </tr>
    {% for req in requests %}
        <tr>
            <td>{{ req.id }}</td>
            <td>{{ req.question }}</td>
            <td>{{ req.caller_id }}</td>
            <td>{{ req.created_at }}</td>
            <td>
                <form method="post" style="display:inline;" onsubmit="showSpinner();">
                    <input hidden name="id" value="{{ req.id }}">
                    <input name="answer" placeholder="Supervisor answer..." required>
                    <button type="submit" class="emoji-btn">✅ Resolve</button>
                </form>
            </td>
            <td>
                <form method="post" style="display:inline;">
                    <input hidden name="id" value="{{ req.id }}">
                    <input hidden name="decline" value="true">
                    <input name="decline_comment" placeholder="Decline reason..." style="width:130px;" required>
                    <button type="submit" style="background-color:#faa;" class="emoji-btn" onclick="return confirm('Are you sure to decline this request?');">❌ Decline</button>
                </form>
            </td>
        </tr>
    {% endfor %}
</table>

<h3>✅ Resolved Requests</h3>
<ul>
{% for req in history if req.status == 'resolved' %}
    <li>
        <b>[{{ req.created_at }}]</b> {{ req.question }}
        {% if req.response %}
            <br><i>Response: {{ req.response }}</i>
            <span style="color:green;font-weight:bold;">Answered from KB</span>
        {% endif %}
    </li>
{% endfor %}
</ul>

<h3>❌ Declined/Other Requests</h3>
<ul>
{% for req in history if req.status == 'declined' %}
    <li>
        <b>[{{ req.created_at }}]</b> {{ req.question }}
        {% if req.response %}
            <br><i>Supervisor comment: {{ req.response }}</i>
        {% endif %}
    </li>
{% endfor %}
</ul>

<script>
function showSpinner() {
    document.getElementById('spinner').style.display = 'block';
    setTimeout(function() {
        document.getElementById('notification').innerText = 'Resolved successfully!';
        document.getElementById('notification').style.display = 'block';
        document.getElementById('spinner').style.display = 'none';
    }, 1250); // simulate a short delay
}
</script>
</body>
</html>
'''

@app.route("/", methods=["GET", "POST"])
def home():
    db = get_db()
    if request.method == "POST":
        try:
            help_id = request.form["id"]
            if "decline" in request.form:
                supervisor_id = "supervisor1"
                comment = request.form.get("decline_comment") or "Request declined"
                resolve_help_request(help_id, comment, supervisor_id, status="declined")
                flash("Request declined!", "info")
            else:
                answer = request.form["answer"]
                supervisor_id = "supervisor1"
                resolve_help_request(help_id, answer, supervisor_id)
                doc = db.collection("help_requests").document(help_id).get()
                question = doc.to_dict()["question"]
                add_answer(question, answer)
                flash("Resolved and KB updated!", "success")
        except Exception as ex:
            print("[ERROR] Supervisor resolve error:", ex)
            flash(f"ERROR: Could not resolve and update KB: {ex}", "danger")
        return redirect("/")

    help_requests = db.collection("help_requests").get()
    pending = []
    history = []
    for doc in help_requests:
        d = doc.to_dict()
        d["id"] = doc.id
        if d["status"] == "pending":
            pending.append(d)
        else:
            history.append(d)
    stats = {
        "pending": len(pending),
        "resolved": sum(1 for h in history if h["status"] == "resolved"),
        "declined": sum(1 for h in history if h["status"] == "declined")
    }
    search_query = request.args.get("q", "").strip().lower()
    if search_query:
        history = [h for h in history if search_query in h["question"].lower()]
    return render_template_string(HTML, requests=pending, history=history, stats=stats)

@app.route("/kb", methods=["GET", "POST"])
def kb_admin():
    from agent.knowledge_base import load_kb, save_kb, KB_PATH

    kb = load_kb()
    export_status = ""
    if request.method == "POST":
        if "save" in request.form:
            try:
                edited = request.form["kb_text"]
                new_kb = {}
                for line in edited.splitlines():
                    if ":" in line:
                        q, a = line.split(":", 1)
                        new_kb[q.strip().lower()] = a.strip()
                save_kb(new_kb)
                kb = new_kb
                flash("KB updated!", "success")
            except Exception as e:
                flash(f"Error updating KB: {e}", "danger")
        elif "backup" in request.form:
            backup_file = KB_PATH + ".bak"
            shutil.copy(KB_PATH, backup_file)
            export_status = f"Backed up as {backup_file}"

    kb_text = "\n".join(f"{q}: {a}" for q, a in kb.items())
    return render_template_string('''
        <h2>🗄️ Knowledge Base Editor</h2>
        <form method="post">
            <textarea name="kb_text" rows="14" cols="70">{{ kb_text }}</textarea><br>
            <button type="submit" name="save" class="emoji-btn">💾 Save KB</button>
            <button type="submit" name="backup" class="emoji-btn">🗂️ Backup KB</button>
        </form>
        {% if export_status %}
            <div style="color:blue;font-weight:bold;">{{ export_status }}</div>
        {% endif %}
        <p><a href="/">⬅️ Back to supervisor panel</a></p>
    ''', kb_text=kb_text, export_status=export_status)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
