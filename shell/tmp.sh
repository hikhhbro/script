if [[ "$1" == "" ]];then
exit 0
fi
downloads_dir="/home/hik/ws/core_work/pulseaudio/downloads/"
if [ ! -f "${downloads_dir}$1" ];then
echo "$1 不存在"
exit 0
fi
tar -xvf ${downloads_dir}/$1
name=$1
name=${name%%-*}
echo $name
dir=$1
dir=${dir:0:0-7}
echo $dir
mv $dir $name
cd $name
echo "{
  "type": "automake",
  "install":[]
}" > build.json
code build.json
read -p "编写build.json"
git init
git add .
git commit -s -m "Initialize the project"
git checkout -b $dir

git remote add origin "git@git.n.xiaomi.com:system_dev/minacore/external/$name.git"
git log
git branch -a

read -p "提交 : n 推出:" para

case $para in 
	[nN])
		echo "退出"
		;;
	*)
		git push origin $dir
esac # end case
