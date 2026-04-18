import argparse
import gc
import os
import re

import cv2
import h5py
import numpy as np
from ROOT import TChain


parser = argparse.ArgumentParser()
parser.add_argument("-i", "--index", dest="index", action="store")
parser.add_argument("-d", "--dataset", dest="dataset", action="store")
parser.add_argument("-o", "--outname", dest="outname", action="store")
parser.add_argument("-l", "--lines", dest="lines", action="store")
args = parser.parse_args()

import cv2
import gc
import numpy as np

def normalize_image(img, method="log", out_max=255.0, q=99.5, alpha=1.0, eps=1e-12):
    img = img.astype(np.float32)

    if img.size == 0 or img.max() <= 0:
        return np.zeros_like(img, dtype=np.float32)

    if method == "max":
        denom = img.max()
        return (img / max(denom, eps)) * out_max

    elif method == "log":
        img2 = np.log1p(alpha * img)
        denom = img2.max()
        return (img2 / max(denom, eps)) * out_max

    elif method == "sqrt":
        img2 = np.sqrt(img)
        denom = img2.max()
        return (img2 / max(denom, eps)) * out_max

    elif method == "percentile":
        high = np.percentile(img, q)
        high = max(high, eps)
        img2 = np.clip(img, 0, high)
        return (img2 / high) * out_max

    elif method == "percentile_log":
        high = np.percentile(img, q)
        high = max(high, eps)
        img2 = np.clip(img, 0, high)
        img2 = np.log1p(alpha * img2)
        denom = img2.max()
        return (img2 / max(denom, eps)) * out_max

    else:
        raise ValueError(f"Unknown normalization method: {method}")


def ImageResize(EEImage, ES1Image, ES2Image, norm_method="max",alpha_n = 10000):
    EEImageResize = cv2.resize(
        EEImage,
        (EEImage.shape[1] * 14, EEImage.shape[0] * 14),
        interpolation=cv2.INTER_NEAREST
    )

    ES1ImageResize = cv2.resize(
        ES1Image,
        (ES1Image.shape[1] * 32, ES1Image.shape[0]),
        interpolation=cv2.INTER_NEAREST
    )
    ES1ImageResize = np.pad(ES1ImageResize, pad_width=1, mode='constant')

    ES2ImageResize = cv2.resize(
        ES2Image,
        (ES2Image.shape[1], ES2Image.shape[0] * 32),
        interpolation=cv2.INTER_NEAREST
    )
    ES2ImageResize = np.pad(ES2ImageResize, pad_width=1, mode='constant')

    EEImageResize = normalize_image(EEImageResize, method=norm_method, alpha = alpha_n)
    ES1ImageResize = normalize_image(ES1ImageResize, method=norm_method, alpha = alpha_n)
    ES2ImageResize = normalize_image(ES2ImageResize, method=norm_method, alpha = alpha_n)

    total_img = np.stack((EEImageResize, ES1ImageResize, ES2ImageResize), axis=2).astype(np.float64)
    print(total_img)
    del EEImageResize, ES1ImageResize, ES2ImageResize
    gc.collect()

    return total_img

def parse_mass_from_path(file_path, prefix):
    # ex) ...H500..., ...A0p4... -> 500.0, 0.4
    match = re.search(rf"{prefix}([0-9]+(?:p[0-9]+)?)", file_path)
    if not match:
        return np.nan
    token = match.group(1).replace("p", ".")
    try:
        return float(token)
    except ValueError:
        return np.nan


def append_dataset(hf, name, values, dtype=None, string=False):
    if string:
        arr = np.asarray(values, dtype=h5py.string_dtype(encoding="utf-8"))
    elif dtype is not None:
        arr = np.asarray(values, dtype=dtype)
    else:
        arr = np.asarray(values)

    if name not in hf:
        hf.create_dataset(name, data=arr, maxshape=(None,) + arr.shape[1:], chunks=True)
        return

    ds = hf[name]
    old_n = ds.shape[0]
    ds.resize((old_n + arr.shape[0],) + ds.shape[1:])
    ds[old_n:] = arr


