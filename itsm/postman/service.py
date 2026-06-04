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
            "headers.X-Bkapi-Authorization.bk_app_code",
            "headers.X-Bkapi-Authorization.bk_app_secret",
            "headers.X-Bkapi-Authorization.access_token",
            "headers.X-Bkapi-Authorization.bk_username",
            "headers.X-Bkapi-Authorization.bk_ticket"
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
            ast.Constant,          # Python 3.8+
            ast.Str, ast.Num,      # Python 3.7 兼容
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

            # 5. 禁止 Subscript 的非法下标（如数字下标用于 dict 可能危险，但字符串下标允许）
            #    这里不做过度限制，因为 response['data'] 是正常用法

        # 如果走到这里，说明通过了校验
        return

