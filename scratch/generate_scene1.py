import subprocess
from pathlib import Path

html = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    width: 1080px;
    height: 1920px;
    background: #090d14;
    overflow: hidden;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    position: relative;
  }
  
  /* Deep room lighting and acoustic wood slat wall background */
  .room-bg {
    position: absolute;
    top: 0; left: 0; width: 100%; height: 1920px;
    background: radial-gradient(circle at 65% 25%, #151d2c 0%, #0c111a 50%, #06090e 100%);
  }
  
  /* Vertical acoustic slat wall panels */
  .slat-wall {
    position: absolute;
    top: 0; left: 0; width: 100%; height: 1100px;
    background: repeating-linear-gradient(
      90deg,
      rgba(255, 255, 255, 0.015) 0px,
      rgba(255, 255, 255, 0.015) 18px,
      transparent 18px,
      transparent 36px
    );
    mask-image: linear-gradient(180deg, rgba(0,0,0,0.6) 0%, rgba(0,0,0,0) 90%);
  }

  /* Warm ambient studio light on the right edge */
  .ambient-warm {
    position: absolute;
    top: 100px; right: -100px;
    width: 600px; height: 900px;
    background: radial-gradient(ellipse at center, rgba(245, 158, 11, 0.07) 0%, transparent 70%);
    filter: blur(60px);
  }

  /* Cool monitor bias back-glow */
  .monitor-glow {
    position: absolute;
    top: 240px; left: 50%;
    transform: translateX(-50%);
    width: 980px; height: 800px;
    background: radial-gradient(ellipse at center, rgba(56, 189, 248, 0.14) 0%, rgba(30, 58, 138, 0.08) 55%, transparent 75%);
    filter: blur(50px);
  }

  /* Main workspace container */
  .workspace {
    position: absolute;
    top: 180px; left: 50%;
    transform: translateX(-50%);
    width: 1020px;
    display: flex;
    flex-direction: column;
    align-items: center;
  }

  /* Curved Ultrawide Monitor */
  .monitor-frame {
    width: 980px;
    height: 740px;
    background: linear-gradient(180deg, #182230 0%, #0f1520 100%);
    border-radius: 20px;
    padding: 12px;
    box-shadow: 
      0 30px 70px -15px rgba(0, 0, 0, 0.95),
      0 0 0 1px rgba(255, 255, 255, 0.09),
      0 2px 20px rgba(56, 189, 248, 0.08);
    display: flex;
    flex-direction: column;
    position: relative;
  }

  /* Monitor screen with IDE interface */
  .monitor-screen {
    flex: 1;
    background: #0b0f17;
    border-radius: 12px;
    overflow: hidden;
    display: flex;
    border: 1px solid rgba(255, 255, 255, 0.05);
  }

  /* IDE Left Navigation Panel */
  .ide-nav {
    width: 200px;
    background: #0d121c;
    border-right: 1px solid rgba(255, 255, 255, 0.05);
    padding: 20px 14px;
    display: flex;
    flex-direction: column;
    gap: 12px;
  }
  .nav-header {
    height: 10px; width: 60px; background: #334155; border-radius: 4px; margin-bottom: 8px;
  }
  .tree-node {
    display: flex; align-items: center; gap: 8px;
  }
  .icon-folder { width: 12px; height: 10px; background: #f59e0b; border-radius: 2px; }
  .icon-java { width: 12px; height: 12px; background: #38bdf8; border-radius: 3px; }
  .icon-config { width: 12px; height: 12px; background: #10b981; border-radius: 3px; }
  .node-label { height: 7px; background: #475569; border-radius: 3px; }

  /* IDE Main Code Editor */
  .ide-editor {
    flex: 1;
    display: flex;
    flex-direction: column;
    background: #0a0d14;
  }
  .tabs-bar {
    height: 38px;
    background: #080b10;
    border-bottom: 1px solid rgba(255, 255, 255, 0.05);
    display: flex;
    align-items: center;
    padding: 0 12px;
    gap: 6px;
  }
  .tab-active {
    height: 28px;
    width: 140px;
    background: #0f1522;
    border-radius: 6px 6px 0 0;
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-bottom: none;
    display: flex;
    align-items: center;
    padding: 0 10px;
    gap: 8px;
  }
  .tab-inactive {
    height: 28px;
    width: 110px;
    background: transparent;
    display: flex;
    align-items: center;
    padding: 0 10px;
    gap: 8px;
    opacity: 0.4;
  }

  .code-viewport {
    flex: 1;
    padding: 24px 20px;
    display: flex;
    flex-direction: column;
    gap: 11px;
    position: relative;
  }
  .code-row {
    display: flex;
    gap: 8px;
    align-items: center;
  }
  .gutter-num {
    width: 24px;
    height: 7px;
    background: #1e293b;
    border-radius: 3px;
    margin-right: 14px;
  }
  /* Syntax token pills */
  .tok-kw { height: 8px; background: #c084fc; border-radius: 4px; }
  .tok-ann { height: 8px; background: #fbbf24; border-radius: 4px; }
  .tok-type { height: 8px; background: #38bdf8; border-radius: 4px; }
  .tok-fn { height: 8px; background: #60a5fa; border-radius: 4px; }
  .tok-str { height: 8px; background: #34d399; border-radius: 4px; }
  .tok-var { height: 8px; background: #f472b6; border-radius: 4px; }
  .tok-cm { height: 8px; background: #475569; border-radius: 4px; }

  /* IDE Bottom Terminal */
  .ide-terminal {
    height: 120px;
    background: #070a0f;
    border-top: 1px solid rgba(255, 255, 255, 0.05);
    padding: 12px 18px;
    display: flex;
    flex-direction: column;
    gap: 8px;
  }
  .term-header {
    display: flex; align-items: center; gap: 10px; margin-bottom: 4px;
  }
  .term-dot { width: 8px; height: 8px; border-radius: 50%; background: #10b981; }
  .term-line { display: flex; gap: 8px; align-items: center; }

  /* Right Inspector / Service Topology */
  .ide-inspector {
    width: 260px;
    background: #0c1018;
    border-left: 1px solid rgba(255, 255, 255, 0.05);
    padding: 18px 14px;
    display: flex;
    flex-direction: column;
    gap: 14px;
  }
  .panel-card {
    background: #111722;
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 8px;
    padding: 14px;
    display: flex;
    flex-direction: column;
    gap: 10px;
  }
  .metric-bar-group { display: flex; flex-direction: column; gap: 6px; }
  .metric-bar {
    height: 6px;
    background: #1e293b;
    border-radius: 3px;
    overflow: hidden;
  }
  .metric-fill { height: 100%; border-radius: 3px; }

  /* Monitor Stand Assembly */
  .monitor-stand {
    display: flex;
    flex-direction: column;
    align-items: center;
    z-index: 2;
  }
  .stand-neck {
    width: 64px;
    height: 55px;
    background: linear-gradient(90deg, #18202c 0%, #2a3547 50%, #18202c 100%);
    box-shadow: 0 10px 20px rgba(0,0,0,0.6);
  }
  .stand-base {
    width: 280px;
    height: 12px;
    background: linear-gradient(180deg, #2d3848 0%, #161e29 100%);
    border-radius: 6px;
    box-shadow: 0 10px 25px rgba(0,0,0,0.8);
  }

  /* Full Width Desk Surface spanning from midground to bottom */
  .desk-assembly {
    width: 1080px;
    margin-top: -6px;
    background: linear-gradient(180deg, #111620 0%, #0d121a 40%, #080b11 100%);
    border-top: 1px solid rgba(255, 255, 255, 0.08);
    box-shadow: 
      inset 0 20px 40px rgba(56, 189, 248, 0.04),
      0 -10px 30px rgba(0,0,0,0.8);
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 30px 40px 120px 40px;
    position: relative;
    height: 840px;
  }

  /* Desk Mat */
  .desk-mat {
    width: 1000px;
    height: 480px;
    background: #0a0d14;
    border-radius: 20px;
    border: 1px solid rgba(255, 255, 255, 0.05);
    box-shadow: 
      0 20px 50px rgba(0,0,0,0.9),
      inset 0 0 0 1px rgba(255, 255, 255, 0.03);
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 40px;
    padding: 30px;
    position: relative;
  }

  /* Mechanical Keyboard */
  .keyboard {
    width: 580px;
    height: 220px;
    background: #10151f;
    border-radius: 12px;
    border: 1px solid rgba(255, 255, 255, 0.07);
    box-shadow: 
      0 20px 40px rgba(0,0,0,0.8),
      0 0 20px rgba(56, 189, 248, 0.05);
    padding: 16px;
    display: flex;
    flex-direction: column;
    gap: 8px;
  }
  .kb-row {
    display: flex; gap: 6px; flex: 1;
  }
  .key {
    flex: 1;
    background: #1a2230;
    border-radius: 4px;
    box-shadow: 0 2px 0 #0d121a;
  }
  .key.mod { background: #222d40; }
  .key.accent { background: #1e3a5f; }
  .key.space { flex: 4; }

  /* Ergonomic Wireless Mouse */
  .mouse {
    width: 85px;
    height: 145px;
    background: linear-gradient(180deg, #1b2332 0%, #121822 100%);
    border-radius: 42px;
    box-shadow: 
      0 15px 30px rgba(0,0,0,0.7),
      inset 0 1px 1px rgba(255,255,255,0.1);
    border: 1px solid rgba(255, 255, 255, 0.05);
    position: relative;
  }
  .mouse-wheel {
    position: absolute;
    top: 25px; left: 50%; transform: translateX(-50%);
    width: 10px; height: 26px;
    background: #2d3b52;
    border-radius: 5px;
  }

  /* Minimalist Matte Coffee Mug */
  .coffee-mug {
    position: absolute;
    right: 50px;
    top: 60px;
    width: 90px;
    height: 90px;
    background: radial-gradient(circle at 40% 40%, #1e2634 0%, #101620 100%);
    border-radius: 50%;
    box-shadow: 
      0 15px 30px rgba(0,0,0,0.8),
      inset 0 0 0 8px #151b26;
    display: flex;
    align-items: center;
    justify-content: center;
  }
  .coffee-liquid {
    width: 60px;
    height: 60px;
    background: #1c130d;
    border-radius: 50%;
    box-shadow: inset 0 2px 6px rgba(0,0,0,0.8);
  }

  /* Soft Subtitle Safe Area Indicator / Gradient at bottom */
  .safe-area-fade {
    position: absolute;
    bottom: 0; left: 0; width: 100%; height: 350px;
    background: linear-gradient(180deg, transparent 0%, rgba(6, 9, 14, 0.5) 100%);
    pointer-events: none;
  }
</style>
</head>
<body>
  <div class="room-bg"></div>
  <div class="slat-wall"></div>
  <div class="ambient-warm"></div>
  <div class="monitor-glow"></div>

  <div class="workspace">
    <div class="monitor-frame">
      <div class="monitor-screen">
        <!-- Navigation Tree -->
        <div class="ide-nav">
          <div class="nav-header"></div>
          <div class="tree-node"><div class="icon-folder"></div><div class="node-label" style="width:100px"></div></div>
          <div class="tree-node" style="margin-left:14px"><div class="icon-java"></div><div class="node-label" style="width:85px"></div></div>
          <div class="tree-node" style="margin-left:14px"><div class="icon-java"></div><div class="node-label" style="width:110px"></div></div>
          <div class="tree-node" style="margin-left:14px"><div class="icon-config"></div><div class="node-label" style="width:75px"></div></div>
          <div class="tree-node"><div class="icon-folder" style="background:#6366f1"></div><div class="node-label" style="width:90px"></div></div>
          <div class="tree-node" style="margin-left:14px"><div class="icon-java"></div><div class="node-label" style="width:95px"></div></div>
          <div class="tree-node" style="margin-left:14px"><div class="icon-java"></div><div class="node-label" style="width:80px"></div></div>
        </div>

        <!-- Code Editor -->
        <div class="ide-editor">
          <div class="tabs-bar">
            <div class="tab-active"><div class="icon-java" style="width:10px;height:10px"></div><div class="node-label" style="width:70px"></div></div>
            <div class="tab-inactive"><div class="icon-config" style="width:10px;height:10px"></div><div class="node-label" style="width:55px"></div></div>
          </div>
          <div class="code-viewport">
            <div class="code-row"><div class="gutter-num"></div><div class="tok-ann" style="width:110px"></div></div>
            <div class="code-row"><div class="gutter-num"></div><div class="tok-kw" style="width:50px"></div><div class="tok-type" style="width:120px"></div></div>
            <div class="code-row"><div class="gutter-num"></div></div>
            <div class="code-row" style="margin-left:24px"><div class="gutter-num"></div><div class="tok-ann" style="width:90px"></div></div>
            <div class="code-row" style="margin-left:24px"><div class="gutter-num"></div><div class="tok-kw" style="width:55px"></div><div class="tok-type" style="width:70px"></div><div class="tok-fn" style="width:130px"></div></div>
            <div class="code-row" style="margin-left:48px"><div class="gutter-num"></div><div class="tok-cm" style="width:180px"></div></div>
            <div class="code-row" style="margin-left:48px"><div class="gutter-num"></div><div class="tok-var" style="width:90px"></div><div class="tok-fn" style="width:80px"></div><div class="tok-str" style="width:120px"></div></div>
            <div class="code-row" style="margin-left:48px"><div class="gutter-num"></div><div class="tok-kw" style="width:45px"></div><div class="tok-fn" style="width:100px"></div></div>
            <div class="code-row" style="margin-left:24px"><div class="gutter-num"></div><div class="tok-kw" style="width:30px"></div></div>
            <div class="code-row"><div class="gutter-num"></div></div>
            <div class="code-row" style="margin-left:24px"><div class="gutter-num"></div><div class="tok-ann" style="width:80px"></div></div>
            <div class="code-row" style="margin-left:24px"><div class="gutter-num"></div><div class="tok-kw" style="width:50px"></div><div class="tok-type" style="width:85px"></div><div class="tok-fn" style="width:110px"></div></div>
            <div class="code-row" style="margin-left:48px"><div class="gutter-num"></div><div class="tok-var" style="width:110px"></div><div class="tok-fn" style="width:90px"></div></div>
          </div>
          <!-- Terminal -->
          <div class="ide-terminal">
            <div class="term-header"><div class="term-dot"></div><div class="node-label" style="width:130px"></div></div>
            <div class="term-line"><div class="node-label" style="width:80px;background:#38bdf8"></div><div class="node-label" style="width:200px"></div></div>
            <div class="term-line"><div class="node-label" style="width:120px;background:#10b981"></div><div class="node-label" style="width:160px"></div></div>
          </div>
        </div>

        <!-- Right Telemetry Panel -->
        <div class="ide-inspector">
          <div class="panel-card">
            <div class="node-label" style="width:90px;background:#64748b"></div>
            <div class="metric-bar-group">
              <div class="metric-bar"><div class="metric-fill" style="width:78%;background:#38bdf8"></div></div>
              <div class="metric-bar"><div class="metric-fill" style="width:42%;background:#10b981"></div></div>
              <div class="metric-bar"><div class="metric-fill" style="width:65%;background:#f59e0b"></div></div>
            </div>
          </div>
          <div class="panel-card">
            <div class="node-label" style="width:110px;background:#64748b"></div>
            <div style="display:flex;gap:6px;margin-top:4px">
              <div style="flex:1;height:36px;background:rgba(56,189,248,0.12);border:1px solid rgba(56,189,248,0.3);border-radius:4px"></div>
              <div style="flex:1;height:36px;background:rgba(16,185,129,0.12);border:1px solid rgba(16,185,129,0.3);border-radius:4px"></div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Stand -->
    <div class="monitor-stand">
      <div class="stand-neck"></div>
      <div class="stand-base"></div>
    </div>

    <!-- Full Desk Assembly -->
    <div class="desk-assembly">
      <div class="desk-mat">
        <div class="keyboard">
          <div class="kb-row"><div class="key"></div><div class="key"></div><div class="key"></div><div class="key"></div><div class="key"></div><div class="key"></div><div class="key"></div><div class="key"></div><div class="key"></div><div class="key"></div><div class="key"></div></div>
          <div class="kb-row"><div class="key mod"></div><div class="key"></div><div class="key"></div><div class="key"></div><div class="key"></div><div class="key"></div><div class="key"></div><div class="key"></div><div class="key"></div><div class="key"></div><div class="key mod"></div></div>
          <div class="kb-row"><div class="key mod"></div><div class="key"></div><div class="key"></div><div class="key space"></div><div class="key"></div><div class="key accent"></div><div class="key mod"></div></div>
        </div>
        <div class="mouse"><div class="mouse-wheel"></div></div>
        <div class="coffee-mug"><div class="coffee-liquid"></div></div>
      </div>
    </div>
  </div>

  <div class="safe-area-fade"></div>
</body>
</html>
"""

Path("scratch/scene1_gen.html").write_text(html, encoding="utf-8")
subprocess.run([
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "--headless",
    "--screenshot=scratch/scene1_gen.png",
    "--window-size=1080,1920",
    "--hide-scrollbars",
    f"file://{Path('scratch/scene1_gen.html').resolve()}"
], check=True)
print("Generated Scene 1 successfully!")
