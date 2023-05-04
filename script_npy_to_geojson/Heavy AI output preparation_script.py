import json
import os
import numpy as np
import argparse

#Steps:
#1- Get the Geojson file
#2- Get the npy file
#3- Make a copy of the geojson file
#4.1- Make a dictionary of the geojson file: {key=CODE_CUIL, value=CULTURE}
#4.2- Make a dictionary of the npy file: {key=CODE_CUIL, value=y_pred}
# Then, there are 2 modifications to do: First: If y_expected ==1, and y_pred == 0, then y_pred = 1
#   And the second modification is: if y_pred == 0, then y_pred =  "non building", else y_pred = "building"
#5- Iterate the features of the geojson file and add replace the value of the Classe by the y_pred value.


def inf(config):
    #1- Get the Geojson file
    Geojson_path=config['path'] + "OCS_OBS.geojson"
    #2- Get the npy file
    npy_path = config['path'] + "tuntun.npy"


    #3- Make a copy of the geojson file
    with open(Geojson_path) as f:
        data = json.load(f)
        with open(config["path"]+"Output for HeavyAI/"+"HEAVY_tuntun.geojson","w") as outfile:
            json.dump(data, outfile, indent=4)

    #4.1- Make a dictionary of the geojson file: {key=Matricule, value=Classe}
    geojson_dict = {}
    with open(config["path"]+"Output for HeavyAI/"+"HEAVY_tuntun.geojson") as f:
        data = json.load(f)
        for feature in data['features']:
            geojson_dict[feature['properties']['CODE_CULT']] = feature['properties']['CULTURE']
    
    #print(geojson_dict)  ######!!!!!!!!!!

    #4.2- Make a dictionary of the npy file: {key=Matricule, value=y_pred}
    #iterate the npy file, and make a dictionary of the npy file: {key=Matricule, value=y_pred}
    npy = np.load(npy_path)
    npy_dict_pred = {npy[i][0]:npy[i][2] for i in range(npy.shape[0])}    ######!!!!!!!!!!
    npy_dict_expected = {npy[i][0]:npy[i][1] for i in range(npy.shape[0])}
    
    for key in npy_dict_expected.keys():
        if npy_dict_pred[key] == '0':
            npy_dict_pred[key] = "1"
        elif npy_dict_pred[key] == '1':
            npy_dict_pred[key] = "2"
        elif npy_dict_pred[key] == '2':
            npy_dict_pred[key] = "3"
        elif npy_dict_pred[key] == '3':
            npy_dict_pred[key] = "4"
        elif npy_dict_pred[key] == '4':
            npy_dict_pred[key] = "5"
        elif npy_dict_pred[key] == '5':
            npy_dict_pred[key] = "6"
        elif npy_dict_pred[key] == '6':
            npy_dict_pred[key] = "7"
        elif npy_dict_pred[key] == '7':
            npy_dict_pred[key] = "8"
        elif npy_dict_pred[key] == '8':
            npy_dict_pred[key] = "9"
        elif npy_dict_pred[key] == '9':
            npy_dict_pred[key] = "10"
        elif npy_dict_pred[key] == '10':
            npy_dict_pred[key] = "11"
        elif npy_dict_pred[key] == '11':
            npy_dict_pred[key] = "12"
        elif npy_dict_pred[key] == '12':
            npy_dict_pred[key] = "13"
        elif npy_dict_pred[key] == '13':
            npy_dict_pred[key] = "14"
        elif npy_dict_pred[key] == '14':
            npy_dict_pred[key] = "15"
        elif npy_dict_pred[key] == '15':
            npy_dict_pred[key] = "16"
        elif npy_dict_pred[key] == '16':
            npy_dict_pred[key] = "17"
               
    list_geojson = []
    for geo in geojson_dict.keys():
        list_geojson.append(geo)
    list_geojson.sort()
    list_npy_pred = []
    for pred in npy_dict_pred.keys():
        list_npy_pred.append(pred)
    list_npy_pred.sort()

    '''
    ##The following part is to check the parcels tha we didin't use neither in the training nor in the testing phase, and we did that for multiple reasons:
    #  1- The parcel is a parking (Not deleted form the geojson file): They do not represent a problem, I just deleted them in training and testing phase.
    #  2- The parcel is too small (Deleted from the geojson file)
    #  3- It happened a rotation in the parcel. (Deleted from the geojson file)
    difference = list(set(list_geojson) - set(list_npy_pred))

    print ("Length of the geojson file: ", len(list_geojson))
    print ("Length of the npy file: ", len(list_npy_pred))
    print ("Difference: ", difference)
    #print (npy_dict_expected)

    ###### Here in JEMMEL, we deleted the parcels: 3,4 for rotation. ####
    ######                 And we deleted 11 because it's parking. ######
   

    with open(config["path"]+"Output for HeavyAI/"+"HEAVY_tuntun.geojson") as f:
        data = json.load(f)
        for feature in data['features']:
            if (feature['properties']['CULTURE'] == 'parking'):
                continue
            feature['properties']['CULTURE'] = npy_dict_pred[feature['properties']['CODE_CULT']]
        with open(config["path"]+"Output for HeavyAI/"+"HEAVY_JEMMEL.geojson", "w") as outfile:
            json.dump(data, outfile, indent=4)
 '''

