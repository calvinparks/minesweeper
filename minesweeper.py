import itertools
import random


class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        safe_cells = set()
        if self.count == 0:
            safe_cells = self.cells
        return safe_cells
       

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        mine_cells = set()
        if  self.count > 0 and self.count == len(self.cells):
            mine_cells = self.cells
        return mine_cells


    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        if cell in self.cells:                      
            self.cells.discard(cell)
            self.count -= 1

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        if cell in self.cells:       
            self.cells.discard(cell)
            #print("sentence's cell marked as safe")

class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        self.moves_made.add(cell) # add to moves made to ensure the ai will not choose the mine cell
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)






    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """
        
        self.moves_made.add(cell)  # mark the cell as a move that has been made
        self.mark_safe(cell)    # mark the cell as a safe move

        neighboring_cells = set()      
        neighboring_cells  = self.get_neighboring_cells(cell)              # this function will create a list of all cells next to the target cell 
        cell_count = count
        
        if count == 0:
            for tmp_cell in neighboring_cells:
                #print("Marking all neighboring_cells as safe")
                self.mark_safe(tmp_cell)
        elif count == len(neighboring_cells):
            for tmp_cell in neighboring_cells:
               # print("Marking all neighboring_cells as mines")
                self.mark_mine(tmp_cell)
        else:     
            unique_neighboring_cells  = neighboring_cells.difference(self.safes) # removed already determined safe cells

            # Check to see if any cells include already known mines if so remove them and reduce count
            intersection_neighboring_cells  = unique_neighboring_cells.intersection(self.mines)
            if len(intersection_neighboring_cells) > 0 and cell_count > 0: 
                unique_neighboring_cells = unique_neighboring_cells.difference(intersection_neighboring_cells) # removed already determined mine cells
                cell_count = cell_count - len(intersection_neighboring_cells) # reduce the count for already determined mine cells

            #print(f"new knowledge:  {unique_neighboring_cells} = {cell_count}")
            self.knowledge.append(Sentence(unique_neighboring_cells, cell_count))          # Add knowledge




        # Update sentences with count greater than 0 and remove any SAFE cell that it contains
        for tmp_sentence in self.knowledge:
            if tmp_sentence.count > 0:
                for a_safe_cell in self.safes:
                    if a_safe_cell in tmp_sentence.cells:
                        tmp_sentence.cells.remove(a_safe_cell)
        

        # check sentences to see if the number of cell that it contains equal the count of mines that it has if so mark them as mines
        # and update the knowledge sentences
        a_mine_cell_list =[]
        for tmp_sentence in self.knowledge:
            if tmp_sentence.count > 0:
                if len(tmp_sentence.cells) == tmp_sentence.count:
                    for a_mine_cell in tmp_sentence.cells:
                       a_mine_cell_list.append(a_mine_cell)
        for a_mine_cell in a_mine_cell_list:
            self.mark_mine(a_mine_cell)
            self.remove_mine_from_sentences_with_counts_greater_than_1(a_mine_cell)
            print(f"******************************************** NOW Marking A Mine {a_mine_cell} **************************")

        
        # analyze all knowledge for mines and mark them then remove them from knowlege
        for tmp_sentence in self.knowledge:
            if tmp_sentence.count == 1:
                if len(tmp_sentence.cells) == 1:
                       if len(tmp_sentence.known_mines()) > 0: #ensure that there are mines
                            self.mark_mine(tmp_sentence.cells.pop())

        # analyze all knowledge for safes and mark them then remove them from knowlege
        for tmp_sentence in self.knowledge:
            if tmp_sentence.count == 0:
                if len(tmp_sentence.cells) > 0:
                    known_safe_cells = tmp_sentence.known_safes()
                    for safe_cell in known_safe_cells:
                            self.mark_safe(safe_cell.pop())


        # analyze all neighbors of the cell if it has a count greater than zero. 
        # If the number of the of neighbors that are MINES are equal the the COUNT then the remaining neighbors can be considered SAFE and marked              
        if count > 0:
            safe_cells_based_on_the_count = self.check_which_neighbor_cells_are_safe(cell,count)
            if len(safe_cells_based_on_the_count) > 0:
                for safe_cell_based_on_count in safe_cells_based_on_the_count:
                    self.mark_safe(safe_cell_based_on_count)
                    #print(f"marking the cell as safe {safe_cell_based_on_count}")


    def make_safe_move(self):
        """                                                             
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """

        possible_safe_moves = self.safes.copy()
        #print(f"safes    {known_safe_cells}")
        possible_safe_moves.difference_update(self.moves_made)
        if len(possible_safe_moves) < 1:
            return None
        return possible_safe_moves.pop()


    
    def make_random_move(self):
        """                                                               
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        virtual_board_cells = set()
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
                virtual_board_cells.add((i,j))

        virtual_board_cells.difference_update(self.moves_made)

        

        know_mine_cells = []
        for sentence in self.knowledge:
            if sentence.count == len(sentence.cells) and len(sentence.cells) > 0:
                know_mine_cells.append(sentence.cells)

        
        #print(f"random    {know_mine_cells}")
        virtual_board_cells.difference_update(set(know_mine_cells))

        random_move = None
        if len(virtual_board_cells) > 0:
            random_move = virtual_board_cells.pop()

        print(f" the random move is {random_move}")    
        return random_move


    def get_neighboring_cells(self, cell):
        #  Return a set of all the neighbors of a given cell
        self.neighboring_cells = set()
        self.virtual_board_cells = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
                self.virtual_board_cells.append((i,j))

        if (cell[0] - 1, cell[1]) in self.virtual_board_cells:          # cell located upper
            self.neighboring_cells.add((cell[0] - 1, cell[1]))
            #print("Tuple Exists - cell located upper")

        if (cell[0] + 1, cell[1]) in self.virtual_board_cells:        # cell located lower
            self.neighboring_cells.add((cell[0] + 1, cell[1]))
            #print("Tuple Exists - cell located lower")


        if (cell[0], cell[1] - 1) in self.virtual_board_cells:          # cell located left
            self.neighboring_cells.add((cell[0], cell[1] - 1))
            #print("Tuple Exists - cell located left")

        if (cell[0] - 1, cell[1] - 1) in self.virtual_board_cells:        # cell located upper-left-diagnol
            self.neighboring_cells.add((cell[0] - 1, cell[1] - 1))
            #print("Tuple Exists - cell located upper-left-diagnol")

        if (cell[0] + 1, cell[1] - 1) in self.virtual_board_cells:        # cell located lower-left-diagnol
            self.neighboring_cells.add((cell[0] + 1, cell[1] - 1))
            #print("Tuple Exists - cell located lower-left-diagnol ")


        if (cell[0], cell[1] + 1) in self.virtual_board_cells:          # cell located right
            self.neighboring_cells.add((cell[0], cell[1] + 1))
            #print("Tuple Exists - cell located right")

        if (cell[0] - 1, cell[1] + 1) in self.virtual_board_cells:        # cell located upper-right-diagnol
            self.neighboring_cells.add((cell[0] - 1, cell[1] + 1))
            #print("Tuple Exists - cell located upper-right-diagnol")

        if (cell[0] + 1, cell[1] + 1) in self.virtual_board_cells:        # cell located lower-right-diagnol
            self.neighboring_cells.add((cell[0] + 1, cell[1] + 1))
            #print("Tuple Exists - cell located lower-right-diagnol")
        
        return(self.neighboring_cells)


    def check_which_neighbor_cells_are_safe(self, cell, count):
        neighboring_cells_that_are_safe = set()
        neighboring_cells  = self.get_neighboring_cells(cell)              # this function will create a list of all cells next to the target cell
        neighboring_cells_that_are_mines = neighboring_cells.intersection(self.mines)
        if count == len(neighboring_cells_that_are_mines):
          neighboring_cells_that_are_safe = neighboring_cells.difference(neighboring_cells_that_are_mines)

        return neighboring_cells_that_are_safe
   
    
    
    def remove_mine_from_sentences_with_counts_greater_than_1(self, cell):
        for tmp_sentence in self.knowledge:
            if tmp_sentence.count > 1:
                if cell in tmp_sentence.cells:
                    tmp_sentence.cells.remove(cell)
                    tmp_sentence.count -= 1
        return True

