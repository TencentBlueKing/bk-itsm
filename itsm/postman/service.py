import ast
import json
import re
from typing import Dict, Any

from common.log import logger
from itsm.meta.services.context import ContextService


class RunApiService:


    # before_req 默认白名单：即使数据库未配置，也强制校验这些字段
    # 格式与 DB 配置保持一致，使用全路径格式
    DEFAULT_BEFORE_REQ_WHITELIST = {
        "headers": [
            "headers.*",
        ]
    }

    # map_code 默认白名单：对 map_code 中访问的 response 路径进行校验
    # 未配置白名单时，默认允许访问 response 的所有路径（即不做限制）
    # 一旦配置了白名单，则 map_code 中只能访问白名单中列出的 response 路径
    DEFAULT_MAP_CODE_WHITELIST = {
        "response": [
            "response.*",
        ]
    }

    def get_context_verify_data(self, key: str, user_data: dict) -> tuple[bool, str]:
        context = ContextService()
        
        # 1. 基础白名单（硬编码，不可绕过）
        whitelist_config = {
            k: list(v) for k, v in self.DEFAULT_BEFORE_REQ_WHITELIST.items()
        }
        
        # 2. 数据库扩展白名单（叠加到基础白名单上）
        extra_whitelist = context.get_context_value_dict(key)
        if extra_whitelist:
            for config_key, allowed_paths in extra_whitelist.items():
                if isinstance(allowed_paths, list):
                    config_key_lower = config_key.lower()
                    if config_key_lower in whitelist_config:
                        # 追加到现有类别
                        whitelist_config[config_key_lower].extend(
                            p.lower() for p in allowed_paths
                        )
                    else:
                        # 新增类别
                        whitelist_config[config_key_lower] = [
                            p.lower() for p in allowed_paths
                        ]
                else:
                    logger.warning(
                        f"扩展白名单配置 '{config_key}' 的值不是数组格式，跳过"
                    )
        
        # 扁平化所有允许的路径
        allowed_paths = set()
        for config_key, paths in whitelist_config.items():
            if isinstance(paths, list):
                for p in paths:
                    allowed_paths.add(p.lower())
            else:
                logger.warning(f"白名单配置 '{config_key}' 的值不是数组格式，跳过")
        
        user_paths = self._build_user_paths(user_data)
        
        # 校验
        for user_path, value in user_paths.items():
            normalized_user_path = user_path.lower()

            matched = False
            for allowed_path in allowed_paths:
                # 精确匹配
                if normalized_user_path == allowed_path:
                    matched = True
                    break
                # 通配符匹配
                if allowed_path.endswith(".*"):
                    prefix = allowed_path[:-2]
                    if normalized_user_path.startswith(prefix):
                        matched = True
                        break
            
            if not matched:
                return False, f"不允许注入 '{user_path}' 字段，该路径不在白名单中"
        
        return True, ""
    
    
    def _build_user_paths(self, user_data: Dict[str, Any], parent_key: str = "") -> Dict[str, Any]:
        """递归获取用户输入的所有的path，只收集叶子节点"""
        paths = {}
        
        for key, value in user_data.items():
            current_path = f"{parent_key}.{key}" if parent_key else key
            
            # 如果 value 是 dict，递归处理，不收集当前路径
            if isinstance(value, dict):
                sub_paths = self._build_user_paths(value, current_path)
                paths.update(sub_paths)
            # 如果 value 是字符串，尝试解析为 JSON
            elif isinstance(value, str):
                try:
                    parsed_value = json.loads(value)
                    # 如果解析后是 dict，递归处理，不收集当前路径
                    if isinstance(parsed_value, dict):
                        sub_paths = self._build_user_paths(parsed_value, current_path)
                        paths.update(sub_paths)
                    else:
                        # 解析后不是 dict，作为叶子节点收集当前路径
                        paths[current_path] = value
                except (json.JSONDecodeError, TypeError):
                    # 不是 JSON 字符串，作为叶子节点收集当前路径
                    paths[current_path] = value
            else:
                # 其他类型，作为叶子节点收集当前路径
                paths[current_path] = value
        
        return paths

    @staticmethod
    def inner_of_update(s: str) -> Dict[str, Any]:
        """从代码字符串中提取 update(...) 中的字典参数
        
        支持以下格式：
        - query_params.update({"key": "value"})
        - body.update({'key': 'value'})
        """
        # 找到 update( 的位置
        pattern = r'\bupdate\s*\('
        match = re.search(pattern, s, flags=re.S)
        if not match:
            raise ValueError('输入结构错误：未找到 update() 调用')
        
        # 找到 '(' 的位置，然后找到匹配的 ')' 的位置（处理嵌套括号）
        start = match.end() - 1  # '(' 的位置
        depth = 1
        end = start + 1
        
        while end < len(s) and depth > 0:
            if s[end] == '(':
                depth += 1
            elif s[end] == ')':
                depth -= 1
            end += 1
        
        if depth != 0:
            raise ValueError('输入结构错误：括号不匹配')
        
        # 提取括号内的内容（去掉外层的括号）
        content = s[start + 1:end - 1].strip()
        
        try:
            result = ast.literal_eval(content)
            if not isinstance(result, dict):
                raise ValueError('update() 参数必须是一个字典')
            return result
        except (SyntaxError, ValueError) as e:
            raise ValueError(f'解析 update() 参数失败: {str(e)}')

    @staticmethod
    def inner_of_map(s: str) -> None:
        """
        校验 map_code 字符串的安全性。

        允许的 AST 节点白名单：
        - Module, Expr
        - Call, Attribute
        - Name (id 必须是 'response')
        - Load, Store, Del (上下文)
        - Str, Constant (字符串常量)
        - Dict, List, Tuple
        - Num, Constant (数字常量)
        - Subscript, Index (下标访问)
        - Assign, AugAssign (赋值语句)
        - keyword (关键字参数)
        - JoinedStr, FormattedValue (f-string)

        禁止的行为：
        - 访问 response 以外的变量
        - 调用未明确允许的方法
        - 导入语句、函数定义等

        :param s: 用户输入的 map_code 字符串
        :raises ValueError: 如果包含不允许的语法
        """

        # 允许的基础 AST 节点类型
        ALLOWED_NODES = {
            ast.Module, ast.Expr,
            ast.Call, ast.Attribute,
            ast.Name,
            ast.Load, ast.Store, ast.Del,
            ast.Constant,  # Python 3.8+
            ast.Str, ast.Num,  # Python 3.7 兼容
            ast.Dict, ast.List, ast.Tuple, ast.Set,
            ast.Subscript, ast.Index,
            ast.Assign, ast.AugAssign,
            ast.keyword,
            ast.JoinedStr, ast.FormattedValue,
            # 常见安全运算
            ast.BinOp, ast.Add, ast.Sub, ast.Mult, ast.Div, ast.FloorDiv,
            ast.Mod, ast.Pow,
            ast.UnaryOp, ast.UAdd, ast.USub, ast.Not,
            ast.Compare,
            ast.Eq, ast.NotEq, ast.Lt, ast.LtE, ast.Gt, ast.GtE,
            ast.And, ast.Or,
            ast.BoolOp,
            ast.IfExp,  # 三元表达式
            # 推导式（由 RestrictedPython 沙箱二次保护）
            ast.ListComp, ast.DictComp, ast.SetComp, ast.GeneratorExp,
            ast.comprehension,
        }

        # response 对象上允许调用的方法名
        ALLOWED_METHODS = {'update', 'pop', 'get'}

        try:
            tree = ast.parse(s)
        except SyntaxError as e:
            raise ValueError(f"map_code 语法错误: {str(e)}")

        for node in ast.walk(tree):
            # 1. 校验节点类型在白名单中
            if type(node) not in ALLOWED_NODES:
                raise ValueError(
                    f"map_code 包含不允许的语法: {type(node).__name__}"
                )

            # 2. 校验 Name 节点：只能是 'response'
            if isinstance(node, ast.Name):
                if node.id != 'response':
                    raise ValueError(
                        f"map_code 不允许访问变量 '{node.id}'，只允许访问 'response'"
                    )

            # 3. 校验 Attribute：不允许访问任意属性，只允许调用 ALLOWED_METHODS
            if isinstance(node, ast.Attribute):
                if node.attr not in ALLOWED_METHODS:
                    raise ValueError(
                        f"map_code 不允许调用方法 '{node.attr}'"
                    )

            # 4. 校验 Assign / AugAssign：只允许 response.xxx = ... 这样的左值
            if isinstance(node, (ast.Assign, ast.AugAssign)):
                for target in ast.walk(node):
                    if isinstance(target, ast.Name) and target.id != 'response':
                        raise ValueError(
                            f"map_code 不允许对变量 '{target.id}' 赋值"
                        )

            # 5. 校验 Subscript 的下标必须是字符串常量
            #    不允许数字、变量或表达式作为下标（如 response[0]、response[dynamic_var]）
            if isinstance(node, ast.Subscript):
                slice_node = node.slice
                # Python 3.8 及以下，slice 外层包裹了 ast.Index
                if isinstance(slice_node, ast.Index):
                    slice_node = slice_node.value
                # 下标必须是字符串常量
                if isinstance(slice_node, ast.Str):
                    pass  # 字符串常量，允许
                elif isinstance(slice_node, ast.Constant) and isinstance(slice_node.value, str):
                    pass  # 字符串常量（Python 3.8+），允许
                else:
                    raise ValueError(
                        "map_code 的下标访问仅支持字符串常量，"
                        "不允许数字、变量或表达式作为下标"
                    )

        # 如果走到这里，说明通过了校验
        return

    def _extract_map_code_paths(self, s: str) -> set:
        """从 map_code 的 AST 中提取用户访问的 response 路径

        提取规则：
        - response['key'] / response["key"] → response.key
        - response.key（非方法调用）→ response.key
        - 嵌套访问 response['data']['list'] → response.data.list
        - response.get('key', ...) → response.key（从第一个参数提取实际访问路径）
        - response.pop('key') → response.key（从第一个参数提取实际访问路径）
        - response.update({'key': val, ...}) → response.key, ...（从字典参数提取所有键路径）
        - 链式调用 response.pop("data",{}).get("bugs", []) → response.data.bugs
        - 方法调用本身不产生 response.get / response.pop / response.update 路径
        """
        try:
            tree = ast.parse(s)
        except SyntaxError:
            return set()

        paths = set()

        def _extract_str(node):
            """从 AST 节点中提取字符串常量值"""
            if isinstance(node, ast.Str):
                return node.s
            if isinstance(node, ast.Constant) and isinstance(node.value, str):
                return node.value
            return None

        def _extract_dict_keys(node):
            """从 AST 节点中提取字典的所有键（字符串键）"""
            keys = []
            if isinstance(node, ast.Dict):
                for key_node in node.keys:
                    key_str = _extract_str(key_node)
                    if key_str is not None:
                        keys.append(key_str)
            return keys

        def _eval_node(node):
            """递归求值一个 AST 节点，返回其代表的 response 路径

            返回值：
            - 字符串：该节点代表的 response 路径（如 'response.data'）
            - None：该节点不涉及 response 访问，或无法静态推断路径

            核心设计：
            - 对于 Call 节点，返回方法调用结果的路径（而非方法名路径）
            - 对于链式调用 response.pop("x").get("y")，
              先递归求值 pop 得到 'response.x'，再以 'response.x' 为基础求值 get
            """
            if isinstance(node, ast.Name):
                if node.id == 'response':
                    return 'response'
                return None

            if isinstance(node, ast.Attribute):
                parent = _eval_node(node.value)
                if parent is not None:
                    return f"{parent}.{node.attr}"
                return None

            if isinstance(node, ast.Subscript):
                parent = _eval_node(node.value)
                if parent is None:
                    return None
                slice_node = node.slice
                if isinstance(slice_node, ast.Index):
                    slice_node = slice_node.value
                key = _extract_str(slice_node) if isinstance(slice_node, (ast.Str, ast.Constant)) else None
                if key is not None:
                    return f"{parent}.{key}"
                return parent

            if isinstance(node, ast.Call):
                return _eval_call(node)

            return None

        def _eval_call(node):
            """处理方法调用节点，提取参数中实际访问的 response 路径

            返回值：方法调用结果对应的 response 路径

            - response.get('key', ...) → 提取 response.key，返回 'response.key'
            - response.pop('key') → 提取 response.key，返回 'response.key'
            - response.update({...}) → 提取字典中的所有键路径，返回 'response'（update 返回 None）
            """
            if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Attribute):
                return None

            method_name = node.func.attr

            # 递归求值 func.value，获取调用者的路径
            # 对于链式调用 response.pop("x").get("y")：
            #   get 的 func.value 是 pop(...) 这个 Call 节点
            #   _eval_node(pop(...)) 会递归处理 pop 并返回 'response.x'
            caller_path = _eval_node(node.func.value)
            if caller_path is None:
                return None

            if method_name == 'get':
                if node.args:
                    key_str = _extract_str(node.args[0])
                    if key_str is not None:
                        result_path = f"{caller_path}.{key_str}"
                        paths.add(result_path)
                        return result_path
                return None

            elif method_name == 'pop':
                if node.args:
                    key_str = _extract_str(node.args[0])
                    if key_str is not None:
                        result_path = f"{caller_path}.{key_str}"
                        paths.add(result_path)
                        return result_path
                return None

            elif method_name == 'update':
                # 位置参数中的字典
                for arg in node.args:
                    for key_str in _extract_dict_keys(arg):
                        paths.add(f"{caller_path}.{key_str}")
                # 关键字参数
                for kw in node.keywords:
                    if kw.arg:
                        paths.add(f"{caller_path}.{kw.arg}")
                # update 返回 None，不产生结果路径
                return None

            return None

        # 收集所有作为 Call 节点 func 的 Attribute 节点的 id
        # 这些 Attribute 的 attr 是方法名（如 get/pop/update），不应作为数据路径提取
        call_func_attr_ids = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                call_func_attr_ids.add(id(node.func))

        # 递归遍历整个 AST 树，提取路径
        def _walk(node):
            """递归遍历 AST 树，对每个节点调用 _eval_node 提取路径"""
            # 跳过作为 Call.func 的 Attribute 节点（方法名不是数据字段）
            if id(node) in call_func_attr_ids:
                # 但仍需遍历其子节点
                for child in ast.iter_child_nodes(node):
                    _walk(child)
                return

            # 先对当前节点求值
            path = _eval_node(node)
            if path is not None and path != 'response':
                paths.add(path)

            # 然后递归遍历子节点
            for child in ast.iter_child_nodes(node):
                _walk(child)

        _walk(tree)

        return paths

    def verify_map_code_whitelist(self, map_code: str) -> tuple:
        """校验 map_code 中访问的 response 路径是否在白名单中

        :param map_code: 用户输入的 map_code 字符串
        :returns: (is_valid, message) 元组
        """
        # 提取 map_code 中访问的 response 路径
        user_paths = self._extract_map_code_paths(map_code)
        if not user_paths:
            return True, ""

        # 1. 基础白名单（硬编码，不可绕过）
        whitelist_config = {
            k: list(v) for k, v in self.DEFAULT_MAP_CODE_WHITELIST.items()
        }

        # 2. 数据库扩展白名单（叠加到基础白名单上）
        context = ContextService()
        extra_whitelist = context.get_context_value_dict("run_api_map_code")
        if extra_whitelist:
            for config_key, allowed_paths in extra_whitelist.items():
                if isinstance(allowed_paths, list):
                    config_key_lower = config_key.lower()
                    if config_key_lower in whitelist_config:
                        whitelist_config[config_key_lower].extend(
                            p.lower() for p in allowed_paths
                        )
                    else:
                        whitelist_config[config_key_lower] = [
                            p.lower() for p in allowed_paths
                        ]
                else:
                    logger.warning(
                        f"扩展白名单配置 '{config_key}' 的值不是数组格式，跳过"
                    )

        # 扁平化所有允许的路径
        allowed_paths = set()
        for config_key, paths in whitelist_config.items():
            if isinstance(paths, list):
                for p in paths:
                    allowed_paths.add(p.lower())
            else:
                logger.warning(f"白名单配置 '{config_key}' 的值不是数组格式，跳过")

        # 校验
        for user_path in user_paths:
            normalized_user_path = user_path.lower()

            # 禁止访问 dunder 属性（以 .__ 开头的路径段），防止沙箱逃逸
            # 例如 response.data.__class__、response.data.__mro__ 等
            if ".__" in normalized_user_path:
                return False, (
                    f"map_code 不允许访问 dunder 属性路径 '{user_path}'，"
                    f"路径中不允许包含 '.__'（如 __class__、__mro__ 等）"
                )

            matched = False
            for allowed_path in allowed_paths:
                # 精确匹配
                if normalized_user_path == allowed_path:
                    matched = True
                    break
                # 通配符匹配
                if allowed_path.endswith(".*"):
                    prefix = allowed_path[:-2]
                    if normalized_user_path.startswith(prefix):
                        # 通配符匹配成功后，仍需检查匹配部分之后的路径段是否为 dunder 属性
                        remaining = normalized_user_path[len(prefix):]
                        # dunder 属性特征：路径段以 __ 开头且以 __ 结尾
                        # 如 __class__、__mro__、__subclasses__、__init__、__dict__ 等
                        if remaining and remaining.startswith("__") and remaining.endswith("__"):
                            matched = False
                            continue
                        matched = True
                        break

            if not matched:
                return False, f"map_code 不允许访问 '{user_path}' 路径，该路径不在白名单中"

        return True, ""
