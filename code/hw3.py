__author__ = 'shuoy'
import cv2

import numpy as np
import math
import random

FileImage = "..//data//ncc-imagePt.txt"
FileWord = "..//data//ncc-worldPt.txt"
FileRANSAC = "..//data//RANSAC.config"

def fetchRANSACData(file):
    fd = open(file)
    Mat = list()
    Line = fd.readline()
    while Line:
        iList = Line.split('=')
        Mat.append(iList[1])
        Line = fd.readline()
    return Mat

def fetchPoints(File):
    PointMat = list()
    fd = open(File)
    PointAccount = fd.readline()
    Line = fd.readline()
    while Line :
        row  = Line.split()
        if (File == FileImage) :
            coordinates = (float(row[0]), float(row[1]), 1)
            PointMat.append(coordinates)
        if (File == FileWord) :
            coordinates = (float(row[0]), float(row[1]), float(row[2]), 1)
            PointMat.append(coordinates)
        Line = fd.readline()

    return PointMat

def LoadDataFromFile(FileImage, FileWord,FileRANSAC) :
    imgPoints = fetchPoints(FileImage)
    worldPoints = fetchPoints(FileWord)
    paraPansac = fetchRANSACData(FileRANSAC)

    return imgPoints, worldPoints, paraPansac

def ExactRansacParameter(ParaRANSAC) :
    prob = float(ParaRANSAC[0])
    SamplePoints = int(ParaRANSAC[1])
    kMax = int(ParaRANSAC[2])
    TimesOfSample = int(ParaRANSAC[3])
    default_w = float(ParaRANSAC[4])
    threshold = float(ParaRANSAC[5])

    return prob, SamplePoints, kMax, TimesOfSample, default_w,threshold

def RandomIndex(WorldPoints) :
    MaxLen = len(WorldPoints)
    Index = random.sample(range(0, MaxLen), SamplePoints)

    return Index

def SampleNewPointsSets(ImagePoints,WorldPoints):

    SImagePoints = list()
    SWorldPoints = list()

    IndexList = RandomIndex(WorldPoints)

    for i in range(0, IndexList.__len__(),1) :
        SImagePoints.append(ImagePoints[IndexList[i]])
        SWorldPoints.append(WorldPoints[IndexList[i]])

    return SImagePoints, SWorldPoints

def buildMatrix(wpt, imgpt) :

    a = np.zeros((2*len(wpt),12))
    for i in range (0,2*len(wpt),1):
            p=i/2
            if i%2 ==0:
                a[i][0:4] = wpt[p]
                a[i][4:8] = 0
                a[i][8] = -imgpt[p][0]*wpt[p][0]
                a[i][9] = -imgpt[p][0]*wpt[p][1]
                a[i][10] = -imgpt[p][0]*wpt[p][2]
                a[i][11] = -imgpt[p][0]*wpt[p][3]

            if i%2 !=0:
                a[i][0:4] = 0
                a[i][4:8] = wpt[p]

                a[i][8] = -imgpt[p][1]*wpt[p][0]
                a[i][9] = -imgpt[p][1]*wpt[p][1]
                a[i][10] = -imgpt[p][1]*wpt[p][2]
                a[i][11] = -imgpt[p][1]*wpt[p][3]

    return a

def CaculateSvd(matA) :
    U, s, Vh = np.linalg.svd(matA)

    lastV = Vh[-1]

    m = np.zeros((3,4))
    for i in range(0,3,1):
        for j in range(0,4,1):
            m[i][j] = lastV[i*4+j]

    a3t=list(m[2][0:3])
    a3=np.transpose(a3t)
    ro = 1/np.linalg.norm(a3)
    return ro*m

def distance(p1,p2):
    return math.sqrt(math.pow(p1[0]-p2[0],2)+math.pow(p1[1]-p2[1],2))

def middle(d):
    length = len(d)
    d1 = list(d)
    d1.sort()
    return d1[length/2]

def fitInliers(matM, allWorldPoints, allImagePoints):
    error=list()
    length = len(allWorldPoints)
    inlierList = list()
    for i in range(0,length,1):
        imgpt=np.dot(matM, allWorldPoints[i])
        imgpt[0] = imgpt[0]/imgpt[2]
        imgpt[1] = imgpt[1]/imgpt[2]
        error.append(distance(imgpt,allImagePoints[i]))
    med = threshold*middle(error)
    for i in range(0,length,1):
        if error[i]<med:
            inlierList.append(i)
    return inlierList

