import PySimpleGUI as sg
import logging, numpy, os
from pathlib import Path
import pandas as pd
import xml.etree.ElementTree as ET
from logging.handlers import RotatingFileHandler
from pathlib import Path

# Create a rotating file handler
file_handler = RotatingFileHandler(filename="GUI_Log.log",
                                   maxBytes=25 * 1024 * 1024,  # Max File Size: 25 MB
                                   backupCount=2,  # Number of backup files to keep
                                   encoding="utf-8",  # Specify the encoding if needed
                                   delay=False)  # Set to True if you want to delay file opening
# Define the log format
formatter = logging.Formatter("%(asctime)s %(name)s %(levelname)s %(message)s",
                              datefmt="Date: %d-%m-%Y Time: %H:%M:%S")
# Set the formatter for the file handler
file_handler.setFormatter(formatter)

# Create a logger and add the file handler
logger = logging.getLogger()
logger.addHandler(file_handler)
logger.setLevel(logging.INFO)  # Set the desired log level

# Function to read input files with Pandas 
def read_file_data(file):
    
    file_suffix_in = Path(file).suffix.upper().strip(".")
    
    if file_suffix_in == "CSV":
        file_csv = pd.read_csv(file,index_col=None,engine="python")
        window["-OUTPUT_WINDOW-"].print(file_csv)
        
    elif file_suffix_in == "XML":
        file_xml = pd.read_xml(file)
        window["-OUTPUT_WINDOW-"].print(file_xml)
    
    elif file_suffix_in == "":
        window["-OUTPUT_WINDOW-"].print(">>> Error Input is empty, cannot read nothing!")

#============ CONVERSION FUNCTION START ============#
   
def CSVtoXML(input_path,output_path): # CSV to XML
    
    try:
        if not input_path.lower().endswith(".csv"):
            window["-OUTPUT_WINDOW-"].print(">>> Input: Expected a CSV File")
        if not output_path.lower().endswith(".xml"):
            window["-OUTPUT_WINDOW-"].print(">>> Output: Expected as a XML File")
        df = pd.read_csv(input_path)
        df.to_xml(output_path)
        window["-OUTPUT_WINDOW-"].print(f"Successfully converted {Path(input_path).stem} CSV to {Path(output_path).stem} XML")
        logger.info(f">>> Successfully converted {Path(input_path).stem} CSV to {Path(output_path).stem} XML")
    except FileNotFoundError:
        window["-OUTPUT_WINDOW-"].print(">>> CSV File not found")

def XMLtoCSV(input_path,output_path): # XML to CSV
    
    try:
        if not input_path.lower().endswith(".xml"):
            window["-OUTPUT_WINDOW-"].print(">>> Input: Expected a XML file")
        if not output_path.lower().endswith(".csv"):
            window["-OUTPUT_WINDOW-"].print(">>> Output: Expected as a CSV file")
        df = pd.read_xml(input_path)
        df.to_csv(output_path)
        window["-OUTPUT_WINDOW-"].print(f"Successfully converted {Path(input_path).stem} XML to {Path(output_path).stem} CSV")
        logger.info(f">>> Successfully converted {Path(input_path).stem} XML to {Path(output_path).stem} CSV")
    except FileNotFoundError:
        window["-OUTPUT_WINDOW-"].print(">>> XML File not found")

def CSVtoMarkdown(input_path,output_path): # CSV to Markdown
    
    try:
        if not input_path.lower().endswith(".csv"):
            window["-OUTPUT_WINDOW-"].print(">>> Input: Expected a CSV file")
        if not output_path.lower().endswith(".md"):
            window["-OUTPUT_WINDOW-"].print(">>> Output: Expceted as a Markdown file")
        df = pd.read_csv(input_path)
        df.to_markdown(output_path)
        window["-OUTPUT_WINDOW-"].print(f"Successfully converted {Path(input_path).stem} XML to {Path(output_path).stem} Markdown")
        logger.info(f">>> Successfully converted {Path(input_path).stem} CSV to {Path(output_path).stem} Markdown")
    except FileNotFoundError:
        window["-OUTPUT_WINDOW-"].print(">>> CSV File not found")
        
