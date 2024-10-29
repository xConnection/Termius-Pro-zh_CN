import shutil
import os
import subprocess
import logging
import argparse
from os import path

# 设置日志配置
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def run_command(cmd, shell=False):
    """运行命令并处理异常。"""
    try:
        logging.info(f"Running command: {cmd}")
        subprocess.run(cmd, shell=shell, check=True)
    except subprocess.CalledProcessError as e:
        logging.error(f"Command failed with error: {e}")
    except FileNotFoundError:
        logging.error(f"Command not found: {cmd}")
    except Exception as e:
        logging.error(f"Error running command: {cmd} - {e}")

class TermiusModifier:
    def __init__(self, termius_path):
        self.termius_path = termius_path
        self.files_cache: dict[str, str] = {}

    def read_file(self, file_path, strip_empty=True):
        """读取文件内容并处理异常。"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                if strip_empty:
                    return [line.rstrip("\r\n") for line in file if line.strip()]  # 返回非空行列表
                return file.read()  # 返回文件内容作为字符串
        except FileNotFoundError:
            logging.error(f"File not found: {file_path}")
            return None
        except Exception as e:
            logging.error(f"Error reading file: {file_path} - {e}")
            return None

    def decompress_asar(self):
        cmd = f"asar extract {self.termius_path}/app.asar {self.termius_path}/app"
        run_command(cmd, shell=True)

    def pack_to_asar(self):
        cmd = f'asar pack {self.termius_path}/app {self.termius_path}/app.asar --unpack-dir {{"node_modules/@termius,out"}}'
        run_command(cmd, shell=True)

    def backup_asar(self):
        """备份 ASAR 文件。"""
        backup_path = f"{self.termius_path}/app.asar.bak"
        if not path.exists(backup_path):
            shutil.copy(f"{self.termius_path}/app.asar", backup_path)
        else:
            shutil.copy(backup_path, f"{self.termius_path}/app.asar")

    def load_files(self, code_files):
        """加载文件内容到缓存中。"""
        for file in code_files:
            if path.exists(file):
                self.files_cache[file] = self.read_file(file, strip_empty=False)  # 读取完整内容

    def replace_strings_in_content(self, file_content, cn_lang):
        """在内容中替换字符串。"""
        if not file_content:
            return file_content

        for lang in cn_lang:
            if lang.startswith("#"):
                continue
            if "|" in lang:
                old_value, new_value = lang.split("|", 1)
                file_content = file_content.replace(old_value, new_value)
            else:
                logging.error(f"Skipping invalid entry: {lang}")

        return file_content

    def replace_strings_in_files(self, cn_lang):
        """在文件中替换字符串。"""
        for file_path in self.files_cache:
            file_content = self.files_cache[file_path]
            self.files_cache[file_path] = self.replace_strings_in_content(file_content, cn_lang)

    def write_files(self):
        """将修改后的内容写入文件。"""
        for file_path, content in self.files_cache.items():
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(content)

    def get_code_files(self, include_css=False):
        """获取所有代码文件路径（包含 .code 和可选的 .css 文件）。"""
        prefix_links = [
            os.path.join(self.termius_path, 'app', 'background-process', 'assets'),
            os.path.join(self.termius_path, 'app', 'ui-process', 'assets'),
            os.path.join(self.termius_path, 'app', 'main-process'),
        ]
        code_files = []
        for prefix in prefix_links:
            for root, _, files in os.walk(prefix):
                if include_css:
                    code_files.extend([os.path.join(root, f) for f in files if f.endswith(('.js', '.css'))])
                else:
                    code_files.extend([os.path.join(root, f) for f in files if f.endswith(".js")])
        return code_files

    def search_in_files(self, search_terms, code_files):
        """在 JS 和 CSS 文件中搜索字符串并打印结果。"""
        found_files = []
        for file_path in code_files:
            file_content = self.read_file(file_path, strip_empty=False)  # 读取完整内容
            if file_content and all(term in file_content for term in search_terms):  # 检查所有搜索项
                found_files.append(file_path)

        if found_files:
            logging.info(f"Found all terms {search_terms} in: {found_files}")
        else:
            logging.info(f"No results found for terms {search_terms}.")

    def perform_replacement(self, include_css=False):
        """执行字符串替换的所有步骤。"""
        self.backup_asar()

        app_path = f"{self.termius_path}/app"
        if path.exists(app_path):
            shutil.rmtree(app_path)  # Windows 兼容的删除方式

        if not path.exists(app_path):
            self.decompress_asar()

        cn_lang = self.read_file("locales.txt")  # 读取语言文件内容
        code_files = self.get_code_files(include_css=include_css)  # 根据 include_css 参数获取文件列表

        self.load_files(code_files)
        self.replace_strings_in_files(cn_lang)
        self.write_files()
        self.pack_to_asar()
        logging.info("Replacement done.")

def main():
    parser = argparse.ArgumentParser(description='Modify Termius application.')
    parser.add_argument('-search', '-S', nargs='+',
                        help="Search for terms in JS and CSS files (use single quotes for each term).")
    parser.add_argument('-replace', '-R', action='store_true', help='Perform replacement using lang.txt.')
    parser.add_argument('-css', '-C', action='store_true', help='Include CSS files in search and replacement.')
    args = parser.parse_args()

    termius_path = os.path.join(os.getenv('USERPROFILE'), 'AppData', 'Local', 'Programs', 'Termius', 'resources')
    modifier = TermiusModifier(termius_path)

    # 如果没有提供 `-search` 或 `-replace` 参数，默认执行 `-replace`
    if not (args.replace or args.search):
        args.replace = True

    # 更新 get_code_files 以根据参数包含 CSS 文件
    code_files = modifier.get_code_files(include_css=args.css)

    if args.replace:
        modifier.perform_replacement(include_css=args.css)

    elif args.search:
        modifier.search_in_files(args.search, code_files)

    else:
        logging.error("Invalid command. Use '-search' or '-replace'.")

if __name__ == "__main__":
    main()
