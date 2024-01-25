import PySimpleGUI as sg
from pathlib import Path
import pandas as pd
import csv

# OUTPUT FILES xml,csv,json,xlsx,md,html
# INPUT FILES csv,xlsx,xml,son

# Define a mapping of file extensions to corresponding read and write functions
CONVERSION_FUNCTIONS = {
    # JSON Conversion
    ("json", "html"): (pd.read_json, pd.DataFrame.to_html),
    ("json", "csv"): (pd.read_json, pd.DataFrame.to_csv),
    ("json", "xml"): (pd.read_json, pd.DataFrame.to_xml),
    ("json", "xlsx"): (pd.read_json, pd.DataFrame.to_excel),
    ("json", "md"): (pd.read_json, pd.DataFrame.to_markdown),
    # CSV Conversion
    ("csv", "html"): (pd.read_csv, pd.DataFrame.to_html),
    ("csv", "xml"): (pd.read_csv, pd.DataFrame.to_xml),
    ("csv", "json"): (pd.read_csv, pd.DataFrame.to_json),
    ("csv", "xlsx"): (pd.read_csv, pd.DataFrame.to_excel),
    ("csv", "md"): (pd.read_csv, pd.DataFrame.to_markdown),
    # XML Conversion
    ("xml", "html"): (pd.read_xml, pd.DataFrame.to_html),
    ("xml", "csv"): (pd.read_xml, pd.DataFrame.to_csv),
    ("xml", "json"): (pd.read_xml, pd.DataFrame.to_json),
    ("xml", "xlsx"): (pd.read_xml, pd.DataFrame.to_excel),
    ("xml", "md"): (pd.read_xml, pd.DataFrame.to_markdown),
    # Excel Conversion
    ("xlsx", "html"): (pd.read_excel, pd.DataFrame.to_html),
    ("xlsx", "csv"): (pd.read_excel, pd.DataFrame.to_csv),
    ("xlsx", "json"): (pd.read_excel, pd.DataFrame.to_json),
    ("xlsx", "xml"): (pd.read_excel, pd.DataFrame.to_xml),
    ("xlsx", "md"): (pd.read_excel, pd.DataFrame.to_markdown)
}

# Generic conversion function
def convert_files(input_path, output_path, input_ext, output_ext):
    
    try:
        read_func, write_func = CONVERSION_FUNCTIONS.get((input_ext, output_ext), (None, None))
        
        if read_func is None or write_func is None:
            window["-OUTPUT_WINDOW-"].update(">>> Unsupported conversion!",text_color="#ff4545")
            
        df = read_func(input_path)
        write_func(df, output_path)
        window["-OUTPUT_WINDOW-"].update(f"Successfully converted {Path(input_path).stem} {input_ext.upper()} to {Path(output_path).stem} {output_ext.upper()}",text_color="#51e98b")
        
    except FileNotFoundError:
        window["-OUTPUT_WINDOW-"].update(f">>> {input_ext.upper()} File not found!",text_color="#ff4545")
        
# Function to read input files with Pandas
def read_file_data(file):
    try:
        file_suffix_in_input = Path(file).suffix.upper().strip(".")
        df = None
        
        if file_suffix_in_input == "CSV":
            with open(file, 'r', newline='') as csv_file:
                
                # Use the Sniffer class to automatically detect the delimiter
                sniffer = csv.Sniffer()
                sample_data = csv_file.read(512)  # Read a sample of the file to determine the delimiter
                
                # Determine the CSV Delimiter
                dialect = sniffer.sniff(sample_data)
                separator = dialect.delimiter
                print(f"Seperator: {separator}")
                
                # Determine the CSV line ending
                line_endings = {'\r\n': 'Windows', '\n': 'Unix/Linux', '\r': 'Old Mac'}
                detected_line_ending = line_endings.get(csv_file.newlines, 'Unknown')
                print(f"Detected Line Ending: {detected_line_ending}")
            
        if file_suffix_in_input == "CSV":
            df = pd.read_csv(file, sep=separator, lineterminator="\r", index_col=False)
            window["-OUTPUT_WINDOW-"].update(df,text_color="white")
        elif file_suffix_in_input == "XML":
            df = pd.read_xml(file)
            window["-OUTPUT_WINDOW-"].update(df,text_color="white")
        elif file_suffix_in_input == "JSON":
            df = pd.read_json(file)
            window["-OUTPUT_WINDOW-"].update(df,text_color="white")
        elif file_suffix_in_input == "XLSX":
            df = pd.read_excel(file)
            window["-OUTPUT_WINDOW-"].update(df,text_color="white")
        elif file_suffix_in_input == "":
            window["-OUTPUT_WINDOW-"].update(">>> Error Input is empty, cannot read nothing!",text_color="#ff4545")
        if df is not None:
            column_names = df.columns.tolist()
            window["-COLUMNS-"].update(values=column_names)
            return df, column_names
        else:
            return None, []
        
    except Exception as e:
        window["-OUTPUT_WINDOW-"].update(f"ERROR: {e}",text_color="#ff4545")

# ====== Graphical User Interface settings ====== #

