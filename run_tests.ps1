Write-Host "Maya-AE Bridge Test Suite" -ForegroundColor Cyan
Write-Host "=" * 60

$mayaPaths = @(
    "C:\Program Files\Autodesk\Maya2025\bin\mayapy.exe",
    "C:\Program Files\Autodesk\Maya2024\bin\mayapy.exe",
    "C:\Program Files\Autodesk\Maya2023\bin\mayapy.exe"
)

$mayapy = $null
foreach ($path in $mayaPaths) {
    if (Test-Path $path) {
        $mayapy = $path
        $version = [regex]::Match($path, 'Maya(\d+)').Groups[1].Value
        Write-Host "Using Maya $version" -ForegroundColor Green
        break
    }
}

if (-not $mayapy) {
    Write-Host "ERROR: Maya not found" -ForegroundColor Red
    exit 1
}

$tests = @(
    "tests\test_serializer.py",
    "tests\test_scene_reader.py",
    "tests\test_aov_manager.py"
)

$totalPassed = 0
$totalFailed = 0

foreach ($test in $tests) {
    if (Test-Path $test) {
        Write-Host "`nRunning $test..." -ForegroundColor Yellow
        & $mayapy $test
        
        if ($LASTEXITCODE -eq 0) {
            $totalPassed++
            Write-Host "✓ $test PASSED" -ForegroundColor Green
        } else {
            $totalFailed++
            Write-Host "✗ $test FAILED" -ForegroundColor Red
        }
    } else {
        Write-Host "⚠ $test not found" -ForegroundColor Yellow
    }
}

Write-Host "`n" + "=" * 60
Write-Host "Test Summary" -ForegroundColor Cyan
Write-Host "Passed: $totalPassed" -ForegroundColor Green
Write-Host "Failed: $totalFailed" -ForegroundColor Red
Write-Host "=" * 60

if ($totalFailed -eq 0) {
    Write-Host "`n✓ All tests passed!" -ForegroundColor Green
    exit 0
} else {
    Write-Host "`n✗ Some tests failed" -ForegroundColor Red
    exit 1
}