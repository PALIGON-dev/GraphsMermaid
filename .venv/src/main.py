from git import Repo
from git.exc import InvalidGitRepositoryError
import argparse
from datetime import datetime, timezone


def validate_repo(repo_path):
    try:
        repo = Repo(repo_path)
        if repo.bare:
            raise ValueError("Путь указывает на пустой репозиторий (bare repository).")
    except InvalidGitRepositoryError:
        raise ValueError("Указанный путь не является корректным Git-репозиторием.")


def get_commits(repo_path, cutoff_date):
    repo = Repo(repo_path)
    if repo.head.is_detached:
        raise ValueError("Репозиторий не содержит активной ветки.")
    if not repo.branches:
        raise ValueError("Репозиторий не содержит веток.")
    branch = repo.active_branch if not repo.head.is_detached else repo.branches[0]
    if not list(repo.iter_commits(branch)):
        raise ValueError(f"Ветка '{branch}' не содержит коммитов.")
    commits = []
    for commit in repo.iter_commits(branch):
        commit_date = commit.committed_datetime
        if commit_date <= cutoff_date:
            commits.append((
                commit.hexsha,
                [parent.hexsha for parent in commit.parents],
                commit_date.strftime('%Y-%m-%d'),
                commit.message.strip()
            ))
    commits.sort(key=lambda x: x[2])
    numbered_commits = [(i + 1, commit[0], commit[1], commit[2], commit[3]) for i, commit in enumerate(commits)]
    return numbered_commits


def build_mermaid_graph(commits):
    graph = "graph TD;\n"
    for number, commit_hash, parents, commit_date, message in commits:
        commit_label = f"#{number}: {message}"
        graph += f'    C{number}["{commit_label}"];\n'
        for parent in parents:
            parent_number = next((num for num, hash_, *_ in commits if hash_ == parent), None)
            if parent_number:
                graph += f'    C{number} --> C{parent_number};\n'
    return graph


def save_mermaid_file(mermaid_graph, output_path):
    with open(output_path, 'w', encoding="utf-8") as f:
        f.write(mermaid_graph)


def main():
    parser = argparse.ArgumentParser(description="Визуализация графа зависимостей коммитов в git-репозитории.")
    parser.add_argument('-r', '--repo-path', type=str, required=True, help="Путь к анализируемому git-репозиторию")
    parser.add_argument('-d', '--date', type=str, required=True, help="Дата коммитов в формате YYYY-MM-DD")
    parser.add_argument('-o', '--output', type=str, default="graph.mmd", help="Путь для сохранения графа Mermaid")
    args = parser.parse_args()

    try:
        cutoff_date = datetime.strptime(args.date, '%Y-%m-%d').replace(tzinfo=timezone.utc)
    except ValueError:
        print("Неправильный формат даты. Используйте формат YYYY-MM-DD.")
        return
    try:
        validate_repo(args.repo_path)
        commits = get_commits(args.repo_path, cutoff_date)
        graph = build_mermaid_graph(commits)
        save_mermaid_file(graph, args.output)
        print(f"Граф зависимостей успешно сохранён в {args.output}.")
    except Exception as e:
        print(f"Ошибка: {e}")


if __name__ == '__main__':
    main()
