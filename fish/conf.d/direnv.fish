if status is-interactive
    if command -v direnv >/dev/null 2>&1
        direnv hook fish | source
    end
end
