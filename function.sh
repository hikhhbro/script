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
  ${script_arg[0]}_${describe} 
)

# #执行外部脚本
# rerun_script() {
#   if [ ! -f "${script_arg[0]}" ];then
#     if [ ! -f "${HIK_SCRIPT_TOP_DIR}/script/${script_arg[0]}" ];then
#         _func "${script_arg[0]} 不存在"
#         exit 0
#     fi
#     script_arg[0]="${HIK_SCRIPT_TOP_DIR}/script/${script_arg[0]}"
#   fi
#   for i in $(seq 1 $rerun_j)
#   do
#     _func ". ""${script_arg[*]}"  "第${i}次执行开始 === 剩余:$(expr $rerun_j - $i)次"
#     $(echo ". ""${script_arg[*]}")
#   done
# }

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
        if [ -d  ${HIK_SCRIPT_TOP_DIR}/script ];then
            file_un=$(read_dir ${HIK_SCRIPT_TOP_DIR}/script)
            rm -r ${HIK_SCRIPT_TOP_DIR}/.compile/script/
        fi
        if [ -d  ${HIK_SCRIPT_TOP_DIR}/.compile/company/ ];then
            file_un="$(read_dir ${HIK_SCRIPT_TOP_DIR}/company) ${file_un}"
            rm -r ${HIK_SCRIPT_TOP_DIR}/.compile/company/
        fi
        file_un=($file_un)
        for i in ${file_un[@]}
        do
          outre=$(my_compile "$i")
          if [ "$?" == "0" ]; then
            . ${HIK_SCRIPT_TOP_DIR}/.compile/$i 
              outrd_=$(${i##*/}_describe)
              # echo $outrd_
              printf "%-24s %s %s" ${i##*/} "|" ${outrd_};
              printf "\n" ;
          fi
            echo  > ${HIK_SCRIPT_TOP_DIR}/.compile/.no_su_flag
        done
}
_describe() {
  echo "短选项：-*  ${short_opts}"
  echo "长选项：--*  ${long_opts}"
  echo "--rerun= 循环执行  -1 为无线循环,>0 为循环次数" 
  echo "其选项：支持运行安装目录下的无后缀模板类型脚本"
  echo "| tee file.log  参数尾加入,同时输出到文件中"
}
