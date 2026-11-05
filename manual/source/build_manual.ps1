# 사용설명서 다시 만들기 (PowerShell 에서 실행)
#   -Capture : 앱 화면 스크린샷도 새로 찍는다 (UI를 바꿨을 때)
param([switch]$Capture)
$ErrorActionPreference = "Stop"
$src = $PSScriptRoot
$proj = Split-Path (Split-Path $src)
$manual = Split-Path $src

if (-not (Test-Path "$src\node_modules\pptxgenjs")) {
    Push-Location -LiteralPath $src; npm install; Pop-Location
}
if ($Capture) {
    py "$src\capture_app.py" "$proj" "$src\shots"
    py "$src\blur_shots.py" "$src\shots"
}

$env:NODE_PATH = "$src\node_modules"
$pptx = "$src\manual.pptx"; $pdf = "$src\manual.pdf"
node "$src\build_deck.js" "$src\shots" $pptx
& "$src\export.ps1" -Pptx $pptx -Pdf $pdf -PngDir "$src\png"

Copy-Item $pptx "$manual\갤럭시 카메라 무음 사용설명서.pptx" -Force
Copy-Item $pdf "$manual\갤럭시 카메라 무음 사용설명서.pdf" -Force
Write-Host "완료: $manual"
