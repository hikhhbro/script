_hikrun() {
    local pre cur tmp_opt
    . ${HIK_SCRIPT_TOP_DIR}/base.sh
    COMPREPLY=()
    pre=${COMP_WORDS[COMP_CWORD-1]}
    cur=${COMP_WORDS[COMP_CWORD]}

    if [[ ${cur} == --* ]] ; then
        COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
        return 0
    fi
    if [[ ${COMP_CWORD} < 2 ]];then
        COMPREPLY=( $(compgen -W "${pre_opts}" -- ${cur}) )
        return 0
    fi
    case "$pre" in
      -B | -C)
        tmp_opt="android y4 rpi"
        COMPREPLY=( $(compgen -W "${tmp_opt}" -- ${cur}) )
        tmp_opt=""
        return 0
        ;;
      --code)
        tmp_opt="`ls ${HIK_SCRIPT_TOP_DIR}/script/`"" `ls ${HIK_SCRIPT_TOP_DIR}/`"
        COMPREPLY=( $(compgen -W "${tmp_opt}" -- ${cur}) )
        tmp_opt=""
        return 0
        ;;
      --script)
        tmp_opt="`ls ${HIK_SCRIPT_TOP_DIR}/script/`"
        COMPREPLY=( $(compgen -W "${tmp_opt}" -- ${cur}) )
        tmp_opt=""
        return 0
        ;;
    esac
}
complete -F _hikrun  -o default hikrun