# Add your new theme colors and settings
my_new_theme = {"BACKGROUND": "#191e26",
                "TEXT": "#d2d2d3",
                "INPUT": "#292a2e",
                "TEXT_INPUT": "#d2d2d3",
                "SCROLL": "#292a2e",
                "BUTTON": ("#ff793f", "#313641"),
                "PROGRESS": ("#ff793f", "#4a6ab3"),
                "BORDER": 1,
                "SLIDER_DEPTH": 0,
                "PROGRESS_DEPTH": 0}

sg.theme_add_new("MyTheme", my_new_theme) # Add your dictionary to the PySimpleGUI themes
sg.theme("MyTheme") # Switch your theme to use the newly added one. You can add spaces to make it more readable
font = ("Arial", 16)

# Graphical User Interface layout #
MENU_RIGHT_CLICK = ["", ["Clear Output", "Version", "Exit"]]
FILE_TYPES_INPUT = (("CSV (Comma Seperated Value)", ".csv"), ("XLSX (Excel Sheet)",".xlsx"), ("XML (Extensible Markup Language)", ".xml"), ("JSON (JavaScript Object Notation)", ".json"))
FILE_TYPES_OUTPUT = (("XML (Extensible Markup Language)", ".xml"), ("CSV (Comma Seperated Value)", ".csv"), ("JSON (JavaScript Object Notation)", ".json"), ("XLSX (Excel Sheet)",".xlsx"), ("MD (Markdown README)", ".md"), ("HTML (Hypertext Markup Language)", ".html"))

layout_title = [[sg.Text("Pandas Data Converter", font="Arial 28 bold underline", text_color="#ff793f")],
                [sg.Text("A tool built with Python and the PySimpleGUI module\nfor conversion of common file extensions to other.")],
                [sg.Text()]]

layout_inputs = [[sg.Text("Select an input file for conversion:")],
                             [sg.Text("Input:"), sg.Input(size=(30, 1), key="-FILE_INPUT-"), sg.FileBrowse(file_types=FILE_TYPES_INPUT, size=(7, 1)), sg.Button("Read", size=(7, 1), key="-READ_FILE-")],
                             [sg.Text("Convert input file to a different one:")],
                             [sg.Text("Output:"), sg.Input(size=(29, 1), key="-FILE_OUTPUT-"), sg.FileSaveAs(button_text="Save as", size=(7,1), file_types=FILE_TYPES_OUTPUT, target="-FILE_OUTPUT-", key="-SAVE_AS_BUTTON-"), sg.Button("Convert", key="-SAVE-")],
                             [sg.Text()]]

layout_data_properties = [[sg.Text("Columns:"),sg.Combo(values="",key="-COLUMNS-",size=(10, 1)),sg.Text("To get the Column names, read a file first.")]]

layout_output_and_exit = [[sg.Multiline(size=(54, 12), key="-OUTPUT_WINDOW-")],
                             [sg.Button("Exit", expand_x=True)]]

layout_checkbox = [[sg.Checkbox(text="Show Data Properties",default=False,key="-CHECKBOX_DATA_PROPERTIES-",enable_events=True),sg.Checkbox(text="Show Output Window",default=False,key="-CHECKBOX_SHOW_OUTPUT-",enable_events=True)],
                    [sg.pin(sg.Column(layout_data_properties,key="-DATA_PROPERTIES_FRAME-",visible=False))],
                    [sg.pin(sg.Frame("Output Window",layout_output_and_exit,key="-OUTPUT_WINDOW_FRAME-",visible=False))]]


layout = [[sg.Column(layout_title, justification="center")],
          [sg.Column(layout_inputs)],
          [sg.Column(layout_checkbox)]]
# Graphical User Interface layout END#

window = sg.Window("Data Parser and Converter", layout, font=font, finalize=True, right_click_menu=MENU_RIGHT_CLICK)

# ====== Main Window events and functionality ====== #

while True:
    
    event, values = window.read()
    #window["-OUTPUT_WINDOW-"].update(f"Event: {event}  ||  Values: {values}")
    if event == sg.WIN_CLOSED or event == "Exit":
        break

    # VARIABLES #
    input_path = values["-FILE_INPUT-"]
    output_path = values["-FILE_OUTPUT-"]
    input_ext = Path(input_path).suffix.lower().strip(".")
    output_ext = Path(output_path).suffix.lower().strip(".")

    if event == "-CHECKBOX_DATA_PROPERTIES-":
        if values["-CHECKBOX_DATA_PROPERTIES-"]:
            window["-DATA_PROPERTIES_FRAME-"].update(visible=True)
        else:
            window["-DATA_PROPERTIES_FRAME-"].update(visible=False)
            
    if event == "-CHECKBOX_SHOW_OUTPUT-":
        if values["-CHECKBOX_SHOW_OUTPUT-"]:
            window["-OUTPUT_WINDOW_FRAME-"].update(visible=True)
        else:
            window["-OUTPUT_WINDOW_FRAME-"].update(visible=False)
    
    if event == "-READ_FILE-":
        window.perform_long_operation(lambda: read_file_data(input_path), "-OUTPUT_WINDOW-")
    if event == "-SAVE-":
        window.perform_long_operation(lambda: convert_files(input_path, output_path, input_ext, output_ext), "-OUTPUT_WINDOW-")
    if event == "Clear Output":
        window["-OUTPUT_WINDOW-"].update("")

window.close()  # Kill program