from abc import abstractmethod
import re
import sys, os

#===============================================================================
#                              GLOBALS
#===============================================================================
RESERVED_WORDS = ["end", "Int", "String", "function", "and", "for", "as", "is", "in", "with", "needs", "perform", "on", "alert", "START_BUILD", "END_BUILD"]
FUNC_NAMES = ["InstanceBuilder", "SecurityGroupBuilder"]
FUNC_ARGS = ["sg_name", "sg_description", "sg_id", "instance_name", "ami", "instance_type", "ingress_port", "ingress_protocol", "ingress_description", "egress_port", "egress_protocol"]
MONITERING_METRICS = ["CPUUtilization", "NetworkPacketsIn", "NetworkPacketsOut", "DiskReadOps", "DiskWriteOps"]
COMPARISON_OPERATORS = [">", "<", "<=", ">="]
COMPARISON_OPERATORS_CODE = {"<": "LessThanThreshold", ">": "GreaterThanThreshold", "<=": "LessThanOrEqualToThreshold", ">=": "GreaterThanOrEqualToThreshold"}

FUNC_NEEDS = {"InstanceBuilder": (["instance_name"], ["ami", "instance_type", "sg_id"]), "SecurityGroupBuilder": (["sg_name", "ingress_port", "ingress_protocol"], ["ingress_description", "egress_port", "egress_protocol", "sg_description"])}

FILE_LOC = sys.argv[1].split(".")[0]
FILE_NAME = FILE_LOC.split("/")[-1]

if not os.path.exists("out/" + FILE_NAME + "/"):
    os.makedirs("out/" + FILE_NAME + "/")
    PATH = "out/" + FILE_NAME + "/"
else:
    i = 1
    while os.path.exists("out/" + FILE_NAME + "(" + str(i) + ")" + "/"):
        i += 1
    os.makedirs("out/" + FILE_NAME + "(" + str(i) + ")" + "/")
    PATH = "out/" + FILE_NAME + "(" + str(i) + ")" + "/"

#===============================================================================
#                              TOKENIZER
#===============================================================================

class Token():
    def __init__(self, type, value):
        self.type = type
        self.value = value
    
class Tokenizer():
    def __init__(self, source):
        self.DIGITS = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"]
        self.LETTERS = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z", "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"]
        self.source = source
        self.position = 0
        self.next = None
    
    def selectNext(self):
        if self.position >= len(self.source):
            self.next = Token("EOF", None)
        elif self.source[self.position] == " ":
            while self.position < len(self.source) and self.source[self.position] == " ":
                self.position += 1
            self.selectNext()
            self.position -= 1
        elif self.source[self.position] == "\n":
            self.next = Token("ENDLINE", "\n")
        elif self.source[self.position] == "+":
            self.next = Token("PLUS", "+")
        elif self.source[self.position] == "-":
            self.next = Token("MINUS", "-")
        elif self.source[self.position] == "*":
            self.next = Token("MULT", "*")
        elif self.source[self.position] == "/":
            self.next = Token("DIV", "/")
        elif self.source[self.position] == ".":
            self.next = Token("CONCAT", ".")
        elif self.source[self.position] == ",":
            self.next = Token("COMMA", ",")
        elif self.source[self.position] == "(":
            self.next = Token("OPEN_BRACKET", "(")
        elif self.source[self.position] == ")":
            self.next = Token("CLOSE_BRACKET", ")")
        elif self.source[self.position] == "=":
            self.next = Token("ASSIGN", "=")
        elif self.source[self.position] == ":":
            self.next = Token("TO", ":")
        elif self.source[self.position] in COMPARISON_OPERATORS:
            if self.source[self.position + 1] == "=":
                self.next = Token("COMPARISON_OPERATOR", self.source[self.position] + "=")
                self.position += 1
            else:
                self.next = Token("COMPARISON_OPERATOR", self.source[self.position])
        elif self.source[self.position] in self.DIGITS:
            number = ""
            while self.position < len(self.source) and self.source[self.position] in self.DIGITS:
                number += self.source[self.position]
                self.position += 1
            self.next = Token("INT", number)
            self.position -= 1
        elif self.source[self.position] in self.LETTERS:
            word = ""
            while self.position < len(self.source) and (self.source[self.position] in self.LETTERS or self.source[self.position] in self.DIGITS or self.source[self.position] == "_"):
                word += self.source[self.position]
                self.position += 1
            if word in RESERVED_WORDS:
                self.next = Token(word, word)
            elif word in FUNC_NAMES:
                self.next = Token("FUNC_NAME", word)
            elif word in FUNC_ARGS:
                self.next = Token("FUNC_ARG", word)
            elif word in MONITERING_METRICS:
                self.next = Token("MONITERING_METRIC", word)
            else:
                self.next = Token("ID", word)
            self.position -= 1
        elif self.source[self.position] == '"':
            self.position += 1
            word = ""
            while self.position < len(self.source) and self.source[self.position] != '"':
                word += self.source[self.position]
                self.position += 1
            self.next = Token("STRING", word)
        else:
            sys.stderr.write("Not expected token")
            sys.exit(1)
        self.position += 1


