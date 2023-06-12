# APS - Lógica da Computação

**Feito por:** Francisco Pinheiro Janela

## 1. Introdução

Esta linguagem será desenvolvida com o intuito de facilitar a criação de infraestruturas na AWS. 

Definido o contexto e a aplicação, as próximas etapas serão de construção efetiva da linguagem, passando pela criação de um exemplo de linguagem que irá facilitar a conversão para a EBNF. Com a EBNF será possível desenvolver o diagrama sintático e posteriormente o compilador.

## 2. EBNF

Utilizando o exemplo de linguagem, a EBNF resultante para a linguagem é a seguinte:

```bash
BLOCK = { DECLARATION_STATEMENT };

DECLARATION_STATEMENT = [ (IDENTIFIER, "is", EXPRESSION) | ("function", FUNC_NAME, "as", IDENTIFIER, "with", "\n", [ FUNC_ARG , "as", EXPRESSION , { "and" , "\n , FUNC_ARG , "as", EXPRESSION} , "\n" ], "end") | ( "START_BUILD", "\n", { BUILD_STATEMENT }, "END_BUILD" ) ] , "\n" ;

BUILD_STATEMENT = [ ([ "for" , IDENTIFIER, "in", EXPRESSION, ":", EXPRESSION] , PERFORM_STATEMENT) | ( "on" , MONITERING_METRIC, COMPARISON_OPERATOR, EXPRESSION, "in", EXPRESSION, "alert") ], "\n";

PERFORM_STATEMENT = "perform", ( IDENTIFIER | FUNC_NAME ), "with", "\n", [ FUNC_ARG , "as", EXPRESSION , { "and" , "\n , FUNC_ARG , "as", EXPRESSION} , "\n" ], "end";

EXPRESSION = TERM, { ("+" | "-" | "."), TERM } ;

TERM = FACTOR, { ("*" | "/"), FACTOR } ;

FACTOR = NUMBER | STRING | "(", EXPRESSION, ")" | IDENTIFIER | ("+" | "-"), FACTOR;

IDENTIFIER = ( LETTER, { LETTER | DIGIT | "_" } ) | (KNOWN_IDENTIFIERS);

STRING = '"', { LETTER | DIGIT | " " | "." | "," | ":" | ";" | "-" | "_" | "/" | "\\" | "!" | "?" | "@" | "#" | "$" | "%" | "&" | "*" | "(" | ")" | "[" | "]" | "{" | "}" | "<" | ">" | "=" | "+" | "~" | "^" | "`" }, '"' ;

NUMBER = DIGIT, { DIGIT } ;

LETTER = ( a | ... | z | A | ... | Z ) ;

DIGIT = ( 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 0 ) ;

FUNC_NAME = ( "InstanceBuilder" | "SecurityGroupBuilder" );

FUNC_ARG = ( "sg_name" | "sg_description" | "sg_id" | "instance_name" | "ami" | "instance_type" | "ingress_port" | "ingress_protocol" | "ingress_description" | "egress_port" | "egress_protocol" );

MONITERING_METRIC = ( "CPUUtilization" | "NetworkPacketsIn" | "NetworkPacketsOut" | "DiskReadOps" | "DiskWriteOps" );

COMPARISON_OPERATOR = ( ">" | "<" | "<=" | ">=" );

```

## 3. Exemplo da Linguagem

Abaixo, tem-se dois exemplos de código para a linguagem:

```
# Must define AWS KEY variables
KEY_ID is "[YOUR_KEY_ID]"
SECRET_KEY is "[YOUR_SECRET_KEY]"

general_instance_description is "General Description"

function InstanceBuilder as instance_builder_type1 with
    instance_type as "t2.medium"
end

START_BUILD
    perform SecurityGroupBuilder with
        sg_name as "Teste SG" and
        sg_description as general_instance_description . " for SecGroup " and
        ingress_port as 22 and
        ingress_protocol as "tcp"
    end
    perform instance_builder_type1 with
        instance_name as "Teste 1"
    end
    for i in 1:(2*1) perform InstanceBuilder with
        instance_name as "Teste 2 (" . (i + 4) . ")"
    end
END_BUILD
```
<br/>

```
KEY_ID is "[YOUR_KEY_ID]"
SECRET_KEY is "[YOUR_SECRET_KEY]"

treshhold_limit is 90
instance_1_id is "i-092990761db1e7ca1"

START_BUILD
    on CPUUtilization >= treshhold_limit in instance_1_id alert
END_BUILD
```

Vale ressaltar alguns detalhes importantes:

1. Existem variáveis que precisam ser inseridas no arquivo, uma vez que são estas que irão compor os meta-dados obrigatórios. São elas a `KEY_ID` e a `SECRET_KEY`.
<br/>

2. Existem apenas 2 tipos de variáveis: `string` e `number`.
<br/>

3. Não é possível criar funções genéricas, elas já são pré-definidas, no entanto, dá-se a possibilidade de usar a declaração de função para poder predefinir alguns parâmetros essenciais e reformatar as necessidades da função base, dando a ela um novo identificador.
<br/>

4. A preposição `perform` será a base para definir a execução de uma ação.
<br/>

5. O `loop` existente na linguagem é o `for`, que é utilizado para definir um range de inteiros entre dois valores incluindo o primeiro até menor que o segundo, variando em adições de 1.
<br/>

6. A linguagem é case-sensitive, ou seja, diferencia letras maiúsculas de minúsculas.

7. A estrutura condicional da linguagem é utilizada somente para criar os alarmes em função de métricas que podem ser avaliadas.

