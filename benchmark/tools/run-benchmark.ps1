param(
    [Parameter(Mandatory=$false)]
    [string]$TestPath="default",
    [string]$CondaEnv = "aider-dev",
    [Parameter(Mandatory=$true)]
    [string]$Model = "openrouter/Qwen/Qwen-2.5-coder-32b-instruct",
    [string]$EditFormat = "diff",
    [int]$Threads = 1,
    [int]$NumTests = -1
)

# Stop on any error
$ErrorActionPreference = "Stop"

# Check if .env file exists and load it
if (!(Test-Path .env)) {
    Write-Error ".env file not found. Please create a .env file with your API keys."
    exit 1
}

if ($TestPath -eq "all") {
    # Get timestamp for benchmark run name
    $timestamp = Get-Date -Format "yyyy-MM-dd-HH-mm-ss"
    $runName = "${timestamp}--${Model}-${EditFormat}"

    Write-Host "Running all tests..."
    Write-Host "Using model: $Model"
    Write-Host "Edit format: $EditFormat"
    Write-Host "Threads: $Threads"

    Write-Host "Activating $CondaEnv conda environment..."
    conda activate $CondaEnv

    # Set environment variables from .env file
    Get-Content .env | ForEach-Object {
        if ($_ -match '^([^=]+)=(.*)$') {
            $key = $matches[1]
            $value = $matches[2]
            [Environment]::SetEnvironmentVariable($key, $value)
        }
    }

    # Run all benchmarks (no need to copy files as benchmark.py handles it)
    $env:AIDER_BENCHMARK_DIR = (Resolve-Path (Join-Path $PSScriptRoot "tmp.benchmarks")).Path
    $env:AIDER_RUN_LOCALLY = "true"
    python benchmark/benchmark.py "tmp.benchmarks/${runName}" --model $Model --edit-format $EditFormat --threads $Threads

    # Generate stats
    Write-Host "Generating benchmark stats..."
    python benchmark/benchmark.py --stats "tmp.benchmarks/${runName}"

    Write-Host "Benchmark complete! Results are in tmp.benchmarks/${runName}"
    Write-Host "You can view the stats by running: python benchmark/benchmark.py --stats tmp.benchmarks/${runName}"
    exit 0
}

# Rest of the original script for single test...
$fullTestPath = Join-Path "tmp.benchmarks/exercism-python" $TestPath
if (!$NumTests -gt 0 -and !(Test-Path $fullTestPath)) {
    Write-Error "Test path not found: $fullTestPath"
    Write-Error "Please provide a path relative to tmp.benchmarks/exercism-python/"
    Write-Error "Example: .\run-test.ps1 -TestPath 'hello-world'"
    exit 1
}

# Get timestamp for benchmark run name
$timestamp = Get-Date -Format "yyyy-MM-dd-HH-mm-ss"
$testName = Split-Path $TestPath -Leaf
$runName = "${timestamp}--${testName}-${Model}-${EditFormat}"

# Define the temporary directory path
$testDir = Join-Path "tmp.benchmarks" $runName

# Copy only the specific test to the temporary directory if not using num-tests
if ($NumTests -le 0) {
    # Create directory only when we need to copy a specific test
    New-Item -ItemType Directory -Path $testDir | Out-Null
    Copy-Item -Path $fullTestPath -Destination $testDir -Recurse
}

Write-Host "Activating $CondaEnv conda environment..."
conda activate $CondaEnv

# Set environment variables from .env file
Get-Content .env | ForEach-Object {
    if ($_ -match '^([^=]+)=(.*)$') {
        $key = $matches[1]
        $value = $matches[2]
        [Environment]::SetEnvironmentVariable($key, $value)
    }
}

# Run the benchmark
Write-Host "Running test: $(if ($NumTests -ne -1) { 'all (filtered by num-tests)' } else { $TestPath })"
Write-Host "Using model: $Model"
Write-Host "Edit format: $EditFormat"
Write-Host "Number of tests: $(if ($NumTests -eq -1) { 'all' } else { $NumTests })"

$env:AIDER_BENCHMARK_DIR = (Resolve-Path (Join-Path $PSScriptRoot "tmp.benchmarks")).Path
$env:AIDER_RUN_LOCALLY = "true"
$env:AIDER_DOCKER = 1
if ($NumTests -ne -1) {
    python ../benchmark.py "tmp.benchmarks/${runName}" --model $Model --edit-format $EditFormat --threads $Threads --num-tests $NumTests
} else {
    python ../benchmark.py "tmp.benchmarks/${runName}" --model $Model --edit-format $EditFormat --threads $Threads --keywords $TestPath
}

# Generate stats
Write-Host "Generating test stats..."
python ../benchmark.py --stats "tmp.benchmarks/${runName}"

Write-Host "Test complete! Results are in tmp.benchmarks/${runName}"
Write-Host "You can view the stats by running: python ../benchmark.py --stats tmp.benchmarks/${runName}" 