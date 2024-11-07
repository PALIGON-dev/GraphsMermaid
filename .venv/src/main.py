import argparse
import subprocess
from datetime import datetime

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

    commits.sort(key=lambda x: x[2])
    numbered_commits = [(i + 1, commit[0], commit[1]) for i, commit in enumerate(commits)]
    return numbered_commits

def build_mermaid_graph(commits):
    graph = "graph TD;\n"
    for number, commit_hash, parents in commits:
        graph += f"    {commit_hash[:7]}[\"{number}: {commit_hash[:7]}\"];\n"
        for parent in parents:
            graph += f"    {commit_hash[:7]} --> {parent[:7]};\n"
        return graph

