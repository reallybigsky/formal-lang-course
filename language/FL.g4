grammar FL;

prog: (((print_stmt | bind) SEMICOLON) | comment)* ;

comment: '/*' .*? '*/' ;

print_stmt: PRINT expr ;
bind: IDENT ASSIGN expr ;

const: STRING | DECIMAL ;

list_expr: LSQ_BRACKET (expr (COMMA expr)*)? RSQ_BRACKET ;

two_args_builtin: SET_START | SET_FINAL | ADD_START | ADD_FINAL ;
one_args_builtin: GET_START | GET_FINAL | GET_REACHABLE | GET_VERTICES | GET_EDGES | GET_LABELS ;

with_builtin: MAP | FILTER ;

string_args_builtin: LOAD | REGEX | CFG ;

two_args_lang_builtin: INTERSECT | CONCAT | UNION ;
one_args_lang_builtin: KLEENE_CLOSURE ;

expr:
    const
  | lambda_expr
  | two_args_builtin L_BRACKET expr COMMA expr R_BRACKET
  | one_args_builtin L_BRACKET expr R_BRACKET
  | with_builtin expr WITH expr
  | string_args_builtin STRING
  | two_args_lang_builtin expr AND expr
  | one_args_lang_builtin expr
  | list_expr
  | logic
  | L_BRACKET expr R_BRACKET
  | IDENT;

logic_atom: IDENT IN expr ;

logic:
    logic_atom
  | logic_atom AND logic
  | logic_atom OR logic
  | NOT logic
  | L_BRACKET logic R_BRACKET ;

args:
    IDENT
  | LSQ_BRACKET (args (COMMA args)*)? RSQ_BRACKET ;

lambda_expr:
    LAMBDA L_BRACKET args R_BRACKET OF expr FO ;

SEMICOLON: ';' ;
COMMA : ',' ;

PRINT: 'print' ;
STRING: '"' .*? '"' ;
DECIMAL: [0-9]+ ;
ASSIGN: ':=' ;

KLEENE_CLOSURE : 'kleene' ;
UNION : 'union' ;
CONCAT : 'concat' ;
INTERSECT : 'intersect' ;

CFG : 'cfg' ;
REGEX : 'regex' ;
LOAD : 'load' ;

FILTER : 'filter' ;
MAP : 'map' ;
GET_LABELS : 'gel_labels' ;
GET_EDGES : 'get_edges' ;
GET_VERTICES : 'get_vertices' ;
GET_REACHABLE : 'get_reachable' ;
GET_FINAL : 'get_final' ;
GET_START : 'get_start' ;
ADD_FINAL : 'add_final' ;
ADD_START : 'add_start' ;
SET_FINAL : 'set_final' ;
SET_START : 'set_start' ;

L_BRACKET : '(' ;
R_BRACKET : ')' ;
LSQ_BRACKET : '[' ;
RSQ_BRACKET : ']' ;

AND : 'and' ;
OR : 'or' ;
NOT : 'not' ;
IN : 'in' ;

LAMBDA : 'lambda' ;

OF : 'of' ;
FO : 'fo' ;
WITH : 'with' ;

IDENT: [_a-zA-Z0-9]+ ;
WS : [\n\r\t\f]+ -> skip ;
