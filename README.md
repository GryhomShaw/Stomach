# Stomach
- **运行程序** \
  `python cut_image.py -i='your input' -o='your output'`
- **参数说明** \
    -i: 表示数据文件的根目录(默认为'./dataset') \
    -o: 表示文件的输出目录(默认为'./output') \
    -c: 每张大图能够小图数量的上限(默认为12)\
    -p: 每张小图在缩略图中的最大边长(默认为60像素)
    -ps: 线程数量(默认为1)
 - **输出目录格式** 
    - 第一级目录为输出的根目录 
    - 第二级目录表示大图的文件名 
    - 第三级目录表示生成的tiff小图，命名规则为文件名_序号。(color.jpg表示小图在缩略图的位置，便于查看切割效果)
 ![Alt text](https://github.com/GryhomShaw/Stomach/blob/master/temp.png) 
 
