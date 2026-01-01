Here is the updated, complete script and the setup guide for your future Linux installations.

Part 1: Quick Install Commands
Run these on any new machine to prepare the environment:

# 1. Install dependencies
sudo apt update && sudo apt install zsh curl git fzf -y

# 2. Install Oh My Posh
curl -s https://ohmyposh.dev/install.sh | sudo bash -s -- -d /usr/local/bin

# 3. Setup Plugins
mkdir -p ~/.zsh/plugins
git clone https://github.com/zsh-users/zsh-autosuggestions ~/.zsh/plugins/zsh-autosuggestions

# 4. Create History File
touch ~/.zsh_history && chmod 600 ~/.zsh_history


Part 2: The Final .zshrc Script:

# ------------------------------------------------------------------------------
# 1. ENVIRONMENT PATHS
# ------------------------------------------------------------------------------
export PATH=$PATH:/usr/local/bin:$HOME/bin

# ------------------------------------------------------------------------------
# 2. HISTORY CONFIGURATION
# ------------------------------------------------------------------------------
HISTFILE=$HOME/.zsh_history
HISTSIZE=10000
SAVEHIST=10000

setopt INC_APPEND_HISTORY
setopt SHARE_HISTORY 
setopt HIST_IGNORE_DUPS
setopt HIST_EXPIRE_DUPS_FIRST

# ------------------------------------------------------------------------------
# 3. PLUGINS & EXTENSIONS
# ------------------------------------------------------------------------------
source ~/.zsh/plugins/zsh-autosuggestions/zsh-autosuggestions.zsh
export ZSH_AUTOSUGGEST_HIGHLIGHT_STYLE="fg=cyan"

# Load FZF (Fuzzy Finder) key bindings
[ -f /usr/share/doc/fzf/examples/key-bindings.zsh ] && source /usr/share/doc/fzf/examples/key-bindings.zsh

# ------------------------------------------------------------------------------
# 4. USEFUL ALIASES (Shortcuts)
# ------------------------------------------------------------------------------
# System Updates
alias update='sudo apt update && sudo apt upgrade -y'
alias clean='sudo apt autoremove -y && sudo apt autoclean'

# Navigation & Listing
alias ..='cd ..'
alias ...='cd ../..'
alias ll='ls -lah' # Detailed list with hidden files
alias la='ls -A'   # List all except . and ..

# Quick Edit Configuration
alias zconf='nano ~/.zshrc'
alias zreload='source ~/.zshrc'

# ------------------------------------------------------------------------------
# 5. COMPLETION & SELECTION MENU
# ------------------------------------------------------------------------------
autoload -Uz compinit
compinit

zstyle ':completion:*' menu select
zstyle ':completion:*' matcher-list 'm:{a-z}={A-Z}'

bindkey '^[[A' up-line-or-search
bindkey '^[[B' down-line-or-search

# ------------------------------------------------------------------------------
# 6. PROMPT CUSTOMIZATION (Oh My Posh)
# ------------------------------------------------------------------------------
eval "$(oh-my-posh init zsh --config https://raw.githubusercontent.com/JanDeDobbeleer/oh-my-posh/main/themes/atomic.omp.json)"


Part 3:
How to use your new Aliases
- update: Instead of typing the whole update and upgrade string, just type update.

- zconf: Quickly opens this file so you can add more themes or plugins.

- zreload: Apply changes instantly after editing your config.

- ll: The standard way to see file sizes and permissions clearly.


Final Step:
Don't forget to set Zsh as default:

sudo chsh -s $(which zsh) $USER 

Then restart your computer (or log out and back in) to finalize the shell change.
