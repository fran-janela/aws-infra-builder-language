from rply import ParserGenerator

class Parser():
    def __init__(self):
        # add all lexer tokens to parser
        self.pg = ParserGenerator(["OPEN_PAREN", "CLOSE_PAREN", "SUM", "SUB", "MUL",
                                    "IS", "AS", "LIST", "OF", "LOAD", "NEEDS", 
                                    "WITH", "AND", "END", "FIND", "GT", "LT", "ET", 
                                    "NET", "GTE", "LTE", "FUNC_TYPE", "FOR", "IN", 
                                    "FUNC_DEC", "START_BUILD", "END_BUILD", "IDENTIFIER", 
                                    "NUMBER", "STRING", "NEWLINE", "COMMA", "ON", 
                                    "PERFORM", "USE"], 
                                    precedence=[
                                    ('left', ['SUM', 'SUB']),
                                    ('left', ['MUL'])
                                    ])
        
        
    def parse(self):
        @self.pg.production("block : statements")
        def program(p):
            return p[0]
        
        @self.pg.production("statements : statement statements")
        @self.pg.production("statements : statement")
        def statements(p):
            return p
        
        @self.pg.production("statement : NEWLINE")
        @self.pg.production("statement : declaration NEWLINE")
        @self.pg.production("statement : START_BUILD NEWLINE build_statements END_BUILD")
        def statement(p):
            return p[0]
        
        @self.pg.production("declaration : assignment")
        @self.pg.production("declaration : FUNC_DEC function_declaration")
        def declaration(p):
            return p[0]
        
        @self.pg.production("assignment : IDENTIFIER IS value")
        @self.pg.production("assignment : IDENTIFIER IS LIST values")
        @self.pg.production("assignment : IDENTIFIER IS LOAD STRING")
        @self.pg.production("assignment : IDENTIFIER IS IDENTIFIER")
        def assignment(p):
            return p
        
        @self.pg.production("function_declaration : FUNC_TYPE AS IDENTIFIER NEEDS identifiers WITH NEWLINE function_variable_declarations END")
        @self.pg.production("function_declaration : FUNC_TYPE AS IDENTIFIER WITH NEWLINE function_variable_declarations END")
        def function_declaration(p):
            return p
        
        @self.pg.production("function_variable_declarations : function_variable_declaration NEWLINE")
        @self.pg.production("function_variable_declarations : function_variable_declaration AND NEWLINE function_variable_declarations")
        def function_variable_declarations(p):
            return p
        
        @self.pg.production("function_variable_declaration : LOAD IDENTIFIER")
        @self.pg.production("function_variable_declaration : IDENTIFIER AS value")
        @self.pg.production("function_variable_declaration : IDENTIFIER AS IDENTIFIER")
        @self.pg.production("function_variable_declaration : IDENTIFIER AS LIST values")
        def function_variable_declaration(p):
            return p
        
        @self.pg.production("build_statements : build_statement")
        @self.pg.production("build_statements : build_statement build_statements")
        def build_statements(p):
            return p
        
        @self.pg.production("build_statement : NEWLINE")
        @self.pg.production("build_statement : loop_statement")
        @self.pg.production("build_statement : conditional_statement")
        @self.pg.production("build_statement : perform_statement")
        def build_statement(p):
            return p[0]
        
        @self.pg.production("loop_statement : FOR IDENTIFIER IN IDENTIFIER perform_statement")
        def loop_statement(p):
            return p
        
        @self.pg.production("conditional_statement : ON condition perform_statement")
        def conditional_statement(p):
            return p
        
        @self.pg.production("condition : condition_variable compare_methods condition_variable")
        def condition(p):
            return p
        
        @self.pg.production("condition_variable : IDENTIFIER")
        @self.pg.production("condition_variable : value")
        @self.pg.production("condition_variable : find_statement")
        def condition_variable(p):
            return p
        
        @self.pg.production("compare_methods : GT")
        @self.pg.production("compare_methods : LT")
        @self.pg.production("compare_methods : ET")
        @self.pg.production("compare_methods : NET")
        @self.pg.production("compare_methods : GTE")
        @self.pg.production("compare_methods : LTE")
        def compare_methods(p):
            return p[0]
        
        @self.pg.production("perform_statement : PERFORM IDENTIFIER WITH arguments NEWLINE")
        @self.pg.production("perform_statement : PERFORM IDENTIFIER WITH USE IDENTIFIER NEWLINE")
        @self.pg.production("perform_statement : PERFORM FUNC_TYPE WITH arguments NEWLINE")
        @self.pg.production("perform_statement : PERFORM FUNC_TYPE WITH USE IDENTIFIER NEWLINE")
        def perform_statement(p):
            return p
        
        @self.pg.production("arguments : function_variable_declaration")
        @self.pg.production("arguments : function_variable_declaration AND arguments")
        def arguments(p):
            return p
        
        @self.pg.production("find_statement : FIND IDENTIFIER OF find_statement")
        @self.pg.production("find_statement : FIND IDENTIFIER OF IDENTIFIER")
        def find_statement(p):
            return p
        
        @self.pg.production("value : STRING")
        @self.pg.production("value : expression")
        def value(p):
            return p[0]
        
        @self.pg.production("values : value")
        @self.pg.production("values : value COMMA values")
        def values(p):
            return p
        
        @self.pg.production("expression : term")
        @self.pg.production("expression : term SUM expression")
        @self.pg.production("expression : term SUB expression")
        def expression(p):
            return p
        
        @self.pg.production("term : factor")
        @self.pg.production("term : factor MUL term")
        def term(p):
            return p
        
        @self.pg.production("factor : NUMBER")
        @self.pg.production("factor : OPEN_PAREN expression CLOSE_PAREN")
        @self.pg.production("factor : IDENTIFIER")
        def factor(p):
            return p[0]
        
        @self.pg.production("identifiers : IDENTIFIER")
        @self.pg.production("identifiers : IDENTIFIER COMMA identifiers")
        def identifiers(p):
            return p

        @self.pg.error
        def error_handle(token):
            print("TOKEN ERROR: ", token)
            raise ValueError(token)
        
    def get_parser(self):
        return self.pg.build()

        
        