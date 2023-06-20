grammar FL;

program: (stmt SEMICOLON)*;

stmt: print | bind;

print: PRINT value=expr;
bind: id=IDENT ASSIGN value=expr;

val:
    value=STRING # val_string
  | value=INT    # val_int
  | set          # val_list
  | value=IDENT  # val_id
  ;

bool: TRUE | FALSE;
vertex: INT;
edge: LP INT COMMA STRING COMMA INT RP;
graph: LP set COMMA set RP;
set: LB RB | LB items+=expr (COMMA items+=expr)* RB;
lambda: LAMBDA LP val RP ARROW LB body=expr RB;

expr:
    LP expr RP # expr_expr
  | name=IDENT # expr_var
  | val        # expr_val
  | lambda     # expr_lambda
  | GET_EDGES value=expr                     # expr_get_edge
  | GET_LABELS value=expr                    # expr_get_labels
  | GET_VERTICES value=expr                  # expr_get_vertices
  | GET_REACHABLE value=expr                 # expr_get_reachable
  | GET_START value=expr                     # expr_get_start
  | GET_FINAL value=expr                     # expr_get_final
  | SET_START LP to=expr COMMA start=expr RP # expr_set_start
  | SET_FINAL LP to=expr COMMA final=expr RP # expr_set_final
  | ADD_START LP to=expr COMMA start=expr RP # expr_add_start
  | ADD_FINAL LP to=expr COMMA final=expr RP # expr_add_final
  | MAP LP lambda COMMA expr RP              # expr_map
  | FILTER LP lambda COMMA expr RP           # expr_filter
  | LOAD value=STRING                        # expr_load
  | left=expr INTERSECT right=expr           # expr_intersect
  | left=expr CONCAT right=expr              # expr_concat
  | left=expr IN right=expr                  # expr_in
  | left=expr EQUAL right=expr               # expr_equal
  | left=expr NOT_EQUAL right=expr           # expr_not_equal
  ;

COMMA: ',';
ASSIGN: ':=';
ARROW: '->';
SEMICOLON: ';';

CONCAT: '||';
INTERSECT: '&&';
EQUAL: '==';
NOT_EQUAL: '!=';
IN: 'in';

PRINT: 'print';

LAMBDA: 'lambda';
MAP: 'map';
FILTER: 'filter';
LOAD: 'load';

GET_EDGES: 'get_edges';
GET_LABELS: 'get_labels';
GET_VERTICES: 'get_vertices';
GET_REACHABLE: 'get_reachable';

GET_FINAL: 'get_final';
GET_START: 'get_start';
ADD_FINAL: 'add_final';
ADD_START: 'add_start';
SET_FINAL: 'set_final';
SET_START: 'set_start';

LP: '(';
RP: ')';
LB: '{';
RB: '}';

TRUE: 'true';
FALSE: 'false';
INT: [1-9][0-9]* | '0';
STRING: '"' (~["\\] | '\\' .)* '"';
IDENT: CHAR (CHAR | DIGIT)*;
CHAR: [a-zA-Z_];
DIGIT: [0-9];

COMMENT: '//' ~[\n]* -> skip;
WS: [ \t\n\r\f]+ -> channel(HIDDEN);
