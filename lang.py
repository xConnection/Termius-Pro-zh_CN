# -*- coding: utf-8 -*-
import argparse
import logging
import os
import platform
import re
import shutil
import stat
import subprocess
import sys
import time
import tkinter as tk
from tkinter import filedialog

# 日志配置
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)7s - %(message)s")


class TermiusModifier:
    @property
    def _backup_path(self):
        """备份文件路径"""
        return os.path.join(self.termius_path, "app.asar.bak")

    @property
    def _original_path(self):
        """原始文件路径"""
        return os.path.join(self.termius_path, "app.asar")

    @property
    def _app_dir(self):
        return os.path.join(self.termius_path, "app")

    def __init__(self, termius_path, args):
        """初始化修改器实例"""
        self.termius_path = termius_path
        self.args = args
        self.files_cache = {}
        self.rule_contents = []

    def load_rules(self):
        """动态加载与参数同名的规则文件"""
        script_dir = os.path.dirname(os.path.abspath(__file__))
        # 定义需要处理的参数列表
        rule_args = ["skip_login", "trial", "style", "localize"]

        for arg in rule_args:
            if not getattr(self.args, arg, False):
                continue
            # 自动生成文件名, 强制保持参数名与文件名一致
            file_name = f"{arg}.txt"
            try:
                file_path = os.path.join(script_dir, "rules", file_name)
                if content := read_file(file_path):
                    self.rule_contents.extend(content)
            except Exception as e:
                logging.error(f"Error loading {file_name}: {e}")
                sys.exit(1)

    def decompress_asar(self):
        """解压 app.asar 文件"""
        cmd = f"asar extract {self._original_path} {self._app_dir}"
        run_command(cmd, shell=True)

    def pack_to_asar(self):
        """打包 app.asar 文件"""
        cmd = f"asar pack {self._app_dir} {self._original_path} --unpack-dir {{node_modules/@termius,out}}"
        run_command(cmd, shell=True)

    @staticmethod
    def _handle_remove_readonly(func, path, _):
        """处理只读文件"""
        os.chmod(path, stat.S_IWRITE)
        func(path)

    def restore_backup(self):
        """完整还原操作"""
        if not os.path.exists(self._backup_path):
            logging.info("Backup file not found, skip backup restore.")
            return

        shutil.copy(self._backup_path, self._original_path)
        logging.info("Restored from backup")

    def create_backup(self):
        """智能备份管理（仅在缺失时创建）"""
        if not os.path.exists(self._backup_path):
            shutil.copy(self._original_path, self._backup_path)
            logging.info("Created initial backup")

    def manage_workspace(self):
        # 备份
        self.create_backup()
        self.clean_workspace()

    def clean_workspace(self):
        # 还原备份
        self.restore_backup()
        # 清理
        if os.path.exists(self._app_dir):
            shutil.rmtree(self._app_dir, onexc=self._handle_remove_readonly)
            logging.debug("Cleaned app directory")

    def restore_changes(self):
        self.clean_workspace()
        if os.path.exists(self._backup_path):
            os.remove(self._backup_path)

    def load_files(self):
        """加载所有代码文件到内存"""
        code_files = self.collect_code_files()
        for file in code_files:
            if os.path.exists(file):
                self.files_cache[file] = read_file(file, strip_empty=False)

    def replace_content(self, file_content):
        """执行内容替换的核心逻辑"""
        if not file_content:
            return file_content

        for line in self.rule_contents:
            try:
                if is_comment_line(line):
                    continue
                old_val, new_val = parse_replace_rule(line)
                if is_regex_pattern(old_val):
                    pattern = re.compile(old_val[1:-1])
                    file_content = pattern.sub(new_val, file_content)
                else:
                    file_content = file_content.replace(old_val, new_val)

            except ValueError as e:
                logging.error(f"Skipping invalid rule: {line} → {str(e)}")
            except re.error as e:
                logging.error(f"Regex error: {line} → {str(e)}")

        return file_content

    def replace_rules(self):
        """规则替换"""
        for file_path in self.files_cache:
            self.files_cache[file_path] = self.replace_content(self.files_cache[file_path])

    def write_files(self):
        """将修改后的内容写入文件"""
        for file_path, content in self.files_cache.items():
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(content)

    def collect_code_files(self):
        """获取所有代码文件路径"""
        prefix_links = [
            os.path.join(self._app_dir, "background-process", "assets"),
            os.path.join(self._app_dir, "ui-process", "assets"),
            os.path.join(self._app_dir, "main-process"),
        ]
        code_files = []
        for prefix in prefix_links:
            for root, _, files in os.walk(prefix):
                if self.args.style:
                    code_files.extend([os.path.join(root, f) for f in files if f.endswith((".js", ".css"))])
                else:
                    code_files.extend([os.path.join(root, f) for f in files if f.endswith(".js")])
        return code_files

    def apply_changes(self):
        """规则替换功能"""
        start_time = time.monotonic()
        self.manage_workspace()
        self.decompress_asar()
        self.load_rules()
        self.load_files()
        self.replace_rules()
        self.write_files()
        self.pack_to_asar()
        elapsed = time.monotonic() - start_time
        logging.info(f"Replacement done in {elapsed:.2f} seconds.")

    def find_in_content(self):
        """文件内容搜索功能"""
        code_files = self.collect_code_files()
        if not os.path.exists(self._app_dir):
            self.decompress_asar()
        find_terms = self.args.find
        found_files = []
        for file_path in code_files:
            file_content = read_file(file_path, strip_empty=False)
            if file_content and all(term in file_content for term in find_terms):
                found_files.append(file_path)
        if found_files:
            logging.info(f"Found all terms {find_terms} in: {found_files}")
        else:
            logging.warning(f"No results found for terms {find_terms}.")


