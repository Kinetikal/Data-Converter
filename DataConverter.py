import PySimpleGUI as sg
from pathlib import Path
import pandas as pd
import csv
from lxml import etree
import numpy as np

# OUTPUT FILES xml,csv,json,xlsx,md,html
# INPUT FILES csv,xlsx,xml,son

# Mapping of file extensions to corresponding read and write functions
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

# Remove whitespace from a file
def remove_whitespace_from_file(input_file):
    with open(input_file, 'r') as file:
        content = file.read()
    content_without_whitespace = content.replace(" ", "_")
    with open(input_file, 'w') as file:
        file.write(content_without_whitespace)

# Generic conversion function
def convert_files(input_file, output_file, input_ext, output_ext):
    try:
        read_func, write_func = CONVERSION_FUNCTIONS.get((input_ext, output_ext), (None, None))
        
        if read_func is None or write_func is None:
            window["-OUTPUT_WINDOW-"].update("Unsupported conversion!", text_color="#ff4545")
            return

        # Check and remove whitespace from input file if the output file is XML
        if output_ext.upper() == "XML":
            # If Input file has whitespaces, replace whitespaces with underline
            if ' ' in open(input_file, 'r').read():
                remove_whitespace_from_file(input_file)
                window["-OUTPUT_WINDOW-"].update(f"Successfully converted {Path(input_file).stem} {input_ext.upper()} to {Path(output_file).stem} {output_ext.upper()} (INFO: Input file contained whitespaced, whitespaced have been removed for XML conversion, because it's not supported!)", text_color="#51e98b")
                
        df = read_func(input_file)
        write_func(df, output_file)
        window["-OUTPUT_WINDOW-"].update(f"Successfully converted {Path(input_file).stem} {input_ext.upper()} to {Path(output_file).stem} {output_ext.upper()}", text_color="#51e98b")

        # Check if input file has underlines, if it does re-add whitespaces :)
        if "_" in open(input_file).read():
            with open(input_file, "r") as file_with_underlines:
                content = file_with_underlines.read()
            readd_whitespaces = content.replace("_"," ")
            with open(input_file,"w") as file_with_underlines:
                file_with_underlines.write(readd_whitespaces)
        
    except FileNotFoundError:
        window["-OUTPUT_WINDOW-"].update(f"{input_ext.upper()} File not found!", text_color="#ff4545")
    except Exception as e:
        window["-OUTPUT_WINDOW-"].update(f"ERROR: {e}", text_color="#ff4545")
 
 # Read file data in Pandas DataFrame       
def read_file_data(file):
    try:
        file_suffix_in_input = Path(file).suffix.upper().strip(".")
        df = None
        
        if file_suffix_in_input == "CSV":
            # Use the Sniffer class to automatically detect the delimiter
            with open(file, 'r', newline='') as csv_file:
                sniffer = csv.Sniffer()
                sample_data = csv_file.read(512)  # Read a sample of the file to determine the delimiter
                dialect = sniffer.sniff(sample_data)
                csv_delimiter = dialect.delimiter

                if csv_delimiter == ";":
                    # Read the content with the old delimiter
                    with open(file, 'r', newline='') as csv_file_read:
                        reader = csv.reader(csv_file_read, delimiter=";")
                        rows = list(reader)

                    # Write the content with the new delimiter
                    with open(file, 'w', newline='') as csv_file_write:
                        writer = csv.writer(csv_file_write, delimiter=",")
                        writer.writerows(rows)

                    print("Delimiter successfully changed!")

            # Reopen the file after changing the delimiter
            with open(file, 'r', newline='') as csv_file:
                # Determine the CSV line ending
                line_endings = {"\r\n": "Windows", "\n": "Unix/Linux", "\r": "Old Mac"}
                detected_line_ending = line_endings.get(csv_file.newlines, 'Unknown')

                if detected_line_ending == "Windows":
                    lineterminator = "\r\n"
                elif detected_line_ending == "Unix/Linux":
                    lineterminator = "\n"
                elif detected_line_ending == "Old Mac":
                    lineterminator = "\r"
                else:
                    lineterminator = None

                df = pd.read_csv(csv_file, delimiter=",", lineterminator=lineterminator)
                
        elif file_suffix_in_input == "XML":
            df = pd.read_xml(file)
        elif file_suffix_in_input == "JSON":
            df = pd.read_json(file)
        elif file_suffix_in_input == "XLSX":
            df = pd.read_excel(file)
        elif file_suffix_in_input == "":
            raise ValueError("Error: Input is empty. Cannot read nothing!")
        
        if df is not None:
            column_names = df.columns.tolist()
            window["-COLUMNS-"].update(values=column_names)
            window["-OUTPUT_WINDOW-"].update(df, text_color="white")
            return df, column_names
        else:
            return None, []

    except Exception as e:
        window["-OUTPUT_WINDOW-"].update(f"ERROR: {e}", text_color="#ff4545")
        return None, []

def get_min_mid_max(file):
    try:
        file_suffix = Path(file).suffix.upper().strip(".")
        pg_columns = values["-COLUMNS-"]
        
        if file_suffix == "CSV":
            df = pd.read_csv(file)
            # Ensure that df and pg_columns are not None
            if df is not None and pg_columns != "":
                if event == "-MIN-":
                    min_value = df[pg_columns].min()
                    window["-OUTPUT_WINDOW-"].update(min_value)
                elif event == "-MID-":
                    mid_value = df[pg_columns].mean()
                    window["-OUTPUT_WINDOW-"].update(mid_value)
                elif event == "-MAX-":
                    max_value = df[pg_columns].max()
                    window["-OUTPUT_WINDOW-"].update(max_value)
            else:
                window["-OUTPUT_WINDOW-"].update("ERROR: Press 'Read' and then select a Column!")
    except Exception as e:
        window["-OUTPUT_WINDOW-"].update(f"ERROR: {e}")

            
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

layout_data_properties = [[sg.Text("Columns:"),sg.Combo(values="",key="-COLUMNS-",size=(10, 1)),sg.Button("Min",key="-MIN-"),sg.Button("Mid",key="-MID-"),sg.Button("Max",key="-MAX-")]]

layout_output_and_exit = [[sg.Multiline(size=(62, 12), key="-OUTPUT_WINDOW-")],
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
    input_file = values["-FILE_INPUT-"]
    output_file = values["-FILE_OUTPUT-"]
    input_ext = Path(input_file).suffix.lower().strip(".")
    output_ext = Path(output_file).suffix.lower().strip(".")

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
        window.perform_long_operation(lambda: read_file_data(input_file), "-OUTPUT_WINDOW-")
    if event == "-SAVE-":
        window.perform_long_operation(lambda: convert_files(input_file, output_file, input_ext, output_ext), "-OUTPUT_WINDOW-")
    if event == "-MIN-":
        window.perform_long_operation(lambda: get_min_mid_max(input_file),"-OUTPUT_WINDOW-")
    if event == "-MID-":
        window.perform_long_operation(lambda: get_min_mid_max(input_file),"-OUTPUT_WINDOW-")
    if event == "-MAX-":
        window.perform_long_operation(lambda: get_min_mid_max(input_file),"-OUTPUT_WINDOW-")
    if event == "Clear Output":
        window["-OUTPUT_WINDOW-"].update("")

window.close()  # Kill program