# Roboflow-to-SSD training tool

## About This tool

This is quick guide of training custom object detection models that runs on your FRC Robot's NVIDIA Jetson Co-processors.
Tools Used:
- [Roboflow](https://roboflow.com/)
- [Jetson-Inference](https://github.com/dusty-nv/jetson-inference)

### Step 1: Collect your DataSet

To Collect your own dataset On RobotFlow, please follow [This Guide](https://docs.roboflow.com/datasets/create-a-project).  For this tutorial, we will be using [this](https://universe.roboflow.com/michael-jansen/frc-2024-tlxdn) open source dataset. 

### Step 2: Download Dataset
- Click Download button
![alt text](<./docs/roboflow project page.png>)
- Select Pascal VOC
![alt text](<docs/export menu.png>)
- Select Download Zip To This Computer
![alt text](<docs/download button.png>)
- Unzip the file, you should see:
![alt text](<docs/dataset dir.png>)

### Step 3: Prepare Jetson Inference On Jetson
Follow [This Guide](https://github.com/dusty-nv/jetson-inference/blob/master/docs/jetpack-setup-2.md) or open ~/jetson-inference on an [Phantom Jetson]()
### (Optinal) Prepare WSL For Better GPU Performance During Training
- Prepare a Computer with NVIDIA Graphics Card (recommend rtx2060 or newer) and Windows11 System.
- To Install Windows Subsystem For Linux, follow [This Guide](https://learn.microsoft.com/en-us/windows/wsl/install).
- Install [Ubuntu from Microsoft Store](https://apps.microsoft.com/detail/9pn20msr04dw?hl=en-us&gl=US).

- Open Ubuntu ![alt text](<docs/ubuntu on windows.png>)![alt text](docs/ubuntu.png)

- NVIDIA Drivers are pre-installed on WSL, type nvidia-smi and you should see this:![alt text](docs/nvidiasmi.png)

- Download [CUDA](https://developer.nvidia.com/cuda-downloads) and install.

- Install Python
```
sudo apt update && sudo apt upgrade
sudo apt install python3
```

- Install [Pytorch](https://pytorch.org/) Cuda
```
pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

- Get Jetson Inference
```
git clone --recursive --depth=1 https://github.com/dusty-nv/jetson-inference
```

- To move dataset directory to WSL, open File Explorer and type 
```
\\wsl$
```
![alt text](<docs/wsl directory.png>)

### Organizing dataset

```
cd jetson-inference/python/training/detection/ssd/

mkdir Annotations JPEGImages

mv [path to dataset]/train/*.jpg ./JPEGImages

mv [path to dataset]/train/*.xml ./Annotations



```