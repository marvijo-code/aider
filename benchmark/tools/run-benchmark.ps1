param(
    [Parameter(Mandatory=$true)]
    [string]$TestPath="say",
    [string]$CondaEnv = "aider-dev",
    [Parameter(Mandatory=$true)]
    [string]$Model = "deepseek/deepseek-coder",
    [string]$EditFormat = "diff",
    [int]$Threads = 1
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
    $env:AIDER_BENCHMARK_DIR = "tmp.benchmarks"
    $env:AIDER_RUN_LOCALLY = "true"
    python benchmark/benchmark.py $runName --model $Model --edit-format $EditFormat --threads $Threads

    # Generate stats
    Write-Host "Generating benchmark stats..."
    python benchmark/benchmark.py --stats "tmp.benchmarks/${runName}"

    Write-Host "Benchmark complete! Results are in tmp.benchmarks/${runName}"
    Write-Host "You can view the stats by running: python benchmark/benchmark.py --stats tmp.benchmarks/${runName}"
    exit 0
}

# Rest of the original script for single test...
$fullTestPath = Join-Path "tmp.benchmarks/exercism-python" $TestPath
if (!(Test-Path $fullTestPath)) {
    Write-Error "Test path not found: $fullTestPath"
    Write-Error "Please provide a path relative to tmp.benchmarks/exercism-python/"
    Write-Error "Example: .\run-test.ps1 -TestPath 'hello-world'"
    exit 1
}

# Get timestamp for benchmark run name
$timestamp = Get-Date -Format "yyyy-MM-dd-HH-mm-ss"
$testName = Split-Path $TestPath -Leaf
$runName = "${timestamp}--${testName}-${Model}-${EditFormat}"

# Create a temporary directory for this test
$testDir = Join-Path "tmp.benchmarks" $runName
New-Item -ItemType Directory -Path $testDir | Out-Null

# Copy only the specific test to the temporary directory
Copy-Item -Path $fullTestPath -Destination $testDir -Recurse

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
Write-Host "Running test: $TestPath"
Write-Host "Using model: $Model"
Write-Host "Edit format: $EditFormat"

$env:AIDER_BENCHMARK_DIR = "tmp.benchmarks"
$env:AIDER_RUN_LOCALLY = "true"
python benchmark/benchmark.py $runName --model $Model --edit-format $EditFormat --threads $Threads --keywords $testName

# Generate stats
Write-Host "Generating test stats..."
python benchmark/benchmark.py --stats "tmp.benchmarks/${runName}"

Write-Host "Test complete! Results are in tmp.benchmarks/${runName}"
Write-Host "You can view the stats by running: python benchmark/benchmark.py --stats tmp.benchmarks/${runName}" 