from compilador.lexer import Lexer
from compilador.parser import Parser

text_input = open('tests/teste2.txt', 'r').read()

lexer = Lexer().get_lexer()
tokens = lexer.lex(text_input)

for token in tokens:
    print(token)

pg = Parser()
pg.parse()
parser = pg.get_parser()


try:
    result = parser.parse(lexer.lex(text_input))
    print("Parsing completed successfully!")
except Exception as e:
    print("Parsing failed!")
    print("Exception: ",e)

