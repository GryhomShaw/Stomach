import os
import argparse
import pyvips
import openslide as opsl
import numpy as np
from xml.dom.minidom import Document
import xml.dom.minidom as minidom
from np2vips import numpy2vips


def cut_xml(coords, xml_path, output_path='./'):
    '''
    :param coords: [x1, y1, x2, y2]
    :param xml_path: e.g. ./test/xml
    :return: None
    '''
    coords = np.array(coords)
    assert len(coords.shape) == 1 and coords.shape[0] == 4, print('COORDS SHAPE ERROR!')
    x1, y1, x2, y2 = coords
    xml_name = "{}_{}.xml".format(x1, y1)
    xml = minidom.parse(xml_path)
    root = xml.documentElement
    #xml_info =
    xml_info = xml_parser(root, coords)

    gen_xml(xml_info, output_path, xml_name)


def xml_parser(root, coords):
    coords = np.array([coords[1], coords[0], coords[3], coords[2]])
    annos_dict_list = []
    annos = root.getElementsByTagName('Annotation')
    print(len(annos))
    for i in range(len(annos)):
        anno_dict = {}
        anno_dict['Name'] = annos[i].getAttribute('Name')
        anno_dict['Type'] = annos[i].getAttribute('Type')
        anno_dict['PartOfGroup'] = annos[i].getAttribute('PartOfGroup')
        anno_dict['Color'] = annos[i].getAttribute('Color')
        labels = []
        coordinates = annos[i].getElementsByTagName('Coordinates')[0].getElementsByTagName('Coordinate') # X->W, Y->H
        for each_coord in coordinates:
            labels.append([float(each_coord.getAttribute('X')), float(each_coord.getAttribute('Y'))])

        #print(anno_dict, len(coordinates))
        labels = np.array(labels)
        if isvaild(coords, labels):
            labels -= coords[:2]
            anno_dict['labels'] = labels
            annos_dict_list.append(anno_dict)
    print(len(annos_dict_list))
    return annos_dict_list


def gen_xml(annos_dict_list, output_path, xml_name):
    doc = Document()
    ASAP_Annotations = doc.createElement('ASAP_Annotations')
    doc.appendChild(ASAP_Annotations)
    Annotations = doc.createElement('Annotations')
    category_set = {}

    for each_anno in annos_dict_list:
        anno = doc.createElement('Annotation')
        anno.setAttribute('Name', each_anno['Name'])
        anno.setAttribute('Type', each_anno['Type'])
        anno.setAttribute('PartOfGroup', each_anno['PartOfGroup'])
        category_set[each_anno['PartOfGroup']] = each_anno['Color']
        anno.setAttribute('Color', each_anno['Color'])
        Annotations.appendChild(anno)
        coords = doc.createElement('Coordinates')
        anno.appendChild(coords)

        for id, each_coord in enumerate(each_anno['labels']):
            coord = doc.createElement('Coordinate')
            coord.setAttribute('Order', str(id))
            coord.setAttribute('X', str(round(each_coord[0], 4)))
            coord.setAttribute('Y', str(round(each_coord[1], 4)))
            coords.appendChild(coord)
    ASAP_Annotations.appendChild(Annotations)

    AnnotationGroups = doc.createElement('AnnotationGroups')

    for each_group in category_set.keys():
        anno_group = doc.createElement('Group')
        anno_group.setAttribute('Name', "_" + str(each_group))
        anno_group.setAttribute('PartOfGroup', "None")
        anno_group.setAttribute('Color', category_set[each_group])
        attr = doc.createElement('Attributes')
        anno_group.appendChild(attr)
        AnnotationGroups.appendChild(anno_group)
    ASAP_Annotations.appendChild(AnnotationGroups)

    with open(os.path.join(output_path, xml_name), 'w') as f:
        doc.writexml(f, indent='\t', newl='\n', addindent='\t', encoding='utf-8')


def isvaild(coords, labels, threshold=0.1):
    '''
    :param coords: 切图的坐标
    :param labels: xml坐标
    :return:
    '''
    print(coords.shape, labels.shape)
    m = labels.shape[0]
    count = 0
    for each in labels:
        print(each)
        if coords[0] <= each[0] <=coords[2] and coords[1]<= each[1] <= coords[3]:
            count +=1
    print(m, count)
    return count >= int(m * threshold)


def cut(tiff_path, coords):
    slide = opsl.OpenSlide(tiff_path)
    cur_img = np.array(slide.read_region((coords[1], coords[0]), 0, (coords[3] - coords[1], coords[2] - coords[0]))
                       .convert('RGB'))
    img_name = "{}_{}.tiff".format(coords[0], coords[1])
    im = numpy2vips(cur_img)
    im.tiffsave(img_name, tile=True, compression='jpeg', bigtiff=True, pyramid=True)


if __name__ == '__main__':
    xml_path = './test.xml'
    tif_path = './2000527-1胃窦1_0.tiff'
    cut_xml([500, 3500, 3500, 8400], xml_path)
    cut(tif_path, [500, 3500, 3500, 8400])



