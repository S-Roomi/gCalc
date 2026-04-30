import pandas as pd
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, DataTable, Input, Label, Static
from textual.containers import Grid
from textual.binding import Binding
from textual.screen import ModalScreen
from textual.containers import Horizontal
from textual.theme import Theme
from rich.text import Text

from src.grade import Course

# ---------------------------------------------------------------------------
# Modal Screen — a popup that floats over the app
# ModalScreen[str] means it returns a str when dismissed
# ---------------------------------------------------------------------------
class EditCellModal(ModalScreen[str]):
    """Popup to edit the value of the selected cell."""

    BINDINGS = [("escape", "app.pop_screen", "Cancel")]

    def __init__(self, current_value: str, hint: str | None = None):
        super().__init__()
        self.current_value = current_value
        self.hint = hint

    def compose(self) -> ComposeResult:
        yield Label(f"Current value: {self.current_value}")

        if self.hint:
            yield Input(placeholder=self.hint, id="cell_input")
        else:
            yield Input(placeholder="New value", id="cell_input")

    def on_mount(self) -> None:
        # Auto-focus the input when the modal opens
        self.query_one("#cell_input", Input).focus()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        # dismiss() sends the value back to the caller's callback
        self.dismiss(event.value)

class GradeDisplay(Static):
    def set_grade(self, grade: float | None) -> None:
        if grade is None:
            self.update("Grade: --")
        else:
            self.update(f"Grade: {grade:.1f}%")

