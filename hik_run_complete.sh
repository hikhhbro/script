__get_file() {
        # set -x
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
              if [[ "${i}" != *.* ]] ; then
                input2=${input2}" "$i
                if [ -d "$1$i" ] || [ -d "$2$i" ];then
                  input2=${input2}"/"
                fi
              fi
          done
          COMPREPLY=( $(compgen -W "${input2}" -- ) )
          # echo "  111r"
        else
          if [[ ${cur} != */ ]];then
            if [[ ${cur} != */* ]];then
              if [ -d "$1" ] && [ -d "$2" ];then 
                input1="`ls $1`"" `ls $2`"
                dir1=$1
                dir2=$2
              fi
              cur_cur=${cur}
            else
                temp_cur=${cur%/*}
                cur_cur=${cur##*/}
              if [ -d "$1${temp_cur}" ];then
                  input1="`ls $1${temp_cur}`"
              elif [ -d "$2${temp_cur}" ];then
                  input1="`ls $2${temp_cur}`"
              else
                echo $1 "32"
                  echo $1${temp_cur} "32" "  "${cur}
                return 0
              fi
            fi

            for i in ${input1}
            do
                if [[ "${i}" != *.* ]] ; then
                  input2=${input2}" "$i
                  if [ -d "$1$i" ] || [ -d "$2$i" ];then
                    input2=${input2}"/"
                  fi
                fi
            done
            compopt -o nospace
            COMPREPLY=( $(compgen -W "${input2}" -- ${cur_cur}) )
            if [[ ${cur} == */* ]];then
                  compopt +o nospace
                  for(( i=0;i<${#COMPREPLY[@]};i++)) do
                    COMPREPLY[$i]="${temp_cur}/${COMPREPLY[$i]}"
                  done; 
            else
                if [[ "${#COMPREPLY[@]}" == "1" && ${COMPREPLY[0]} != */ ]];then
                    compopt +o nospace
                fi
            fi



          
          
          else
            temp_cur=${cur%/*}
            if [ -d "$1${temp_cur}" ];then
                input1="`ls $1${temp_cur}`"
            elif [ -d "$2${temp_cur}" ];then
                input1="`ls $2${temp_cur}`"
            else
              # echo $1 "dd"
              return 0
            fi
            for i in ${input1}
            do
                if [[ "${i}" != *.* ]] ; then
                  input2=${input2}" "$i
                  if [ -d "$1$i" ] || [ -d "$2$i" ];then
                    input2=${input2}"/"
                  fi
                fi
            done
            compopt -o nospace
            COMPREPLY=( $(compgen -W "${input2}" -- ) )
            if [[ "${#COMPREPLY[@]}" == "1"  ]];then
                    compopt +o nospace
                    COMPREPLY[0]="${temp_cur}/${COMPREPLY[0]}"
                    

            fi
          fi
          
        fi
                  

}

_hikrun() {
    local pre cur tmp_opt
    . ${HIK_SCRIPT_TOP_DIR}/base.sh
    COMPREPLY=()
    pre=${COMP_WORDS[COMP_CWORD-1]}
    cur=${COMP_WORDS[COMP_CWORD]}


    if [[ ${COMP_CWORD} == 1 ]];then
      if [[ ${cur} == --* ]] ; then
          COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
          return 0
      else
        __get_file ${HIK_SCRIPT_TOP_DIR}/script/  ${HIK_SCRIPT_TOP_DIR}/company/
        return 0
      fi
    fi
    case "$pre" in
      -B | -C)
        tmp_opt="android y4 rpi"
        COMPREPLY=( $(compgen -W "${tmp_opt}" -- ${cur}) )
        tmp_opt=""
        return 0
        ;;
      --code)
        __get_file ${HIK_SCRIPT_TOP_DIR}/script/  ${HIK_SCRIPT_TOP_DIR}/company/
        return 0
        ;;
      --rm)
        __get_file ${HIK_SCRIPT_TOP_DIR}/script/  ${HIK_SCRIPT_TOP_DIR}/company/
        return 0
        ;;
      --script)
        __get_file ${HIK_SCRIPT_TOP_DIR}/script/  ${HIK_SCRIPT_TOP_DIR}/company/
        return 0
        ;;
      *)
        local dir_ro=""
        if [[ -f ${HIK_SCRIPT_TOP_DIR}/script/${COMP_WORDS[1]} ]];then
            dir_ro="script"
        elif [[ -f ${HIK_SCRIPT_TOP_DIR}/company/${COMP_WORDS[1]} ]];then
            dir_ro="company"
        else
          return 0
        fi
        if [ "${HIK_SCRIPT_TOP_DIR}/${dir_ro}/${COMP_WORDS[1]}" -nt  "${HIK_SCRIPT_TOP_DIR}/.compile/${dir_ro}/${COMP_WORDS[1]}" ];then 
                my_compile ${dir_ro}/${COMP_WORDS[1]}
        fi
         . ${HIK_SCRIPT_TOP_DIR}/.compile/${dir_ro}/${COMP_WORDS[1]}
        tmp_opt=( $(${COMP_WORDS[1]}_get_options) )
        local opt_
        local opt
        local E_OPTS
        local L_E_OPTS
        # echo ${tmp_opt[@]}
        for i in ${tmp_opt[@]}
        do
            if [[ $i == --* ]]; then
                opt_="${i} ${opt_}"
                L_E_OPTS="${i:2},${L_E_OPTS}"
            elif [[ $i == -* ]]; then
                opt_="${i} ${opt_}"
                E_OPTS="${i:1}${E_OPTS}"
            else
              opt="${i} ${opt}"
            fi
        done
        if [[ ${E_OPTS} != "" ]]; then
          echo ${E_OPTS} > ${HIK_SCRIPT_TOP_DIR}/.compile/.tmp_opt
        else 
          echo  > ${HIK_SCRIPT_TOP_DIR}/.compile/.tmp_opt
        fi
        if [[ ${L_E_OPTS} != "" ]]; then
          echo ${L_E_OPTS} > ${HIK_SCRIPT_TOP_DIR}/.compile/.l_tmp_opt
        else
          echo  > ${HIK_SCRIPT_TOP_DIR}/.compile/.l_tmp_opt
        fi
        # echo ${opt_}
        local opt_e=${opt}
        case "$cur" in
            -*)
              opt_e="${opt_} ${pub_opt}"
              shift
            ;;
        esac 
        COMPREPLY=( $(compgen -W " ${opt_e}" -- ${cur}) )
        unset tmp_opt
        unset ${COMP_WORDS[1]}"_probe"
        unset ${COMP_WORDS[1]}"_describe"
        unset ${COMP_WORDS[1]}"_get_options"
        unset ${COMP_WORDS[1]}"_s_get_options"
        unset ${COMP_WORDS[1]}"_l_get_options"
        unset options
        return 0
        ;;
    esac
}
__hikrun_program="hikrun"
have ${__hikrun_program} && \
 complete -o filenames -F _hikrun  ${__hikrun_program}
 unset __hikrun_program