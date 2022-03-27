if [ ${#script_arg[@]} -gt 0 ];then
  if [[ -f ${HIK_SCRIPT_TOP_DIR}/script/${script_arg[0]} ]];then
      dir_ro="script"
  elif [[ -f ${HIK_SCRIPT_TOP_DIR}/company/${script_arg[0]} ]];then
      dir_ro="company"
  else
      echo "文件不存在  ${script_arg[0]}"
      exit 1
  fi
  if [ "${HIK_SCRIPT_TOP_DIR}/${dir_ro}/${script_arg[0]}" -nt  "${HIK_SCRIPT_TOP_DIR}/.compile/${dir_ro}/${script_arg[0]}" ];then 
          my_compile ${dir_ro}/${script_arg[0]}
  fi
  . ${HIK_SCRIPT_TOP_DIR}/.compile/${dir_ro}/${script_arg[0]}
  unset dir_ro
fi
run_func=(
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

function read_dir(){
  for file in `ls $1` 
  do
    if [ -d $1"/"$file ] 
    then
    read_dir $1"/"$file
    else
      if [[ "$file" != *.* ]] ; then
        local out=$1
        out=${out##*/}
        echo $out"/"$file 
      fi
    fi
  done
} 

_all_describe() {
        local file_un outre
        file_un=$(read_dir ${HIK_SCRIPT_TOP_DIR}/script)
        file_un="$(read_dir ${HIK_SCRIPT_TOP_DIR}/company) ${file_un}"
        file_un=($file_un)
        rm -r ${HIK_SCRIPT_TOP_DIR}/.compile/script/
        rm -r ${HIK_SCRIPT_TOP_DIR}/.compile/company/
        for i in ${file_un[@]}
        do
          outre=$(my_compile "$i")
          if [ "$?" == "0" ]; then
            . ${HIK_SCRIPT_TOP_DIR}/.compile/$i 
              outrd_=$(${i##*/}_describe)
              printf "%-26s %s" ${i##*/} ${outrd_};
              printf "\n" ;
          fi
            echo  > ${HIK_SCRIPT_TOP_DIR}/.compile/.no_su_flag
        done
}
_describe() {
  echo "短选项：-*  ${short_opts}"
  echo "长选项：--*  ${long_opts}"
  echo "其选项：支持运行安装目录下的无后缀模板类型脚本"
  echo "z foo  CD到最近的dir匹配foo "
  echo "z foo bar  CD到最近的dir匹配foo和bar "
  echo "z -r foo  CD到最高级的dir匹配foo "
  echo "z -t foo  CD到最近一次访问的dir匹配foo "
  echo "z -l foo  list匹配而不是CD "
  echo "z -e foo  echo最佳匹配，不要CD "
  echo "z -c foo 限制匹配$PWD的子目录 "
  echo "z -x 从数据文件中删除当前目录 "
  echo "z -h 显示一个简短的帮助信息 "
}
