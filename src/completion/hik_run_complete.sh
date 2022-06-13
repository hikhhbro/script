_hikrun () {
    COMPREPLY=()
    local end
    if [[ "${COMP_LINE:0-1}" == " " ]];then
      end='y'
    else
      end='n'
    fi
    
    local res=( $(python3 ${HIK_SCRIPT_TOP_DIR}/src/completion/complete.py ${COMP_WORDS[*]} ${end}) )
    local lsnospace=${res[*]:0:3}
    unset res[0]
    unset res[1]
    unset res[2]
    ${lsnospace}
    COMPREPLY=( ${res[*]} )  
}
__hikrun_program="hikrun"
have ${__hikrun_program} && \
 complete -o default -F _hikrun  ${__hikrun_program}
 unset __hikrun_program