import numpy as np
import cv2
import ROOT
import os
import pandas as pd
import gc
import psutil  # RAM 사용량 확인
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-i","--index",dest="index",action="store")
parser.add_argument("-d","--dataset",dest="dataset",action="store")
parser.add_argument("-o","--outname",dest="outname",action="store")
args = parser.parse_args()

#def print_memory_usage(stage):
#    """현재 메모리 사용량 출력"""
#    process = psutil.Process(os.getpid())
#    mem_info = process.memory_info()
#    print(f"[{stage}] RAM 사용량: {mem_info.rss / 1024**2:.2f} MB")

def ImageResize(EEImage, ES1Image, ES2Image):
    """이미지 크기 조정 함수 (메모리 효율적으로 개선)"""
    EEImageResize = cv2.resize(EEImage, (EEImage.shape[1] * 14, EEImage.shape[0] * 14), interpolation=cv2.INTER_NEAREST)
    ES1ImageResize = cv2.resize(ES1Image, (ES1Image.shape[1] * 32, ES1Image.shape[0]), interpolation=cv2.INTER_NEAREST)
    ES1ImageResize = np.pad(ES1ImageResize,pad_width = 1,mode='constant')
    #print(ES1ImageResize.shape)

    ES2ImageResize = cv2.resize(ES2Image, (ES2Image.shape[1], ES2Image.shape[0] * 32), interpolation=cv2.INTER_NEAREST)
    ES2ImageResize = np.pad(ES2ImageResize,pad_width = 1,mode='constant')
    #print(ES2ImageResize.shape)
    #print(EEImageResize.shape)
    # 정규화 및 스택
    EEImageResize = (EEImageResize / EEImageResize.max()) * 255 if EEImageResize.max() != 0 else EEImageResize
    ES1ImageResize = (ES1ImageResize / ES1ImageResize.max()) * 255 if ES1ImageResize.max() != 0 else ES1ImageResize
    ES2ImageResize = (ES2ImageResize / ES2ImageResize.max()) * 255 if ES2ImageResize.max() != 0 else ES2ImageResize
    total_img = np.stack((EEImageResize, ES1ImageResize, ES2ImageResize), axis=2)
    del EEImageResize, ES1ImageResize, ES2ImageResize
    gc.collect()

    return total_img
    
# ROOT 파일 읽기
dataset = args.dataset
outname = args.outname
fp = open("./input/"+outname+"/"+dataset+".dat","r")
index = int(args.index)
filelist = []
for line in fp:
    line = line.strip()
    filelist.append(line)
print(filelist[index])
inputfile = filelist[index]
f1 = ROOT.TFile.Open(inputfile)
t = f1.Get('mergedLeptonIDImage/ImageTree')

# 데이터 저장 리스트
t.SetBranchStatus("*", 0)
t.SetBranchStatus("EEImage", 1)
t.SetBranchStatus("ES1Image", 1)
t.SetBranchStatus("ES2Image", 1)
t.SetBranchStatus("NumEle", 1)
t.SetBranchStatus("NumEleHard", 1)
t.SetBranchStatus("IsAddTrk", 1)
t.SetBranchStatus("IsEleCleaningID", 1)
t.SetBranchStatus("dPhi",1)
t.SetBranchStatus("dEta",1)

# 출력 폴더 생성
output_dir = f'/pnfs/knu.ac.kr/data/cms/store/user/yeo/ImageDataMergedEle/{outname}/{dataset}/{dataset}_{index}/'

csv_path = f"/pnfs/knu.ac.kr/data/cms/store/user/yeo/ImageDataMergedEle/{outname}/{dataset}/{dataset}_{index}.csv"
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
    
    EEarray = np.array([list(row) for row in t.EEImage], dtype=np.float32)
    ES1array = np.array([list(row) for row in t.ES1Image], dtype=np.float32)
    ES2array = np.array([list(row) for row in t.ES2Image], dtype=np.float32)

    dEta = np.array(t.dEta,dtype=np.float32)
    dPhi = np.array(t.dPhi,dtype=np.float32)

    # ROOT 배열을 NumPy 배열로 변환 (메모리 효율적)
    #EEarray = np.array([[t.EEImage[i][j] for j in range(len(t.EEImage[i]))] for i in range(len(t.EEImage))], dtype=np.float64,copy = True)
    #ES1array = np.array([[t.ES1Image[i][j] for j in range(len(t.ES1Image[i]))] for i in range(len(t.ES1Image))], dtype=np.float64,copy = True)
    #ES2array = np.array([[t.ES2Image[i][j] for j in range(len(t.ES2Image[i]))] for i in range(len(t.ES2Image))], dtype=np.float64,copy = True)

    #print_memory_usage(f"Numpy {idx} ")  # 메모리 확인
    # 이미지 크기 조정
    img = ImageResize(EEarray, ES1array, ES2array)

    #print_memory_usage(f"resize {idx} ")  # 메모리 확인
    # 이미지 저장
    file_path = os.path.join(output_dir, f"Image_{idx}.png")
    cv2.imwrite(file_path, img)

    #print_memory_usage(f"write img {idx} ")  # 메모리 확인
    del EEarray, ES1array, ES2array, img
    gc.collect()
    #print_memory_usage(f"remove memory {idx} ")  # 메모리 확인


    # 데이터 저장
    if t.NumEleHard > 1 and t.IsEleCleaningID == 0:
        label = 'mergedHard'
    elif t.NumEleHard == 1:
        label = 'notMerged'
    else:
        label = 'notElectron'
    
    data.append([t.NumEle, t.NumEleHard, t.IsAddTrk, file_path, label, dPhi, dEta])
    # 일정 개수마다 CSV로 저장 후 리스트 초기화
    #if idx % 1000 == 0:
    #    print(str(idx)+" evts process")
    #    del t
    #    f1.Close()
    #    f1 = ROOT.TFile(inputfile, 'READ')
    #    t = f1.Get('mergedLeptonIDImage/ImageTree')
    #    t.SetBranchStatus("*", 0)
    #    t.SetBranchStatus("EEImage", 1)
    #    t.SetBranchStatus("ES1Image", 1)
    #    t.SetBranchStatus("ES2Image", 1)
    #    t.SetBranchStatus("NumEle", 1)
    #    t.SetBranchStatus("NumEleHard", 1)
    #    t.SetBranchStatus("IsAddTrk", 1)
    #    #print_memory_usage(f"ROOT 파일 다시 열기 {idx}")

    #if len(data) >= batch_size:
    #    df = pd.DataFrame(data, columns=['NumEle', 'NumEleHard', 'IsAddTrk', 'ImagePath', 'Label'])
    #    df.to_csv(csv_path, mode='a', header=False, index=False)
    #    data = []  # 리스트 초기화
    #    gc.collect()  # 메모리 해제
    #    print("data processing...")
    

# 데이터프레임 생성 및 저장
if data:
    df = pd.DataFrame(data, columns=['NumEle', 'NumEleHard', 'IsAddTrk', 'IsEleCleaningID', 'ImagePath', 'Label', 'dPhi', 'dEta'])
    df.to_csv(csv_path, mode='a', header=False, index=False)

# ROOT 파일 닫기
f1.Close()
gc.collect()
print("Processing complete. Images and metadata saved.")