def run_command(cmd, shell=False):
    """执行系统命令"""
    logging.info(f"Running command: {cmd}")
    try:
        subprocess.run(cmd, shell=shell, check=True)
    except subprocess.CalledProcessError as e:
        logging.error(f"Command failed: {e}")
        sys.exit(1)
    except Exception as e:
        logging.error(f"Error: {e}")
        sys.exit(1)


def read_file(file_path, strip_empty=True):
    """安全读取文件内容"""
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return [line.rstrip("\r\n") for line in file if line.strip()] if strip_empty else file.read()
    except Exception as e:
        logging.error(f"Read error: {file_path} - {e}")
        sys.exit(1)


def is_comment_line(line):
    """判断是否为注释行"""
    return line.strip().startswith("#")


def is_regex_pattern(s):
    """判断是否为正则表达式模式(/pattern/格式)"""
    return len(s) > 1 and s.startswith("/") and s.endswith("/") and "//" not in s


def parse_replace_rule(rule):
    """分割替换规则"""
    if "|" not in rule:
        raise ValueError("Invalid replacement rule format.")
    # 最多分割一次
    return rule.split("|", 1)


def is_valid_path(path):
    """验证路径是否合法"""
    return path and os.path.isdir(path)


def check_asar_existence(path):
    """检查指定路径下是否存在 app.asar 文件"""
    return os.path.exists(os.path.join(path, "app.asar"))


def check_asar_installed():
    """检查是否安装了 asar 命令"""
    run_command("asar --version", shell=True)


def select_directory(title):
    """弹出文件夹选择对话框, 手动文件夹路径"""
    try:
        root = tk.Tk()
        root.withdraw()
        selected_path = filedialog.askdirectory(title=title)
        root.destroy()
        return selected_path if is_valid_path(selected_path) else None
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        sys.exit(1)


def get_termius_path():
    """获取 Termius 的路径"""
    default_paths = {
        "Windows": lambda: os.path.join(os.getenv("USERPROFILE"), "AppData", "Local", "Programs", "Termius", "resources"),
        "Darwin": lambda: "/Applications/Termius.app/Contents/Resources",
        "Linux": lambda: "/opt/Termius/resources"
    }
    system = platform.system()
    path_generator = default_paths.get(system)

    if path_generator:
        # 调用 lambda 函数生成路径
        termius_path = path_generator()
    else:
        logging.error(f"Unsupported OS: {system}")
        sys.exit(1)
    if not check_asar_existence(termius_path):
        logging.warning(f"Termius app.asar file not found at: {os.path.join(termius_path, 'app.asar')}")
        logging.info("Please select the correct Termius folder.")
        termius_path = select_directory("Please select the Termius path containing app.asar.")
        if not termius_path or not check_asar_existence(termius_path):
            logging.error("Valid Termius app.asar file not found. Exiting.")
            sys.exit(1)

    return termius_path


def main():
    parser = argparse.ArgumentParser(description="Modify Termius application.")
    parser.add_argument("-t", "--trial", action="store_true", help="Activate professional edition trial.")
    parser.add_argument("-k", "--skip-login", action="store_true", help="Disable authentication workflow.")
    parser.add_argument("-l", "--localize", action="store_true", help="Enable localization patch (Chinese translation/adaptation).")
    parser.add_argument("-s", "--style", action="store_true", help="UI/UX customization preset.")
    parser.add_argument("-r", "--restore", action="store_true", help="Restore software to initial state.")
    parser.add_argument("-f", "--find", nargs="+", help="Multi-mode search operation.")
    args = parser.parse_args()

    # 如果没有提供参数，默认执行 `--localize`
    if not any((args.trial, args.find, args.style, args.skip_login, args.localize, args.restore)):
        args.localize = True

    check_asar_installed()
    termius_path = get_termius_path()
    modifier = TermiusModifier(termius_path, args)

    if any((args.trial, args.style, args.skip_login, args.localize)):
        modifier.apply_changes()
    elif args.find:
        modifier.find_in_content()
    elif args.restore:
        modifier.restore_changes()
    else:
        logging.error("Invalid command. Use '--help'.")


if __name__ == "__main__":
    main()
