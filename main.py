import yaml
from lark import Lark, Transformer, v_args, Tree

GRAMMAR = r"""
start: entry*

entry: const_decl
     | mapping

const_decl: NAME "=" value ";"
mapping: NAME "->" dict_expr

?value: NUMBER      -> number
      | STRING      -> string
      | dict_expr   -> dict
      | const_ref   -> const_lookup

dict_expr: "{" pair+ "}"
pair: NAME "->" value "."

const_ref: "^[" NAME "]"

NAME: /[a-zA-Z0-9_]+/
NUMBER: /\d+/
STRING: /q\([^\)]*\)/

%ignore /\s+/
"""

constants = {}

@v_args(inline=False)
class AST(Transformer):
    def start(self, children):
        merged = {}
        for child in children:
            # если элемент Tree, берем его children[0] (он должен быть словарем)
            if isinstance(child, Tree) and child.children:
                content = child.children[0]
                if isinstance(content, dict):
                    merged.update(content)
            elif isinstance(child, dict):
                merged.update(child)
        return merged

    def const_decl(self, children):
        name, value = children
        constants[str(name)] = value
        return {str(name): value}

    def number(self, n):
        return int(n[0])

    def string(self, s):
        return s[0][2:-1]

    def const_lookup(self, tree):
        # tree — это Tree('const_ref', [Token('NAME', 'name')])
        if isinstance(tree, list):
            tree = tree[0]  # если inline=False, может быть списком
        if isinstance(tree, Tree) and tree.data == 'const_ref':
            name_token = tree.children[0]  # берем первый ребенок
        else:
            name_token = tree  # на всякий случай

        # берем value токена
        name_str = name_token.value if hasattr(name_token, 'value') else str(name_token)

        if name_str not in constants:
            raise ValueError(f"Constant '{name_str}' is not defined")
        return constants[name_str]

    def pair(self, children):
        key, value = children
        return (str(key), value)

    def dict_expr(self, children):
        result = {}
        for p in children:
            if isinstance(p, tuple) and len(p) == 2:
                result[p[0]] = p[1]
        return result

    def mapping(self, children):
        name, dict_expr = children
        return {str(name): dict_expr}

def clean_tree(obj):
    if isinstance(obj, list):
        return [clean_tree(e) for e in obj if e not in (None, [], {})]
    elif isinstance(obj, dict):
        return {k: clean_tree(v) for k, v in obj.items() if v not in (None, [], {})}
    elif isinstance(obj, Tree):
        return clean_tree([clean_tree(c) for c in obj.children])
    else:
        return obj


def tree_to_plain(obj):
    if isinstance(obj, Tree):
        if obj.data == 'dict':
            result = {}
            for child in obj.children:
                child_dict = tree_to_plain(child)
                if child_dict:  # пропускаем пустые None
                    result.update(child_dict)
            return result
        elif obj.data == 'pair':
            key, value = obj.children
            return {str(key): tree_to_plain(value)}
        else:
            children = [tree_to_plain(c) for c in obj.children if c is not None]
            if len(children) == 1:
                return children[0]
            return children
    elif isinstance(obj, list):
        return [tree_to_plain(e) for e in obj if e is not None]
    elif isinstance(obj, dict):
        return {k: tree_to_plain(v) for k, v in obj.items() if v is not None}
    else:
        return obj


def main():
    parser = Lark(GRAMMAR, parser="lalr", transformer=AST())
    import sys
    text = sys.stdin.read()

    result = parser.parse(text)

    # Превращаем все Tree в чистые dict/list
    plain_result = tree_to_plain(result)
    clean_result = clean_tree(plain_result)

    yaml.safe_dump(clean_result, sys.stdout, sort_keys=False, allow_unicode=True, default_flow_style=False)




if __name__ == "__main__":
    main()
