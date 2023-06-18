grammar FL;

program: (stmt SEMICOLON)*;

stmt: print | bind;

print: PRINT expr;
bind: var ASSIGN expr;

var: IDENT;
integer: DIGIT+;
string: STRING;
edge: LP integer COMMA string COMMA integer RP;
item: var | string | integer | edge | list;
list: LB RB | LB item (COMMA item)* RB;
graph: LP list COMMA list RP;
iterable: list | var;
val: integer | string | list | edge | graph;

target: var | integer | list;
source: var | graph;

normalize: NORMALIZE target;
get_start: GET_START OF target;
get_final: GET_FINAL OF target;
set_start: SET_START OF source TO target;
set_final: SET_FINAL OF source TO target;
add_start: ADD_START OF source TO target;
add_final: ADD_FINAL OF source TO target;

get_edges: GET_EDGES OF target;
get_labels: GET_LABELS OF target;
get_vertices: GET_VERTICES OF target;
get_reachable: GET_REACHABLE OF target;

lambda: LP LAMBDA list ARROW expr RP;
map: MAP (lambda | var) COLON iterable;
filter: FILTER (lambda | var) COLON iterable;
load: LOAD (string | var);

bin_arg_l: var | string | graph;
bin_arg_r: var | string | graph;
bin_eq_arg_l: var | val;
bin_eq_arg_r: var | val;
bin_in_arg_l: var | integer | string | edge;
bin_in_arg_r: var | string | graph;

union: bin_arg_l UNION bin_arg_r;
intersect: bin_arg_l INTERSECT bin_arg_r;
equal: bin_eq_arg_l EQUAL bin_eq_arg_r;
in: bin_in_arg_l IN bin_in_arg_r;
concat: bin_arg_l CONCAT bin_arg_r;
kleene: bin_arg_l KLEENE;

expr:
    LP expr RP
  | val
  | var
  | normalize
  | get_start
  | get_final
  | set_start
  | set_final
  | add_start
  | add_final
  | get_edges
  | get_labels
  | get_vertices
  | get_reachable
  | lambda
  | map
  | filter
  | load
  | union
  | intersect
  | equal
  | in
  | concat
  | kleene
  ;

COMMA: ',';
COLON: ':';
ASSIGN: ':=';
ARROW: '->';
SEMICOLON: ';';

UNION: '|';
INTERSECT: '&';
EQUAL: '==';
CONCAT: '.';
KLEENE: '*';

PRINT: 'print';

LAMBDA: 'lambda';
MAP: 'map';
FILTER: 'filter';
LOAD: 'load';

NORMALIZE: 'normalize';
GET_EDGES: 'get_edges';
GET_LABELS: 'gel_labels';
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

OF: 'of';
TO: 'to';
IN: 'in';

IDENT: CHAR (CHAR | DIGIT)*;
CHAR: [a-zA-Z_];
DIGIT: [0-9];
STRING: '"' (~["\\] | '\\' .)* '"';

COMMENT: '//' ~[\n]* -> skip;
WS: [ \t\n\r\f]+ -> channel(HIDDEN);
