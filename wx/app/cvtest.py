import cv2
import numpy as np
import pytesseract
import os
from queue import Queue
from fnmatch import fnmatch

pytesseract.pytesseract.tesseract_cmd = 'D:\\tesseract\\Tesseract-OCR\\tesseract.exe'


def clean_bg(filename):
    #print(filename)
    #image = cv2.imread(filename,0)
    file=np.asarray(bytearray(filename),dtype='uint8')
    image=cv2.imdecode(file,0)
    #print(image[0,0])
    new_image = np.zeros(image.shape, np.uint8)
    height,width= image.shape
    img_name=filename
    for i in range(height):
        for j in range(width):
            new_image[i,j] = image[i,j]#max(image[i,j][0],image[i,j][1],image[i,j][2])

    #ret,new_image = cv2.threshold(new_image,200,255,cv2.THRESH_BINARY)
    #new_image = cv2.adaptiveThreshold(new_image,255,cv2.ADAPTIVE_THRESH_MEAN_C,\
            #cv2.THRESH_BINARY,11,2)
    new_image = cv2.adaptiveThreshold(new_image,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,\
            cv2.THRESH_BINARY,11,2)
    new_image=interference_line(new_image,'22')
    new_image=interference_point(new_image,'22')
    #new_image=interference_point(new_image,'22')
    #new_image=interference_line(new_image,'22')
    #new_image=interference_line(new_image,'22')
    #cv2.imshow('invImage',new_image)
    #cv2.waitKey(0)
    #border_width = 2
    #new_image = new_image[border_width:height-border_width,border_width:width-border_width]
    #cv2.imshow('invImage',new_image)
    #cv2.waitKey(0)
    #cv2.imwrite('testt.png',new_image)
    #cv2.destroyAllWindows()
  
    c=pytesseract.image_to_string(new_image)
    #print(c)
    #cv2.imshow('IMage',new_image)
    #cv2.waitKey(0)
    #cv2.destroyAllWindows()
    alphabet='01234567890qwertyuiopasdfghjklzxcvbnm'
    # error level 切换验证码 并不提交
    
    if(len(c)<4):
      return 1
    c=c.replace(' ','')
    c=c.replace('“','W')
    c=c.replace('-','')
    for cc in c:
      if cc.lower() not in alphabet:
        c=c.replace(cc,'')
    if(len(c)<4):
      return 1
    #print('C:',c)
    if(len(c)>4):
      c=c[0:4]
    return c

def interference_line(img, img_name):
  '''
  干扰线降噪
  '''

  filename =  './out_img/1-interferenceline.jpg'
  h, w = img.shape[:2]
  # ！！！opencv矩阵点是反的
  # img[1,2] 1:图片的高度，2：图片的宽度
  for y in range(1, w - 1):
    for x in range(1, h - 1):
      count = 0
      if img[x, y - 1] > 245:
        count = count + 1
      if img[x, y + 1] > 245:
        count = count + 1
      if img[x - 1, y] > 245:
        count = count + 1
      if img[x + 1, y] > 245:
        count = count + 1
      if count > 2:
        img[x, y] = 255
  cv2.imwrite(filename,img)
  return img
def interference_point(img,img_name, x = 0, y = 0):
    """点降噪
    9邻域框,以当前点为中心的田字框,黑点个数
    :param x:
    :param y:
    :return:
    """
    #filename =  './out_img/' + img_name.split('.')[0] + '-interferencePoint.jpg'
    # todo 判断图片的长宽度下限
    cur_pixel = img[x,y]# 当前像素点的值
    height,width = img.shape[:2]

    for y in range(0, width - 1):
      for x in range(0, height - 1):
        if y == 0:  # 第一行
            if x == 0:  # 左上顶点,4邻域
                # 中心点旁边3个点
                sum = int(cur_pixel) \
                      + int(img[x, y + 1]) \
                      + int(img[x + 1, y]) \
                      + int(img[x + 1, y + 1])
                if sum <= 2 * 245:
                  img[x, y] = 0
            elif x == height - 1:  # 右上顶点
                sum = int(cur_pixel) \
                      + int(img[x, y + 1]) \
                      + int(img[x - 1, y]) \
                      + int(img[x - 1, y + 1])
                if sum <= 2 * 245:
                  img[x, y] = 0
            else:  # 最上非顶点,6邻域
                sum = int(img[x - 1, y]) \
                      + int(img[x - 1, y + 1]) \
                      + int(cur_pixel) \
                      + int(img[x, y + 1]) \
                      + int(img[x + 1, y]) \
                      + int(img[x + 1, y + 1])
                if sum <= 3 * 245:
                  img[x, y] = 0
        elif y == width - 1:  # 最下面一行
            if x == 0:  # 左下顶点
                # 中心点旁边3个点
                sum = int(cur_pixel) \
                      + int(img[x + 1, y]) \
                      + int(img[x + 1, y - 1]) \
                      + int(img[x, y - 1])
                if sum <= 2 * 245:
                  img[x, y] = 0
            elif x == height - 1:  # 右下顶点
                sum = int(cur_pixel) \
                      + int(img[x, y - 1]) \
                      + int(img[x - 1, y]) \
                      + int(img[x - 1, y - 1])

                if sum <= 2 * 245:
                  img[x, y] = 0
            else:  # 最下非顶点,6邻域
                sum = int(cur_pixel) \
                      + int(img[x - 1, y]) \
                      + int(img[x + 1, y]) \
                      + int(img[x, y - 1]) \
                      + int(img[x - 1, y - 1]) \
                      + int(img[x + 1, y - 1])
                if sum <= 3 * 245:
                  img[x, y] = 0
        else:  # y不在边界
            if x == 0:  # 左边非顶点
                sum = int(img[x, y - 1]) \
                      + int(cur_pixel) \
                      + int(img[x, y + 1]) \
                      + int(img[x + 1, y - 1]) \
                      + int(img[x + 1, y]) \
                      + int(img[x + 1, y + 1])

                if sum <= 3 * 245:
                  img[x, y] = 0
            elif x == height - 1:  # 右边非顶点
                sum = int(img[x, y - 1]) \
                      + int(cur_pixel) \
                      + int(img[x, y + 1]) \
                      + int(img[x - 1, y - 1]) \
                      + int(img[x - 1, y]) \
                      + int(img[x - 1, y + 1])

                if sum <= 3 * 245:
                  img[x, y] = 0
            else:  # 具备9领域条件的
                sum = int(img[x - 1, y - 1]) \
                      + int(img[x - 1, y]) \
                      + int(img[x - 1, y + 1]) \
                      + int(img[x, y - 1]) \
                      + int(cur_pixel) \
                      + int(img[x, y + 1]) \
                      + int(img[x + 1, y - 1]) \
                      + int(img[x + 1, y]) \
                      + int(img[x + 1, y + 1])
                if sum <= 4 * 245:
                  img[x, y] = 0
    #cv2.imwrite(filename,img)
    return img


#for file in os.listdir('./imgcode'):
  #print(file)
  #if file.split('.')[-1]=='png':
  #files=os.path.join('imgcode',file)
  #print(files)
  #clean_bg(files)
      


