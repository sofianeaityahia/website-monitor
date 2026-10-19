"""
Website Uptime & Latency Monitor
Runs automated health checks on target websites and generates a modern status dashboard.
"""
import time
import json
from datetime import datetime, timezone
import urllib.request
import urllib.error

TARGETS = [
    {"name": "GitHub", "url": "https://github.com", "category": "Developer Tools"},
    {"name": "Google", "url": "https://www.google.com", "category": "Search & Web"},
    {"name": "Cloudflare DNS", "url": "https://1.1.1.1", "category": "Infrastructure"},
    {"name": "Wikipedia", "url": "https://www.wikipedia.org", "category": "Content & Knowledge"},
    {"name": "Python.org", "url": "https://www.python.org", "category": "Software & Language"},
]

def check_site(target):
    name = target["name"]
    url = target["url"]
    category = target["category"]
    
    start_time = time.time()
    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) GitHub-Action-Uptime-Bot/1.0"}
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            latency_ms = round((time.time() - start_time) * 1000, 2)
            code = response.getcode()
            status = "Operational" if code in [200, 301, 302] else "Degraded"
            return {
                "name": name,
                "url": url,
                "category": category,
                "status": status,
                "code": code,
                "latency_ms": latency_ms,
                "error": None
            }
    except urllib.error.HTTPError as e:
        latency_ms = round((time.time() - start_time) * 1000, 2)
        return {
            "name": name,
            "url": url,
            "category": category,
            "status": "Degraded",
            "code": e.code,
            "latency_ms": latency_ms,
            "error": str(e.reason)
        }
    except Exception as e:
        latency_ms = round((time.time() - start_time) * 1000, 2)
        return {
            "name": name,
            "url": url,
            "category": category,
            "status": "Down",
            "code": 0,
            "latency_ms": latency_ms,
            "error": str(e)
        }

