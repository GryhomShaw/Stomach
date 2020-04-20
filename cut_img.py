import os
import cv2
import time
import openslide as opsl
import numpy as np
import threadpool
import pyvips
from kmeans import kmeans
from kmeans import color
from np2vips import numpy2vips
import argparse


def get_args():
    parser = argparse.ArgumentParser(description='stomach / cut_img')
    parser.add_argument('-tiff_path', '--tiff_path', type=str, default='./dataset', help='path of tiff')
    parser.add_argument('-bmp_path', '--bmp_path', type=str, default=None, help='path of bmp')
    parser.add_argument('-o', '--output', type=str, default='./output', help='path of output')
    parser.add_argument('-label', '--label', type=int, default=[], nargs='+', help='coords of box', required=True)
    return parser.parse_args()


def cut(tiff_path, bmp_path, output_path, coords):
    assert os.path.isfile(tiff_path), print('TIFF PATH ERROR: {}'.format(tiff_path))
    slide_name = tiff_path.split('/')[-1].replace('.tiff', '')
    if bmp_path is None:
        bmp_path = os.path.join(tiff_path.replace(tiff_path.split('/')[-1], ''), 'preview.bmp')
    assert os.path.isfile(bmp_path), print('BMP PATH ERROR: {}'.format(bmp_path))
    assert isinstance(coords, list), print('COORDS TYPE ERROR: {}'.format(type(coords)))
    assert len(coords) == 4, print('COORDS LENGTH ERROR: {}'.format(len(coords)))
    if not os.path.isdir(output_path):
        os.makedirs(output_path)
    slide = opsl.OpenSlide(tiff_path)  # W,H
    img = cv2.imread(bmp_path)  # H, W
    slide_w, slide_h = slide.dimensions
    img_h, img_w = img.shape[:2]
    downsample = min(int(slide_h / img_h), int(slide_w / img_w))
    coords = downsample * np.array(coords)
    suffix_name = str(coords[0]) + "_" + str(coords[1])
    cur_slide_name = os.path.join(output_path, slide_name+'_' + suffix_name + '.tiff')
    cur_img = np.array(slide.read_region((coords[1], coords[0]), 0, (coords[3] - coords[1], coords[2] - coords[0]))
                       .convert('RGB'))
    print('Save:{}'.format(cur_slide_name))
    im = numpy2vips(cur_img)
    im.tiffsave(cur_slide_name, tile=True, compression='jpeg', bigtiff=True, pyramid=True)


if __name__ == '__main__':
    args = get_args()
    cut(args.tiff_path, args.bmp_path, args.output, args.label)


