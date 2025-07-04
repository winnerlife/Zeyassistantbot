from flask import Flask, render_template_string

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Zeylo's Bot</title>
    <style>
        body {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: #fff;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            display: flex;
            align-items: center;
            justify-content: center;
            height: 100vh;
            margin: 0;
        }
        .container {
            text-align: center;
            background-color: rgba(0, 0, 0, 0.3);
            padding: 40px;
            border-radius: 16px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
        }
        h1 {
            font-size: 2.5rem;
            margin-bottom: 10px;
        }
        p {
            font-size: 1.2rem;
            opacity: 0.85;
        }
        .badge {
            display: inline-block;
            margin-top: 20px;
            padding: 8px 16px;
            background-color: #ffffff22;
            border: 1px solid #ffffff44;
            border-radius: 8px;
            font-weight: bold;
            font-size: 0.9rem;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>👋 Welcome to Zeylo's Bot</h1>
        <p>This site does <strong>NOT</strong> do anything, but your bot is <em>live and running</em>!</p>
        <div class="badge">Powered by Flask</div>
    </div>
</body>
</html>
"""

@app.route("/")
def hello_world():
    return render_template_string(HTML_TEMPLATE)

if __name__ == "__main__":
    app.run()
