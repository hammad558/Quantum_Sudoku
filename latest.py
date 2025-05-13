import pygame
import numpy as np
import random
import sys
from typing import List, Tuple, Dict, Optional, Set

# Initialize pygame
pygame.init()
pygame.font.init()

# Constants
WIDTH, HEIGHT = 900, 700
BOARD_SIZE = 540
CELL_SIZE = BOARD_SIZE // 9
MARGIN = 50
BUTTON_HEIGHT = 50
BUTTON_WIDTH = 180
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
LIGHT_GRAY = (230, 230, 230)
DARK_GRAY = (100, 100, 100)
BLUE = (0, 120, 215)
LIGHT_BLUE = (100, 180, 255)
RED = (255, 50, 50)
GREEN = (50, 200, 50)
PURPLE = (150, 50, 200)
YELLOW = (255, 215, 0)
ORANGE = (255, 150, 50)

# Fonts
TITLE_FONT = pygame.font.SysFont('Arial', 40, bold=True)
BUTTON_FONT = pygame.font.SysFont('Arial', 24)
CELL_FONT = pygame.font.SysFont('Arial', 32, bold=True)
SMALL_FONT = pygame.font.SysFont('Arial', 16)
INFO_FONT = pygame.font.SysFont('Arial', 20)

class QuantumCell:
    def __init__(self, row: int, col: int):
        self.row = row
        self.col = col
        self.value = 0  # 0 means empty
        self.superposition = []  # Possible values when in superposition
        self.collapsed = True    # By default cells are collapsed (not in superposition)
        self.entangled_with = []  # List of cells this cell is entangled with
        self.entanglement_group = None  # Group ID for entangled cells
        self.locked = False      # If True, this is a starting cell that cannot be modified
        
    def set_superposition(self, values: List[int]):
        """Set possible values for this quantum cell"""
        if len(values) == 1:
            self.value = values[0]
            self.collapsed = True
            self.superposition = []
        else:
            self.superposition = values
            self.collapsed = False
            self.value = 0
            
    def collapse(self, value: Optional[int] = None) -> bool:
        """Collapse the superposition to a specific value or randomly"""
        if not self.superposition or self.collapsed:
            return False
            
        if value is None:
            self.value = random.choice(self.superposition)
        else:
            if value in self.superposition:
                self.value = value
            else:
                return False
                
        self.collapsed = True
        self.superposition = []
        return True
        
    def is_quantum(self) -> bool:
        """Check if this cell is in superposition"""
        return len(self.superposition) > 0 and not self.collapsed
        
    def __str__(self):
        if self.collapsed:
            return str(self.value) if self.value != 0 else " "
        elif self.is_quantum():
            return "Q" + ",".join(map(str, sorted(self.superposition)))
        else:
            return " "

