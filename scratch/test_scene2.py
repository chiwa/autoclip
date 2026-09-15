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
    background: #06090e;
    overflow: hidden;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    position: relative;
  }

  /* Data center cold aisle perspective */
  .dc-corridor {
    position: absolute;
    top: 0; left: 0; width: 1080px; height: 1920px;
    background: radial-gradient(circle at 50% 35%, #0f1724 0%, #080d14 50%, #040609 100%);
  }

  /* Ceiling cable trays and LED strip runner lights */
  .ceiling-lights {
    position: absolute;
    top: 0; left: 0; width: 1080px; height: 250px;
    background: 
      linear-gradient(180deg, rgba(56, 189, 248, 0.08) 0%, transparent 100%),
      repeating-linear-gradient(90deg, transparent 0px, transparent 120px, rgba(255,255,255,0.03) 120px, rgba(255,255,255,0.03) 124px);
  }
  .overhead-light-bar {
    position: absolute;
    top: 30px; left: 50%; transform: translateX(-50%);
    width: 800px; height: 8px;
    background: #e0f2fe;
    border-radius: 4px;
    box-shadow: 0 0 30px rgba(56, 189, 248, 0.6), 0 0 80px rgba(56, 189, 248, 0.3);
  }

  /* Vanishing corridor lines in background */
  .perspective-lines {
    position: absolute;
    top: 100px; left: 0; width: 1080px; height: 1400px;
    opacity: 0.15;
    background-image: 
      linear-gradient(45deg, transparent 48%, rgba(56, 189, 248, 0.4) 50%, transparent 52%),
      linear-gradient(-45deg, transparent 48%, rgba(56, 189, 248, 0.4) 50%, transparent 52%);
    background-size: 1080px 1400px;
    mask-image: radial-gradient(circle at 50% 45%, black 20%, transparent 70%);
  }

  /* Main Enterprise 42U Server Rack (Hero Subject) */
  .server-rack-container {
    position: absolute;
    top: 140px; left: 50%;
    transform: translateX(-50%);
    width: 880px;
    height: 1450px;
    background: linear-gradient(180deg, #131a24 0%, #0c1118 100%);
    border-radius: 16px;
    border: 2px solid rgba(255, 255, 255, 0.1);
    box-shadow: 
      0 40px 100px rgba(0, 0, 0, 0.95),
      0 0 60px rgba(56, 189, 248, 0.1),
      inset 0 0 30px rgba(0,0,0,0.8);
    display: flex;
    padding: 16px 12px;
    gap: 12px;
    z-index: 10;
  }

  /* Rack mounting rails on sides */
  .rack-rail {
    width: 28px;
    height: 100%;
    background: repeating-linear-gradient(
      180deg,
      #1c2533 0px, #1c2533 12px,
      #0e141c 12px, #0e141c 24px,
      #090d13 24px, #090d13 36px
    );
    border-radius: 4px;
    border: 1px solid rgba(255, 255, 255, 0.05);
  }

  /* Server Bays Stack */
  .server-stack {
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 10px;
  }

  /* Server Chassis 2U / 4U */
  .chassis {
    width: 100%;
    background: linear-gradient(180deg, #17202d 0%, #101620 50%, #0d121a 100%);
    border-radius: 8px;
    border: 1px solid rgba(255, 255, 255, 0.07);
    box-shadow: 
      0 8px 16px rgba(0,0,0,0.6),
      inset 0 1px 1px rgba(255,255,255,0.1);
    display: flex;
    align-items: center;
    padding: 12px 18px;
    gap: 16px;
  }

  .chassis.h-1u { height: 75px; }
  .chassis.h-2u { height: 110px; }
  .chassis.h-4u { height: 180px; }

  /* Drive Bays Array */
  .drive-bay-group {
    display: flex;
    gap: 6px;
    flex: 2;
  }
  .drive-caddy {
    flex: 1;
    height: 50px;
    background: #090d13;
    border-radius: 4px;
    border: 1px solid rgba(255, 255, 255, 0.05);
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    padding: 5px;
    box-shadow: inset 0 2px 4px rgba(0,0,0,0.7);
  }
  .caddy-handle { height: 6px; background: #1f2a3a; border-radius: 2px; }
  .caddy-led {
    width: 6px; height: 6px; border-radius: 50%;
    background: #10b981;
    box-shadow: 0 0 6px #10b981;
  }
  .caddy-led.blue { background: #38bdf8; box-shadow: 0 0 6px #38bdf8; }
  .caddy-led.amber { background: #f59e0b; box-shadow: 0 0 6px #f59e0b; }

  /* Perforated Honeycomb Cooling Grille */
  .honeycomb-grille {
    flex: 2;
    height: 50px;
    background: 
      radial-gradient(circle, #080c12 25%, transparent 26%) 0 0,
      radial-gradient(circle, #080c12 25%, transparent 26%) 4px 4px;
    background-size: 8px 8px;
    background-color: #172230;
    border-radius: 4px;
    border: 1px solid rgba(255, 255, 255, 0.04);
  }

  /* Status Indicator Bar */
  .status-cluster {
    display: flex;
    flex-direction: column;
    gap: 6px;
    width: 90px;
    background: #0a0e15;
    padding: 8px;
    border-radius: 4px;
    border: 1px solid rgba(255,255,255,0.04);
  }
  .status-line { display: flex; align-items: center; justify-content: space-between; }
  .led-label { width: 45px; height: 5px; background: #334155; border-radius: 2px; }
  .pulse-led {
    width: 7px; height: 7px; border-radius: 50%;
    background: #10b981;
    box-shadow: 0 0 8px #10b981;
  }

  /* High-Speed Switch with SFP+ Ports and Fiber Optic Loom */
  .switch-unit {
    width: 100%;
    height: 95px;
    background: linear-gradient(180deg, #1b2432 0%, #111822 100%);
    border-radius: 8px;
    border: 1px solid rgba(255, 255, 255, 0.08);
    display: flex;
    align-items: center;
    padding: 12px 18px;
    gap: 20px;
  }
  .port-matrix {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    flex: 3;
  }
  .sfp-port {
    width: 22px; height: 16px;
    background: #090d13;
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 2px;
    position: relative;
    display: flex; align-items: center; justify-content: center;
  }
  .fiber-plug {
    width: 14px; height: 8px;
    border-radius: 2px;
  }
  .fiber-plug.aqua { background: #06b6d4; box-shadow: 0 0 6px #06b6d4; }
  .fiber-plug.orange { background: #f97316; box-shadow: 0 0 6px #f97316; }
  .fiber-plug.yellow { background: #eab308; box-shadow: 0 0 6px #eab308; }

  /* Structured Vertical Fiber Cable Bundles */
  .cable-bundle {
    position: absolute;
    top: 200px; right: 60px;
    width: 40px; height: 1200px;
    display: flex;
    gap: 4px;
    opacity: 0.85;
  }
  .cable-strand {
    width: 6px; height: 100%;
    border-radius: 3px;
  }
  .c-aqua { background: linear-gradient(180deg, #0891b2 0%, #06b6d4 50%, #0891b2 100%); box-shadow: 0 0 8px rgba(6,182,212,0.4); }
  .c-orange { background: linear-gradient(180deg, #ea580c 0%, #f97316 50%, #ea580c 100%); box-shadow: 0 0 8px rgba(249,115,22,0.4); }
  .c-yellow { background: linear-gradient(180deg, #ca8a04 0%, #eab308 50%, #ca8a04 100%); box-shadow: 0 0 8px rgba(234,179,8,0.4); }

  /* Raised Floor Tiles at Bottom */
  .raised-floor {
    position: absolute;
    top: 1540px; left: 0; width: 1080px; height: 380px;
    background: linear-gradient(180deg, #111722 0%, #0c1018 40%, #06090e 100%);
    border-top: 2px solid rgba(255, 255, 255, 0.08);
    box-shadow: 
      inset 0 30px 60px rgba(56, 189, 248, 0.05),
      0 -20px 50px rgba(0,0,0,0.9);
    background-image: 
      linear-gradient(rgba(255,255,255,0.03) 1px, transparent 1px),
      linear-gradient(90deg, rgba(255,255,255,0.03) 1px, transparent 1px);
    background-size: 180px 120px;
  }
  .floor-reflection {
    position: absolute;
    top: 0; left: 50%; transform: translateX(-50%);
    width: 800px; height: 140px;
    background: radial-gradient(ellipse at 50% 0%, rgba(56, 189, 248, 0.12) 0%, rgba(16, 185, 129, 0.08) 35%, transparent 70%);
    pointer-events: none;
  }

  /* Subtitle safe gradient */
  .safe-area-bottom {
    position: absolute;
    bottom: 0; left: 0; width: 1080px; height: 360px;
    background: linear-gradient(180deg, transparent 0%, rgba(4, 6, 9, 0.65) 100%);
    pointer-events: none;
  }
</style>
</head>
<body>
  <div class="dc-corridor"></div>
  <div class="ceiling-lights"></div>
  <div class="overhead-light-bar"></div>
  <div class="perspective-lines"></div>

  <!-- Server Rack -->
  <div class="server-rack-container">
    <div class="rack-rail"></div>

    <div class="server-stack">
      <!-- Top Switch 1 -->
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

      <!-- Server 1 (2U Storage/Compute) -->
      <div class="chassis h-2u">
        <div class="drive-bay-group">
          <div class="drive-caddy"><div class="caddy-handle"></div><div class="caddy-led blue"></div></div>
          <div class="drive-caddy"><div class="caddy-handle"></div><div class="caddy-led blue"></div></div>
          <div class="drive-caddy"><div class="caddy-handle"></div><div class="caddy-led blue"></div></div>
          <div class="drive-caddy"><div class="caddy-handle"></div><div class="caddy-led blue"></div></div>
          <div class="drive-caddy"><div class="caddy-handle"></div><div class="caddy-led blue"></div></div>
          <div class="drive-caddy"><div class="caddy-handle"></div><div class="caddy-led amber"></div></div>
        </div>
        <div class="honeycomb-grille"></div>
        <div class="status-cluster">
          <div class="status-line"><div class="led-label"></div><div class="pulse-led"></div></div>
          <div class="status-line"><div class="led-label"></div><div class="pulse-led"></div></div>
        </div>
      </div>

      <!-- Server 2 (4U Enterprise Core) -->
      <div class="chassis h-4u">
        <div class="drive-bay-group">
          <div class="drive-caddy"><div class="caddy-handle"></div><div class="caddy-led"></div></div>
          <div class="drive-caddy"><div class="caddy-handle"></div><div class="caddy-led"></div></div>
          <div class="drive-caddy"><div class="caddy-handle"></div><div class="caddy-led"></div></div>
          <div class="drive-caddy"><div class="caddy-handle"></div><div class="caddy-led"></div></div>
          <div class="drive-caddy"><div class="caddy-handle"></div><div class="caddy-led"></div></div>
          <div class="drive-caddy"><div class="caddy-handle"></div><div class="caddy-led blue"></div></div>
        </div>
        <div class="honeycomb-grille" style="height:120px"></div>
        <div class="status-cluster">
          <div class="status-line"><div class="led-label"></div><div class="pulse-led"></div></div>
          <div class="status-line"><div class="led-label"></div><div class="pulse-led"></div></div>
          <div class="status-line"><div class="led-label"></div><div class="pulse-led"></div></div>
        </div>
      </div>

      <!-- Server 3 (2U Backend Node) -->
      <div class="chassis h-2u">
        <div class="drive-bay-group">
          <div class="drive-caddy"><div class="caddy-handle"></div><div class="caddy-led"></div></div>
          <div class="drive-caddy"><div class="caddy-handle"></div><div class="caddy-led"></div></div>
          <div class="drive-caddy"><div class="caddy-handle"></div><div class="caddy-led"></div></div>
          <div class="drive-caddy"><div class="caddy-handle"></div><div class="caddy-led"></div></div>
          <div class="drive-caddy"><div class="caddy-handle"></div><div class="caddy-led"></div></div>
          <div class="drive-caddy"><div class="caddy-handle"></div><div class="caddy-led"></div></div>
        </div>
        <div class="honeycomb-grille"></div>
        <div class="status-cluster">
          <div class="status-line"><div class="led-label"></div><div class="pulse-led"></div></div>
          <div class="status-line"><div class="led-label"></div><div class="pulse-led"></div></div>
        </div>
      </div>

      <!-- Server 4 (2U Database Node) -->
      <div class="chassis h-2u">
        <div class="drive-bay-group">
          <div class="drive-caddy"><div class="caddy-handle"></div><div class="caddy-led blue"></div></div>
          <div class="drive-caddy"><div class="caddy-handle"></div><div class="caddy-led blue"></div></div>
          <div class="drive-caddy"><div class="caddy-handle"></div><div class="caddy-led blue"></div></div>
          <div class="drive-caddy"><div class="caddy-handle"></div><div class="caddy-led blue"></div></div>
          <div class="drive-caddy"><div class="caddy-handle"></div><div class="caddy-led blue"></div></div>
          <div class="drive-caddy"><div class="caddy-handle"></div><div class="caddy-led blue"></div></div>
        </div>
        <div class="honeycomb-grille"></div>
        <div class="status-cluster">
          <div class="status-line"><div class="led-label"></div><div class="pulse-led"></div></div>
          <div class="status-line"><div class="led-label"></div><div class="pulse-led"></div></div>
        </div>
      </div>

      <!-- Server 5 (4U Persistence Engine) -->
      <div class="chassis h-4u">
        <div class="drive-bay-group">
          <div class="drive-caddy"><div class="caddy-handle"></div><div class="caddy-led"></div></div>
          <div class="drive-caddy"><div class="caddy-handle"></div><div class="caddy-led"></div></div>
          <div class="drive-caddy"><div class="caddy-handle"></div><div class="caddy-led"></div></div>
          <div class="drive-caddy"><div class="caddy-handle"></div><div class="caddy-led"></div></div>
          <div class="drive-caddy"><div class="caddy-handle"></div><div class="caddy-led"></div></div>
          <div class="drive-caddy"><div class="caddy-handle"></div><div class="caddy-led amber"></div></div>
        </div>
        <div class="honeycomb-grille" style="height:120px"></div>
        <div class="status-cluster">
          <div class="status-line"><div class="led-label"></div><div class="pulse-led"></div></div>
          <div class="status-line"><div class="led-label"></div><div class="pulse-led"></div></div>
          <div class="status-line"><div class="led-label"></div><div class="pulse-led"></div></div>
        </div>
      </div>

      <!-- Server 6 (2U Failover Replica) -->
      <div class="chassis h-2u">
        <div class="drive-bay-group">
          <div class="drive-caddy"><div class="caddy-handle"></div><div class="caddy-led"></div></div>
          <div class="drive-caddy"><div class="caddy-handle"></div><div class="caddy-led"></div></div>
          <div class="drive-caddy"><div class="caddy-handle"></div><div class="caddy-led"></div></div>
          <div class="drive-caddy"><div class="caddy-handle"></div><div class="caddy-led"></div></div>
          <div class="drive-caddy"><div class="caddy-handle"></div><div class="caddy-led"></div></div>
          <div class="drive-caddy"><div class="caddy-handle"></div><div class="caddy-led"></div></div>
        </div>
        <div class="honeycomb-grille"></div>
        <div class="status-cluster">
          <div class="status-line"><div class="led-label"></div><div class="pulse-led"></div></div>
          <div class="status-line"><div class="led-label"></div><div class="pulse-led"></div></div>
        </div>
      </div>
    </div>

    <div class="rack-rail"></div>
  </div>

  <!-- Cable Loom -->
  <div class="cable-bundle">
    <div class="cable-strand c-aqua"></div>
    <div class="cable-strand c-orange"></div>
    <div class="cable-strand c-yellow"></div>
  </div>

  <!-- Raised Floor -->
  <div class="raised-floor">
    <div class="floor-reflection"></div>
  </div>

  <div class="safe-area-bottom"></div>
</body>
</html>
"""

Path("scratch/scene2_test.html").write_text(html, encoding="utf-8")
subprocess.run([
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "--headless",
    "--screenshot=scratch/scene2_test.png",
    "--window-size=1080,1920",
    "--hide-scrollbars",
    f"file://{Path('scratch/scene2_test.html').resolve()}"
], check=True)
print("Rendered Scene 2 test!")
