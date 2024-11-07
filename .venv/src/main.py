import argparse
import subprocess

def get_commits(repo_path, cutoff_date):
    result = subprocess.run(
        ["git", "-C", repo_path, "log", "--pretty=format:%H %P %ct", "--before", cutoff_date],
        capture_output=True,
        text=True,
        check=True
    )
    commits = []
    for line in result.stdout.splitlines():
        parts = line.strip().split()
        commit_hash = parts[0]
        parents = parts[1:-1]
        timestamp = int(parts[-1])
        commits.append((commit_hash, parents, timestamp))
    return commits