def XMLtoMarkdown(input_path,output_path): # XML to Markdown
    
    try:
        if not input_path.lower().endswith(".xml"):
            window["-OUTPUT_WINDOW-"].print(">>> Input: Expected a CSV file")
        if not output_path.lower().endswith(".md"):
            window["-OUTPUT_WINDOW-"].print(">>> Output: Expceted as a Markdown file")
        df = pd.read_csv(input_path)
        df.to_markdown(output_path)
        window["-OUTPUT_WINDOW-"].print(f"Successfully converted {Path(input_path).stem} XML to {Path(output_path).stem} Markdown")
        logger.info(f">>> Successfully converted {Path(input_path).stem} XML to {Path(output_path).stem} Markdown")
    except FileNotFoundError:
        window["-OUTPUT_WINDOW-"].print(">>> XML File not found")
        
def JSONtoCSV(input_path,output_path): # XML to CSV
    
    try:
        if not input_path.lower().endswith(".json"):
            window["-OUTPUT_WINDOW-"].print(">>> Input: Expected a JSON file")
        if not output_path.lower().endswith(".csv"):
            window["-OUTPUT_WINDOW-"].print(">>> Output: Expected as a CSV file")
        df = pd.read_json(input_path)
        df.to_csv(output_path)
        window["-OUTPUT_WINDOW-"].print(f"Successfully converted {Path(input_path).stem} JSON to {Path(output_path).stem} CSV")
        logger.info(f">>> Successfully converted {Path(input_path).stem} JSON to {Path(output_path).stem} CSV")
    except FileNotFoundError:
        window["-OUTPUT_WINDOW-"].print(">>> JSON File not found")

def JSONtoXML(input_path,output_path): # XML to CSV
    
    try:
        if not input_path.lower().endswith(".json"):
            window["-OUTPUT_WINDOW-"].print(">>> Input: Expected a JSON file")
        if not output_path.lower().endswith(".xml"):
            window["-OUTPUT_WINDOW-"].print(">>> Output: Expected as a XML file")
        df = pd.read_json(input_path)
        df.to_xml(output_path)
        window["-OUTPUT_WINDOW-"].print(f"Successfully converted {Path(input_path).stem} JSON to {Path(output_path).stem} XML")
        logger.info(f">>> Successfully converted {Path(input_path).stem} JSON to {Path(output_path).stem} XML")
    except FileNotFoundError:
        window["-OUTPUT_WINDOW-"].print(">>> JSON File not found")

def XMLtoJSON(input_path,output_path): # XML to CSV
    
    try:
        if not input_path.lower().endswith(".xml"):
            window["-OUTPUT_WINDOW-"].print(">>> Input: Expected a XML file")
        if not output_path.lower().endswith(".json"):
            window["-OUTPUT_WINDOW-"].print(">>> Output: Expected as a JSON file")
        df = pd.read_xml(input_path)
        df.to_json(output_path)
        window["-OUTPUT_WINDOW-"].print(f"Successfully converted {Path(input_path).stem} XML to {Path(output_path).stem} JSON")
        logger.info(f">>> Successfully converted {Path(input_path).stem} XML to {Path(output_path).stem} JSON")
    except FileNotFoundError:
        window["-OUTPUT_WINDOW-"].print(">>> XML File not found")

def CSVtoJSON(input_path,output_path): # XML to CSV
    
    try:
        if not input_path.lower().endswith(".csv"):
            window["-OUTPUT_WINDOW-"].print(">>> Input: Expected a CSV file")
        if not output_path.lower().endswith(".json"):
            window["-OUTPUT_WINDOW-"].print(">>> Output: Expected as a JSON file")
        df = pd.read_csv(input_path)
        df.to_json(output_path)
        window["-OUTPUT_WINDOW-"].print(f"Successfully converted {Path(input_path).stem} CSV to {Path(output_path).stem} JSON")
        logger.info(f">>> Successfully converted {Path(input_path).stem} CSV to {Path(output_path).stem} JSON")
    except FileNotFoundError:
        window["-OUTPUT_WINDOW-"].print(">>> CSV File not found")
        
#============ CONVERSION FUNCTION END ============#