#===============================================================================
#                              SYMBOL TABLE
#===============================================================================

class SymbolTable():
    def __init__(self) -> None:
        self.ST = {}
    
    def getter(self, key):
        return self.ST[key]
    
    def setter(self, key, tupla):
        if key not in self.ST:
            sys.stderr.write("Variable not declared: " + key)
            sys.exit()
        if self.ST[key][0] == tupla[0]:
            self.ST[key] = tupla
        else:
            sys.stderr.write("Type mismatch on setter")
            sys.exit()

    def create(self, key, tupla):
        if key in self.ST:
            sys.stderr.write("Variable already declared")
            sys.exit()
        self.ST[key] = tupla

    def delete(self, key):
        if key not in self.ST:
            sys.stderr.write("Variable not declared")
            sys.exit()
        del self.ST[key]

#===============================================================================
#                              FUNCTION TABLE
#===============================================================================

class FunctionTable():
    def __init__(self) -> None:
        self.FT = {}
    
    def getter(self, key):
        return self.FT[key]

    def create(self, key, func_node):
        if key in self.FT:
            sys.stderr.write("Variable already declared")
            sys.exit()
        self.FT[key] = func_node

functionTable = FunctionTable()

#===============================================================================
#                              FUNCTIONS
#===============================================================================
class InstanceBuilder():
    i = 1

    def build_instance(args):
        print("Building instance with args: {}".format(args))
        with open(PATH + "instance.tf", "a") as f:
            f.write("resource \"aws_instance\" \"instance" + str(InstanceBuilder.i) +"\" {\n")
            f.write("\tami = \"" + args["ami"] + "\"\n")
            f.write("\tinstance_type = \"" + args["instance_type"] + "\"\n")
            if args["sg_id"] != None:
                f.write("\tsecurity_groups = [\"" + args["sg_id"] + "\"]\n")
            f.write("\ttags = {\n\t\tName = \"" + args["instance_name"] + "\"\n\t}\n")
            f.write("}\n\n")
            InstanceBuilder.i += 1
        print("Instance built successfully!\n")

class SecurityGroupBuilder():
    i = 1

    def build_security_group(args):
        print("Building security group with args: {}".format(args))
        with open(PATH + "security_group.tf", "a") as f:
            f.write("resource \"aws_security_group\" \"sg" + str(SecurityGroupBuilder.i) + "\" {\n")
            f.write("\tname = \"" + args["sg_name"] + "\"\n")
            if args["sg_description"] != None:
                f.write("\tdescription = \"" + args["sg_description"] + "\"\n")
            f.write("\tingress {\n\t\tfrom_port = " + str(args["ingress_port"]) + "\n\t\tto_port = " + str(args["ingress_port"]) + "\n\t\tprotocol = \""+ str(args["ingress_protocol"]) +"\"\n\t\tcidr_blocks = [\"0.0.0.0/0\"]\n\t}\n")
            f.write("\tegress {\n\t\tfrom_port = " + str(args["egress_port"]) + "\n\t\tto_port = " + str(args["egress_port"]) + "\n\t\tprotocol = \""+ str(args["egress_protocol"]) +"\"\n\t\tcidr_blocks = [\"0.0.0.0/0\"]\n\t}\n")
            f.write("}\n\n")
        print("Security group built successfully!\n")


