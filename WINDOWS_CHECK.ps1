# WINDOWS_CHECK.ps1 — Gnani Kirana Voice Agent, Windows diagnostic
# Run this in PowerShell from the repo root (the folder that contains backend\).
# It does NOT print your API key. It only says whether a key looks set or not.
# Copy the whole output and send it to the assistant — key never included.

$ErrorActionPreference = "Continue"
Write-Host "=== Gnani Kirana — Windows check ==="
Write-Host ""

# 1. Where are we, and is the server folder here?
Write-Host "Folder: $((Get-Location).Path)"
if (Test-Path "backend\app\main.py") { Write-Host "backend folder: FOUND" } else { Write-Host "backend folder: NOT FOUND — run this script from the repo root (gnani-kirana-voice-agent)" }

# 2. Python and uvicorn
try { $py = (python --version) 2>&1; Write-Host "python: $py" } catch { Write-Host "python: NOT FOUND" }
try { $uv = (uvicorn --version) 2>&1; Write-Host "uvicorn: $uv" } catch { Write-Host "uvicorn: NOT FOUND (run: pip install -r backend\requirements.txt)" }

# 3. Is anything listening on port 8000?
$port8000 = Get-NetTCPConnection -LocalPort 8000 -State Listen -ErrorAction SilentlyContinue
if ($port8000) { Write-Host "Port 8000: LISTENING (server process looks running)" } else { Write-Host "Port 8000: NOT LISTENING — server is not running. Start it with: cd backend; uvicorn app.main:app --reload --port 8000" }

# 4. Health check — this is the step that tells mock vs real mode
try {
    $health = Invoke-RestMethod -Uri "http://127.0.0.1:8000/health" -TimeoutSec 10
    Write-Host "Health: OK"
    Write-Host "  status: $($health.status)"
    Write-Host "  mock_mode: $($health.mock_mode)"
} catch {
    Write-Host "Health: FAILED — $($_.Exception.Message)"
    Write-Host "  (If the server window was closed, restart it first. If the port is in use, use --port 8001 and change the URLs below to 8001.)"
}

# 5. Products check
try {
    $products = Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/products" -TimeoutSec 10
    Write-Host "Products: OK — $($products.products.Count) items returned (shop: $($products.shop_name))"
} catch {
    Write-Host "Products: FAILED — $($_.Exception.Message)"
}

# 6. Mock order check (no key needed, no real Gnani call)
try {
    $body = @{ text = "2 kg atta aur 1 litre tel chahiye" } | ConvertTo-Json
    $order = Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/text-order" -Method Post -ContentType "application/json" -Body $body -TimeoutSec 15
    Write-Host "Mock order: OK — total Rs $($order.total)"
} catch {
    Write-Host "Mock order: FAILED — $($_.Exception.Message)"
}

# 7. .env check — key presence only, NEVER the value
if (Test-Path "backend\.env") {
    $envText = Get-Content "backend\.env" -Raw
    if ($envText -match "GNANI_MOCK_MODE\s*=\s*false") { Write-Host ".env: mock mode is OFF (real Gnani mode)" } else { Write-Host ".env: mock mode is ON (or not set to false)" }
    if ($envText -match "GNANI_API_KEY\s*=\s*(\S+)") {
        $val = $Matches[1]
        if ($val -eq "<redacted>" -or $val -eq "" -or $val -like "*your*key*") { Write-Host ".env: API key looks EMPTY / placeholder — real mode will fail with 502 until a real key is put in .env only" } else { Write-Host ".env: API key looks SET (value not shown here)" }
    } else { Write-Host ".env: no GNANI_API_KEY line found" }
} else {
    Write-Host ".env: NOT FOUND — mock mode is expected; for real mode, copy backend\.env.example to backend\.env first"
}

Write-Host ""
Write-Host "=== Done. Copy everything above and send it — do NOT add your key. ==="
