# APS - Lógica da Computação

## 1. Introdução

## 2. EBNF

```bash
BLOCK = { STATEMENT };

STATEMENT = [ DECLARATION | ( "START BUILD", { BUILD_STATEMENT }, "END BUILD" ) ], "\n";

DECLARATION = ( ASSIGNMENT | ("f", ":", FUNCTION_DECLARATION) );

ASSIGNMENT = ( IDENTIFIER, "is", ( VALUE | ( "list", "of", { VALUE } ) | ( "load" , STRING ) | IDENTIFIER ) )

FUNCTION_DECLARATION = FUNCTION_TYPE, "as", IDENTIFIER, [ "needs", { IDENTIFIER } ], "with", ( ( FUNCTION_VARIABLE_DECLARATION, { "and", FUNCTION_VARIABLE_DECLARATION } ) | ( "\n", FUNCTION_VARIABLE_DECLARATION, "\n", { "and", FUNCTION_VARIABLE_DECLARATION, "\n" }, "end" ) ) ;

FUNCTION_VARIABLE_DECLARATION = IDENTIFIER, "as", ( VALUE | IDENTIFIER );

BUILD_STATEMENT = ( LOOP_STATEMENT | CONDITIONAL_STATEMENT | PERFORM_STATEMENT );

LOOP_STATEMENT = "for", "each", IDENTIFIER, "in", IDENTIFIER, PERFORM_STATEMENT;

CONDITIONAL_STATEMENT = "on", CONDITION, PERFORM_STATEMENT;

PERFORM_STATEMENT = "perform", IDENTIFIER, [ "with", FUNCTION_VARIABLE_DECLARATION, { FUNCTION_VARIABLE_DECLARATION } ];

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
perform InstanceBuilder with intance_configuration_type_2

# User defined Functions
perform autoscaling_type1 with intance_configuration_type_1

## Conditional Statements
on find CPUUtilization of find name of intance_configuration_type_2 gt scale_up_factor + scale_trashold perform EmailSender with Template as CPUUsageWarning and Subject as "CPU Usage Warning"

# Must have END mark
END BUILD
```