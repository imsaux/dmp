#!/usr/bin/env python
# -*- coding:utf-8 -*-

# -*- coding: UTF-8 -*-
from PIL import Image, ImageStat, ImageEnhance
# from numpy import *
import numpy as np
import cv2
import time
import random


# 亮度增强
def linear(image, imagecount, savepath):
    im = Image.open(image)
    mode = im.mode
    # 像素增量 列表
    s = [0.5]
    for k in range(1, imagecount - 1):
        l = s[k - 1] + 1 / (imagecount - 1)
        s.append(l)
    s.append(1.5)
    if mode == 'L':
        for c in range(imagecount):
            enh_bri = ImageEnhance.Brightness(im)
            brightness = s[c]
            image_brightened = enh_bri.enhance(brightness)
            image_brightened.save(savepath + '\\' + image[:-4] + '_A_%s.jpg' % c)

    elif mode == 'RGB':
        for c in range(imagecount):
            enh_bri = ImageEnhance.Brightness(im)
            brightness = s[c]
            image_brightened = enh_bri.enhance(brightness)
            image_brightened.save(savepath + '\\' + image[:-4] + '_A_%s.jpg' % c)

def nolinear(image, imagecount, savepath):
    img = Image.open(image)
    mode=img.mode
    s = [0.5]
    for k in range(1, imagecount - 1):
        l = s[k - 1] + 1.5 / (imagecount - 1)
        s.append(l)
    s.append(2)
    if mode == 'L':
        for c in range(imagecount):
            enh_con = ImageEnhance.Contrast(img)
            contrast = s[c]
            image_contrasted = enh_con.enhance(contrast)
            image_contrasted.save(savepath + '\\' + image[:-4] + '_B_%s.jpg' % c)

    if mode == 'RGB':
        for c in range(imagecount):
            enh_con = ImageEnhance.Contrast(img)
            contrast = s[c]
            image_contrasted = enh_con.enhance(contrast)
            image_contrasted.save(savepath + '\\' + image[:-4] + '_B_%s.jpg' % c)

# 添加椒盐噪声（系数从0.01到0.11）
def SaltAndPepper(image, imagecount, savepath):
    im = Image.open(image)
    mode = im.mode
    if mode == 'L':
        SP_NoiseImg = cv2.imread(image, 0)
        # 像素增量 列表
        s = [0.01]
        for k in range(1, imagecount - 1):
            l = s[k - 1] + 0.1 / (imagecount - 1)
            s.append(l)
        s.append(0.11)
        for c in range(imagecount):
            SP_NoiseNum = int(s[c] * SP_NoiseImg.shape[0] * SP_NoiseImg.shape[1])
            for i in range(SP_NoiseNum):
                randX = random.randint(0, SP_NoiseImg.shape[0] - 1)
                randY = random.randint(0, SP_NoiseImg.shape[1] - 1)
                pix = random.randint(200, 255)
                SP_NoiseImg[randX, randY] = pix
            cv2.imwrite(savepath + '\\' + image[:-4] + '_C_%s.jpg' % c, SP_NoiseImg)
            SP_NoiseImg = cv2.imread(image, 0)

    elif mode =='RGB':
        SP_NoiseImg = cv2.imread(image, 1)
        # 像素增量 列表
        s = [0.01]
        for k in range(1,imagecount-1):
            l = s[k-1] + 0.1/(imagecount - 1)
            s.append(l)
        s.append(0.11)

        for c in range(imagecount):

            # SP_NoiseImg = cv2.imread(image, 1)
            SP_NoiseNum = int(s[c] * SP_NoiseImg.shape[0] * SP_NoiseImg.shape[1])
            # start = time.time()
            for i in range(SP_NoiseNum):
                randX = random.randint(1, SP_NoiseImg.shape[0] - 1)
                randY = random.randint(1, SP_NoiseImg.shape[1] - 1)
                SP_NoiseImg[randX, randY][0] = random.randint(200, 255)
                SP_NoiseImg[randX, randY][1] = random.randint(200, 255)
                SP_NoiseImg[randX, randY][2] = random.randint(200, 255)

            cv2.imwrite(savepath + '\\' + image[:-4] + '_C_%s.jpg' % c, SP_NoiseImg)

#  高斯滤波去噪（系数从0.5到5）
def clearNoise(image, imagecount, savepath):
    im = Image.open(image)
    mode = im.mode
    s = [0.5]
    for k in range(1, imagecount - 1):
        l = s[k - 1] + 4.5 / (imagecount - 1)
        s.append(l)
    s.append(5)
    if mode == 'RGB':
        img = cv2.imread(image, 1)
        for c in range(imagecount):
            median = cv2.GaussianBlur(img, (5, 5), s[c])
            cv2.imwrite(savepath + '\\' + image[:-4] + '_D_%s.jpg' % c, median)
    elif mode == 'L':
        img = cv2.imread(image, 0)
        for c in range(imagecount):
            median = cv2.GaussianBlur(img, (5, 5), s[c])
            cv2.imwrite(savepath + '\\' + image[:-4] + '_D_%s.jpg' % c, median)


# 主程序
def image_deal(image, processMethod, imagecount, savepath):
        if processMethod == 'A':
            linear(image, imagecount, savepath)
        elif processMethod == 'B':
            nolinear(image, imagecount, savepath)
        elif processMethod == 'C':
            SaltAndPepper(image, imagecount, savepath)
        elif processMethod == 'D':
            clearNoise(image, imagecount, savepath)

image_deal('33.jpg', 'C', 3, 'C:\\yimi\\noise')   # 文件名，操作类型，数量，保存路径