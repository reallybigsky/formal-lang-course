from typing import Set

from antlr4 import *
from pyformlang.finite_automaton import EpsilonNFA

from project.language.dist.FLParser import FLParser
from project.language.dist.FLVisitor import FLVisitor
from project.language.FL_utils import FLValueType, FLValueHolder
from project.graphs import get_nx_graph_by_name
from project.regular_path_queries import intersect_enfa, nfa_iterator, concat
from project.finite_automaton import graph_to_nfa, regex_to_min_dfa


class InterpretError(Exception):
    def __init__(self, ex, ctx):
        self.ex = ex
        self.ctx = ctx

    def __str__(self):
        if self.ctx is None:
            return str(self.ex)
        return f"{ctx_location(self.ctx)}: {self.ex}"


def interpret(program: ParserRuleContext, out=None):
    visitor = InterpretVisitor(out=out)
    try:
        return program.accept(visitor)
    except Exception as e:
        raise InterpretError(e, visitor.ctx) from e


class InterpretVisitor(FLVisitor):
    def __init__(self, out=None):
        self.out = out
        self.scopes = [dict()]
        self.ctx_stack = list()
        self.scopes[0]["true"] = True
        self.scopes[0]["false"] = False

    def enter_ctx(self, ctx: ParserRuleContext):
        self.ctx_stack.append(ctx)

    def exit_ctx(self):
        self.ctx_stack.pop()

    def get_nfa_from_holder(self, holder: FLValueHolder, ctx) -> FLValueHolder:
        if holder.value_type is FLValueType.FiniteAutomataValue:
            return holder
        elif holder.value_type is FLValueType.StringValue:
            casted_value = regex_to_min_dfa(holder.value)
            result = FLValueHolder(
                value=casted_value, ctx=ctx, value_type=FLValueType.FiniteAutomataValue
            )
            return result
        else:
            raise InterpretError(
                "Can not get NFA from " + str(holder.value_type) + " type", ctx
            )

    def get_nfa_with_states_set(
        self, fa: FLValueHolder, states: FLValueHolder, ctx
    ) -> (EpsilonNFA, Set):
        if fa.value_type is FLValueType.FiniteAutomataValue:
            nfa = fa.value
        elif fa.value_type is FLValueType.StringValue:
            nfa = regex_to_min_dfa(fa.value)
        else:
            raise InterpretError(
                "Can not get NFA from " + str(fa.value_type) + " type", ctx
            )

        if states.value_type is FLValueType.SetValue:
            states_set = states.value
        else:
            raise InterpretError(
                "Can not get states from " + str(states.value_type) + " type", ctx
            )

        return nfa, states_set

    def add_starts(
        self, to: FLValueHolder, starts: FLValueHolder, ctx
    ) -> FLValueHolder:
        nfa, starts_set = self.get_nfa_with_states_set(to, starts, ctx)
        for node in starts_set:
            nfa.add_start_state(node)
        result = FLValueHolder(
            value=nfa, ctx=ctx, value_type=FLValueType.FiniteAutomataValue
        )
        return result

    def add_finals(
        self, to: FLValueHolder, finals: FLValueHolder, ctx
    ) -> FLValueHolder:
        nfa, finals_set = self.get_nfa_with_states_set(to, finals, ctx)
        for node in finals_set:
            nfa.add_final_state(node)
        result = FLValueHolder(
            value=nfa, ctx=ctx, value_type=FLValueType.FiniteAutomataValue
        )
        return result

    def set_starts(
        self, to: FLValueHolder, starts: FLValueHolder, ctx
    ) -> FLValueHolder:
        nfa, starts_set = self.get_nfa_with_states_set(to, starts, ctx)
        nfa.start_states.clear()
        for node in starts_set:
            nfa.add_start_state(node)
        result = FLValueHolder(
            value=nfa, ctx=ctx, value_type=FLValueType.FiniteAutomataValue
        )
        return result

    def set_finals(
        self, to: FLValueHolder, finals: FLValueHolder, ctx
    ) -> FLValueHolder:
        nfa, finals_set = self.get_nfa_with_states_set(to, finals, ctx)
        nfa.final_states.clear()
        for node in finals_set:
            nfa.add_final_state(node)
        result = FLValueHolder(
            value=nfa, ctx=ctx, value_type=FLValueType.FiniteAutomataValue
        )
        return result

    def get_reachable(self, value: FLValueHolder, ctx) -> FLValueHolder:
        dfa = value.value
        if value.value_type is FLValueType.StringValue:
            dfa = regex_to_min_dfa(value.value)
        elif value.value_type is not FLValueType.FiniteAutomataValue:
            InterpretError(
                "Cannot get reachable vertices from " + str(value.value_type), ctx
            )
        reachable = dfa._get_reachable_states()
        result = FLValueHolder(
            value=reachable, ctx=ctx, value_type=FLValueType.SetValue
        )
        return result

    def get_vertices(self, value: FLValueHolder, ctx) -> FLValueHolder:
        dfa = value.value
        if value.value_type is FLValueType.StringValue:
            dfa = regex_to_min_dfa(value.value)
        elif value.value_type is not FLValueType.FiniteAutomataValue:
            InterpretError("Cannot get vertices from " + str(value.value_type), ctx)
        reachable = dfa.states
        result = FLValueHolder(
            value=reachable, ctx=ctx, value_type=FLValueType.SetValue
        )
        return result

    def get_edges(self, value: FLValueHolder, ctx) -> FLValueHolder:
        dfa = value.value
        if value.value_type is FLValueType.StringValue:
            dfa = regex_to_min_dfa(value.value)
        elif value.value_type is not FLValueType.FiniteAutomataValue:
            InterpretError("Cannot get edges from " + str(value.value_type), ctx)
        it = nfa_iterator(dfa)
        edges = {(u, l, v) for u, l, v in it}
        result = FLValueHolder(value=edges, ctx=ctx, value_type=FLValueType.SetValue)
        return result

    def get_labels(self, value: FLValueHolder, ctx) -> FLValueHolder:
        dfa = value.value
        if value.value_type is FLValueType.StringValue:
            dfa = regex_to_min_dfa(value.value)
        elif value.value_type is not FLValueType.FiniteAutomataValue:
            InterpretError("Cannot get labels from " + str(value.value_type), ctx)
        labels = dfa.symbols
        result = FLValueHolder(value=labels, ctx=ctx, value_type=FLValueType.SetValue)
        return result

    def compare_holders(
        self, lhs: FLValueHolder, rhs: FLValueHolder, ctx
    ) -> FLValueHolder:
        if lhs.value_type is not rhs.value_type:
            raise InterpretError(
                "Incomparable types: "
                + str(lhs.value_type)
                + " and "
                + str(rhs.value_type),
                ctx,
            )
        result = lhs.value == rhs.value
        return FLValueHolder(value=result, ctx=ctx, value_type=FLValueType.BoolValue)

    def contains_value(
        self, lhs: FLValueHolder, rhs: FLValueHolder, ctx
    ) -> FLValueHolder:
        if (
            lhs.value_type is FLValueType.StringValue
            and rhs.value_type is FLValueType.StringValue
        ):
            result = lhs.value in rhs.value
        elif rhs.value_type is FLValueType.SetValue:
            result = lhs.value in rhs.value
        elif rhs.value_type is FLValueType.FiniteAutomataValue:
            if lhs.value_type is FLValueType.IntValue:
                result = lhs.value in rhs.value.states
            elif lhs.value_type is FLValueType.StringValue:
                result = lhs.value in rhs.value.symbols
            elif lhs.value_type is FLValueType.FiniteAutomataValue:
                result = lhs.value == intersect_enfa(lhs.value, rhs.value)
            else:
                raise InterpretError(
                    "In is not supported by "
                    + str(lhs.value_type)
                    + " and "
                    + str(rhs.value_type),
                    ctx,
                )
        else:
            raise InterpretError(
                "In is not supported by "
                + str(lhs.value_type)
                + " and "
                + str(rhs.value_type),
                ctx,
            )

        return FLValueHolder(value=result, ctx=ctx, value_type=FLValueType.BoolValue)

    def intersect_holders(
        self, lhs: FLValueHolder, rhs: FLValueHolder, ctx
    ) -> FLValueHolder:
        if (
            lhs.value_type is FLValueType.BoolValue
            and rhs.value_type is FLValueType.BoolValue
        ):
            result = lhs.value and rhs.value_type
            result = FLValueHolder(
                value=result, ctx=ctx, value_type=FLValueType.BoolValue
            )
        elif lhs.value_type is FLValueType.StringValue:
            if rhs.value_type is FLValueType.StringValue:
                result = "".join(set(lhs.value).intersection(rhs.value))
                result = FLValueHolder(
                    value=result, ctx=ctx, value_type=FLValueType.StringValue
                )
            elif rhs.value_type is FLValueType.FiniteAutomataValue:
                intersection = intersect_enfa(regex_to_min_dfa(lhs.value), rhs.value)
                result = FLValueHolder(
                    value=intersection,
                    ctx=ctx,
                    value_type=FLValueType.FiniteAutomataValue,
                )
            else:
                raise InterpretError(
                    "Cannot intersect "
                    + str(lhs.value_type)
                    + " and "
                    + str(rhs.value_type),
                    ctx,
                )
        elif (
            lhs.value_type is FLValueType.SetValue
            and rhs.value_type is FLValueType.SetValue
        ):
            result = lhs.value.intersection(rhs.value)
            result = FLValueHolder(
                value=result, ctx=ctx, value_type=FLValueType.SetValue
            )
        elif lhs.value_type is FLValueType.FiniteAutomataValue:
            if rhs.value_type is FLValueType.StringValue:
                intersection = intersect_enfa(lhs.value, regex_to_min_dfa(rhs.value))
                result = FLValueHolder(
                    value=intersection,
                    ctx=ctx,
                    value_type=FLValueType.FiniteAutomataValue,
                )
            elif rhs.value_type is FLValueType.FiniteAutomataValue:
                intersection = intersect_enfa(lhs.value, rhs.value)
                result = FLValueHolder(
                    value=intersection,
                    ctx=ctx,
                    value_type=FLValueType.FiniteAutomataValue,
                )
            else:
                raise InterpretError(
                    "Cannot intersect "
                    + str(lhs.value_type)
                    + " and "
                    + str(rhs.value_type),
                    ctx,
                )
        else:
            raise InterpretError(
                "Cannot intersect "
                + str(lhs.value_type)
                + " and "
                + str(rhs.value_type),
                ctx,
            )

        return result

    def concat_holders(
        self, lhs: FLValueHolder, rhs: FLValueHolder, ctx
    ) -> FLValueHolder:
        if (
            lhs.value_type is FLValueType.BoolValue
            and rhs.value_type is FLValueType.BoolValue
        ):
            result = lhs.value or rhs.value_type
            result = FLValueHolder(
                value=result, ctx=ctx, value_type=FLValueType.BoolValue
            )
        elif lhs.value_type is FLValueType.StringValue:
            if rhs.value_type is FLValueType.StringValue:
                result = lhs.value + rhs.value
                result = FLValueHolder(
                    value=result, ctx=ctx, value_type=FLValueType.StringValue
                )
            elif rhs.value_type is FLValueType.FiniteAutomataValue:
                intersection = concat(regex_to_min_dfa(lhs.value), rhs.value)
                result = FLValueHolder(
                    value=intersection,
                    ctx=ctx,
                    value_type=FLValueType.FiniteAutomataValue,
                )
            else:
                raise InterpretError(
                    "Cannot concat "
                    + str(lhs.value_type)
                    + " and "
                    + str(rhs.value_type),
                    ctx,
                )
        elif (
            lhs.value_type is FLValueType.SetValue
            and rhs.value_type is FLValueType.SetValue
        ):
            result = lhs.value.union(rhs.value)
            result = FLValueHolder(
                value=result, ctx=ctx, value_type=FLValueType.SetValue
            )
        elif lhs.value_type is FLValueType.FiniteAutomataValue:
            if rhs.value_type is FLValueType.StringValue:
                intersection = concat(lhs.value, regex_to_min_dfa(rhs.value))
                result = FLValueHolder(
                    value=intersection,
                    ctx=ctx,
                    value_type=FLValueType.FiniteAutomataValue,
                )
            elif rhs.value_type is FLValueType.FiniteAutomataValue:
                intersection = concat(lhs.value, rhs.value)
                result = FLValueHolder(
                    value=intersection,
                    ctx=ctx,
                    value_type=FLValueType.FiniteAutomataValue,
                )
            else:
                raise InterpretError(
                    "Cannot concat "
                    + str(lhs.value_type)
                    + " and "
                    + str(rhs.value_type),
                    ctx,
                )
        else:
            raise InterpretError(
                "Cannot concat " + str(lhs.value_type) + " and " + str(rhs.value_type),
                ctx,
            )
        return result

    @property
    def ctx(self) -> ParserRuleContext | None:
        if len(self.ctx_stack) == 0:
            return None
        return self.ctx_stack[-1]

    @property
    def scope(self) -> dict[str, FLValueHolder]:
        return self.scopes[-1]

    def return_value_from_scope(self, name: str) -> FLValueHolder:
        try:
            return self.scope[name]
        except KeyError as e:
            raise ValueError(f'name "{str}" is not in scope') from e

    # Visit a parse tree produced by FLParser#program.
    def visitProgram(self, ctx: FLParser.ProgramContext):
        self.enter_ctx(ctx)
        stmts = ctx.stmt()
        for stmt in stmts:
            stmt.accept(self)
        self.exit_ctx()

    # Visit a parse tree produced by FLParser#print.
    def visitPrint(self, ctx: FLParser.PrintContext):
        self.enter_ctx(ctx)
        print(repr(ctx.value.accept(self)), file=self.out)
        self.exit_ctx()

    # Visit a parse tree produced by FLParser#expr_expr.
    def visitExpr_expr(self, ctx: FLParser.Expr_exprContext):
        # self.enter_ctx(self)
        self.enter_ctx(ctx)
        value = ctx.children[1].accept(self)
        self.exit_ctx()
        return value

    # Visit a parse tree produced by FLParser#bind.
    def visitBind(self, ctx: FLParser.BindContext):
        self.enter_ctx(ctx)
        value = ctx.value.accept(self)
        self.scopes[0][ctx.id_.text] = value
        self.exit_ctx()

    # Visit a parse tree produced by FLParser#val_string.
    def visitVal_string(self, ctx: FLParser.Val_stringContext):
        self.enter_ctx(ctx)
        string = FLValueHolder(
            value=eval(ctx.value.text), ctx=ctx, value_type=FLValueType.StringValue
        )
        self.exit_ctx()
        return string

    # Visit a parse tree produced by FLParser#val_int.
    def visitVal_int(self, ctx: FLParser.Val_stringContext):
        self.enter_ctx(ctx)
        integer = FLValueHolder(
            value=eval(ctx.value.text), ctx=ctx, value_type=FLValueType.IntValue
        )
        self.exit_ctx()
        return integer

    # Visit a parse tree produced by FLParser#val_list.
    def visitVal_list(self, ctx: FLParser.Val_listContext):
        self.enter_ctx(ctx)
        try:
            if len(ctx.children[0].children) == 2:
                s = FLValueHolder({}, ctx, FLValueType.SetValue)
            else:
                v = set()
                for x in ctx.children[0].items:
                    v.add(x.accept(self).value)
                s = FLValueHolder(value=v, ctx=ctx, value_type=FLValueType.SetValue)
        except Exception as _:
            raise InterpretError("Invalid set declaration", ctx)
        self.exit_ctx()
        return s

    # Visit a parse tree produced by FLParser#val_id.
    def visitVal_id(self, ctx: FLParser.Val_idContext):
        self.enter_ctx(ctx)
        result = self.return_value_from_scope(ctx.name.text)
        self.exit_ctx()
        return result

    # Visit a parse tree produced by FLParser#expr_set_final.
    def visitExpr_set_final(self, ctx: FLParser.Expr_set_finalContext):
        self.enter_ctx(ctx)
        to = ctx.to.accept(self)
        finals = ctx.final.accept(self)
        result = self.set_finals(to, finals, ctx)
        self.exit_ctx()
        return result

    # Visit a parse tree produced by FLParser#expr_get_final.
    def visitExpr_get_final(self, ctx: FLParser.Expr_get_finalContext):
        self.enter_ctx(ctx)
        value = ctx.value.accept(self)
        dfa = self.get_nfa_from_holder(value, ctx)
        result = FLValueHolder(
            value=dfa.value.final_states, ctx=ctx, value_type=FLValueType.SetValue
        )
        self.exit_ctx()
        return result

    # Visit a parse tree produced by FLParser#expr_add_start.
    def visitExpr_add_start(self, ctx: FLParser.Expr_set_startContext):
        self.enter_ctx(ctx)
        to = ctx.to.accept(self)
        starts = ctx.start.accept(self)
        result = self.add_starts(to, starts, ctx)
        self.exit_ctx()
        return result

    # Visit a parse tree produced by FLParser#expr_add_final.
    def visitExpr_add_final(self, ctx: FLParser.Expr_set_finalContext):
        self.enter_ctx(ctx)
        to = ctx.to.accept(self)
        finals = ctx.final.accept(self)
        result = self.add_finals(to, finals, ctx)
        self.exit_ctx()
        return result

    # Visit a parse tree produced by FLParser#expr_set_start.
    def visitExpr_set_start(self, ctx: FLParser.Expr_set_startContext):
        self.enter_ctx(ctx)
        to = ctx.to.accept(self)
        starts = ctx.start.accept(self)
        result = self.set_starts(to, starts, ctx)
        self.exit_ctx()
        return result

    # Visit a parse tree produced by FLParser#expr_get_start.
    def visitExpr_get_start(self, ctx: FLParser.Expr_get_startContext):
        self.enter_ctx(ctx)
        value = ctx.value.accept(self)
        dfa = self.get_nfa_from_holder(value, ctx)
        result = FLValueHolder(
            value=dfa.value.start_states, ctx=ctx, value_type=FLValueType.SetValue
        )
        self.exit_ctx()
        return result

    # Visit a parse tree produced by FLParser#expr_get_reachable.
    def visitExpr_get_reachable(self, ctx: FLParser.Expr_get_reachableContext):
        self.enter_ctx(ctx)
        value = ctx.value.accept(self)
        result = self.get_reachable(value, ctx)
        self.exit_ctx()
        return result

    # Visit a parse tree produced by FLParser#expr_get_vertices.
    def visitExpr_get_vertices(self, ctx: FLParser.Expr_get_verticesContext):
        self.enter_ctx(ctx)
        value = ctx.value.accept(self)
        result = self.get_vertices(value, ctx)
        self.exit_ctx()
        return result

    # Visit a parse tree produced by FLParser#expr_get_edge.
    def visitExpr_get_edge(self, ctx: FLParser.Expr_get_edgeContext):
        self.enter_ctx(ctx)
        value = ctx.value.accept(self)
        result = self.get_edges(value, ctx)
        self.exit_ctx()
        return result

    # Visit a parse tree produced by FLParser#expr_get_labels.
    def visitExpr_get_labels(self, ctx: FLParser.Expr_get_labelsContext):
        self.enter_ctx(ctx)
        value = ctx.value.accept(self)
        result = self.get_labels(value, ctx)
        self.exit_ctx()
        return result

    # Visit a parse tree produced by FLParser#expr_load.
    def visitExpr_load(self, ctx: FLParser.Expr_loadContext):
        self.enter_ctx(ctx)
        graph = graph_to_nfa(get_nx_graph_by_name(eval(ctx.value.text)))
        result = FLValueHolder(
            value=graph, ctx=ctx, value_type=FLValueType.FiniteAutomataValue
        )
        self.exit_ctx()
        return result

    # Visit a parse tree produced by FLParser#expr_val.
    def visitExpr_val(self, ctx: FLParser.Expr_valContext):
        self.enter_ctx(ctx)
        val = ctx.children[0].accept(self)
        self.exit_ctx()
        return val

    # Visit a parse tree produced by FLParser#expr_var.
    def visitExpr_var(self, ctx: FLParser.Expr_valContext):
        self.enter_ctx(ctx)
        result = self.return_value_from_scope(ctx.name.text)
        self.exit_ctx()
        return result

    # Visit a parse tree produced by FLParser#expr_lambda.
    def visitExpr_lambda(self, ctx: FLParser.Expr_lambdaContext):
        # self.enter_ctx(self)
        self.enter_ctx(ctx)
        self.exit_ctx()

    # Visit a parse tree produced by FLParser#expr_map.
    def visitExpr_map(self, ctx: FLParser.Expr_mapContext):
        self.enter_ctx(ctx)
        self.exit_ctx()

    # Visit a parse tree produced by FLParser#expr_filter.
    def visitExpr_filter(self, ctx: FLParser.Expr_filterContext):
        self.enter_ctx(ctx)
        self.exit_ctx()

    # Visit a parse tree produced by FLParser#expr_not_equal.
    def visitExpr_equal(self, ctx: FLParser.Expr_equalContext):
        self.enter_ctx(ctx)
        left_value = ctx.left.accept(self)
        right_value = ctx.right.accept(self)
        result = self.compare_holders(left_value, right_value, ctx)
        self.exit_ctx()
        return result

    # Visit a parse tree produced by FLParser#expr_equal.
    def visitExpr_not_equal(self, ctx: FLParser.Expr_not_equalContext):
        self.enter_ctx(ctx)
        left_value = ctx.left.accept(self)
        right_value = ctx.right.accept(self)
        result = self.compare_holders(left_value, right_value, ctx)
        result = FLValueHolder(
            value=not result.value, ctx=ctx, value_type=FLValueType.BoolValue
        )
        self.exit_ctx()
        return result

    # Visit a parse tree produced by FLParser#expr_in.
    def visitExpr_in(self, ctx: FLParser.Expr_inContext):
        self.enter_ctx(ctx)
        left_value = ctx.left.accept(self)
        right_value = ctx.right.accept(self)
        result = self.contains_value(left_value, right_value, ctx)
        self.exit_ctx()
        return result

    # Visit a parse tree produced by FLParser#expr_intersect.
    def visitExpr_intersect(self, ctx: FLParser.Expr_intersectContext):
        self.enter_ctx(ctx)
        left_value = ctx.left.accept(self)
        right_value = ctx.right.accept(self)
        result = self.intersect_holders(left_value, right_value, ctx)
        self.exit_ctx()
        return result

    # Visit a parse tree produced by FLParser#expr_concat.
    def visitExpr_concat(self, ctx: FLParser.Expr_concatContext):
        self.enter_ctx(ctx)
        left_value = ctx.left.accept(self)
        right_value = ctx.right.accept(self)
        result = self.concat_holders(left_value, right_value, ctx)
        self.exit_ctx()
        return result


def ctx_location(ctx: ParserRuleContext) -> str:
    return f"{ctx.start.line}:{ctx.start.column + 1}"