# ---------------------------------------------------------------------------
# Main App
# ---------------------------------------------------------------------------
class GCalcApp(App):
    CSS_PATH = "gCalc.tcss"

    # BINDINGS: (key, action_name, description shown in Footer)
    # Textual calls action_<name>() when the key is pressed.
    BINDINGS = [
        Binding("q",    "quit",             "Quit"),
        Binding("a",    "add_row",          "Add Row"),
        Binding("A",    "add_col",          "Add Col"),
        Binding("r",    "remove_row",       "Del Row"),
        Binding("R",    "remove_col",       "Del Col"),
        Binding("e",    "edit_cell",        "Edit Cell"),
        Binding("n",    "rename_column",    "Rename Col"),
        Binding("w",   "change_weight",    "Change Weight"),
    ]
    def compose(self) -> ComposeResult:
        """Build the widget tree. Widgets are yielded top-to-bottom."""
        yield Header()
        yield Grid(DataTable())
        yield Horizontal(Label("", id="status"), GradeDisplay("Grade: --", id="grade"), id="status_bar")
        # one-line status bar above the footer
        yield Footer()                 # auto-renders BINDINGS as hotkey hints

    def on_mount(self) -> None:
        """Runs once after compose(). Good place for first-time setup."""
        self.course = Course()
        self.theme = "dracula"
        self._refresh_table()

    # -----------------------------------------------------------------------
    # Helpers
    # -----------------------------------------------------------------------

    def _refresh_table(self) -> None:
        """Sync the DataTable with the current course state."""
        table = self.query_one(DataTable)
        cursor = table.cursor_coordinate   # save cursor position

        table.clear(columns=True)

        df = self.course.sheet
        
        for i, col in enumerate(df.columns):
            weight = self.course.get_weight(i)
            
            if weight is not None:
                display_weight = weight * 100
                table.add_column(Text(f"{col} {display_weight:g}%", justify="center"), width=16)
            else:
                table.add_column(Text(col, justify="center"), width=16)

        for _, row in df.iterrows():
            table.add_row(*[Text("" if pd.isna(value) else str(value), justify="center") for value in row])
        
        grade = self.course.calculate_grade()
        self.query_one("#grade", GradeDisplay).set_grade(grade)
        # Restore cursor (clamped so it stays in bounds after shrinking)
        r = min(cursor.row, table.row_count - 1)
        c = min(cursor.column, len(df.columns) - 1)
        table.move_cursor(row=r, column=c)

    def _status(self, message: str) -> None:
        self.query_one("#status", Label).update(message)

    # -----------------------------------------------------------------------
    # Event handlers
    # -----------------------------------------------------------------------

    def on_data_table_cell_highlighted(self, event: DataTable.CellHighlighted) -> None:
        """Fires whenever the cursor moves to a new cell."""
        coord = event.coordinate
        value = self.course.sheet.iloc[coord.row, coord.column]
        self._status(f"Row {coord.row + 1}  Col {coord.column + 1}  Value: {value}")

    # -----------------------------------------------------------------------
    # Actions (called by BINDINGS)
    # -----------------------------------------------------------------------

    def action_add_row(self) -> None:
        table = self.query_one(DataTable)
        coord = table.cursor_coordinate.column
        col_name = self.course.sheet.columns[coord]
        self.course.add_row(col_name)
        self._refresh_table()
        self._status(f"Added row {len(self.course.sheet)}")

    def add_to_current_row(self) -> None:
        pass

    def action_add_col(self) -> None:
        self.course.add_col()
        self._refresh_table()
        self._status(f"Added column {len(self.course.sheet.columns)}")

    def action_remove_row(self) -> None:
        res: int = self.course.remove_last_row() 
        if res == -1:
            self._status("No rows to remove")
            return
        self._refresh_table()
        self._status("Removed last row")

    def action_remove_col(self) -> None:
        res: int = self.course.remove_last_col()
        if res == -1:
            self._status("No columns to remove")
            return
        self._refresh_table()
        self._status("Removed last column")

    def action_edit_cell(self) -> None:
        """Push the edit modal; handle the returned value in a callback."""
        table = self.query_one(DataTable)
        coord = table.cursor_coordinate
        current = str(self.course.sheet.iloc[coord.row, coord.column])

        def on_done(new_value: str | None) -> None:
            if new_value is None:
                return  # Escape was pressed
            try:
                parsed = float(new_value)
            except ValueError:
                self._status(f"'{new_value}' is not a valid number")
                return
            self.course.sheet.iloc[coord.row, coord.column] = parsed
            self._refresh_table()
            self._status(f"Set ({coord.row + 1}, {coord.column + 1}) = {parsed}")

        # push_screen shows the modal; on_done is called when it dismisses
        self.push_screen(EditCellModal(current), callback=on_done)

    def action_rename_column(self) -> None:
        table = self.query_one(DataTable)
        column_index = table.cursor_coordinate.column
        current_name = str(self.course.sheet.columns[column_index])

        def on_done(new_name: str | None) -> None:
            if not new_name:
                return
            
            self.course.sheet.rename(columns={self.course.sheet.columns[column_index]: new_name}, inplace=True)
            self._refresh_table()
            self._status(f"Renamed column to '{current_name}'")

        self.push_screen(EditCellModal(current_name), callback=on_done)

    def action_change_weight(self) -> None:
        table = self.query_one(DataTable)
        column = table.cursor_coordinate.column
        current_weight = self.course.get_weight(column)
        
        def on_done(new_weight: str | None) -> None:
            if not new_weight:
                return
            self.course.set_weight(column, float(new_weight))
            self._refresh_table()
            self._status(f"Changed weight to -> {new_weight}")
        
        hint = "if weight is 50%, enter 0.5"
        self.push_screen(EditCellModal(str(current_weight) if current_weight is not None else "None", hint), callback=on_done)

    def on_data_table_header_selected(self, event: DataTable.HeaderSelected) -> None:
        column_index = event.column_index
        current_name = str(self.course.sheet.columns[column_index])
        
        def on_done(new_name: str | None) -> None:
            if not new_name:
                return
            
            self.course.sheet.rename(columns={self.course.sheet.columns[column_index]: new_name}, inplace=True)
            self._refresh_table()
            self._status(f"Renamed column to '{current_name}'")

        self.push_screen(EditCellModal(current_name), callback=on_done)
    


if __name__ == "__main__":
    GCalcApp().run()
