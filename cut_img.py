import os
import cv2
import openslide as opsl
import numpy as np
from PIL import Image
from libtiff import TIFF
import threadpool
import pyvips
from kmeans import kmeans
from kmeans import color
from np2vips import numpy2vips
import argparse


def get_args():
    parser = argparse.ArgumentParser(description='stomach / cut_image')
    parser.add_argument('-i', '--input', type=str, default='./dataset', help='path of input data')
    parser.add_argument('-o', '--output', type=str, default='./output', help='path of output')
    parser.add_argument('-c','--centers', type=int, default=12, help='nums of centers')
    parser.add_argument('-p', '--patch', type=int, default=60, help='size of patch')
    parser.add_argument('-ps', '--poolsize', type=int, default=1, help='nums of threadpool ')
    return parser.parse_args()


def cut(p):
    tiff_path, bmp_path, output_path, n_clusters, patch_size = p
    slide_name = tiff_path.split('/')[-1].replace('.tiff','')
    output_path = os.path.join(output_path, slide_name)
    if not os.path.isdir(output_path):
        os.makedirs(output_path)
    slide = opsl.OpenSlide(tiff_path)  # W,H
    img = cv2.imread(bmp_path) # H, W
    slide_w, slide_h = slide.dimensions
    img_h, img_w = img.shape[:2]
    downsample = min(int(slide_h / img_h) , int(slide_w / img_w))
    coords, centers= kmeans(bmp_path, n_clusters, patch_size) #(x1,y1,x2,y2)
    color(bmp_path, output_path, centers)
    coords = downsample * coords
    #print(slide_w, slide_h, img_w, img_h, downsample)
    print("Processing: {}\t Rois: {}".format(slide_name, centers.shape[0]))
    for i, each_coord in enumerate(coords):
        cur_slide_name = os.path.join(output_path, slide_name+'_' + str(i) + '.tif')
        cur_img = np.array(slide.read_region((each_coord[1], each_coord[0]), 0, (each_coord[3] - each_coord[1], each_coord[2] - each_coord[0])).convert('RGB'))
        print('Save:{}'.format(cur_slide_name))
        im = numpy2vips(cur_img)
        im.tiffsave(cur_slide_name, tile=True, bigtiff=True)


if __name__ == '__main__':
    args = get_args()
    data_path = args.input
    out_path = args.output
    n_clusters = args.centers
    patch_size = args.patch
    tiff_path = []
    bmp_path = []
    for roots, dirs, filenames in os.walk(data_path):
        for each_file in filenames:
            if '.tiff' in each_file:
                tiff_path.append(os.path.join(roots,each_file))
            if 'preview.bmp' in each_file:
                bmp_path.append(os.path.join(roots,each_file))
    assert len(tiff_path) == len(bmp_path), print('length error')
    params = [[tiff_path[i], bmp_path[i], out_path, n_clusters, patch_size]for i in range(len(tiff_path))]
    if not os.path.isdir(out_path):
        os.makedirs(out_path)
    pool = threadpool.ThreadPool(args.poolsize)
    requests = threadpool.makeRequests(cut, params)
    [pool.putRequest(req) for req in requests]
    pool.wait()

