import os
import numpy as np
import cv2
import math
from sklearn.cluster import KMeans


def OSTU (img_path):
    img = cv2.imread(img_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    ret1, th1 = cv2.threshold(gray, 0, 255, cv2.THRESH_OTSU)
    mask = 255 - th1
    return mask


def kmeans(img_path, n_clusters, patch_size):
    mask = OSTU(img_path)
    #print(mask.shape)
    features = []
    h, w = mask.shape[:2]
    for i in range(h):
        for j in range(w):
            if mask[i][j] == 255:
                features.append([i, j])

    features = np.array(features)
    #print(features.shape)
    res = KMeans(n_clusters=n_clusters, random_state=0).fit(features)
    centers = res.cluster_centers_
    centers = nms(centers, patch_size)
    coords = []
    for each_centers in centers:
        x1 = max(int(each_centers[0] - patch_size // 2), 0)
        y1 = max(int(each_centers[1] - patch_size // 2), 0)
        x2 = min(int(each_centers[0] + patch_size // 2), h)
        y2 = min(int(each_centers[1] + patch_size // 2), w)
        coords.append([x1, y1, x2, y2])
    return np.array(coords), centers


def nms(centers, patch_size):
    res = []
    cur = []
    visit = [False] * len(centers)
    for i, each in enumerate(centers):
        if not visit[i]:
            cur.append(each)
            visit[i] = True
            for j in range(i+1,len(centers)):
                delta_x = cur[0][0] - centers[j][0]
                delta_y = cur[0][1] - centers[j][1]
                if math.sqrt((delta_x*delta_x + delta_y*delta_y)) <= patch_size:
                    cur.append(centers[j])
                    visit[j] = True
            res.append(np.mean(cur, axis=0))
            cur = []
   # print(len(res))
    return np.array(res)


def color(img_path, out_path, centers):
    img = cv2.imread(img_path)
    for each_center in centers:
        start = (int(each_center[1]) - 30, int(each_center[0]) - 30)
        end = (int(each_center[1]) + 30, int(each_center[0]) + 30)
        img = cv2.rectangle(img, start, end, (255, 0, 0), 3)
    cv2.imwrite(os.path.join(out_path, 'color.jpg'), img)

