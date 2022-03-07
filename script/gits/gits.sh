
creat="create"
gits_run(){
    if [ "${self_arg[1]}" == "create" ];then
        _task gits_create_bare
    else
        echo "其他"
    fi
}
gits_create_bare(){
    if ssh gits test -e /gits/${self_arg[2]}.git; then 
        _task "${self_arg[2]} 已存在"
    else 
        _task mkdir ${self_arg[2]}.git
        _task cd ${self_arg[2]}.git
        _task git init ${self_arg[2]}.git --bare 
        _task scp -r ${self_arg[2]}.git gits:/gits/
    fi

# scp下载判断
    # if scp -r gits:/volume2/git-server/${self_arg[1]}.git ./ >& /dev/null
    # then 
    #     _task "${self_arg[1]} 已存在"
    # else 
    #     _task mkdir ${self_arg[1]}.git
    #     _task cd ${self_arg[1]}.git
    #     _task git init ${self_arg[1]}.git --bare 
    #     _task scp -r ${self_arg[1]}.git gits:/volume2/git-server/
    # fi
}
gits_create_dir(){
    mkdir $1
}
gits_run