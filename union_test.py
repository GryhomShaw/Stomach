import os
import argparse
from preview import get_labels
from kmeans import color
from cut_img import cut


def get_args():
    parser = argparse.ArgumentParser(description='stomach / preview')
    parser.add_argument('-tiff_path', '--tiff_path', type=str, default='./dataset', help='path of tiff')
    parser.add_argument('-bmp_path', '--bmp_path', type=str, default=None, help='path of bmp')
    parser.add_argument('-c', '--centers', type=int, default=12, help='nums of centers')
    parser.add_argument('-p', '--patch', type=int, default=60, help='size of patch')
    parser.add_argument('-iou', '--iou', type=float, default=0.25, help='val of IOU')
    parser.add_argument('-o', '--output', type=str, default='./output', help='path of output')
    parser.add_argument('-label', '--label', type=int, default=[], nargs='+', help='coords of box')
    return parser.parse_args()



if __name__ == '__main__':
    args = get_args()
    labels = get_labels(args.tiff_path, args.bmp_path, args.centers, args.patch, args.iou)
    slidename = args.tiff_path.split('/')[-1]
    root_path = args.tiff_path.replace(slidename, "")
    if args.bmp_path is None: #没有指定缩略图路径
        args.bmp_path = os.path.join(root_path, 'preview.bmp')

    color(args.bmp_path, args.output, labels)
    for each_label in labels:
        cut(args.tiff_path, args.bmp_path, args.output, each_label)

