import json
import shutil
import subprocess
import zipfile
import sys
from pathlib import Path

# Paths
BASE_DIR = Path("/Users/zengcode/projects/autoclip")
sys.path.insert(0, str(BASE_DIR))

ASSETS_DIR = BASE_DIR / "assets" / "thai_java_zone_why_java_alive_reel"
ASSETS_IMAGES = ASSETS_DIR / "images"
DIST_DIR = BASE_DIR / "dist" / "thai-java-zone-why-java-alive"
DIST_IMAGES = DIST_DIR / "images"
DIST_ZIP = BASE_DIR / "dist" / "thai-java-zone-why-java-alive.zip"
SCRATCH_HTML = BASE_DIR / "scratch" / "html_templates"

CHROME_BIN = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

ASSETS_IMAGES.mkdir(parents=True, exist_ok=True)
DIST_IMAGES.mkdir(parents=True, exist_ok=True)
SCRATCH_HTML.mkdir(parents=True, exist_ok=True)

SCENE_HTMLS = {}

# =========================================================
# SCENE 1: Modern Developer Workstation at Night (IDE Hook)
# =========================================================
SCENE_HTMLS["scene-01-hook.png"] = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    width: 1080px; height: 1920px; background: #06090e; overflow: hidden;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    position: relative;
  }
  .wall {
    position: absolute; top: 0; left: 0; width: 1080px; height: 1150px;
    background: radial-gradient(circle at 68% 28%, #162030 0%, #0c1119 55%, #06090e 100%);
  }
  .acoustic-slats {
    position: absolute; top: 0; left: 0; width: 1080px; height: 1150px;
    background: repeating-linear-gradient(
      90deg, rgba(255, 255, 255, 0.018) 0px, rgba(255, 255, 255, 0.018) 16px,
      transparent 16px, transparent 32px
    );
    mask-image: radial-gradient(circle at 60% 35%, rgba(0,0,0,0.85) 0%, transparent 80%);
  }
  .lamp-glow {
    position: absolute; top: 0; right: 0; width: 550px; height: 1400px;
    background: radial-gradient(ellipse at 90% 10%, rgba(245, 158, 11, 0.09) 0%, rgba(245, 158, 11, 0.03) 45%, transparent 75%);
    filter: blur(50px); pointer-events: none;
  }
  .monitor-ambient-glow {
    position: absolute; top: 70px; left: 50%; transform: translateX(-50%);
    width: 1040px; height: 950px;
    background: radial-gradient(ellipse at center, rgba(56, 189, 248, 0.16) 0%, rgba(30, 58, 138, 0.08) 50%, transparent 75%);
    filter: blur(60px);
  }
  .monitor-container {
    position: absolute; top: 70px; left: 50%; transform: translateX(-50%);
    width: 1000px; display: flex; flex-direction: column; align-items: center; z-index: 10;
  }
  .monitor-frame {
    width: 1000px; height: 930px;
    background: linear-gradient(180deg, #1b2636 0%, #101724 100%);
    border-radius: 20px; padding: 12px;
    box-shadow: 0 35px 80px -15px rgba(0, 0, 0, 0.95), 0 0 0 1px rgba(255, 255, 255, 0.1), 0 0 40px rgba(56, 189, 248, 0.08);
    display: flex; flex-direction: column;
  }
  .monitor-screen {
    flex: 1; background: #090d14; border-radius: 12px; overflow: hidden; display: flex;
    border: 1px solid rgba(255, 255, 255, 0.05); box-shadow: inset 0 0 20px rgba(0,0,0,0.5);
  }
  .ide-nav {
    width: 210px; background: #0c1119; border-right: 1px solid rgba(255, 255, 255, 0.05);
    padding: 18px 14px; display: flex; flex-direction: column; gap: 11px;
  }
  .nav-title { height: 10px; width: 65px; background: #334155; border-radius: 4px; margin-bottom: 6px; }
  .tree-row { display: flex; align-items: center; gap: 8px; }
  .folder-icon { width: 12px; height: 10px; background: #f59e0b; border-radius: 2px; }
  .java-icon { width: 12px; height: 12px; background: #38bdf8; border-radius: 3px; }
  .conf-icon { width: 12px; height: 12px; background: #10b981; border-radius: 3px; }
  .node-bar { height: 7px; background: #475569; border-radius: 3px; }
  .ide-editor { flex: 1; display: flex; flex-direction: column; background: #0a0e15; }
  .tab-bar {
    height: 38px; background: #080b10; border-bottom: 1px solid rgba(255, 255, 255, 0.05);
    display: flex; align-items: center; padding: 0 12px; gap: 6px;
  }
  .active-tab {
    height: 28px; width: 145px; background: #111722; border-radius: 6px 6px 0 0;
    border: 1px solid rgba(255, 255, 255, 0.08); border-bottom: none;
    display: flex; align-items: center; padding: 0 10px; gap: 8px;
  }
  .inactive-tab {
    height: 28px; width: 115px; display: flex; align-items: center; padding: 0 10px; gap: 8px; opacity: 0.35;
  }
  .code-scroll {
    flex: 1; padding: 18px 18px; display: flex; flex-direction: column; gap: 8px;
  }
  .c-row { display: flex; gap: 7px; align-items: center; }
  .c-line-num { width: 22px; height: 7px; background: #1e293b; border-radius: 3px; margin-right: 12px; }
  .t-ann { height: 8px; background: #fbbf24; border-radius: 4px; }
  .t-kw { height: 8px; background: #c084fc; border-radius: 4px; }
  .t-type { height: 8px; background: #38bdf8; border-radius: 4px; }
  .t-fn { height: 8px; background: #60a5fa; border-radius: 4px; }
  .t-str { height: 8px; background: #34d399; border-radius: 4px; }
  .t-var { height: 8px; background: #f472b6; border-radius: 4px; }
  .t-cm { height: 8px; background: #475569; border-radius: 4px; }
  .t-op { height: 8px; width: 14px; background: #94a3b8; border-radius: 3px; }
  .ide-term {
    height: 140px; background: #070a0f; border-top: 1px solid rgba(255, 255, 255, 0.06);
    padding: 12px 16px; display: flex; flex-direction: column; gap: 7px;
  }
  .term-title-bar { display: flex; align-items: center; gap: 8px; margin-bottom: 2px; }
  .dot-green { width: 8px; height: 8px; border-radius: 50%; background: #10b981; }
  .term-txt { display: flex; gap: 8px; align-items: center; }
  .ide-right {
    width: 240px; background: #0b0f17; border-left: 1px solid rgba(255, 255, 255, 0.05);
    padding: 18px 14px; display: flex; flex-direction: column; gap: 14px;
  }
  .card-metric {
    background: #101622; border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 8px; padding: 12px; display: flex; flex-direction: column; gap: 8px;
  }
  .spark-chart {
    height: 40px; background: linear-gradient(180deg, rgba(56, 189, 248, 0.15) 0%, rgba(56, 189, 248, 0) 100%);
    border-bottom: 2px solid #38bdf8; border-radius: 4px;
  }
  .stand-column {
    width: 70px; height: 60px;
    background: linear-gradient(90deg, #182230 0%, #2b394d 50%, #182230 100%);
    box-shadow: 0 10px 20px rgba(0,0,0,0.6);
  }
  .stand-foot {
    width: 280px; height: 12px;
    background: linear-gradient(180deg, #2d3a4d 0%, #171f2b 100%);
    border-radius: 6px; box-shadow: 0 8px 20px rgba(0,0,0,0.8);
  }
  .desk-plane {
    position: absolute; top: 1040px; left: 0; width: 1080px; height: 880px;
    background: linear-gradient(180deg, #141b26 0%, #0f151f 35%, #0a0e16 100%);
    border-top: 2px solid rgba(255, 255, 255, 0.08);
    box-shadow: inset 0 30px 60px rgba(56, 189, 248, 0.04), 0 -20px 40px rgba(0,0,0,0.9);
    display: flex; flex-direction: column; align-items: center; padding: 25px 40px 0 40px;
  }
  .desk-mat {
    width: 1000px; height: 720px; background: #080b11; border-radius: 24px;
    border: 1px solid rgba(255, 255, 255, 0.04);
    box-shadow: 0 25px 60px rgba(0,0,0,0.95), inset 0 0 0 1px rgba(255, 255, 255, 0.03);
    display: flex; flex-direction: column; align-items: center; padding: 30px 50px; position: relative;
  }
  .desk-gear {
    width: 100%; display: flex; align-items: center; justify-content: center; gap: 45px; margin-top: 10px;
  }
  .keyboard-assembly {
    display: flex; flex-direction: column; gap: 12px; align-items: center;
  }
  .keyboard {
    width: 620px; height: 230px; background: #0e131d; border-radius: 14px;
    border: 1px solid rgba(255, 255, 255, 0.08);
    box-shadow: 0 20px 45px rgba(0,0,0,0.85), 0 0 25px rgba(56, 189, 248, 0.06);
    padding: 18px; display: flex; flex-direction: column; gap: 8px;
  }
  .wrist-rest {
    width: 620px; height: 70px; background: linear-gradient(180deg, #141c28 0%, #0c121b 100%);
    border-radius: 10px; border: 1px solid rgba(255, 255, 255, 0.05);
    box-shadow: 0 10px 20px rgba(0,0,0,0.6);
  }
  .kb-line { display: flex; gap: 7px; flex: 1; }
  .k-cap { flex: 1; background: #182232; border-radius: 5px; box-shadow: 0 3px 0 #0d121c; }
  .k-cap.mod { background: #222e42; }
  .k-cap.accent { background: #1e3a5f; }
  .k-cap.space { flex: 4.5; }
  .mouse {
    width: 90px; height: 155px; background: linear-gradient(180deg, #1d2638 0%, #111722 100%);
    border-radius: 45px; box-shadow: 0 18px 35px rgba(0,0,0,0.75), inset 0 1px 2px rgba(255,255,255,0.12);
    border: 1px solid rgba(255, 255, 255, 0.06); position: relative;
  }
  .mouse-roller {
    position: absolute; top: 26px; left: 50%; transform: translateX(-50%);
    width: 11px; height: 28px; background: #2d3b52; border-radius: 6px;
  }
  .coffee-station {
    position: absolute; right: 50px; top: 50px; width: 95px; height: 95px;
    background: radial-gradient(circle at 40% 40%, #1e2838 0%, #101622 100%);
    border-radius: 50%; box-shadow: 0 18px 35px rgba(0,0,0,0.85), inset 0 0 0 9px #151d2a;
    display: flex; align-items: center; justify-content: center;
  }
  .coffee-fill {
    width: 62px; height: 62px; background: #1a120b; border-radius: 50%;
    box-shadow: inset 0 2px 8px rgba(0,0,0,0.9);
  }
  .screen-desk-reflection {
    position: absolute; top: 0; left: 50%; transform: translateX(-50%);
    width: 800px; height: 120px;
    background: radial-gradient(ellipse at 50% 0%, rgba(56, 189, 248, 0.1) 0%, transparent 70%);
    pointer-events: none;
  }
  .safe-area-lower {
    position: absolute; bottom: 0; left: 0; width: 1080px; height: 380px;
    background: linear-gradient(180deg, transparent 0%, rgba(7, 10, 15, 0.5) 100%);
    pointer-events: none;
  }
</style>
</head>
<body>
  <div class="wall"></div>
  <div class="acoustic-slats"></div>
  <div class="lamp-glow"></div>
  <div class="monitor-ambient-glow"></div>
  <div class="monitor-container">
    <div class="monitor-frame">
      <div class="monitor-screen">
        <div class="ide-nav">
          <div class="nav-title"></div>
          <div class="tree-row"><div class="folder-icon"></div><div class="node-bar" style="width:105px"></div></div>
          <div class="tree-row" style="margin-left:14px"><div class="java-icon"></div><div class="node-bar" style="width:90px"></div></div>
          <div class="tree-row" style="margin-left:14px"><div class="java-icon"></div><div class="node-bar" style="width:115px"></div></div>
          <div class="tree-row" style="margin-left:14px"><div class="conf-icon"></div><div class="node-bar" style="width:80px"></div></div>
          <div class="tree-row"><div class="folder-icon" style="background:#6366f1"></div><div class="node-bar" style="width:95px"></div></div>
          <div class="tree-row" style="margin-left:14px"><div class="java-icon"></div><div class="node-bar" style="width:100px"></div></div>
          <div class="tree-row" style="margin-left:14px"><div class="java-icon"></div><div class="node-bar" style="width:85px"></div></div>
          <div class="tree-row"><div class="folder-icon" style="background:#ec4899"></div><div class="node-bar" style="width:90px"></div></div>
          <div class="tree-row" style="margin-left:14px"><div class="java-icon"></div><div class="node-bar" style="width:75px"></div></div>
          <div class="tree-row"><div class="folder-icon" style="background:#10b981"></div><div class="node-bar" style="width:85px"></div></div>
          <div class="tree-row" style="margin-left:14px"><div class="java-icon"></div><div class="node-bar" style="width:95px"></div></div>
        </div>
        <div class="ide-editor">
          <div class="tab-bar">
            <div class="active-tab"><div class="java-icon" style="width:10px;height:10px"></div><div class="node-bar" style="width:75px"></div></div>
            <div class="inactive-tab"><div class="conf-icon" style="width:10px;height:10px"></div><div class="node-bar" style="width:60px"></div></div>
          </div>
          <div class="code-scroll">
            <div class="c-row"><div class="c-line-num"></div><div class="t-ann" style="width:130px"></div></div>
            <div class="c-row"><div class="c-line-num"></div><div class="t-kw" style="width:50px"></div><div class="t-type" style="width:130px"></div></div>
            <div class="c-row"><div class="c-line-num"></div></div>
            <div class="c-row" style="margin-left:24px"><div class="c-line-num"></div><div class="t-ann" style="width:100px"></div></div>
            <div class="c-row" style="margin-left:24px"><div class="c-line-num"></div><div class="t-kw" style="width:55px"></div><div class="t-type" style="width:70px"></div><div class="t-fn" style="width:140px"></div></div>
            <div class="c-row" style="margin-left:48px"><div class="c-line-num"></div><div class="t-cm" style="width:190px"></div></div>
            <div class="c-row" style="margin-left:48px"><div class="c-line-num"></div><div class="t-var" style="width:85px"></div><div class="t-op"></div><div class="t-fn" style="width:90px"></div><div class="t-str" style="width:110px"></div></div>
            <div class="c-row" style="margin-left:48px"><div class="c-line-num"></div><div class="t-kw" style="width:45px"></div><div class="t-fn" style="width:110px"></div><div class="t-var" style="width:60px"></div></div>
            <div class="c-row" style="margin-left:24px"><div class="c-line-num"></div><div class="t-kw" style="width:30px"></div></div>
            <div class="c-row"><div class="c-line-num"></div></div>
            <div class="c-row" style="margin-left:24px"><div class="c-line-num"></div><div class="t-ann" style="width:90px"></div></div>
            <div class="c-row" style="margin-left:24px"><div class="c-line-num"></div><div class="t-kw" style="width:55px"></div><div class="t-type" style="width:80px"></div><div class="t-fn" style="width:120px"></div></div>
            <div class="c-row" style="margin-left:48px"><div class="c-line-num"></div><div class="t-type" style="width:95px"></div><div class="t-var" style="width:70px"></div><div class="t-op"></div><div class="t-kw" style="width:35px"></div><div class="t-type" style="width:90px"></div></div>
            <div class="c-row" style="margin-left:48px"><div class="c-line-num"></div><div class="t-var" style="width:65px"></div><div class="t-fn" style="width:85px"></div><div class="t-var" style="width:55px"></div></div>
            <div class="c-row" style="margin-left:48px"><div class="c-line-num"></div><div class="t-kw" style="width:50px"></div><div class="t-fn" style="width:105px"></div></div>
            <div class="c-row" style="margin-left:24px"><div class="c-line-num"></div><div class="t-kw" style="width:30px"></div></div>
            <div class="c-row" style="margin-left:24px"><div class="c-line-num"></div><div class="t-ann" style="width:110px"></div></div>
            <div class="c-row" style="margin-left:24px"><div class="c-line-num"></div><div class="t-kw" style="width:55px"></div><div class="t-type" style="width:85px"></div><div class="t-fn" style="width:130px"></div></div>
            <div class="c-row" style="margin-left:48px"><div class="c-line-num"></div><div class="t-kw" style="width:45px"></div><div class="t-var" style="width:95px"></div><div class="t-op"></div><div class="t-fn" style="width:75px"></div></div>
            <div class="c-row" style="margin-left:24px"><div class="c-line-num"></div><div class="t-kw" style="width:30px"></div></div>
            <div class="c-row" style="margin-left:24px"><div class="c-line-num"></div><div class="t-ann" style="width:85px"></div></div>
            <div class="c-row" style="margin-left:24px"><div class="c-line-num"></div><div class="t-kw" style="width:45px"></div><div class="t-type" style="width:70px"></div><div class="t-fn" style="width:115px"></div></div>
            <div class="c-row" style="margin-left:48px"><div class="c-line-num"></div><div class="t-fn" style="width:90px"></div><div class="t-var" style="width:80px"></div></div>
            <div class="c-row" style="margin-left:24px"><div class="c-line-num"></div><div class="t-kw" style="width:30px"></div></div>
          </div>
          <div class="ide-term">
            <div class="term-title-bar"><div class="dot-green"></div><div class="node-bar" style="width:140px;background:#64748b"></div></div>
            <div class="term-txt"><div class="node-bar" style="width:75px;background:#38bdf8"></div><div class="node-bar" style="width:220px"></div></div>
            <div class="term-txt"><div class="node-bar" style="width:110px;background:#10b981"></div><div class="node-bar" style="width:170px"></div></div>
            <div class="term-txt"><div class="node-bar" style="width:90px;background:#f59e0b"></div><div class="node-bar" style="width:190px"></div></div>
          </div>
        </div>
        <div class="ide-right">
          <div class="card-metric">
            <div class="node-bar" style="width:85px;background:#64748b"></div>
            <div class="spark-chart"></div>
            <div style="display:flex;justify-content:space-between;margin-top:4px">
              <div class="node-bar" style="width:40px;background:#38bdf8"></div>
              <div class="node-bar" style="width:50px;background:#10b981"></div>
            </div>
          </div>
          <div class="card-metric">
            <div class="node-bar" style="width:110px;background:#64748b"></div>
            <div style="display:flex;flex-direction:column;gap:6px;margin-top:4px">
              <div style="height:6px;background:#1e293b;border-radius:3px;overflow:hidden"><div style="height:100%;width:82%;background:#38bdf8"></div></div>
              <div style="height:6px;background:#1e293b;border-radius:3px;overflow:hidden"><div style="height:100%;width:58%;background:#10b981"></div></div>
              <div style="height:6px;background:#1e293b;border-radius:3px;overflow:hidden"><div style="height:100%;width:91%;background:#6366f1"></div></div>
            </div>
          </div>
          <div class="card-metric">
            <div class="node-bar" style="width:95px;background:#64748b"></div>
            <div style="display:flex;gap:6px;margin-top:4px">
              <div style="flex:1;height:28px;background:rgba(56,189,248,0.15);border:1px solid #38bdf8;border-radius:4px"></div>
              <div style="flex:1;height:28px;background:rgba(16,185,129,0.15);border:1px solid #10b981;border-radius:4px"></div>
            </div>
          </div>
        </div>
      </div>
    </div>
    <div class="stand-column"></div>
    <div class="stand-foot"></div>
  </div>
  <div class="desk-plane">
    <div class="desk-mat">
      <div class="screen-desk-reflection"></div>
      <div class="desk-gear">
        <div class="keyboard-assembly">
          <div class="keyboard">
            <div class="kb-line"><div class="k-cap"></div><div class="k-cap"></div><div class="k-cap"></div><div class="k-cap"></div><div class="k-cap"></div><div class="k-cap"></div><div class="k-cap"></div><div class="k-cap"></div><div class="k-cap"></div><div class="k-cap"></div><div class="k-cap"></div></div>
            <div class="kb-line"><div class="k-cap mod"></div><div class="k-cap"></div><div class="k-cap"></div><div class="k-cap"></div><div class="k-cap"></div><div class="k-cap"></div><div class="k-cap"></div><div class="k-cap"></div><div class="k-cap"></div><div class="k-cap"></div><div class="k-cap mod"></div></div>
            <div class="kb-line"><div class="k-cap mod"></div><div class="k-cap"></div><div class="k-cap"></div><div class="k-cap"></div><div class="k-cap"></div><div class="k-cap"></div><div class="k-cap"></div><div class="k-cap"></div><div class="k-cap"></div><div class="k-cap mod"></div><div class="k-cap mod"></div></div>
            <div class="kb-line"><div class="k-cap mod"></div><div class="k-cap"></div><div class="k-cap"></div><div class="k-cap space"></div><div class="k-cap"></div><div class="k-cap accent"></div><div class="k-cap mod"></div></div>
          </div>
          <div class="wrist-rest"></div>
        </div>
        <div class="mouse"><div class="mouse-roller"></div></div>
      </div>
      <div class="coffee-station"><div class="coffee-fill"></div></div>
    </div>
  </div>
  <div class="safe-area-lower"></div>
</body>
</html>
"""

# =========================================================
# SCENE 2: Enterprise Server Data Center Rack (Stability)
# =========================================================
SCENE_HTMLS["scene-02-stability.png"] = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    width: 1080px; height: 1920px; background: #06090e; overflow: hidden;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    position: relative;
  }
  .dc-corridor {
    position: absolute; top: 0; left: 0; width: 1080px; height: 1920px;
    background: radial-gradient(circle at 50% 35%, #0f1724 0%, #080d14 50%, #040609 100%);
  }
  .overhead-light-bar {
    position: absolute; top: 25px; left: 50%; transform: translateX(-50%);
    width: 840px; height: 8px; background: #e0f2fe; border-radius: 4px;
    box-shadow: 0 0 35px rgba(56, 189, 248, 0.6), 0 0 80px rgba(56, 189, 248, 0.3);
  }
  .server-rack-container {
    position: absolute; top: 60px; left: 50%; transform: translateX(-50%);
    width: 900px; height: 1560px;
    background: linear-gradient(180deg, #131a24 0%, #0c1118 100%);
    border-radius: 16px; border: 2px solid rgba(255, 255, 255, 0.1);
    box-shadow: 0 40px 100px rgba(0, 0, 0, 0.95), 0 0 60px rgba(56, 189, 248, 0.1), inset 0 0 30px rgba(0,0,0,0.8);
    display: flex; padding: 14px 12px; gap: 12px; z-index: 10;
  }
  .rack-rail {
    width: 28px; height: 100%;
    background: repeating-linear-gradient(
      180deg, #1c2533 0px, #1c2533 12px, #0e141c 12px, #0e141c 24px, #090d13 24px, #090d13 36px
    );
    border-radius: 4px; border: 1px solid rgba(255, 255, 255, 0.05);
  }
  .server-stack { flex: 1; display: flex; flex-direction: column; gap: 8px; }
  .chassis {
    width: 100%; background: linear-gradient(180deg, #17202d 0%, #101620 50%, #0d121a 100%);
    border-radius: 7px; border: 1px solid rgba(255, 255, 255, 0.07);
    box-shadow: 0 8px 16px rgba(0,0,0,0.6), inset 0 1px 1px rgba(255,255,255,0.1);
    display: flex; align-items: center; padding: 8px 16px; gap: 14px;
  }
  .chassis.h-1u { height: 62px; }
  .chassis.h-2u { height: 95px; }
  .chassis.h-4u { height: 155px; }
  .drive-bay-group { display: flex; gap: 5px; flex: 2; }
  .drive-caddy {
    flex: 1; height: 46px; background: #090d13; border-radius: 4px;
    border: 1px solid rgba(255, 255, 255, 0.05); display: flex; flex-direction: column;
    justify-content: space-between; padding: 4px; box-shadow: inset 0 2px 4px rgba(0,0,0,0.7);
  }
  .caddy-handle { height: 5px; background: #1f2a3a; border-radius: 2px; }
  .caddy-led { width: 5px; height: 5px; border-radius: 50%; background: #10b981; box-shadow: 0 0 5px #10b981; }
  .caddy-led.blue { background: #38bdf8; box-shadow: 0 0 5px #38bdf8; }
  .caddy-led.amber { background: #f59e0b; box-shadow: 0 0 5px #f59e0b; }
  .honeycomb-grille {
    flex: 2; height: 46px;
    background: radial-gradient(circle, #080c12 25%, transparent 26%) 0 0, radial-gradient(circle, #080c12 25%, transparent 26%) 4px 4px;
    background-size: 8px 8px; background-color: #172230; border-radius: 4px; border: 1px solid rgba(255, 255, 255, 0.04);
  }
  .status-cluster {
    display: flex; flex-direction: column; gap: 5px; width: 80px; background: #0a0e15;
    padding: 6px; border-radius: 4px; border: 1px solid rgba(255,255,255,0.04);
  }
  .status-line { display: flex; align-items: center; justify-content: space-between; }
  .led-label { width: 42px; height: 5px; background: #334155; border-radius: 2px; }
  .pulse-led { width: 6px; height: 6px; border-radius: 50%; background: #10b981; box-shadow: 0 0 7px #10b981; }
  .switch-unit {
    width: 100%; height: 75px; background: linear-gradient(180deg, #1b2432 0%, #111822 100%);
    border-radius: 7px; border: 1px solid rgba(255, 255, 255, 0.08);
    display: flex; align-items: center; padding: 8px 16px; gap: 14px;
  }
  .port-matrix { display: flex; flex-wrap: wrap; gap: 5px; flex: 3; }
  .sfp-port {
    width: 18px; height: 14px; background: #090d13; border: 1px solid rgba(255,255,255,0.1);
    border-radius: 2px; display: flex; align-items: center; justify-content: center;
  }
  .fiber-plug { width: 11px; height: 7px; border-radius: 2px; }
  .fiber-plug.aqua { background: #06b6d4; box-shadow: 0 0 5px #06b6d4; }
  .fiber-plug.orange { background: #f97316; box-shadow: 0 0 5px #f97316; }
  .fiber-plug.yellow { background: #eab308; box-shadow: 0 0 5px #eab308; }
  .cable-bundle {
    position: absolute; top: 70px; right: 50px; width: 36px; height: 1520px;
    display: flex; gap: 4px; opacity: 0.85; z-index: 12;
  }
  .cable-strand { width: 6px; height: 100%; border-radius: 3px; }
  .c-aqua { background: linear-gradient(180deg, #0891b2 0%, #06b6d4 50%, #0891b2 100%); box-shadow: 0 0 8px rgba(6,182,212,0.4); }
  .c-orange { background: linear-gradient(180deg, #ea580c 0%, #f97316 50%, #ea580c 100%); box-shadow: 0 0 8px rgba(249,115,22,0.4); }
  .c-yellow { background: linear-gradient(180deg, #ca8a04 0%, #eab308 50%, #ca8a04 100%); box-shadow: 0 0 8px rgba(234,179,8,0.4); }
  .raised-floor {
    position: absolute; top: 1580px; left: 0; width: 1080px; height: 340px;
    background: linear-gradient(180deg, #111722 0%, #0c1018 40%, #06090e 100%);
    border-top: 2px solid rgba(255, 255, 255, 0.08);
    box-shadow: inset 0 30px 60px rgba(56, 189, 248, 0.05), 0 -20px 50px rgba(0,0,0,0.9);
    background-image:
      linear-gradient(rgba(255,255,255,0.03) 1px, transparent 1px),
      linear-gradient(90deg, rgba(255,255,255,0.03) 1px, transparent 1px);
    background-size: 180px 120px;
  }
  .floor-reflection {
    position: absolute; top: 0; left: 50%; transform: translateX(-50%);
    width: 800px; height: 140px;
    background: radial-gradient(ellipse at 50% 0%, rgba(56, 189, 248, 0.12) 0%, rgba(16, 185, 129, 0.08) 35%, transparent 70%);
    pointer-events: none;
  }
  .safe-area-bottom {
    position: absolute; bottom: 0; left: 0; width: 1080px; height: 380px;
    background: linear-gradient(180deg, transparent 0%, rgba(4, 6, 9, 0.5) 100%);
    pointer-events: none;
  }
</style>
</head>
<body>
  <div class="dc-corridor"></div>
  <div class="overhead-light-bar"></div>
  <div class="server-rack-container">
    <div class="rack-rail"></div>
    <div class="server-stack">
      <!-- 1. Top Fiber Switch -->
      <div class="switch-unit">
        <div class="port-matrix">
          <div class="sfp-port"><div class="fiber-plug aqua"></div></div>
          <div class="sfp-port"><div class="fiber-plug aqua"></div></div>
          <div class="sfp-port"><div class="fiber-plug orange"></div></div>
          <div class="sfp-port"><div class="fiber-plug orange"></div></div>
          <div class="sfp-port"><div class="fiber-plug yellow"></div></div>
          <div class="sfp-port"><div class="fiber-plug yellow"></div></div>
          <div class="sfp-port"><div class="fiber-plug aqua"></div></div>
          <div class="sfp-port"><div class="fiber-plug aqua"></div></div>
          <div class="sfp-port"><div class="fiber-plug orange"></div></div>
          <div class="sfp-port"><div class="fiber-plug yellow"></div></div>
          <div class="sfp-port"><div class="fiber-plug aqua"></div></div>
          <div class="sfp-port"><div class="fiber-plug aqua"></div></div>
        </div>
        <div class="status-cluster">
          <div class="status-line"><div class="led-label"></div><div class="pulse-led"></div></div>
          <div class="status-line"><div class="led-label"></div><div class="pulse-led"></div></div>
        </div>
      </div>
      <!-- 2. Management Controller 1U -->
      <div class="chassis h-1u">
        <div class="status-cluster" style="width:120px"><div class="status-line"><div class="led-label"></div><div class="pulse-led"></div></div></div>
        <div class="honeycomb-grille" style="height:34px"></div>
        <div class="status-cluster" style="width:70px"><div class="status-line"><div class="led-label"></div><div class="pulse-led" style="background:#38bdf8;box-shadow:0 0 6px #38bdf8"></div></div></div>
      </div>
      <!-- 3. Server Node 2U -->
      <div class="chassis h-2u">
        <div class="drive-bay-group">
          <div class="drive-caddy"><div class="caddy-handle"></div><div class="caddy-led blue"></div></div>
          <div class="drive-caddy"><div class="caddy-handle"></div><div class="caddy-led blue"></div></div>
          <div class="drive-caddy"><div class="caddy-handle"></div><div class="caddy-led blue"></div></div>
          <div class="drive-caddy"><div class="caddy-handle"></div><div class="caddy-led blue"></div></div>
          <div class="drive-caddy"><div class="caddy-handle"></div><div class="caddy-led amber"></div></div>
        </div>
        <div class="honeycomb-grille"></div>
        <div class="status-cluster"><div class="status-line"><div class="led-label"></div><div class="pulse-led"></div></div><div class="status-line"><div class="led-label"></div><div class="pulse-led"></div></div></div>
      </div>
      <!-- 4. Core Enterprise Compute 4U -->
      <div class="chassis h-4u">
        <div class="drive-bay-group">
          <div class="drive-caddy"><div class="caddy-handle"></div><div class="caddy-led"></div></div>
          <div class="drive-caddy"><div class="caddy-handle"></div><div class="caddy-led"></div></div>
          <div class="drive-caddy"><div class="caddy-handle"></div><div class="caddy-led"></div></div>
          <div class="drive-caddy"><div class="caddy-handle"></div><div class="caddy-led"></div></div>
          <div class="drive-caddy"><div class="caddy-handle"></div><div class="caddy-led blue"></div></div>
        </div>
        <div class="honeycomb-grille" style="height:100px"></div>
        <div class="status-cluster">
          <div class="status-line"><div class="led-label"></div><div class="pulse-led"></div></div>
          <div class="status-line"><div class="led-label"></div><div class="pulse-led"></div></div>
          <div class="status-line"><div class="led-label"></div><div class="pulse-led"></div></div>
        </div>
      </div>
      <!-- 5. App Cluster Node 2U -->
      <div class="chassis h-2u">
        <div class="drive-bay-group">
          <div class="drive-caddy"><div class="caddy-handle"></div><div class="caddy-led"></div></div>
          <div class="drive-caddy"><div class="caddy-handle"></div><div class="caddy-led"></div></div>
          <div class="drive-caddy"><div class="caddy-handle"></div><div class="caddy-led"></div></div>
          <div class="drive-caddy"><div class="caddy-handle"></div><div class="caddy-led"></div></div>
          <div class="drive-caddy"><div class="caddy-handle"></div><div class="caddy-led"></div></div>
        </div>
        <div class="honeycomb-grille"></div>
        <div class="status-cluster"><div class="status-line"><div class="led-label"></div><div class="pulse-led"></div></div><div class="status-line"><div class="led-label"></div><div class="pulse-led"></div></div></div>
      </div>
      <!-- 6. Database Replica 2U -->
      <div class="chassis h-2u">
        <div class="drive-bay-group">
          <div class="drive-caddy"><div class="caddy-handle"></div><div class="caddy-led blue"></div></div>
          <div class="drive-caddy"><div class="caddy-handle"></div><div class="caddy-led blue"></div></div>
          <div class="drive-caddy"><div class="caddy-handle"></div><div class="caddy-led blue"></div></div>
          <div class="drive-caddy"><div class="caddy-handle"></div><div class="caddy-led blue"></div></div>
          <div class="drive-caddy"><div class="caddy-handle"></div><div class="caddy-led blue"></div></div>
        </div>
        <div class="honeycomb-grille"></div>
        <div class="status-cluster"><div class="status-line"><div class="led-label"></div><div class="pulse-led"></div></div><div class="status-line"><div class="led-label"></div><div class="pulse-led"></div></div></div>
      </div>
      <!-- 7. Heavy Persistence Store 4U -->
      <div class="chassis h-4u">
        <div class="drive-bay-group">
          <div class="drive-caddy"><div class="caddy-handle"></div><div class="caddy-led"></div></div>
          <div class="drive-caddy"><div class="caddy-handle"></div><div class="caddy-led"></div></div>
          <div class="drive-caddy"><div class="caddy-handle"></div><div class="caddy-led"></div></div>
          <div class="drive-caddy"><div class="caddy-handle"></div><div class="caddy-led"></div></div>
          <div class="drive-caddy"><div class="caddy-handle"></div><div class="caddy-led amber"></div></div>
        </div>
        <div class="honeycomb-grille" style="height:100px"></div>
        <div class="status-cluster">
          <div class="status-line"><div class="led-label"></div><div class="pulse-led"></div></div>
          <div class="status-line"><div class="led-label"></div><div class="pulse-led"></div></div>
          <div class="status-line"><div class="led-label"></div><div class="pulse-led"></div></div>
        </div>
      </div>
      <!-- 8. Failover Cluster 2U -->
      <div class="chassis h-2u">
        <div class="drive-bay-group">
          <div class="drive-caddy"><div class="caddy-handle"></div><div class="caddy-led"></div></div>
          <div class="drive-caddy"><div class="caddy-handle"></div><div class="caddy-led"></div></div>
          <div class="drive-caddy"><div class="caddy-handle"></div><div class="caddy-led"></div></div>
          <div class="drive-caddy"><div class="caddy-handle"></div><div class="caddy-led"></div></div>
          <div class="drive-caddy"><div class="caddy-handle"></div><div class="caddy-led"></div></div>
        </div>
        <div class="honeycomb-grille"></div>
        <div class="status-cluster"><div class="status-line"><div class="led-label"></div><div class="pulse-led"></div></div><div class="status-line"><div class="led-label"></div><div class="pulse-led"></div></div></div>
      </div>
      <!-- 9. Redundant Gateway 2U -->
      <div class="chassis h-2u">
        <div class="drive-bay-group">
          <div class="drive-caddy"><div class="caddy-handle"></div><div class="caddy-led blue"></div></div>
          <div class="drive-caddy"><div class="caddy-handle"></div><div class="caddy-led blue"></div></div>
          <div class="drive-caddy"><div class="caddy-handle"></div><div class="caddy-led blue"></div></div>
          <div class="drive-caddy"><div class="caddy-handle"></div><div class="caddy-led blue"></div></div>
          <div class="drive-caddy"><div class="caddy-handle"></div><div class="caddy-led blue"></div></div>
        </div>
        <div class="honeycomb-grille"></div>
        <div class="status-cluster"><div class="status-line"><div class="led-label"></div><div class="pulse-led"></div></div><div class="status-line"><div class="led-label"></div><div class="pulse-led"></div></div></div>
      </div>
      <!-- 10. Secondary Switch 1U -->
      <div class="switch-unit" style="height:62px">
        <div class="port-matrix">
          <div class="sfp-port"><div class="fiber-plug aqua"></div></div>
          <div class="sfp-port"><div class="fiber-plug aqua"></div></div>
          <div class="sfp-port"><div class="fiber-plug orange"></div></div>
          <div class="sfp-port"><div class="fiber-plug yellow"></div></div>
          <div class="sfp-port"><div class="fiber-plug aqua"></div></div>
          <div class="sfp-port"><div class="fiber-plug aqua"></div></div>
        </div>
        <div class="status-cluster"><div class="status-line"><div class="led-label"></div><div class="pulse-led"></div></div></div>
      </div>
      <!-- 11. Dual Enterprise UPS Power Station 3U -->
      <div class="chassis" style="height:115px">
        <div class="drive-bay-group" style="flex:1">
          <div class="drive-caddy" style="background:#131d2a;height:80px"><div class="caddy-handle"></div><div class="caddy-led"></div></div>
          <div class="drive-caddy" style="background:#131d2a;height:80px"><div class="caddy-handle"></div><div class="caddy-led"></div></div>
        </div>
        <div class="honeycomb-grille" style="flex:3;height:80px"></div>
        <div class="status-cluster">
          <div class="status-line"><div class="led-label"></div><div class="pulse-led"></div></div>
          <div class="status-line"><div class="led-label"></div><div class="pulse-led"></div></div>
        </div>
      </div>
    </div>
    <div class="rack-rail"></div>
  </div>
  <div class="cable-bundle">
    <div class="cable-strand c-aqua"></div>
    <div class="cable-strand c-orange"></div>
    <div class="cable-strand c-yellow"></div>
  </div>
  <div class="raised-floor"><div class="floor-reflection"></div></div>
  <div class="safe-area-bottom"></div>
</body>
</html>
"""

# =========================================================
# SCENE 3: Enterprise Architecture & Ecosystem (4 Tiers)
# =========================================================
SCENE_HTMLS["scene-03-enterprise-ecosystem.png"] = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    width: 1080px; height: 1920px; background: #06090e; overflow: hidden;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    position: relative;
  }
  .arch-bg {
    position: absolute; top: 0; left: 0; width: 1080px; height: 1920px;
    background: radial-gradient(circle at 50% 40%, #121c2d 0%, #090e17 55%, #05070a 100%);
  }
  .iso-grid {
    position: absolute; top: 0; left: 0; width: 1080px; height: 1920px;
    background-image:
      linear-gradient(rgba(56, 189, 248, 0.03) 1px, transparent 1px),
      linear-gradient(90deg, rgba(56, 189, 248, 0.03) 1px, transparent 1px);
    background-size: 60px 60px;
    mask-image: radial-gradient(circle at 50% 45%, black 40%, transparent 85%);
  }
  .core-glow {
    position: absolute; top: 350px; left: 50%; transform: translateX(-50%);
    width: 950px; height: 1000px;
    background: radial-gradient(circle at center, rgba(56, 189, 248, 0.12) 0%, rgba(16, 185, 129, 0.06) 45%, transparent 70%);
    filter: blur(60px);
  }
  .stack-container {
    position: absolute; top: 80px; left: 50%; transform: translateX(-50%);
    width: 960px; display: flex; flex-direction: column; gap: 20px; z-index: 10;
  }
  .arch-tier {
    width: 100%; background: linear-gradient(180deg, #111823 0%, #0d121b 100%);
    border-radius: 16px; border: 1px solid rgba(255, 255, 255, 0.08);
    box-shadow: 0 20px 50px rgba(0, 0, 0, 0.8), 0 0 30px rgba(56, 189, 248, 0.04);
    padding: 20px 24px; display: flex; flex-direction: column; gap: 14px; position: relative;
  }
  .tier-tag { display: flex; align-items: center; justify-content: space-between; }
  .tag-pill { height: 10px; width: 120px; background: #334155; border-radius: 5px; }
  .tag-status { width: 10px; height: 10px; border-radius: 50%; background: #10b981; box-shadow: 0 0 10px #10b981; }

  /* Ingress Cards */
  .ingress-row { display: flex; gap: 16px; }
  .ingress-card {
    flex: 1; height: 75px; background: #16202e; border-radius: 10px;
    border: 1px solid rgba(56, 189, 248, 0.2); box-shadow: 0 8px 16px rgba(0,0,0,0.5);
    display: flex; align-items: center; justify-content: space-around; padding: 0 16px;
  }
  .card-icon-hex { width: 32px; height: 32px; border-radius: 8px; background: rgba(56, 189, 248, 0.2); border: 1px solid #38bdf8; }
  .card-bars { display: flex; flex-direction: column; gap: 6px; width: 130px; }
  .c-bar-1 { height: 8px; background: #e2e8f0; border-radius: 4px; }
  .c-bar-2 { height: 6px; width: 65%; background: #64748b; border-radius: 3px; }

  /* Core Microservices Cluster (Spring Boot) */
  .service-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 14px; }
  .service-card {
    background: #141d2a; border-radius: 12px; border: 1px solid rgba(255, 255, 255, 0.06);
    box-shadow: 0 10px 20px rgba(0,0,0,0.6); padding: 16px; display: flex; flex-direction: column; gap: 10px;
  }
  .service-card.highlight { border-color: rgba(56, 189, 248, 0.35); background: #172436; }
  .svc-header { display: flex; align-items: center; gap: 10px; }
  .svc-dot { width: 12px; height: 12px; border-radius: 3px; background: #38bdf8; }
  .svc-dot.green { background: #10b981; }
  .svc-dot.amber { background: #f59e0b; }
  .svc-dot.purple { background: #c084fc; }
  .svc-metrics { display: flex; flex-direction: column; gap: 5px; }
  .m-track { height: 6px; background: #1f2937; border-radius: 3px; overflow: hidden; }
  .m-fill { height: 100%; border-radius: 3px; }

  /* Conduits & Bus lines */
  .bus-conduit {
    width: 100%; height: 44px; background: #0c121b; border-radius: 10px;
    border: 1px dashed rgba(56, 189, 248, 0.3); display: flex; align-items: center; justify-content: space-around;
    padding: 0 20px;
  }
  .bus-packet {
    width: 55px; height: 14px; background: rgba(56, 189, 248, 0.2); border-radius: 7px;
    border: 1px solid #38bdf8; box-shadow: 0 0 10px rgba(56, 189, 248, 0.4);
  }
  .bus-packet.orange {
    background: rgba(249, 115, 22, 0.2); border-color: #f97316; box-shadow: 0 0 10px rgba(249, 115, 22, 0.4);
  }

  /* Streaming Tier (Kafka) */
  .stream-tier {
    width: 100%; background: linear-gradient(180deg, #121822 0%, #0d121a 100%);
    border-radius: 16px; border: 1px solid rgba(255, 255, 255, 0.08);
    box-shadow: 0 20px 50px rgba(0, 0, 0, 0.8);
    padding: 18px 24px; display: flex; flex-direction: column; gap: 12px;
  }
  .stream-topics { display: flex; flex-direction: column; gap: 8px; }
  .topic-lane {
    height: 34px; background: #090d14; border-radius: 6px; border: 1px solid rgba(255, 255, 255, 0.04);
    display: flex; align-items: center; padding: 0 12px; gap: 10px;
  }
  .topic-badge { width: 60px; height: 14px; background: #1f2937; border-radius: 3px; }
  .msg-dots { display: flex; gap: 8px; flex: 1; justify-content: space-around; }
  .m-dot { width: 10px; height: 10px; border-radius: 50%; background: #38bdf8; box-shadow: 0 0 8px #38bdf8; }
  .m-dot.green { background: #10b981; box-shadow: 0 0 8px #10b981; }
  .m-dot.amber { background: #f59e0b; box-shadow: 0 0 8px #f59e0b; }

  /* Persistence Tier */
  .db-row { display: flex; gap: 16px; justify-content: center; }
  .db-cylinder-card {
    flex: 1; height: 110px; background: #131a26; border-radius: 12px;
    border: 1px solid rgba(255, 255, 255, 0.07); box-shadow: 0 10px 20px rgba(0,0,0,0.6);
    display: flex; align-items: center; justify-content: center; gap: 16px; padding: 12px;
  }
  .db-disk-stack { display: flex; flex-direction: column; gap: 5px; width: 44px; }
  .db-disk {
    height: 12px; background: #253346; border-radius: 6px; border: 1px solid rgba(56, 189, 248, 0.3);
  }

  .safe-area-lower {
    position: absolute; bottom: 0; left: 0; width: 1080px; height: 380px;
    background: linear-gradient(180deg, transparent 0%, rgba(5, 7, 10, 0.5) 100%);
    pointer-events: none;
  }
</style>
</head>
<body>
  <div class="arch-bg"></div>
  <div class="iso-grid"></div>
  <div class="core-glow"></div>
  <div class="stack-container">
    <!-- 1. Gateway & Edge Tier -->
    <div class="arch-tier">
      <div class="tier-tag"><div class="tag-pill"></div><div class="tag-status"></div></div>
      <div class="ingress-row">
        <div class="ingress-card"><div class="card-icon-hex"></div><div class="card-bars"><div class="c-bar-1"></div><div class="c-bar-2"></div></div></div>
        <div class="ingress-card"><div class="card-icon-hex" style="border-color:#10b981;background:rgba(16,185,129,0.2)"></div><div class="card-bars"><div class="c-bar-1"></div><div class="c-bar-2"></div></div></div>
        <div class="ingress-card"><div class="card-icon-hex" style="border-color:#f59e0b;background:rgba(245,158,11,0.2)"></div><div class="card-bars"><div class="c-bar-1"></div><div class="c-bar-2"></div></div></div>
      </div>
    </div>
    <!-- 2. Core Spring Boot Microservices Cluster -->
    <div class="arch-tier" style="padding:22px 24px">
      <div class="tier-tag"><div class="tag-pill" style="width:140px;background:#475569"></div><div class="tag-status"></div></div>
      <div class="service-grid">
        <div class="service-card highlight">
          <div class="svc-header"><div class="svc-dot"></div><div class="c-bar-1" style="width:80px"></div></div>
          <div class="svc-metrics"><div class="m-track"><div class="m-fill" style="width:75%;background:#38bdf8"></div></div><div class="m-track"><div class="m-fill" style="width:40%;background:#10b981"></div></div></div>
        </div>
        <div class="service-card">
          <div class="svc-header"><div class="svc-dot green"></div><div class="c-bar-1" style="width:70px"></div></div>
          <div class="svc-metrics"><div class="m-track"><div class="m-fill" style="width:85%;background:#10b981"></div></div><div class="m-track"><div class="m-fill" style="width:50%;background:#38bdf8"></div></div></div>
        </div>
        <div class="service-card">
          <div class="svc-header"><div class="svc-dot amber"></div><div class="c-bar-1" style="width:85px"></div></div>
          <div class="svc-metrics"><div class="m-track"><div class="m-fill" style="width:60%;background:#f59e0b"></div></div><div class="m-track"><div class="m-fill" style="width:30%;background:#10b981"></div></div></div>
        </div>
        <div class="service-card">
          <div class="svc-header"><div class="svc-dot purple"></div><div class="c-bar-1" style="width:75px"></div></div>
          <div class="svc-metrics"><div class="m-track"><div class="m-fill" style="width:90%;background:#c084fc"></div></div><div class="m-track"><div class="m-fill" style="width:65%;background:#38bdf8"></div></div></div>
        </div>
        <div class="service-card highlight">
          <div class="svc-header"><div class="svc-dot"></div><div class="c-bar-1" style="width:90px"></div></div>
          <div class="svc-metrics"><div class="m-track"><div class="m-fill" style="width:80%;background:#38bdf8"></div></div><div class="m-track"><div class="m-fill" style="width:55%;background:#10b981"></div></div></div>
        </div>
        <div class="service-card">
          <div class="svc-header"><div class="svc-dot green"></div><div class="c-bar-1" style="width:65px"></div></div>
          <div class="svc-metrics"><div class="m-track"><div class="m-fill" style="width:70%;background:#10b981"></div></div><div class="m-track"><div class="m-fill" style="width:45%;background:#f59e0b"></div></div></div>
        </div>
      </div>
    </div>
    <!-- 3. Distributed Event Streaming (Kafka) -->
    <div class="stream-tier">
      <div class="tier-tag"><div class="tag-pill" style="width:130px"></div><div class="tag-status" style="background:#38bdf8;box-shadow:0 0 10px #38bdf8"></div></div>
      <div class="stream-topics">
        <div class="topic-lane"><div class="topic-badge"></div><div class="msg-dots"><div class="m-dot"></div><div class="m-dot green"></div><div class="m-dot"></div><div class="m-dot amber"></div><div class="m-dot green"></div><div class="m-dot"></div></div></div>
        <div class="topic-lane"><div class="topic-badge" style="background:#263346"></div><div class="msg-dots"><div class="m-dot green"></div><div class="m-dot"></div><div class="m-dot amber"></div><div class="m-dot"></div><div class="m-dot green"></div><div class="m-dot"></div></div></div>
      </div>
    </div>
    <!-- 4. Distributed Persistence Tier -->
    <div class="arch-tier">
      <div class="tier-tag"><div class="tag-pill" style="width:110px"></div><div class="tag-status"></div></div>
      <div class="db-row">
        <div class="db-cylinder-card"><div class="db-disk-stack"><div class="db-disk"></div><div class="db-disk"></div><div class="db-disk"></div></div><div class="card-bars"><div class="c-bar-1"></div><div class="c-bar-2"></div></div></div>
        <div class="db-cylinder-card"><div class="db-disk-stack"><div class="db-disk" style="border-color:#10b981"></div><div class="db-disk" style="border-color:#10b981"></div><div class="db-disk" style="border-color:#10b981"></div></div><div class="card-bars"><div class="c-bar-1"></div><div class="c-bar-2"></div></div></div>
        <div class="db-cylinder-card"><div class="db-disk-stack"><div class="db-disk" style="border-color:#f59e0b"></div><div class="db-disk" style="border-color:#f59e0b"></div><div class="db-disk" style="border-color:#f59e0b"></div></div><div class="card-bars"><div class="c-bar-1"></div><div class="c-bar-2"></div></div></div>
      </div>
    </div>
  </div>
  <div class="safe-area-lower"></div>
</body>
</html>
"""

# =========================================================
# SCENE 4: Modern JVM Performance & Virtual Threads
# =========================================================
SCENE_HTMLS["scene-04-modern-performance.png"] = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    width: 1080px; height: 1920px; background: #06090e; overflow: hidden;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    position: relative;
  }
  .bg-grad {
    position: absolute; top: 0; left: 0; width: 1080px; height: 1920px;
    background: radial-gradient(circle at 50% 38%, #111a29 0%, #090d16 55%, #05070a 100%);
  }
  .grid-overlay {
    position: absolute; top: 0; left: 0; width: 1080px; height: 1920px;
    background-image:
      linear-gradient(rgba(56, 189, 248, 0.025) 1px, transparent 1px),
      linear-gradient(90deg, rgba(56, 189, 248, 0.025) 1px, transparent 1px);
    background-size: 50px 50px;
    mask-image: radial-gradient(circle at 50% 45%, black 40%, transparent 85%);
  }
  .ambient-glow {
    position: absolute; top: 250px; left: 50%; transform: translateX(-50%);
    width: 950px; height: 950px;
    background: radial-gradient(circle at center, rgba(16, 185, 129, 0.1) 0%, rgba(56, 189, 248, 0.08) 40%, transparent 70%);
    filter: blur(60px);
  }
  .jvm-dashboard {
    position: absolute; top: 70px; left: 50%; transform: translateX(-50%);
    width: 960px; display: flex; flex-direction: column; gap: 18px; z-index: 10;
  }
  /* Top Telemetry Meters */
  .meter-deck { display: flex; gap: 14px; }
  .meter-card {
    flex: 1; height: 120px; background: linear-gradient(180deg, #131c2a 0%, #0e141f 100%);
    border-radius: 14px; border: 1px solid rgba(255, 255, 255, 0.07);
    box-shadow: 0 15px 35px rgba(0,0,0,0.7); padding: 16px; display: flex; flex-direction: column; justify-content: space-between;
  }
  .meter-header { display: flex; justify-content: space-between; align-items: center; }
  .meter-label { width: 75px; height: 8px; background: #475569; border-radius: 4px; }
  .meter-led { width: 8px; height: 8px; border-radius: 50%; background: #10b981; box-shadow: 0 0 8px #10b981; }
  .meter-chart {
    height: 44px; background: linear-gradient(180deg, rgba(16, 185, 129, 0.2) 0%, transparent 100%);
    border-bottom: 2px solid #10b981; border-radius: 4px;
  }
  .meter-chart.blue {
    background: linear-gradient(180deg, rgba(56, 189, 248, 0.2) 0%, transparent 100%);
    border-color: #38bdf8;
  }
  .meter-chart.amber {
    background: linear-gradient(180deg, rgba(245, 158, 11, 0.2) 0%, transparent 100%);
    border-color: #f59e0b;
  }

  /* Virtual Threads Concurrency Matrix (Project Loom) */
  .concurrency-matrix {
    background: linear-gradient(180deg, #111824 0%, #0c121c 100%);
    border-radius: 16px; border: 1px solid rgba(255, 255, 255, 0.08);
    box-shadow: 0 30px 70px rgba(0,0,0,0.85), 0 0 40px rgba(56, 189, 248, 0.05);
    padding: 22px 26px; display: flex; flex-direction: column; gap: 14px;
  }
  .sec-title-bar { display: flex; align-items: center; justify-content: space-between; }
  .sec-title-bar .title-pill { width: 140px; height: 10px; background: #64748b; border-radius: 5px; }

  /* Thread Lanes */
  .thread-lanes { display: flex; flex-direction: column; gap: 8px; }
  .lane-row {
    height: 36px; background: #080c13; border-radius: 8px; border: 1px solid rgba(255, 255, 255, 0.04);
    display: flex; align-items: center; padding: 0 14px; gap: 10px; position: relative; overflow: hidden;
  }
  .carrier-tag { width: 34px; height: 16px; background: #1e293b; border-radius: 4px; }
  .fiber-track { flex: 1; height: 100%; display: flex; align-items: center; gap: 8px; }
  .fiber-pill { height: 12px; border-radius: 6px; }
  .f-cyan { width: 80px; background: #06b6d4; box-shadow: 0 0 8px rgba(6,182,212,0.5); }
  .f-emerald { width: 110px; background: #10b981; box-shadow: 0 0 8px rgba(16,185,129,0.5); }
  .f-blue { width: 95px; background: #38bdf8; box-shadow: 0 0 8px rgba(56,189,248,0.5); }
  .f-purple { width: 70px; background: #a855f7; box-shadow: 0 0 8px rgba(168,85,247,0.5); }
  .f-amber { width: 85px; background: #f59e0b; box-shadow: 0 0 8px rgba(245,158,11,0.5); }

  /* JIT Compilation Pipeline */
  .jit-pipeline {
    background: linear-gradient(180deg, #111824 0%, #0c121c 100%);
    border-radius: 16px; border: 1px solid rgba(255, 255, 255, 0.08);
    box-shadow: 0 25px 60px rgba(0,0,0,0.8);
    padding: 20px 26px; display: flex; flex-direction: column; gap: 14px;
  }
  .jit-stages { display: flex; gap: 12px; align-items: center; }
  .stage-box {
    flex: 1; height: 80px; background: #151f2e; border-radius: 10px;
    border: 1px solid rgba(255, 255, 255, 0.06); display: flex; flex-direction: column;
    justify-content: space-between; padding: 12px; box-shadow: 0 8px 16px rgba(0,0,0,0.5);
  }
  .stage-box.active { border-color: #10b981; background: #162635; }
  .stage-arrow { width: 18px; height: 2px; background: #475569; position: relative; }
  .stage-arrow::after {
    content: ''; position: absolute; right: 0; top: -3px;
    width: 0; height: 0; border-top: 4px solid transparent; border-bottom: 4px solid transparent;
    border-left: 6px solid #475569;
  }

  /* Memory Heap Allocations (Eden, Survivor, Tenured, Metaspace) */
  .heap-section {
    background: linear-gradient(180deg, #111824 0%, #0c121c 100%);
    border-radius: 16px; border: 1px solid rgba(255, 255, 255, 0.08);
    box-shadow: 0 25px 60px rgba(0,0,0,0.8);
    padding: 20px 26px; display: flex; flex-direction: column; gap: 12px;
  }
  .heap-bar-group { display: flex; height: 42px; gap: 6px; border-radius: 8px; overflow: hidden; background: #080c13; padding: 4px; }
  .heap-seg-eden { flex: 4; background: linear-gradient(90deg, #10b981 0%, #059669 100%); border-radius: 4px; }
  .heap-seg-surv { flex: 2; background: linear-gradient(90deg, #38bdf8 0%, #0284c7 100%); border-radius: 4px; }
  .heap-seg-tenured { flex: 6; background: linear-gradient(90deg, #6366f1 0%, #4338ca 100%); border-radius: 4px; }
  .heap-seg-meta { flex: 2; background: linear-gradient(90deg, #f59e0b 0%, #d97706 100%); border-radius: 4px; }

  .safe-area-lower {
    position: absolute; bottom: 0; left: 0; width: 1080px; height: 380px;
    background: linear-gradient(180deg, transparent 0%, rgba(5, 7, 10, 0.5) 100%);
    pointer-events: none;
  }
</style>
</head>
<body>
  <div class="bg-grad"></div>
  <div class="grid-overlay"></div>
  <div class="ambient-glow"></div>
  <div class="jvm-dashboard">
    <!-- Top Telemetry Meters -->
    <div class="meter-deck">
      <div class="meter-card"><div class="meter-header"><div class="meter-label"></div><div class="meter-led"></div></div><div class="meter-chart"></div></div>
      <div class="meter-card"><div class="meter-header"><div class="meter-label"></div><div class="meter-led" style="background:#38bdf8;box-shadow:0 0 8px #38bdf8"></div></div><div class="meter-chart blue"></div></div>
      <div class="meter-card"><div class="meter-header"><div class="meter-label"></div><div class="meter-led" style="background:#f59e0b;box-shadow:0 0 8px #f59e0b"></div></div><div class="meter-chart amber"></div></div>
    </div>
    <!-- Virtual Threads Matrix (Project Loom) - 8 Lanes -->
    <div class="concurrency-matrix">
      <div class="sec-title-bar"><div class="title-pill"></div><div class="meter-led"></div></div>
      <div class="thread-lanes">
        <div class="lane-row"><div class="carrier-tag"></div><div class="fiber-track"><div class="fiber-pill f-emerald"></div><div class="fiber-pill f-cyan"></div><div class="fiber-pill f-blue"></div><div class="fiber-pill f-purple"></div><div class="fiber-pill f-emerald"></div><div class="fiber-pill f-cyan"></div></div></div>
        <div class="lane-row"><div class="carrier-tag"></div><div class="fiber-track"><div class="fiber-pill f-blue"></div><div class="fiber-pill f-emerald"></div><div class="fiber-pill f-amber"></div><div class="fiber-pill f-cyan"></div><div class="fiber-pill f-purple"></div><div class="fiber-pill f-emerald"></div></div></div>
        <div class="lane-row"><div class="carrier-tag"></div><div class="fiber-track"><div class="fiber-pill f-purple"></div><div class="fiber-pill f-blue"></div><div class="fiber-pill f-emerald"></div><div class="fiber-pill f-amber"></div><div class="fiber-pill f-cyan"></div><div class="fiber-pill f-blue"></div></div></div>
        <div class="lane-row"><div class="carrier-tag"></div><div class="fiber-track"><div class="fiber-pill f-cyan"></div><div class="fiber-pill f-emerald"></div><div class="fiber-pill f-purple"></div><div class="fiber-pill f-blue"></div><div class="fiber-pill f-amber"></div><div class="fiber-pill f-emerald"></div></div></div>
        <div class="lane-row"><div class="carrier-tag"></div><div class="fiber-track"><div class="fiber-pill f-emerald"></div><div class="fiber-pill f-blue"></div><div class="fiber-pill f-cyan"></div><div class="fiber-pill f-emerald"></div><div class="fiber-pill f-purple"></div><div class="fiber-pill f-cyan"></div></div></div>
        <div class="lane-row"><div class="carrier-tag"></div><div class="fiber-track"><div class="fiber-pill f-amber"></div><div class="fiber-pill f-cyan"></div><div class="fiber-pill f-emerald"></div><div class="fiber-pill f-blue"></div><div class="fiber-pill f-emerald"></div><div class="fiber-pill f-amber"></div></div></div>
        <div class="lane-row"><div class="carrier-tag"></div><div class="fiber-track"><div class="fiber-pill f-cyan"></div><div class="fiber-pill f-purple"></div><div class="fiber-pill f-blue"></div><div class="fiber-pill f-emerald"></div><div class="fiber-pill f-cyan"></div><div class="fiber-pill f-purple"></div></div></div>
        <div class="lane-row"><div class="carrier-tag"></div><div class="fiber-track"><div class="fiber-pill f-emerald"></div><div class="fiber-pill f-amber"></div><div class="fiber-pill f-cyan"></div><div class="fiber-pill f-emerald"></div><div class="fiber-pill f-blue"></div><div class="fiber-pill f-emerald"></div></div></div>
      </div>
    </div>
    <!-- JIT Compilation Pipeline -->
    <div class="jit-pipeline">
      <div class="sec-title-bar"><div class="title-pill" style="width:110px"></div><div class="meter-led" style="background:#38bdf8;box-shadow:0 0 8px #38bdf8"></div></div>
      <div class="jit-stages">
        <div class="stage-box"><div class="meter-label" style="width:50px"></div><div style="height:6px;width:70%;background:#475569;border-radius:3px"></div></div>
        <div class="stage-arrow"></div>
        <div class="stage-box"><div class="meter-label" style="width:40px;background:#38bdf8"></div><div style="height:6px;width:85%;background:#38bdf8;border-radius:3px"></div></div>
        <div class="stage-arrow"></div>
        <div class="stage-box active"><div class="meter-label" style="width:45px;background:#10b981"></div><div style="height:6px;width:95%;background:#10b981;border-radius:3px"></div></div>
      </div>
    </div>
    <!-- Garbage Collection & Memory Management -->
    <div class="heap-section">
      <div class="sec-title-bar"><div class="title-pill" style="width:130px"></div><div class="meter-led" style="background:#f59e0b;box-shadow:0 0 8px #f59e0b"></div></div>
      <div class="heap-bar-group"><div class="heap-seg-eden"></div><div class="heap-seg-surv"></div><div class="heap-seg-tenured"></div><div class="heap-seg-meta"></div></div>
    </div>
  </div>
  <div class="safe-area-lower"></div>
</body>
</html>
"""

# =========================================================
# SCENE 5: Scale, Maintainability & Strong Typing (Blueprint)
# =========================================================
SCENE_HTMLS["scene-05-scale-and-maintainability.png"] = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    width: 1080px; height: 1920px; background: #06080e; overflow: hidden;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    position: relative;
  }
  .blueprint-bg {
    position: absolute; top: 0; left: 0; width: 1080px; height: 1920px;
    background: radial-gradient(circle at 50% 36%, #121c2d 0%, #080d15 55%, #040609 100%);
  }
  .grid-pattern {
    position: absolute; top: 0; left: 0; width: 1080px; height: 1920px;
    background-image:
      linear-gradient(rgba(56, 189, 248, 0.035) 1px, transparent 1px),
      linear-gradient(90deg, rgba(56, 189, 248, 0.035) 1px, transparent 1px);
    background-size: 40px 40px;
    mask-image: radial-gradient(circle at 50% 45%, black 40%, transparent 85%);
  }
  .ambient-glow {
    position: absolute; top: 300px; left: 50%; transform: translateX(-50%);
    width: 950px; height: 950px;
    background: radial-gradient(circle at center, rgba(56, 189, 248, 0.12) 0%, rgba(99, 102, 241, 0.06) 45%, transparent 70%);
    filter: blur(60px);
  }
  .blueprint-container {
    position: absolute; top: 75px; left: 50%; transform: translateX(-50%);
    width: 960px; display: flex; flex-direction: column; gap: 20px; z-index: 10;
  }
  .domain-card {
    background: linear-gradient(180deg, #121926 0%, #0c111c 100%);
    border-radius: 16px; border: 1px solid rgba(255, 255, 255, 0.08);
    box-shadow: 0 20px 50px rgba(0,0,0,0.85), 0 0 35px rgba(56, 189, 248, 0.04);
    padding: 20px 24px; display: flex; flex-direction: column; gap: 14px; position: relative;
  }
  .domain-header { display: flex; align-items: center; justify-content: space-between; }
  .domain-title { width: 130px; height: 10px; background: #64748b; border-radius: 5px; }
  .status-badge {
    width: 32px; height: 16px; background: rgba(16, 185, 129, 0.2); border-radius: 8px;
    border: 1px solid #10b981; display: flex; align-items: center; justify-content: center;
  }
  .status-badge::after { content: ''; width: 6px; height: 6px; border-radius: 50%; background: #10b981; }

  /* Interlocking Strong-Type Modules */
  .interlocking-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px; }
  .module-block {
    background: #151f2e; border-radius: 12px; border: 1px solid rgba(56, 189, 248, 0.15);
    padding: 16px; display: flex; flex-direction: column; gap: 12px;
    box-shadow: 0 10px 20px rgba(0,0,0,0.6); position: relative;
  }
  .module-block.verified { border-color: rgba(16, 185, 129, 0.3); background: #142332; }
  .contract-pins {
    display: flex; gap: 8px; position: absolute; top: -7px; right: 24px;
  }
  .pin { width: 14px; height: 6px; background: #38bdf8; border-radius: 3px; }
  .pin.green { background: #10b981; }

  .mod-header { display: flex; align-items: center; gap: 10px; }
  .mod-icon { width: 14px; height: 14px; border-radius: 4px; background: #38bdf8; }
  .mod-icon.green { background: #10b981; }
  .mod-icon.purple { background: #c084fc; }
  .mod-icon.amber { background: #f59e0b; }
  .mod-bar-1 { width: 110px; height: 8px; background: #e2e8f0; border-radius: 4px; }

  .interface-signature {
    display: flex; flex-direction: column; gap: 6px; background: #0a0e16; padding: 10px; border-radius: 6px;
    border: 1px solid rgba(255,255,255,0.03);
  }
  .sig-row { display: flex; gap: 8px; align-items: center; }
  .sig-type { width: 45px; height: 6px; background: #38bdf8; border-radius: 3px; }
  .sig-name { width: 75px; height: 6px; background: #64748b; border-radius: 3px; }
  .sig-ret { width: 35px; height: 6px; background: #10b981; border-radius: 3px; }

  /* Dependency Injection Conduits */
  .di-bus-channel {
    height: 40px; background: #0a0f18; border-radius: 10px; border: 1px solid rgba(255, 255, 255, 0.05);
    display: flex; align-items: center; justify-content: space-around; padding: 0 24px;
  }
  .di-node-chip {
    width: 60px; height: 16px; background: rgba(56, 189, 248, 0.15); border-radius: 8px;
    border: 1px solid #38bdf8;
  }

  .safe-area-lower {
    position: absolute; bottom: 0; left: 0; width: 1080px; height: 380px;
    background: linear-gradient(180deg, transparent 0%, rgba(4, 6, 9, 0.5) 100%);
    pointer-events: none;
  }
</style>
</head>
<body>
  <div class="blueprint-bg"></div>
  <div class="grid-pattern"></div>
  <div class="ambient-glow"></div>
  <div class="blueprint-container">
    <!-- Domain 1: Financial & Transaction Core -->
    <div class="domain-card">
      <div class="domain-header"><div class="domain-title"></div><div class="status-badge"></div></div>
      <div class="interlocking-grid">
        <div class="module-block verified">
          <div class="contract-pins"><div class="pin green"></div><div class="pin green"></div></div>
          <div class="mod-header"><div class="mod-icon green"></div><div class="mod-bar-1"></div></div>
          <div class="interface-signature">
            <div class="sig-row"><div class="sig-type"></div><div class="sig-name"></div><div class="sig-ret"></div></div>
            <div class="sig-row"><div class="sig-type" style="background:#c084fc"></div><div class="sig-name" style="width:90px"></div><div class="sig-ret"></div></div>
          </div>
        </div>
        <div class="module-block verified">
          <div class="contract-pins"><div class="pin green"></div><div class="pin green"></div></div>
          <div class="mod-header"><div class="mod-icon"></div><div class="mod-bar-1" style="width:95px"></div></div>
          <div class="interface-signature">
            <div class="sig-row"><div class="sig-type"></div><div class="sig-name" style="width:65px"></div><div class="sig-ret"></div></div>
            <div class="sig-row"><div class="sig-type" style="background:#f59e0b"></div><div class="sig-name" style="width:80px"></div><div class="sig-ret"></div></div>
          </div>
        </div>
      </div>
    </div>
    <!-- DI Conduit 1 -->
    <div class="di-bus-channel">
      <div class="di-node-chip"></div><div class="di-node-chip" style="border-color:#10b981;background:rgba(16,185,129,0.15)"></div><div class="di-node-chip"></div><div class="di-node-chip" style="border-color:#c084fc;background:rgba(192,132,252,0.15)"></div>
    </div>
    <!-- Domain 2: Security, Auth & RBAC Matrix -->
    <div class="domain-card">
      <div class="domain-header"><div class="domain-title" style="width:160px"></div><div class="status-badge"></div></div>
      <div class="interlocking-grid">
        <div class="module-block">
          <div class="contract-pins"><div class="pin"></div><div class="pin"></div></div>
          <div class="mod-header"><div class="mod-icon purple"></div><div class="mod-bar-1" style="width:105px"></div></div>
          <div class="interface-signature">
            <div class="sig-row"><div class="sig-type" style="background:#c084fc"></div><div class="sig-name"></div><div class="sig-ret"></div></div>
            <div class="sig-row"><div class="sig-type"></div><div class="sig-name" style="width:70px"></div><div class="sig-ret"></div></div>
          </div>
        </div>
        <div class="module-block">
          <div class="contract-pins"><div class="pin"></div><div class="pin"></div></div>
          <div class="mod-header"><div class="mod-icon amber"></div><div class="mod-bar-1" style="width:85px"></div></div>
          <div class="interface-signature">
            <div class="sig-row"><div class="sig-type" style="background:#f59e0b"></div><div class="sig-name" style="width:85px"></div><div class="sig-ret"></div></div>
            <div class="sig-row"><div class="sig-type"></div><div class="sig-name" style="width:60px"></div><div class="sig-ret"></div></div>
          </div>
        </div>
      </div>
    </div>
    <!-- DI Conduit 2 -->
    <div class="di-bus-channel">
      <div class="di-node-chip" style="border-color:#f59e0b;background:rgba(245,158,11,0.15)"></div><div class="di-node-chip"></div><div class="di-node-chip" style="border-color:#10b981;background:rgba(16,185,129,0.15)"></div><div class="di-node-chip"></div>
    </div>
    <!-- Domain 3: Scalable Data Infrastructure & Contract Schema -->
    <div class="domain-card">
      <div class="domain-header"><div class="domain-title" style="width:145px"></div><div class="status-badge"></div></div>
      <div class="interlocking-grid">
        <div class="module-block verified">
          <div class="contract-pins"><div class="pin green"></div><div class="pin green"></div></div>
          <div class="mod-header"><div class="mod-icon green"></div><div class="mod-bar-1" style="width:100px"></div></div>
          <div class="interface-signature">
            <div class="sig-row"><div class="sig-type"></div><div class="sig-name" style="width:80px"></div><div class="sig-ret"></div></div>
            <div class="sig-row"><div class="sig-type" style="background:#38bdf8"></div><div class="sig-name" style="width:60px"></div><div class="sig-ret"></div></div>
          </div>
        </div>
        <div class="module-block verified">
          <div class="contract-pins"><div class="pin green"></div><div class="pin green"></div></div>
          <div class="mod-header"><div class="mod-icon"></div><div class="mod-bar-1" style="width:90px"></div></div>
          <div class="interface-signature">
            <div class="sig-row"><div class="sig-type" style="background:#38bdf8"></div><div class="sig-name" style="width:75px"></div><div class="sig-ret"></div></div>
            <div class="sig-row"><div class="sig-type" style="background:#10b981"></div><div class="sig-name" style="width:65px"></div><div class="sig-ret"></div></div>
          </div>
        </div>
      </div>
    </div>
  </div>
  <div class="safe-area-lower"></div>
</body>
</html>
"""

# =========================================================
# SCENE 6: Real-World Mission-Critical Global Infrastructure
# =========================================================
SCENE_HTMLS["scene-06-real-world-usage.png"] = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    width: 1080px; height: 1920px; background: #06080e; overflow: hidden;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    position: relative;
  }
  .noc-bg {
    position: absolute; top: 0; left: 0; width: 1080px; height: 1920px;
    background: radial-gradient(circle at 50% 35%, #10192a 0%, #080c14 55%, #040508 100%);
  }
  .ambient-glow {
    position: absolute; top: 220px; left: 50%; transform: translateX(-50%);
    width: 950px; height: 900px;
    background: radial-gradient(circle at center, rgba(56, 189, 248, 0.14) 0%, rgba(37, 99, 235, 0.08) 45%, transparent 70%);
    filter: blur(60px);
  }
  .noc-wall {
    position: absolute; top: 70px; left: 50%; transform: translateX(-50%);
    width: 980px; display: flex; flex-direction: column; gap: 20px; z-index: 10;
  }
  /* Global Topology Display */
  .main-display {
    width: 100%; height: 560px; background: linear-gradient(180deg, #131c2b 0%, #0d131f 100%);
    border-radius: 20px; border: 1px solid rgba(255, 255, 255, 0.09);
    box-shadow: 0 35px 80px rgba(0,0,0,0.9), 0 0 50px rgba(56, 189, 248, 0.08);
    padding: 24px; display: flex; flex-direction: column; justify-content: space-between; position: relative; overflow: hidden;
  }
  .disp-header { display: flex; justify-content: space-between; align-items: center; }
  .disp-title { width: 140px; height: 10px; background: #64748b; border-radius: 5px; }
  .sla-badge {
    height: 24px; padding: 0 12px; background: rgba(16, 185, 129, 0.15); border: 1px solid #10b981;
    border-radius: 12px; display: flex; align-items: center; gap: 6px;
  }
  .sla-dot { width: 6px; height: 6px; border-radius: 50%; background: #10b981; box-shadow: 0 0 6px #10b981; }
  .world-map-svg {
    position: absolute; top: 70px; left: 50%; transform: translateX(-50%);
    width: 900px; height: 420px;
  }

  /* Operations Console Cards (4 Cards) */
  .console-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px; }
  .ops-card {
    height: 230px; background: linear-gradient(180deg, #111824 0%, #0c111a 100%);
    border-radius: 14px; border: 1px solid rgba(255, 255, 255, 0.07);
    box-shadow: 0 20px 45px rgba(0,0,0,0.75); padding: 18px; display: flex; flex-direction: column; justify-content: space-between;
  }
  .ops-card-header { display: flex; justify-content: space-between; align-items: center; }
  .ops-title { width: 90px; height: 8px; background: #475569; border-radius: 4px; }
  .ops-chart-area {
    height: 120px; background: #080c13; border-radius: 8px; border: 1px solid rgba(255, 255, 255, 0.04);
    padding: 10px; display: flex; flex-direction: column; justify-content: flex-end; position: relative; overflow: hidden;
  }
  .wave-svg { width: 100%; height: 100%; position: absolute; bottom: 0; left: 0; }

  /* Command Console Desk Surface */
  .console-desk {
    position: absolute; top: 1140px; left: 0; width: 1080px; height: 780px;
    background: linear-gradient(180deg, #111622 0%, #0b0f17 40%, #06080e 100%);
    border-top: 2px solid rgba(255, 255, 255, 0.08);
    box-shadow: inset 0 30px 60px rgba(56, 189, 248, 0.04), 0 -20px 40px rgba(0,0,0,0.9);
    display: flex; flex-direction: column; align-items: center; padding: 25px 40px 0 40px;
  }
  .desk-console-pad {
    width: 980px; height: 500px; background: #080c13; border-radius: 20px;
    border: 1px solid rgba(255, 255, 255, 0.05); box-shadow: 0 20px 50px rgba(0,0,0,0.9);
    padding: 25px; display: flex; flex-direction: column; gap: 16px;
  }
  .telemetry-row { display: flex; gap: 16px; width: 100%; }
  .terminal-strip {
    flex: 1; height: 110px; background: #0f1520; border-radius: 8px;
    border: 1px solid rgba(255, 255, 255, 0.05); padding: 14px; display: flex; flex-direction: column; gap: 8px;
  }
  .strip-line { height: 6px; background: #334155; border-radius: 3px; }

  .safe-area-lower {
    position: absolute; bottom: 0; left: 0; width: 1080px; height: 380px;
    background: linear-gradient(180deg, transparent 0%, rgba(4, 6, 9, 0.5) 100%);
    pointer-events: none;
  }
</style>
</head>
<body>
  <div class="noc-bg"></div>
  <div class="ambient-glow"></div>
  <div class="noc-wall">
    <!-- Main Topology Display -->
    <div class="main-display">
      <div class="disp-header"><div class="disp-title"></div><div class="sla-badge"><div class="sla-dot"></div></div></div>
      <svg class="world-map-svg" viewBox="0 0 900 420">
        <!-- Global Routing Arcs -->
        <path d="M 220 200 Q 420 90 520 180" fill="none" stroke="#38bdf8" stroke-width="2.5" stroke-dasharray="6,4" opacity="0.8"/>
        <path d="M 520 180 Q 680 110 760 230" fill="none" stroke="#10b981" stroke-width="2.5" stroke-dasharray="6,4" opacity="0.8"/>
        <path d="M 220 200 Q 500 300 760 230" fill="none" stroke="#f59e0b" stroke-width="2.5" stroke-dasharray="6,4" opacity="0.8"/>
        <path d="M 220 200 Q 350 270 500 260" fill="none" stroke="#38bdf8" stroke-width="2" opacity="0.6"/>
        <path d="M 500 260 Q 620 270 760 230" fill="none" stroke="#10b981" stroke-width="2" opacity="0.6"/>

        <!-- Hub Nodes -->
        <!-- New York -->
        <circle cx="220" cy="200" r="16" fill="rgba(56, 189, 248, 0.2)" stroke="#38bdf8" stroke-width="2"/>
        <circle cx="220" cy="200" r="7" fill="#38bdf8"/>
        <!-- London / Frankfurt -->
        <circle cx="520" cy="180" r="18" fill="rgba(16, 185, 129, 0.2)" stroke="#10b981" stroke-width="2"/>
        <circle cx="520" cy="180" r="8" fill="#10b981"/>
        <!-- Singapore / Tokyo -->
        <circle cx="760" cy="230" r="16" fill="rgba(245, 158, 11, 0.2)" stroke="#f59e0b" stroke-width="2"/>
        <circle cx="760" cy="230" r="7" fill="#f59e0b"/>
        <!-- Mid Transit Hubs -->
        <circle cx="500" cy="260" r="12" fill="rgba(99, 102, 241, 0.2)" stroke="#6366f1" stroke-width="1.5"/>
        <circle cx="500" cy="260" r="5" fill="#6366f1"/>
      </svg>
      <div style="display:flex;justify-content:space-between;align-items:center;z-index:2">
        <div style="display:flex;gap:12px"><div class="disp-title" style="width:70px"></div><div class="disp-title" style="width:90px;background:#38bdf8"></div></div>
        <div class="disp-title" style="width:80px;background:#10b981"></div>
      </div>
    </div>

    <!-- Operations Telemetry Grid (4 Cards) -->
    <div class="console-grid">
      <div class="ops-card">
        <div class="ops-card-header"><div class="ops-title"></div><div class="sla-dot"></div></div>
        <div class="ops-chart-area">
          <svg class="wave-svg" viewBox="0 0 400 120" preserveAspectRatio="none">
            <path d="M 0 100 Q 50 40 100 70 T 200 40 T 300 80 T 400 30 L 400 120 L 0 120 Z" fill="rgba(56, 189, 248, 0.15)"/>
            <path d="M 0 100 Q 50 40 100 70 T 200 40 T 300 80 T 400 30" fill="none" stroke="#38bdf8" stroke-width="2.5"/>
          </svg>
        </div>
      </div>
      <div class="ops-card">
        <div class="ops-card-header"><div class="ops-title" style="width:110px"></div><div class="sla-dot" style="background:#38bdf8;box-shadow:0 0 6px #38bdf8"></div></div>
        <div class="ops-chart-area">
          <svg class="wave-svg" viewBox="0 0 400 120" preserveAspectRatio="none">
            <path d="M 0 90 Q 60 110 120 60 T 240 70 T 320 30 T 400 45 L 400 120 L 0 120 Z" fill="rgba(16, 185, 129, 0.15)"/>
            <path d="M 0 90 Q 60 110 120 60 T 240 70 T 320 30 T 400 45" fill="none" stroke="#10b981" stroke-width="2.5"/>
          </svg>
        </div>
      </div>
      <div class="ops-card">
        <div class="ops-card-header"><div class="ops-title" style="width:85px"></div><div class="sla-dot" style="background:#f59e0b;box-shadow:0 0 6px #f59e0b"></div></div>
        <div class="ops-chart-area">
          <div style="display:flex;flex-direction:column;gap:8px;padding-top:10px">
            <div style="height:8px;background:#1e293b;border-radius:4px;overflow:hidden"><div style="height:100%;width:88%;background:#f59e0b"></div></div>
            <div style="height:8px;background:#1e293b;border-radius:4px;overflow:hidden"><div style="height:100%;width:64%;background:#10b981"></div></div>
            <div style="height:8px;background:#1e293b;border-radius:4px;overflow:hidden"><div style="height:100%;width:92%;background:#38bdf8"></div></div>
          </div>
        </div>
      </div>
      <div class="ops-card">
        <div class="ops-card-header"><div class="ops-title" style="width:100px"></div><div class="sla-dot" style="background:#c084fc;box-shadow:0 0 6px #c084fc"></div></div>
        <div class="ops-chart-area">
          <svg class="wave-svg" viewBox="0 0 400 120" preserveAspectRatio="none">
            <path d="M 0 70 Q 70 30 140 80 T 280 40 T 400 60 L 400 120 L 0 120 Z" fill="rgba(192, 132, 252, 0.15)"/>
            <path d="M 0 70 Q 70 30 140 80 T 280 40 T 400 60" fill="none" stroke="#c084fc" stroke-width="2.5"/>
          </svg>
        </div>
      </div>
    </div>
  </div>

  <!-- Lower Desk -->
  <div class="console-desk">
    <div class="desk-console-pad">
      <div class="telemetry-row">
        <div class="terminal-strip"><div class="strip-line" style="width:80px;background:#38bdf8"></div><div class="strip-line" style="width:180px"></div><div class="strip-line" style="width:140px"></div></div>
        <div class="terminal-strip"><div class="strip-line" style="width:90px;background:#10b981"></div><div class="strip-line" style="width:160px"></div><div class="strip-line" style="width:130px"></div></div>
      </div>
      <div class="telemetry-row">
        <div class="terminal-strip"><div class="strip-line" style="width:70px;background:#f59e0b"></div><div class="strip-line" style="width:190px"></div></div>
        <div class="terminal-strip"><div class="strip-line" style="width:100px;background:#c084fc"></div><div class="strip-line" style="width:150px"></div></div>
      </div>
    </div>
  </div>
  <div class="safe-area-lower"></div>
</body>
</html>
"""

# =========================================================
# SCENE 7: Future of Java & Conclusion Cockpit
# =========================================================
SCENE_HTMLS["scene-07-conclusion.png"] = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    width: 1080px; height: 1920px; background: #06090e; overflow: hidden;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    position: relative;
  }
  .cockpit-wall {
    position: absolute; top: 0; left: 0; width: 1080px; height: 1150px;
    background: radial-gradient(circle at 65% 28%, #162030 0%, #0c1119 55%, #070a0f 100%);
  }
  .acoustic-slats {
    position: absolute; top: 0; left: 0; width: 1080px; height: 1150px;
    background: repeating-linear-gradient(
      90deg, rgba(255, 255, 255, 0.018) 0px, rgba(255, 255, 255, 0.018) 16px,
      transparent 16px, transparent 32px
    );
    mask-image: radial-gradient(circle at 60% 35%, rgba(0,0,0,0.85) 0%, transparent 80%);
  }
  .warm-lamp {
    position: absolute; top: 0; right: 0; width: 600px; height: 1400px;
    background: radial-gradient(ellipse at 90% 12%, rgba(245, 158, 11, 0.1) 0%, rgba(245, 158, 11, 0.03) 45%, transparent 75%);
    filter: blur(50px); pointer-events: none;
  }
  .dual-ambient-glow {
    position: absolute; top: 70px; left: 50%; transform: translateX(-50%);
    width: 1040px; height: 950px;
    background: radial-gradient(ellipse at center, rgba(56, 189, 248, 0.16) 0%, rgba(16, 185, 129, 0.08) 50%, transparent 75%);
    filter: blur(60px);
  }

  /* Dual Screen Cockpit Container */
  .cockpit-screens {
    position: absolute; top: 70px; left: 50%; transform: translateX(-50%);
    width: 1020px; display: flex; gap: 16px; justify-content: center; z-index: 10;
  }

  /* Left Screen: Modern IDE with Success build */
  .screen-card {
    flex: 1; height: 900px; background: linear-gradient(180deg, #182232 0%, #0f1522 100%);
    border-radius: 18px; padding: 10px; border: 1px solid rgba(255, 255, 255, 0.09);
    box-shadow: 0 35px 80px rgba(0,0,0,0.9), 0 0 35px rgba(56, 189, 248, 0.06);
    display: flex; flex-direction: column;
  }
  .screen-card.right-disp {
    box-shadow: 0 35px 80px rgba(0,0,0,0.9), 0 0 35px rgba(16, 185, 129, 0.06);
  }
  .inner-display {
    flex: 1; background: #090d14; border-radius: 10px; overflow: hidden; display: flex;
    flex-direction: column; border: 1px solid rgba(255, 255, 255, 0.05);
  }
  .title-bar-tabs {
    height: 36px; background: #080b10; border-bottom: 1px solid rgba(255, 255, 255, 0.05);
    display: flex; align-items: center; padding: 0 12px; gap: 6px;
  }
  .tab-pill {
    height: 24px; width: 100px; background: #111722; border-radius: 4px;
    display: flex; align-items: center; padding: 0 8px; gap: 6px;
  }

  .left-code-body {
    flex: 1; padding: 18px 16px; display: flex; flex-direction: column; gap: 7px;
  }
  .c-row { display: flex; gap: 6px; align-items: center; }
  .c-num { width: 18px; height: 6px; background: #1e293b; border-radius: 3px; margin-right: 8px; }
  .t-ann { height: 7px; background: #fbbf24; border-radius: 3px; }
  .t-kw { height: 7px; background: #c084fc; border-radius: 3px; }
  .t-type { height: 7px; background: #38bdf8; border-radius: 3px; }
  .t-fn { height: 7px; background: #60a5fa; border-radius: 3px; }
  .t-str { height: 7px; background: #34d399; border-radius: 3px; }
  .t-var { height: 7px; background: #f472b6; border-radius: 3px; }

  /* Success Build Banner at Bottom of IDE */
  .build-success-banner {
    height: 95px; background: #061512; border-top: 1px solid rgba(16, 185, 129, 0.3);
    padding: 12px 16px; display: flex; flex-direction: column; justify-content: center; gap: 6px;
  }
  .success-chip { display: flex; align-items: center; gap: 8px; }
  .success-dot { width: 10px; height: 10px; border-radius: 50%; background: #10b981; box-shadow: 0 0 10px #10b981; }

  /* Right Screen: Production Live Telemetry Dashboard */
  .right-telemetry-body {
    flex: 1; padding: 18px 16px; display: flex; flex-direction: column; gap: 12px;
  }
  .kpi-card {
    background: #111824; border-radius: 8px; border: 1px solid rgba(255, 255, 255, 0.05);
    padding: 12px; display: flex; flex-direction: column; gap: 8px;
  }
  .kpi-chart {
    height: 70px; background: linear-gradient(180deg, rgba(16, 185, 129, 0.15) 0%, transparent 100%);
    border-bottom: 2px solid #10b981; border-radius: 4px;
  }

  /* Dual Stand Assembly */
  .cockpit-stands {
    position: absolute; top: 970px; left: 50%; transform: translateX(-50%);
    width: 800px; display: flex; justify-content: space-around; z-index: 8;
  }
  .c-stand {
    width: 60px; height: 75px; background: linear-gradient(90deg, #182230 0%, #2b394d 50%, #182230 100%);
  }

  /* Full Lower Desk Assembly */
  .desk-plane {
    position: absolute; top: 1040px; left: 0; width: 1080px; height: 880px;
    background: linear-gradient(180deg, #141b26 0%, #0f151f 35%, #0a0e16 100%);
    border-top: 2px solid rgba(255, 255, 255, 0.08);
    box-shadow: inset 0 30px 60px rgba(56, 189, 248, 0.04), 0 -20px 40px rgba(0,0,0,0.9);
    display: flex; flex-direction: column; align-items: center; padding: 25px 40px 0 40px;
  }
  .desk-mat {
    width: 1000px; height: 720px; background: #080b11; border-radius: 24px;
    border: 1px solid rgba(255, 255, 255, 0.04);
    box-shadow: 0 25px 60px rgba(0,0,0,0.95), inset 0 0 0 1px rgba(255, 255, 255, 0.03);
    display: flex; flex-direction: column; align-items: center; padding: 30px 50px; position: relative;
  }
  .desk-gear {
    width: 100%; display: flex; align-items: center; justify-content: center; gap: 45px; margin-top: 10px;
  }
  .keyboard-assembly {
    display: flex; flex-direction: column; gap: 12px; align-items: center;
  }
  .keyboard {
    width: 620px; height: 230px; background: #0e131d; border-radius: 14px;
    border: 1px solid rgba(255, 255, 255, 0.08);
    box-shadow: 0 20px 45px rgba(0,0,0,0.85), 0 0 25px rgba(16, 185, 129, 0.06);
    padding: 18px; display: flex; flex-direction: column; gap: 8px;
  }
  .wrist-rest {
    width: 620px; height: 70px; background: linear-gradient(180deg, #141c28 0%, #0c121b 100%);
    border-radius: 10px; border: 1px solid rgba(255, 255, 255, 0.05);
    box-shadow: 0 10px 20px rgba(0,0,0,0.6);
  }
  .kb-line { display: flex; gap: 7px; flex: 1; }
  .k-cap { flex: 1; background: #182232; border-radius: 5px; box-shadow: 0 3px 0 #0d121c; }
  .k-cap.mod { background: #222e42; }
  .k-cap.accent { background: #164e3d; }
  .k-cap.space { flex: 4.5; }
  .mouse {
    width: 90px; height: 155px; background: linear-gradient(180deg, #1d2638 0%, #111722 100%);
    border-radius: 45px; box-shadow: 0 18px 35px rgba(0,0,0,0.75);
    border: 1px solid rgba(255, 255, 255, 0.06); position: relative;
  }
  .mouse-roller {
    position: absolute; top: 26px; left: 50%; transform: translateX(-50%);
    width: 11px; height: 28px; background: #2d3b52; border-radius: 6px;
  }
  .coffee-station {
    position: absolute; right: 50px; top: 50px; width: 95px; height: 95px;
    background: radial-gradient(circle at 40% 40%, #1e2838 0%, #101622 100%);
    border-radius: 50%; box-shadow: 0 18px 35px rgba(0,0,0,0.85), inset 0 0 0 9px #151d2a;
    display: flex; align-items: center; justify-content: center;
  }
  .coffee-fill {
    width: 62px; height: 62px; background: #1a120b; border-radius: 50%;
    box-shadow: inset 0 2px 8px rgba(0,0,0,0.9);
  }
  .screen-desk-reflection {
    position: absolute; top: 0; left: 50%; transform: translateX(-50%);
    width: 850px; height: 130px;
    background: radial-gradient(ellipse at 50% 0%, rgba(16, 185, 129, 0.1) 0%, transparent 70%);
    pointer-events: none;
  }
  .safe-area-lower {
    position: absolute; bottom: 0; left: 0; width: 1080px; height: 380px;
    background: linear-gradient(180deg, transparent 0%, rgba(7, 10, 15, 0.5) 100%);
    pointer-events: none;
  }
</style>
</head>
<body>
  <div class="cockpit-wall"></div>
  <div class="acoustic-slats"></div>
  <div class="warm-lamp"></div>
  <div class="dual-ambient-glow"></div>
  <div class="cockpit-screens">
    <!-- Left Screen: Modern IDE with Successful Build -->
    <div class="screen-card">
      <div class="inner-display">
        <div class="title-bar-tabs">
          <div class="tab-pill"><div style="width:8px;height:8px;border-radius:2px;background:#38bdf8"></div><div style="height:6px;width:60px;background:#64748b;border-radius:3px"></div></div>
        </div>
        <div class="left-code-body">
          <div class="c-row"><div class="c-num"></div><div class="t-ann" style="width:90px"></div></div>
          <div class="c-row"><div class="c-num"></div><div class="t-kw" style="width:40px"></div><div class="t-type" style="width:90px"></div></div>
          <div class="c-row"><div class="c-num"></div></div>
          <div class="c-row" style="margin-left:16px"><div class="c-num"></div><div class="t-ann" style="width:75px"></div></div>
          <div class="c-row" style="margin-left:16px"><div class="c-num"></div><div class="t-kw" style="width:45px"></div><div class="t-type" style="width:60px"></div><div class="t-fn" style="width:100px"></div></div>
          <div class="c-row" style="margin-left:32px"><div class="c-num"></div><div class="t-var" style="width:65px"></div><div class="t-fn" style="width:70px"></div><div class="t-str" style="width:85px"></div></div>
          <div class="c-row" style="margin-left:16px"><div class="c-num"></div><div class="t-kw" style="width:25px"></div></div>
          <div class="c-row"><div class="c-num"></div></div>
          <div class="c-row" style="margin-left:16px"><div class="c-num"></div><div class="t-ann" style="width:80px"></div></div>
          <div class="c-row" style="margin-left:16px"><div class="c-num"></div><div class="t-kw" style="width:45px"></div><div class="t-type" style="width:65px"></div><div class="t-fn" style="width:95px"></div></div>
          <div class="c-row" style="margin-left:32px"><div class="c-num"></div><div class="t-kw" style="width:35px"></div><div class="t-fn" style="width:80px"></div></div>
          <div class="c-row" style="margin-left:16px"><div class="c-num"></div><div class="t-kw" style="width:25px"></div></div>
          <div class="c-row" style="margin-left:16px"><div class="c-num"></div><div class="t-ann" style="width:70px"></div></div>
          <div class="c-row" style="margin-left:16px"><div class="c-num"></div><div class="t-kw" style="width:40px"></div><div class="t-type" style="width:85px"></div></div>
          <div class="c-row" style="margin-left:32px"><div class="c-num"></div><div class="t-var" style="width:90px"></div><div class="t-fn" style="width:75px"></div></div>
          <div class="c-row" style="margin-left:16px"><div class="c-num"></div><div class="t-kw" style="width:25px"></div></div>
          <div class="c-row" style="margin-left:16px"><div class="c-num"></div><div class="t-ann" style="width:65px"></div></div>
          <div class="c-row" style="margin-left:16px"><div class="c-num"></div><div class="t-kw" style="width:40px"></div><div class="t-fn" style="width:105px"></div></div>
          <div class="c-row" style="margin-left:16px"><div class="c-num"></div><div class="t-kw" style="width:25px"></div></div>
        </div>
        <div class="build-success-banner">
          <div class="success-chip"><div class="success-dot"></div><div style="height:8px;width:120px;background:#10b981;border-radius:4px"></div></div>
          <div style="height:6px;width:180px;background:#334155;border-radius:3px"></div>
        </div>
      </div>
    </div>

    <!-- Right Screen: Production Live Dashboard -->
    <div class="screen-card right-disp">
      <div class="inner-display">
        <div class="title-bar-tabs">
          <div class="tab-pill" style="border:1px solid rgba(16,185,129,0.3)"><div style="width:8px;height:8px;border-radius:2px;background:#10b981"></div><div style="height:6px;width:70px;background:#64748b;border-radius:3px"></div></div>
        </div>
        <div class="right-telemetry-body">
          <div class="kpi-card">
            <div style="display:flex;justify-content:space-between"><div style="height:7px;width:80px;background:#64748b;border-radius:3px"></div><div class="success-dot"></div></div>
            <div class="kpi-chart"></div>
          </div>
          <div class="kpi-card">
            <div style="display:flex;justify-content:space-between"><div style="height:7px;width:95px;background:#64748b;border-radius:3px"></div><div class="success-dot" style="background:#38bdf8;box-shadow:0 0 10px #38bdf8"></div></div>
            <div class="kpi-chart" style="border-color:#38bdf8;background:linear-gradient(180deg, rgba(56,189,248,0.15) 0%, transparent 100%)"></div>
          </div>
          <div class="kpi-card" style="padding:12px">
            <div style="display:flex;flex-direction:column;gap:6px">
              <div style="height:6px;background:#1e293b;border-radius:3px;overflow:hidden"><div style="height:100%;width:88%;background:#10b981"></div></div>
              <div style="height:6px;background:#1e293b;border-radius:3px;overflow:hidden"><div style="height:100%;width:72%;background:#38bdf8"></div></div>
            </div>
          </div>
          <div class="kpi-card" style="padding:10px">
            <div style="display:flex;gap:6px">
              <div style="flex:1;height:24px;background:rgba(16,185,129,0.15);border:1px solid #10b981;border-radius:4px"></div>
              <div style="flex:1;height:24px;background:rgba(56,189,248,0.15);border:1px solid #38bdf8;border-radius:4px"></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <div class="cockpit-stands"><div class="c-stand"></div><div class="c-stand"></div></div>

  <!-- Lower Desk -->
  <div class="desk-plane">
    <div class="desk-mat">
      <div class="screen-desk-reflection"></div>
      <div class="desk-gear">
        <div class="keyboard-assembly">
          <div class="keyboard">
            <div class="kb-line"><div class="k-cap"></div><div class="k-cap"></div><div class="k-cap"></div><div class="k-cap"></div><div class="k-cap"></div><div class="k-cap"></div><div class="k-cap"></div><div class="k-cap"></div><div class="k-cap"></div><div class="k-cap"></div><div class="k-cap"></div></div>
            <div class="kb-line"><div class="k-cap mod"></div><div class="k-cap"></div><div class="k-cap"></div><div class="k-cap"></div><div class="k-cap"></div><div class="k-cap"></div><div class="k-cap"></div><div class="k-cap"></div><div class="k-cap"></div><div class="k-cap"></div><div class="k-cap mod"></div></div>
            <div class="kb-line"><div class="k-cap mod"></div><div class="k-cap"></div><div class="k-cap"></div><div class="k-cap"></div><div class="k-cap"></div><div class="k-cap"></div><div class="k-cap"></div><div class="k-cap"></div><div class="k-cap"></div><div class="k-cap mod"></div><div class="k-cap mod"></div></div>
            <div class="kb-line"><div class="k-cap mod"></div><div class="k-cap"></div><div class="k-cap"></div><div class="k-cap space"></div><div class="k-cap"></div><div class="k-cap accent"></div><div class="k-cap mod"></div></div>
          </div>
          <div class="wrist-rest"></div>
        </div>
        <div class="mouse"><div class="mouse-roller"></div></div>
      </div>
      <div class="coffee-station"><div class="coffee-fill"></div></div>
    </div>
  </div>
  <div class="safe-area-lower"></div>
</body>
</html>
"""

def render_all_images():
    print("--- Rendering 7 Scenes via Chrome Headless ---")
    for filename, html_content in SCENE_HTMLS.items():
        html_file = SCRATCH_HTML / f"{filename}.html"
        html_file.write_text(html_content, encoding="utf-8")
        out_asset = ASSETS_IMAGES / filename
        out_dist = DIST_IMAGES / filename

        cmd = [
            CHROME_BIN,
            "--headless",
            f"--screenshot={out_asset}",
            "--window-size=1080,1920",
            "--hide-scrollbars",
            f"file://{html_file.resolve()}"
        ]
        subprocess.run(cmd, check=True)
        shutil.copyfile(out_asset, out_dist)
        print(f"Rendered: {filename} -> {out_asset.stat().st_size} bytes")

def create_script_json():
    script_data = {
        "project": {
            "id": "thai-java-zone-why-java-alive",
            "title": "Java ทำไมยังไม่ตาย? ทำไมองค์กรใหญ่ยังใช้ Java กันเต็มไปหมด",
            "language": "th-TH",
            "resolution": "1080x1920",
            "fps": 30
        },
        "voice": {
            "provider": "google-gemini",
            "voice": "Fenrir",
            "speed": 1.0,
            "style_prompt": (
                "Read aloud in a natural, friendly, confident senior software engineer tone in Thai. "
                "Conversational, easy to understand, slightly playful yet professional. "
                "Keep common technical terms in English natural. Never sound robotic or like a news anchor."
            )
        },
        "scenes": [
            {
                "id": "scene-01-hook",
                "image": "images/scene-01-hook.png",
                "narration": "รู้มั้ยครับว่า ทุกครั้งที่เราโอนเงิน จองตั๋วเครื่องบิน หรือช้อปปิ้งออนไลน์ เบื้องหลังแทบทั้งหมด... ยังเป็น Java!",
                "tts_text": "รู้มั้ยครับว่า ทุกครั้งที่เราโอนเงิน จองตั๋วเครื่องบิน หรือช้อปปิ้งออนไลน์ เบื้องหลังแทบทั้งหมด... ยังเป็น จาวา!",
                "subtitle": "รู้มั้ยครับว่า ระบบเบื้องหลังที่เราใช้ทุกวัน... ยังเป็น Java แทบทั้งหมด!",
                "show_subtitle": True,
                "motion": "cinematic_push_in",
                "transition": "fade",
                "motion_speed": "slow",
                "estimated_duration": 6.5
            },
            {
                "id": "scene-02-stability",
                "image": "images/scene-02-stability.png",
                "narration": "หลายคนบอกว่า Java มันเก่า เชย เขียนยาว... แต่ทำไมธนาคารและองค์กรระดับ Fortune 500 ถึงไม่ยอมเปลี่ยน?",
                "tts_text": "หลายคนบอกว่า จาวา มันเก่า เชย เขียนยาว... แต่ทำไมธนาคารและองค์กรระดับ ฟอร์จูน ไฟฟ์ฮันเดรด ถึงไม่ยอมเปลี่ยน?",
                "subtitle": "หลายคนบอกว่า Java เก่าและเชย... แต่ทำไมธนาคารระดับโลกยังใช้อยู่?",
                "show_subtitle": True,
                "motion": "documentary_pan",
                "transition": "fade",
                "motion_speed": "slow",
                "estimated_duration": 6.5
            },
            {
                "id": "scene-03-enterprise-ecosystem",
                "image": "images/scene-03-enterprise-ecosystem.png",
                "narration": "คำตอบแรกคือ Ecosystem ครับ! กว่า 25 ปีที่ผ่านมา Java มี Library, Framework อย่าง Spring Boot และเครื่องมือระดับ Enterprise ครบวงจรที่สุดในโลก อยากทำระบบอะไร... มีคนแก้ปัญหาและทดสอบมาให้หมดแล้ว",
                "tts_text": "คำตอบแรกคือ อีโคซิสเต็ม ครับ! กว่า ยี่สิบห้า ปีที่ผ่านมา จาวา มี ไลบรารี เฟรมเวิร์ก อย่าง สปริง บูท และเครื่องมือระดับ เอ็นเตอร์ไพรส์ ครบวงจรที่สุดในโลก",
                "subtitle": "คำตอบแรกคือ Ecosystem และ Spring Boot ที่มีเครื่องมือ Enterprise ครบที่สุดในโลก",
                "show_subtitle": True,
                "motion": "slow_zoom_in",
                "transition": "fade",
                "motion_speed": "slow",
                "estimated_duration": 8.5
            },
            {
                "id": "scene-04-modern-performance",
                "image": "images/scene-04-modern-performance.png",
                "narration": "สองคือ Performance ที่โหดขึ้นเรื่อยๆ JVM ยุคใหม่มี JIT Compiler ปรับแต่งโค้ดระดับ Machine Code แบบเรียลไทม์ แถมยังมี Virtual Threads ที่รองรับ Request ได้นับล้านพร้อมกันโดยไม่กินแรม",
                "tts_text": "สองคือ เพอร์ฟอร์มานซ์ ที่โหดขึ้นเรื่อยๆ เจวีเอ็ม ยุคใหม่มี เจไอที คอมไพเลอร์ ปรับแต่งโค้ดระดับ แมชชีน โค้ด แบบเรียลไทม์ แถมยังมี เวอร์ชวล เธรดส์ ที่รองรับ รีเควสต์ ได้นับล้านพร้อมกัน",
                "subtitle": "JVM ยุคใหม่มี JIT Compiler แรงระดับ Machine Code พร้อม Virtual Threads รับล้าน Request!",
                "show_subtitle": True,
                "motion": "drift_top_right",
                "transition": "fade",
                "motion_speed": "slow",
                "estimated_duration": 8.5
            },
            {
                "id": "scene-05-scale-and-maintainability",
                "image": "images/scene-05-scale-and-maintainability.png",
                "narration": "สามคือเรื่อง Scale และคน ระบบที่โค้ดเป็นล้านๆ บรรทัด คนเขียนเป็นร้อยคน ความเป็น Strongly Typed ของ Java ทำให้แก้โค้ดได้อย่างปลอดภัย Refactor ใหญ่แค่ไหนก็ไม่พังง่ายๆ",
                "tts_text": "สามคือเรื่อง สเกล และคน ระบบที่โค้ดเป็นล้านๆ บรรทัด คนเขียนเป็นร้อยคน ความเป็น สตรองลี ไทป์ ของ จาวา ทำให้แก้โค้ดได้อย่างปลอดภัย รีแฟกเตอร์ ใหญ่แค่ไหนก็ไม่พังง่ายๆ",
                "subtitle": "โค้ดนับล้านบรรทัด ทีมงานนับร้อยคน... Strongly Typed ทำให้ Refactor ปลอดภัยที่สุด",
                "show_subtitle": True,
                "motion": "pan_left_to_right_zoom_in",
                "transition": "fade",
                "motion_speed": "slow",
                "estimated_duration": 8.0
            },
            {
                "id": "scene-06-real-world-usage",
                "image": "images/scene-06-real-world-usage.png",
                "narration": "ระบบการเงินทั่วโลก ตลาดหุ้น Netflix หรือแม้แต่ Android ก็ขับเคลื่อนด้วย Java ทั้งนั้น มันไม่ใช่แค่ภาษาเขียนโปรแกรม... แต่มันคือโครงสร้างพื้นฐานของเศรษฐกิจดิจิทัล",
                "tts_text": "ระบบการเงินทั่วโลก ตลาดหุ้น เน็ตฟลิกซ์ หรือแม้แต่ แอนดรอยด์ ก็ขับเคลื่อนด้วย จาวา ทั้งนั้น มันไม่ใช่แค่ภาษาเขียนโปรแกรม... แต่มันคือโครงสร้างพื้นฐานของเศรษฐกิจดิจิทัล",
                "subtitle": "ระบบการเงิน ตลาดหุ้น Netflix และ Android... ล้วนขับเคลื่อนด้วย Java",
                "show_subtitle": True,
                "motion": "gentle_float",
                "transition": "fade",
                "motion_speed": "slow",
                "estimated_duration": 8.0
            },
            {
                "id": "scene-07-conclusion",
                "image": "images/scene-07-conclusion.png",
                "narration": "ดังนั้น ถ้าใครบอกคุณว่า Java กำลังจะตาย... บอกเค้าเลยครับว่า Java ไม่ได้กำลังจะตาย แต่มันกำลังรันโลกอยู่เบื้องหลังต่างหาก! แล้วคุณล่ะครับ ทุกวันนี้ยังใช้ Java ทำระบบอะไรกันอยู่บ้าง? คอมเมนต์คุยกันหน่อยครับ",
                "tts_text": "ดังนั้น ถ้าใครบอกคุณว่า จาวา กำลังจะตาย... บอกเค้าเลยครับว่า จาวา ไม่ได้กำลังจะตาย แต่มันกำลังรันโลกอยู่เบื้องหลังต่างหาก! แล้วคุณล่ะครับ ทุกวันนี้ยังใช้ จาวา ทำระบบอะไรกันอยู่บ้าง? คอมเมนต์คุยกันหน่อยครับ",
                "subtitle": "Java ไม่ได้กำลังจะตาย... แต่มันกำลังรันโลกอยู่เบื้องหลังต่างหาก!",
                "show_subtitle": True,
                "motion": "cinematic_push_in",
                "transition": "fade",
                "motion_speed": "slow",
                "estimated_duration": 8.5
            }
        ]
    }
    content = json.dumps(script_data, ensure_ascii=False, indent=2)
    (DIST_DIR / "script.json").write_text(content, encoding="utf-8")
    (ASSETS_DIR / "script.json").write_text(content, encoding="utf-8")
    print("Created script.json successfully!")

def create_video_metadata():
    metadata = {
        "title": "Java ทำไมยังไม่ตาย? ทำไมองค์กรใหญ่ยังใช้ Java กันเต็มไปหมด",
        "description": (
            "Java ทำไมยังไม่ตาย? ทำไมระบบธนาคาร ตลาดหุ้น Netflix และองค์กรระดับ Fortune 500 ถึงยังใช้ Java เป็นหัวใจหลัก?\n\n"
            "คลิปนี้พาไปเจาะลึก 3 เหตุผลแท้จริงของ Senior Backend Engineer:\n"
            "1. Ecosystem & Frameworks (Spring Boot ที่ครบวงจรที่สุด)\n"
            "2. High Performance JVM & Virtual Threads (Project Loom รองรับล้าน Request)\n"
            "3. Enterprise Scale & Strongly Typed Maintainability (Refactor โค้ดล้านบรรทัดได้มั่นใจ)\n\n"
            "#Java #Backend #SoftwareEngineer #Springboot #Programming #ThaiJavaZone #DevLife"
        ),
        "tags": [
            "Java",
            "Thai Java Zone",
            "Backend Development",
            "Spring Boot",
            "JVM",
            "Virtual Threads",
            "Software Architecture",
            "Enterprise Architecture",
            "Coding",
            "Programming"
        ],
        "category": "Science & Technology",
        "language": "th-TH"
    }
    content = json.dumps(metadata, ensure_ascii=False, indent=2)
    (DIST_DIR / "video-metadata.json").write_text(content, encoding="utf-8")
    (ASSETS_DIR / "video-metadata.json").write_text(content, encoding="utf-8")
    print("Created video-metadata.json successfully!")

def create_readme():
    readme_content = """# Thai Java Zone — Java ทำไมยังไม่ตาย?

แพ็กเกจวิดีโอแนวตั้ง (9:16) สำหรับ **Thai Java Zone** บนแพลตฟอร์ม AutoClip
อธิบายว่าทำไมภาษา Java และ JVM ถึงยังคงเป็นหัวใจหลักของระบบระดับโลกและ Enterprise Architecture ในปัจจุบัน

## ข้อมูลแพ็กเกจ (Package Info)
- **ช่อง (Channel)**: Thai Java Zone
- **หัวข้อ (Topic)**: Java ทำไมยังไม่ตาย? ทำไมองค์กรใหญ่ยังใช้ Java กันเต็มไปหมด
- **ความยาว (Duration)**: ประมาณ 54 วินาที (7 ซีน)
- **ความละเอียด (Resolution)**: 1080x1920 (9:16 Vertical Reel/Shorts/TikTok)
- **เสียงบรรยาย (Voice)**: Google Gemini TTS (Fenrir, th-TH)
- **อาร์ตไดเรกชัน (Visual Style Bible)**:
  - Clean modern software-engineering explainer
  - Realistic developer workspace, server infrastructure, 3D system architecture & JVM telemetry
  - Dark slate/charcoal tech background, soft cinematic studio lighting, subtle depth
  - ปราศจากตัวหนังสือ, watermark, logo, fake UI labels และปราศจาก cyberpunk/neon ตามกฎ start.md

## โครงสร้างไฟล์ใน ZIP Archive
```
thai-java-zone-why-java-alive.zip
├── script.json
├── video-metadata.json
└── images/
    ├── scene-01-hook.png
    ├── scene-02-stability.png
    ├── scene-03-enterprise-ecosystem.png
    ├── scene-04-modern-performance.png
    ├── scene-05-scale-and-maintainability.png
    ├── scene-06-real-world-usage.png
    └── scene-07-conclusion.png
```
*(หมายเหตุ: ไฟล์ README.md อยู่นอก ZIP ตามมาตรฐาน Package Contract เพื่อให้ผ่าน PackageService Validation)*
"""
    (DIST_DIR / "README.md").write_text(readme_content, encoding="utf-8")
    (ASSETS_DIR / "README.md").write_text(readme_content, encoding="utf-8")
    print("Created README.md successfully!")

def package_zip():
    if DIST_ZIP.exists():
        DIST_ZIP.unlink()

    with zipfile.ZipFile(DIST_ZIP, "w", zipfile.ZIP_DEFLATED) as zipf:
        zipf.write(DIST_DIR / "script.json", arcname="script.json")
        zipf.write(DIST_DIR / "video-metadata.json", arcname="video-metadata.json")
        for img in sorted((DIST_DIR / "images").glob("*.png")):
            zipf.write(img, arcname=f"images/{img.name}")

    print(f"Created ZIP: {DIST_ZIP} ({DIST_ZIP.stat().st_size} bytes)")

def validate_package():
    from app.services.package_service import PackageService
    pkg_service = PackageService(500 * 1024 * 1024)
    val_dir = BASE_DIR / "scratch" / "validation_test"
    shutil.rmtree(val_dir, ignore_errors=True)
    manifest, extracted_dir = pkg_service.extract_and_validate(DIST_ZIP, val_dir)
    print("Package validation passed successfully!")
    print(f"Validated {len(manifest.scenes)} scenes, all assets valid.")

if __name__ == "__main__":
    render_all_images()
    create_script_json()
    create_video_metadata()
    create_readme()
    package_zip()
    validate_package()
