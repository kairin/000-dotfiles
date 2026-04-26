function direnv --description "direnv wrapper that locks .envrc after allow"
    if test "$argv[1]" = "allow"
        command direnv allow $argv[2..]
        if test -f .envrc
            chmod 444 .envrc
            and sudo chattr +i .envrc
            and echo "direnv: .envrc locked (chmod 444 + chattr +i)"
            or echo "direnv: .envrc chmod 444 applied (chattr +i requires sudo)"
        end
    else
        command direnv $argv
    end
end
