import os
import json
from xml.dom.minidom import Document

label_path = './data'
label_name = 'data.json'
with open(os.path.join(label_path, label_name), 'r') as f:
    labels = json.load(f)
print(len(labels['annotations']))

category_set = set()
cmap = ["#00AA00", "#FFFF33", "#FF0000", "#0000CC", "#FF00FF", "#BB5500", "#007799"]
doc = Document()
'''
<ASAP_Annotations>
'''
ASAP_Annotations = doc.createElement('ASAP_Annotations')
doc.appendChild(ASAP_Annotations)
'''
<Annotations>
'''
Annotations = doc.createElement('Annotations')


for each_anno in labels['annotations']:
    anno = doc.createElement('Annotation')
    anno.setAttribute('Name', str(each_anno['id']))
    anno.setAttribute('Type', "Polygon")
    anno.setAttribute('PartOfGroup', "_" + str(each_anno['category_id']))
    category_set.add(each_anno['category_id'])
    anno.setAttribute('Color', cmap[int(each_anno['category_id'])])
    Annotations.appendChild(anno)
    coords = doc.createElement('Coordinates')
    anno.appendChild(coords)
    for id, each_coord in enumerate(each_anno['segmentation']):
        coord = doc.createElement('Coordinate')
        coord.setAttribute('Order', str(id))
        coord.setAttribute('X', str(round(2*each_coord[0], 4)))
        coord.setAttribute('Y', str(round(2*each_coord[1], 4)))
        coords.appendChild(coord)
ASAP_Annotations.appendChild(Annotations)
'''
<AnnotationGroups>
'''
AnnotationGroups = doc.createElement('AnnotationGroups')

for each_group in category_set:
    anno_group = doc.createElement('Group')
    anno_group.setAttribute('Name', "_" + str(each_group))
    anno_group.setAttribute('PartOfGroup', "None")
    anno_group.setAttribute('Color', cmap[each_group])
    attr = doc.createElement('Attributes')
    anno_group.appendChild(attr)
    AnnotationGroups.appendChild(anno_group)
ASAP_Annotations.appendChild(AnnotationGroups)

with open(os.path.join(label_path, 'label.xml'), 'w') as f:
    doc.writexml(f, indent='\t', newl='\n', addindent='\t', encoding='utf-8')

