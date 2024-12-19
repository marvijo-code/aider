param(
    [Parameter(Mandatory=$true)]
    [string]$Model,
    [string]$EditFormat = "diff",
    [int]$Threads = 10
)

# Stop on any error
$ErrorActionPreference = "Stop"

# Check if Git is installed
if (!(Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Error "Git is not installed. Please install Git first."
    exit 1
}

# Check if Docker is installed and running
if (!(Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Error "Docker is not installed. Please install Docker first."
    exit 1
}

try {
    docker info | Out-Null
} catch {
    Write-Error "Docker is not running. Please start Docker first."
    exit 1
}

# Check if .env file exists
if (!(Test-Path .env)) {
    Write-Error ".env file not found. Please create a .env file with your API keys."
    exit 1
}

# Create directories if they don't exist
if (!(Test-Path tmp.benchmarks)) {
    New-Item -ItemType Directory -Path tmp.benchmarks
}

# Clone repositories if they don't exist
if (!(Test-Path python)) {
    Write-Host "Cloning Exercism Python repository..."
    git clone https://github.com/exercism/python.git
}

# Copy practice exercises to benchmark directory
Write-Host "Copying practice exercises..."
if (!(Test-Path tmp.benchmarks/exercism-python)) {
    Copy-Item -Path "python/exercises/practice" -Destination "tmp.benchmarks/exercism-python" -Recurse
}

# Build Docker container
Write-Host "Building Docker container..."
docker build --file benchmark/Dockerfile -t aider-benchmark .

# Get timestamp for benchmark run name
$timestamp = Get-Date -Format "yyyy-MM-dd-HH-mm-ss"
$runName = "${timestamp}--${Model}-${EditFormat}"

# Run the benchmark in Docker
Write-Host "Running benchmark..."
docker run `
    --rm `
    -v "${PWD}:/aider" `
    -v "${PWD}/tmp.benchmarks/.:/benchmarks" `
    --env-file .env `
    -e HISTFILE=/aider/.bash_history `
    -e AIDER_DOCKER=1 `
    -e AIDER_BENCHMARK_DIR=/benchmarks `
    aider-benchmark `
    /bin/bash -c "pip install -e . && ./benchmark/benchmark.py $runName --model $Model --edit-format $EditFormat --threads $Threads"

# Generate stats
Write-Host "Generating benchmark stats..."
docker run `
    --rm `
    -v "${PWD}:/aider" `
    -v "${PWD}/tmp.benchmarks/.:/benchmarks" `
    -e AIDER_BENCHMARK_DIR=/benchmarks `
    aider-benchmark `
    /bin/bash -c "./benchmark/benchmark.py --stats /benchmarks/${runName}"

Write-Host "Benchmark complete! Results are in tmp.benchmarks/${runName}"
Write-Host "You can view the stats by running: ./benchmark/benchmark.py --stats tmp.benchmarks/${runName}"
