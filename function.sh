if [ -f "${HIK_SCRIPT_TOP_DIR}/company/companyfunc.sh" ];then
source ${HIK_SCRIPT_TOP_DIR}/company/companyfunc.sh
fi

# if [ -f "${HIK_SCRIPT_TOP_DIR}/script/${script_arg[0]}" ];then
#   . ${HIK_SCRIPT_TOP_DIR}/script/${script_arg[0]}
# elif [ -f "${HIK_SCRIPT_TOP_DIR}/company/${script_arg[0]}" ];then
#   . ${HIK_SCRIPT_TOP_DIR}/company/${script_arg[0]}
# fi
# my_compile_get_describec() {
#   if [[ "$1" == "<_describe>" ]] ;then
  
# }
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

if [[ -f ${HIK_SCRIPT_TOP_DIR}/script/${script_arg[0]} ]];then
    dir_ro="script"
elif [[ -f ${HIK_SCRIPT_TOP_DIR}/company/${script_arg[0]} ]];then
    dir_ro="company"
else
    echo "文件不存在"
    exit 1
fi
if [ "${HIK_SCRIPT_TOP_DIR}/${dir_ro}/${script_arg[0]}" -nt  "${HIK_SCRIPT_TOP_DIR}/.compile/${dir_ro}/${script_arg[0]}" ];then 
        temp_dir_s="${HIK_SCRIPT_TOP_DIR}/${dir_ro}/${script_arg[0]}"
        mkdir -p  ${temp_dir_s%/*}
        my_compile ${dir_ro}/${script_arg[0]}
        unset temp_dir_s
fi
. ${HIK_SCRIPT_TOP_DIR}/.compile/${dir_ro}/${script_arg[0]}
unset dir_ro
run_func=(
  ${machine}_${project}_${download}
  ${machine}_${project}_${prebuilt}
  ${machine}_${project}_${build}
  ${machine}_${project}_${rootfs}
  ${rerun}_${script}
  ${script_arg[0]}_${describe} 
  ${script_arg[0]}_${probe}
)

#执行外部脚本
rerun_script() {
  if [ ! -f "${script_arg[0]}" ];then
    if [ ! -f "${HIK_SCRIPT_TOP_DIR}/script/${script_arg[0]}" ];then
        _func "${script_arg[0]} 不存在"
        exit 0
    fi
    script_arg[0]="${HIK_SCRIPT_TOP_DIR}/script/${script_arg[0]}"
  fi
  for i in $(seq 1 $rerun_j)
  do
    _func ". ""${script_arg[*]}"  "第${i}次执行开始 === 剩余:$(expr $rerun_j - $i)次"
    $(echo ". ""${script_arg[*]}")
  done
}