""" def train(config):
    npy_path = config['path'] + subfolder + "Predictions_id_ytrue_y_pred.npy"
    #1- Make a dictionary of the npy file: {key=Matricule, value=y_pred}
    #iterate the npy file, and make a dictionary of the npy file: {key=Matricule, value=y_pred}
    npy = np.load(npy_path)
    npy_dict_pred = {npy[i][0]:npy[i][2] for i in range(npy.shape[0])}    ######!!!!!!!!!!
    npy_dict_expected = {npy[i][0]:npy[i][1] for i in range(npy.shape[0])}
    for key in npy_dict_expected.keys():
        if npy_dict_expected[key] == '1' and npy_dict_pred[key] == '0':
            npy_dict_pred[key] = '1'

        if npy_dict_pred[key] == '0':
            npy_dict_pred[key] = "non building"
        elif npy_dict_pred[key] == '1':
            npy_dict_pred[key] = "building"

    #print(npy_dict_pred)
    #print(npy_dict_expected)
    #2- Iterate through geojson files
    directory_path = config['path'] + subfolder
    # Iterate through each subdirectory
    for subdir, __, files in os.walk(directory_path):
        # Check if there are any files in the current subdirectory
        if files:
            # Iterate through each file in the subdirectory
            for filename in files:
                # Check if the file is a geojson file
                if filename.endswith(".geojson"):
                    # Access the full path to the geojson file
                    geojson_path = os.path.join(subdir, filename)
                    L = geojson_path.split(("/"))
                    Zone_name = L[-1]
                    with open(geojson_path) as f:
                        data = json.load(f)
                        for feature in data['features']:
                            if (feature['properties']['CULTURE'] == 'parking'):
                                continue
                            if feature['properties']['CODE_CULT'] not in npy_dict_pred.keys():
                                feature['properties']['CULTURE'] = "N.A"   ###This is for the parcels that we didin't use in the training phase;
                                #We deleted the .npy files and its META, but without deleting their coordinates from the geojson file.
                                continue
                            feature['properties']['CULTURE'] = npy_dict_pred[feature['properties']['CODE_CULT']]
                        with open(config["path"]+"Output for HeavyAI/HEAVY_"+Zone_name, "w") as outfile:
                            json.dump(data, outfile, indent=4)

                        #It still to add the parcels where happened rotation:

"""

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    #Set-up parameters
    parser.add_argument('--path', type=str, default='/home/pc/Documents/script_npy_to_geojson/', help='Path to the folder containing the geojson files')
    parser.add_argument('--type', type=str, default='Inference', help='It could be either Inference(Here kairouan) or Training(The rest)')
    #parser.add_argument("--Rotation", type=str, default="Yes", help="If Yes: Add the rotated parcels to the geojson file. If No: Don't add them.")
    config = parser.parse_args()
    config = vars(config)

    
    
    inf(config)