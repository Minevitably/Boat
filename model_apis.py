"""
参数与返回值统一使用opencv图片格式
输入参数为原始图片，返回值为处理后的图片
api命名格式为“ModelName + Predict”
"""
import cv2
import torch
from ultralytics import YOLO


# 下面这四个模型是小目标检测所用的模型
def Yolov10Predict(src_img):
    """
    使用Yolov10模型进行预测
    :param src_img: 原始图片
    :return: 处理后的图片
    """
    res_img = src_img

    return res_img


def Yolov11Predict(src_img):
    """
    使用Yolov11模型进行预测
    :param src_img: 原始图片
    :return: 处理后的图片
    """
    res_img = src_img
    # 检查设备
    device = 'cuda' if torch.cuda.is_available() else 'cpu'

    # 初始化模型
    # TODO: 这里可以进行性能优化，例如在程序初始化后只加载一次模型
    # 目前有多少张图片就会载入多少次模型
    model = YOLO('yolo11n.pt')  # 使用适当的模型文件

    # 进行目标检测
    results = model(src_img, device=device)  # 指定设备
    res_img = results[0].plot()  # 绘制结果

    return res_img


def DETRPredict(src_img):
    """
    使用DETR模型进行预测
    :param src_img: 原始图片
    :return: 处理后的图片
    """
    res_img = src_img

    return res_img

def RCNNPredict(src_img):
    """
    使用RCNN模型进行预测
    :param src_img: 原始图片
    :return: 处理后的图片
    """
    res_img = src_img

    return res_img

# 下面三个模型是小目标去噪使用的模型
def M1Predict(src_img):
    """
    使用M1模型进行预测
    :param src_img: 原始图片
    :return: 处理后的图片
    """
    res_img = src_img

    return res_img

def M2Predict(src_img):
    """
    使用M2模型进行预测
    :param src_img: 原始图片
    :return: 处理后的图片
    """
    res_img = src_img

    return res_img

def M3Predict(src_img):
    """
    使用M3模型进行预测
    :param src_img: 原始图片
    :return: 处理后的图片
    """
    res_img = src_img

    return res_img


# 示例使用
if __name__ == "__main__":
    # 读取原始图片
    src_image = cv2.imread('bus.jpg')

    # 进行预测
    processed_image = Yolov11Predict(src_image)

    # 显示处理后的图片
    cv2.imshow('Processed Image', processed_image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()