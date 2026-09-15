import subprocess
import shutil
import zipfile
from pathlib import Path

CHROME_PATH = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
OUT_DIR = Path("scratch/tjz_masterpiece")
OUT_DIR.mkdir(parents=True, exist_ok=True)

def render(html_content, filename):
    out_path = OUT_DIR / filename
    temp_html = OUT_DIR / f"{filename}.html"
    temp_html.write_text(html_content, encoding="utf-8")
    cmd = [
        CHROME_PATH,
        "--headless=new",
        "--disable-gpu",
        "--hide-scrollbars",
        "--window-size=1080,1920",
        f"--screenshot={out_path.resolve()}",
        str(temp_html.resolve())
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(f"[OK] Rendered {filename} ({out_path.stat().st_size:,} bytes)")

BASE_CSS = """
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    width: 1080px; height: 1920px; background: #070a12;
    overflow: hidden; font-family: "JetBrains Mono", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, monospace;
    color: #f1f5f9; position: relative;
  }
  .bg-glow {
    position: absolute; inset: 0;
    background: 
      radial-gradient(circle at 540px 320px, rgba(30, 58, 138, 0.28) 0%, transparent 65%),
      radial-gradient(circle at 180px 850px, rgba(14, 165, 233, 0.16) 0%, transparent 55%),
      radial-gradient(circle at 900px 1050px, rgba(16, 185, 129, 0.12) 0%, transparent 55%),
      radial-gradient(circle at 540px 1450px, rgba(30, 58, 138, 0.22) 0%, transparent 60%),
      linear-gradient(180deg, #050811 0%, #0c1322 50%, #04060b 100%);
    z-index: 1;
  }
  .grid-pattern {
    position: absolute; inset: 0;
    background-image: 
      linear-gradient(to right, rgba(255, 255, 255, 0.022) 1px, transparent 1px),
      linear-gradient(to bottom, rgba(255, 255, 255, 0.022) 1px, transparent 1px);
    background-size: 36px 36px; z-index: 2;
  }
  .subtitle-vignette {
    position: absolute; bottom: 0; left: 0; width: 1080px; height: 320px;
    background: linear-gradient(180deg, transparent 0%, rgba(5, 8, 15, 0.75) 45%, rgba(3, 5, 10, 0.98) 100%);
    pointer-events: none; z-index: 30;
  }
"""

# ==============================================================================
# SCENE 1: HOOK — Senior Engineer Cockpit & Java 21 Code
# ==============================================================================
html_scene1 = f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><style>
{BASE_CSS}
  .monitor-frame {{
    position: absolute; top: 35px; left: 35px; width: 1010px; height: 1220px;
    background: #0f172a; border-radius: 18px;
    box-shadow: 0 35px 90px rgba(0,0,0,0.9), 0 0 0 1px rgba(255,255,255,0.08), 0 0 50px rgba(56, 189, 248, 0.14);
    display: flex; flex-direction: column; overflow: hidden; z-index: 10;
  }}
  .ide-header {{
    height: 46px; background: #0b1120; border-bottom: 1px solid rgba(255,255,255,0.08);
    display: flex; align-items: center; padding: 0 20px; gap: 14px;
  }}
  .window-dots {{ display: flex; gap: 8px; }}
  .dot {{ width: 12px; height: 12px; border-radius: 50%; }}
  .dot-red {{ background: #ef4444; }} .dot-yellow {{ background: #f59e0b; }} .dot-green {{ background: #10b981; }}
  .ide-tabs {{ display: flex; margin-left: 20px; gap: 4px; font-size: 13px; font-weight: 500; }}
  .tab {{ padding: 8px 18px; border-radius: 6px 6px 0 0; color: #94a3b8; background: transparent; display: flex; align-items: center; gap: 8px; }}
  .tab.active {{ background: #1e293b; color: #38bdf8; border-top: 2px solid #38bdf8; }}
  .java-badge {{ color: #f97316; font-weight: 700; }}
  .ide-body {{ flex: 1; display: flex; background: #0a0f1d; overflow: hidden; }}
  .ide-sidebar {{ width: 220px; background: #0c1322; border-right: 1px solid rgba(255,255,255,0.06); padding: 16px 14px; font-size: 11.5px; color: #64748b; }}
  .project-name {{ font-weight: 700; color: #cbd5e1; margin-bottom: 10px; text-transform: uppercase; letter-spacing: 0.5px; font-size: 11px; }}
  .file-tree-item {{ padding: 4px 6px; border-radius: 4px; display: flex; align-items: center; gap: 6px; color: #94a3b8; margin-bottom: 2px; }}
  .file-tree-item.active {{ background: rgba(56, 189, 248, 0.12); color: #38bdf8; font-weight: 600; }}
  .editor-column {{ flex: 1; display: flex; flex-direction: column; overflow: hidden; }}
  .code-editor {{ flex: 1; padding: 14px 18px; font-size: 12.5px; line-height: 1.65; color: #e2e8f0; overflow: hidden; }}
  .line {{ display: flex; gap: 12px; }}
  .line-num {{ color: #334155; width: 24px; text-align: right; user-select: none; font-size: 11.5px; }}
  .kw {{ color: #f43f5e; font-weight: 600; }}
  .type {{ color: #38bdf8; font-weight: 600; }}
  .anno {{ color: #eab308; }}
  .fn {{ color: #60a5fa; }}
  .str {{ color: #34d399; }}
  .com {{ color: #475569; font-style: italic; }}
  .var {{ color: #f1f5f9; }}
  .terminal-panel {{
    height: 380px; background: #060913; border-top: 1px solid rgba(255,255,255,0.08);
    padding: 12px 18px; font-size: 11.5px; line-height: 1.6; color: #94a3b8;
  }}
  .term-header {{ display: flex; justify-content: space-between; color: #64748b; font-size: 10.5px; text-transform: uppercase; margin-bottom: 6px; font-weight: 700; }}
  .spring-banner {{ color: #10b981; font-weight: 700; font-family: monospace; white-space: pre; line-height: 1.15; margin-bottom: 6px; font-size: 11px; }}
  .ide-telemetry {{ width: 250px; background: #090e1a; border-left: 1px solid rgba(255,255,255,0.06); padding: 14px 12px; display: flex; flex-direction: column; gap: 10px; }}
  .metric-card {{ background: #0f172a; border: 1px solid rgba(255,255,255,0.06); border-radius: 8px; padding: 10px; }}
  .metric-title {{ font-size: 10px; color: #64748b; text-transform: uppercase; font-weight: 700; letter-spacing: 0.5px; margin-bottom: 3px; }}
  .metric-val {{ font-size: 19px; font-weight: 700; color: #38bdf8; }}
  .metric-sub {{ font-size: 10px; color: #10b981; margin-top: 2px; }}

  .monitor-stand {{ position: absolute; top: 1255px; left: 490px; width: 100px; height: 80px; background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%); border-radius: 4px; z-index: 5; }}
  .monitor-base {{ position: absolute; top: 1320px; left: 350px; width: 380px; height: 18px; background: #1e293b; border-radius: 9px; border: 1px solid rgba(255,255,255,0.08); z-index: 6; }}
  .desk-surface {{ position: absolute; top: 1300px; left: 0; width: 1080px; height: 620px; background: linear-gradient(180deg, #090d16 0%, #060911 50%, #020306 100%); border-top: 1px solid rgba(255,255,255,0.05); z-index: 4; }}
  .desk-mat {{ position: absolute; top: 1340px; left: 30px; width: 1020px; height: 490px; background: #0d1322; border-radius: 16px; border: 1px solid rgba(255,255,255,0.04); box-shadow: inset 0 2px 10px rgba(0,0,0,0.6), 0 20px 50px rgba(0,0,0,0.8); z-index: 7; }}
  .keyboard-frame {{ position: absolute; top: 1380px; left: 100px; width: 640px; height: 210px; background: #111827; border-radius: 12px; padding: 14px; box-shadow: 0 15px 35px rgba(0,0,0,0.8), 0 0 0 1px rgba(255,255,255,0.05); z-index: 8; }}
  .key-rows {{ display: flex; flex-direction: column; gap: 6px; }}
  .key-row {{ display: flex; gap: 6px; }}
  .key {{ height: 28px; background: #1e293b; border-radius: 4px; box-shadow: 0 3px 0 #0f172a; flex: 1; border: 1px solid rgba(255,255,255,0.03); }}
  .key.space {{ flex: 6; background: #243247; }} .key.accent {{ background: #0284c7; box-shadow: 0 3px 0 #0369a1; }} .key.mod {{ flex: 1.5; background: #162032; }}
  .wrist-rest {{ position: absolute; top: 1605px; left: 100px; width: 640px; height: 48px; background: #0b101c; border-radius: 8px; border: 1px solid rgba(255,255,255,0.03); z-index: 8; }}
  .mouse {{ position: absolute; top: 1420px; left: 810px; width: 85px; height: 145px; background: radial-gradient(circle at 40px 40px, #1e293b 0%, #0f172a 100%); border-radius: 42px; box-shadow: 0 15px 30px rgba(0,0,0,0.8); z-index: 8; }}
  .mouse-wheel {{ position: absolute; top: 25px; left: 38px; width: 8px; height: 24px; background: #38bdf8; border-radius: 4px; }}
  .coffee-mug {{ position: absolute; top: 1380px; left: 920px; width: 70px; height: 70px; border-radius: 50%; background: radial-gradient(circle, #2d1810 40%, #522d1e 75%, #1e293b 100%); box-shadow: 0 10px 20px rgba(0,0,0,0.7), 0 0 0 3px #334155; z-index: 8; }}
</style></head>
<body>
  <div class="bg-glow"></div><div class="grid-pattern"></div>
  <div class="monitor-frame">
    <div class="ide-header">
      <div class="window-dots"><div class="dot dot-red"></div><div class="dot dot-yellow"></div><div class="dot dot-green"></div></div>
      <div class="ide-tabs">
        <div class="tab active"><span class="java-badge">J</span> CoreBankingEngine.java</div>
        <div class="tab">TransactionPipeline.java</div>
        <div class="tab">VirtualThreadCluster.java</div>
      </div>
    </div>
    <div class="ide-body">
      <div class="ide-sidebar">
        <div class="project-name">enterprise-banking</div>
        <div class="file-tree-item">src/main/java</div>
        <div class="file-tree-item">├── domain</div>
        <div class="file-tree-item active">│   ├── CoreBankingEngine.java</div>
        <div class="file-tree-item">│   └── AccountAggregate.java</div>
        <div class="file-tree-item">├── infrastructure</div>
        <div class="file-tree-item">│   ├── KafkaEventStream.java</div>
        <div class="file-tree-item">│   └── ZGCMemoryPolicy.java</div>
        <div class="file-tree-item">└── pom.xml</div>
      </div>
      <div class="editor-column">
        <div class="code-editor">
          <div class="line"><span class="line-num">1</span><span><span class="kw">package</span> <span class="var">com.enterprise.banking.core;</span></span></div>
          <div class="line"><span class="line-num">2</span><span></span></div>
          <div class="line"><span class="line-num">3</span><span><span class="anno">@Service</span></span></div>
          <div class="line"><span class="line-num">4</span><span><span class="anno">@RequiredArgsConstructor</span></span></div>
          <div class="line"><span class="line-num">5</span><span><span class="kw">public class</span> <span class="type">CoreBankingEngine</span> {{</span></div>
          <div class="line"><span class="line-num">6</span><span>&nbsp;&nbsp;<span class="kw">private final</span> <span class="type">TransactionLedger</span> <span class="var">ledger;</span></span></div>
          <div class="line"><span class="line-num">7</span><span>&nbsp;&nbsp;<span class="kw">private final</span> <span class="type">EventPublisher</span> <span class="var">eventBus;</span></span></div>
          <div class="line"><span class="line-num">8</span><span></span></div>
          <div class="line"><span class="line-num">9</span><span>&nbsp;&nbsp;<span class="anno">@Transactional</span>(<span class="var">isolation</span> = <span class="type">SERIALIZABLE</span>)</span></div>
          <div class="line"><span class="line-num">10</span><span>&nbsp;&nbsp;<span class="kw">public</span> <span class="type">PaymentReceipt</span> <span class="fn">processTransfer</span>(<span class="type">TransferRequest</span> <span class="var">req</span>) {{</span></div>
          <div class="line"><span class="line-num">11</span><span>&nbsp;&nbsp;&nbsp;&nbsp;<span class="kw">try</span> (<span class="kw">var</span> <span class="var">scope</span> = <span class="kw">new</span> <span class="type">StructuredTaskScope</span>.<span class="type">ShutdownOnFailure</span>()) {{</span></div>
          <div class="line"><span class="line-num">12</span><span>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="kw">var</span> <span class="var">auth</span> = <span class="var">scope</span>.<span class="fn">fork</span>(() -&gt; <span class="fn">verifyAccount</span>(<span class="var">req</span>.<span class="fn">from</span>()));</span></div>
          <div class="line"><span class="line-num">13</span><span>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="kw">var</span> <span class="var">risk</span> = <span class="var">scope</span>.<span class="fn">fork</span>(() -&gt; <span class="fn">evaluateRisk</span>(<span class="var">req</span>));</span></div>
          <div class="line"><span class="line-num">14</span><span>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="var">scope</span>.<span class="fn">join</span>().<span class="fn">throwIfFailed</span>();</span></div>
          <div class="line"><span class="line-num">15</span><span></span></div>
          <div class="line"><span class="line-num">16</span><span>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="kw">if</span> (<span class="var">risk</span>.<span class="fn">get</span>().<span class="fn">isApproved</span>() &amp;&amp; <span class="var">auth</span>.<span class="fn">get</span>()) {{</span></div>
          <div class="line"><span class="line-num">17</span><span>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="type">LedgerEntry</span> <span class="var">entry</span> = <span class="var">ledger</span>.<span class="fn">commit</span>(<span class="var">req</span>.<span class="fn">amount</span>());</span></div>
          <div class="line"><span class="line-num">18</span><span>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="var">eventBus</span>.<span class="fn">publish</span>(<span class="kw">new</span> <span class="type">TransferCompletedEvent</span>(<span class="var">entry</span>));</span></div>
          <div class="line"><span class="line-num">19</span><span>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="kw">return</span> <span class="type">PaymentReceipt</span>.<span class="fn">success</span>(<span class="var">entry</span>.<span class="fn">id</span>());</span></div>
          <div class="line"><span class="line-num">20</span><span>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;}}</span></div>
          <div class="line"><span class="line-num">21</span><span>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="kw">return</span> <span class="type">PaymentReceipt</span>.<span class="fn">declined</span>(<span class="str">"RISK_REJECTED"</span>);</span></div>
          <div class="line"><span class="line-num">22</span><span>&nbsp;&nbsp;&nbsp;&nbsp;}}</span></div>
          <div class="line"><span class="line-num">23</span><span>&nbsp;&nbsp;}}</span></div>
          <div class="line"><span class="line-num">24</span><span>&nbsp;&nbsp;<span class="kw">private</span> <span class="type">boolean</span> <span class="fn">verifyAccount</span>(<span class="type">AccountId</span> <span class="var">id</span>) {{</span></div>
          <div class="line"><span class="line-num">25</span><span>&nbsp;&nbsp;&nbsp;&nbsp;<span class="kw">return</span> <span class="var">ledger</span>.<span class="fn">findActiveAccount</span>(<span class="var">id</span>).<span class="fn">filter</span>(<span class="type">Account</span>::<span class="fn">isNotLocked</span>).<span class="fn">isPresent</span>();</span></div>
          <div class="line"><span class="line-num">26</span><span>&nbsp;&nbsp;}}</span></div>
          <div class="line"><span class="line-num">27</span><span>}}</span></div>
        </div>
        <div class="terminal-panel">
          <div class="term-header"><span>Terminal: Spring Boot Runner</span><span>JVM 21.0.2 LTS</span></div>
          <div class="spring-banner">  .   ____          _            __ _ _
 /\\ / ___'_ __ _ _(_)_ __  __ _ \ \ \ \
( ( )\___ | '_ | '_| | '_ \/ _` | \ \ \ \
 \\/  ___)| |_)| | | | | || (_| |  ) ) ) )</div>
          <div><span style="color:#10b981;">[INFO]</span> Started CoreBankingApplication in 1.412 seconds (process running for 1.89)</div>
          <div><span style="color:#38bdf8;">[INFO]</span> Netty WebServer initialized on port 8080 (HTTP/2.0 TLSv1.3)</div>
          <div><span style="color:#f59e0b;">[INFO]</span> VirtualThreadExecutor: 1,000,000 carrier pool initialized</div>
          <div><span style="color:#10b981;">[INFO]</span> Kafka Consumer Group 'banking-tx-v1' rebalance complete (32 partitions)</div>
          <div><span style="color:#10b981;">[READY]</span> Application ready for traffic - zero pause Generational ZGC active</div>
        </div>
      </div>
      <div class="ide-telemetry">
        <div class="metric-card"><div class="metric-title">JVM RUNTIME</div><div class="metric-val">JDK 21 LTS</div><div class="metric-sub">● HotSpot 64-Bit Server</div></div>
        <div class="metric-card"><div class="metric-title">VIRTUAL THREADS</div><div class="metric-val">1,240,000</div><div class="metric-sub">▲ 0.04% CPU overhead</div></div>
        <div class="metric-card"><div class="metric-title">THROUGHPUT</div><div class="metric-val">485,200/s</div><div class="metric-sub">● p99 latency 1.8ms</div></div>
        <div class="metric-card"><div class="metric-title">GC PAUSE (ZGC)</div><div class="metric-val">&lt; 0.42 ms</div><div class="metric-sub">● Sub-millisecond target</div></div>
        <div class="metric-card"><div class="metric-title">HEAP FOOTPRINT</div><div class="metric-val">18.4 / 64 GB</div><div class="metric-sub">● Colored Pointers Active</div></div>
        <div class="metric-card"><div class="metric-title">JIT OPTIMIZATION</div><div class="metric-val">C2 Tiered</div><div class="metric-sub">● AVX-512 SIMD Enabled</div></div>
      </div>
    </div>
  </div>
  <div class="monitor-stand"></div><div class="monitor-base"></div><div class="desk-surface"></div><div class="desk-mat"></div>
  <div class="keyboard-frame">
    <div class="key-rows">
      <div class="key-row"><div class="key"></div><div class="key"></div><div class="key"></div><div class="key"></div><div class="key"></div><div class="key"></div><div class="key"></div><div class="key"></div><div class="key"></div><div class="key"></div><div class="key"></div><div class="key"></div><div class="key mod"></div></div>
      <div class="key-row"><div class="key mod"></div><div class="key"></div><div class="key"></div><div class="key"></div><div class="key"></div><div class="key"></div><div class="key"></div><div class="key"></div><div class="key"></div><div class="key"></div><div class="key"></div><div class="key"></div><div class="key mod"></div></div>
      <div class="key-row"><div class="key mod"></div><div class="key"></div><div class="key"></div><div class="key"></div><div class="key"></div><div class="key"></div><div class="key"></div><div class="key"></div><div class="key"></div><div class="key"></div><div class="key"></div><div class="key accent"></div></div>
      <div class="key-row"><div class="key mod"></div><div class="key"></div><div class="key"></div><div class="key"></div><div class="key"></div><div class="key"></div><div class="key"></div><div class="key"></div><div class="key"></div><div class="key"></div><div class="key mod"></div></div>
      <div class="key-row"><div class="key mod"></div><div class="key mod"></div><div class="key mod"></div><div class="key space"></div><div class="key mod"></div><div class="key mod"></div><div class="key mod"></div></div>
    </div>
  </div>
  <div class="wrist-rest"></div><div class="mouse"><div class="mouse-wheel"></div></div><div class="coffee-mug"></div>
  <div class="subtitle-vignette"></div>
</body></html>
"""
render(html_scene1, "scene-01-hook.png")

# Scene 2 from scratch/test_full_rack.html
with open("scratch/test_full_rack.html", "r", encoding="utf-8") as f:
    html_scene2 = f.read()
render(html_scene2, "scene-02-stability.png")

# ==============================================================================
# SCENE 3: ECOSYSTEM — Spring Boot, Kafka, Enterprise Stack (Explicit Height 280px per tier)
# ==============================================================================
html_scene3 = f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><style>
{BASE_CSS}
  .arch-canvas {{
    position: absolute; top: 35px; left: 35px; width: 1010px; height: 1580px;
    display: flex; flex-direction: column; justify-content: space-between; z-index: 10;
  }}
  .tier-card {{
    background: #0d1527; border: 1px solid rgba(255,255,255,0.08); border-radius: 12px;
    padding: 16px 20px; box-shadow: 0 15px 35px rgba(0,0,0,0.6); display: flex; flex-direction: column; justify-content: space-between;
    height: 275px;
  }}
  .tier-header {{ display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid rgba(255,255,255,0.06); padding-bottom: 8px; }}
  .tier-title {{ font-size: 13px; font-weight: 700; color: #38bdf8; letter-spacing: 0.5px; text-transform: uppercase; }}
  .tier-badge {{ font-size: 11px; color: #10b981; font-weight: 600; background: rgba(16,185,129,0.12); border: 1px solid rgba(16,185,129,0.25); padding: 3px 10px; border-radius: 6px; }}
  
  .nodes-grid {{ display: grid; gap: 10px; }}
  .grid-4 {{ grid-template-columns: repeat(4, 1fr); }}
  .grid-3 {{ grid-template-columns: repeat(3, 1fr); }}

  .node-box {{
    background: #111a2e; border: 1px solid rgba(255,255,255,0.06); border-radius: 8px;
    padding: 12px 14px; display: flex; flex-direction: column; gap: 4px;
  }}
  .node-box.highlight {{ border-color: rgba(56, 189, 248, 0.4); background: #13223f; }}
  .node-name {{ font-size: 12.5px; font-weight: 700; color: #f8fafc; }}
  .node-desc {{ font-size: 11px; color: #94a3b8; line-height: 1.35; }}
  .node-tech {{ font-size: 10px; color: #38bdf8; font-weight: 600; text-transform: uppercase; }}

  .tier-footer {{
    background: #0a0f1d; border-radius: 6px; padding: 8px 14px; display: flex; justify-content: space-between;
    font-size: 11px; color: #94a3b8; border: 1px solid rgba(255,255,255,0.04);
  }}

  .conduit-bar {{
    height: 16px; display: flex; align-items: center; justify-content: center; gap: 12px;
  }}
  .conduit-line {{ flex: 1; height: 2px; background: linear-gradient(90deg, transparent, rgba(56, 189, 248, 0.6), transparent); }}
  .conduit-label {{ font-size: 9.5px; color: #64748b; text-transform: uppercase; letter-spacing: 1px; font-weight: 700; }}
</style></head>
<body>
  <div class="bg-glow"></div><div class="grid-pattern"></div>
  <div class="arch-canvas">
    <!-- Tier 1: Client Ingress & Gateway -->
    <div class="tier-card">
      <div class="tier-header"><div class="tier-title">TIER 1: TRAFFIC INGRESS &amp; API GATEWAY</div><div class="tier-badge">SPRING CLOUD GATEWAY</div></div>
      <div class="nodes-grid grid-3">
        <div class="node-box"><div class="node-name">Rate Limiter &amp; WAF</div><div class="node-desc">Distributed Token Bucket / Redis Cluster</div><div class="node-tech">Reactive Non-Blocking Filter</div></div>
        <div class="node-box highlight"><div class="node-name">OAuth2 / OIDC Security</div><div class="node-desc">Spring Security 6.2 / Keycloak</div><div class="node-tech">Stateless JWT Signature Verification</div></div>
        <div class="node-box"><div class="node-name">Global Load Balancer</div><div class="node-desc">Envoy / Netflix Ribbon Mesh</div><div class="node-tech">Weighted Round Robin &amp; Canary</div></div>
      </div>
      <div class="tier-footer">
        <span>● Active Ingress Conduits: <strong>100GbE Spine-Leaf</strong></span>
        <span>● SSL Offloading: <strong>TLSv1.3 Hardware Accelerated</strong></span>
        <span style="color:#10b981;">● Status: <strong>0 Dropped Packets</strong></span>
      </div>
    </div>

    <div class="conduit-bar"><div class="conduit-line"></div><div class="conduit-label">High-Speed RPC / gRPC Netty Pipeline</div><div class="conduit-line"></div></div>

    <!-- Tier 2: Microservices Layer -->
    <div class="tier-card">
      <div class="tier-header"><div class="tier-title">TIER 2: SPRING BOOT MICROSERVICES CLUSTER</div><div class="tier-badge">JAVA 21 LTS RUNTIME</div></div>
      <div class="nodes-grid grid-4">
        <div class="node-box highlight"><div class="node-name">AccountService</div><div class="node-desc">Core Ledger Aggregates</div><div class="node-tech">@RestController</div></div>
        <div class="node-box highlight"><div class="node-name">PaymentGateway</div><div class="node-desc">ISO 20022 Adapter</div><div class="node-tech">@Transactional</div></div>
        <div class="node-box"><div class="node-name">FraudEngine</div><div class="node-desc">Real-time ML Inference</div><div class="node-tech">Resilience4j CB</div></div>
        <div class="node-box"><div class="node-name">NotificationHub</div><div class="node-desc">Async Event Dispatch</div><div class="node-tech">VirtualThreadExecutor</div></div>
      </div>
      <div class="tier-footer">
        <span>● Microservice Pods: <strong>256 Instances</strong></span>
        <span>● Concurrency: <strong>1.2M Virtual Threads</strong></span>
        <span style="color:#38bdf8;">● Inter-Service RPC: <strong>Sub-millisecond gRPC</strong></span>
      </div>
    </div>

    <div class="conduit-bar"><div class="conduit-line"></div><div class="conduit-label">Enterprise Distributed Event Mesh (KRaft Protocol)</div><div class="conduit-line"></div></div>

    <!-- Tier 3: Event Stream Fabric (Kafka) -->
    <div class="tier-card">
      <div class="tier-header"><div class="tier-title">TIER 3: APACHE KAFKA DISTRIBUTED EVENT FABRIC</div><div class="tier-badge">1.8M EVENTS / SEC</div></div>
      <div class="nodes-grid grid-3">
        <div class="node-box"><div class="node-name">transfers.inbound</div><div class="node-desc">32 Partitions / 3x In-Sync Replicas</div><div class="node-tech">Exactly-Once Semantics (EOS-2)</div></div>
        <div class="node-box highlight"><div class="node-name">fraud.verified</div><div class="node-desc">Kafka Streams State Topology</div><div class="node-tech">RocksDB Persistent StateStore</div></div>
        <div class="node-box"><div class="node-name">ledger.committed</div><div class="node-desc">Compacted Immutable Audit Log</div><div class="node-tech">Schema Registry Avro Serialization</div></div>
      </div>
      <div class="tier-footer">
        <span>● Cluster Quorum: <strong>KRaft 5-Broker Controller</strong></span>
        <span>● Message Durability: <strong>acks=all min.insync.replicas=2</strong></span>
        <span style="color:#10b981;">● End-to-End Lag: <strong>0 ms</strong></span>
      </div>
    </div>

    <div class="conduit-bar"><div class="conduit-line"></div><div class="conduit-label">ACID Distributed Persistence &amp; Replication Conduits</div><div class="conduit-line"></div></div>

    <!-- Tier 4: Enterprise Persistence -->
    <div class="tier-card">
      <div class="tier-header"><div class="tier-title">TIER 4: ENTERPRISE PERSISTENCE &amp; DATA GRID</div><div class="tier-badge">ZERO DATA LOSS (RPO=0)</div></div>
      <div class="nodes-grid grid-3">
        <div class="node-box highlight"><div class="node-name">PostgreSQL 16 Cluster</div><div class="node-desc">Primary-Standby Multi-AZ Synchronous</div><div class="node-tech">Hibernate ORM 6.4 / HikariCP Pool</div></div>
        <div class="node-box"><div class="node-name">Distributed Data Grid</div><div class="node-desc">Redis 7 Cluster / Hazelcast IMDG</div><div class="node-tech">Sub-millisecond L2 Caching Tier</div></div>
        <div class="node-box"><div class="node-name">Audit Data Vault</div><div class="node-desc">Encrypted WORM Compliance Storage</div><div class="node-tech">SEC 17a-4 Regulatory Archive</div></div>
      </div>
      <div class="tier-footer">
        <span>● Transaction Isolation: <strong>SERIALIZABLE (ACID)</strong></span>
        <span>● Read Replica Sync: <strong>Streaming WAL &lt; 1ms</strong></span>
        <span style="color:#f59e0b;">● Encryption: <strong>AES-256 at Rest &amp; Transit</strong></span>
      </div>
    </div>

    <div class="conduit-bar"><div class="conduit-line"></div><div class="conduit-label">Telemetry &amp; OpenTelemetry Distributed Tracing Spine</div><div class="conduit-line"></div></div>

    <!-- Tier 5: Observability & Cloud Ops -->
    <div class="tier-card">
      <div class="tier-header"><div class="tier-title">TIER 5: ENTERPRISE OBSERVABILITY &amp; CLOUD PLATFORM</div><div class="tier-badge">FULL DISTRIBUTED TRACING</div></div>
      <div class="nodes-grid grid-3">
        <div class="node-box"><div class="node-name">Prometheus JVM Metrics</div><div class="node-desc">Micrometer Collector (GC, Threads, Heap)</div><div class="node-tech">10s Real-time Scrape Resolution</div></div>
        <div class="node-box highlight"><div class="node-name">Grafana Cloud NOC</div><div class="node-desc">Unified SRE Dashboards &amp; SLO Tracker</div><div class="node-tech">Real-time P99 Latency Anomaly Alerting</div></div>
        <div class="node-box"><div class="node-name">OpenTelemetry Tracing</div><div class="node-desc">W3C TraceContext Ingress to Storage</div><div class="node-tech">Tempo / Jaeger Distributed Spans</div></div>
      </div>
      <div class="tier-footer">
        <span>● SRE Reliability Target: <strong>99.9999% Availability</strong></span>
        <span>● Ingest Rate: <strong>250k spans/sec</strong></span>
        <span style="color:#10b981;">● Anomaly Detection: <strong>ML Auto-Heal Active</strong></span>
      </div>
    </div>
  </div>
  <div class="subtitle-vignette"></div>
</body></html>
"""
render(html_scene3, "scene-03-enterprise-ecosystem.png")

# ==============================================================================
# SCENE 4: PERFORMANCE — Modern JVM (Explicit Height 350px per card)
# ==============================================================================
html_scene4 = f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><style>
{BASE_CSS}
  .perf-canvas {{
    position: absolute; top: 35px; left: 35px; width: 1010px; height: 1580px;
    display: flex; flex-direction: column; justify-content: space-between; z-index: 10;
  }}
  .perf-card {{
    background: #0d1527; border: 1px solid rgba(255,255,255,0.08); border-radius: 12px;
    padding: 18px 22px; box-shadow: 0 15px 35px rgba(0,0,0,0.6); display: flex; flex-direction: column; justify-content: space-between;
    height: 360px;
  }}
  .perf-header {{ display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid rgba(255,255,255,0.06); padding-bottom: 8px; }}
  .perf-title {{ font-size: 13px; font-weight: 700; color: #38bdf8; letter-spacing: 0.5px; text-transform: uppercase; }}
  .perf-badge {{ font-size: 11px; color: #f59e0b; font-weight: 600; background: rgba(245,158,11,0.12); border: 1px solid rgba(245,158,11,0.25); padding: 3px 10px; border-radius: 6px; }}

  .thread-lanes {{ display: flex; flex-direction: column; gap: 6px; }}
  .thread-lane {{
    background: #0a0f1d; border: 1px solid rgba(255,255,255,0.05); border-radius: 6px;
    height: 26px; display: flex; align-items: center; padding: 0 10px; gap: 10px;
  }}
  .lane-label {{ font-size: 10.5px; font-weight: 700; color: #64748b; width: 125px; }}
  .lane-track {{ flex: 1; height: 12px; background: #131c30; border-radius: 6px; display: flex; gap: 3px; overflow: hidden; padding: 2px; }}
  .segment {{ height: 100%; border-radius: 2px; }}
  .seg-blue {{ background: #38bdf8; flex: 3; }}
  .seg-green {{ background: #10b981; flex: 4; }}
  .seg-amber {{ background: #f59e0b; flex: 2; }}
  .seg-purple {{ background: #a855f7; flex: 3; }}

  .pipeline-steps {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; }}
  .pipe-step {{
    background: #111a2e; border: 1px solid rgba(255,255,255,0.06); border-radius: 8px;
    padding: 12px; display: flex; flex-direction: column; gap: 4px;
  }}
  .pipe-num {{ font-size: 9.5px; color: #38bdf8; font-weight: 700; }}
  .pipe-name {{ font-size: 12.5px; font-weight: 700; color: #f8fafc; }}
  .pipe-desc {{ font-size: 10.5px; color: #94a3b8; }}

  .heap-vis {{ display: flex; height: 48px; border-radius: 8px; overflow: hidden; gap: 2px; }}
  .heap-young {{ background: #10b981; flex: 2.5; display: flex; align-items: center; justify-content: center; font-size: 11px; font-weight: 700; color: #052e16; }}
  .heap-old {{ background: #0284c7; flex: 4.5; display: flex; align-items: center; justify-content: center; font-size: 11px; font-weight: 700; color: #082f49; }}
  .heap-free {{ background: #1e293b; flex: 3; display: flex; align-items: center; justify-content: center; font-size: 11px; font-weight: 700; color: #64748b; }}
</style></head>
<body>
  <div class="bg-glow"></div><div class="grid-pattern"></div>
  <div class="perf-canvas">
    <!-- Concurrency: Loom -->
    <div class="perf-card">
      <div class="perf-header"><div class="perf-title">CONCURRENCY: PROJECT LOOM &amp; VIRTUAL THREADS</div><div class="perf-badge">1,000,000+ LIGHTWEIGHT THREADS</div></div>
      <div class="thread-lanes">
        <div class="thread-lane"><div class="lane-label">Carrier Worker 01</div><div class="lane-track"><div class="seg-blue"></div><div class="seg-green"></div><div class="seg-amber"></div><div class="seg-purple"></div><div class="seg-blue"></div></div></div>
        <div class="thread-lane"><div class="lane-label">Carrier Worker 02</div><div class="lane-track"><div class="seg-green"></div><div class="seg-purple"></div><div class="seg-blue"></div><div class="seg-amber"></div><div class="seg-green"></div></div></div>
        <div class="thread-lane"><div class="lane-label">Carrier Worker 03</div><div class="lane-track"><div class="seg-amber"></div><div class="seg-blue"></div><div class="seg-green"></div><div class="seg-purple"></div><div class="seg-blue"></div></div></div>
        <div class="thread-lane"><div class="lane-label">Carrier Worker 04</div><div class="lane-track"><div class="seg-purple"></div><div class="seg-amber"></div><div class="seg-blue"></div><div class="seg-green"></div><div class="seg-amber"></div></div></div>
        <div class="thread-lane"><div class="lane-label">Carrier Worker 05</div><div class="lane-track"><div class="seg-blue"></div><div class="seg-purple"></div><div class="seg-amber"></div><div class="seg-green"></div><div class="seg-blue"></div></div></div>
        <div class="thread-lane"><div class="lane-label">Carrier Worker 06</div><div class="lane-track"><div class="seg-green"></div><div class="seg-amber"></div><div class="seg-blue"></div><div class="seg-purple"></div><div class="seg-green"></div></div></div>
        <div class="thread-lane"><div class="lane-label">Carrier Worker 07</div><div class="lane-track"><div class="seg-amber"></div><div class="seg-green"></div><div class="seg-purple"></div><div class="seg-blue"></div><div class="seg-amber"></div></div></div>
      </div>
      <div style="display:grid; grid-template-columns:repeat(3, 1fr); gap:10px;">
        <div style="background:#0a0f1d; padding:8px 12px; border-radius:6px; font-size:11px; border:1px solid rgba(255,255,255,0.04);">
          <div style="color:#64748b;">ACTIVE VIRTUAL THREADS</div>
          <div style="font-size:18px; font-weight:700; color:#38bdf8;">1,240,000</div>
        </div>
        <div style="background:#0a0f1d; padding:8px 12px; border-radius:6px; font-size:11px; border:1px solid rgba(255,255,255,0.04);">
          <div style="color:#64748b;">MEMORY FOOTPRINT</div>
          <div style="font-size:18px; font-weight:700; color:#10b981;">&lt; 1 KB / Thread</div>
        </div>
        <div style="background:#0a0f1d; padding:8px 12px; border-radius:6px; font-size:11px; border:1px solid rgba(255,255,255,0.04);">
          <div style="color:#64748b;">SCHEDULER CPU LOAD</div>
          <div style="font-size:18px; font-weight:700; color:#f59e0b;">0.04% Overhead</div>
        </div>
      </div>
    </div>

    <!-- JIT Compilation Pipeline -->
    <div class="perf-card">
      <div class="perf-header"><div class="perf-title">EXECUTION ENGINE: TIERED JIT &amp; GRAALVM COMPILER</div><div class="perf-badge">DYNAMIC ADAPTIVE OPTIMIZATION</div></div>
      <div class="pipeline-steps">
        <div class="pipe-step"><div class="pipe-num">STAGE 01</div><div class="pipe-name">Bytecode</div><div class="pipe-desc">Portable .class representation</div></div>
        <div class="pipe-step"><div class="pipe-num">STAGE 02</div><div class="pipe-name">C1 Client JIT</div><div class="pipe-desc">Fast baseline machine code</div></div>
        <div class="pipe-step"><div class="pipe-num">STAGE 03</div><div class="pipe-name">PGO Profiling</div><div class="pipe-desc">Branch counters &amp; type feedback</div></div>
        <div class="pipe-step" style="border-color:rgba(56,189,248,0.5);"><div class="pipe-num">STAGE 04</div><div class="pipe-name">C2 / GraalVM</div><div class="pipe-desc">AVX-512 SIMD Vectorization</div></div>
      </div>
      <div style="background:#0a0f1d; border:1px solid rgba(255,255,255,0.06); border-radius:6px; padding:10px 14px; font-size:11px; color:#38bdf8; font-family:monospace; line-height:1.5;">
        <div>vmovups ymm0, [rdi+rax*4] ; Vectorized inner loop AVX-512 SIMD</div>
        <div style="color:#94a3b8;">vaddps  ymm0, ymm0, [rsi+rax*4] ; 8 parallel single-precision floats / cycle</div>
        <div style="color:#10b981;">● Inlining Depth: 9 levels | Escape Analysis: 100% Scalar Replaced</div>
      </div>
    </div>

    <!-- Memory: Generational ZGC -->
    <div class="perf-card">
      <div class="perf-header"><div class="perf-title">MEMORY MANAGEMENT: GENERATIONAL ZGC</div><div class="perf-badge">MAX PAUSE &lt; 0.5 MILLISECOND</div></div>
      <div class="heap-vis">
        <div class="heap-young">Young Gen (Eden &amp; Survivor - 16GB)</div>
        <div class="heap-old">Old Gen (Tenured - Colored Pointers - 32GB)</div>
        <div class="heap-free">Available Heap Headroom (16GB)</div>
      </div>
      <div style="display:grid; grid-template-columns:repeat(4, 1fr); gap:10px;">
        <div style="background:#111a2e; padding:10px; border-radius:6px; font-size:11px;">
          <div style="color:#64748b;">CONCURRENT MARK</div>
          <div style="color:#38bdf8; font-weight:700;">Zero Stop-World</div>
        </div>
        <div style="background:#111a2e; padding:10px; border-radius:6px; font-size:11px;">
          <div style="color:#64748b;">COLORED POINTERS</div>
          <div style="color:#10b981; font-weight:700;">Load Barrier Active</div>
        </div>
        <div style="background:#111a2e; padding:10px; border-radius:6px; font-size:11px;">
          <div style="color:#64748b;">MAX RECORDED PAUSE</div>
          <div style="color:#f59e0b; font-weight:700;">0.38 ms</div>
        </div>
        <div style="background:#111a2e; padding:10px; border-radius:6px; font-size:11px;">
          <div style="color:#64748b;">TOTAL HEAP SIZE</div>
          <div style="color:#a855f7; font-weight:700;">64 GB (Terabyte scale)</div>
        </div>
      </div>
    </div>

    <!-- Throughput & Latency Distribution -->
    <div class="perf-card">
      <div class="perf-header"><div class="perf-title">PRODUCTION TELEMETRY: 500K REQ/SEC BENCHMARK</div><div class="perf-badge">FLAT P99 PROFILE</div></div>
      <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px;">
        <div style="background:#111a2e; padding:12px; border-radius:8px;">
          <div style="font-size:10.5px; color:#64748b; font-weight:700;">SUSTAINED RPS</div>
          <div style="font-size:22px; font-weight:700; color:#38bdf8;">524,800</div>
          <div style="font-size:10.5px; color:#10b981;">▲ 99.98% success rate</div>
        </div>
        <div style="background:#111a2e; padding:12px; border-radius:8px;">
          <div style="font-size:10.5px; color:#64748b; font-weight:700;">P99 LATENCY</div>
          <div style="font-size:22px; font-weight:700; color:#10b981;">2.14 ms</div>
          <div style="font-size:10.5px; color:#94a3b8;">Zero GC latency spikes</div>
        </div>
        <div style="background:#111a2e; padding:12px; border-radius:8px;">
          <div style="font-size:10.5px; color:#64748b; font-weight:700;">CPU SATURATION</div>
          <div style="font-size:22px; font-weight:700; color:#f59e0b;">42.8%</div>
          <div style="font-size:10.5px; color:#94a3b8;">128 vCPUs linear scaling</div>
        </div>
      </div>
      <div style="height:48px; background:#0a0f1d; border-radius:6px; padding:0 14px; display:flex; align-items:center; gap:12px;">
        <span style="font-size:10px; color:#64748b; font-weight:700;">REAL-TIME P99 LATENCY (1HR)</span>
        <svg style="flex:1; height:24px;">
          <path d="M0,12 Q100,10 200,12 T400,12 T600,11 T800,12" fill="none" stroke="#10b981" stroke-width="2"/>
        </svg>
        <span style="font-size:11px; color:#10b981; font-weight:700;">STABLE 1.84ms</span>
      </div>
    </div>
  </div>
  <div class="subtitle-vignette"></div>
</body></html>
"""
render(html_scene4, "scene-04-modern-performance.png")

# ==============================================================================
# SCENE 5: SCALE & MAINTAINABILITY (Explicit Height 360px per card)
# ==============================================================================
html_scene5 = f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><style>
{BASE_CSS}
  .mod-canvas {{
    position: absolute; top: 35px; left: 35px; width: 1010px; height: 1580px;
    display: flex; flex-direction: column; justify-content: space-between; z-index: 10;
  }}
  .mod-card {{
    background: #0d1527; border: 1px solid rgba(255,255,255,0.08); border-radius: 12px;
    padding: 18px 22px; box-shadow: 0 15px 35px rgba(0,0,0,0.6); display: flex; flex-direction: column; justify-content: space-between;
    height: 360px;
  }}
  .mod-header {{ display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid rgba(255,255,255,0.06); padding-bottom: 8px; }}
  .mod-title {{ font-size: 13px; font-weight: 700; color: #38bdf8; letter-spacing: 0.5px; text-transform: uppercase; }}
  .mod-badge {{ font-size: 11px; color: #10b981; font-weight: 600; background: rgba(16,185,129,0.12); border: 1px solid rgba(16,185,129,0.25); padding: 3px 10px; border-radius: 6px; }}

  .code-block {{
    background: #0a0f1d; border: 1px solid rgba(255,255,255,0.06); border-radius: 8px;
    padding: 14px 18px; font-size: 12px; line-height: 1.65; color: #e2e8f0;
  }}
  .kw {{ color: #f43f5e; font-weight: 600; }}
  .type {{ color: #38bdf8; font-weight: 600; }}
  .fn {{ color: #60a5fa; }}
  .str {{ color: #34d399; }}
  .var {{ color: #f1f5f9; }}
  .com {{ color: #475569; font-style: italic; }}

  .layers-stack {{ display: flex; flex-direction: column; gap: 7px; }}
  .layer-row {{
    background: #111a2e; border: 1px solid rgba(255,255,255,0.06); border-radius: 8px;
    padding: 11px 16px; display: flex; justify-content: space-between; align-items: center;
  }}
  .layer-name {{ font-size: 12.5px; font-weight: 700; color: #f8fafc; }}
  .layer-rule {{ font-size: 11px; color: #38bdf8; }}

  .timeline-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; }}
  .time-box {{ background: #111a2e; border: 1px solid rgba(255,255,255,0.06); border-radius: 8px; padding: 12px; text-align: center; }}
  .time-ver {{ font-size: 14px; font-weight: 700; color: #38bdf8; }}
  .time-desc {{ font-size: 10.5px; color: #94a3b8; margin-top: 3px; }}
</style></head>
<body>
  <div class="bg-glow"></div><div class="grid-pattern"></div>
  <div class="mod-canvas">
    <!-- Strong Type Safety & Pattern Matching -->
    <div class="mod-card">
      <div class="mod-header"><div class="mod-title">COMPILE-TIME TYPE SAFETY: SEALED HIERARCHIES &amp; RECORDS</div><div class="mod-badge">EXHAUSTIVE PATTERN MATCHING</div></div>
      <div class="code-block">
        <div><span class="kw">public sealed interface</span> <span class="type">PaymentResult</span> <span class="kw">permits</span> <span class="type">Settled</span>, <span class="type">Declined</span>, <span class="type">FraudHold</span> {{}}</div>
        <div style="margin-top:3px;"><span class="kw">public record</span> <span class="type">Settled</span>(<span class="type">TxnId</span> <span class="var">id</span>, <span class="type">Money</span> <span class="var">amount</span>, <span class="type">Instant</span> <span class="var">timestamp</span>) <span class="kw">implements</span> <span class="type">PaymentResult</span> {{}}</div>
        <div style="margin-top:3px;"><span class="kw">public record</span> <span class="type">Declined</span>(<span class="type">TxnId</span> <span class="var">id</span>, <span class="type">String</span> <span class="var">reason</span>) <span class="kw">implements</span> <span class="type">PaymentResult</span> {{}}</div>
        <div style="margin-top:5px;"><span class="kw">public</span> <span class="type">String</span> <span class="fn">handle</span>(<span class="type">PaymentResult</span> <span class="var">res</span>) = <span class="kw">switch</span> (<span class="var">res</span>) {{</div>
        <div>&nbsp;&nbsp;<span class="kw">case</span> <span class="type">Settled</span> <span class="var">s</span>   -&gt; <span class="str">"Success: "</span> + <span class="var">s</span>.<span class="fn">id</span>() + <span class="str">" | Amount: "</span> + <span class="var">s</span>.<span class="fn">amount</span>();</div>
        <div>&nbsp;&nbsp;<span class="kw">case</span> <span class="type">Declined</span> <span class="var">d</span>  -&gt; <span class="str">"Rejected: "</span> + <span class="var">d</span>.<span class="fn">reason</span>();</div>
        <div>&nbsp;&nbsp;<span class="kw">case</span> <span class="type">FraudHold</span> <span class="var">f</span> -&gt; <span class="str">"Escalate to RiskOps: "</span> + <span class="var">f</span>.<span class="fn">riskScore</span>();</div>
        <div>}}; <span class="com">// Compiler guarantees all branches handled with zero default needed</span></div>
      </div>
      <div style="background:#0a0f1d; padding:8px 12px; border-radius:6px; display:flex; justify-content:space-between; font-size:11px; color:#94a3b8;">
        <span>● Null Safety: <strong>Objects.requireNonNull() in Compact Constructors</strong></span>
        <span style="color:#10b981;">● Zero NullPointerExceptions in Core Domain</span>
      </div>
    </div>

    <!-- Clean Architecture Layers -->
    <div class="mod-card">
      <div class="mod-header"><div class="mod-title">CLEAN MODULAR ARCHITECTURE: DEPENDENCY INVERSION</div><div class="mod-badge">10-YEAR CODEBASE SURVIVAL</div></div>
      <div class="layers-stack">
        <div class="layer-row" style="border-left: 4px solid #38bdf8;"><div class="layer-name">1. Ingress Adapters</div><div class="layer-rule">Spring MVC Rest, gRPC Endpoints, Kafka Consumers</div></div>
        <div class="layer-row" style="border-left: 4px solid #10b981;"><div class="layer-name">2. Application Use Cases</div><div class="layer-rule">Transaction Handlers, Command &amp; Query Bus</div></div>
        <div class="layer-row" style="border-left: 4px solid #f59e0b;"><div class="layer-name">3. Pure Domain Entities</div><div class="layer-rule">Account Aggregates, Value Objects, Zero Lib Deps</div></div>
        <div class="layer-row" style="border-left: 4px solid #a855f7;"><div class="layer-name">4. Infrastructure Adapters</div><div class="layer-rule">PostgreSQL JPA Repositories, Kafka Event Sinks</div></div>
      </div>
      <div style="background:#0a0f1d; padding:8px 12px; border-radius:6px; display:flex; justify-content:space-between; font-size:11px; color:#94a3b8;">
        <span>● Dependency Rule: <strong>Dependencies point strictly inward toward Domain</strong></span>
        <span style="color:#38bdf8;">● ArchUnit Test: 100% Enforced in CI</span>
      </div>
    </div>

    <!-- Backward Compatibility Guarantees -->
    <div class="mod-card">
      <div class="mod-header"><div class="mod-title">ENTERPRISE LONGEVITY: BACKWARD COMPATIBILITY GUARANTEE</div><div class="mod-badge">BINARY COMPATIBLE</div></div>
      <div class="timeline-grid">
        <div class="time-box"><div class="time-ver">Java 8 (2014)</div><div class="time-desc">Lambdas / Streams API</div></div>
        <div class="time-box"><div class="time-ver">Java 17 (2021)</div><div class="time-desc">Records &amp; Sealed Classes</div></div>
        <div class="time-box"><div class="time-ver" style="color:#10b981;">Java 21 (LTS)</div><div class="time-desc">Virtual Threads &amp; ZGC</div></div>
        <div class="time-box"><div class="time-ver">Java 25 (LTS)</div><div class="time-desc">Project Valhalla / Leyden</div></div>
      </div>
      <div style="font-size:11px; color:#94a3b8; line-height:1.45; background:#0a0f1d; padding:10px 14px; border-radius:6px;">
        Enterprises run decade-old core banking services without breaking rewrites. Continuous binary backward compatibility protects billions of dollars in enterprise software investments.
      </div>
    </div>

    <!-- Enterprise Large-Team Scale -->
    <div class="mod-card">
      <div class="mod-header"><div class="mod-title">ENGINEERING GOVERNANCE: AUTOMATED QUALITY GATES</div><div class="mod-badge">500+ ENGINEERS COLLABORATING</div></div>
      <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px;">
        <div style="background:#111a2e; padding:12px; border-radius:8px;">
          <div style="font-size:10.5px; color:#64748b; font-weight:700;">AUTOMATED TESTS</div>
          <div style="font-size:22px; font-weight:700; color:#38bdf8;">18,420</div>
          <div style="font-size:10.5px; color:#10b981;">100% Passing (CI Pipeline)</div>
        </div>
        <div style="background:#111a2e; padding:12px; border-radius:8px;">
          <div style="font-size:10.5px; color:#64748b; font-weight:700;">CODE COVERAGE</div>
          <div style="font-size:22px; font-weight:700; color:#10b981;">99.4%</div>
          <div style="font-size:10.5px; color:#94a3b8;">Jacoco Branch Coverage</div>
        </div>
        <div style="background:#111a2e; padding:12px; border-radius:8px;">
          <div style="font-size:10.5px; color:#64748b; font-weight:700;">SONARQUBE GATE</div>
          <div style="font-size:22px; font-weight:700; color:#a855f7;">GRADE A</div>
          <div style="font-size:10.5px; color:#94a3b8;">Zero Security Hotspots</div>
        </div>
      </div>
      <div style="background:#0a0f1d; padding:10px 14px; border-radius:6px; display:flex; justify-content:space-between; font-size:11px; color:#94a3b8;">
        <span>● ArchUnit Architecture Rules: <strong>Enforced</strong></span>
        <span>● Automated CI Build: <strong>Passed in 3m 42s</strong></span>
        <span style="color:#10b981;">● Security Vulnerabilities: <strong>0</strong></span>
      </div>
    </div>
  </div>
  <div class="subtitle-vignette"></div>
</body></html>
"""
render(html_scene5, "scene-05-scale-and-maintainability.png")

# ==============================================================================
# SCENE 6: MISSION CRITICAL — Global Financial NOC (Explicit Height Distribution)
# ==============================================================================
html_scene6 = f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><style>
{BASE_CSS}
  .noc-canvas {{
    position: absolute; top: 35px; left: 35px; width: 1010px; height: 1580px;
    display: flex; flex-direction: column; justify-content: space-between; z-index: 10;
  }}
  .noc-card {{
    background: #0d1527; border: 1px solid rgba(255,255,255,0.08); border-radius: 12px;
    padding: 16px 20px; box-shadow: 0 15px 35px rgba(0,0,0,0.6); display: flex; flex-direction: column; justify-content: space-between;
  }}
  .noc-header {{ display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid rgba(255,255,255,0.06); padding-bottom: 8px; }}
  .noc-title {{ font-size: 13px; font-weight: 700; color: #38bdf8; letter-spacing: 0.5px; text-transform: uppercase; }}
  .noc-badge {{ font-size: 11px; color: #10b981; font-weight: 600; background: rgba(16,185,129,0.12); border: 1px solid rgba(16,185,129,0.25); padding: 3px 10px; border-radius: 6px; }}

  .map-box {{
    height: 380px; background: #0a0f1d; border: 1px solid rgba(255,255,255,0.06); border-radius: 10px;
    position: relative; overflow: hidden; margin: 8px 0;
  }}
  .map-hub {{
    position: absolute; width: 14px; height: 14px; border-radius: 50%;
    background: #38bdf8; box-shadow: 0 0 15px #38bdf8; display: flex; align-items: center; justify-content: center;
  }}
  .hub-ping {{
    position: absolute; inset: -8px; border-radius: 50%; border: 1px solid rgba(56, 189, 248, 0.6);
  }}
  .hub-label {{
    position: absolute; top: 18px; font-size: 11px; font-weight: 700; color: #f8fafc; white-space: nowrap;
  }}

  .stream-rows {{ display: flex; flex-direction: column; gap: 6px; margin: 6px 0; }}
  .stream-row {{
    background: #111a2e; border: 1px solid rgba(255,255,255,0.06); border-radius: 6px;
    padding: 8px 14px; display: flex; justify-content: space-between; align-items: center;
  }}
  .stream-id {{ font-size: 10.5px; color: #38bdf8; font-weight: 700; width: 95px; }}
  .stream-type {{ font-size: 11px; color: #f8fafc; font-weight: 500; flex: 1; }}
  .stream-status {{ font-size: 10px; color: #10b981; font-weight: 700; }}
</style></head>
<body>
  <div class="bg-glow"></div><div class="grid-pattern"></div>
  <div class="noc-canvas">
    <!-- Top Stats Banner (Height 190px) -->
    <div class="noc-card" style="height: 190px;">
      <div class="noc-header"><div class="noc-title">GLOBAL FINANCIAL SETTLEMENT GRID</div><div class="noc-badge">AVAILABILITY: 99.9999%</div></div>
      <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px;">
        <div style="background:#111a2e; padding:12px; border-radius:8px;">
          <div style="font-size:10.5px; color:#64748b; font-weight:700;">DAILY SETTLEMENT</div>
          <div style="font-size:22px; font-weight:700; color:#38bdf8;">$4.82T USD</div>
          <div style="font-size:10.5px; color:#10b981;">Interbank Core Volume</div>
        </div>
        <div style="background:#111a2e; padding:12px; border-radius:8px;">
          <div style="font-size:10.5px; color:#64748b; font-weight:700;">ZERO DATA LOSS</div>
          <div style="font-size:22px; font-weight:700; color:#10b981;">RPO = 0</div>
          <div style="font-size:10.5px; color:#94a3b8;">RTO &lt; 1.5 Seconds</div>
        </div>
        <div style="background:#111a2e; padding:12px; border-radius:8px;">
          <div style="font-size:10.5px; color:#64748b; font-weight:700;">COMPLIANCE</div>
          <div style="font-size:22px; font-weight:700; color:#f59e0b;">ISO 20022</div>
          <div style="font-size:10.5px; color:#94a3b8;">SWIFT MT/MX Native</div>
        </div>
      </div>
    </div>

    <!-- Global Financial Topology Map (Height 480px) -->
    <div class="noc-card" style="height: 480px;">
      <div class="noc-header"><div class="noc-title">GLOBAL REAL-TIME SETTLEMENT TOPOLOGY</div><div class="noc-badge">14,820 CONNECTED INSTITUTIONS</div></div>
      <div class="map-box">
        <svg style="position:absolute; inset:0; width:100%; height:100%;">
          <line x1="0" y1="95" x2="1000" y2="95" stroke="rgba(255,255,255,0.03)" stroke-width="1"/>
          <line x1="0" y1="190" x2="1000" y2="190" stroke="rgba(255,255,255,0.03)" stroke-width="1"/>
          <line x1="0" y1="285" x2="1000" y2="285" stroke="rgba(255,255,255,0.03)" stroke-width="1"/>
          <line x1="250" y1="0" x2="250" y2="380" stroke="rgba(255,255,255,0.03)" stroke-width="1"/>
          <line x1="500" y1="0" x2="500" y2="380" stroke="rgba(255,255,255,0.03)" stroke-width="1"/>
          <line x1="750" y1="0" x2="750" y2="380" stroke="rgba(255,255,255,0.03)" stroke-width="1"/>

          <!-- Routing lines -->
          <line x1="180" y1="130" x2="450" y2="100" stroke="#38bdf8" stroke-width="2" stroke-dasharray="4 4" opacity="0.7"/>
          <line x1="450" y1="100" x2="780" y2="140" stroke="#38bdf8" stroke-width="2" stroke-dasharray="4 4" opacity="0.7"/>
          <line x1="780" y1="140" x2="680" y2="260" stroke="#38bdf8" stroke-width="2" stroke-dasharray="4 4" opacity="0.7"/>
          <line x1="180" y1="130" x2="680" y2="260" stroke="#38bdf8" stroke-width="2" stroke-dasharray="4 4" opacity="0.3"/>
          <line x1="450" y1="100" x2="680" y2="260" stroke="#10b981" stroke-width="2" stroke-dasharray="4 4" opacity="0.6"/>
        </svg>
        <div class="map-hub" style="left:170px; top:120px;"><div class="hub-ping"></div><div class="hub-label">New York (Fedwire)</div></div>
        <div class="map-hub" style="left:440px; top:90px;"><div class="hub-ping"></div><div class="hub-label">London (CHAPS / SWIFT)</div></div>
        <div class="map-hub" style="left:770px; top:130px;"><div class="hub-ping"></div><div class="hub-label">Tokyo (BOJ-NET)</div></div>
        <div class="map-hub" style="left:670px; top:250px;"><div class="hub-ping"></div><div class="hub-label">Singapore / Bangkok (BAHTNET)</div></div>
      </div>
      <div style="display:flex; justify-content:space-between; font-size:11px; color:#94a3b8; background:#0a0f1d; padding:8px 14px; border-radius:6px;">
        <span>Latency: Transatlantic <strong>32ms</strong> | Transpacific <strong>54ms</strong> | Regional <strong>8ms</strong></span>
        <span style="color:#10b981;">● All Interbank Fiber Trunks Online</span>
      </div>
    </div>

    <!-- Live Transaction Stream (Height 520px) -->
    <div class="noc-card" style="height: 520px;">
      <div class="noc-header"><div class="noc-title">REAL-TIME MISSION CRITICAL TRANSACTION STREAM</div><div class="noc-badge">LATENCY: 0.8MS (ACID)</div></div>
      <div class="stream-rows">
        <div class="stream-row"><div class="stream-id">TXN-882941</div><div class="stream-type">RTGS High-Value Interbank Clearing ($140,000,000 USD)</div><div class="stream-status">SETTLED (ACID)</div></div>
        <div class="stream-row"><div class="stream-id">TXN-882942</div><div class="stream-type">Foreign Exchange Cross-Currency Swap (JPY/USD ¥12.4B)</div><div class="stream-status">SETTLED (ACID)</div></div>
        <div class="stream-row"><div class="stream-id">TXN-882943</div><div class="stream-type">Core Banking ISO 20022 Instant Payment pacs.008</div><div class="stream-status">SETTLED (ACID)</div></div>
        <div class="stream-row"><div class="stream-id">TXN-882944</div><div class="stream-type">Securities Depository Netting Batch (Depository Trust)</div><div class="stream-status">SETTLED (ACID)</div></div>
        <div class="stream-row"><div class="stream-id">TXN-882945</div><div class="stream-type">Real-Time Retail Payment Settlement (PromptPay Instant)</div><div class="stream-status">SETTLED (ACID)</div></div>
        <div class="stream-row"><div class="stream-id">TXN-882946</div><div class="stream-type">Treasury Central Liquidity Rebalancing Sweep</div><div class="stream-status">SETTLED (ACID)</div></div>
        <div class="stream-row"><div class="stream-id">TXN-882947</div><div class="stream-type">Multi-Currency Card Network Batch Settlement</div><div class="stream-status">SETTLED (ACID)</div></div>
        <div class="stream-row"><div class="stream-id">TXN-882948</div><div class="stream-type">Central Counterparty Clearing Margin Collateral Call</div><div class="stream-status">SETTLED (ACID)</div></div>
      </div>
      <div style="background:#0a0f1d; padding:8px 14px; border-radius:6px; display:flex; justify-content:space-between; font-size:11px; color:#94a3b8;">
        <span>Stream Processing Engine: <strong>Apache Kafka + RocksDB</strong></span>
        <span style="color:#38bdf8;">Peak Load: <strong>1,840,000 tx/sec</strong></span>
      </div>
    </div>

    <!-- Distributed Ledger Consensus Grid (Height 230px) -->
    <div class="noc-card" style="height: 230px;">
      <div class="noc-header"><div class="noc-title">CONSENSUS &amp; DATA INTEGRITY VERIFICATION</div><div class="noc-badge">ZERO PHANTOM READS</div></div>
      <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px;">
        <div style="background:#111a2e; padding:12px; border-radius:6px; font-size:11px;">
          <div style="color:#38bdf8; font-weight:700; font-size:12px;">2PC &amp; Raft Quorum</div>
          <div style="color:#94a3b8; font-size:10.5px; margin-top:4px;">3-AZ Synchronous State Commitment</div>
        </div>
        <div style="background:#111a2e; padding:12px; border-radius:6px; font-size:11px;">
          <div style="color:#10b981; font-weight:700; font-size:12px;">SHA-256 Merkle Audit</div>
          <div style="color:#94a3b8; font-size:10.5px; margin-top:4px;">Continuous Cryptographic Proof Verified</div>
        </div>
        <div style="background:#111a2e; padding:12px; border-radius:6px; font-size:11px;">
          <div style="color:#f59e0b; font-weight:700; font-size:12px;">Immutable Write-Once</div>
          <div style="color:#94a3b8; font-size:10.5px; margin-top:4px;">Regulatory Compliance SEC 17a-4</div>
        </div>
      </div>
      <div style="background:#0a0f1d; padding:8px 14px; border-radius:6px; display:flex; justify-content:space-between; font-size:11px; color:#10b981;">
        <span>● Ledger State: <strong>100% Consistent Across 3 Geo-Redundant Sites</strong></span>
        <span>RPO = 0 (Zero Loss)</span>
      </div>
    </div>
  </div>
  <div class="subtitle-vignette"></div>
</body></html>
"""
render(html_scene6, "scene-06-real-world-usage.png")

# ==============================================================================
# SCENE 7: CONCLUSION — Dual Displays, Production Green & Workstation
# ==============================================================================
html_scene7 = f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><style>
{BASE_CSS}
  .cockpit-frame {{
    position: absolute; top: 35px; left: 35px; width: 1010px; height: 1220px;
    display: flex; gap: 18px; z-index: 10;
  }}
  .screen {{
    flex: 1; background: #0f172a; border-radius: 16px;
    box-shadow: 0 30px 80px rgba(0,0,0,0.9), 0 0 0 1px rgba(255,255,255,0.08), 0 0 40px rgba(16, 185, 129, 0.12);
    display: flex; flex-direction: column; overflow: hidden;
  }}
  .screen-header {{
    height: 44px; background: #0b1120; border-bottom: 1px solid rgba(255,255,255,0.08);
    display: flex; align-items: center; padding: 0 16px; justify-content: space-between;
  }}
  .screen-title {{ font-size: 12px; font-weight: 700; color: #38bdf8; }}
  .screen-status {{ font-size: 11px; color: #10b981; font-weight: 700; }}

  .screen-body {{ flex: 1; background: #0a0f1d; padding: 14px; display: flex; flex-direction: column; gap: 10px; font-size: 12px; line-height: 1.6; overflow: hidden; }}
  
  .desk-surface {{ position: absolute; top: 1280px; left: 0; width: 1080px; height: 640px; background: linear-gradient(180deg, #090d16 0%, #060911 50%, #020306 100%); border-top: 1px solid rgba(255,255,255,0.05); z-index: 4; }}
  .desk-mat {{ position: absolute; top: 1330px; left: 30px; width: 1020px; height: 500px; background: #0d1322; border-radius: 16px; border: 1px solid rgba(255,255,255,0.04); box-shadow: inset 0 2px 10px rgba(0,0,0,0.6), 0 20px 50px rgba(0,0,0,0.8); z-index: 7; }}
  
  .keyboard-frame {{ position: absolute; top: 1370px; left: 100px; width: 640px; height: 210px; background: #111827; border-radius: 12px; padding: 14px; box-shadow: 0 15px 35px rgba(0,0,0,0.8); z-index: 8; }}
  .wrist-rest {{ position: absolute; top: 1595px; left: 100px; width: 640px; height: 48px; background: #0b101c; border-radius: 8px; border: 1px solid rgba(255,255,255,0.03); z-index: 8; }}
  .key-rows {{ display: flex; flex-direction: column; gap: 6px; }}
  .key-row {{ display: flex; gap: 6px; }}
  .key {{ height: 28px; background: #1e293b; border-radius: 4px; flex: 1; }}
  .key.space {{ flex: 6; background: #243247; }} .key.accent {{ background: #10b981; }} .key.mod {{ flex: 1.5; background: #162032; }}
  
  .mouse {{ position: absolute; top: 1410px; left: 810px; width: 85px; height: 145px; background: radial-gradient(circle at 40px 40px, #1e293b 0%, #0f172a 100%); border-radius: 42px; z-index: 8; }}
  .mouse-wheel {{ position: absolute; top: 25px; left: 38px; width: 8px; height: 24px; background: #10b981; border-radius: 4px; }}
  .coffee-mug {{ position: absolute; top: 1370px; left: 920px; width: 70px; height: 70px; border-radius: 50%; background: radial-gradient(circle, #2d1810 40%, #522d1e 75%, #1e293b 100%); border: 3px solid #334155; z-index: 8; }}
</style></head>
<body>
  <div class="bg-glow"></div><div class="grid-pattern"></div>
  <div class="cockpit-frame">
    <!-- Left Screen: Build & Test Success (Fully Populated) -->
    <div class="screen">
      <div class="screen-header"><div class="screen-title">INTELLIJ IDEA — BUILD &amp; TEST SUITE</div><div class="screen-status">● 100% PASSED</div></div>
      <div class="screen-body">
        <div style="background:#052e16; border:1px solid #10b981; border-radius:8px; padding:10px 14px; color:#a7f3d0; font-weight:700; display:flex; justify-content:space-between; align-items:center;">
          <span>✔ ALL 18,420 TESTS PASSED</span><span style="font-size:11px; color:#10b981;">Total Time: 14.2s</span>
        </div>

        <!-- Code Editor Slice -->
        <div style="background:#060913; border:1px solid rgba(255,255,255,0.06); border-radius:8px; padding:12px 14px; font-size:11px; line-height:1.6; color:#94a3b8; height:430px; overflow:hidden;">
          <div style="color:#64748b; font-size:10px; margin-bottom:6px; text-transform:uppercase;">CoreBankingIntegrationTest.java</div>
          <div><span style="color:#f43f5e;">@SpringBootTest</span>(<span style="color:#38bdf8;">webEnvironment</span> = <span style="color:#eab308;">RANDOM_PORT</span>)</div>
          <div><span style="color:#f43f5e;">@Testcontainers</span></div>
          <div><span style="color:#f43f5e;">class</span> <span style="color:#38bdf8;">CoreBankingIntegrationTest</span> {{</div>
          <div>&nbsp;&nbsp;<span style="color:#f43f5e;">@Container</span> <span style="color:#f43f5e;">static</span> <span style="color:#38bdf8;">KafkaContainer</span> kafka = <span style="color:#f43f5e;">new</span> <span style="color:#38bdf8;">KafkaContainer</span>();</div>
          <div>&nbsp;&nbsp;<span style="color:#f43f5e;">@Container</span> <span style="color:#f43f5e;">static</span> <span style="color:#38bdf8;">PostgreSQLContainer</span>&lt;?&gt; pg = <span style="color:#f43f5e;">new</span> <span style="color:#38bdf8;">PostgreSQLContainer</span>();</div>
          <div></div>
          <div>&nbsp;&nbsp;<span style="color:#f43f5e;">@Test</span></div>
          <div>&nbsp;&nbsp;<span style="color:#f43f5e;">void</span> <span style="color:#60a5fa;">shouldExecuteHighVolumeSettlementUnderVirtualThreads</span>() {{</div>
          <div>&nbsp;&nbsp;&nbsp;&nbsp;<span style="color:#f43f5e;">var</span> receipt = bankingEngine.<span style="color:#60a5fa;">processTransfer</span>(tx);</div>
          <div>&nbsp;&nbsp;&nbsp;&nbsp;<span style="color:#60a5fa;">assertThat</span>(receipt.<span style="color:#60a5fa;">isSettled</span>()).<span style="color:#60a5fa;">isTrue</span>();</div>
          <div>&nbsp;&nbsp;&nbsp;&nbsp;<span style="color:#60a5fa;">assertThat</span>(receipt.<span style="color:#60a5fa;">latencyMs</span>()).<span style="color:#60a5fa;">isLessThan</span>(<span style="color:#38bdf8;">2.0</span>);</div>
          <div>&nbsp;&nbsp;}}</div>
          <div>}}</div>
          <div style="margin-top:8px; color:#10b981; font-weight:700;">✔ 18,420 tests passed in 14.2s (0 failures, 0 skipped)</div>
        </div>

        <!-- Terminal Logs Slice -->
        <div style="background:#060913; border:1px solid rgba(255,255,255,0.06); border-radius:8px; padding:12px 14px; font-size:11px; line-height:1.65; color:#94a3b8; height:500px; display:flex; flex-direction:column; justify-content:space-between;">
          <div>
            <div style="color:#64748b; font-size:10px; margin-bottom:4px; text-transform:uppercase;">Maven Build &amp; Container Package</div>
            <div>[INFO] --- maven-clean-plugin:3.2.0:clean ---</div>
            <div>[INFO] --- maven-compiler-plugin:3.11.0:compile ---</div>
            <div>[INFO] Compiling 420 source files to target/classes</div>
            <div>[INFO] --- maven-surefire-plugin:3.2.0:test ---</div>
            <div>[INFO] Tests run: 18,420, Failures: 0, Errors: 0, Skipped: 0</div>
            <div>[INFO] --- spring-boot-maven-plugin:repackage ---</div>
            <div>[INFO] Replacing target/core-banking-21.0.jar</div>
            <div>[INFO] Container Image: ghcr.io/enterprise/banking:21.0 (Signed)</div>
            <div>[INFO] SBOM generated: target/classes/META-INF/sbom/application.cdx.json</div>
            <div><span style="color:#10b981; font-weight:700;">[INFO] BUILD SUCCESS (Total time: 14.218 s)</span></div>
          </div>
          <div style="background:#111a2e; padding:8px 10px; border-radius:6px; color:#38bdf8; font-size:10.5px;">
            Git: main [origin/main] ✔ Working tree clean (commit #4f82a1b)
          </div>
        </div>
      </div>
    </div>

    <!-- Right Screen: Production Dashboard (Fully Populated) -->
    <div class="screen">
      <div class="screen-header"><div class="screen-title">GRAFANA — PRODUCTION K8S CLUSTER</div><div class="screen-status">● 100% HEALTHY</div></div>
      <div class="screen-body">
        <div style="display:grid; grid-template-columns:1fr 1fr; gap:10px;">
          <div style="background:#111a2e; padding:10px 14px; border-radius:8px;"><div style="font-size:10px; color:#64748b; font-weight:700;">ACTIVE PODS</div><div style="font-size:22px; font-weight:700; color:#10b981;">256/256</div></div>
          <div style="background:#111a2e; padding:10px 14px; border-radius:8px;"><div style="font-size:10px; color:#64748b; font-weight:700;">SUCCESS RATE</div><div style="font-size:22px; font-weight:700; color:#38bdf8;">100.00%</div></div>
        </div>

        <div style="background:#111a2e; padding:12px 14px; border-radius:8px; display:flex; flex-direction:column; gap:6px;">
          <div style="display:flex; justify-content:space-between; align-items:center;">
            <span style="font-size:10.5px; color:#64748b; font-weight:700;">P99 LATENCY UNDER 500K RPS</span>
            <span style="font-size:11px; color:#10b981; font-weight:700;">1.84ms</span>
          </div>
          <svg style="width:100%; height:90px; background:#0a0f1d; border-radius:6px; padding:8px;">
            <line x1="0" y1="20" x2="450" y2="20" stroke="rgba(255,255,255,0.05)" stroke-width="1"/>
            <line x1="0" y1="45" x2="450" y2="45" stroke="rgba(255,255,255,0.05)" stroke-width="1"/>
            <line x1="0" y1="70" x2="450" y2="70" stroke="rgba(255,255,255,0.05)" stroke-width="1"/>
            <path d="M0,60 Q100,56 200,60 T350,59 T450,60" fill="none" stroke="#10b981" stroke-width="2.5"/>
            <path d="M0,60 Q100,56 200,60 T350,59 T450,60 L450,85 L0,85 Z" fill="rgba(16,185,129,0.12)"/>
          </svg>
          <div style="display:flex; justify-content:space-between; font-size:10px; color:#94a3b8;">
            <span>p50: <strong>0.35ms</strong></span><span>p95: <strong>1.12ms</strong></span><span>p99: <strong>1.84ms</strong></span>
          </div>
        </div>

        <div style="background:#111a2e; padding:12px 14px; border-radius:8px; display:flex; flex-direction:column; gap:6px; flex:1;">
          <div style="font-size:10.5px; color:#64748b; font-weight:700; margin-bottom:2px;">SERVICE MESH TOPOLOGY</div>
          <div style="display:flex; justify-content:space-between; font-size:11px; padding:3px 0; border-bottom:1px solid rgba(255,255,255,0.04);"><span>gateway-ingress (32 pods)</span><span style="color:#10b981; font-weight:700;">100% OK (0.4ms)</span></div>
          <div style="display:flex; justify-content:space-between; font-size:11px; padding:3px 0; border-bottom:1px solid rgba(255,255,255,0.04);"><span>banking-core (128 pods)</span><span style="color:#10b981; font-weight:700;">100% OK (1.2ms)</span></div>
          <div style="display:flex; justify-content:space-between; font-size:11px; padding:3px 0; border-bottom:1px solid rgba(255,255,255,0.04);"><span>payment-adapter (64 pods)</span><span style="color:#10b981; font-weight:700;">100% OK (0.8ms)</span></div>
          <div style="display:flex; justify-content:space-between; font-size:11px; padding:3px 0; border-bottom:1px solid rgba(255,255,255,0.04);"><span>fraud-engine (48 pods)</span><span style="color:#10b981; font-weight:700;">100% OK (1.1ms)</span></div>
          <div style="display:flex; justify-content:space-between; font-size:11px; padding:3px 0; border-bottom:1px solid rgba(255,255,255,0.04);"><span>kafka-brokers (12 nodes)</span><span style="color:#10b981; font-weight:700;">100% OK (0.2ms)</span></div>
          <div style="display:flex; justify-content:space-between; font-size:11px; padding:3px 0; border-bottom:1px solid rgba(255,255,255,0.04);"><span>postgres-cluster (3 nodes)</span><span style="color:#10b981; font-weight:700;">100% OK (0.9ms)</span></div>
          <div style="display:flex; justify-content:space-between; font-size:11px; padding:3px 0; border-bottom:1px solid rgba(255,255,255,0.04);"><span>redis-l2-cache (16 nodes)</span><span style="color:#10b981; font-weight:700;">100% OK (0.1ms)</span></div>
          <div style="display:flex; justify-content:space-between; font-size:11px; padding:3px 0;"><span>otel-collector (8 pods)</span><span style="color:#10b981; font-weight:700;">100% OK (0.3ms)</span></div>
          <div style="margin-top:auto; background:#0a0f1d; padding:8px 10px; border-radius:6px; font-size:10.5px; color:#10b981;">
            ● Production Cluster SLA: 99.9999% | Zero downtime in 365 days
          </div>
        </div>
      </div>
    </div>
  </div>
  <div class="desk-surface"></div><div class="desk-mat"></div>
  <div class="keyboard-frame">
    <div class="key-rows">
      <div class="key-row"><div class="key"></div><div class="key"></div><div class="key"></div><div class="key"></div><div class="key"></div><div class="key"></div><div class="key"></div><div class="key"></div><div class="key"></div><div class="key"></div><div class="key"></div><div class="key"></div><div class="key mod"></div></div>
      <div class="key-row"><div class="key mod"></div><div class="key"></div><div class="key"></div><div class="key"></div><div class="key"></div><div class="key"></div><div class="key"></div><div class="key"></div><div class="key"></div><div class="key"></div><div class="key"></div><div class="key"></div><div class="key mod"></div></div>
      <div class="key-row"><div class="key mod"></div><div class="key"></div><div class="key"></div><div class="key"></div><div class="key"></div><div class="key"></div><div class="key"></div><div class="key"></div><div class="key"></div><div class="key"></div><div class="key"></div><div class="key accent"></div></div>
      <div class="key-row"><div class="key mod"></div><div class="key"></div><div class="key"></div><div class="key"></div><div class="key"></div><div class="key"></div><div class="key"></div><div class="key"></div><div class="key"></div><div class="key"></div><div class="key mod"></div></div>
      <div class="key-row"><div class="key mod"></div><div class="key mod"></div><div class="key mod"></div><div class="key space"></div><div class="key mod"></div><div class="key mod"></div><div class="key mod"></div></div>
    </div>
  </div>
  <div class="wrist-rest"></div>
  <div class="mouse"><div class="mouse-wheel"></div></div><div class="coffee-mug"></div>
  <div class="subtitle-vignette"></div>
</body></html>
"""
render(html_scene7, "scene-07-conclusion.png")
print("\nAll 7 Masterpiece scenes rendered successfully with zero empty voids!")
