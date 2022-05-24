 # -*- coding: utf-8 -*-
import gitlab
import os
import sys

if __name__ == '__main__':
    url = 'https://git.n.xiaomi.com/' 
    private_token = 'rwDxVLx8byp5YHUSNqLK'
    top_dir_id = 27411
    gl = gitlab.Gitlab(url, private_token)
    group = gl.groups.get(top_dir_id)
    projects = group.projects.list(all=True)
    i=0
    for project in projects:
        i = i+1
        p = gl.projects.get(project.id)
        p_branches = p.protectedbranches.list()
        for p_b in p_branches:
            if p_b.name != 'mina-dev':
                p_branch = pr1.protectedbranches.create({
                    'name': 'mina-dev',
                    'merge_access_level': gitlab.const.MAINTAINER_ACCESS,
                    'push_access_level': gitlab.const.MAINTAINER_ACCESS
                })
                print(p_b)