def flush_batch(h5_path, image_batch, meta_batch):
    if not meta_batch:
        return

    batch = np.array(meta_batch, dtype=object)
    with h5py.File(h5_path, "a") as hf:
        append_dataset(hf, "images", np.asarray(image_batch, dtype=np.uint8), dtype=np.uint8)
        append_dataset(hf, "NumEle", batch[:, 0], dtype=np.int32)
        append_dataset(hf, "NumEleHard", batch[:, 1], dtype=np.int32)
        append_dataset(hf, "IsAddTrk", batch[:, 2], dtype=np.int32)
        append_dataset(hf, "IsEleCleaningID", batch[:, 3], dtype=np.int32)
        append_dataset(hf, "Label", batch[:, 4], string=True)
        append_dataset(hf, "dPhi", batch[:, 5], dtype=np.float32)
        append_dataset(hf, "dEta", batch[:, 6], dtype=np.float32)
        append_dataset(hf, "pT", batch[:, 7], dtype=np.float32)
        append_dataset(hf, "E5x5", batch[:, 8], dtype=np.float32)
        append_dataset(hf, "dR", batch[:, 9], dtype=np.float32)
        append_dataset(hf, "H_mass", batch[:, 10], dtype=np.float32)
        append_dataset(hf, "A_mass", batch[:, 11], dtype=np.float32)
        append_dataset(hf, "source_file", batch[:, 12], string=True)
        append_dataset(hf, "weight", batch[:, 13], dtype=np.float32)


def get_filelist(dat_path):
    filelist = []
    with open(dat_path, "r", encoding="utf-8") as fp:
        for line in fp:
            line = line.strip()
            if line:
                filelist.append(line)
    return filelist


def main():
    dataset = args.dataset
    outname = args.outname
    index = int(args.index)
    lines = int(args.lines)

    filelist = get_filelist(f"./input/{outname}/{dataset}.dat")

    file_num = 10
    if lines // 10 == index:
        file_num = lines - index * 10

    chain = TChain("mergedLeptonIDImage/ImageTree")
    for i in range(file_num):
        input_file = filelist[index * 10 + i]
        print(input_file)
        chain.Add(input_file)

    chain.SetBranchStatus("*", 0)
    chain.SetBranchStatus("EEImage", 1)
    chain.SetBranchStatus("ES1Image", 1)
    chain.SetBranchStatus("ES2Image", 1)
    chain.SetBranchStatus("NumEle", 1)
    chain.SetBranchStatus("NumEleHard", 1)
    chain.SetBranchStatus("IsAddTrk", 1)
    chain.SetBranchStatus("IsEleCleaningID", 1)
    chain.SetBranchStatus("dPhi", 1)
    chain.SetBranchStatus("dEta", 1)
    chain.SetBranchStatus("pT", 1)
    chain.SetBranchStatus("genDR", 1)
    chain.SetBranchStatus("weight", 1)

    output_dir = f"/d0/scratch/eoyun/ImageDataMergedEle/{outname}/{dataset}/"
    os.makedirs(output_dir, exist_ok=True)
    h5_path = os.path.join(output_dir, f"{dataset}_{index}.h5")

    batch_size = 100
    image_batch = []
    meta_batch = []

    for evt in range(chain.GetEntries()):
        chain.GetEntry(evt)
        if chain.IsAddTrk == 1:
            continue

        ee = np.array([list(row) for row in chain.EEImage], dtype=np.float32)
        es1 = np.array([list(row) for row in chain.ES1Image], dtype=np.float32)
        es2 = np.array([list(row) for row in chain.ES2Image], dtype=np.float32)

        e5x5 = ee[1:6, 1:6].sum()
        img = ImageResize(ee, es1, es2)

        source_file = chain.GetCurrentFile().GetName() if chain.GetCurrentFile() else ""
        h_mass = parse_mass_from_path(source_file, "H")
        a_mass = parse_mass_from_path(source_file, "A")

        if chain.NumEleHard > 1 and chain.IsEleCleaningID == 0:
            label = "mergedHard"
        elif chain.NumEleHard == 1 or (chain.NumEleHard > 1 and chain.IsEleCleaningID == 1):
            label = "notMerged"
        else:
            label = "notElectron"

        image_batch.append(img)
        meta_batch.append(
            [
                chain.NumEle,
                chain.NumEleHard,
                chain.IsAddTrk,
                chain.IsEleCleaningID,
                label,
                np.array(chain.dPhi, dtype=np.float32),
                np.array(chain.dEta, dtype=np.float32),
                chain.pT,
                e5x5,
                chain.genDR,
                h_mass,
                a_mass,
                source_file,
                chain.weight,
            ]
        )

        del ee, es1, es2, img
        gc.collect()

        if len(meta_batch) >= batch_size:
            flush_batch(h5_path, image_batch, meta_batch)
            image_batch = []
            meta_batch = []
            gc.collect()
            print("data processing... (saved to hdf5)")

    flush_batch(h5_path, image_batch, meta_batch)
    gc.collect()
    print(f"Processing complete. Images and metadata saved to {h5_path}")


if __name__ == "__main__":
    main()
