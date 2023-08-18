import PySimpleGUI as sg
import logging, numpy
import pandas as pd
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
    window["-OUTPUT_WINDOW-"].update(xml_string)
    
    # Get elements in XML File:
    tags_xml = [elem.tag for elem in root.iter()]
    tags_to_set = set(tags_xml)
    tags_to_list = list(tags_to_set)
    
    # Add Elements to ComboBox List
    window["-ELEMENT_NAME_INPUT-"].update(values=tags_to_list)
    window["-DEL_ELEMENT_NAME_INPUT-"].update(values=tags_to_list)
    
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
    window["-DEL_ELEMENT_NAME_INPUT-"].update("")
    window["-DEL_ATTRIBUTE_NAME_INPUT-"]

def conert_xml_to_csv(file,output):
    df = pd.read_xml(file)
    df.to_csv(output)
    
#def csv_parser()
#def json_parser()
#def config_parser()
# Graphical User Interface settings #

# Add your new theme colors and settings
my_new_theme = {"BACKGROUND": "#3d3f46",
                "TEXT": "#d2d2d3",
                "INPUT": "#1c1e23",
                "TEXT_INPUT": "#d2d2d3",
                "SCROLL": "#1c1e23",
                "BUTTON": ("#e6d922", "#313641"),
                "PROGRESS": ("#e6d922", "#4a6ab3"),
                "BORDER": 1,
                "SLIDER_DEPTH": 0,
                "PROGRESS_DEPTH": 0}
# Add your dictionary to the PySimpleGUI themes
sg.theme_add_new("MyYellow", my_new_theme)

# Switch your theme to use the newly added one. You can add spaces to make it more readable
sg.theme("MyYellow")
font = ("Consolas", 14)

# Graphical User Interface layout #
MENU_RIGHT_CLICK = ["",["Clear Output", "Version", "Exit"]]
FILE_TYPES = (("XML (Extensible Markup Language)",".xml"),("CSV (Comma Seperated Value)", ".csv"),("JSON (JavaScript Object Notation)",".json"),("Configuration-File",".config"))
element_name_in_xml = [""]

layout = [[sg.Text("XML Data Parser",font="Consolas 28 bold underline",text_color="#e6d922",justification="center")],
          [sg.Text("Manipulation of XML files.")],
          [sg.Text("Input:"),sg.Input(size=(43,1),key="-FILE_INPUT-"),sg.FileBrowse(file_types=FILE_TYPES),sg.Button("Read",key="-READ_FILE-")],
          [sg.Text("Adding Attributes to XML:",text_color="#e6d922")],
          [sg.Text("Add attribute:"),sg.Input(size=(10,1),key="-ATTRIBUTE_NAME_INPUT-"),sg.Text("to element:"),sg.Combo(element_name_in_xml,size=(10,1),key="-ELEMENT_NAME_INPUT-"),sg.Text("with value:"),sg.Input(size=(10,1),key="-ATTRIBUTE_VALUE_INPUT-"),sg.Button("Add",key="-ADD_ATTRIBUTE_BUTTON-")],
          [sg.HSeparator()],
          [sg.Text("Deleting Attributes from XML:",text_color="#e6d922")],
          [sg.Text("Del attribute:"),sg.Input(size=(10,1),key="-DEL_ATTRIBUTE_NAME_INPUT-"),sg.Text("from element:"),sg.Combo(element_name_in_xml,size=(10,1),key="-DEL_ELEMENT_NAME_INPUT-"),sg.Button("Delete",key="-DELETE_ATTRIBUTE_BUTTON-")],
          [sg.HSeparator()],
          [sg.Multiline(size=(80,10),key="-OUTPUT_WINDOW-")],
          [sg.HSeparator()],
          [sg.Text("Convert the XML file to a different one:",text_color="#e6d922")],
          [sg.Text("Output:"),sg.Input(size=(36,1),key="-FILE_OUTPUT-"),sg.FileSaveAs(file_types=FILE_TYPES,target="-FILE_OUTPUT-",key="-SAVE_AS_BUTTON-"),sg.Button("Save",key="-SAVE-")],
          [sg.HSeparator()],
          [sg.Multiline(size=(80,10))],
          [sg.Button("Exit",expand_x=True)]]

window = sg.Window("Data Parser",layout,font=font, finalize=True,right_click_menu=MENU_RIGHT_CLICK)

# Main Window events and functionality #
while True:
    event,values = window.read(timeout=50)
    
    if event == sg.WIN_CLOSED or event == "Exit":
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
            window["-OUTPUT_WINDOW-"].update("Error, no Input File selected or wrong filetype")
        else:
            window.perform_long_operation(lambda: xml_parser(input_path),"-OUTPUT_WINDOW-")
        
    if event == "-ADD_ATTRIBUTE_BUTTON-":
        if len(input_path) == 0 or not input_path.endswith(".xml"):
            window["-OUTPUT_WINDOW-"].update("Error, no Input File selected or wrong filetype")
        else:
            window.perform_long_operation(lambda: xml_add_attribute(input_path,element_name,attribute_name,attribute_value),"-OUTPUT_WINDOW-")
    if event =="-DELETE_ATTRIBUTE_BUTTON-":
        if len(input_path) == 0 or not input_path.endswith(".xml"):
            window["-OUTPUT_WINDOW-"].update("Empty Inputs, can't delete Attribute.")
        else:
            window.perform_long_operation(lambda: xml_delete_attribute(input_path,del_element_name,del_attribute_name),"-OUTPUT_WINDOW-")
    if event == "Clear Output":
        window["-OUTPUT_WINDOW-"].update("")
    if event == "Version":
            sg.popup_scrolled(sg.get_versions())
            
    if event == "-SAVE-":
        if len(values["-FILE_OUTPUT-"]) == 0:
            window["-OUTPUT_WINDOW-"].print("Path to save is empty")
        elif not output_path.endswith(".csv"):
            window["-OUTPUT_WINDOW-"].print("Wrong filetype to save as")
        else:
            window.perform_long_operation(lambda: conert_xml_to_csv(input_path,output_path),"-OUTPUT_WINDOW-")
        
window.close() # Kill program