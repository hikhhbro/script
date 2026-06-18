__file_sw=''

_hikrun_ls_color_entry() {
    local key="$1"
    local code="${LS_COLORS#*$key=}"

    if [[ "$code" == "$LS_COLORS" ]]; then
        code=""
    else
        code="${code%%:*}"
    fi
    printf '%s' "$code"
}

_hikrun_ls_color_code() {
    local source_path="$1"
    local code=""

    # Python tools are exposed as short hikrun commands but backed by
    # src/utils/*.py. Use a fixed colour so they never look like dirs or shell.
    if [[ "$source_path" == "${SCRIPT_TOP_DIR}/src/utils/"*.py ]]; then
        printf '%s' "01;38;5;196"
        return
    fi

    if [[ -d "$source_path" ]]; then
        code="$(_hikrun_ls_color_entry di)"
    elif [[ -L "$source_path" ]]; then
        code="$(_hikrun_ls_color_entry ln)"
    elif [[ -x "$source_path" ]]; then
        code="$(_hikrun_ls_color_entry ex)"
    else
        local ext="${source_path##*.}"
        if [[ "$source_path" == *.* && -n "$ext" ]]; then
            code="$(_hikrun_ls_color_entry '*.'"$ext")"
        fi
    fi

    printf '%s' "$code"
}

_hikrun_colored_text() {
    local display_name="$1"
    local source_path="$2"
    local code
    code="$(_hikrun_ls_color_code "$source_path")"

    if [[ -n "$code" ]]; then
        printf '\033[%sm%s\033[0m' "$code" "$display_name"
    else
        printf '%s' "$display_name"
    fi
}

_hikrun_prompt_line() {
    printf '%s%s' "${PS1@P}" "$COMP_LINE"
}

_hikrun_print_display_list() {
    local width=${COLUMNS:-80}
    local count=$#
    local names=()
    local paths=()
    local pair name source_path
    local max_len=0

    for pair in "$@"; do
        name="${pair%%=*}"
        source_path="${pair#*=}"
        names+=("$name")
        paths+=("$source_path")
        (( ${#name} > max_len )) && max_len=${#name}
    done

    local col_width=$((max_len + 2))
    local cols=$((width / col_width))
    (( cols < 1 )) && cols=1
    (( cols > count )) && cols=$count
    local rows=$(((count + cols - 1) / cols))

    local out=$'\n'
    local row col idx pad colored spaces
    for ((row = 0; row < rows; row++)); do
        out+='  '
        for ((col = 0; col < cols; col++)); do
            idx=$((row + col * rows))
            (( idx >= count )) && continue
            name="${names[idx]}"
            colored="$(_hikrun_colored_text "$name" "${paths[idx]}")"
            out+="$colored"
            if (( col < cols - 1 )); then
                pad=$((col_width - ${#name}))
                printf -v spaces '%*s' "$pad" ''
                out+="$spaces"
            fi
        done
        out+=$'\n'
    done
    out+="$(_hikrun_prompt_line)"
    printf '%s' "$out" >&2
}

_hikrun () {
    COMPREPLY=()
    local end
    if [[ "${COMP_LINE:0-1}" == " " ]];then
      end='y'
    else
      end='n'
    fi

    local res=( $(python3 ${SCRIPT_TOP_DIR}/src/complete.py ${COMP_WORDS[*]} ${end}) )
    local lsnospace=${res[*]:0:3}
    if [[ "${res[3]}" == "true" ]];then
        __file_sw="-o default"
    else
        __file_sw=" "
    fi
    unset res[0]
    unset res[1]
    unset res[2]
    unset res[3]
    ${lsnospace}

    # Separate metadata lines from completion candidates. COMPREPLY must stay
    # plain text so readline inserts the short hikrun command names correctly.
    local py_tools=()
    local display_meta=()
    local clean=()
    for item in ${res[*]}; do
        if [[ "$item" == _py_:* ]]; then
            py_tools+=("${item#_py_:}")
        elif [[ "$item" == _display_:* ]]; then
            display_meta+=("${item#_display_:}")
        elif [[ -n "$item" ]]; then
            clean+=("$item")
        fi
    done
    # For a single match, let readline insert it normally. For multiple matches,
    # show our coloured list and clear COMPREPLY so readline does not print the
    # uncoloured default list on the next Tab.
    if [[ ${#clean[@]} -eq 1 ]]; then
        COMPREPLY=( "${clean[0]}" )
    elif [[ ${#display_meta[@]} -gt 0 ]]; then
        COMPREPLY=()
        _hikrun_print_display_list "${display_meta[@]}"
    elif [[ ${#py_tools[@]} -gt 0 ]]; then
        COMPREPLY=()
        local name py_meta=()
        for name in "${py_tools[@]}"; do
            py_meta+=("$name=${SCRIPT_TOP_DIR}/src/utils/${name^}.py")
        done
        _hikrun_print_display_list "${py_meta[@]}"
    else
        COMPREPLY=( "${clean[@]}" )
    fi
}

__hikrun_program=${SCRIPT_TOOL_NAME}
have ${__hikrun_program} && \
 complete ${__file_sw}  -F _hikrun  ${__hikrun_program}
 unset __hikrun_program __file_sw