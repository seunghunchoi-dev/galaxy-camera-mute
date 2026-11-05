param([string]$Pptx, [string]$Pdf, [string]$PngDir)
$pp = New-Object -ComObject PowerPoint.Application
try {
    $p = $pp.Presentations.Open($Pptx, $true, $false, $false)
    $p.SaveAs($Pdf, 32)
    if ($PngDir) {
        New-Item -ItemType Directory -Force $PngDir | Out-Null
        Get-ChildItem $PngDir -Filter *.png | Remove-Item
        for ($i = 1; $i -le $p.Slides.Count; $i++) {
            $p.Slides.Item($i).Export((Join-Path $PngDir ("s{0:D2}.png" -f $i)), "PNG", 1600, 900)
        }
    }
    "slides=" + $p.Slides.Count
    $p.Close()
} finally {
    $pp.Quit()
    [System.Runtime.InteropServices.Marshal]::ReleaseComObject($pp) | Out-Null
}
