# Prepare for benchmarking
git clone git@github.com:exercism/python.git

Copy-Item -Path 'python/exercises/practice' -Destination 'tmp.benchmarks/exercism-python' -Recurse -Force

## Package exercism python repo into a text file:

repomix --remote https://github.com/exercism/python --include exercises/practice -o .aider.repo.log --ignore "**/.approaches,**/.articles,**/.meta,**/introduction.md"

repomix --include "aider" -o .aider.repo.log --ignore "**/website"

Get-Content .aider.repo.log | Select-Object -First 10000 | Out-File .aider.repo.log

.\run-benchmark.ps1 -Model openrouter/qwen/qwen-2.5-coder-32b-instruct -TestPath "say"

.\run-benchmark.ps1 -Model openrouter/qwen/qwen-2.5-coder-32b-instruct -TestPath "all-your-base"

.\run-benchmark.ps1 -Model openrouter/qwen/qwen-2.5-coder-32b-instruct -NumTests 5  

python -m unittest C:\dev\aider\benchmark\tools\tmp.benchmarks\2024-12-21-02-24-18--rest-api-openrouter\qwen\qwen-2.5-coder-32b-instruct-diff\rest-api\rest_api_test.py

python -m unittest discover -s "C:\dev\aider\benchmark\tools\tmp.benchmarks\2024-12-21-02-24-18--rest-api-openrouter\qwen\qwen-2.5-coder-32b-instruct-diff\rest-api" -t "C:\dev\aider\benchmark\tools\tmp.benchmarks\2024-12-21-02-24-18--rest-api-openrouter\qwen\qwen-2.5-coder-32b-instruct-diff\rest-api" -p rest_api_test.py

python -m unittest discover -s benchmark -t benchmark -p *_test.py


python -m unittest discover -s tmp.benchmarks\2024-12-21-02-33-53--rest-api-openrouter\qwen\qwen-2.5-coder-32b-instruct-diff\rest-api -t tmp.benchmarks\2024-12-21-02-33-53--rest-api-openrouter\qwen\qwen-2.5-coder-32b-instruct-diff\rest-api -p *_test.py

aider --model openrouter/qwen/qwen-2.5-coder-32b-instruct --apply-clipboard-edits
python -m unittest discover -s . -t . -p *_test.py

.\run-benchmark.ps1 -Model openrouter/qwen/qwen-2.5-coder-32b-instruct -TestPath "rest-api"
