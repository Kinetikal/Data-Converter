import PySimpleGUI as sg
import csv, json, logging, configparser
import xml.etree.ElementTree as ET
from logging.handlers import RotatingFileHandler

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

# Function declaration #

def xml_parser(file):
    
    tree = ET.parse(file)
    root = tree.getroot()

    xml_string = ET.tostring(root).decode("UTF-8")
    window["-INPUT_CONSOLE-"].update(xml_string)
    
    document = [elem.tag for elem in root.iter()]
    document_to_set = set(document)
    set_to_list = list(document_to_set)
    # Add Elements to ComboBox List
    window["-ELEMENT_NAME_INPUT-"].update(values=set_to_list)
    window["-DEL_ELEMENT_NAME_INPUT-"].update(values=set_to_list)
    
def xml_add_attribute(file,element_name,attribute_name,attribute_value):
    
    tree = ET.parse(file)
    root = tree.getroot()

   # Add attribute to specified Element
    for element in tree.findall(element_name):
        element.set(attribute_name,attribute_value)
        
        if attribute_name == "id":
            window.refresh()
            window["-ATTRIBUTE_VALUE_INPUT-"].update(1)
            id = 1
            for element in tree.findall(element_name):
                element.set("id",str(id))
                id += 1
        else:
            pass
        
    tree.write(file)

def xml_delete_attribute(file,element_name,attribute_name):
    tree = ET.parse(file)
    root = tree.getroot()
    
    for element in tree.findall(element_name):
        del(element.attrib[attribute_name])
    
    tree.write(file)
    
#def csv_parser()
#def json_parser()
#def config_parser()
# Graphical User Interface settings #

# Add your new theme colors and settings
my_new_theme = {"BACKGROUND": "#1c1e23",
                "TEXT": "#d2d2d3",
                "INPUT": "#3d3f46",
                "TEXT_INPUT": "#d2d2d3",
                "SCROLL": "#3d3f46",
                "BUTTON": ("#6fb97e", "#313641"),
                "PROGRESS": ("#6fb97e", "#4a6ab3"),
                "BORDER": 1,
                "SLIDER_DEPTH": 0,
                "PROGRESS_DEPTH": 0}
# Add your dictionary to the PySimpleGUI themes
sg.theme_add_new("MyGreen", my_new_theme)

# Switch your theme to use the newly added one. You can add spaces to make it more readable
sg.theme("MyGreen")
font = ("Arial", 18)

# Graphical User Interface layout #
MENU_RIGHT_CLICK = ["",["Clear Output", "Version", "Exit"]]
FILE_TYPES = (("XML (Extensible Markup Language)",".xml"),("CSV (Comma Seperated Value)", ".csv"),("JSON (JavaScript Object Notation)",".json"),("Configuration-File",".config"))
element_name_in_xml = [""]

layout = [[sg.Text("Program Main",font="Consolas 24 bold underline",justification="center")],
          [sg.Text("Electronic Data Parser")],
          [sg.Text("Input:"),sg.Input(size=(43,1),key="-FILE_INPUT-"),sg.FileBrowse(file_types=FILE_TYPES),sg.Button("Read",key="-READ_FILE-")],
          [sg.Text("Add attribute:"),sg.Input(size=(10,1),key="-ATTRIBUTE_NAME_INPUT-"),sg.Text("to element:"),sg.Combo(element_name_in_xml,size=(10,1),key="-ELEMENT_NAME_INPUT-"),sg.Text("with value:"),sg.Input(size=(10,1),key="-ATTRIBUTE_VALUE_INPUT-"),sg.Button("Add",key="-ADD_ATTRIBUTE_BUTTON-")],
          [sg.Text("Del attribute:"),sg.Input(size=(10,1),key="-DEL_ATTRIBUTE_NAME_INPUT-"),sg.Text("from element:"),sg.Combo(element_name_in_xml,size=(10,1),key="-DEL_ELEMENT_NAME_INPUT-"),sg.Button("Delete",key="-DELETE_ATTRIBUTE_BUTTON-")],
          [sg.Multiline(size=(80,10),key="-INPUT_CONSOLE-")],
          [sg.Text("Convert the Opened file to a different one:")],
          [sg.Text("Output:"),sg.Input(size=(36,1),key="-OUTPUT_CONSOLE-"),sg.FolderBrowse(key="-FILE_OUTPUT-"),sg.FileSaveAs(file_types=FILE_TYPES)],
          [sg.Multiline(size=(80,10))]]

window = sg.Window("Data Parser",layout,font=font, finalize=True,right_click_menu=MENU_RIGHT_CLICK)

# Main Window events and functionality #
while True:
    event,values = window.read(timeout=50)
    
    if event == sg.WIN_CLOSED:
        break
    
    # VARIABLES #
    input_path = values["-FILE_INPUT-"]
    output_path = values["-FILE_OUTPUT-"]
    element_name = values["-ELEMENT_NAME_INPUT-"]
    del_element_name = values["-DEL_ELEMENT_NAME_INPUT-"]
    del_attribute_name = values["-DEL_ATTRIBUTE_NAME_INPUT-"]
    attribute_name = values["-ATTRIBUTE_NAME_INPUT-"]
    attribute_value = values["-ATTRIBUTE_VALUE_INPUT-"]

    if event == "-READ_FILE-":
        if len(input_path) == 0 or not input_path.endswith(".xml"):
            window["-INPUT_CONSOLE-"].update("Error, no Input File selected or wrong filetype")
        else:
            window.perform_long_operation(lambda: xml_parser(input_path),"-INPUT_CONSOLE-")
        
    if event == "-ADD_ATTRIBUTE_BUTTON-":
        if len(input_path) == 0 or not input_path.endswith(".xml"):
            window["-INPUT_CONSOLE-"].update("Error, no Input File selected or wrong filetype")
        else:
            window.perform_long_operation(lambda: xml_add_attribute(input_path,element_name,attribute_name,attribute_value),"-INPUT_CONSOLE-")
    if event =="-DELETE_ATTRIBUTE_BUTTON-":
        if len(input_path) == 0 or not input_path.endswith(".xml"):
            window["-INPUT_CONSOLE-"].update("Empty Inputs, can't delete Attribute.")
        else:
            window.perform_long_operation(lambda: xml_delete_attribute(input_path,del_element_name,del_attribute_name),"-INPUT_CONSOLE-")
            
window.close # Kill program
