import random
import time
from tkinter import *
try:
    from drawable import *
    from VisualizationApp import *
except ModuleNotFoundError:
    from .drawable import *
    from .VisualizationApp import *

CELL_SIZE = 50
CELL_BORDER = 2
ARRAY_X0 = 100
ARRAY_Y0 = 100
FONT_SIZE = '20'
VALUE_FONT = ('Helvetica', FONT_SIZE)
VALUE_COLOR = 'black'
FOUND_FONT = ('Helvetica', FONT_SIZE)
FOUND_COLOR = 'green2'

def add_vector(v1, v2):
    return tuple(map(lambda x, y: x + y, v1, v2))

class Array(VisualizationApp):
    nextColor = 0

    def __init__(self, size=10, **kwargs):
        super().__init__(**kwargs)
        self.list = []
        self.size = size
        self.foundCellValue = None
        self.indexArrow = None
        self.buttons = self.makeButtons()
        
        for i in range(9):
            self.insert(random.randrange(90))
        self.display()

    def __str__(self):
        return str(self.list)

    # ARRAY FUNCTIONALITY
    def isSorted(self):
        for i in range(1, len(self.list)):
            if self.list[i] < self.list[i-1]:
                return False
        return True

    def get(self, index):
        try:
            return self.list[index].val
        except:
            print("Invalid list index")
            return -1

    def set(self, index, val):
        # reset the value of the Drawable at that index to val
        self.list[index].val = val

        # get the position of the displayed value
        pos = self.canvas.coords(self.list[index].display_val)

        # delete the displayed value and replace it with the updated value
        self.canvas.delete(self.list[index].display_val)
        self.list[index].display_val = self.canvas.create_text(
            pos[0], pos[1], text=str(val), font=VALUE_FONT, fill=VALUE_COLOR)

        # update window
        self.window.update()

    def createIndexArrow(self, index):  # Create an arrow to point at an array
        cell_coords = self.cellCoords(index) # cell at the given index
        cell_center = self.cellCenter(index)
        x = cell_center[0]
        y0 = cell_coords[1] - CELL_SIZE * 4 // 5
        y1 = cell_coords[1] - CELL_SIZE * 3 // 10
        self.indexArrow = self.canvas.create_line(
            x, y0, x, y1, arrow="last", fill='red')
        
    def insert(self, val):
        self.clearPastOperations()
        self.createIndexArrow(len(self.list))

        # create new cell and cell value display objects
        cell = self.canvas.create_rectangle(
            *self.cellCoords(len(self.list)), 
            fill=drawable.palette[Array.nextColor], outline='')
        cell_val = self.canvas.create_text(
            *self.cellCenter(len(self.list)), text=val,
            font=VALUE_FONT, fill=VALUE_COLOR)

        # add a new Drawable to the list with the new value, color, and display objects
        self.list.append(drawable(val, drawable.palette[Array.nextColor], 
                                  cell, cell_val))

        # increment nextColor
        Array.nextColor = (Array.nextColor + 1) % len(drawable.palette)

        # update window
        self.window.update()

    def removeFromEnd(self):
        self.clearPastOperations()
        # pop a Drawable from the list
        if len(self.list) == 0:
            self.setMessage('Array is empty!')
            return
        n = self.list.pop()

        # delete the associated display objects
        self.canvas.delete(n.display_shape)
        self.canvas.delete(n.display_val)

        # update window
        self.window.update()

    def assignElement(self, fromIndex, toIndex):

        # get position of "to" cell
        posToCell = self.canvas.coords(self.list[toIndex].display_shape)

        # get position of "from" cell and value
        posFromCell = self.canvas.coords(self.list[fromIndex].display_shape)
        posFromCellVal = self.canvas.coords(self.list[fromIndex].display_val)

        # create new display objects that are copies of the "from" cell and value
        newCellShape = self.canvas.create_rectangle(
            *posFromCell, fill=self.list[fromIndex].color, outline='')
        newCellVal = self.canvas.create_text(
            *posFromCellVal, text=self.list[fromIndex].val,
            font=VALUE_FONT, fill=VALUE_COLOR)

        # set xspeed to move in the correct direction
        xspeed = 1
        if fromIndex > toIndex:
            xspeed = -xspeed
        distance = abs(int(posToCell[0] - posFromCell[0]))

        # move the new display objects until they are in the position of the "to" cell
        for i in range(distance):
            self.canvas.move(newCellShape, xspeed, 0)
            self.canvas.move(newCellVal, xspeed, 0)
            self.window.update()
            time.sleep(self.speed(0.01))

        # delete the original "to" display value and the new display shape
        self.canvas.delete(self.list[toIndex].display_val)
        self.canvas.delete(self.list[toIndex].display_shape)

        # update value and display value in "to" position in the list
        self.list[toIndex].display_val = newCellVal
        self.list[toIndex].val = self.list[fromIndex].val
        self.list[toIndex].display_shape = newCellShape
        self.list[toIndex].color = self.list[fromIndex].color

        # update the window
        self.window.update()

    def cellCoords(self, cell_index): # Get bounding rectangle for array cell
        return (ARRAY_X0 + CELL_SIZE * cell_index, ARRAY_Y0, # at index
                ARRAY_X0 + CELL_SIZE * (cell_index + 1) - CELL_BORDER,
                ARRAY_Y0 + CELL_SIZE - CELL_BORDER)

    def cellCenter(self, cell_index): # Center point for array cell at index
        half_cell = (CELL_SIZE - CELL_BORDER) // 2
        return add_vector(self.cellCoords(cell_index), (half_cell, half_cell))

    def display(self):
        self.canvas.delete("all")

        # print(self.size)
        for i in range(self.size):  # Draw grid of cells
            cell_coords = self.cellCoords(i)
            half_border = CELL_BORDER // 2
            self.canvas.create_rectangle(
                *add_vector(cell_coords, 
                            (-half_border, -half_border,
                             CELL_BORDER - half_border,
                             CELL_BORDER - half_border)),
                fill='white', outline='black', width=CELL_BORDER)

        # go through each Drawable in the list
        for i, n in enumerate(self.list):
            # print(n)
            # create display objects for the associated Drawables
            cell = self.canvas.create_rectangle(
                *self.cellCoords(i), fill=n.color, outline='', width=0)
            cell_val = self.canvas.create_text(
                *self.cellCenter(i), text=n.val, font=VALUE_FONT,
                fill=VALUE_COLOR)

            # save the display objects in the Drawable object fields
            n.display_shape = cell
            n.display_val = cell_val

        self.window.update()

    def clearPastOperations(self):  # Remove highlighting from past operations
        for item in (self.indexArrow, self.foundCellValue):
            self.canvas.delete(item)
        self.setMessage()
        
    def find(self, val):
        global running
        running = True
        self.clearPastOperations()

        # draw an arrow over the first cell
        self.createIndexArrow(0)

        # go through each Drawable in the list
        for i in range(len(self.list)):
            self.window.update()

            n = self.list[i]

            # if the value is found
            if n.val == val:
                # get the position of the displayed cell and val
                posVal = self.canvas.coords(n.display_val)

                # cover the current display value with the updated value in green
                #cell_shape = canvas.create_rectangle(
                #  posCell[0], posCell[1], posCell[2], posCell[3], fill=n[1])
                self.foundCellValue = self.canvas.create_text(
                    *posVal, text=str(val), font=FOUND_FONT, fill=FOUND_COLOR)

                # update the display
                self.window.update()

                return i

            # if the value hasn't been found, wait 1 second, and then move the arrow over one cell
            time.sleep(self.speed(1))
            self.canvas.move(self.indexArrow, CELL_SIZE, 0)

            if not running:
                break

        return None

    def remove(self, val):
        index = self.find(val)
        if index != None:
            time.sleep(1)
            self.clearPastOperations()

            n = self.list[index]

            # Slide value rectangle up and off screen
            while self.canvas.coords(n.display_shape)[3] > 0:
                self.canvas.move(n.display_shape, 0, -1)
                self.canvas.move(n.display_val, 0, -1)
                self.window.update()
                time.sleep(self.speed(0.01))

            self.window.update()

            # Slide values from right to left to fill gap
            for i in range(index+1, len(self.list)):
                self.assignElement(i, i-1)

            self.removeFromEnd()
            return True
        return False

    def makeButtons(self):
        vcmd = (self.window.register(numericValidate),
                '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
        findButton = self.addOperation(
            "Find", lambda: self.clickFind(), hasArgument=True,
            validationCmd=vcmd)
        insertButton = self.addOperation(
            "Insert", lambda: self.clickInsert(), hasArgument=True,
            validationCmd=vcmd)
        deleteValueButton = self.addOperation(
            "Delete", lambda: self.clickDelete(), hasArgument=True,
            validationCmd=vcmd)
        deleteRightmostButton = self.addOperation(
            "Delete Rightmost", lambda: self.removeFromEnd())
        return [findButton, insertButton, deleteValueButton,
                deleteRightmostButton]

    def validArgument(self):
        entered_text = self.getArgument()
        if entered_text and entered_text.isdigit():
            val = int(entered_text)
            if val < 100:
                return val
        
    # Button functions
    def clickFind(self):
        val = self.validArgument()
        if val is None:
            self.setMessage("Input value must be an integer from 0 to 99.")
        else:
            result = self.find(val)
            if result != None:
                msg = "Found {}!".format(val)
            else:
                msg = "Value {} not found".format(val)
            self.setMessage(msg)
        self.clearArgument()

    def clickInsert(self):
        val = self.validArgument()
        if val is None:
            self.setMessage("Input value must be an integer from 0 to 99.")
        else:
            if len(array.list) >= array.size:
                self.setMessage("Error! Array is already full.")
            else:
                array.insert(val)
        self.clearArgument()

    def clickDelete(self):
        val = self.validArgument()
        if val is None:
            self.setMessage("Input value must be an integer from 0 to 99.")
        else:
            result = array.remove(val)
            if result:
                msg = "Value {} deleted!".format(val)
            else:
                msg = "Value {} not found".format(val)
            self.setMessage(msg)
        self.clearArgument()

# validate text entry
def numericValidate(action, index, value_if_allowed,
             prior_value, text, validation_type, trigger_type, widget_name):
    if text in '0123456789':
        return True
    else:
        return False

if __name__ == '__main__':
    random.seed(3.14159)    # Use fixed seed for testing consistency
    array = Array()

    array.runVisualization()

'''
To Do:
- make it look pretty
- animate insert
'''
