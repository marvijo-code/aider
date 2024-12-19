# Prepare for benchmarking
git clone git@github.com:exercism/python.git
Copy-Item -Path 'python/exercises/practice' -Destination 'tmp.benchmarks/exercism-python' -Recurse -Force

## Package exercism python repo into a text file:

repomix --remote https://github.com/exercism/python --include exercises/practice -o .aider.repo.log --ignore "**/.approaches,**/.articles,**/.meta,**/introduction.md"

Get-Content .aider.repo.log | Select-Object -First 10000 | Out-File .aider.repo.log

.\run-benchmark.ps1 -Model openrouter/qwen/qwen-2.5-coder-32b-instruct -TestPath "say"