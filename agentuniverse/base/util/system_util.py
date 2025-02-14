# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/3/14 10:42
# @Author  : fanen.lhy
# @Email   : fanen.lhy@antgroup.com
# @FileName: system_util.py
import os
from pathlib import Path
import importlib

PROJECT_ROOT_PATH = None


def get_project_root_path() -> Path:
    """Get the project root path."""
    global PROJECT_ROOT_PATH
    if PROJECT_ROOT_PATH:
        return PROJECT_ROOT_PATH
    current_work_directory = Path.cwd()
    root_path = current_work_directory.parents[1]
    PROJECT_ROOT_PATH = root_path
    return root_path


def parse_dynamic_str(param: str):
    """
    Translate a string, firstly attempting to parse it as a full path to a
    parameterless function. If it can be correctly imported, return the result
    of the function execution, otherwise return the original string.
    This is useful in scenarios where it's inconvenient to write the real
    value directly, such as with secret keys.
    """
    try:
        parts = param.rsplit('.', 1)
        if len(parts) == 2:
            module_path, func_name = parts
            module = importlib.import_module(module_path)
            func = getattr(module, func_name)
            if callable(func):
                return func()
            else:
                return param
        else:
            return param
    except (ImportError, AttributeError, Exception):
        return param


def get_module_path(yaml_path: str, root_name: str) -> str:
    """
    Convert a YAML file path to its corresponding Python module path.
    This function takes a YAML file path and a root package name, and returns the full Python module path.
    For example, if yaml_path is '/path/to/root_pkg/sub_pkg/demo_agent.yaml' and root_name is 'root_pkg',
    it will return 'root_pkg.sub_pkg.demo_agent'

    Args:
        yaml_path: The full path to the YAML file
        root_name: The name of the root package that serves as the starting point for the module path

    Returns:
        str: The full Python module path corresponding to the YAML file location

    Raises:
        FileNotFoundError: If the corresponding Python file doesn't exist
    """

    # Get the directory of the YAML file and the filename (without extension)
    dir_path = os.path.dirname(yaml_path)
    file_name = os.path.splitext(os.path.basename(yaml_path))[0]

    # Check if the corresponding Python file exists in the same directory
    py_file = os.path.join(dir_path, f"{file_name}.py")
    if not os.path.isfile(py_file):
        raise FileNotFoundError(f"Corresponding Python file not found for YAML file: {yaml_path}")

    # Get the absolute path of the directory and split it into components
    abs_dir_path = os.path.abspath(dir_path)
    path_parts = abs_dir_path.split(os.sep)

    try:
        # Find the position of the root path
        root_index = path_parts.index(root_name)
    except ValueError:
        raise FileNotFoundError(f"Corresponding Python file not found for YAML file: {yaml_path}")

    # Extract the directory parts after the root path
    relevant_dirs = path_parts[root_index + 1:]

    # Construct the module path
    module_parts = [root_name] + relevant_dirs + [file_name]
    module_path = ".".join(module_parts)

    return module_path
