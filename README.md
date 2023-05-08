# APS - Lógica da Computação

**Feito por:** Francisco Pinheiro Janela

## 1. Introdução

Esta linguagem será desenvolvida com o intuito de facilitar a criação de infraestruturas na AWS. 

Definido o contexto e a aplicação, as próximas etapas serão de construção efetiva da linguagem, passando pela criação de um exemplo de linguagem que irá facilitar a conversão para a EBNF. Com a EBNF será possível desenvolver o diagrama sintático e posteriormente o compilador.

## 2. EBNF

Utilizando o exemplo de linguagem, a EBNF resultante para a linguagem é a seguinte:

```bash
BLOCK = { STATEMENT };

STATEMENT = [ DECLARATION | ( "START BUILD", { BUILD_STATEMENT }, "END BUILD" ) ], "\n";

DECLARATION = ( ASSIGNMENT | ("f", ":", FUNCTION_DECLARATION) );

ASSIGNMENT = ( IDENTIFIER, "is", ( VALUE | ( "list", "of", { VALUE } ) | ( "load" , STRING ) | IDENTIFIER ) )

FUNCTION_DECLARATION = FUNCTION_TYPE, "as", IDENTIFIER, [ "needs", { IDENTIFIER } ], "with", "\n", FUNCTION_VARIABLE_DECLARATION, {"and", "\n", FUNCTION_VARIABLE_DECLARATION, "\n" }, "end";

FUNCTION_VARIABLE_DECLARATION = IDENTIFIER, "as", ( VALUE | IDENTIFIER );

BUILD_STATEMENT = ( LOOP_STATEMENT | CONDITIONAL_STATEMENT | PERFORM_STATEMENT );

LOOP_STATEMENT = "for", "each", IDENTIFIER, "in", IDENTIFIER, PERFORM_STATEMENT;

CONDITIONAL_STATEMENT = "on", CONDITION, PERFORM_STATEMENT;

PERFORM_STATEMENT = "perform", ( IDENTIFIER | FUNCTION_TYPE ), [ ("with", FUNCTION_VARIABLE_DECLARATION, { "and", FUNCTION_VARIABLE_DECLARATION }) | ("with", "use", IDENTIFIER) ];

CONDITION = ( ( IDENTIFIER | VALUE | FIND ), COMPARE_METHODS, ( IDENTIFIER | VALUE | FIND ) );

COMPARE_METHODS = ( "gt" | "lt" | "et" | "net" | "gte" | "lte" );

FUNCTION_TYPE = ( "AutoScaleBuilder" | "LoadBalancerBuilder" | "InstanceBuilder" | "SubnetBuilder" | "SecurityGroupBuilder" | "EmailSender" );

FIND = "find", IDENTIFIER, "of", ( FIND | IDENTIFIER );

VALUE = ( STRING | EXPRESSION );

EXPRESSION = TERM, { ("+" | "-"), TERM } ;

TERM = FACTOR, { "*", FACTOR } ;

FACTOR = NUMBER | "(", EXPRESSION, ")" | IDENTIFIER ;

IDENTIFIER = ( LETTER, { LETTER | DIGIT | "_" } ) | (KNOWN_IDENTIFIERS);

KNOWN_IDENTIFIERS = ( "CPUUtilization" | "RAMUsage" | "AvailableMemorySpace" );

STRING = '"', { LETTER | DIGIT | " " | "." | "," | ":" | ";" | "-" | "_" | "/" | "\\" | "!" | "?" | "@" | "#" | "$" | "%" | "&" | "*" | "(" | ")" | "[" | "]" | "{" | "}" | "<" | ">" | "=" | "+" | "~" | "^" | "`" }, '"' ;

NUMBER = DIGIT, { DIGIT } ;

LETTER = ( a | ... | z | A | ... | Z ) ;

DIGIT = ( 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 0 ) ;

```

## 3. Exemplo da Linguagem

Abaixo, tem-se um exemplo de código para a linguagem:

```
# Must define variables
Infrastructure is "sample"
Provider is load ".env"
EmailSendTo is "email@example.com"

# Scale Factor:
monitoring is CPUUtilization
scale_up_factor is 60
scale_down_factor is 20
scale_trashold is 20

# Subnet Variables
subnet_ips is list of "172.16.11.0/24", "172.16.12.0/24", "172.16.13.0/24"

# Security Group Variables
security_groups_config is load "security_group.json"

# Instance Configuration Variables
intance_configuration_type_1 is load "instance_configuration_type1.json"
intance_configuration_type_2 is load "instance_configuration_type2.json"

# Other Variables
CPUUsageWarning is load "cpu_usage_warning.html"

## Defining Functions
# AutoScaling Function
f: AutoScaleBuilder as autoscaling_type1 needs InstanceConfigurationType with
    Name as type1 and
    Size as list of 1, 2, 5 and
    SubnetIPS as subnet_ips and
    Monitoring as monitoring and
    ScaleFactor as list of scale_up_factor, scale_down_factor
end

# Must have START mark
START BUILD

## Loops
for each subnet_ip in subnet_ips perform SubnetBuilder with SubnetIp as subnet_ip
for each security_group in security_groups_config perform SecurityGroupBuilder with SecurityGroupConfig as security_group

## Execute Functions
# Default Functions
perform InstanceBuilder with use intance_configuration_type_2

# User defined Functions
perform autoscaling_type1 with use intance_configuration_type_1

## Conditional Statements
on find CPUUtilization of find name of intance_configuration_type_2 gt scale_up_factor + scale_trashold perform EmailSender with Template as CPUUsageWarning and Subject as "Type 2 - CPU Usage Warning"

# Must have END mark
END BUILD
```

Vale ressaltar alguns detalhes importantes:

1. Existem variáveis que precisam ser inseridas no arquivo, uma vez que são estas que irão compor os meta-dados obrigatórios.
<br/>

2. Existem apenas 2 tipos de variáveis: `string` e `number`. Além disso, elas podem constituir uma lista, de um único tipo.
<br/>

3. É possível complementar a linguagem e as variáveis com a função load, que poderá carregar arquivos externos. Um uso que será de extrema importância é o carregamento de arquivos JSON, que serão utilizados para a criação de instâncias, subnets, security groups, etc. Isto ocorre pois estes podem conter as informações para as variáveis dependentes das funções.
<br/>

4. Não é possível criar funções genéricas, elas já são pré-definidas, no entanto, dá-se a possibilidade de usar a declaração de função para poder predefinir alguns parâmetros essenciais e reformatar as necessidades da função base, dando a ela um novo identificador.
<br/>

5. A linguagem não possui um tipo de dado booleano, mas é possível utilizar as comparações para obter o mesmo resultado. Vale lembrar que não é possível utilizar a resposta negativa da comparação, como seria nas linguagens de programação.
<br/>

6. A preposição `perform` será a base para definir a execução de uma ação.
<br/>

7. A preposição `find` será a base para encontrar métricas específicas da infraestrutura, como por exemplo, a CPUUtilization de uma instância específica, mas também para encontrar o valor de um identificador de dentro de um JSON, caso haja necessidade. As métricas específicas possuem uma necessidade específica para encontrarem o que se procura, devendo ser respeitada depois do `of`, no exemplo acima, a métrica é `CPUUtilization` e precisa do nome da instância para coletar as suas informações.
<br/>

8. O `loop` existente na linguagem é o `for each`, que é utilizado para percorrer uma lista ou um JSON de valores e executar uma ação para cada um deles.