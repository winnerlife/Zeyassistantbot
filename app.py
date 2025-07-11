from flask import Flask, render_template_string

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Zeylence Bot</title>
  
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 68 68'%3E%3Cdefs%3E%3ClinearGradient id='grad' x1='0%25' y1='0%25' x2='100%25' y2='100%25'%3E%3Cstop offset='0%25' style='stop-color:%23e94560;' /%3E%3Cstop offset='100%25' style='stop-color:%23903749;' /%3E%3C/linearGradient%3E%3C/defs%3E%3Crect x='6' y='12' width='56' height='44' rx='12' fill='url(%23grad)'/%3E%3Crect x='0' y='28' width='6' height='12' rx='3' fill='%23e94560'/%3E%3Crect x='62' y='28' width='6' height='12' rx='3' fill='%23e94560'/%3E%3Crect x='14' y='20' width='40' height='28' rx='8' fill='%231a1a2e'/%3E%3Crect x='23' y='28' width='6' height='8' rx='2' fill='%23fff'/%3E%3Crect x='39' y='28' width='6' height='8' rx='2' fill='%23fff'/%3E%3Crect x='28' y='40' width='12' height='4' rx='2' fill='%23e94560'/%3E%3C/svg%3E">

  <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;500;700&display=swap" rel="stylesheet">
  
  <style>
    :root {
      --bg-color: #1a1a2e;
      --accent: #e94560;
      --text-light: #f0f0f0;
      --text-muted: #bbbbbb;
      --card-bg: rgba(25, 25, 40, 0.8);
    }

    body {
      margin: 0;
      font-family: 'Poppins', sans-serif;
      color: var(--text-light);
      background-color: var(--bg-color);
      overflow: hidden;
    }
    
    #app {
      position: relative;
      width: 100vw;
      height: 100vh;
      display: grid;
      place-items: center;
    }

    #webgl-canvas {
      position: fixed;
      top: 0;
      left: 0;
      /* This is the crucial fix that solves the black screen issue */
      width: 100%;
      height: 100%;
      z-index: -1;
    }

    .container {
      position: relative;
      z-index: 1;
      max-width: 380px;
      padding: 2rem;
      background: var(--card-bg);
      border-radius: 1rem;
      box-shadow: 0 8px 32px rgba(0, 0, 0, 0.7);
      text-align: center;
      backdrop-filter: blur(8px);
      border: 1px solid rgba(255, 255, 255, 0.1);
    }

    .ai-bot {
      margin: 0 auto 1.5rem;
      width: 68px;
      height: 68px;
      position: relative;
      animation: float 3s ease-in-out infinite;
    }

    @keyframes float {
      0%, 100% { transform: translateY(0); }
      50% { transform: translateY(-10px); }
    }

    .ai-bot .head {
      background: linear-gradient(135deg, #e94560 0%, #903749 100%);
      border-radius: 0.75rem;
      width: 56px;
      height: 44px;
      position: relative;
    }

    .ai-bot .head::before,
    .ai-bot .head::after {
      content: '';
      position: absolute;
      width: 6px;
      height: 12px;
      background: #e94560;
      border-radius: 3px;
      top: 16px;
    }

    .ai-bot .head::before { left: -6px; }
    .ai-bot .head::after  { right: -6px; }

    .ai-bot .face {
      position: absolute;
      top: 8px;
      left: 8px;
      width: 40px;
      height: 28px;
      background: #1a1a2e;
      border-radius: 0.5rem;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      gap: 4px;
    }

    .eyes { display: flex; gap: 6px; }
    .eyes span {
      display: block; width: 6px; height: 8px;
      background: #ffffff; border-radius: 2px;
      animation: blink 4s infinite;
    }
    @keyframes blink {
      0%, 90%, 100% { transform: scaleY(1); }
      92%, 98% { transform: scaleY(0.2); }
    }

    .mouth {
      width: 12px; height: 4px;
      background: var(--accent);
      border-radius: 0 0 4px 4px;
      animation: smile 2s ease-in-out infinite;
    }
    @keyframes smile {
      0%, 100% { transform: scaleX(1); }
      50% { transform: scaleX(1.3); }
    }

    h1 {
      margin: 0 0 0.5rem; font-size: 1.5rem;
      font-weight: 700; color: var(--text-light);
    }

    p {
      margin: 0 0 1.5rem; font-size: 1rem;
      color: var(--text-muted); line-height: 1.4;
    }

    .badges-container {
      display: flex; justify-content: center;
      gap: 0.75rem;
    }
    
    .badge {
      display: inline-block; padding: 0.4rem 1rem;
      font-size: 0.9rem; font-weight: 500;
      color: #fff; background: var(--accent);
      border-radius: 2rem; text-transform: uppercase;
      letter-spacing: 0.05em; text-decoration: none;
      transition: background 0.3s, color 0.3s, transform 0.2s;
    }
    .badge:hover { transform: translateY(-2px); }
    .badge.secondary {
      background: transparent;
      border: 1px solid var(--accent); color: var(--accent);
    }
    .badge.secondary:hover { background: var(--accent); color: #fff; }
  </style>
</head>
<body>
  
  <div id="app">
    <canvas id="webgl-canvas"></canvas>

    <div class="container">
      <div class="ai-bot">
        <div class="head">
          <div class="face">
            <div class="eyes"><span></span><span></span></div>
            <div class="mouth"></div>
          </div>
        </div>
      </div>
      <h1>Welcome to your Userbot</h1>
      <p>If you see this site, this means your bot is <strong>alive</strong>, go and test by sending <em>.alive</em> into any chat!</p>
      <div class="badges-container">
        <a href="https://zylenceorg.gitbook.io/zylencebot/" class="badge secondary">Zeylence</a>
        <a href="https://t.me/zeyl0" class="badge">Make your own bot</a>
      </div>
    </div>
  </div>

<!-- ... keep all your HTML and CSS the same ... -->

  <script type="module">
    import Grid1Background from 'https://cdn.jsdelivr.net/npm/threejs-components@0.0.16/build/backgrounds/grid1.cdn.min.js';

    // Let's try to initialize the background with ZERO options.
    // This will use the library's default settings.
    try {
      const bg = Grid1Background(document.getElementById('webgl-canvas'));
      console.log("Grid1Background initialized successfully with default settings.");
    } catch (error) {
      console.error("Failed to initialize Grid1Background:", error);
    }
  </script>
  
</body>
</html>
  
</body>
</html>
"""

@app.route("/")
def hello_world():
    return render_template_string(HTML_TEMPLATE)

if __name__ == "__main__":
    app.run()
