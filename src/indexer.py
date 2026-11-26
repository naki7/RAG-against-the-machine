from pathlib import Path
from typing import Any


def file_organizer(files: list[Any]) -> dict[str, str]:
    stringafied = [str(file) for file in files]
    result = {}

    for file in stringafied:
        with open(file, 'r', encoding='utf-8') as text:
            temp = text.read()
        result[file] = temp

    return result


def ingest() -> dict[str, Any]:
    results = {}
    source: Path = Path('./data/raw/')
    md_files = list(source.glob('**/*.md'))
    py_files = list(source.glob('**/*.py'))
    txt_files = list(source.glob('**/*.txt'))

    results['md'] = file_organizer(md_files)
    results['py'] = file_organizer(py_files)
    results['txt'] = file_organizer(txt_files)

    for file_type in results:
        temp = {location: content[:25] for location, content in results[file_type].items()}
        for file in temp:
            print(file, " - ", temp[file][:10])

    return results


def md_chunker(content: str, size: int) -> int:
    in_section = False
    section_levels = {}
    curr_level = 0
    i = 0

    for char in content:
        if in_section is True:
            if char == '#':
                curr_level += 1
            else:
                if section_levels.get(curr_level) is None:
                    section_levels[curr_level] = [0, 0]
                elif section_levels[curr_level][0] == 1:
                    section_levels[curr_level][1] = i - curr_level
                section_levels[curr_level][0] += 1
                in_section = False
                curr_level = 0
        elif char == '#':
            in_section = True
            curr_level = 1
        i += 1

    if len(section_levels) == 0:
        return size
    elif section_levels.get(1) is not None:
        if section_levels[1][0] > 1:
            return section_levels[1][1]

    return size


def py_chunker(content: str, size: int) -> int:
    type_levels = {}
    state = []
    end_positions = {}
    i = 0

    for char in content:
        if char == 'c':
            if content[i: i + 5] == 'class':
                if type_levels.get('class') is None:
                    type_levels['class'] = [0, 0]
                type_levels['class'][0] += 1
                state.append('class')
        elif char == 'd':
            if content[i: i + 3] == 'def':
                if type_levels.get('func') is None:
                    type_levels['func'] = [0, 0]
                type_levels['func'][0] += 1
                state.append('func')
        elif char == '{':
            if len(state) == 0:
                state.append('inline')
                type_levels['inline'] = [1, 0]
            type_levels[state[-1]][1] += 1
        elif char == '}':
            if len(state) > 0:
                type_levels[state[-1]][1] -= 1
                if type_levels[state[-1]][1] == 0:
                    if type_levels[state[-1]][0] == 1:
                        end_positions[state[-1]] = i
                    state.pop()
        i += 1

    if end_positions.get('class') is not None:
        return i
    elif end_positions.get('func') is not None:
        return i

    return size


def txt_chunker(raw_data: str, size: int) -> int:
    pass


def main_chunker(file_type: str, raw_data: list[str, str],
            size: int) -> dict[str, Any]:
    results = []
    path = raw_data[0]
    remaining_content = raw_data[1]
    start_i = 0
    if len(remaining_content) < size:
        size = len(remaining_content)
    chunk_len = size

    while len(remaining_content) > 0:
        window = remaining_content[: size]
        chunk_len = 0
        if file_type == 'md':
            chunk_len = md_chunker(window, size)
        elif file_type == 'py':
            chunk_len = py_chunker(window, size)
        elif file_type == 'txt':
            chunk_len = txt_chunker(window, size)
        if len(remaining_content) < size and size == chunk_len:
            chunk_len = len(remaining_content)
        results.append({
                'path': path,
                'content': window[:chunk_len],
                'start_i': start_i,
                'end_i': start_i + chunk_len
            })
        remaining_content = remaining_content[chunk_len:]
        start_i += chunk_len + 1

    return results


def main() -> None:
    raw_data = ingest()
    size = None
    if size is None:
        size = 2000
    chunks = []
    # if raw_data.get('md') is not None:
    #     for file in raw_data['md']:
    #         chunks.append(main_chunker('md', [file, raw_data['md'][file]], size))
    if raw_data.get('py') is not None:
        for file in raw_data['py']:
            chunks.append(main_chunker('py', [file, raw_data['py'][file]], size))
    # act_len = len("# Security Policy\n\n## Reporting security issues\n\nPlease report security issues privately using [the vulnerability submission form](https://github.com/vllm-project/vllm/security/advisories/new).\n\n## Issue triage\n\nReports will then be triaged by the [vulnerability management team](https://docs.vllm.ai/en/latest/contributing/vulnerability_management.html).\n\n## Threat model\n\nPlease see the [Security Guide in the vLLM documentation](https://docs.vllm.ai/en/latest/usage/security.html) for more information on vLLM's security assumptions and recommendations.\n\nPlease see [PyTorch's Security Policy](https://github.com/pytorch/pytorch/blob/main/SECURITY.md) for more information and recommendations on how to securely interact with models.\n\n## Issue severity\n\nWe will determine the risk of each issue, taking into account our experience dealing with past issues, versions affected, common defaults, and use cases. We use the following severity categories:\n\n### CRITICAL Severity\n\nVulnerabilities that allow remote attackers to execute arbitrary code, take full control of the system, or significantly compromise confidentiality, integrity, or availability without any interaction or privileges needed, examples include remote code execution via network, deserialization issues that allow exploit chains. Generally those issues which are rated as CVSS  ≥\u202f9.0.\n\n### HIGH Severity\n\nSerious security flaws that allow elevated impact—like RCE in specific, limited contexts or significant data loss—but require advanced conditions or some trust, examples include RCE in advanced deployment modes (e.g. multi-node), or high impact issues where some sort of privileged network access is required. These issues typically have CVSS scores between 7.0 and 8.9\n\n### MODERATE Severity\n\nVulnerabilities that cause denial of service or partial disruption, but do not allow arbitrary code execution or data breach and have limited impact. These issues have a CVSS rating between 4.0 and 6.9\n\n### LOW Severity\n\nMinor iss")
    # print(act_len)
    # print(chunks[0][0], chunks[0][1])
    print(len(chunks))
    for chunk in chunks:
        for i in range(0, len(chunk)):
            print(len(chunk), chunk[i]['path'], len(chunk[i]['content']), chunk[i]['start_i'], chunk[i]['end_i'])
    # check_len = 0
    # for chunk in chunks[1]:
    #     # print(chunk['content'])
    #     check_len += len(chunk['content'])
    # print(check_len)
    # print(len(raw_data['py']['data/raw/vllm-0.10.1/setup.py']))

if __name__ == "__main__":
    main()
