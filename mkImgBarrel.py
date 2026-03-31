import numpy as np
import cv2
import ROOT
import os
import pandas as pd
import gc
import psutil  # RAM 사용량 확인
import argparse
from ROOT import TChain

parser = argparse.ArgumentParser()
parser.add_argument("-i","--index",dest="index",action="store")
parser.add_argument("-d","--dataset",dest="dataset",action="store")
parser.add_argument("-o","--outname",dest="outname",action="store")
parser.add_argument("-l","--lines",dest="lines",action="store")
args = parser.parse_args()

#def print_memory_usage(stage):
#    """현재 메모리 사용량 출력"""
#    process = psutil.Process(os.getpid())
#    mem_info = process.memory_info()
#    print(f"[{stage}] RAM 사용량: {mem_info.rss / 1024**2:.2f} MB")
def ImageResize(EBImage):
    """이미지 크기 조정 함수 (메모리 효율적으로 개선)"""
    EBImageResize = cv2.resize(EBImage, (EBImage.shape[1] * 14, EBImage.shape[0] * 14), interpolation=cv2.INTER_NEAREST)

    #print(EBImageResize.shape)
    ES1ImageResize = np.zeros((98,98))
    ES2ImageResize = np.zeros((98,98))
    # 정규화 및 스택
    EBImageResize = (EBImageResize / EBImageResize.max()) * 255 if EBImageResize.max() != 0 else EBImageResize
    total_img = np.stack((EBImageResize, ES1ImageResize, ES2ImageResize), axis=2)
    del EBImageResize, ES1ImageResize, ES2ImageResize
    gc.collect()

    return total_img

# ROOT 파일 읽기
dataset = args.dataset
outname = args.outname
lines = int(args.lines)
fp = open("./input/"+outname+"/"+dataset+".dat","r")
index = int(args.index)
file_num = 10
if lines//10 == index :
    file_num = lines - index*10
filelist = []
for line in fp:
    line = line.strip()
    filelist.append(line)
t = TChain('mergedLeptonIDImage/ImageTree')


for i in range(file_num):
    print(filelist[index*10 + i])
    inputfile = filelist[index*10 +i]
    t.Add(inputfile)

#f1 = ROOT.TFile.Open(inputfile)
#t = f1.Get('mergedLeptonIDImage/ImageTree')

# 데이터 저장 리스트
t.SetBranchStatus("*", 0)
t.SetBranchStatus("EBImage", 1)
t.SetBranchStatus("NumEle", 1)
t.SetBranchStatus("NumEleHard", 1)
t.SetBranchStatus("IsAddTrk", 1)
t.SetBranchStatus("IsEleCleaningID", 1)
t.SetBranchStatus("dPhi",1)
t.SetBranchStatus("dEta",1)
t.SetBranchStatus("pT",1)
t.SetBranchStatus("genDR",1)

# 출력 폴더 생성
#output_dir = f'/pnfs/knu.ac.kr/data/cms/store/user/yeo/ImageDataMergedEle/{outname}/{dataset}/{dataset}_{index}/'
output_dir = f'/d0/scratch/eoyun/ImageDataMergedEle/{outname}/{dataset}/{dataset}_{index}/'

csv_path = f"/d0/scratch/eoyun/ImageDataMergedEle/{outname}/{dataset}/{dataset}_{index}.csv"
os.makedirs(output_dir, exist_ok=True)

#if not os.path.exists(csv_path):
#    pd.DataFrame(columns=['NumEle', 'NumEleHard', 'IsAddTrk', 'ImagePath', 'Label']).to_csv(csv_path, index=False)

# 메모리 관리 개선
batch_size = 100  # 일정 개수씩 저장하여 메모리 과부하 방지
data = []