def CaculateRANSACParameter(inlierList, WorldPoints, NumPoints) :
    w = float(len(inlierList))/float(len(WorldPoints))
    k = math.log(1-probability)/math.log(1-math.pow(w,NumPoints))

    return w, k

def FetchInlierPoints(inlierList,WorldPoints, ImagePoints ):
    ImgPT =list()
    WordPT = list()

    for n in range(0,inlierList.__len__(),1):
        ImgPT.append(ImagePoints[inlierList[n]])
        WordPT.append(WorldPoints[inlierList[n]])

    return ImgPT,WordPT

def CalculateCameraParameter(MatM) :
    a1t=list(MatM[0][0:3])
    a2t=list(MatM[1][0:3])
    a3t=list(MatM[2][0:3])
    bt=list((MatM[0][3],MatM[1][3],MatM[2][3]))

    a1=np.transpose(a1t)
    a2=np.transpose(a2t)
    a3=np.transpose(a3t)
    b=np.transpose(bt)
    b3=b[-1]

    rho = 1/np.linalg.norm(a3)
    rho2power = math.pow(rho,2)
    u0= rho2power*np.vdot(a1,a3)
    v0= rho2power*np.vdot(a2,a3)

    alphaV= math.sqrt(rho2power*np.vdot(a2,a2)-math.pow(v0,2))
    s=(math.pow(rho2power,2)/alphaV)*np.dot(np.cross(a1,a3),np.cross(a2,a3))
    if(s < 0.0001) :
        s = 0

    alphaU=math.sqrt(rho2power*np.dot(a1,a1)-math.pow(s,2)-math.pow(u0,2))
    Kstar=([alphaV,s,u0],[0,alphaU,v0],[0,0,1])
    epsilon=np.sign(b3)

    Tstar=epsilon*rho*np.dot(np.linalg.inv(Kstar),b)
    r3=rho*epsilon*a3
    r1= rho2power/alphaV*np.cross(a2,a3)
    r2=np.cross(r3,r1)

    RstarT=[np.transpose(r1),np.transpose(r2),np.transpose(r3)]
    Rstar=np.transpose(RstarT)

    error=list()
    length = len(WorldPoints)
    inlierList = list()
    for i in range(0,length,1):
        imgpt=np.dot(MatM, WorldPoints[i])
        imgpt[0] = imgpt[0]/imgpt[2]
        imgpt[1] = imgpt[1]/imgpt[2]
        error.append(distance(imgpt,WorldPoints[i]))

    print("error", error)
    print("K*", Kstar)
    print("T*", Tstar)
    print("R*", RstarT)
    print("s",s)
    print("u0",u0)
    print("v0",v0)
    print("AlphaU",alphaU)
    print("AlphaV",alphaV)


def BuildModel(ImagePoints, WorldPoints):
    inlierList = []

    k = math.log(1-probability) / math.log(1-math.pow(default_w, SamplePoints))
    i = 0

    while (i < k):
        i+=1
        SImagePoints, SWorldPoints = SampleNewPointsSets(ImagePoints,WorldPoints)
        matA = buildMatrix(SWorldPoints, SImagePoints)
        matM = CaculateSvd(matA)
        inlierList1 = fitInliers(matM,WorldPoints, ImagePoints )
        InlierImgPT, InlierWrPT = FetchInlierPoints(inlierList1,WorldPoints, ImagePoints )

        matA = buildMatrix(InlierWrPT, InlierImgPT)
        matM = CaculateSvd(matA)

        inlierList2 = fitInliers(matM,WorldPoints, ImagePoints )
        w, k = CaculateRANSACParameter(inlierList2, WorldPoints, SamplePoints)

        if (k > kMax):
            break

    return matM

# Main Function
ImagePoints, WorldPoints, ParaRANSAC  = LoadDataFromFile(FileImage, FileWord, FileRANSAC)
probability , SamplePoints, kMax, TimesOfSample, default_w , threshold= ExactRansacParameter(ParaRANSAC)

BestSolutionM= BuildModel(ImagePoints, WorldPoints)
CalculateCameraParameter(BestSolutionM)





