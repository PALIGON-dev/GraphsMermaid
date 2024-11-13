import argparse
import subprocess
from datetime import datetime


def get_commits(repo_path, cutoff_date):
    """
    Получает список коммитов до указанной даты в формате (hash, parents) с нумерацией.
    """
    result = subprocess.run(
        ["git", "-C", repo_path, "log", "--pretty=format:%H %P %ct", "--before", cutoff_date],
        capture_output=True,
        text=True,
        check=True
    )

    # Парсим коммиты, включая отметку времени, чтобы потом сортировать их
    commits = []
    for line in result.stdout.splitlines():
        parts = line.strip().split()
        commit_hash = parts[0]
        parents = parts[1:-1]  # Родительские коммиты
        timestamp = int(parts[-1])  # Время коммита
        commits.append((commit_hash, parents, timestamp))

    # Сортируем коммиты по отметке времени (от самого старого к новому) и добавляем нумерацию
    commits.sort(key=lambda x: x[2])
    numbered_commits = [(i + 1, commit[0], commit[1]) for i, commit in enumerate(commits)]

    return numbered_commits


def build_mermaid_graph(commits):
    """
    Создает граф в формате Mermaid из списка коммитов и их зависимостей с нумерацией.
    """
    graph = "graph TD;\n"
    for number, commit_hash, parents in commits:
        graph += f"    {commit_hash[:7]}[\"{number}: {commit_hash[:7]}\"];\n"
        for parent in parents:
            graph += f"    {commit_hash[:7]} --> {parent[:7]};\n"
    return graph


def save_mermaid_file(mermaid_graph, output_path):
    """
    Сохраняет граф Mermaid в файл.
    """
    with open(output_path, 'w', encoding="utf-8") as f:
        f.write(mermaid_graph)


def main():
    # Парсер аргументов командной строки
    parser = argparse.ArgumentParser(description="Визуализация графа зависимостей коммитов в git-репозитории.")
    parser.add_argument('-m', '--mermaid-path', type=str, required=True, help="Путь к mermaid-cli")
    parser.add_argument('-r', '--repo-path', type=str, required=True, help="Путь к анализируемому git-репозиторию")
    parser.add_argument('-d', '--date', type=str, required=True, help="Дата коммитов в формате YYYY-MM-DD")

    args = parser.parse_args()

    # Проверка даты
    try:
        cutoff_date = datetime.strptime(args.date, '%Y-%m-%d').strftime('%Y-%m-%d')
    except ValueError:
        print("Неправильный формат даты. Используйте формат YYYY-MM-DD.")
        return

    # Получаем список коммитов с нумерацией
    commits = get_commits(args.repo_path, cutoff_date)

    # Строим граф зависимостей в формате Mermaid с нумерацией
    graph = build_mermaid_graph(commits)

    # Сохраняем граф в файл
    save_mermaid_file(graph, "graph.mmd")
    print("Граф зависимостей успешно сохранён в 'graph.mmd'.")


if __name__ == '__main__':
    main()