#for idx, itree in enumerate(t):
for idx in range(t.GetEntries()):
    t.GetEntry(idx)
    if t.IsAddTrk == 0:
        continue  # 조건 만족하지 않으면 스킵
    #print_memory_usage(f"Loop {idx} 시작")  # 메모리 확인
    
    EBarray = np.array([list(row) for row in t.EBImage], dtype=np.float32)

    dEta = np.array(t.dEta,dtype=np.float32)
    dPhi = np.array(t.dPhi,dtype=np.float32)

    # ROOT 배열을 NumPy 배열로 변환 (메모리 효율적)
    #EBarray = np.array([[t.EBImage[i][j] for j in range(len(t.EBImage[i]))] for i in range(len(t.EBImage))], dtype=np.float64,copy = True)
    #ES1array = np.array([[t.ES1Image[i][j] for j in range(len(t.ES1Image[i]))] for i in range(len(t.ES1Image))], dtype=np.float64,copy = True)
    #ES2array = np.array([[t.ES2Image[i][j] for j in range(len(t.ES2Image[i]))] for i in range(len(t.ES2Image))], dtype=np.float64,copy = True)

    E5x5 = EBarray[1:6, 1:6]
    Esum = E5x5.sum()
    
    #print_memory_usage(f"Numpy {idx} ")  # 메모리 확인
    # 이미지 크기 조정
    img = ImageResize(EBarray)

    #print_memory_usage(f"resize {idx} ")  # 메모리 확인
    # 이미지 저장
    file_path = os.path.join(output_dir, f"Image_{idx}.png")
    cv2.imwrite(file_path, img)

    #print_memory_usage(f"write img {idx} ")  # 메모리 확인
    del EBarray, img
    gc.collect()
    #print_memory_usage(f"remove memory {idx} ")  # 메모리 확인


    # 데이터 저장
    if t.NumEleHard > 1 and t.IsEleCleaningID == 0:
        label = 'merged'
    elif t.NumEleHard == 1 or (t.NumEleHard > 1 and t.IsEleCleaningID == 1):
        label = 'single'
    else:
        label = 'fake'
    
    data.append([t.NumEle, t.NumEleHard, t.IsAddTrk, t.IsEleCleaningID, file_path, label, dPhi, dEta, t.pT, Esum, t.genDR])
    # 일정 개수마다 CSV로 저장 후 리스트 초기화
    #if idx % 1000 == 0:
    #    print(str(idx)+" evts process")
    #    del t
    #    f1.Close()
    #    f1 = ROOT.TFile(inputfile, 'READ')
    #    t = f1.Get('mergedLeptonIDImage/ImageTree')
    #    t.SetBranchStatus("*", 0)
    #    t.SetBranchStatus("EBImage", 1)
    #    t.SetBranchStatus("ES1Image", 1)
    #    t.SetBranchStatus("ES2Image", 1)
    #    t.SetBranchStatus("NumEle", 1)
    #    t.SetBranchStatus("NumEleHard", 1)
    #    t.SetBranchStatus("IsAddTrk", 1)
    #    #print_memory_usage(f"ROOT 파일 다시 열기 {idx}")

    if len(data) >= batch_size:
        df = pd.DataFrame(data, columns=['NumEle', 'NumEleHard', 'IsAddTrk','IsEleCleaningID', 'ImagePath', 'Label','dPhi','dEta','pT','E5x5',"dR"])
        df.to_csv(csv_path, mode='a', header=False, index=False)
        data = []  # 리스트 초기화
        gc.collect()  # 메모리 해제
        print("data processing...")
    

# 데이터프레임 생성 및 저장
if data:
    df = pd.DataFrame(data, columns=['NumEle', 'NumEleHard', 'IsAddTrk', 'IsEleCleaningID', 'ImagePath', 'Label', 'dPhi', 'dEta','pT','E5x5','dR'])
    df.to_csv(csv_path, mode='a', header=False, index=False)

# ROOT 파일 닫기
#f1.Close()
gc.collect()
print("Processing complete. Images and metadata saved.")