def append_new_function(name, declared_args):
    if name == "InstanceBuilder":
        instance_builder_args = {"instance_name": None, "instance_description": None, "sg_id": None, "ami": "ami-00a0e0b890ae17d65", "instance_type": "t2.micro"}
        for arg in declared_args:
            instance_builder_args[arg] = declared_args[arg]
        InstanceBuilder.build_instance(instance_builder_args)

    elif name == "SecurityGroupBuilder":
        security_group_builder_args = {"sg_name": None, "sg_description": None, "ingress_port": None, "ingress_protocol": None, "egress_port": 0, "egress_protocol": "-1"}
        for arg in declared_args:
            security_group_builder_args[arg] = declared_args[arg]
        SecurityGroupBuilder.build_security_group(security_group_builder_args)

class AlertBuilder():
    i = 1

    def create_alert(monitoring_metric, comparisson_operator, treshhold, instance_id):
        converted_comparisson_operator = COMPARISON_OPERATORS_CODE[comparisson_operator]
        print("Creating alert with monitoring metric: {}, comparisson operator: {} and treshhold: {}".format(monitoring_metric, converted_comparisson_operator, treshhold))
        with open(PATH + "alert.tf", "a") as f:
            f.write("resource \"aws_cloudwatch_metric_alarm\" \"alarm" + str(AlertBuilder.i) + "\" {\n")
            f.write("\talarm_name = \"alarm" + str(AlertBuilder.i) + "\"\n")
            f.write("\tcomparison_operator = \"" + converted_comparisson_operator + "\"\n")
            f.write("\tevaluation_periods = 1\n")
            f.write("\tmetric_name = \"" + monitoring_metric + "\"\n")
            f.write("\tnamespace = \"AWS/EC2\"\n")
            f.write("\tperiod = 120\n")
            f.write("\tstatistic = \"Average\"\n")
            f.write("\tthreshold = " + str(treshhold) + "\n")
            f.write("\tinsufficient_data_actions = []\n")
            f.write("\tdimensions = {\n")
            f.write("\t\tInstanceId = \""+ instance_id +"\"\n")
            f.write("\t}\n")
            f.write("}\n\n")
        print("Alert created successfully!\n")



def create_provider_file(symbolTable: SymbolTable):
    key_id = symbolTable.getter("KEY_ID")[1]
    secret_key = symbolTable.getter("SECRET_KEY")[1]
    region = "us-east-1"
    print("Creating provider file with key id: {}, secret key: {} and region: {}\n".format(key_id, secret_key, region))
    with open(PATH + "main.tf", "w") as f:
        f.write("""
        terraform {\n
        \t required_providers {\n
        \t\t aws = {\n
        \t\t\t source = "hashicorp/aws"\n
        \t\t\t version = "~> 4.16"\n
        \t\t }\n
        \t }\n
        \t required_version = ">= 1.2.0"\n
        }\n\n
        provider "aws" {\n
        \t region = \"""" + region + """\"\n
        \t access_key = \"""" + key_id + """\"\n
        \t secret_key = \"""" + secret_key + """\"\n
        }\n\n
        """)
    print("Main file created successfully!\n")



#===============================================================================
#                              NODES
#===============================================================================

@abstractmethod
class Node():
    def __init__(self, value: str, children: list):
        self.value = value
        self.children = children

    def evaluate(self, symbolTable: SymbolTable) -> tuple:
        pass

class NoOp(Node):
    pass

class IntVal(Node):
    def evaluate(self, symbolTable: SymbolTable):
        return ("Int", int(self.value))
    
class StrVal(Node):
    def evaluate(self, symbolTable: SymbolTable):
        return ("String", self.value)
    
class UnOp(Node):
    def evaluate(self, symbolTable: SymbolTable):
        e_child_0 = self.children[0].evaluate(symbolTable)
        if e_child_0[0] == "Int":
            if self.value == "-":
                return ("Int", -e_child_0[1])
            elif self.value == "!":
                return ("Int", not e_child_0[1])
            return ("Int", e_child_0[1])
        else:
            sys.stderr.write("Type mismatch for Operation Un")
            sys.exit()

