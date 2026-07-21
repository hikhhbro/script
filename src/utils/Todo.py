import time
import os
from command.Shell import Shell
from command.Base import Base
import Log


class Todo(Base):
    TODO_FILE = 'todo_list.json'
    DONE_FILE = 'done_list.json'

    def __init__(self, args=None):
        super().__init__(args)
        self.meta("记录、查看和完成待办事项。")
        self.command('add', '新增待办；add 后面的所有参数会合并为一条文本').run(self.add).args("<文本>")
        self.command('rm', '按序号或序号范围完成待办').run(self.rm).args("<序号|范围|日期>")
        self.command('show', '显示待办；show done 显示已完成').run(self.show).value(['done']).args("[done|日期]")
        self.__ensure_store()

    def __today(self):
        return time.strftime("%Y/%m/%d")

    def __ensure_store(self):
        self.ensure_dir(self.data_dir)
        for path in [self.data_path(self.TODO_FILE), self.data_path(self.DONE_FILE)]:
            if not os.path.exists(path):
                self.__save(path, {})

    def __load(self, path):
        return self.read_json_file(path, {})

    def __save(self, path, data):
        return self.write_json_file(path, data, ensure_ascii=False)

    def __store_path(self, done=False):
        return self.data_path(self.DONE_FILE if done else self.TODO_FILE)

    def __todos(self):
        return self.__load(self.__store_path())

    def __done(self):
        return self.__load(self.__store_path(done=True))

    def __append_item(self, path, text):
        data = self.__load(path)
        data.setdefault(self.__today(), []).append(text)
        self.__save(path, data)

    def __init_git(self):
        git_remote = input("请输出远程仓库地址: ")
        Shell.chain(cwd=self.data_dir).git("init").git("remote", "add", "origin", git_remote).status()

    def __commit_store(self, commit):
        if not os.path.exists(self.data_path('.git')):
            Log.tips("此目录任不是git仓库，请初始化")
            self.__init_git()
            return
        Shell.chain(cwd=self.data_dir).git("add", ".").git("commit", "-m", commit).status()

    def __text(self, words):
        return ' '.join(words).strip()

    def __print_group(self, date, items, show_serial=True, start=0):
        print("\033[1;34m   %s\033[0m" % date)
        for offset, item in enumerate(items):
            prefix = "%s: " % (start + offset) if show_serial else ""
            print("%s%s" % (prefix, item))
        return start + len(items)

    def __parse_remove_targets(self, args):
        dates = set()
        indexes = set()
        for item in args:
            if '/' in item:
                dates.add(item)
            elif ':' in item:
                start, end = item.split(':', 1)
                indexes.update(range(int(start), int(end) + 1))
            else:
                indexes.add(int(item))
        return dates, indexes

    def __take_removed(self, todos, dates, indexes):
        removed = []
        current = 0

        for date, items in list(todos.items()):
            kept = []
            for item in items:
                if date in dates or current in indexes:
                    removed.append("[%s]: %s" % (date, item))
                else:
                    kept.append(item)
                current += 1
            if kept:
                todos[date] = kept
            else:
                del todos[date]
        return removed

    def __archive_removed(self, items):
        done = self.__done()
        done.setdefault(self.__today(), []).extend(items)
        self.__save(self.__store_path(done=True), done)

    def add(self, words):
        text = self.__text(words)
        if not text:
            self.help('add')
            return
        self.__append_item(self.__store_path(), text)
        self.__commit_store("add todo")

    def show(self, args):
        show_done = bool(args and args[0] == "done")
        query = self.__text(args[1:] if show_done else args)
        data = self.__done() if show_done else self.__todos()
        show_serial = not show_done

        if query and query in data:
            self.__print_group(query, data[query], show_serial)
            return

        index = 0
        for date, items in data.items():
            index = self.__print_group(date, items, show_serial, index)

    def rm(self, args):
        if not args:
            self.help('rm')
            return
        todos = self.__todos()
        dates, indexes = self.__parse_remove_targets(args)
        removed = self.__take_removed(todos, dates, indexes)
        if not removed:
            Log.tips("没有匹配到需要完成的 todo")
            return
        self.__save(self.__store_path(), todos)
        self.__archive_removed(removed)
        self.__commit_store("rm todo")
