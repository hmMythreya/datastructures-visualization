from tkinter import *

try:
    from drawnValue import *
    from VisualizationApp import *
except ModuleNotFoundError:
    from .drawnValue import *
    from .VisualizationApp import *

class InfixCalculator(VisualizationApp):
    nextColor = 0
    MAX_ARG_WIDTH = 20
    ARRAY_SIZE = 14
    MAX_EXPRESSION_LENGTH = ARRAY_SIZE * 2
    CELL_WIDTH = 50
    CELL_HEIGHT = 18
    CELL_BORDER = 2
    CELL_BORDER_COLOR = 'black'
    INPUT_BOX_X0 = 90
    INPUT_BOX_Y0 = 10
    INPUT_BOX_WIDTH = 400
    INPUT_BOX_HEIGHT = 30
    INPUT_BOX_BG = 'powder blue'
    OUTPUT_BOX_X0 = 570
    OUTPUT_BOX_Y0 = 350
    OUTPUT_BOX_WIDTH = 210
    OUTPUT_BOX_HEIGHT = 30
    OUTPUT_BOX_BG = VisualizationApp.OPERATIONS_BG
    TR_STACK_X0 = INPUT_BOX_X0
    TR_STACK_Y0 = 380
    TR_QUEUE_X0 = 280
    TR_QUEUE_Y0 = TR_STACK_Y0
    EV_STACK_X0 = TR_QUEUE_X0 + TR_QUEUE_X0 - TR_STACK_X0
    EV_STACK_Y0 = TR_STACK_Y0
    ARRAY_X0s = [TR_STACK_X0, TR_QUEUE_X0, EV_STACK_X0]
    PRECEDENCE_X0 = OUTPUT_BOX_X0 + 10
    PRECEDENCE_Y0 = 30
    PRECEDENCE_SPACING = 25
    operators = ["|", "&", "+-", "*/%", "^", "()"]
    allOperators = ''.join(operators)
    MAX_OPERATOR_STRING_WIDTH = max(len(s) for s in operators)

    def __init__(self, maxArgWidth=MAX_ARG_WIDTH, title="Infix Calculator", 
                 **kwargs):
        kwargs['title'] = title
        kwargs['maxArgWidth'] = maxArgWidth
        super().__init__(**kwargs)
        self.TRstack = []
        self.TRqueue = [drawnValue(None) for i in range(self.ARRAY_SIZE)]
        self.TRqueueRear = 0
        self.TRqueueFront = 1
        self.TRqueueSize = 0
        self.EVstack = []
        self.structures = [self.TRstack, self.TRqueue, self.EVstack]
        self.indices = [None] * 3
        self.buttons = self.makeButtons()
        self.display()

    def cellCoords(self, index, array=0):
        'Bounding box of a cell in one of the arrays for stacks & queue'
        return (self.ARRAY_X0s[array],
                self.TR_STACK_Y0 - self.CELL_HEIGHT * (index + 1),
                self.ARRAY_X0s[array] + self.CELL_WIDTH - self.CELL_BORDER,
                self.TR_STACK_Y0 - self.CELL_HEIGHT * index - self.CELL_BORDER)

    def cellCenter(self, index, array=0):
        box = self.cellCoords(index, array)
        return divide_vector(add_vector(box[:2], box[2:]), 2)

    # Get the coordinates of an index arrow pointing at a cell in an array
    def indexCoords(self, index, array=0, level=0):
        cell_coords = self.cellCoords(index, array)
        cell_center = self.cellCenter(index, array)
        x0 = cell_coords[0] - self.CELL_WIDTH * 3 // 5 - level * 45
        x1 = cell_coords[0] - self.CELL_WIDTH * 1 // 10
        y0 = y1 = cell_center[1]
        return x0, y0, x1, y1
    
    # Create an index arrow to point at a cell in one of the arrays
    def createIndex(
            self, index, array=0, name=None, level=0, color=None, font=None, 
            tags=()):
        if color is None:
            color = self.VARIABLE_COLOR
        if font is None:
            font = self.VARIABLE_FONT
        arrowCoords = self.indexCoords(index, array, level)
        arrow = self.canvas.create_line(
            *arrowCoords, arrow="last", fill=color, tags=tags)
        if name:
            label = self.canvas.create_text(
                *arrowCoords[:2], text=name, anchor=NE, font=font, fill=color, 
                tags=tags)
            return (arrow, label)

        return (arrow,)

    def inputBoxCoords(self):
        return (self.INPUT_BOX_X0, self.INPUT_BOX_Y0,
                self.INPUT_BOX_X0 + self.INPUT_BOX_WIDTH,
                self.INPUT_BOX_Y0 + self.INPUT_BOX_HEIGHT)

    def outputBoxCoords(self):
        return (self.OUTPUT_BOX_X0, self.OUTPUT_BOX_Y0,
                self.OUTPUT_BOX_X0 + self.OUTPUT_BOX_WIDTH,
                self.OUTPUT_BOX_Y0 + self.OUTPUT_BOX_HEIGHT)

    def operandAndOperatorCoords(self):
        oBox = self.outputBoxCoords()
        y0 = oBox[1] - 3 * (oBox[3] - oBox[1])
        return (((oBox[0] * 4 + oBox[2]) // 5, y0),
                ((oBox[0] + oBox[2]) // 2, y0),
                ((oBox[0] + oBox[2] * 4) // 5, y0))
    
    def createArrayCell(self, index, array=0, tags=()):
        'Create a box representing an array cell'
        cell_coords = self.cellCoords(index, array)
        half_border = self.CELL_BORDER // 2
        other_half = self.CELL_BORDER - half_border
        cell = add_vector(cell_coords,
                          (-half_border, -half_border, other_half, other_half))
        rect = self.canvas.create_rectangle(
            cell, fill=None, outline=self.CELL_BORDER_COLOR,
            width=self.CELL_BORDER, tags=tags)
        self.canvas.lower(rect)
        return rect

    def createCellValue(self, indexOrCoords, value, array=0, color=None):
        """Create new canvas items to represent a cell value.  A rectangle
        is created filled with a particular color with an text value centered
        inside.  The position of the cell can either be an integer index in
        one of the arrays or the bounding box coordinates of the rectangle.
        If color is not supplied, the next color in the palette among
        those not used for operator precedence is chosen.
        Returns the tuple, (square, text), of canvas items
        """
        # Determine position and color of cell
        if isinstance(indexOrCoords, int):
            rectPos = self.cellCoords(indexOrCoords, array)
            valPos = self.cellCenter(indexOrCoords, array)
        else:
            rectPos = indexOrCoords
            valPos = divide_vector(add_vector(rectPos[:2], rectPos[2:]), 2)

        if color is None:
            # Take the next color from the palette
            color = drawnValue.palette[len(self.operators) + self.nextColor]
            self.nextColor = (self.nextColor + 1) % (
                len(drawnValue.palette) - len(self.operators))
        cell_rect = self.canvas.create_rectangle(
            *rectPos, fill=color, outline='', width=0)
        cell_val = self.canvas.create_text(
            *valPos, text=value, font=self.tokenFont, fill=self.VALUE_COLOR)
        return cell_rect, cell_val

    def display(self, inputString=''):
        self.tokenFont = (self.VALUE_FONT[0], self.VALUE_FONT[1] * 2 // 3)
        self.canvas.delete("all")

        inBoxCoords = self.inputBoxCoords()
        self.inputBox = self.canvas.create_rectangle(
            *inBoxCoords, fill=self.INPUT_BOX_BG, width=1, outline='black')
        self.inputLabel = self.canvas.create_text(
            inBoxCoords[0] - 10, (inBoxCoords[1] + inBoxCoords[3]) // 2,
            text='Infix', anchor=E, font=self.VARIABLE_FONT, 
            fill=self.VARIABLE_COLOR)

        # Text input string
        self.infixInputString = self.canvas.create_text(
            inBoxCoords[0] + 10, (inBoxCoords[1] + inBoxCoords[3]) // 2,
            text=inputString, anchor=W, font=self.VALUE_FONT,
            fill=self.VALUE_COLOR)

        # Operator prececedence table
        tableTitle = "Operator Precedence"
        self.canvas.create_text(
            self.PRECEDENCE_X0, self.PRECEDENCE_Y0, text=tableTitle,
            anchor=W, font=self.VARIABLE_FONT, fill='black')
        nLevels = len(self.operators)
        pad = 5
        x0, y0 = self.PRECEDENCE_X0, self.PRECEDENCE_Y0 
        dY = self.PRECEDENCE_SPACING
        width = self.textWidth(self.VARIABLE_FONT, tableTitle)
        for j, operatorString in enumerate(self.operators):
            self.canvas.create_rectangle(
                x0 - pad,         y0 + int((nLevels - j - 0.5) * dY),
                x0 + width + pad, y0 + int((nLevels - j + 0.5) * dY),
                fill=drawnValue.palette[j], outline='', width=0)
            self.canvas.create_text(
                x0, y0 + (nLevels - j) * dY,
                text=', '.join(c for c in operatorString),
                anchor=W, font=self.VARIABLE_FONT, fill='black')
            
        outBoxCoords = self.outputBoxCoords()
        self.outputBox = self.canvas.create_rectangle(
            *outBoxCoords, fill=self.OUTPUT_BOX_BG, width=1, outline='black')
        self.outputLabel = self.canvas.create_text(
            (outBoxCoords[0] + outBoxCoords[2]) // 2, outBoxCoords[1] - 10,
            text='Output', anchor=S, font=self.VARIABLE_FONT, 
            fill=self.VARIABLE_COLOR)
        
        # No structures yet
        self.TRstackTopIndex = None
        self.TRqueueRearIndex = None
        self.TRqueueFrontIndex = None
        self.EVstackTopIndex = None
        self.postfixInputString = None

    def createTranslateStructues(self):
        colors = [[dValue and dValue.val and dValue.color(self.canvas) 
                   for dValue in struct]
                  for struct in self.structures]
            
        # Create array structured for PostfixTranslate
        for array in (0, 1):  # Draw cells for translation stack and queue
            tag = 'array-{}'.format(array)
            for i in range(self.ARRAY_SIZE):
                self.createArrayCell(i, array, tags=tag)

            for i, value in enumerate(self.structures[array]):
                if value.val is not None:
                    value.items = self.createCellValue(
                        i, value.val, array, color=colors[array][i])

        # Create index pointers for translation stack and queue
        self.TRstackTopIndex = self.createIndex(
            len(self.TRstack), array=0, name='top', tags='index-0')
        self.indices[0] = self.TRstackTopIndex
        self.TRqueueRearIndex = self.createIndex(
            self.TRqueueRear, array=1, name='rear', tags='index-1')
        self.TRqueueFrontIndex = self.createIndex(
            self.TRqueueFront, array=1, name='front', level=1, tags='index-1')
        self.indices[1] = (self.TRqueueRearIndex, self.TRqueueFrontIndex)

        inBoxCoords = self.inputBoxCoords()
        self.postfixLabel = self.canvas.create_text(
            inBoxCoords[0] - 10, inBoxCoords[3] + self.INPUT_BOX_HEIGHT,
            text='Postfix', anchor=E, font=self.VARIABLE_FONT,
            fill=self.VARIABLE_COLOR)
        self.postfixInputString = self.canvas.create_text(
            inBoxCoords[0] + 10, inBoxCoords[3] + self.INPUT_BOX_HEIGHT,
            text='', anchor=W, font=self.VALUE_FONT, fill=self.VALUE_COLOR)

    def createEvaluateStructues(self, postfix, callEnviron=None):
        colors = [[dValue.color(self.canvas) for dValue in struct]
                  for struct in self.structures]
            
        # Create array structured for Evaluate
        array = 2
        tag = 'array-2'
        for i in range(self.ARRAY_SIZE):
            cell = self.createArrayCell(i, array, tags=tag)
            if callEnviron:
                callEnviron.add(cell)

        for i, value in enumerate(self.structures[array]):
            if value.val is not None:
                value.items = self.createCellValue(
                    i, value.val, array, color=colors[array][i])
                if callEnviron:
                    callEnviron |= set(value.items)

        # Create index pointers for translation stack and queue
        tag = 'index-2'
        self.EVstackTopIndex = self.createIndex(
            len(self.EVstack), array=2, name='top', tags=tag)
        self.indices[2] = self.EVstackTopIndex
        if callEnviron:
            callEnviron |= set(self.EVstackTopIndex)

        self.canvas.itemconfigure(self.postfixInputString, text=postfix)
        
    def makeButtons(self):
        vcmd = (self.window.register(lambda P: self.updateInput(P)), '%P')

        evalButton = self.addOperation(
            "Evaluate", lambda: self.clickEvaluate(), numArguments=1,
            argHelpText=['infix expression'], validationCmd=vcmd,
            helpText='Evaluate infix expression')

        self.addAnimationButtons()
        return [evalButton]

    def validExpression(self, text):
        return all(c.isdigit() or c.isspace() or c in self.allOperators
                   for c in text)
    
    def updateInput(self, newText):
        valid = (self.validExpression(newText) and
                 len(newText) < self.MAX_EXPRESSION_LENGTH)
        if self.animationsStopped() and valid:
            if self.postfixInputString:
                self.display(newText)
            else:
                self.canvas.itemconfigure(self.infixInputString, text=newText)
        return valid

    # Button functions
    def clickEvaluate(self):
        try:
            result = self.PostfixEvaluate(self.getArgument())
            self.setMessage('Expression evaluates to {}'.format(result))
        except UserStop:
            self.setMessage('Evaluation stopped prematurely')
        except IndexError as e:
            self.setMessage('Error! {}'.format(e))
            self.setArgumentHighlight(color=self.ERROR_HIGHLIGHT)
            raise e   # For debugging only

    def PostfixEvaluate(self, infixExpression):
        callEnviron = self.createCallEnvironment()
        self.startAnimations()

        postfixExpression = self.PostfixTranslate(infixExpression)

        # Restore infix expression that was parsed
        self.canvas.itemconfigure(self.infixInputString, text=infixExpression)
        
        del self.EVstack[:]
        for array in (0, 1):         # Gray out arrays used by Translate
            self.canvas.itemconfigure(
                'array-{}'.format(array), outline='gray80')
            self.canvas.itemconfigure('index-{}'.format(array), fill='gray80')
        self.createEvaluateStructues(postfixExpression, callEnviron=callEnviron)

        left, operator, right = [
            self.canvas.create_text(
                *coords, text='', font=self.VALUE_FONT, fill=self.VALUE_COLOR)
            for coords in self.operandAndOperatorCoords()]
        operatorCoords = self.canvas.coords(operator)
        
        token, postfixExpression = self.nextToken(self.postfixInputString)
        tokenItem = self.extractToken(token, self.postfixInputString,
                                      callEnviron)
        
        while token:
            prec = self.precedence(token)
            if prec:
                self.moveItemsTo(tokenItem, operatorCoords, sleepTime=0.01)
                self.canvas.itemconfigure(operator, text=token)
                self.canvas.delete(tokenItem)
                rightDValue = self.popToken(callEnviron, array=2,
                                            displayString=right)
                leftDValue = self.popToken(callEnviron, array=2,
                                           displayString=left)
                self.moveItemsTo(
                    (left, right), (operatorCoords, operatorCoords), 
                    sleepTime=0.01)
                op = token
                L, R = eval(leftDValue.val), eval(rightDValue.val)
                result = str(
                    L|R if op == '|' else L&R if op == '&' else
                    L+R if op == '+' else L-R if op == '-' else
                    L*R if op == '*' else L/R if op == '/' else
                    L%R if op == '%' else L^R if op == '^' else None)
                tokenItem = self.canvas.create_text(
                    *operatorCoords, text=result, font=self.VALUE_FONT,
                    fill=self.VALUE_COLOR)
                for displayString, coords in zip(
                        (left, operator, right),
                        self.operandAndOperatorCoords()):
                    self.canvas.itemconfigure(displayString, text='')
                    self.canvas.coords(displayString, *coords)
            self.pushToken(tokenItem, callEnviron, array=2)
                          
            token, postfixExpression = self.nextToken(self.postfixInputString)
            tokenItem = self.extractToken(token, self.postfixInputString,
                                          callEnviron)

        outputBox = self.outputBoxCoords()
        self.canvas.itemconfigure(operator, text='')
        self.canvas.coords(
            operator, 
            *divide_vector(add_vector(outputBox[:2], outputBox[2:]), 2))
        dValue = self.popToken(callEnviron, array=2, displayString=operator)
        
        self.cleanUp(callEnviron)
        return dValue.val

    def PostfixTranslate(self, infixExpression):
        del self.TRstack[:]
        self.TRqueue = [drawnValue(None) for i in self.TRqueue]
        self.TRqueueRear = 0
        self.TRqueueFront = 1
        self.TRqueueSize = 0
        self.display(inputString=infixExpression)
        self.createTranslateStructues()

        callEnviron = self.createCallEnvironment()
        self.startAnimations()

        token, infixExpression = self.nextToken(self.infixInputString)
        tokenItem = self.extractToken(token, self.infixInputString,
                                      callEnviron)
        
        while token:
            prec = self.precedence(token)
            delim = self.delimiter(token)
            if delim:
                if token == '(':
                    self.pushToken(tokenItem, callEnviron, array=0,
                                   color=drawnValue.palette[prec - 1])
                else:
                    self.canvas.delete(tokenItem)
                    while self.TRstack:
                        top = self.popToken(callEnviron, array=0)
                        if top.val == '(':
                            for item in top.items:
                                self.canvas.delete(item)
                            break
                        else:
                            self.insertToken(top, callEnviron)
            elif prec:                # Input token is an operator
                while self.TRstack:
                    top = self.popToken(callEnviron, array=0)
                    if top.val == '(':
                        # Just put drawnValue back in place
                        self.pushToken(top, callEnviron, array=0)
                        break
                    else:
                        if self.precedence(top.val) >= prec:
                            self.insertToken(top, callEnviron)
                        else:
                            self.pushToken(top, callEnviron, array=0)
                            break
                self.pushToken(tokenItem, callEnviron,
                               array=0, color=drawnValue.palette[prec - 1])
            else:                     # Input token is an operand
                self.insertToken(tokenItem, callEnviron, self.infixInputString)

            token, infixExpression = self.nextToken(self.infixInputString)
            tokenItem = self.extractToken(token, self.infixInputString,
                                          callEnviron)

        while self.TRstack:
            self.insertToken(self.popToken(callEnviron, array=0), callEnviron)

        ans = ""
        while self.TRqueueSize > 0:
            if len(ans) > 0:
                ans += " "
            ans += self.removeToken(callEnviron, self.postfixInputString)
                
        self.cleanUp(callEnviron)
        return ans
    
    def nextToken(self, displayString, waitForStrip=0.1):
        text = self.canvas.itemconfigure(displayString, 'text')[-1]
        token = ''
        stripped = text.strip()
        if stripped != text:
            self.canvas.itemconfigure(displayString, text=stripped)
            text = stripped
            if waitForStrip:
                self.wait(waitForStrip)
        if len(text) > 0:
            if self.precedence(text[0]):
                token = text[0]
                text = text[1:]
            else:
                while len(text) > 0 and not (   # to next operator or space
                        self.precedence(text[0]) or text[0].isspace()):
                    token += text[0]
                    text = text[1:]
        return token, text  # Return the token, and remaining input string

    def extractToken(self, token, displayString, callEnviron, anchor=None,
                     font=None, color=None):
        '''Get a canvas text item to repesent a token extracted from the
        beginning of a displayed string'''
        text = self.canvas.itemconfigure(displayString, 'text')[-1]
        if not text.startswith(token):
            raise ValueError('Token does not match beginning of string')
        coords = self.canvas.coords(displayString)
        if font is None:
            font = self.VALUE_FONT
        if color is None:
            color = self.VALUE_COLOR
        tokenItem = self.canvas.create_text(
            *coords, text=token, font=font, fill=color, anchor=W)
        callEnviron.add(tokenItem)
        self.moveItemsBy(tokenItem, (0, self.INPUT_BOX_HEIGHT), sleepTime=0.01)
        self.canvas.itemconfigure(tokenItem, anchor=anchor)
        self.canvas.itemconfigure(displayString, text=text[len(token):])
        return tokenItem
        
    def pushToken(self, token, callEnviron, array=0, color=None):
        '''Push a token on a stack.  The token can either be canvas text
        item or a drawnValue.'''
        index = len(self.structures[array])
        if index >= self.ARRAY_SIZE:
            raise IndexError('Stack overflow')
        toCoords = self.cellCoords(index, array)
        toCenter = self.cellCenter(index, array)
        if isinstance(token, int):
            self.moveItemsTo(token, toCenter, sleepTime=0.01)
            text = self.canvas.itemconfigure(token, 'text')[-1]
            dValue = drawnValue(
                text, *self.createCellValue(index, text, array, color=color))
            self.canvas.delete(token)
            callEnviron.discard(token)
        else:
            if vector_length2(subtract_vector(
                    toCoords, self.canvas.coords(token.items[0]))) > 0.1:
                self.moveItemsTo(token.items, (toCoords, toCenter),
                                 sleepTime=0.01)
            dValue = token
        self.structures[array].append(dValue)
        self.moveItemsBy(
            self.indices[array], (0, - self.CELL_HEIGHT), sleepTime=0.01)

    def popToken(self, callEnviron, array=0, displayString=0):
        '''Pop a drawnValue record from an array structure and optionally
        move a copy of its value text to a displayString'''
        index = len(self.structures[array]) - 1
        if index < 0:
            raise IndexError('Stack underflow')
        top = self.structures[array].pop()
        if displayString:
            text = self.canvas.itemconfigure(displayString, 'text')[-1]
            if len(text) > 0 and not text.endswith(' '):
                text += ' '
            copyItem = self.copyCanvasItem(top.items[1])
            callEnviron.add(copyItem)
            for item in top.items:
                self.canvas.delete(item)
            toCoords = add_vector(
                self.canvas.coords(displayString),
                (self.textWidth(self.VALUE_FONT, text + top.val) // 2, 0))
            self.moveItemsTo(copyItem, toCoords, sleepTime=0.01)
            self.canvas.itemconfigure(displayString, text=text + top.val)
            self.canvas.delete(copyItem)
        self.moveItemsBy(
            self.indices[array], (0, self.CELL_HEIGHT), sleepTime=0.01)
        return top
    
    def insertToken(self, token, callEnviron, displayString=None, color=None):
        '''Insert a token at the rear of the queue.  Token can either be a
        drawnValue on a stack, or a canvas text item ID (int)'''
        if self.TRqueueSize >= self.ARRAY_SIZE:
            raise IndexError('Queue overflow')
        index = (self.TRqueueRear + 1) % len(self.TRqueue)
        indexCoords = self.indexCoords(index, array=1, level=0)
        self.moveItemsTo(self.TRqueueRearIndex, (indexCoords, indexCoords[:2]),
                         sleepTime=0.01)
        toCoords = self.cellCoords(index, array=1)
        toCenter = self.cellCenter(index, array=1)
        if isinstance(token, int) and displayString:
            items = (token,)
            dValue = None
        elif isinstance(token, drawnValue) and displayString is None:
            items = token.items
            dValue = token
        self.moveItemsTo(
            items, (toCoords, toCenter) if len(items) == 2 else (toCenter),
            sleepTime=0.01)
        if dValue is None:
            text = self.canvas.itemconfigure(token, 'text')[-1]
            dValue = drawnValue(
                text, 
                *self.createCellValue(index, text, array=1, color=color))
            for item in items:
                self.canvas.delete(item)
                callEnviron.discard(item)
        self.TRqueue[index] = dValue
        self.TRqueueRear = index
        self.TRqueueSize += 1

    def removeToken(self, callEnviron, displayString=None):
        if self.TRqueueSize <= 0:
            raise IndexError('Queue underflow')
        dValue = self.TRqueue[self.TRqueueFront]
        removed = dValue.val
        index = (self.TRqueueFront + 1) % len(self.TRqueue)
        if displayString:
            text = self.canvas.itemconfigure(displayString, 'text')[-1]
            if len(text) > 0 and not text.endswith(' '):
                text += ' '
            copyItem = self.copyCanvasItem(dValue.items[1])
            callEnviron.add(copyItem)
            self.canvas.itemconfigure(copyItem, anchor=W)
            toCoords = add_vector(
                self.canvas.coords(displayString),
                (self.textWidth(self.VALUE_FONT, text), 0))
            self.moveItemsTo(copyItem, toCoords, sleepTime=0.01)
            self.canvas.itemconfigure(displayString, text=text + removed)
            self.canvas.delete(copyItem)
        self.TRqueueFront = index
        self.TRqueueSize -= 1
        indexCoords = self.indexCoords(self.TRqueueFront, array=1, level=1)
        self.moveItemsTo(self.TRqueueFrontIndex, (indexCoords, indexCoords[:2]),
                         sleepTime=0.01)
        for item in dValue.items:
            self.canvas.delete(item)
        dValue.val, dValue.items = None, ()
        
        return removed
    
    def precedence(self, operator):    # Get the precedence of an operator
        for p, ops in enumerate(self.operators):  # Loop through operators
            if operator in ops:              # If found,
                return p + 1                 # return precedence (low = 1)
        # else not an operator, return None
        
    def delimiter(self, character):  # Determine if character is delimiter
        return self.precedence(character) == len(self.operators)

if __name__ == '__main__':
    # random.seed(3.14159)    # Use fixed seed for testing consistency
    app = InfixCalculator()
    app.runVisualization()

