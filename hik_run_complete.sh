__get_file() {
         trap exit 0 3
        COMPREPLY=()
        unset input2
        local  input2 
        # echo "${cur}" "dcur"
        if [[ "${cur}" == "" ]];then
          if [ -d "$1" ] && [ -d "$2" ];then 
            input1="`ls $1`"" `ls $2`"
            dir1=$1
            dir2=$2
          fi

          for i in ${input1}
          do
              input2=${input2}" "$i
              if [ -d "$1$i" ] || [ -d "$2$i" ];then
                input2=${input2}"/"
              fi
          done
          COMPREPLY=( $(compgen -W "${input2}" -- ) )
          # echo "  111r"
        else

          if [ -d "$dir1$1" ];then
              input1="`ls $dir1$1`"
              # echo $input1
                # return 0
          elif [ -d "$dir2$1" ];then
              input1="`ls $dir2$1`"
                # return 0
          else
            echo $1
            return 0
          fi
          echo "  er"
        fi
        # if [ -d "$1" ] && [ -d "$2" ];then 
        #   input1="`ls $1`"" `ls $2`"
        #   dir1=$1
        #   dir2=$2
        # elif [ -d "$dir1$1" ];then
        #     input1="`ls $dir1$1`"
        #     # echo $input1
        #       # return 0
        # elif [ -d "$dir2$1" ];then
        #     input1="`ls $dir2$1`"
        #       # return 0
        # else
        #   echo $1
        #   return 0
        # fi

            
            # if [[ ${cur} == */ ]];then
            #     echo $input1
            #   COMPREPLY=( $(compgen -W "${input2}" -- ) )
              
            # else
            
            #   COMPREPLY=( $(compgen -W "${input2}" -- ${cur}) )
            # fi
            
            # if [[ ${#COMPREPLY[@]} -eq 1 ]]; then
            #   echo "de-1"
            #   if [[ ${COMPREPLY} == */ ]];then
            #       echo "de-2"
            #       compopt -o nospace
            #   fi 
            # fi
            # if [[ ${cur} == */ ]];then
            #     echo "de-3"  
            #     if [[ "${COMPREPLY}" != "${cur}" ]];then
            #         echo ${COMPREPLY} ${cur} "rsi"
            #         sleep 2
            #         __get_file ${cur}
            #         echo ${COMPREPLY} "ri"
            #     else
            #         #  echo ${COMPREPLY}"  "${cur}" "${input1} "  "${COMP_CWORD}
            #         echo "de-5"
            #         compopt -o nospace
            #       return 0
            #     fi 
            # fi 
            # echo "de-6"
            # echo " re "${input1}
}
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
    if [[ ${COMP_CWORD} == 1 ]];then
        __get_file ${HIK_SCRIPT_TOP_DIR}/script/  ${HIK_SCRIPT_TOP_DIR}/company/

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
        tmp_opt="`ls ${HIK_SCRIPT_TOP_DIR}/script/`"" `ls ${HIK_SCRIPT_TOP_DIR}/company/`"" `ls ${HIK_SCRIPT_TOP_DIR}/`"
        COMPREPLY=( $(compgen -W "${tmp_opt}" -- ${cur}) )
        tmp_opt=""
        return 0
        ;;
      --rm)
        tmp_opt="`ls ${HIK_SCRIPT_TOP_DIR}/script/`"" `ls ${HIK_SCRIPT_TOP_DIR}/company/`"" `ls ${HIK_SCRIPT_TOP_DIR}/`"
        COMPREPLY=( $(compgen -W "${tmp_opt}" -- ${cur}) )
        tmp_opt=""
        return 0
        ;;
      --script)
        tmp_opt="`ls ${HIK_SCRIPT_TOP_DIR}/script/`"" `ls ${HIK_SCRIPT_TOP_DIR}/company/`"
        COMPREPLY=( $(compgen -W "${tmp_opt}" -- ${cur}) )
        tmp_opt=""
        return 0
        ;;
      *)

        if [[ -f ${HIK_SCRIPT_TOP_DIR}/script/${COMP_WORDS[1]} ]];then
          . ${HIK_SCRIPT_TOP_DIR}/script/${COMP_WORDS[1]}
        elif [[ -f ${HIK_SCRIPT_TOP_DIR}/company/${COMP_WORDS[1]} ]];then
          . ${HIK_SCRIPT_TOP_DIR}/company/${COMP_WORDS[1]}
        else
          return 0
        fi
        tmp_opt=( $(${COMP_WORDS[1]}_get_options) )
        # echo ${tmp_opt[@]}
        local opt_
        local opt
        for i in ${tmp_opt[@]}
        do
            if [[ $i == -* ]]; then
                opt_=${opt_}" "${i}
            else
              opt=${opt}" "${i}
            fi
        done
        # echo ${opt_}
        local opt_e=${opt}
        case "$cur" in
          -*)
            opt_e=${opt_}
          ;;
        esac
        COMPREPLY=( $(compgen -W " ${opt_e}${pub_opt}" -- ${cur}) )
        unset tmp_opt
        unset ${COMP_WORDS[1]}"_probe"
        unset ${COMP_WORDS[1]}"_describe"
        unset ${COMP_WORDS[1]}"_get_options"
        unset options
        return 0
        ;;
    esac
}
__hikrun_program="hikrun"
have ${__hikrun_program} && \
 complete -F _hikrun  ${__hikrun_program}
 unset __hikrun_program