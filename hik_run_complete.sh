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
              input2=${input2}" "$i
              if [ -d "$1$i" ] || [ -d "$2$i" ];then
                input2=${input2}"/"
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
                input2=${input2}" "$i
                if [ -d "$1$i" ] || [ -d "$2$i" ];then
                  input2=${input2}"/"
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
              echo $1 "dd"
              return 0
            fi
            for i in ${input1}
            do
                input2=${input2}" "$i
                if [ -d "$1$i" ] || [ -d "$2$i" ];then
                  input2=${input2}"/"
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
my_compile() {
  tem_line=""
  line_nub=0
  flag_read="begin"
  func_read=""
  prefix_=$1
  prefix_=${prefix_##*/}

  echo 0 > ${HIK_SCRIPT_TOP_DIR}/.compile/.tmp
  echo '#!/bin/bash' > ${HIK_SCRIPT_TOP_DIR}/.compile/$1
  while read -r line || [[ -n ${line} ]]
  do
    head_=(${line})
        # echo ${flag_read}
    case "${flag_read}" in
      begin)
          # echo ${flag_read}
          # echo ${func_read}
        if [[ "${head_[0]}" == "<_describe>" ]] ;then
          func_read=${head_[0]:1:-1}
          flag_read=${head_[1]}
          if [[ "${flag_read}" == "begin" ]] ;then
            echo "${prefix_}${func_read}() {" >> ${HIK_SCRIPT_TOP_DIR}/.compile/$1
          else
            echo "}" >> ${HIK_SCRIPT_TOP_DIR}/.compile/$1
          fi
        elif [[ "${head_[0]}" == "<_get_options>" ]] ;then  
          func_read=${head_[0]:1:-1}
          flag_read=${head_[1]}
          echo "}" >> ${HIK_SCRIPT_TOP_DIR}/.compile/$1
        elif [[ "${func_read}" == "_describe" ]] ;then
          echo "echo \"${line} \"" >> ${HIK_SCRIPT_TOP_DIR}/.compile/$1
        elif [[ "${func_read}" == "_get_options" ]] ;then
          echo "echo \"${line:3} \"" >> ${HIK_SCRIPT_TOP_DIR}/.compile/$1
        fi
        ;;
      end)
        if [[ "${head_[0]}" == "<_describe>" ]] ;then
          func_read=${head_[0]:1:-1}
          flag_read=${head_[1]}
          # echo ${func_read}
        elif [[ "${head_[0]}" == "<_get_options>" ]] ;then  
          func_read=${head_[0]:1:-1}
          flag_read=${head_[1]}
          if [[ "${flag_read}" == "begin" ]] ;then
            echo "${prefix_}${func_read}() {" >> ${HIK_SCRIPT_TOP_DIR}/.compile/$1
          fi
        elif [[ "${head_[0]}" == "#<user_func>" ]] ;then  
          func_read=${head_[0]}
        elif [[ "${head_[0]}" == "#<main>" ]] ;then  
            flag_read="probe"
            func_read="_probe"
            echo "${prefix_}${func_read}() {" >> ${HIK_SCRIPT_TOP_DIR}/.compile/$1
        else
          if [[ "${func_read}" == "#<user_func>" ]] ;then 
            if [[ "$(type -t ${head_[0]})" == "builtin" ||  "$(type -t ${head_[0]})" == "file" ]] ; then
              line='${db}'" $line" 
            fi
            echo $line >> ${HIK_SCRIPT_TOP_DIR}/.compile/$1
          fi
        fi
      ;;
      probe)
        if [[ "$(type -t ${head_[0]})" == "builtin" ||  "$(type -t ${head_[0]})" == "file" ]] ; then
          line='${db}'" $line" 
          echo 1 > ${HIK_SCRIPT_TOP_DIR}/.compile/.tmp
        fi
         echo $line >> ${HIK_SCRIPT_TOP_DIR}/.compile/$1
      ;;
    esac
  done < "${HIK_SCRIPT_TOP_DIR}/$1"
  # if [[ cat ${HIK_SCRIPT_TOP_DIR}/$1" == "" ]];then
  if [ `cat ${HIK_SCRIPT_TOP_DIR}/.compile/.tmp` -eq 0 ];then
    echo "echo -e \"\033[33m${prefix_}未实现\033[0m\"" >> ${HIK_SCRIPT_TOP_DIR}/.compile/$1
    echo 0 > ${HIK_SCRIPT_TOP_DIR}/.compile/.tmp
  fi
  echo "}" >> ${HIK_SCRIPT_TOP_DIR}/.compile/$1
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
        #   . ${HIK_SCRIPT_TOP_DIR}/.compile/script/${COMP_WORDS[1]}
            dir_ro="script"
        elif [[ -f ${HIK_SCRIPT_TOP_DIR}/company/${COMP_WORDS[1]} ]];then
            dir_ro="company"
        #   . ${HIK_SCRIPT_TOP_DIR}/.compile/company/${COMP_WORDS[1]}
        else
          return 0
          # echo "${HIK_SCRIPT_TOP_DIR}/.compile/company/${COMP_WORDS[1]}"
        fi
        if [ "${HIK_SCRIPT_TOP_DIR}/${dir_ro}/${COMP_WORDS[1]}" -nt  "${HIK_SCRIPT_TOP_DIR}/.compile/${dir_ro}/${COMP_WORDS[1]}" ];then 
                temp_dir_s="${HIK_SCRIPT_TOP_DIR}/${dir_ro}/${COMP_WORDS[1]}"
                mkdir -p  ${temp_dir_s%/*}
                my_compile ${dir_ro}/${COMP_WORDS[1]}
                unset temp_dir_s
        fi
         . ${HIK_SCRIPT_TOP_DIR}/.compile/${dir_ro}/${COMP_WORDS[1]}
        tmp_opt=( $(${COMP_WORDS[1]}_get_options) )
        local opt_
        local opt
        local E_OPTS
        for i in ${tmp_opt[@]}
        do
            if [[ $i == -* ]]; then
                opt_=${opt_}" "${i}
                E_OPTS="${E_OPTS}${i:1}"
            else
              opt=${opt}" "${i}
            fi
        done
        echo ${E_OPTS} > ${HIK_SCRIPT_TOP_DIR}/.compile/.tmp_opt
        # echo ${opt_}
        local opt_e=${opt}
        case "$cur" in
          -*)
            opt_e="${opt_} ${pub_opt}"
          ;;
        esac
        COMPREPLY=( $(compgen -W " ${opt_e}" -- ${cur}) )
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
 complete -o filenames -F _hikrun  ${__hikrun_program}
 unset __hikrun_program