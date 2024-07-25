# coding=utf-8
from asdl.transition_system import TransitionSystem, GenTokenAction

try:
    from cStringIO import StringIO
except:
    from io import StringIO

# from collections import Iterable
from asdl.asdl import *
from asdl.asdl_ast import RealizedField, AbstractSyntaxTree

from common.registerable import Registrable


def commit_node_to_ast(grammar, commit_tokens, start_idx):
    node_name = commit_tokens[start_idx]
    i = start_idx
    if node_name in ['after', 'committer', 'author', 'path', 'before', 'req_deg', ]:
        # it's a predicate
        prod = grammar.get_prod_by_ctr_name('Apply')
        pred_field = RealizedField(prod['predicate'], value=node_name)

        arg_ast_nodes = []
        i += 1
        assert commit_tokens[i] == '('
        while True:
            i += 1
            arg_ast_node, end_idx = commit_node_to_ast(grammar, commit_tokens, i)
            arg_ast_nodes.append(arg_ast_node)

            i = end_idx
            if i >= len(commit_tokens): break
            if commit_tokens[i] == ')':
                i += 1
                break

            assert commit_tokens[i] == ','

        arg_field = RealizedField(prod['arguments'], arg_ast_nodes)
        ast_node = AbstractSyntaxTree(prod, [pred_field, arg_field])
    elif node_name is not None:
        # it's a variable
        prod = grammar.get_prod_by_ctr_name('Variable')
        ast_node = AbstractSyntaxTree(prod,
                                      [RealizedField(prod['variable'], value=node_name)])
        i += 1
    else:
        raise NotImplementedError

    print(ast_node)
    return ast_node, i


def commit_expr_to_ast_helper(grammar, commit_tokens, start_idx=0):
    i = start_idx
    if commit_tokens[i] == '(':
        i += 1

    parsed_nodes = []
    while True:

        if commit_tokens[i] == '(':
            ast_node, end_idx = commit_expr_to_ast_helper(grammar, commit_tokens, i)
            parsed_nodes.append(ast_node)
            i = end_idx
        else:
            ast_node, end_idx = commit_node_to_ast(grammar, commit_tokens, i)
            parsed_nodes.append(ast_node)
            i = end_idx

        if i >= len(commit_tokens): break
        if commit_tokens[i] == ')':
            i += 1
            break

        if commit_tokens[i] == ',':
            # and
            i += 1


    assert parsed_nodes
    if len(parsed_nodes) > 1:
        prod = grammar.get_prod_by_ctr_name('And')
        return_node = AbstractSyntaxTree(prod, [RealizedField(prod['arguments'], parsed_nodes)])
    else:
        return_node = parsed_nodes[0]

    return return_node, i


def commit_expr_to_ast(grammar, commit_expr):
    commit_tokens = commit_expr.strip().split(' ')
    return commit_expr_to_ast_helper(grammar, commit_tokens, start_idx=0)[0]


def ast_to_commit_expr(asdl_ast):
    sb = StringIO()
    constructor_name = asdl_ast.production.constructor.name
    if constructor_name == 'Apply':
        predicate = asdl_ast['predicate'].value
        sb.write(predicate)
        sb.write(' (')
        for i, arg in enumerate(asdl_ast['arguments'].value):
            arg_val = arg.fields[0].value
            if i == 0:
                sb.write(' ')
            else:
                sb.write(' , ')
            sb.write(arg_val)

        sb.write(' )')
    elif constructor_name == 'And':
        for i, arg_ast in enumerate(asdl_ast['arguments'].value):
            arg_str = ast_to_commit_expr(arg_ast)
            if i > 0: sb.write(' , ')
            sb.write(arg_str)
    #print(sb.getvalue())
    return sb.getvalue()


def is_equal_ast(this_ast, other_ast):
    if not isinstance(other_ast, this_ast.__class__):
        return False

    if this_ast == other_ast:
        return True

    if isinstance(this_ast, AbstractSyntaxTree):
        if this_ast.production != other_ast.production:
            return False

        if len(this_ast.fields) != len(other_ast.fields):
            return False

        for i in range(len(this_ast.fields)):
            if this_ast.production.constructor.name in ('And', 'Or') and this_ast.fields[i].name == 'arguments':
                this_field_val = sorted(this_ast.fields[i].value, key=lambda x: x.to_string())
                other_field_val = sorted(other_ast.fields[i].value, key=lambda x: x.to_string())
            else:
                this_field_val = this_ast.fields[i].value
                other_field_val = other_ast.fields[i].value

            if not is_equal_ast(this_field_val, other_field_val): return False
    elif isinstance(this_ast, list):
        if len(this_ast) != len(other_ast): return False

        for i in range(len(this_ast)):
            if not is_equal_ast(this_ast[i], other_ast[i]): return False
    else:
        return this_ast == other_ast

    return True


#@Registrable.register('commit')
class CommitTransitionSystem(TransitionSystem):
    def compare_ast(self, hyp_ast, ref_ast):
        return is_equal_ast(hyp_ast, ref_ast)

    def ast_to_surface_code(self, asdl_ast):
        return ast_to_commit_expr(asdl_ast)

    def surface_code_to_ast(self, code):
        return commit_expr_to_ast(self.grammar, code)

    def hyp_correct(self, hyp, example):
        return is_equal_ast(hyp.tree, example.tgt_ast)

    def tokenize_code(self, code, mode):
        return code.split(' ')

    def get_primitive_field_actions(self, realized_field):
        assert realized_field.cardinality == 'single'
        if realized_field.value is not None:
            return [GenTokenAction(realized_field.value)]
        else:
            return []


if __name__ == '__main__':
    pass
