param(
    [Parameter(Mandatory=$true)]
    [string]$RootDirectory
)

# Check if the directory exists
if (-not (Test-Path -Path $RootDirectory -PathType Container)) {
    Write-Error "Error: $RootDirectory is not a directory"
    exit 1
}

$removedCount = 0

# Find all passed.md files and remove their parent directories
Get-ChildItem -Path $RootDirectory -Filter "passed.md" -Recurse | ForEach-Object {
    $testDir = $_.Directory
    Write-Host "Removing passed test directory: $testDir"
    Remove-Item -Path $testDir -Recurse -Force
    $removedCount++
}

Write-Host "`nRemoved $removedCount directories with passed tests"
