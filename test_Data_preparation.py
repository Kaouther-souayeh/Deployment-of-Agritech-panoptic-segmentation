import os
import tempfile
import pytest
import Data_preparation
from Data_preparation.dataset_preparation import prepare_dataset

@pytest.fixture
def temp_dir():
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


def test_folder_serie_temporelle():
    folder_name = os.path.join("Data_preparation", "serie_temporelle") #using os.path.join() to specify the relative path to the "serie temporelle" folder within the "Data_preparation" folder.
    # Check if the folder exists
    assert os.path.exists(folder_name), f"Folder '{folder_name}' does not exist."
    
    # Check if the folder contains .tiff images
    files = os.listdir(folder_name)
    tiff_files = [f for f in files if f.endswith(".tiff") or f.endswith(".tif")]
    assert len(tiff_files) > 0, f"Folder '{folder_name}' does not contain any .tiff images."
 
 
    
def test_folder_geojson_exists():
    folder_name = os.path.join("Data_preparation", "OCS_OBS.geojson") #using os.path.join() to specify the relative path to the "serie temporelle" folder within the "Data_preparation" folder.
    # Check if the folder exists
    assert os.path.exists(folder_name), f"Folder '{folder_name}' does not exist."



def test_prepare_dataset(temp_dir):
    # define input variables
    output_path = temp_dir
    input_folder =  os.path.join(os.getcwd(), 'Data_preparation/serie_temporelle')
    rpg_file = os.path.join(os.getcwd(), 'Data_preparation/OCS_OBS.geojson')
    label_names = ['CODE_CULT']

    # run the function
    prepare_dataset(output_path, input_folder, rpg_file, label_names=label_names)

    # check that output files were created
    assert os.path.exists(os.path.join(output_path, 'META', 'dates.json'))
    assert os.path.exists(os.path.join(output_path, 'META', 'labels.json'))
    assert os.path.exists(os.path.join(output_path, 'META', 'sizes.json'))
    assert os.path.exists(os.path.join(output_path, 'DATA'))

  
