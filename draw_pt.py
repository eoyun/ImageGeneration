import numpy as np
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

output_dir = f'/d0/scratch/eoyun/pT_dist/{outname}/{dataset}/{dataset}_{index}/'
os.makedirs(output_dir, exist_ok=True)

f1 = ROOT.TFile.Open(output_dir+"test_"+str(index)+".root","recreate")

#t = f1.Get('mergedLeptonIDImage/ImageTree')
h_RE_pT = ROOT.TH1D("h_RE_pT","",1000,0,10000)
h_ME_pT = ROOT.TH1D("h_ME_pT","",1000,0,10000)
h_FE_pT = ROOT.TH1D("h_FE_pT","",1000,0,10000)

h_RE_E5x5 = ROOT.TH1D("h_RE_E5x5","",1000,0,10000)
h_ME_E5x5 = ROOT.TH1D("h_ME_E5x5","",1000,0,10000)
h_FE_E5x5 = ROOT.TH1D("h_FE_E5x5","",1000,0,10000)

# 데이터 저장 리스트
t.SetBranchStatus("*", 0)
t.SetBranchStatus("EEImage", 1)
t.SetBranchStatus("NumEleHard", 1)
t.SetBranchStatus("IsAddTrk", 1)
t.SetBranchStatus("IsEleCleaningID", 1)
t.SetBranchStatus("pT")

# 출력 폴더 생성
#output_dir = f'/pnfs/knu.ac.kr/data/cms/store/user/yeo/ImageDataMergedEle/{outname}/{dataset}/{dataset}_{index}/'


#if not os.path.exists(csv_path):
#    pd.DataFrame(columns=['NumEle', 'NumEleHard', 'IsAddTrk', 'ImagePath', 'Label']).to_csv(csv_path, index=False)

# 메모리 관리 개선
batch_size = 100  # 일정 개수씩 저장하여 메모리 과부하 방지
data = []


#for idx, itree in enumerate(t):
for idx in range(t.GetEntries()):
    t.GetEntry(idx)
    if t.IsAddTrk == 1:
        continue  # 조건 만족하지 않으면 스킵
    #print_memory_usage(f"Loop {idx} 시작")  # 메모리 확인
    if idx%10000 == 0 :
        print(str(idx)+" processing")
    
    EEarray = np.array([list(row) for row in t.EEImage], dtype=np.float32)

    E5x5 = EEarray[1:6, 1:6]
    Esum = E5x5.sum()

    if t.NumEleHard > 1 and t.IsEleCleaningID == 0:
        h_ME_pT.Fill(t.pT)
        h_ME_E5x5.Fill(Esum)
    if t.NumEleHard == 1:
        h_RE_pT.Fill(t.pT)
        h_RE_E5x5.Fill(Esum)
    if t.NumEleHard == 0:
        h_FE_pT.Fill(t.pT)
        h_FE_E5x5.Fill(Esum)

    # ROOT 배열을 NumPy 배열로 변환 (메모리 효율적)
    #EEarray = np.array([[t.EEImage[i][j] for j in range(len(t.EEImage[i]))] for i in range(len(t.EEImage))], dtype=np.float64,copy = True)
    #ES1array = np.array([[t.ES1Image[i][j] for j in range(len(t.ES1Image[i]))] for i in range(len(t.ES1Image))], dtype=np.float64,copy = True)
    #ES2array = np.array([[t.ES2Image[i][j] for j in range(len(t.ES2Image[i]))] for i in range(len(t.ES2Image))], dtype=np.float64,copy = True)

    #print_memory_usage(f"Numpy {idx} ")  # 메모리 확인
    # 이미지 크기 조정

    #print_memory_usage(f"resize {idx} ")  # 메모리 확인
    # 이미지 저장

    #print_memory_usage(f"write img {idx} ")  # 메모리 확인
    #print_memory_usage(f"remove memory {idx} ")  # 메모리 확인


    

    
h_ME_pT.Write()
h_RE_pT.Write()
h_FE_pT.Write()
h_ME_E5x5.Write()
h_RE_E5x5.Write()
h_FE_E5x5.Write()
# 데이터프레임 생성 및 저장
f1.Close()
print("Processing complete. root file saved.")

