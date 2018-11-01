#!/usr/bin/env python
"Collect stats and toss them in a table"
import os

import gitstats.__main__ as gitstats

import db

if __name__ == '__main__':
    db.clear_stat('git commit')
    for repo in gitstats.discover_repositories(os.path.join(os.path.dirname(db.__file__), '..')):
        for commit in gitstats.generate_git_log(repo):
            db.add_stat('git commit', 1, commit[2])
