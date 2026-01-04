# 1. Prompt (Oh My Posh with Atomic theme)
oh-my-posh init pwsh --config https://raw.githubusercontent.com/JanDeDobbeleer/oh-my-posh/main/themes/atomic.omp.json | Invoke-Expression

# 2. Key Plugins (Prediction & Completion)
# This simulates zsh-autosuggestions
Import-Module PSReadLine
Set-PSReadLineOption -PredictionSource History
Set-PSReadLineOption -PredictionViewStyle ListView

# 3. Aliases (Matching your Linux/Mac environment)
Set-Alias -Name ll -Value ls
function update-all {
    winget upgrade --all
}

# DevOps Jump commands
function lab { Set-Location ~/lab }
function gpush { git push origin main }
function gpull { git pull origin main }

# Kubernetes & Docker (Shortcuts)
function k { kubectl $args }
function kgp { kubectl get pods $args }
function dps { docker ps $args }

# 4. Utilities
function zconf { notepad $PROFILE }
function zreload { . $PROFILE }