# pylint: disable=E0611
import train
import argparse
import torch as th
import numpy as np
import utils.plot as up
from utils.args import str2bool, __range
from loader import LandslideDataset, LandslideTrainDataset, create_oversample_data
from torch.utils.data import DataLoader

def custom_collate_fn(batch):
    in_data = th.stack([e['data'] for e in batch], 0)
    label = th.stack([e['gt'] for e in batch], 0)
    return {'data': in_data, 'gt': label}

def get_args():
    parser = argparse.ArgumentParser(description="Training a CNN-Classifier for landslide prediction")
    # parser.add_argument("--cross_validation", type=str2bool, default=False)
    parser.add_argument("--model", type=str, default="FCNwPool")
    parser.add_argument("--lr", type=float, default=0.0001)
    parser.add_argument("--n_epochs", type=int, default=1)
    parser.add_argument("--batch_size", type=int, default=5)
    parser.add_argument("--num_workers", type=int, default=0)
    parser.add_argument("--decay", type=float, default=1e-5)
    parser.add_argument("--load_model", type=str, default='')
    parser.add_argument("--validate", type=str2bool, default=False)
    parser.add_argument("--data_path", type=str, default="../image_data/landslide.h5")
    parser.add_argument("--save_model_to", type=str, default="../models/CNN/")
    parser.add_argument("--region", type=str, default='Veneto')
    parser.add_argument("--pix_res", type=int, default=10)
    parser.add_argument("--stride", type=int, default=200)
    parser.add_argument("--ws", type=int, default=200)
    parser.add_argument("--s", type=int, default=5) #save the model at how many epochs
    parser.add_argument("--c", type=str2bool, default=True)
    parser.add_argument("--pad", type=int, default=64)
    parser.add_argument("--feature_num", type=int, default=94)
    parser.add_argument("--oversample_pts", action='append', type=__range)
    parser.add_argument("--save_res_to", type=str, default='../output/CNN/')
    parser.add_argument("--oversample", type=str2bool, default=False)
    parser.add_argument("--patience", type=int, default=2)
    parser.add_argument("--random_sample", type=str2bool, default=True)
    parser.add_argument("--pos_indices", type=str, default='')
    return parser.parse_args()

def main():
    args = get_args()
    testData = LandslideDataset(
        args.data_path,
        args.region,
        args.ws,
        'test',
        args.pad
    )
    test_loader = DataLoader(
        testData,
        batch_size=args.batch_size,
        shuffle=False,
        num_workers=args.num_workers
    )
    # import ipdb; ipdb.set_trace()
    if args.oversample_pts:
        args.oversample_pts = np.asarray(args.oversample_pts).reshape(-1, 4)
        oversample_path = create_oversample_data(args)
        trainData = LandslideTrainDataset(
            args.data_path,
            args.region,
            args.stride,
            args.ws,
            args.oversample_pts,
            oversample_path,
            args.pad,
            args.feature_num,
        )
    else:
        trainData = LandslideDataset(
            args.data_path,
            args.region,
            args.ws,
            'train',
            args.pad
        )
        print('train data created without oversampling.')
    train_loader = DataLoader(
        trainData,
        batch_size=args.batch_size,
        shuffle=True,
        num_workers=args.num_workers
    )
    if args.validate:
        print("loading a trained model...", end='\r')
        model = th.load(args.load_model)
        if args.random_sample:
            up.validate_on_ones(args, model, testData)
        else:
            # up.validate_all(args, model, test_loader)
            up.validate_all(args, model, train_loader)
    else:
        print("starting to train ...")
        train.train(args, train_loader, test_loader)

if __name__ == "__main__":
    main()
