import os
import numpy as np
from Inference_CULT import predict


def test_folder_pretrained_weights():
    folder_name=os.path.join("PSE-LTAE-pre-trained-weights")
    assert os.path.exists(folder_name), f"Folder '{folder_name}' does not exist."
    
    
def test_folder_Data_preparation():
    folder_name=os.path.join("Data_preparation")
    assert os.path.exists(folder_name), f"Folder '{folder_name}' does not exist."   




# Define a mock model and loader for testing
#class MockModel:
   # def __call__(self, x):
   #     return x

#class MockLoader:
   # def __iter__(self):
   #     return iter([(np.array([1]), np.array([2]), 'id_1'), (np.array([3]), np.array([4]), 'id_2')])
    def __len__(self):
        return 2

#def test_predict(tmpdir):
    # Create a temporary directory for the output file
 #   output_dir = str(tmpdir.mkdir("output"))

    # Define a mock config dictionary
  #  config = {'device': 'cpu', 'output_dir': output_dir}

    # Initialize the model and loader
   # model = MockModel()
     #loader = MockLoader()

    # Call the predict function
   #  predict(model, loader, config)

    # Check if the output file was created
   # output_file = os.path.join(output_dir, 'tuntun.npy')
    #assert os.path.exists(output_file), f"Output file '{output_file}' does not exist."

       