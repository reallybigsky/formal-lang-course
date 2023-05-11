# Описание языка запросов

### Абстрактный синтаксис

```
prog = List<stmt>

stmt =
    Bind of string * expr
  | Print of expr

val =
    String  of string
  | Int     of int

expr =
    Var of string                // переменные
  | Const of val                 // константы
  | Set_start of expr * expr     // задать множество стартовых состояний
  | Set_final of expr * expr     // задать множество финальных состояний
  | Add_start of expr * expr     // добавить состояния в множество стартовых
  | Add_final of expr * expr     // добавить состояния в множество финальных
  | Get_start of expr            // получить множество стартовых состояний
  | Get_final of expr            // получить множество финальных состояний
  | Get_reachable of expr        // получить все пары достижимых вершин
  | Get_vertices of expr         // получить все вершины
  | Get_edges of expr            // получить все рёбра
  | Get_labels of expr           // получить все метки
  | Map of lambda * expr         // классический map
  | Filter of lambda * expr      // классический filter
  | Load of string               // загрузка графа (по пути к файлу)
  | Regex of string              // преобразование строкового выражения к регулярному выражению
  | CFG of string                // преобразование строкового выражения к грамматике
  | Intersect of expr * expr     // пересечение языков
  | Concat of expr * expr        // конкатенация языков
  | Union of expr * expr         // объединение языков
  | Star of expr                 // замыкание языков (звезда Клини)
  | List of List<expr>           // множество элементов
  | Logic of logic               // логическое выражение

logic =
    In  of string * expr         // проверка, лежит ли переменная (задаваемая как имя) в множестве значений expr
  | And of logic * logic         // логическое "и"
  | Or  of logic * logic         // логическое "или"
  | Not of logic                 // логическое "не"

args =
    Wildcard of string                      // аргумент любого вида
  | Edge     of args * string * args        // аргумент ребро, содержащее две вершины и метку
  | List     of List<args>                  // аргумент, являющийся списком элементов

lambda =
    Lambda of args * expr        // лямбда как функция с аргументами и выражением
```

### Конкретный синтаксис

```
grammar lang;

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
```

### Примеры

Получить все вершины, достижимые из 0 вершины, и напечатать:

```
/* Загружаем граф и устанавливаем ему стартовой вершиной 0 */
graph           := set_start (load "pizza", [0]);

/* Получаем пары всех достиимых вершин (пара - лист листов с 2 элементами - вершинами) */
reachable_pairs := get_reachable (graph);

/* Получаем из пар достижимых вершин вторую компоненту */
reachable_list  := map reachable_pairs with lambda ([a, b]) of b fo;
print reachable_list;
```

Найти все вершины, достижимые из начального множества, по которым существует путь удовлетворяющий регулярному выражению:

```
/* Загружаем граф и устанавливаем ему стартовое множество вершин */
graph                               := set_start (load "pizza", [0, 1, 2]);
regular_expr                        := regex "subClassOf*";

/* Пересекаем граф и regex, получаем новый конечный автомат */
graph_and_regular_expr_intersection := intersect graph and regular_expr;

/* Получаем пары вершин достижимых в получившемся автомате - пересечении regex и графа */
reachable_pairs_intersection        := get_reachable (graph_and_regular_expr_intersection);

/* Оставляем только те пары достижимых вершин в пересечении, которые понадобятся для ответа */
reachable_pairs_from_start_set      := filter reachable_pairs_intersection with
                                            lambda ([[graph_s, regex_s], [graph_f, regex_f]]) of
                                                graph_s in get_start (graph) and regex_s in get_start (regular_expr)
                                                and regex_f in get_final (regular_expr)
                                            fo;

/* Печатаем результат */
print map reachable_pairs_from_start_set with lambda ([[graph_s, regex_s], [graph_f, regex_f]]) of graph_f fo
```
