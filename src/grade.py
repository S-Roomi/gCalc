import pandas as pd
from tabulate import tabulate
from .prompts import PROMPTS
def get_user_input(prompt_number: int = 0) -> str:
        """
        Displays a prompt based on prompt_number and returns the user's input.\n
        0: main menu\n
        1: add column\n
        2: add row\n
        3: remove row\n
        4: remove column\n
        5: confirm changes\n
        6: rename column\n
        7: which column to rename\n
        8: enter new column name\n
        """
        prompt = PROMPTS.get(prompt_number, f"Input ({prompt_number}): ")
        return input(prompt).strip().lower()

DEFAULT = ["Homework", "Quizzes", "Exams"]

class Course:
    def __init__(self):
        self.sheet: pd.DataFrame = pd.DataFrame(
            [[0.0 for _ in range(3)] for _ in range(1)], 
            index=[i+1 for i in range(1)], 
            columns=[i for i in DEFAULT]
        )
        self.weights: dict[str:float] = {}

    def add_col(self) -> bool:
        """Prompts the user and appends a new column of zeros to the sheet. Returns True if added."""
        self.sheet[str(len(self.sheet.columns) + 1)] = None
        return True
        
    def add_row(self, column) -> bool:
        """Prompts the user and appends a new row of zeros to the sheet. Returns True if added."""
        nan_rows = self.sheet[self.sheet[column].isna()]
        if not nan_rows.empty:
            self.sheet.at[nan_rows.index[0], column] = float(0)
        else:
            self.sheet.loc[len(self.sheet) + 1] = {column: float(0)}

        return True
    
    def remove_last_col(self) -> int:
        """Removes the last column from the sheet. Returns 1 if removed. -1 if there are 0 columns"""        
        if len(self.sheet.columns) == 0:
            return -1
        
        self.sheet = self.sheet.iloc[:, :-1]
        return 0

    def remove_last_row(self) -> int:
        """Removes the last row from the sheet. Returns 1 if removed. -1 if there are 0 rows"""
        if len(self.sheet) == 0:
            return -1
        
        self.sheet = self.sheet.iloc[:-1]
        return 0
    
    def set_cell(self, row: int, col: int, value) -> bool:
        if row >= 0 or row <= len(self.sheet) and col >= 0 or col <= len(self.sheet.columns):
            self.sheet.at[row, col] = value
            return True
        
        return False

    def set_weight(self, col: int, weight: float) -> bool:
        if col < 0 or col >= len(self.sheet.columns):
            return False
        
        self.weights[self.sheet.columns[col]] = weight
        return True
    
    def get_weight(self, col: int) -> float | None:
        if col < 0 or col >= len(self.sheet.columns):
            return None
        
        return self.weights.get(self.sheet.columns[col])

    def change_column_name(self, col:int, name:str) -> bool:
        if col < 0 or col > len(self.sheet.columns):
            print(f"Column {col} is out of bounds")
            return False
        
        self.sheet.rename(columns={self.sheet.columns.to_list()[col]: name}, inplace=True)
        return True

    # Calculation Function

    def calculate_col(self, col: int, sum: bool = False) -> float | None:
        """Returns the sum or average of a column by index. If sum=True returns the sum, otherwise returns the mean. Returns None if index is out of bounds."""
        if col < 0 or col >= len(self.sheet.columns):

            print(f"Column {col} is out of bounds")
            return None
        
        values = self.sheet.iloc[col].tolist()
        if sum:
            return self.sheet.iloc[col].sum()
        else:
            return self.sheet.iloc[col].mean()

    def weighted_average(self, values: list[float], weights: list[float]) -> float:
        return sum(v * w for v, w in zip(values, weights)) / sum(weights)

    def calculate_row(self, row: int, sum: bool = False) -> float | None:
        """Returns the sum or average of a row by index. If sum=True returns the sum, otherwise returns the mean. Returns None if index is out of bounds."""
        if row < 0 or row >= len(self.sheet):
            print(f"Row {row} is out of bounds")
            return None

        values = self.sheet.iloc[row].tolist()
        if self.weights:
            cols = self.sheet.columns.tolist()
            temp = [self.weights.get(c, 1.0) for c in cols]
            return self.weighted_average(cols, temp)
        
        return self.sheet.iloc[row].sum if sum else self.sheet.iloc[row].mean()


    def calculate_grade(self) -> float | None:
        sum = 0

        if self.weights:
            pass
        else:
            num_of_values = 0
            for col in self.sheet.columns:
                num_of_values += self.sheet[col][self.sheet[col] != 0].count()
            
            sum = self.sheet.sum().sum()

            return round(sum / num_of_values, 2) if sum else 0.0

            
            