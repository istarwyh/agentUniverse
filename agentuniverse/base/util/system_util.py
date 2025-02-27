# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/3/14 10:42
# @Author  : fanen.lhy
# @Email   : fanen.lhy@antgroup.com
# @FileName: system_util.py
import ast
import inspect
import os
from pathlib import Path
import importlib
from typing import Any

from agentuniverse.base.component.component_base import ComponentBase
from agentuniverse.base.component.component_enum import ComponentEnum

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


def process_customized_func(func_expr: str, customized_func_instance: Any) -> str:
    """
    Process the YAML configuration by resolving @FUNC expressions.

    Args:
        func_expr (str): The function expression to process (e.g., '@FUNC(load_api_key("qwen"))').
        customized_func_instance (Any): The instance containing the methods to call.

    Returns:
        str: The result of the function call or the original expression if no @FUNC is found.

    Raises:
        ValueError: If @FUNC expression is provided but `customized_func_instance` is None.
        Exception: If an error occurs while calling the method.
    """
    # Return an empty string if the function expression is None
    if not func_expr or customized_func_instance is None:
        return func_expr

    if func_expr.startswith('@FUNC(') and customized_func_instance is None:
        raise ValueError(f"customized_func is required to resolve @FUNC expression {func_expr}.")

    # Process @FUNC expressions
    if func_expr.startswith('@FUNC(') and func_expr.endswith(')'):
        # Extract the method name and arguments
        func_expr = func_expr[len('@FUNC('):-1]  # Remove '@FUNC(' and ')'
        # Parse the function call expression using AST
        try:
            parsed_expr = ast.parse(func_expr, mode='eval')
        except SyntaxError as e:
            raise ValueError(f"Invalid function expression: {func_expr}. Error: {e}")

        # Ensure the expression is a function call
        if not isinstance(parsed_expr.body, ast.Call):
            raise ValueError(f"Expected a function call, got: {func_expr}")

        # Extract function name and arguments
        func_name = parsed_expr.body.func.id
        args = [ast.literal_eval(arg) for arg in parsed_expr.body.args]
        kwargs = {kw.arg: ast.literal_eval(kw.value) for kw in parsed_expr.body.keywords}

        # Check if the method exists in the customized function instance
        if hasattr(customized_func_instance, func_name):
            func = getattr(customized_func_instance, func_name)

            # Validate function signature
            sig = inspect.signature(func)
            try:
                sig.bind(*args, **kwargs)  # Ensure arguments match the function signature
            except TypeError as e:
                raise ValueError(f"Invalid arguments for method {func_name}: {e}")

            # Call the method and return the result
            try:
                res = func(*args, **kwargs)
                return res
            except Exception as e:
                raise Exception(f"Failed to execute method {func_name}: {str(e)}")
        else:
            raise AttributeError(f"Method {func_name} not found in customized_func.")

    return func_expr


def process_dict_with_funcs(input_dict: dict, customized_func_instance: Any) -> dict:
    """
    Process a dictionary by resolving @FUNC expressions in its values.

    Args:
        input_dict (dict): The dictionary to process.
        customized_func_instance (Any): The instance containing the methods to call.

    Returns:
        dict: A new dictionary with resolved @FUNC expressions.

    Raises:
        ValueError: If @FUNC expression is provided but `customized_func_instance` is None.
        Exception: If an error occurs while calling the method.
    """
    if not input_dict or customized_func_instance is None:
        return input_dict

    processed_dict = {}
    for key, value in input_dict.items():
        if isinstance(value, str) and value.startswith('@FUNC('):
            # Process the @FUNC expression
            processed_dict[key] = process_customized_func(value, customized_func_instance)
        elif isinstance(value, dict):
            # Recursively process nested dictionaries
            processed_dict[key] = process_dict_with_funcs(value, customized_func_instance)
        else:
            # Keep the value as is
            processed_dict[key] = value

    return processed_dict


def is_system_builtin(component_instance: ComponentBase) -> bool:
    """
    Determine if a component is system-built-in based on its type and configuration.

    Args:
        component_instance (ComponentBase): The component instance to check.

    Returns:
        bool: True if the component is system-built-in, False otherwise.
    """
    component_enum: ComponentEnum = component_instance.component_type
    if component_enum is None or not component_instance.component_config_path:
        return False
    if component_enum.value == ComponentEnum.LLM.value:
        # Check if the LLM component is system-built-in
        return "agentuniverse/llm/default" in component_instance.component_config_path
    elif component_enum.value == ComponentEnum.TOOL.value:
        # Check if the Tool component is system-built-in
        return "agentuniverse/agent/action/tool" in component_instance.component_config_path
    return False


def is_api_key_missing(component_instance: ComponentBase, api_key_name: str) -> bool:
    """
    Check if the given API key attribute exists and is empty.

    Args:
        component_instance (ComponentBase): The component instance to check.
        api_key_name (str): The name of the API key attribute.

    Returns:
        bool: True if the API key is missing or empty, False otherwise.
    """
    return hasattr(component_instance, api_key_name) and not getattr(component_instance, api_key_name)


def has_required_api_keys(component_instance: ComponentBase, metadata_module: str) -> bool:
    """
    Check if the component has all required API keys based on the metadata module.

    Args:
        component_instance (ComponentBase): The component instance to check.
        metadata_module (str): The metadata module name.

    Returns:
        bool: True if all required API keys are present, False otherwise.
    """
    api_key_mapping = {
        "google_search": "serper_api_key",
        "search_api": "search_api_key",
        "bing_search": "bing_subscription_key"
    }

    if component_instance is None or not metadata_module:
        return True

    for module_name, api_key_name in api_key_mapping.items():
        if module_name in metadata_module and is_api_key_missing(component_instance, api_key_name):
            return False  # Missing required API key
    return True  # All required API keys are present