#============ CONVERSION OF FILES WITH ASSERTION MAIN ============#
def datatype_conversion(input_path,output_path):
    
    file_suffix_in = Path(input_path).suffix.upper().strip(".") # File extension input path
    file_suffix_out = Path(output_path).suffix.upper().strip(".") # File extension output path
    
    try:
        if file_suffix_in == "CSV" and file_suffix_out == "XML":
            CSVtoXML(input_path, output_path)
        elif file_suffix_in == "XML" and file_suffix_out == "CSV":
            XMLtoCSV(input_path, output_path)
        elif file_suffix_in == "XML" and file_suffix_out == "MD":
            XMLtoMarkdown(input_path,output_path)
        elif file_suffix_in == "CSV" and file_suffix_out == "MD":
            CSVtoMarkdown(input_path,output_path)
        elif file_suffix_in == "JSON" and file_suffix_out == "CSV":
            JSONtoCSV(input_path,output_path)
        elif file_suffix_in == "JSON" and file_suffix_out == "XML":
            JSONtoXML(input_path,output_path)
        elif file_suffix_in == "XML" and file_suffix_out == "JSON":
            XMLtoJSON(input_path,output_path)
        elif file_suffix_in == "CSV" and file_suffix_out == "JSON":
            CSVtoJSON(input_path,output_path)
        elif file_suffix_in == "":
            window["-OUTPUT_WINDOW-"].print(">>> File not found, check input file!")
        elif file_suffix_out == "":
            window["-OUTPUT_WINDOW-"].print(">>> Cannot save, output file not set!")
        else:
            window["-OUTPUT_WINDOW-"].print(">>> Unsupported conversion!")
    except FileNotFoundError:
            window["-OUTPUT_WINDOW-"].print(f">>> {file_suffix_in} File not found!")

# Graphical User Interface settings #

# Add your new theme colors and settings
my_new_theme = {"BACKGROUND": "#3d3f46",
                "TEXT": "#d2d2d3",
                "INPUT": "#1c1e23",
                "TEXT_INPUT": "#d2d2d3",
                "SCROLL": "#1c1e23",
                "BUTTON": ("#1d77eb", "#313641"),
                "PROGRESS": ("#1d77eb", "#4a6ab3"),
                "BORDER": 1,
                "SLIDER_DEPTH": 0,
                "PROGRESS_DEPTH": 0}
# Add your dictionary to the PySimpleGUI themes
sg.theme_add_new("MyYellow", my_new_theme)

# Switch your theme to use the newly added one. You can add spaces to make it more readable
sg.theme("MyYellow")
font = ("Consolas", 16)

# Graphical User Interface layout #
MENU_RIGHT_CLICK = ["",["Clear Output", "Version", "Exit"]]
FILE_TYPES_OUTPUT = (("CSV (Comma Seperated Value)", ".csv"),("XML (Extensible Markup Language)",".xml"),("JSON (JavaScript Object Notation)",".json"),("Markdown",".md"),("Configuration-File",".config"))
FILE_TYPES_INPUT = (("CSV (Comma Seperated Value)", ".csv"),("XML (Extensible Markup Language)",".xml"),("JSON (JavaScript Object Notation)",".json"),("Configuration-File",".config"))


layout = [[sg.Text("Data Parser and Converter",font="Consolas 28 bold underline",text_color="#1d77eb")],
          [sg.Text()],
          [sg.Text("Select an input file for conversion:")],
          [sg.Text("Input:"),sg.Input(size=(43,1),key="-FILE_INPUT-"),sg.FileBrowse(file_types=FILE_TYPES_INPUT),sg.Button("Read",key="-READ_FILE-")],
          [sg.Text("Convert the input file to a different one:")],
          [sg.Text("Output:"),sg.Input(size=(39,1),key="-FILE_OUTPUT-"),sg.FileSaveAs(file_types=FILE_TYPES_OUTPUT,target="-FILE_OUTPUT-",key="-SAVE_AS_BUTTON-"),sg.Button("Save",key="-SAVE-")],
          [sg.Multiline(size=(80,15),key="-OUTPUT_WINDOW-")],
          [sg.Button("Exit",expand_x=True)]]

window = sg.Window("Data Parser and Converter",layout,font=font, finalize=True,right_click_menu=MENU_RIGHT_CLICK)

# Main Window events and functionality #
while True:
    event,values = window.read()
    
    if event == sg.WIN_CLOSED or event == "Exit":
        break
    
    # VARIABLES #
    input_path = values["-FILE_INPUT-"]
    output_path = values["-FILE_OUTPUT-"]
    
    if event == "-READ_FILE-":
        window.perform_long_operation(lambda: read_file_data(input_path),"-OUTPUT_WINDOW-")
    if event == "-SAVE-":
        window.perform_long_operation(lambda: datatype_conversion(input_path,output_path),"-OUTPUT_WINDOW-")
    
window.close() # Kill program
