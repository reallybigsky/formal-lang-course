# Описание языка запросов

### Генерация файлов antlr

```shell
antlr4 FL.g4 -Dlanguage=Python3 -o dist
```

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
```
### Система типов

| Тип    | Описание                             |
|--------|--------------------------------------|
| Int    | Целое число                          |
| String | Строка (в т.ч. регулярное выражение) |
| Bool   | Логическое значение                  |
| Vertex | Вершина графа                        |
| Edge   | Ребро графа                          |
| Graph  | Граф                                 |
| List   | Список                               |
| Lambda | Лямбда функция                       |

### Примеры

Получить все вершины, достижимые из 0 вершины, и напечатать:

```
/* Загружаем граф и устанавливаем ему стартовой вершиной 0 */
graph           := set_start (load "pizza", [0]);

/* Получаем пары всех достиимых вершин (пара - лист листов с 2 элементами - вершинами) */
reachable_pairs := get_reachable (graph);

/* Получаем из пар достижимых вершин вторую компоненту */
reachable_list  := map (lambda ({a, b}) -> {b}, get_reachable (graph));
print reachable_list;
```

Найти все вершины, достижимые из начального множества, по которым существует путь удовлетворяющий регулярному выражению:

```
/* Загружаем граф и устанавливаем ему стартовое множество вершин */
graph                               := set_start (load "pizza", {0, 1, 2});
regular_expr                        := "subClassOf*";

/* Пересекаем граф и regex, получаем новый конечный автомат */
graph_and_regular_expr_intersection := graph && regular_expr;

/* Получаем пары вершин достижимых в получившемся автомате - пересечении regex и графа */
reachable_pairs_intersection        := get_reachable graph_and_regular_expr_intersection;

/* Оставляем только те пары достижимых вершин в пересечении, которые понадобятся для ответа */
reachable_pairs_from_start_set      := filter (lambda ({{graph_s, regex_s}, {graph_f, regex_f}}) ->
                                                 {graph_s in get_start graph && regex_s in get_start regular_expr
                                                && regex_f in get_final regular_expr}, reachable_pairs_interssection);

/* Печатаем результат */
print map (lambda ({{graph_s, regex_s}, {graph_f, regex_f}}) -> {graph_f}, reachable_pairs_from_start_set);
```
