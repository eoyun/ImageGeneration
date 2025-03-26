import numpy as np
import cv2
import ROOT
import pandas as pd

def ImageResize( EEImage,ES1Image,ES2Image) :
    tile = np.ones((14, 14), dtype=int)
    EEImageResize = np.kron(EEImage,tile)
    #print(EEImageResize.max())
    EEImageResize = EEImageResize/EEImageResize.max()*255
    #print(EEImageResize.max())
    tile = np.ones((1, 32), dtype=int)
    ES1ImageResize = np.kron(ES1Image,tile)
    ES1ImageResize = np.pad(ES1ImageResize,pad_width = 1,mode='constant')
    ES1ImageResize = ES1ImageResize/ES1ImageResize.max()*255
    #print(ES1ImageResize.max())
    tile = np.ones((32, 1), dtype=int)
    ES2ImageResize = np.kron(ES2Image,tile)
    ES2ImageResize = np.pad(ES2ImageResize,pad_width = 1,mode='constant')
    ES2ImageResize = ES2ImageResize/ES2ImageResize.max()*255
    #print(ES2ImageResize.max())
    totalArray = np.stack((EEImageResize,ES1ImageResize,ES2ImageResize),axis = 2 )
    #print(totalArray.shape)
    return totalArray

inputfile = 'signal22EE'

f1 = ROOT.TFile(inputfile+'.root','read')

t = f1.Get('mergedLeptonIDImage/ImageTree')

idx =0

numEle = []
numHardEle = []
isAddTrk = []
imgPath = []
label = []
for itree in t:
    #print(itree.EEImage)
    EEarray = np.array([[itree.EEImage[i][j] for j in range(len(itree.EEImage[i]))] for i in range(len(itree.EEImage))], dtype=np.float64)
    ES1array = np.array([[itree.ES1Image[i][j] for j in range(len(itree.ES1Image[i]))] for i in range(len(itree.ES1Image))], dtype=np.float64)
    ES2array = np.array([[itree.ES2Image[i][j] for j in range(len(itree.ES2Image[i]))] for i in range(len(itree.ES2Image))], dtype=np.float64)
    #print(ES1array)
    img = ImageResize(EEarray,ES1array,ES2array)
    #if (idx != 0 ):
    #    break
    #for i in img:
    #    for j in i:
            #print(j)
    file_path = './data/'+inputfile+'/'+inputfile+ str(idx)+'.png'
    #for i in cv2.imread(file_path) :
    #    for j in i:
            #print(j)
    #print(cv2.imread(file_path)[:,:,1].max())
    #print(img[:,:,1].max())
    if itree.IsAddTrk != 1 :
        continue
    #hello = itree.numEle
    #print(hello)
    numEle.append(itree.NumEle)
    numHardEle.append(itree.NumEleHard)
    isAddTrk.append(itree.IsAddTrk)
    imgPath.append(file_path)
    if itree.NumEleHard > 1 :
        label.append('mergedHard')
    elif itree.NumEle > 1 :
        label.append('mergedNotHard')
    elif itree.NumEle == 1 :
        label.append('notMerged')
    elif itree.NumEle == 0 :
        label.append('notElectron')

    idx = idx + 1
    cv2.imwrite(file_path,img)

    #print(i.ES1Image)
    #print(i.ES2Imagei)
df = pd.DataFrame({
    "numEle" : numEle,
    "numHardEle" : numHardEle,
    "isAddTrk" : isAddTrk,
    "imgPath" : imgPath,
    "label" : label,
})
print(df)
df.to_csv(inputfile+".csv")

