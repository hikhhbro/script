__file_sw=''
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
    COMPREPLY=( ${res[*]} )  
}

__hikrun_program=${SCRIPT_TOOL_NAME}
have ${__hikrun_program} && \
 complete ${__file_sw}  -F _hikrun  ${__hikrun_program}
 unset __hikrun_program __file_sw