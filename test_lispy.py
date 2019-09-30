import pytest
import wexpect


class Lispy:
    PROMPT = 'lispy>'

    def __init__(self):
        self.session = wexpect.spawn('lispy.exe')
        self.session.expect(self.PROMPT)
    
    def eval(self, expression):
        self.session.sendline(expression)
        self.session.expect(self.PROMPT)
        return self.session.before.strip()

    def define_fun(self):
        self.eval(r'def {fun} (\ {args body} {def (head args) (\ (tail args) body)})') == '()'

    def close(self):
        self.session.close()

    def __del__(self):
        self.close()


@pytest.fixture
def lispy():
    lispy = Lispy()
    yield lispy
    lispy.close()


def test_builtin_operators(lispy):
    assert lispy.eval('+ 1 1') == '2'
    assert lispy.eval('- 1 1') == '0'
    assert lispy.eval('* 1 1') == '1'
    assert lispy.eval('* 4 2') == '8'
    assert lispy.eval('/ 4 2') == '2'
    assert lispy.eval('+') == '<builtin>'
    assert lispy.eval('-') == '<builtin>'
    assert lispy.eval('*') == '<builtin>'
    assert lispy.eval('/') == '<builtin>'


def test_sexpr(lispy):
    assert lispy.eval('(+ 1 1)') == '2'
    assert lispy.eval('- (* 10 10) (+ 1 1 1)') == '97'
    assert lispy.eval('* 10 (+ 1 51)') == '520'
    assert lispy.eval('+ 1 (* 7 5) 3') == '39'
    assert lispy.eval('(- 100)') == '-100'
    assert lispy.eval('*    55     101    (+ 0 0 0)') == '0'

    assert lispy.eval('') == '()'
    

def test_qexpr(lispy):
    assert lispy.eval('{1 2 3 4}') == '{1 2 3 4}'
    assert lispy.eval('{1 2 (+ 5 6) 4}') == '{1 2 (+ 5 6) 4}'
    assert lispy.eval('{{2 3 4} {1}}') == '{{2 3 4} {1}}'


def builtin_list(lispy):
    assert lispy.eval('list 1 2 3 4') == '{1 2 3 4}'
    assert lispy.eval('{head (list 1 2 3 4)}') == '{head (list 1 2 3 4)}'
    assert lispy.eval('eval {head (list 1 2 3 4)}') == '{1}'
    assert lispy.eval('tail {tail tail tail}') == '{tail tail}'
    assert lispy.eval('eval (tail {tail tail {5 6 7}})') == '{6 7}'
    assert lispy.eval('eval (head {(+ 1 2) (+ 10 20)})') == '3'


def test_variables(lispy):
    assert lispy.eval('eval (head {5 10 11 15})') == '5'
    assert lispy.eval('eval (head {+ - + - * /})') == '<builtin>'
    assert lispy.eval('(eval (head {+ - + - * /})) 10 20') == '30'


def test_def(lispy):
    assert lispy.eval('def {x} 100') == '()'
    assert lispy.eval('def {y} 200') == '()'
    assert lispy.eval('x') == '100'
    assert lispy.eval('y') == '200'
    assert lispy.eval('+ x y') == '300'
    assert lispy.eval('def {a b} 5 6') == '()'
    assert lispy.eval('+ a b') == '11'
    assert lispy.eval('def {arglist} {a b x y}') == '()'
    assert lispy.eval('arglist') == '{a b x y}'
    assert lispy.eval('def arglist 1 2 3 4') == '()'
    assert lispy.eval('list a b x y') == '{1 2 3 4}'


def test_function(lispy):
    assert lispy.eval(r'(\ {x y} {+ x y}) 10 20') == '30'
    assert lispy.eval('def {add-together} (\ {x y} {+ x y})') == '()'
    assert lispy.eval('add-together 10 20') == '30'


def test_partial_evaluation(lispy):
    assert lispy.eval('def {add-mul} (\ {x y} {+ x (* x y)})') == '()'
    assert lispy.eval('add-mul 10 20') == '210'
    assert lispy.eval('add-mul 10') == '(\ {y} {+ x (* x y)})'
    assert lispy.eval('def {add-mul-ten} (add-mul 10)') == '()'
    assert lispy.eval('add-mul-ten 50') == '510'


def test_function_definition(lispy):
    assert lispy.eval(r'def {fun} (\ {args body} {def (head args) (\ (tail args) body)})') == '()'
    assert lispy.eval('fun {add-together x y} {+ x y}') == '()'
    assert lispy.eval('add-together 1 2') == '3'


def test_currying(lispy):
    lispy.define_fun()

    assert lispy.eval('fun {unpack f xs} {eval (join (list f) xs)}') == '()'
    assert lispy.eval('fun {pack f & xs} {f xs}') == '()'
    assert lispy.eval('def {uncurry} pack') == '()'
    assert lispy.eval('def {curry} unpack') == '()'
    assert lispy.eval('curry + {5 6 7}') == '18'
    assert lispy.eval('uncurry head 5 6 7') == '{5}'

    assert lispy.eval('def {add-uncurried} +') == '()'
    assert lispy.eval('def {add-curried} (curry +)') == '()'
    assert lispy.eval('add-curried {5 6 7}') == '18'
    assert lispy.eval('add-uncurried 5 6 7') == '18'


def test_conditionals(lispy):
    assert lispy.eval('> 10 5') == '1'
    assert lispy.eval('<= 88 5') == '0'
    assert lispy.eval('== 5 6') == '0'
    assert lispy.eval('== 5 {}') == '0'
    assert lispy.eval('== 1 1') == '1'
    assert lispy.eval('!= {} 56') == '1'
    assert lispy.eval('== {1 2 3 {5 6}} {1    2   3   {5 6}}') == '1'
    assert lispy.eval('def {x y} 100 200') == '()'
    assert lispy.eval('if (== x y) {+ x y} {- x y}') == '-100'


def test_recursive_function(lispy):
    lispy.define_fun()

    assert lispy.eval(
            """
               (fun {len l} {
                 if (== l {})
                   {0}
                   {+ 1 (len (tail l))}
               })
            """) == '()'

    assert lispy.eval('len {1 2 3 4}') == '4'
    
    assert lispy.eval(
            "(fun {reverse l} {"
            "  if (== l {})"
            "    {{}}"
            "    {join (reverse (tail l)) (head l)}"
            "})") == '()'

    assert lispy.eval('reverse {1 2 3 4}') == '{4 3 2 1}'
    

def test_errors(lispy):
    assert lispy.eval('/ 10 0') == 'Error: Division By Zero'

    assert lispy.eval('(/ ())') == "Error: Function '/' passed "       \
                                   "incorrect type for argument 0. "   \
                                   "Got S-Expression, Expected Number."

    assert lispy.eval('hello') == "Error: Unbound symbol 'hello'"

    assert lispy.eval('+ 1 {5 6 7}') == "Error: Function '+' passed incorrect "         \
                                        "type for argument 1. Got Q-Expression, "       \
                                        "Expected Number."

    assert lispy.eval('head {1 2 3} {4 5 6}') == "Error: Function 'head' passed incorrect " \
                                                 "number of arguments. Got 2, Expected 1."

