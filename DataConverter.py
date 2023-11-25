import PySimpleGUI as sg
import logging
import os
from pathlib import Path
import pandas as pd
from logging.handlers import RotatingFileHandler
from pathlib import Path


# Define a mapping of file extensions to corresponding read and write functions
CONVERSION_FUNCTIONS = {
    ("csv", "xml"): (pd.read_csv, pd.DataFrame.to_xml),
    ("csv", "html"): (pd.read_csv, pd.DataFrame.to_html),
    ("xml", "html"): (pd.read_xml, pd.DataFrame.to_html),
    ("json", "html"): (pd.read_json, pd.DataFrame.to_html),
    ("xml", "csv"): (pd.read_xml, pd.DataFrame.to_csv),
    ("csv", "md"): (pd.read_csv, pd.DataFrame.to_markdown),
    ("xml", "md"): (pd.read_xml, pd.DataFrame.to_markdown),
    ("csv", "json"): (pd.read_csv, pd.DataFrame.to_json),
    ("xml", "json"): (pd.read_xml, pd.DataFrame.to_json),
    ("json", "csv"): (pd.read_json, pd.DataFrame.to_csv),
    ("json", "xml"): (pd.read_json, pd.DataFrame.to_xml)
}

# Generic conversion function

def convert_files(input_path, output_path, input_ext, output_ext):
    try:
        read_func, write_func = CONVERSION_FUNCTIONS.get(
            (input_ext, output_ext), (None, None))
        if read_func is None or write_func is None:
            window["-OUTPUT_WINDOW-"].print(">>> Unsupported conversion!")
            return

        df = read_func(input_path)
        write_func(df, output_path)
        window["-OUTPUT_WINDOW-"].print(
            f"Successfully converted {Path(input_path).stem} {input_ext.upper()} "
            f"to {Path(output_path).stem} {output_ext.upper()}"
        )
    except FileNotFoundError:
        window["-OUTPUT_WINDOW-"].print(
            f">>> {input_ext.upper()} File not found!")

# Function to read input files with Pandas


def read_file_data(file):

    file_suffix_in = Path(file).suffix.upper().strip(".")
    df = None
    if file_suffix_in == "CSV":
        df = pd.read_csv(file, index_col=None, engine="python")
        window["-OUTPUT_WINDOW-"].print(df)

    elif file_suffix_in == "XML":
        df = pd.read_xml(file)
        window["-OUTPUT_WINDOW-"].print(df)

    elif file_suffix_in == "JSON":
        df = pd.read_json(file)
        window["-OUTPUT_WINDOW-"].print(df)

    elif file_suffix_in == "":
        window["-OUTPUT_WINDOW-"].print(
            ">>> Error Input is empty, cannot read nothing!")

    if df is not None:
        column_names = df.columns.tolist()
        window["-COLUMNS-"].update(values=column_names)
        return df, column_names
    else:
        return None, []


# Graphical User Interface settings #
# Add your new theme colors and settings
my_new_theme = {"BACKGROUND": "#434965",
                "TEXT": "#d2d2d3",
                "INPUT": "#3d3f46",
                "TEXT_INPUT": "#d2d2d3",
                "SCROLL": "#3d3f46",
                "BUTTON": ("#ff793f", "#313641"),
                "PROGRESS": ("#ff793f", "#4a6ab3"),
                "BORDER": 1,
                "SLIDER_DEPTH": 0,
                "PROGRESS_DEPTH": 0}
# Add your dictionary to the PySimpleGUI themes
sg.theme_add_new("MyYellow", my_new_theme)

# Switch your theme to use the newly added one. You can add spaces to make it more readable
sg.theme("MyYellow")
font = ("Arial", 16)

# Graphical User Interface layout #
MENU_RIGHT_CLICK = ["", ["Clear Output", "Version", "Exit"]]
FILE_TYPES_OUTPUT = (("CSV (Comma Seperated Value)", ".csv"), ("XML (Extensible Markup Language)", ".xml"), (
    "JSON (JavaScript Object Notation)", ".json"), ("MD (Markdown README)", ".md"), ("HTML (Hypertext Markup Language)", ".html"))
FILE_TYPES_INPUT = (("CSV (Comma Seperated Value)", ".csv"), (
    "XML (Extensible Markup Language)", ".xml"), ("JSON (JavaScript Object Notation)", ".json"))

layout_title = [[sg.Text("Data Parser and Converter", font="Arial 28 bold underline", text_color="#ff793f")],
                [sg.Text(
                    "A tool built with Python and the PySimpleGUI module\nfor conversion of common file extensions to other.")],
                [sg.Text()]]
layout_inputs_and_buttons = [[sg.Text("Select an input file for conversion:")],
                             [sg.Text("Input:"), sg.Input(size=(30, 1), key="-FILE_INPUT-"), sg.FileBrowse(
                                 file_types=FILE_TYPES_INPUT, size=(7, 1)), sg.Button("Read", size=(7, 1), key="-READ_FILE-")],
                             [sg.Text("Convert the input file to a different one:")],
                             [sg.Text("Output:"), sg.Input(size=(29, 1), key="-FILE_OUTPUT-"), sg.FileSaveAs(button_text="Save as",
                                                                                                             file_types=FILE_TYPES_OUTPUT, target="-FILE_OUTPUT-", key="-SAVE_AS_BUTTON-"), sg.Button("Convert", key="-SAVE-")],
                             [sg.Text("Data Properties:")],
                             [sg.Text("Columns:"), sg.Combo(values="", key="-COLUMNS-", size=(10, 1)),
                              sg.Text("To get the Column names, read a file first.")],
                             [sg.HSeparator()],
                             [sg.Multiline(
                                 size=(52, 10), key="-OUTPUT_WINDOW-")],
                             [sg.Button("Exit", expand_x=True)]]

layout = [[sg.Column(layout_title, justification="center")],
          [sg.Column(layout_inputs_and_buttons)]]

window = sg.Window("Data Parser and Converter", layout,
                   font=font, finalize=True, right_click_menu=MENU_RIGHT_CLICK)

# Main Window events and functionality #
while True:
    event, values = window.read()

    if event == sg.WIN_CLOSED or event == "Exit":
        break

    # VARIABLES #
    input_path = values["-FILE_INPUT-"]
    output_path = values["-FILE_OUTPUT-"]
    input_ext = Path(input_path).suffix.lower().strip(".")
    output_ext = Path(output_path).suffix.lower().strip(".")

    if event == "-READ_FILE-":
        window.perform_long_operation(
            lambda: read_file_data(input_path), "-OUTPUT_WINDOW-")
    elif event == "-SAVE-":
        window.perform_long_operation(lambda: convert_files(
            input_path, output_path, input_ext, output_ext), "-OUTPUT_WINDOW-")
    elif event == "Clear Output":
        window["-OUTPUT_WINDOW-"].update("")

window.close()  # Kill program