def generate_dashboard(results, check_time_iso):
    total = len(results)
    operational = sum(1 for r in results if r["status"] == "Operational")
    uptime_pct = round((operational / total) * 100, 1) if total > 0 else 100
    avg_latency = round(sum(r["latency_ms"] for r in results) / total, 1) if total > 0 else 0
    all_ok = operational == total

    banner_color = "bg-emerald-500/10 border-emerald-500/20 text-emerald-400" if all_ok else "bg-amber-500/10 border-amber-500/20 text-amber-400"
    banner_icon = "✓" if all_ok else "⚠"
    banner_text = "All Systems Fully Operational" if all_ok else f"{total - operational} Service(s) Experiencing Issues"

    cards_html = ""
    for r in results:
        status = r["status"]
        if status == "Operational":
            badge_class = "bg-emerald-500/10 text-emerald-400 border border-emerald-500/30"
            dot_class = "bg-emerald-400"
        elif status == "Degraded":
            badge_class = "bg-amber-500/10 text-amber-400 border border-amber-500/30"
            dot_class = "bg-amber-400"
        else:
            badge_class = "bg-rose-500/10 text-rose-400 border border-rose-500/30"
            dot_class = "bg-rose-400"

        cards_html += f"""
        <div class="p-5 rounded-2xl bg-slate-900/60 border border-slate-800 hover:border-slate-700 transition-all flex flex-col justify-between">
            <div class="flex items-center justify-between mb-4">
                <div>
                    <span class="text-xs font-medium text-slate-400 uppercase tracking-wider">{r['category']}</span>
                    <h3 class="text-lg font-semibold text-white mt-0.5">{r['name']}</h3>
                    <a href="{r['url']}" target="_blank" class="text-xs text-sky-400 hover:underline">{r['url']}</a>
                </div>
                <span class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold {badge_class}">
                    <span class="w-2 h-2 rounded-full {dot_class} animate-pulse"></span>
                    {r['status']}
                </span>
            </div>
            <div class="pt-4 border-t border-slate-800/80 flex items-center justify-between text-xs text-slate-400">
                <span>Response Time: <strong class="text-slate-200 font-mono text-sm">{r['latency_ms']} ms</strong></span>
                <span>HTTP Code: <strong class="text-slate-200 font-mono">{r['code']}</strong></span>
            </div>
        </div>
        """

    html = f"""<!DOCTYPE html>
<html lang="en" class="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Live Website Uptime Monitor</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        body {{ font-family: 'Plus Jakarta Sans', sans-serif; }}
    </style>
</head>
<body class="bg-slate-950 text-slate-100 min-h-screen py-10 px-4 sm:px-6 lg:px-8">
    <div class="max-w-5xl mx-auto space-y-8">
        
        <!-- Header -->
        <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 border-b border-slate-800 pb-6">
            <div>
                <div class="flex items-center gap-2">
                    <span class="inline-flex items-center justify-center w-8 h-8 rounded-lg bg-sky-500/10 text-sky-400 border border-sky-500/20 font-bold">⚡</span>
                    <h1 class="text-2xl sm:text-3xl font-bold tracking-tight text-white">Live Website Uptime Monitor</h1>
                </div>
                <p class="text-sm text-slate-400 mt-1">Automated health & latency monitoring powered by GitHub Actions Runner</p>
            </div>
            <div class="text-right">
                <span class="text-xs text-slate-500 block">Server Runner Time (UTC)</span>
                <span class="text-xs font-mono text-slate-300 font-semibold">{check_time_iso}</span>
            </div>
        </div>

        <!-- Status Banner -->
        <div class="p-4 rounded-xl border {banner_color} flex items-center justify-between">
            <div class="flex items-center gap-3">
                <span class="text-xl font-bold">{banner_icon}</span>
                <span class="font-semibold text-sm sm:text-base">{banner_text}</span>
            </div>
            <span class="text-xs opacity-80">Auto-checked on GitHub Linux Server</span>
        </div>

        <!-- Metric Summary Cards -->
        <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div class="p-5 rounded-2xl bg-slate-900/60 border border-slate-800">
                <span class="text-xs text-slate-400 uppercase font-medium">Global Uptime</span>
                <p class="text-3xl font-bold text-emerald-400 mt-1 font-mono">{uptime_pct}%</p>
                <span class="text-xs text-slate-500 mt-1 block">{operational} of {total} targets operational</span>
            </div>
            <div class="p-5 rounded-2xl bg-slate-900/60 border border-slate-800">
                <span class="text-xs text-slate-400 uppercase font-medium">Average Response Time</span>
                <p class="text-3xl font-bold text-sky-400 mt-1 font-mono">{avg_latency} ms</p>
                <span class="text-xs text-slate-500 mt-1 block">Worldwide CDN & DNS endpoints</span>
            </div>
            <div class="p-5 rounded-2xl bg-slate-900/60 border border-slate-800">
                <span class="text-xs text-slate-400 uppercase font-medium">Hosted Environment</span>
                <p class="text-3xl font-bold text-indigo-400 mt-1 font-mono">GitHub Pro</p>
                <span class="text-xs text-slate-500 mt-1 block">Ubuntu Runner + GitHub Pages</span>
            </div>
        </div>

        <!-- Target Site Cards -->
        <div>
            <h2 class="text-lg font-semibold text-white mb-4">Monitored Endpoints</h2>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                {cards_html}
            </div>
        </div>

        <!-- Footer -->
        <div class="pt-8 border-t border-slate-800/80 text-center text-xs text-slate-500 flex flex-col sm:flex-row items-center justify-between gap-2">
            <span>Built & Deployed on GitHub Infrastructure • Open Source</span>
            <a href="https://github.com/sofianeaityahia/website-monitor" target="_blank" class="text-sky-400 hover:underline">View Repository on GitHub →</a>
        </div>

    </div>
</body>
</html>
"""
    return html

def main():
    print("============================================================")
    print("Starting Website Uptime & Latency Check on Server...")
    print("============================================================")
    
    results = []
    for target in TARGETS:
        print(f"Checking {target['name']} ({target['url']})...", end=" ", flush=True)
        res = check_site(target)
        status_icon = "[OK]" if res["status"] == "Operational" else "[ERR]"
        print(f"{status_icon} {res['status']} | {res['latency_ms']} ms (HTTP {res['code']})")
        results.append(res)
        time.sleep(0.2)

    now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    # Save JSON data
    data = {
        "timestamp": now_iso,
        "results": results
    }
    with open("status.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print("\n[+] status.json generated successfully.")

    # Generate HTML Dashboard
    html_content = generate_dashboard(results, now_iso)
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    print("[+] index.html dashboard generated successfully.")
    
    print("============================================================")
    print("All checks complete! Ready for deployment to GitHub Pages.")
    print("============================================================")

if __name__ == "__main__":
    main()
