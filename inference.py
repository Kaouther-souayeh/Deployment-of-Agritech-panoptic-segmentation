import torch
import torch.utils.data as data
import numpy as np

import os
import pickle as pkl
import argparse
import pprint
from tqdm import tqdm

from models.stclassifier import PseLTae_pretrained
from dataset import PixelSetData


def prepare_model_and_loader(config):
    mean_std = pkl.load(open('S2-2017-T31TFM-meanstd.pkl', 'rb'))
    extra = 'geomfeat' if config['geomfeat'] else None
    dt = PixelSetData(config['dataset_folder'], labels='label_44class', npixel=config['npixel'],
                      sub_classes=[1,3,4,11,20,21,23,25,28],
                      norm=mean_std,
                      extra_feature=extra, return_id=True)
    dl = data.DataLoader(dt, batch_size=config['batch_size'], num_workers=config['num_workers'])

    model_config = dict(input_dim=config['input_dim'], mlp1=config['mlp1'], pooling=config['pooling'],
                        mlp2=config['mlp2'], n_head=config['n_head'], d_k=config['d_k'], mlp3=config['mlp3'],
                        dropout=config['dropout'], T=config['T'], len_max_seq=config['lms'],
                        positions=dt.date_positions if config['positions'] == 'bespoke' else None,
                        mlp4=config['mlp4'])

    if config['geomfeat']:
        model_config.update(with_extra=True, extra_size=4)
    else:
        model_config.update(with_extra=False, extra_size=None)

    model = PseLTae_pretrained(config['weight_dir'], model_config, device=config['device'], fold=config['fold'])

    return model, dl


def recursive_todevice(x, device):
    if isinstance(x, torch.Tensor):
        return x.to(device)
    else:
        return [recursive_todevice(c, device) for c in x]


def predict(model, loader, config):
    record = []
    device = torch.device(config['device'])

    for (x, y, ids) in tqdm(loader):
        y_true = (list(map(int, y)))
        #ids = list(ids)
        ids = list(ids)
        x = recursive_todevice(x, device)
        with torch.no_grad():
            prediction = model(x)
        y_p = list(prediction.argmax(dim=1).cpu().numpy())

        record.append(np.stack([ids, y_true, y_p], axis=1))


    record = np.concatenate(record, axis=0)
    

    os.makedirs(config['output_dir'], exist_ok=True)
    np.save(os.path.join(config['output_dir'], 'Predictions_id_ytrue_y_pred5.npy'), record)


def main(config):
    print('Preparation . . . ')
    model, loader = prepare_model_and_loader(config)
    print('Inference . . .')
    predict(model, loader, config)
    print('Results stored in directory {}'.format(config['output_dir']))


if __name__ == '__main__':

    parser = argparse.ArgumentParser()

    # Set-up parameters
    parser.add_argument('--dataset_folder', default='/home/pc/Documents/bilel/deployment-of-agritech-panoptic-segmentation/S2-2017-T31TFM-PixelSet-TOY', type=str,
                        help='Path to the folder where the results are saved.')
    parser.add_argument('--weight_dir', default='/home/pc/Documents/bilel/deployment-of-agritech-panoptic-segmentation/wEIGHTS_CULT', type=str,
                        help='Path to the folder containing the model weights')
    parser.add_argument('--fold', default='all', type=str,
                        help='Specify whether to load the weight sets of al folds (all) or '
                             'only load the weight of a specific fold by indicating its number')
    parser.add_argument('--output_dir', default='/home/pc/Documents/bilel/deployment-of-agritech-panoptic-segmentation/out2',
                        help='Path to the folder where the predictions should be stored')
    parser.add_argument('--num_workers', default=8, type=int, help='Number of data loading workers')
    parser.add_argument('--device', default='cpu', type=str,
                        help='Name of device to use for tensor computations (cuda/cpu)')
    parser.add_argument('--display_step', default=50, type=int,
                        help='Interval in batches between display of training metrics')
   

    # Dataset parameters
    parser.add_argument('--batch_size', default=482, type=int, help='Batch size')
    parser.add_argument('--npixel', default=64, type=int, help='Number of pixels to sample from the input images')

    # Architecture Hyperparameters
    ## PSE
    parser.add_argument('--input_dim', default=10, type=int, help='Number of channels of input images')
    parser.add_argument('--mlp1', default='[10,32,64]', type=str, help='Number of neurons in the layers of MLP1')
    parser.add_argument('--pooling', default='mean_std', type=str, help='Pixel-embeddings pooling strategy')
    parser.add_argument('--mlp2', default='[132,128]', type=str, help='Number of neurons in the layers of MLP2')
    parser.add_argument('--geomfeat', default=1, type=int,
                        help='If 1 the precomputed geometrical features (f) are used in the PSE.')

    ## TAE
    parser.add_argument('--n_head', default=16, type=int, help='Number of attention heads')
    parser.add_argument('--d_k', default=8, type=int, help='Dimension of the key and query vectors')
    parser.add_argument('--mlp3', default='[256,128]', type=str, help='Number of neurons in the layers of MLP3')
    parser.add_argument('--T', default=1000, type=int, help='Maximum period for the positional encoding')
    parser.add_argument('--positions', default='bespoke', type=str,
                        help='Positions to use for the positional encoding (bespoke / order)')
                        
    parser.add_argument('--lms', default=24, type=int,
                        help='Maximum sequence length for positional encoding (only necessary if positions == order)')
    parser.add_argument('--dropout', default=0, type=float, help='Dropout probability')
    parser.add_argument('--d_model', default=256, type=int,help="size of the embeddings (E), if input vectors are of a different size, a linear layer is used to project them to a d_model-dimensional space"
                                                                                                                                                        )
    ## Classifier
    parser.add_argument('--num_classes', default=9, type=int, help='Number of classes')
    parser.add_argument('--mlp4', default='[128, 64, 32, 20]', type=str, help='Number of neurons in the layers of MLP4')
    parser.add_argument('--nker', default='[32,32,128]', type=str, help="Number of successive convolutional kernels ")

    config = parser.parse_args()
    config = vars(config)
    for k, v in config.items():
        if 'mlp' in k:
            v = v.replace('[', '')
            v = v.replace(']', '')
            config[k] = list(map(int, v.split(',')))

    pprint.pprint(config)
    main(config)
