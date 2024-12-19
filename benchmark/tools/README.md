Package exercism python repo into a text file:
repomix --remote https://github.com/exercism/python --include exercises/practice -o .aider.repo.log --ignore "**/.approaches,**/.articles,**/.meta,**/introduction.md"

Get-Content .aider.repo.log | Select-Object -First 10000 | Out-File .aider.repo.log