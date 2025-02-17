from dataTypeDeclaration import *
from Zoro_parser import ZoroParser

# If a new instruction is defined, add a dataclass, class name should be in all caps
@dataclass
class PUSH:
    val: Value

@dataclass
class POP:
    pass

@dataclass
class DUP:
    pass

@dataclass
class LABEL:
    label: int = -1

@dataclass
class JMP_IF_FALSE:
    to: LABEL

@dataclass
class JMP_IF_TRUE:
    to: LABEL

@dataclass
class JMP:
    to: LABEL

@dataclass
class HALT:
    pass


#If you define a new instruction, add it here
Instructions = PUSH | POP | DUP | JMP_IF_FALSE | JMP_IF_TRUE | JMP | HALT | Operator


class ByteCode:
    instructions: List[Instructions]

    def __init__(self):
        self.instructions = []

    def label(self):
        return LABEL(-1)
    
    def emit(self, ins):
        self.instructions.append(ins)

    def emit_label(self, label):
        label.label = len(self.instructions)

class Frame:
    locals: List[Value] = [None]*32
    retaddr: int = -1
    dynLink: 'Frame' = None

l = []
currFrame = Frame()

#in case of binary operations, please remember that left is pushed before right
#thus while popping, the first value you pop will be right, not left.
def parseAST_(ast: AST, code: ByteCode, ) -> None:

    def parse_(ast):
        parseAST_(ast, code)

    match ast:

        case MathOp("+", left, right):
            parse_(left)
            parse_(right)
            code.emit(Operator('+'))
        case MathOp("-", left, right):
            parse_(left)
            parse_(right)
            code.emit(Operator('-'))
        case MathOp("*", left, right):
            parse_(left)
            parse_(right)
            code.emit(Operator('*'))
        case MathOp("/", left, right):
            parse_(left)
            parse_(right)
            code.emit(Operator('/'))
        case MathOp("//", left, right):
            parse_(left)
            parse_(right)
            code.emit(Operator('//'))
        case MathOp("**", left, right):
            parse_(left)
            parse_(right)
            code.emit(Operator('**'))
        case MathOp("%", left, right):
            parse_(left)
            parse_(right)
            code.emit(Operator('%'))

        case CndOp(">", left, right):
            parse_(left)
            parse_(right)
            code.emit(Operator('>'))
        case CndOp("<", left, right):
            parse_(left)
            parse_(right)
            code.emit(Operator('<'))
        case CndOp(">=", left, right):
            parse_(left)
            parse_(right)
            code.emit(Operator('>='))
        case CndOp("<=", left, right):
            parse_(left)
            parse_(right)
            code.emit(Operator('<='))
        case CndOp("==", left, right):
            parse_(left)
            parse_(right)
            code.emit(Operator('=='))
        case CndOp("!=", left, right):
            parse_(left)
            parse_(right)
            code.emit(Operator('!='))

        case UnOp("-", right):
            parse_(right)
            code.emit(Operator('u-'))
        case UnOp("~", right):
            parse_(right)
            code.emit(Operator('u~'))
        case UnOp("not", right):
            parse_(right)
            code.emit(Operator('not'))

        case BitOp("&", left, right):
            parse_(left)
            parse_(right)
            code.emit(Operator('&'))
        case BitOp("|", left, right):
            parse_(left)
            parse_(right)
            code.emit(Operator('|'))
        case BitOp("^", left, right):
            parse_(left)
            parse_(right)
            code.emit(Operator('^'))
        case BitOp("<<", left, right):
            parse_(left)
            parse_(right)
            code.emit(Operator('<<'))
        case BitOp(">>", left, right):
            parse_(left)
            parse_(right)
            code.emit(Operator('>>'))
            
        case LogOp("and", left, right):
            label = LABEL()
            parse_(left)
            code.emit(DUP())
            code.emit(JMP_IF_FALSE(label))
            code.emit(POP())
            parse_(right)
            code.emit_label(label)
        case LogOp("or", left, right):
            label = LABEL()
            parse_(left)
            code.emit(DUP())
            code.emit(JMP_IF_TRUE(label))
            code.emit(POP())
            parse_(right)
            code.emit_label(label)
        case LogOp("xor", left, right):
            parse_(LogOp('or', LogOp('and', left, UnOp('not', right)), LogOp('and', UnOp('not', left), right)))
        case LogOp("nand", left, right):
            parse_(LogOp("and", left, right))
            code.emit(Operator('not'))
        case LogOp("nor", left, right):
            parse_(LogOp("or", left, right))
            code.emit(Operator('not'))
        case LogOp("xnor", left, right):
            parse_(LogOp("xor", left, right))
            code.emit(Operator('not'))
        case Sequence(seq):
            for s in seq:
                parse_(s)
                code.emit(POP())
            code.instructions.pop()

        case If(con, seq):
            endlab = LABEL()
            l = len(con)
            for i in range(l):
                falselab=LABEL()
                parse_(con[i])
                code.emit(JMP_IF_FALSE(falselab))
                parse_(seq[i])
                code.emit(JMP(endlab))
                code.emit_label(falselab)
            if len(seq) > l:
                parse_(seq[l])
            code.emit_label(endlab)

        case While(cnd, seq):
            looplab = LABEL()
            endlab = LABEL()
            parse_(cnd)
            code.emit(JMP_IF_FALSE(endlab))
            code.emit_label(looplab)
            parse_(seq)
            parse_(cnd)
            code.emit(JMP_IF_FALSE(endlab))
            code.emit(POP())
            code.emit(JMP(looplab))
            code.emit_label(endlab)

        
def pprint(l):
    c = 0
    for i in l:
        match i:
            case PUSH(val):
                print(f"\t{c}\t: PUSH    \t{val}")
            case Operator(op):
                print(f"\t{c}\t: {op}")
            case DUP():
                print(f"\t{c}\t: DUP")
            case POP():
                print(f"\t{c}\t: POP")
            case JMP(to):
                print(f"\t{c}\t: JMP    \t{to.label}")
            case JMP_IF_FALSE(to):
                print(f"\t{c}\t: JMP_IF_FALSE\t{to.label}")
            case JMP_IF_TRUE(to):
                print(f"\t{c}\t: JMP_IF_TRUE\t{to.label}")
            case LABEL(label):
                print(f"\t{c}\t: LABEL({label})")
            case HALT():
                print(f"\t{c}\t: HALT")
        c += 1

def parseAST(ast):
    code = ByteCode()
    parseAST_(ast, code)
    code.emit(HALT())
    return code
  
# ast = ZoroParser(<YOUR CODE HERE AS A STRING>).Parsed_AST
# print(ast)
# code = parseAST(<COPIED AST FROM THE TERMINAL HERE>) #For some reason, when the output of the parser is directly put here, the literal values ie int, bool, string, frac, float are ignored
# pprint(code.instructions) #Pretty print
