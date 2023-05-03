import torch
import torch.utils.data as data
import numpy as np

import os
import pickle as pkl
import argparse
import pprint
from tqdm import tqdm
from learning.focal_loss import FocalLoss

from models.stclassifier import PseLTae_pretrained
from dataset import PixelSetData

def evaluation(model, criterion, loader, device, config, mode='test'):
    y_true = []
    y_pred = []

    acc_meter = tnt.meter.ClassErrorMeter(accuracy=True)
    loss_meter = tnt.meter.AverageValueMeter()

    for (x, y) in loader:
        y_true.extend(list(map(int, y)))
        x = recursive_todevice(x, device)
        y = y.to(device)

        with torch.no_grad():
            prediction = model(x)
            loss = criterion(prediction, y)

        acc_meter.add(prediction, y)
        loss_meter.add(loss.item())

        y_p = prediction.argmax(dim=1).cpu().numpy()
        y_pred.extend(list(y_p))

    metrics = {'{}_accuracy'.format(mode): acc_meter.value()[0],
               '{}_loss'.format(mode): loss_meter.value()[0],
               '{}_IoU'.format(mode): mIou(y_true, y_pred, config['num_classes'])}

    if mode == 'val':
        return metrics
    elif mode == 'test':
        return metrics, confusion_matrix(y_true, y_pred, labels=list(range(config['num_classes'])))

def prepare_model_and_loader(config):
    mean_std = mean_std = pkl.load(open('S2-2017-T31TFM-meanstd.pkl', 'rb'))
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
        ids = list(ids)

        x = recursive_todevice(x, device)
        with torch.no_grad():
            prediction = model(x)
        y_p = list(prediction.argmax(dim=1).cpu().numpy())

        record.append(np.stack([ids, y_true, y_p], axis=1))

    record = np.concatenate(record, axis=0)

    os.makedirs(config['output_dir'], exist_ok=True)
    np.save(os.path.join(config['output_dir'], '3.npy'), record)


def main(config):
    print('Preparation . . . ')
    model, loader = prepare_model_and_loader(config)
    print('Inference . . .')
    predict(model, loader, config)
    print('Results stored in directory {}'.format(config['output_dir']))
    np.random.seed(config['rdm_seed'])
    torch.manual_seed(config['rdm_seed'])
    prepare_output(config)

    mean_std = pkl.load(open('S2-2021-T32SNE-meanstd.pkl', 'rb'))
    extra = 'geomfeat' if config['geomfeat'] else None

    # We only consider the subset of classes with more than 100 samples in the S2-Agri dataset
    subset =[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17]
    #subset=[1,3,4,11,20,21,23,25,28]
    if config['preload']:
        dt = PixelSetData_preloaded(config['dataset_folder'], labels='label_44class', npixel=config['npixel'],
                                    sub_classes=subset,
                                    norm=mean_std,
                                    extra_feature=extra)
    else:
        dt = PixelSetData(config['dataset_folder'], labels='label_44class', npixel=config['npixel'],
                          sub_classes=subset,
                          norm=mean_std,
                          extra_feature=extra)
    device = torch.device(config['device'])

    loaders = get_loaders(dt, config['kfold'], config)
    for fold, (train_loader, val_loader, test_loader) in enumerate(loaders):
        print('Starting Fold {}'.format(fold + 1))
        print('Train {}, Val {}, Test {}'.format(len(train_loader), len(val_loader), len(test_loader)))
    criterion = FocalLoss(1)
    test_metrics, conf_mat = evaluation(model, criterion, test_loader, device=device, mode='test', config=config)
    print('Loss {:.4f},  Acc {:.2f},  IoU {:.4f}'.format(test_metrics['test_loss'], test_metrics['test_accuracy'],
                                                             test_metrics['test_IoU'],conf_mat))


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
    parser.add_argument('--output_dir', default='./output',
                        help='Path to the folder where the predictions should be stored')
    parser.add_argument('--num_workers', default=8, type=int, help='Number of data loading workers')
    parser.add_argument('--device', default='cpu', type=str,
                        help='Name of device to use for tensor computations (cuda/cpu)')
    parser.add_argument('--display_step', default=5, type=int,
                        help='Interval in batches between display of training metrics')
   

    # Dataset parameters
    parser.add_argument('--batch_size', default=700, type=int, help='Batch size')
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
    parser.add_argument('--dropout', default=0.2, type=float, help='Dropout probability')
    parser.add_argument('--d_model', default=256, type=int,help="size of the embeddings (E), if input vectors are of a different size, a linear layer is used to project them to a d_model-dimensional space"
                                                                                                                                                        )
    ## Classifier
    parser.add_argument('--num_classes', default=17, type=int, help='Number of classes')
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
