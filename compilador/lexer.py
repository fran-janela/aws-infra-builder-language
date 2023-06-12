from rply import LexerGenerator

class Lexer():
    def __init__(self):
        self.lg = LexerGenerator()
        self.lexer = self.build_lexer()

    def _add_tokens(self):
        # Parenthesis
        self.lg.add('OPEN_PAREN', r'\(')
        self.lg.add('CLOSE_PAREN', r'\)')

        # Operators
        self.lg.add('SUM', r'\+')
        self.lg.add('SUB', r'\-')
        self.lg.add('MUL', r'\*')

        # Comma
        self.lg.add('COMMA', r'\,')

        # Identifiers
        self.lg.add('IS', 'is ')
        self.lg.add('AS', 'as ')
        self.lg.add('LIST', 'list of ')
        self.lg.add('OF', 'of ')
        self.lg.add('LOAD', 'load ')
        self.lg.add('NEEDS', 'needs ')
        self.lg.add('WITH', 'with')
        self.lg.add('AND', 'and')
        self.lg.add('END', 'end')
        self.lg.add('USE', 'use')

        # Find
        self.lg.add('FIND', 'find ')

        # Comparators
        self.lg.add('GT', 'gt ')
        self.lg.add('LT', 'lt ')
        self.lg.add('ET', 'et ')
        self.lg.add('NET', 'net ')
        self.lg.add('GTE', 'gte ')
        self.lg.add('LTE', 'lte ')

        # Function Types
        self.lg.add('FUNC_TYPE', r'(AutoScaleBuilder)|(LoadBalancerBuilder)|(InstanceBuilder)|(SubnetBuilder)|(SecurityGroupBuilder)|(EmailSender)')

        # Loops:
        self.lg.add('FOR', 'for each')
        self.lg.add('IN', 'in ')

        # Conditional Words
        self.lg.add('ON', 'on ')

        # Perform
        self.lg.add('PERFORM', 'perform ')

        # Function declaration
        self.lg.add('FUNC_DEC', 'f: ')

        # Build Identifiers
        self.lg.add('START_BUILD', 'START BUILD')
        self.lg.add('END_BUILD', 'END BUILD')

        # Identifiers:
        self.lg.add('IDENTIFIER', r'[a-zA-Z_][a-zA-Z0-9_]*')

        # Values
        self.lg.add('NUMBER', r'-?\d+')
        self.lg.add('STRING', r'"[^"]*"')

        # Newline
        self.lg.add('NEWLINE', r"\n")

        # Ignore comments
        self.lg.ignore(r'\#.*\n')

        # Ignore spaces
        self.lg.ignore(r' +|\t+|\r+|\f+|\v+')

    def build_lexer(self):
        self._add_tokens()
        return self.lg.build()

    def get_lexer(self):
        return self.lexer