class QuantumSudokuGame:
    def __init__(self, difficulty: str = "medium"):
        self.board = [[QuantumCell(r, c) for c in range(9)] for r in range(9)]
        self.difficulty = difficulty
        self.selected_cell = None
        self.player_turn = True
        self.game_over = False
        self.winner = None
        self.message = ""
        self.entanglement_groups = {}
        self.logic_moves_remaining = 10  # Increased to 10 as requested
        self.show_entanglement_lines = False
        self.using_logic_move = False
        self.player_mistakes = 0
        self.ai_mistakes = 0
        self.setup_game()
        
    def setup_game(self):
        """Initialize the game board with a solvable puzzle and quantum cells"""
        self.generate_solved_board()
        self.create_puzzle()
        
        # Create quantum cells based on difficulty
        num_quantum = {"easy": 5, "medium": 10, "hard": 15}[self.difficulty]
        self.create_quantum_cells(num_quantum)
        
    def generate_solved_board(self):
        """Generate a fully solved Sudoku board"""
        # Reset the board
        for row in range(9):
            for col in range(9):
                self.board[row][col].value = 0
                self.board[row][col].collapsed = True
                self.board[row][col].superposition = []
                self.board[row][col].locked = False
                self.board[row][col].entangled_with = []
                self.board[row][col].entanglement_group = None
                
        # Fill the entire board with valid numbers
        self.solve_board()
        
    def solve_board(self) -> bool:
        """Solve the board using backtracking"""
        empty_cell = self.find_empty_cell()
        if not empty_cell:
            return True
            
        row, col = empty_cell
        for num in range(1, 10):
            if self.is_valid_move(row, col, num, check_quantum=False):
                self.board[row][col].value = num
                
                if self.solve_board():
                    return True
                    
                self.board[row][col].value = 0
                
        return False
        
    def find_empty_cell(self) -> Optional[Tuple[int, int]]:
        """Find the next empty cell (returns row, col)"""
        for row in range(9):
            for col in range(9):
                if self.board[row][col].value == 0:
                    return (row, col)
        return None
        
    def create_puzzle(self):
        """Remove numbers to create a puzzle based on difficulty"""
        # Determine cells to remove based on difficulty
        cells_to_remove = {"easy": 40, "medium": 50, "hard": 60}[self.difficulty]
        
        # Get all cell positions and shuffle them
        all_cells = [(r, c) for r in range(9) for c in range(9)]
        random.shuffle(all_cells)
        
        removed = 0
        for row, col in all_cells:
            if removed >= cells_to_remove:
                break
                
            # Store the original value
            original = self.board[row][col].value
            
            # Temporarily remove the number
            self.board[row][col].value = 0
            
            # For hard difficulty, don't check uniqueness (makes it harder)
            if self.difficulty != "hard":
                # Check if the puzzle still has a unique solution
                board_copy = [[self.board[r][c].value for c in range(9)] for r in range(9)]
                solutions = self.count_solutions(board_copy)
                
                if solutions != 1:
                    # Put the number back if removing it creates multiple solutions
                    self.board[row][col].value = original
                    continue
                    
            removed += 1
            
        # Mark remaining cells as locked (starting numbers)
        for row in range(9):
            for col in range(9):
                if self.board[row][col].value != 0:
                    self.board[row][col].locked = True
                    
    def count_solutions(self, board: List[List[int]]) -> int:
        """Count number of solutions (up to 2 for efficiency)"""
        # Find an empty cell
        empty = None
        for row in range(9):
            for col in range(9):
                if board[row][col] == 0:
                    empty = (row, col)
                    break
            if empty:
                break
                
        if not empty:
            return 1
            
        row, col = empty
        count = 0
        
        for num in range(1, 10):
            if self.is_valid_in_board(board, row, col, num):
                board[row][col] = num
                count += self.count_solutions(board)
                board[row][col] = 0
                
                if count > 1:
                    return count
                    
        return count
        
    def is_valid_in_board(self, board: List[List[int]], row: int, col: int, num: int) -> bool:
        """Check if a move is valid in a given board state"""
        # Check row
        if num in board[row]:
            return False
            
        # Check column
        if num in [board[r][col] for r in range(9)]:
            return False
            
        # Check 3x3 box
        box_row, box_col = (row // 3) * 3, (col // 3) * 3
        for r in range(box_row, box_row + 3):
            for c in range(box_col, box_col + 3):
                if board[r][c] == num:
                    return False
                    
        return True
        
    def create_quantum_cells(self, num_quantum: int):
        """Convert some normal cells to quantum cells"""
        candidates = []
        for row in range(9):
            for col in range(9):
                cell = self.board[row][col]
                if not cell.locked and cell.value != 0 and not cell.is_quantum():
                    candidates.append((row, col))
                    
        random.shuffle(candidates)
        quantum_cells = candidates[:num_quantum]
        
        for row, col in quantum_cells:
            cell = self.board[row][col]
            value = cell.value
            
            # Find possible alternatives that would be valid in this position
            alternatives = []
            for num in range(1, 10):
                if num != value and self.is_valid_move(row, col, num, check_quantum=False):
                    alternatives.append(num)
                    
            if alternatives:
                # Choose 1-2 alternatives for easy, 1-3 for medium/hard
                num_alternatives = random.randint(1, 2) if self.difficulty == "easy" else random.randint(1, 3)
                alternatives = random.sample(alternatives, min(num_alternatives, len(alternatives)))
                cell.set_superposition([value] + alternatives)
                
                # 50% chance to create entanglement
                if random.random() < 0.5:
                    self.create_entanglement(row, col)
                    
    def create_entanglement(self, row: int, col: int):
        """Create entanglement for a quantum cell"""
        cell = self.board[row][col]
        
        # Find other quantum cells to entangle with
        candidates = []
        for r in range(9):
            for c in range(9):
                other = self.board[r][c]
                if (r != row or c != col) and other.is_quantum() and not other.entangled_with:
                    candidates.append((r, c))
                    
        if not candidates:
            return
            
        # Choose a random cell to entangle with
        other_row, other_col = random.choice(candidates)
        other_cell = self.board[other_row][other_col]
        
        # Create new entanglement group
        group_id = len(self.entanglement_groups) + 1
        cell.entanglement_group = group_id
        other_cell.entanglement_group = group_id
        
        cell.entangled_with.append((other_row, other_col))
        other_cell.entangled_with.append((row, col))
        
        self.entanglement_groups[group_id] = [(row, col), (other_row, other_col)]
        
    def is_valid_move(self, row: int, col: int, num: int, check_quantum: bool = True) -> bool:
        """Check if placing 'num' at (row, col) is valid with diagonal checks"""
        if self.using_logic_move:
            return True
            
        cell = self.board[row][col]
        
        # Check row
        for c in range(9):
            other = self.board[row][c]
            if c != col and ((other.collapsed and other.value == num) or 
                           (check_quantum and other.is_quantum() and num in other.superposition)):
                return False
                
        # Check column
        for r in range(9):
            other = self.board[r][col]
            if r != row and ((other.collapsed and other.value == num) or 
                           (check_quantum and other.is_quantum() and num in other.superposition)):
                return False
                
        # Check 3x3 box
        box_row, box_col = (row // 3) * 3, (col // 3) * 3
        for r in range(box_row, box_row + 3):
            for c in range(box_col, box_col + 3):
                other = self.board[r][c]
                if (r != row or c != col) and ((other.collapsed and other.value == num) or 
                                             (check_quantum and other.is_quantum() and num in other.superposition)):
                    return False
        
        # New diagonal validation
        if row == col:  # Main diagonal
            for i in range(9):
                other = self.board[i][i]
                if i != row and ((other.collapsed and other.value == num) or 
                               (check_quantum and other.is_quantum() and num in other.superposition)):
                    return False
                    
        if row + col == 8:  # Anti-diagonal
            for i in range(9):
                other = self.board[i][8-i]
                if i != row and ((other.collapsed and other.value == num) or 
                               (check_quantum and other.is_quantum() and num in other.superposition)):
                    return False
                    
        return True
        
    def collapse_quantum_cell(self, row: int, col: int, value: Optional[int] = None) -> bool:
        """Collapse a quantum cell and handle entanglement"""
        cell = self.board[row][col]
        if not cell.is_quantum():
            return False
            
        success = cell.collapse(value)
        if not success:
            return False
            
        # Handle entanglement
        for other_row, other_col in cell.entangled_with:
            other_cell = self.board[other_row][other_col]
            if other_cell.is_quantum():
                if cell.value in other_cell.superposition:
                    other_cell.collapse(cell.value)
                else:
                    other_cell.collapse()
                    
        return True
        
    def make_move(self, row: int, col: int, value: int) -> bool:
        """Make a move on the board"""
        cell = self.board[row][col]
        
        if cell.locked:
            return False
            
        if cell.collapsed:
            if cell.value == 0:
                if self.is_valid_move(row, col, value):
                    cell.value = value
                    return True
                else:
                    self.player_mistakes += 1
            else:
                # 20% chance to convert to quantum cell when placing same number
                if random.random() < 0.2:
                    if self.create_quantum_cell(row, col):
                        return True
            return False
        else:
            return self.collapse_quantum_cell(row, col, value)
            
    def use_logic_move(self, row: int, col: int, value: Optional[int] = None) -> bool:
        """Use a logic move to force a value (can violate Sudoku rules)"""
        if self.logic_moves_remaining <= 0:
            return False
            
        cell = self.board[row][col]
        
        if cell.locked:
            return False
            
        # Set flag to indicate we're using a logic move (skip validation)
        self.using_logic_move = True
        
        if cell.collapsed:
            if cell.value == 0:
                # Place any number (1-9)
                cell.value = value if value is not None else random.randint(1, 9)
            else:
                # Convert to quantum cell with random alternatives
                current_value = cell.value
                alternatives = [num for num in range(1, 10) if num != current_value]
                num_alternatives = random.randint(1, 3)
                alternatives = random.sample(alternatives, min(num_alternatives, len(alternatives)))
                cell.set_superposition([current_value] + alternatives)
                
                # 50% chance to create entanglement
                if random.random() < 0.5:
                    self.create_entanglement(row, col)
        else:
            # Force collapse quantum cell to any value
            if value is not None and value in cell.superposition:
                cell.collapse(value)
            else:
                cell.collapse()
                
        # Reset the flag
        self.using_logic_move = False
        
        # Decrement logic moves counter
        self.logic_moves_remaining -= 1
        return True
        
    def check_game_over(self):
        """Enhanced win/lose/draw conditions with proper winner determination"""
        all_filled = True
        for row in range(9):
            for col in range(9):
                cell = self.board[row][col]
                if cell.collapsed and cell.value == 0:
                    all_filled = False
                    break
                if not cell.collapsed:
                    all_filled = False
                    break
            if not all_filled:
                break
                
        if all_filled:
            self.game_over = True
            player_correct = self.is_board_solved()
            ai_correct = self.check_ai_moves()
            
            if player_correct and not ai_correct:
                self.winner = "Player"
                self.message = "You won! AI made mistakes."
            elif not player_correct and ai_correct:
                self.winner = "AI"
                self.message = "AI won! You made mistakes."
            elif player_correct and ai_correct:
                if self.player_mistakes < self.ai_mistakes:
                    self.winner = "Player"
                    self.message = "You won! Made fewer mistakes than AI."
                elif self.player_mistakes > self.ai_mistakes:
                    self.winner = "AI"
                    self.message = "AI won! Made fewer mistakes than you."
                else:
                    self.winner = "Draw"
                    self.message = "Perfect match! It's a draw."
            else:
                # If both solutions are incorrect, determine winner by mistakes
                if self.player_mistakes < self.ai_mistakes:
                    self.winner = "Player"
                    self.message = "You won! Made fewer mistakes than AI."
                elif self.player_mistakes > self.ai_mistakes:
                    self.winner = "AI"
                    self.message = "AI won! Made fewer mistakes than you."
                else:
                    self.winner = "Draw"
                    self.message = "Both made same number of mistakes. It's a draw."

    def check_ai_moves(self) -> bool:
        """Check if AI made any incorrect moves"""
        for row in range(9):
            for col in range(9):
                cell = self.board[row][col]
                if cell.collapsed and cell.value != 0 and not cell.locked:
                    if not self.is_valid_move(row, col, cell.value, check_quantum=False):
                        self.ai_mistakes += 1
                        return False
        return True

    def is_board_solved(self) -> bool:
        """Check if the board is solved correctly"""
        # Check rows
        for row in range(9):
            values = set()
            for col in range(9):
                if not self.board[row][col].collapsed or self.board[row][col].value == 0:
                    return False
                values.add(self.board[row][col].value)
            if len(values) != 9:
                return False
                
        # Check columns
        for col in range(9):
            values = set()
            for row in range(9):
                values.add(self.board[row][col].value)
            if len(values) != 9:
                return False
                
        # Check 3x3 boxes
        for box_row in range(0, 9, 3):
            for box_col in range(0, 9, 3):
                values = set()
                for i in range(3):
                    for j in range(3):
                        values.add(self.board[box_row + i][box_col + j].value)
                if len(values) != 9:
                    return False
                    
        # Check diagonals
        main_diag = set()
        anti_diag = set()
        for i in range(9):
            main_diag.add(self.board[i][i].value)
            anti_diag.add(self.board[i][8-i].value)
        
        if len(main_diag) != 9 or len(anti_diag) != 9:
            return False
            
        return True
        
    def ai_move(self):
        """Make an AI move"""
        if self.game_over:
            return
            
        # Try to collapse a quantum cell first
        quantum_cells = []
        for row in range(9):
            for col in range(9):
                if self.board[row][col].is_quantum():
                    quantum_cells.append((row, col))
                    
        if quantum_cells:
            row, col = random.choice(quantum_cells)
            cell = self.board[row][col]
            
            # Find valid collapse options
            valid_values = []
            for value in cell.superposition:
                if self.is_valid_move(row, col, value, check_quantum=False):
                    valid_values.append(value)
                    
            if valid_values:
                cell.collapse(random.choice(valid_values))
            else:
                cell.collapse()
                
            # Handle entanglement
            for other_row, other_col in cell.entangled_with:
                other_cell = self.board[other_row][other_col]
                if other_cell.is_quantum():
                    if cell.value in other_cell.superposition:
                        other_cell.collapse(cell.value)
                    else:
                        other_cell.collapse()
        else:
            # Make a normal move if no quantum cells
            empty_cells = []
            for row in range(9):
                for col in range(9):
                    if self.board[row][col].collapsed and self.board[row][col].value == 0:
                        empty_cells.append((row, col))
                        
            if empty_cells:
                row, col = random.choice(empty_cells)
                valid_values = []
                for num in range(1, 10):
                    if self.is_valid_move(row, col, num, check_quantum=False):
                        valid_values.append(num)
                        
                if valid_values:
                    self.board[row][col].value = random.choice(valid_values)
                else:
                    # If no valid moves, use a random number (may violate rules)
                    self.board[row][col].value = random.randint(1, 9)
                    self.ai_mistakes += 1
                    
        self.player_turn = True
        self.check_game_over()

class Button:
    def __init__(self, x: int, y: int, width: int, height: int, text: str, 
                 color: Tuple[int, int, int], hover_color: Tuple[int, int, int], 
                 text_color: Tuple[int, int, int] = WHITE, font: pygame.font.Font = BUTTON_FONT):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.font = font
        self.is_hovered = False
        
    def draw(self, screen: pygame.Surface):
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(screen, color, self.rect, border_radius=8)
        pygame.draw.rect(screen, BLACK, self.rect, 2, border_radius=8)
        
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)
        
    def check_hover(self, pos: Tuple[int, int]):
        self.is_hovered = self.rect.collidepoint(pos)
        return self.is_hovered
        
    def is_clicked(self, pos: Tuple[int, int], event: pygame.event.Event) -> bool:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self.rect.collidepoint(pos)
        return False

class QuantumSudokuUI:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Quantum Sudoku")
        self.clock = pygame.time.Clock()
        self.running = True
        self.game = None
        self.selected_num = None
        self.show_menu = True
        self.difficulty = "medium"
        self.ai_thinking = False
        self.ai_timer = 0
        
        # Menu buttons
        button_y = HEIGHT // 2 - 30
        self.easy_button = Button(WIDTH // 2 - BUTTON_WIDTH // 2, button_y, BUTTON_WIDTH, BUTTON_HEIGHT, 
                                 "Easy", GREEN, LIGHT_BLUE)
        self.medium_button = Button(WIDTH // 2 - BUTTON_WIDTH // 2, button_y + 70, BUTTON_WIDTH, BUTTON_HEIGHT, 
                                   "Medium", BLUE, LIGHT_BLUE)
        self.hard_button = Button(WIDTH // 2 - BUTTON_WIDTH // 2, button_y + 140, BUTTON_WIDTH, BUTTON_HEIGHT, 
                                 "Hard", RED, LIGHT_BLUE)
        self.quit_button = Button(WIDTH // 2 - BUTTON_WIDTH // 2, button_y + 210, BUTTON_WIDTH, BUTTON_HEIGHT, 
                                 "Quit", DARK_GRAY, LIGHT_GRAY)
        
        # Game buttons
        self.new_game_button = Button(WIDTH - BUTTON_WIDTH - 20, 20, BUTTON_WIDTH, BUTTON_HEIGHT, 
                                     "New Game", BLUE, LIGHT_BLUE)
        self.menu_button = Button(WIDTH - BUTTON_WIDTH - 20, 80, BUTTON_WIDTH, BUTTON_HEIGHT, 
                                "Menu", DARK_GRAY, LIGHT_GRAY)
        self.logic_move_button = Button(WIDTH - BUTTON_WIDTH - 20, 140, BUTTON_WIDTH, BUTTON_HEIGHT,
                                      "Logic Moves: 10", PURPLE, LIGHT_BLUE)  # Updated to show 10
        self.toggle_lines_button = Button(WIDTH - BUTTON_WIDTH - 20, 200, BUTTON_WIDTH, BUTTON_HEIGHT,
                                        "Show Lines: Off", ORANGE, LIGHT_BLUE)
        self.give_up_button = Button(WIDTH - BUTTON_WIDTH - 20, 260, BUTTON_WIDTH, BUTTON_HEIGHT,
                                   "Give Up", RED, LIGHT_BLUE)
        
        # Number selection buttons
        self.number_buttons = []
        num_btn_width = 50
        num_btn_start_x = (WIDTH - 9 * num_btn_width) // 2
        for i in range(1, 10):
            x = num_btn_start_x + (i-1) * num_btn_width
            y = HEIGHT - 70
            self.number_buttons.append(Button(x, y, 40, 40, str(i), LIGHT_GRAY, BLUE, BLACK, CELL_FONT))
            
    def run(self):
        """Main game loop"""
        while self.running:
            self.clock.tick(FPS)
            self.handle_events()
            self.update()
            self.draw()
            
        pygame.quit()
        
    def handle_events(self):
        """Handle pygame events"""
        mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                
            if self.show_menu:
                self.easy_button.check_hover(mouse_pos)
                self.medium_button.check_hover(mouse_pos)
                self.hard_button.check_hover(mouse_pos)
                self.quit_button.check_hover(mouse_pos)
                
                if self.easy_button.is_clicked(mouse_pos, event):
                    self.difficulty = "easy"
                    self.start_game()
                elif self.medium_button.is_clicked(mouse_pos, event):
                    self.difficulty = "medium"
                    self.start_game()
                elif self.hard_button.is_clicked(mouse_pos, event):
                    self.difficulty = "hard"
                    self.start_game()
                elif self.quit_button.is_clicked(mouse_pos, event):
                    self.running = False
            else:
                if not self.ai_thinking:
                    self.new_game_button.check_hover(mouse_pos)
                    self.menu_button.check_hover(mouse_pos)
                    self.logic_move_button.check_hover(mouse_pos)
                    self.toggle_lines_button.check_hover(mouse_pos)
                    self.give_up_button.check_hover(mouse_pos)
                    
                    for btn in self.number_buttons:
                        btn.check_hover(mouse_pos)
                        
                    if self.new_game_button.is_clicked(mouse_pos, event):
                        self.start_game()
                    elif self.menu_button.is_clicked(mouse_pos, event):
                        self.show_menu = True
                    elif self.logic_move_button.is_clicked(mouse_pos, event) and self.game.player_turn:
                        self.handle_logic_move()
                    elif self.toggle_lines_button.is_clicked(mouse_pos, event):
                        self.game.show_entanglement_lines = not self.game.show_entanglement_lines
                        self.toggle_lines_button.text = f"Show Lines: {'On' if self.game.show_entanglement_lines else 'Off'}"
                    elif self.give_up_button.is_clicked(mouse_pos, event):
                        self.handle_give_up()
                    elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        self.handle_board_click(mouse_pos)
                        
                    for i, btn in enumerate(self.number_buttons):
                        if btn.is_clicked(mouse_pos, event) and self.game.player_turn:
                            self.selected_num = i + 1
                    
    def start_game(self):
        """Start a new game"""
        self.game = QuantumSudokuGame(self.difficulty)
        self.show_menu = False
        self.selected_num = None
        self.ai_thinking = False
        self.ai_timer = 0
        self.logic_move_button.text = f"Logic Moves: {self.game.logic_moves_remaining}"
        self.toggle_lines_button.text = "Show Lines: Off"
        self.game.show_entanglement_lines = False
            
    def handle_board_click(self, pos: Tuple[int, int]):
        """Handle click on the game board"""
        if not self.game.player_turn or self.game.game_over:
            return
            
        # Calculate board boundaries
        board_x = (WIDTH - BOARD_SIZE) // 2
        board_y = MARGIN
        
        # Check if click is within board
        if (board_x <= pos[0] <= board_x + BOARD_SIZE and 
            board_y <= pos[1] <= board_y + BOARD_SIZE):
            
            # Calculate cell position
            col = (pos[0] - board_x) // CELL_SIZE
            row = (pos[1] - board_y) // CELL_SIZE
            
            if 0 <= row < 9 and 0 <= col < 9:
                # Select the cell
                self.game.selected_cell = (row, col)
                
                # If a number is selected, make a move
                if self.selected_num is not None:
                    cell = self.game.board[row][col]
                    if not cell.locked:
                        if self.game.make_move(row, col, self.selected_num):
                            # Check if the game is over after player's move
                            self.game.check_game_over()
                            
                            if not self.game.game_over:
                                # AI's turn
                                self.ai_thinking = True
                                self.ai_timer = pygame.time.get_ticks()
                    
                    # Reset selected number
                    self.selected_num = None
    
    def handle_logic_move(self):
        """Handle logic move button click"""
        if self.game.selected_cell and self.game.logic_moves_remaining > 0 and self.selected_num is not None:
            row, col = self.game.selected_cell
            if self.game.use_logic_move(row, col, self.selected_num):
                # Update button text
                self.logic_move_button.text = f"Logic Moves: {self.game.logic_moves_remaining}"
                
                # Check if the game is over after player's move
                self.game.check_game_over()
                
                if not self.game.game_over:
                    # AI's turn
                    self.ai_thinking = True
                    self.ai_timer = pygame.time.get_ticks()
    
    def handle_give_up(self):
        """Handle give up button click"""
        self.game.game_over = True
        self.game.winner = "AI"
        self.game.message = "You surrendered! AI wins."
        self.game.check_ai_moves()  # Check AI's solution
        
    def update(self):
        """Update game state"""
        if not self.show_menu and not self.game.game_over:
            # Handle AI turn after a short delay
            if self.ai_thinking and pygame.time.get_ticks() - self.ai_timer > 1000:  # 1 second delay
                self.game.ai_move()
                self.ai_thinking = False
    
    def draw(self):
        """Draw the game screen"""
        self.screen.fill(WHITE)
        
        if self.show_menu:
            self.draw_menu()
        else:
            self.draw_game()
            
        pygame.display.flip()
    
    def draw_menu(self):
        """Draw the main menu"""
        # Draw title
        title_text = TITLE_FONT.render("Quantum Sudoku", True, BLACK)
        title_rect = title_text.get_rect(center=(WIDTH // 2, HEIGHT // 4))
        self.screen.blit(title_text, title_rect)
        
        # Draw description
        desc_text = INFO_FONT.render("A Sudoku variant with quantum mechanics!", True, DARK_GRAY)
        desc_rect = desc_text.get_rect(center=(WIDTH // 2, HEIGHT // 4 + 50))
        self.screen.blit(desc_text, desc_rect)
        
        # Draw buttons
        self.easy_button.draw(self.screen)
        self.medium_button.draw(self.screen)
        self.hard_button.draw(self.screen)
        self.quit_button.draw(self.screen)
    
    def draw_game(self):
        """Draw the game board and UI"""
        board_x = (WIDTH - BOARD_SIZE) // 2
        board_y = MARGIN
        
        # Draw board background
        pygame.draw.rect(self.screen, LIGHT_GRAY, (board_x, board_y, BOARD_SIZE, BOARD_SIZE))
        
        # Draw entanglement lines first (behind cells)
        if self.game.show_entanglement_lines:
            self.draw_entanglement_lines(board_x, board_y)
        
        # Draw cells
        for row in range(9):
            for col in range(9):
                self.draw_cell(row, col, board_x, board_y)
        
        # Draw grid lines
        for i in range(10):
            line_width = 3 if i % 3 == 0 else 1
            # Vertical lines
            pygame.draw.line(self.screen, BLACK, 
                           (board_x + i * CELL_SIZE, board_y), 
                           (board_x + i * CELL_SIZE, board_y + BOARD_SIZE), 
                           line_width)
            # Horizontal lines
            pygame.draw.line(self.screen, BLACK, 
                           (board_x, board_y + i * CELL_SIZE), 
                           (board_x + BOARD_SIZE, board_y + i * CELL_SIZE), 
                           line_width)
        
        # Draw UI elements
        self.new_game_button.draw(self.screen)
        self.menu_button.draw(self.screen)
        self.logic_move_button.draw(self.screen)
        self.toggle_lines_button.draw(self.screen)
        self.give_up_button.draw(self.screen)
        
        # Draw number selection buttons
        for btn in self.number_buttons:
            btn.draw(self.screen)
        
        # Draw selected number indicator
        if self.selected_num is not None:
            btn = self.number_buttons[self.selected_num - 1]
            pygame.draw.rect(self.screen, YELLOW, btn.rect, 3)
        
        # Draw game status
        if self.game.game_over:
            self.draw_game_over_message()
        elif self.ai_thinking:
            status_text = INFO_FONT.render("AI is thinking...", True, DARK_GRAY)
            status_rect = status_text.get_rect(center=(WIDTH // 2, HEIGHT - 120))
            self.screen.blit(status_text, status_rect)
        elif self.game.player_turn:
            status_text = INFO_FONT.render("Your turn", True, DARK_GRAY)
            status_rect = status_text.get_rect(center=(WIDTH // 2, HEIGHT - 120))
            self.screen.blit(status_text, status_rect)
        else:
            status_text = INFO_FONT.render("AI's turn", True, DARK_GRAY)
            status_rect = status_text.get_rect(center=(WIDTH // 2, HEIGHT - 120))
            self.screen.blit(status_text, status_rect)
            
        # Draw game info
        info_text = INFO_FONT.render(f"Difficulty: {self.game.difficulty.capitalize()}", True, BLACK)
        self.screen.blit(info_text, (20, 20))
        
        # Draw help text
        help_text1 = SMALL_FONT.render("Click a cell and then a number to make a move", True, DARK_GRAY)
        help_text2 = SMALL_FONT.render("Use Logic Moves to force quantum effects", True, DARK_GRAY)
        self.screen.blit(help_text1, (20, HEIGHT - 120))
        self.screen.blit(help_text2, (20, HEIGHT - 100))
    
    def draw_cell(self, row: int, col: int, board_x: int, board_y: int):
        """Draw an individual cell"""
        cell = self.game.board[row][col]
        
        x = board_x + col * CELL_SIZE
        y = board_y + row * CELL_SIZE
        
        # Draw cell background
        cell_color = WHITE
        if (row, col) == self.game.selected_cell:
            cell_color = LIGHT_BLUE
        elif cell.is_quantum():
            cell_color = LIGHT_GRAY
            if cell.entanglement_group is not None:
                # Use different colors for different entanglement groups
                entangle_colors = [YELLOW, GREEN, ORANGE, PURPLE, LIGHT_BLUE]
                group_id = cell.entanglement_group % len(entangle_colors)
                cell_color = entangle_colors[group_id]
        elif cell.locked:
            cell_color = LIGHT_GRAY
            
        pygame.draw.rect(self.screen, cell_color, (x+1, y+1, CELL_SIZE-2, CELL_SIZE-2))
        
        # Draw cell content
        if cell.collapsed and cell.value != 0:
            # Normal cell with a value
            text_color = BLACK if not cell.locked else BLUE
            text_surface = CELL_FONT.render(str(cell.value), True, text_color)
            text_rect = text_surface.get_rect(center=(x + CELL_SIZE // 2, y + CELL_SIZE // 2))
            self.screen.blit(text_surface, text_rect)
        elif cell.is_quantum():
            # Quantum cell with superposition
            # Draw a "Q" indicator
            q_text = CELL_FONT.render("Q", True, PURPLE)
            q_rect = q_text.get_rect(center=(x + CELL_SIZE // 2, y + CELL_SIZE // 3))
            self.screen.blit(q_text, q_rect)
            
            # Draw small superposition values
            super_values = cell.superposition
            if super_values:
                values_text = "".join(str(v) for v in sorted(super_values))
                super_text = SMALL_FONT.render(values_text, True, DARK_GRAY)
                super_rect = super_text.get_rect(center=(x + CELL_SIZE // 2, y + CELL_SIZE * 2 // 3))
                self.screen.blit(super_text, super_rect)
    
    def draw_entanglement_lines(self, board_x: int, board_y: int):
        """Draw lines connecting entangled cells"""
        for group_id, cells in self.game.entanglement_groups.items():
            if len(cells) < 2:
                continue
                
            # Select color based on group ID
            entangle_colors = [YELLOW, GREEN, ORANGE, PURPLE, LIGHT_BLUE]
            color = entangle_colors[group_id % len(entangle_colors)]
            
            # Draw lines between all cells in the group
            for i in range(len(cells)):
                row1, col1 = cells[i]
                cell1_center = (
                    board_x + col1 * CELL_SIZE + CELL_SIZE // 2,
                    board_y + row1 * CELL_SIZE + CELL_SIZE // 2
                )
                
                for j in range(i+1, len(cells)):
                    row2, col2 = cells[j]
                    cell2_center = (
                        board_x + col2 * CELL_SIZE + CELL_SIZE // 2,
                        board_y + row2 * CELL_SIZE + CELL_SIZE // 2
                    )
                    
                    pygame.draw.line(self.screen, color, cell1_center, cell2_center, 3)
    
    def draw_game_over_message(self):
        """Enhanced game over message with different colors for outcomes"""
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))
        
        box_rect = pygame.Rect(WIDTH//2 - 250, HEIGHT//2 - 120, 500, 240)
        pygame.draw.rect(self.screen, WHITE, box_rect, border_radius=10)
        
        # Color based on outcome
        if self.game.winner == "Player":
            border_color = GREEN
        elif self.game.winner == "AI":
            border_color = RED
        elif self.game.winner == "Draw":
            border_color = YELLOW
        else:
            border_color = DARK_GRAY
            
        pygame.draw.rect(self.screen, border_color, box_rect, 3, border_radius=10)
        
        title = TITLE_FONT.render("Game Over", True, border_color)
        title_rect = title.get_rect(center=(WIDTH//2, HEIGHT//2 - 70))
        self.screen.blit(title, title_rect)
        
        message = BUTTON_FONT.render(self.game.message, True, BLACK)
        message_rect = message.get_rect(center=(WIDTH//2, HEIGHT//2 - 20))
        self.screen.blit(message, message_rect)
        
        stats = INFO_FONT.render(f"Your mistakes: {self.game.player_mistakes} | AI mistakes: {self.game.ai_mistakes}", 
                               True, DARK_GRAY)
        stats_rect = stats.get_rect(center=(WIDTH//2, HEIGHT//2 + 20))
        self.screen.blit(stats, stats_rect)
        
        continue_button = Button(WIDTH//2 - 80, HEIGHT//2 + 60, 160, 40, "Continue", BLUE, LIGHT_BLUE)
        continue_button.draw(self.screen)
        
        mouse_pos = pygame.mouse.get_pos()
        continue_button.check_hover(mouse_pos)
        
        for event in pygame.event.get(pygame.MOUSEBUTTONDOWN):
            if event.button == 1 and continue_button.rect.collidepoint(mouse_pos):
                self.show_menu = True

if __name__ == "__main__":
    game = QuantumSudokuUI()
    game.run()