class BinOp(Node):
    def evaluate(self, symbolTable: SymbolTable):
        e_child_0 = self.children[0].evaluate(symbolTable)
        e_child_1 = self.children[1].evaluate(symbolTable)
        if e_child_0[0] == "Int" and e_child_1[0] == "Int":
            if self.value == "+":
                return ("Int", e_child_0[1] + e_child_1[1])
            elif self.value == "-":
                return ("Int", e_child_0[1] - e_child_1[1])
            elif self.value == "*":
                return ("Int", e_child_0[1] * e_child_1[1])
            elif self.value == "/":
                return ("Int", e_child_0[1] // e_child_1[1])
        elif self.value == ".":
            return ("String", str(e_child_0[1]) + str(e_child_1[1]))
        else:
            sys.stderr.write("Type mismatch for Operation")
            sys.exit()

class Identifier(Node):
    def evaluate(self, symbolTable: SymbolTable):
        return symbolTable.getter(self.value)
    
class Block(Node):
    def evaluate(self, symbolTable: SymbolTable):
        for child in self.children:
            child.evaluate(symbolTable)

class VarDec(Node):
    def evaluate(self, symbolTable: SymbolTable):
        symbolTable.create(self.value, self.children[0].evaluate(symbolTable))

class FuncDec(Node):
    def evaluate(self, symbolTable: SymbolTable):
        functionTable.create(self.children[0].value, self)

class FuncCall(Node):
    def evaluate(self, symbolTable: SymbolTable):
        func_name = self.value
        func_total_args_declaraed = {}
        if self.value not in FUNC_NAMES:
            func_dec_node = functionTable.getter(self.value)
            func_name = func_dec_node.value
            for i in range(1, len(func_dec_node.children)):
                func_total_args_declaraed[func_dec_node.children[i].value] = func_dec_node.children[i].children[0].evaluate(symbolTable)[1]
        for i in range(len(self.children)):
            func_total_args_declaraed[self.children[i].value] = self.children[i].children[0].evaluate(symbolTable)[1]

        for i in range(len(FUNC_NEEDS[func_name][0])):
            if FUNC_NEEDS[func_name][0][i] not in func_total_args_declaraed.keys():
                sys.stderr.write("Missing argument: " + FUNC_NEEDS[func_name][0][i])
                sys.exit()
        
        for declared_arg in func_total_args_declaraed:
            if declared_arg not in FUNC_NEEDS[func_name][0] and declared_arg not in FUNC_NEEDS[func_name][1]:
                sys.stderr.write("Extra argument: " + declared_arg)
                sys.exit()
        
        append_new_function(func_name, func_total_args_declaraed)
            

class ForNode(Node):
    def evaluate(self, symbolTable: SymbolTable):
        min_value = self.children[0].evaluate(symbolTable)
        max_value = self.children[1].evaluate(symbolTable)
        if min_value[0] != "Int" or max_value[0] != "Int":
            sys.stderr.write("Type mismatch for For arguments")
            sys.exit()
        symbolTable.create(self.value, ("Int", min_value))
        for i in range(min_value[1], max_value[1]):
            symbolTable.setter(self.value, ("Int", i))
            self.children[2].evaluate(symbolTable)
        symbolTable.delete(self.value)

class OnNode(Node):
    def evaluate(self, symbolTable: SymbolTable):
        value = self.children[0].evaluate(symbolTable)
        instance_id = self.children[1].evaluate(symbolTable)
        if value[0] != "Int":
            sys.stderr.write("Type mismatch for On argument")
            sys.exit()
        if instance_id[0] != "String":
            sys.stderr.write("Type mismatch for On argument")
            sys.exit()
        AlertBuilder.create_alert(self.value[0], self.value[1], value[1], instance_id[1])


#===============================================================================
#                              PREPRO
#===============================================================================
class PrePro():
    def filter(source):
        # create folder infrastructure 
        with open(PATH + "instance.tf", "w") as f:
            f.write("")
        with open(PATH + "alert.tf", "w") as f:
            f.write("")
        with open(PATH + "main.tf", "w") as f:
            f.write("")
        with open(PATH + "security_group.tf", "w") as f:
            f.write("")
        # using regex, remove all comments
        source = re.sub(r"#.*\n", "\n", source)
        source = re.sub(r"#.*", "", source)
        return source
    
#===============================================================================
#                              PARSER
#===============================================================================

class Parser():
    tokenizer = None

    def parseFactor():
        result = None
        if Parser.tokenizer.next.type == "INT":
            result = IntVal(Parser.tokenizer.next.value, [])
            Parser.tokenizer.selectNext()
        elif Parser.tokenizer.next.type == "STRING":
            result = StrVal(Parser.tokenizer.next.value, [])
            Parser.tokenizer.selectNext()
        elif Parser.tokenizer.next.type == "ID":
            result =  Identifier(Parser.tokenizer.next.value, [])
            Parser.tokenizer.selectNext()
        elif Parser.tokenizer.next.type == "MINUS":
            Parser.tokenizer.selectNext()
            result = UnOp("-", [Parser.parseFactor()])
        elif Parser.tokenizer.next.type == "PLUS":
            Parser.tokenizer.selectNext()
            result = UnOp("+", [Parser.parseFactor()])
        elif Parser.tokenizer.next.type == "OPEN_BRACKET":
            Parser.tokenizer.selectNext()
            result = Parser.parseExpression()
            if Parser.tokenizer.next.type != "CLOSE_BRACKET":
                sys.stderr.write("Expected ), received: " + Parser.tokenizer.next.type)
                sys.exit(1)
            Parser.tokenizer.selectNext()
        else:
            sys.stderr.write("Token different from expected: "+ Parser.tokenizer.next.type)
            sys.exit(1)
        return result
    
    def parseTerm():
        result = Parser.parseFactor()
        while Parser.tokenizer.next.type == "MULT" or Parser.tokenizer.next.type == "DIV":
            operation = Parser.tokenizer.next.type
            Parser.tokenizer.selectNext()
            if operation == "MULT":
                result = BinOp("*", [result, Parser.parseFactor()])
            elif operation == "DIV":
                result = BinOp("/", [result, Parser.parseFactor()])
            else:
                sys.stderr.write("Token different from expected * OR /")
                sys.exit(1)
        if Parser.tokenizer.next.type == "INT":
            sys.stderr.write("Expected operator")
            sys.exit(1)
        else:
            return result

    def parseExpression():
        result = Parser.parseTerm()
        while Parser.tokenizer.next.type == "PLUS" or Parser.tokenizer.next.type == "MINUS" or Parser.tokenizer.next.type == "CONCAT":
            operation = Parser.tokenizer.next.type
            Parser.tokenizer.selectNext()
            if operation == "PLUS":
                result = BinOp("+", [result, Parser.parseTerm()])
            elif operation == "MINUS":
                result = BinOp("-", [result, Parser.parseTerm()])
            elif operation == "CONCAT":
                result = BinOp(".", [result, Parser.parseTerm()])
            else:
                sys.stderr.write("Token different from + - .")
                sys.exit(1)
        return result
    
    def parseDecStatement():
        ### *+   VAR   +* ###
        if Parser.tokenizer.next.type == "ID":
            id = Parser.tokenizer.next.value
            Parser.tokenizer.selectNext()
            if Parser.tokenizer.next.type == "is":
                Parser.tokenizer.selectNext()
                return VarDec(id, [Parser.parseExpression()])
            else:
                sys.stderr.write("Expected is - received: " + Parser.tokenizer.next.type)
                sys.exit(1)
        ### *+   FUNC DEC   +* ###
        elif Parser.tokenizer.next.type == "function":
            Parser.tokenizer.selectNext()
            if Parser.tokenizer.next.type == "FUNC_NAME":
                func_name = Parser.tokenizer.next.value
                Parser.tokenizer.selectNext()
                if Parser.tokenizer.next.type == "as":
                    Parser.tokenizer.selectNext()
                    if Parser.tokenizer.next.type == "ID":
                        id = Parser.tokenizer.next.value
                        Parser.tokenizer.selectNext()
                        if Parser.tokenizer.next.type != "with":
                            sys.stderr.write("Expected with")
                            sys.exit(1)
                        Parser.tokenizer.selectNext()
                        if Parser.tokenizer.next.type != "ENDLINE":
                            sys.stderr.write("Expected ENDLINE")
                            sys.exit(1)
                        Parser.tokenizer.selectNext()
                        func_children = []
                        func_children.append(Identifier(id, []))
                        if Parser.tokenizer.next.type != "end":
                            if Parser.tokenizer.next.type != "FUNC_ARG":
                                sys.stderr.write("Expected FUNC_ARG")
                                sys.exit(1)
                            func_arg = Parser.tokenizer.next.value
                            Parser.tokenizer.selectNext()
                            if Parser.tokenizer.next.type != "as":
                                sys.stderr.write("Expected as")
                                sys.exit(1)
                            Parser.tokenizer.selectNext()
                            func_children.append(VarDec(func_arg, [Parser.parseExpression()]))
                            Parser.tokenizer.selectNext()
                            if Parser.tokenizer.next.type != "ENDLINE":
                                while Parser.tokenizer.next.type != "end":
                                    if Parser.tokenizer.next.type != "and":
                                        sys.stderr.write("Expected and")
                                        sys.exit(1)
                                    Parser.tokenizer.selectNext()
                                    if Parser.tokenizer.next.type != "ENDLINE":
                                        sys.stderr.write("Expected ENDLINE")
                                        sys.exit(1)
                                    if Parser.tokenizer.next.type != "FUNC_ARG":
                                        sys.stderr.write("Expected FUNC_ARG")
                                        sys.exit(1)
                                    func_arg = Parser.tokenizer.next.value
                                    Parser.tokenizer.selectNext()
                                    if Parser.tokenizer.next.type != "as":
                                        sys.stderr.write("Expected as")
                                        sys.exit(1)
                                    Parser.tokenizer.selectNext()
                                    func_children.append(VarDec(func_arg, [Parser.parseExpression()]))
                            else:
                                Parser.tokenizer.selectNext()
                        if Parser.tokenizer.next.type != "end":
                            sys.stderr.write("Expected end")
                            sys.exit(1)
                        Parser.tokenizer.selectNext()
                        if Parser.tokenizer.next.type != "ENDLINE":
                            sys.stderr.write("Expected ENDLINE")
                            sys.exit(1)
                        return FuncDec(func_name, func_children)
                    else:
                        sys.stderr.write("Expected as")
                        sys.exit(1)
                else:
                    sys.stderr.write("Expected ID")
                    sys.exit(1)
        elif Parser.tokenizer.next.type == "START_BUILD":
            Parser.tokenizer.selectNext()
            if Parser.tokenizer.next.type != "ENDLINE":
                sys.stderr.write("Expected ENDLINE")
                sys.exit(1)
            Parser.tokenizer.selectNext()
            build_statements = []
            while Parser.tokenizer.next.type != "END_BUILD":
                build_statements.append(Parser.parseBuildStatements())
                Parser.tokenizer.selectNext()
                if Parser.tokenizer.next.type != "ENDLINE":
                    sys.stderr.write("Expected ENDLINE for build statement")
                    sys.exit(1)
                Parser.tokenizer.selectNext()
            return Block("", build_statements)
        ### *+   ENDLINE   +* ###
        elif Parser.tokenizer.next.type == "ENDLINE":
            return NoOp("", [])
        else:
            sys.stderr.write("Not a Statement")
            sys.exit(1)

    def parseBuildStatements():
        ### *+   PERFORM   +* ###
        if Parser.tokenizer.next.type == "perform":
            return Parser.parsePerform()
        ### *+   FOR   +* ###
        elif Parser.tokenizer.next.type == "for":
            Parser.tokenizer.selectNext()
            if Parser.tokenizer.next.type != "ID":
                sys.stderr.write("Expected ID")
                sys.exit(1)
            id = Parser.tokenizer.next.value
            Parser.tokenizer.selectNext()
            if Parser.tokenizer.next.type != "in":
                sys.stderr.write("Expected in")
                sys.exit(1)
            Parser.tokenizer.selectNext()
            min_value = Parser.parseExpression()
            if Parser.tokenizer.next.type != "TO":
                sys.stderr.write("Expected :")
                sys.exit(1)
            Parser.tokenizer.selectNext()
            max_value = Parser.parseExpression()
            if Parser.tokenizer.next.type != "perform":
                sys.stderr.write("Expected perform")
                sys.exit(1)
            return ForNode(id, [min_value, max_value, Parser.parsePerform()])
        ### *+   ON   +* ###
        elif Parser.tokenizer.next.type == "on":
            Parser.tokenizer.selectNext()
            if Parser.tokenizer.next.type != "MONITERING_METRIC":
                sys.stderr.write("Expected MONITERING_METRIC")
                sys.exit(1)
            monitoring_metric = Parser.tokenizer.next.value
            Parser.tokenizer.selectNext()
            if Parser.tokenizer.next.type != "COMPARISON_OPERATOR":
                sys.stderr.write("Expected COMPARISON_OPERATOR")
                sys.exit(1)
            comparison_operator = Parser.tokenizer.next.value
            Parser.tokenizer.selectNext()
            expression = Parser.parseExpression()
            if Parser.tokenizer.next.type != "in":
                sys.stderr.write("Expected in")
                sys.exit(1)
            Parser.tokenizer.selectNext()
            instance_id = Parser.parseExpression()
            if Parser.tokenizer.next.type != "alert":
                sys.stderr.write("Expected alert")
                sys.exit(1)
            return OnNode((monitoring_metric, comparison_operator), [expression, instance_id])
        else:
            sys.stderr.write("Not a Build Statement - " + Parser.tokenizer.next.type)
            sys.exit(1)

    def parsePerform():
        Parser.tokenizer.selectNext()
        if Parser.tokenizer.next.type != "FUNC_NAME" and Parser.tokenizer.next.type != "ID":
            sys.stderr.write("Expected FUNC_NAME or ID")
            sys.exit(1)
        func_name = Parser.tokenizer.next.value
        Parser.tokenizer.selectNext()
        if Parser.tokenizer.next.type != "with":
            sys.stderr.write("Expected with")
            sys.exit(1)
        Parser.tokenizer.selectNext()
        if Parser.tokenizer.next.type != "ENDLINE":
            sys.stderr.write("Expected ENDLINE")
            sys.exit(1)
        Parser.tokenizer.selectNext()
        func_children = []
        if Parser.tokenizer.next.type != "end":
            if Parser.tokenizer.next.type != "FUNC_ARG":
                sys.stderr.write("Expected FUNC_ARG")
                sys.exit(1)
            func_arg = Parser.tokenizer.next.value
            Parser.tokenizer.selectNext()
            if Parser.tokenizer.next.type != "as":
                sys.stderr.write("Expected as")
                sys.exit(1)
            Parser.tokenizer.selectNext()
            func_children.append(VarDec(func_arg, [Parser.parseExpression()]))
            if Parser.tokenizer.next.type != "ENDLINE":
                while Parser.tokenizer.next.type != "ENDLINE":
                    if Parser.tokenizer.next.type != "and":
                        sys.stderr.write("Expected and" + Parser.tokenizer.next.type)
                        sys.exit(1)
                    Parser.tokenizer.selectNext()
                    if Parser.tokenizer.next.type != "ENDLINE":
                        sys.stderr.write("Expected ENDLINE - " + Parser.tokenizer.next.type)
                        sys.exit(1)
                    Parser.tokenizer.selectNext()
                    if Parser.tokenizer.next.type != "FUNC_ARG":
                        sys.stderr.write("Expected FUNC_ARG")
                        sys.exit(1)
                    func_arg = Parser.tokenizer.next.value
                    Parser.tokenizer.selectNext()
                    if Parser.tokenizer.next.type != "as":
                        sys.stderr.write("Expected as")
                        sys.exit(1)
                    Parser.tokenizer.selectNext()
                    func_children.append(VarDec(func_arg, [Parser.parseExpression()]))
            Parser.tokenizer.selectNext()
            if Parser.tokenizer.next.type != "end":
                sys.stderr.write("Expected end - " + Parser.tokenizer.next.type)
                sys.exit(1)
            return FuncCall(func_name, func_children)


    def parseBlock():
        Parser.tokenizer.selectNext()
        statements = []
        while Parser.tokenizer.next.type != "EOF":
            statements.append(Parser.parseDecStatement())
            Parser.tokenizer.selectNext()
        return Block("", statements)
    
    def run(code):
        Parser.tokenizer = Tokenizer(PrePro.filter(code))
        result = Parser.parseBlock() # Retorna a raiz da arvore AST
        if Parser.tokenizer.next.type != "EOF":
            sys.stderr.write("Expected EOF")
            sys.exit(1)
        symbolTable = SymbolTable()
        result.evaluate(symbolTable)
        create_provider_file(symbolTable)
        print("Compilation OK\n")


# =================================================================
#                             MAIN
# =================================================================
def main():
    if len(sys.argv) == 2:
        code = open(sys.argv[1], "r").read()
        Parser.run(code)
    elif len(sys.argv) == 1:
        sys.stderr.write("No code provided")
        sys.exit(1)
    else:
        sys.stderr.write("Too many arguments")
        sys.exit(1)

## FOR DEBUG:
# def main():
#     code = open("teste.jl", "r").read()
#     Parser.run(code)

if __name__ == "__main__":
    main()