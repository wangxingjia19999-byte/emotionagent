"""
面部表情识别模块 — 使用 MediaPipe Face Mesh + 规则判断

支持的分类:
  - neutral   (平静)
  - happy     (开心)
  - sad       (悲伤)
  - surprised (惊讶)
  - angry     (愤怒)
  - fearful   (恐惧)
  - disgusted (厌恶)

基于 MediaPipe 468 个面部关键点计算几何特征，通过阈值规则进行表情分类。
"""

import logging
import math
import os
from dataclasses import dataclass
from typing import Optional

import numpy as np

logger = logging.getLogger("app")

# 模型文件路径（相对于本文件的 models 目录）
_MODEL_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models")
_MODEL_PATH = os.path.join(_MODEL_DIR, "face_landmarker.task")

# ═══════════════════════════════════════════════════════════════
# MediaPipe Face Mesh 关键点索引常量
# ═══════════════════════════════════════════════════════════════

# —— 嘴巴 ——
MOUTH_LEFT = 61       # 左嘴角
MOUTH_RIGHT = 291     # 右嘴角
MOUTH_TOP = 13        # 上唇中心 (外)
MOUTH_BOTTOM = 14     # 下唇中心 (外)
MOUTH_INNER_TOP = 12  # 上唇中心 (内)
MOUTH_INNER_BOTTOM = 16  # 下唇中心 (内)

# —— 左眼 ——
LEFT_EYE_LEFT = 33    # 外眼角
LEFT_EYE_RIGHT = 133  # 内眼角
LEFT_EYE_TOP = 159    # 上眼睑
LEFT_EYE_BOTTOM = 145 # 下眼睑

# —— 右眼 ——
RIGHT_EYE_LEFT = 362  # 内眼角
RIGHT_EYE_RIGHT = 263 # 外眼角
RIGHT_EYE_TOP = 386   # 上眼睑
RIGHT_EYE_BOTTOM = 374 # 下眼睑

# —— 眉毛 ——
LEFT_EYEBROW_OUTER = 105   # 左眉外侧
LEFT_EYEBROW_INNER = 55    # 左眉内侧
RIGHT_EYEBROW_OUTER = 334  # 右眉外侧
RIGHT_EYEBROW_INNER = 285  # 右眉内侧

# —— 鼻子 ——
NOSE_TIP = 1
NOSE_BRIDGE = 168

# —— 参考点 ——
FOREHEAD = 10  # 额头中点 (用于归一化)

# ═══════════════════════════════════════════════════════════════
# 数据结构
# ═══════════════════════════════════════════════════════════════


@dataclass
class ExpressionResult:
    label: str         # 表情标签
    label_cn: str      # 中文标签
    confidence: float  # 置信度 0-1
    features: dict     # 中间特征值 (调试用)


# ═══════════════════════════════════════════════════════════════
# 几何工具函数
# ═══════════════════════════════════════════════════════════════


def _distance(p1: np.ndarray, p2: np.ndarray) -> float:
    """两点欧氏距离"""
    return float(np.linalg.norm(p1 - p2))


def _midpoint(p1: np.ndarray, p2: np.ndarray) -> np.ndarray:
    """两点中点"""
    return (p1 + p2) / 2.0


def _normalized_distance(p1: np.ndarray, p2: np.ndarray, ref: float) -> float:
    """
    归一化距离 — 除以参考距离 (通常用人脸高度或两眼间距)
    ref 不应为 0。
    """
    return _distance(p1, p2) / ref if ref > 1e-6 else 0.0


# ═══════════════════════════════════════════════════════════════
# 特征提取器
# ═══════════════════════════════════════════════════════════════


class FacialFeatureExtractor:
    """从 468 个 MediaPipe 面部关键点中提取表情特征"""

    def __init__(self, landmarks: np.ndarray):
        """
        Args:
            landmarks: shape (468, 3) — (x, y, z) 归一化坐标 (0-1 范围)
        """
        self.lm = landmarks

    def _pt(self, idx: int) -> np.ndarray:
        """获取第 idx 个关键点的 (x, y) 坐标"""
        return self.lm[idx][:2].copy()

    # ── 归一化参考距离 (两眼外眼角间距) ──
    @property
    def eye_distance_ref(self) -> float:
        """两眼外眼角间距，用作归一化参考"""
        d = _distance(self._pt(LEFT_EYE_LEFT), self._pt(RIGHT_EYE_RIGHT))
        return d if d > 1e-6 else 1.0

    # ── 嘴巴特征 ──
    def mouth_aspect_ratio(self) -> float:
        """嘴巴纵横比 = 高度 / 宽度。越大嘴张得越开 (惊讶/恐惧)"""
        mouth_w = _distance(self._pt(MOUTH_LEFT), self._pt(MOUTH_RIGHT))
        mouth_h = _distance(self._pt(MOUTH_TOP), self._pt(MOUTH_BOTTOM))
        return mouth_h / mouth_w if mouth_w > 1e-6 else 0.0

    def mouth_inner_aspect_ratio(self) -> float:
        """内唇纵横比 — 口腔张开程度"""
        w = _distance(self._pt(MOUTH_LEFT), self._pt(MOUTH_RIGHT))
        h = _distance(self._pt(MOUTH_INNER_TOP), self._pt(MOUTH_INNER_BOTTOM))
        return h / w if w > 1e-6 else 0.0

    def mouth_corner_upturn(self) -> float:
        """
        嘴角上扬程度 (归一化)。
        正值 = 上扬 (开心)，负值 = 下垂 (悲伤)
        """
        ref = self.eye_distance_ref
        left = self._pt(MOUTH_LEFT)
        right = self._pt(MOUTH_RIGHT)
        center_y = self._pt(MOUTH_TOP)[1]

        # 计算嘴角相对上唇中点的高度差
        corner_mid_y = (left[1] + right[1]) / 2.0
        return (center_y - corner_mid_y) / ref

    def mouth_width_ratio(self) -> float:
        """嘴角宽度占人脸宽度的比例"""
        return _distance(self._pt(MOUTH_LEFT), self._pt(MOUTH_RIGHT)) / self.eye_distance_ref

    # ── 眼睛特征 ──
    def eye_aspect_ratio(self) -> float:
        """双眼平均纵横比 (EAR)。低 EAR = 眯眼/闭眼"""
        left_ear = self._single_eye_ear(LEFT_EYE_TOP, LEFT_EYE_BOTTOM,
                                         LEFT_EYE_LEFT, LEFT_EYE_RIGHT)
        right_ear = self._single_eye_ear(RIGHT_EYE_TOP, RIGHT_EYE_BOTTOM,
                                          RIGHT_EYE_LEFT, RIGHT_EYE_RIGHT)
        return (left_ear + right_ear) / 2.0

    def _single_eye_ear(self, top: int, bottom: int, left: int, right: int) -> float:
        """单只眼睛的纵横比"""
        h = _distance(self._pt(top), self._pt(bottom))
        w = _distance(self._pt(left), self._pt(right))
        return h / w if w > 1e-6 else 0.0

    def left_eye_aspect_ratio(self) -> float:
        return self._single_eye_ear(LEFT_EYE_TOP, LEFT_EYE_BOTTOM,
                                     LEFT_EYE_LEFT, LEFT_EYE_RIGHT)

    def right_eye_aspect_ratio(self) -> float:
        return self._single_eye_ear(RIGHT_EYE_TOP, RIGHT_EYE_BOTTOM,
                                     RIGHT_EYE_LEFT, RIGHT_EYE_RIGHT)

    # ── 眉毛特征 ──
    def eyebrow_position(self) -> float:
        """
        眉毛相对于眼睛的垂直位置 (归一化)。
        正值 = 眉毛抬高 (惊讶/恐惧)，负值 = 眉毛压低 (愤怒)
        """
        ref = self.eye_distance_ref

        left_brow_y = self._pt(LEFT_EYEBROW_INNER)[1]
        left_eye_y = self._pt(LEFT_EYE_TOP)[1]
        right_brow_y = self._pt(RIGHT_EYEBROW_INNER)[1]
        right_eye_y = self._pt(RIGHT_EYE_TOP)[1]

        left_diff = (left_eye_y - left_brow_y) / ref
        right_diff = (right_eye_y - right_brow_y) / ref
        return (left_diff + right_diff) / 2.0

    def eyebrow_inner_ratio(self) -> float:
        """
        内侧眉毛相对位置 (眉心区域)。
        正值 = 内侧眉毛抬起 (悲伤的特有特征：眉毛内侧抬高)
        """
        ref = self.eye_distance_ref
        # 眉毛内侧与眉毛外侧的高度差
        left_inner_y = self._pt(LEFT_EYEBROW_INNER)[1]
        left_outer_y = self._pt(LEFT_EYEBROW_OUTER)[1]
        right_inner_y = self._pt(RIGHT_EYEBROW_INNER)[1]
        right_outer_y = self._pt(RIGHT_EYEBROW_OUTER)[1]

        left_angle = (left_inner_y - left_outer_y) / ref
        right_angle = (right_inner_y - right_outer_y) / ref
        return (left_angle + right_angle) / 2.0

    # ── 鼻子 → 上唇距离 (厌恶检测) ──
    def nose_lip_distance(self) -> float:
        """鼻尖到上唇的归一化距离。缩小 = 皱鼻/厌恶"""
        d = _distance(self._pt(NOSE_TIP), self._pt(MOUTH_TOP))
        return d / self.eye_distance_ref

    # ── 综合特征字典 ──
    def extract_all(self) -> dict:
        """提取所有特征 (全部转为 Python 原生 float，避免 JSON 序列化报错)"""
        return {
            "mar": float(self.mouth_aspect_ratio()),
            "mar_inner": float(self.mouth_inner_aspect_ratio()),
            "corner_upturn": float(self.mouth_corner_upturn()),
            "mouth_width": float(self.mouth_width_ratio()),
            "ear": float(self.eye_aspect_ratio()),
            "ear_left": float(self.left_eye_aspect_ratio()),
            "ear_right": float(self.right_eye_aspect_ratio()),
            "eyebrow_pos": float(self.eyebrow_position()),
            "eyebrow_inner": float(self.eyebrow_inner_ratio()),
            "nose_lip_dist": float(self.nose_lip_distance()),
        }


# ═══════════════════════════════════════════════════════════════
# 自适应表情分类器 — 个体基线校准 + 相对偏离度评分
# ═══════════════════════════════════════════════════════════════


class AdaptiveExpressionClassifier:
    """
    自适应表情分类器。

    核心思路：每个人的面部几何不同，不应使用绝对阈值。
    改为：
    1. 首先收集 N 帧特征建立「个人基线」(假设多数帧为中性)
    2. 之后每帧与基线比较，计算偏离方向和幅度
    3. 根据 FACS 规则匹配表情

    依据面部动作编码系统 (FACS):
    - AU6 + AU12 → 开心 (脸颊提升 + 嘴角上扬)
    - AU1 + AU5 → 惊讶 (眉毛抬起 + 眼睛睁大)
    - AU1 + AU4 → 悲伤 (内侧眉毛抬起 + 眉毛压低)
    - AU4 + AU7 → 愤怒 (眉毛压低 + 眼睑紧张)
    - AU1 + AU2 + AU5 + AU25 → 恐惧 (眉毛抬起 + 眼睛睁大 + 唇分开)
    - AU9 + AU10 → 厌恶 (皱鼻 + 上唇抬起)
    """

    # 校准帧数
    CALIBRATION_FRAMES = 30

    # 用于建立基线的特征名
    FEATURE_KEYS = [
        "mar", "mar_inner", "corner_upturn", "mouth_width",
        "ear", "ear_left", "ear_right",
        "eyebrow_pos", "eyebrow_inner", "nose_lip_dist",
    ]

    def __init__(self):
        self._baseline: dict[str, float] = {}
        self._feature_history: list[dict[str, float]] = []
        self._calibrated = False

    @property
    def is_calibrated(self) -> bool:
        return self._calibrated

    def calibrate(self, features: dict[str, float]) -> bool:
        """
        喂入一帧特征进行校准。返回 True 表示校准完成。
        前 CALIBRATION_FRAMES 帧用于建立基线。
        """
        if self._calibrated:
            return True

        self._feature_history.append({k: features[k] for k in self.FEATURE_KEYS})

        if len(self._feature_history) >= self.CALIBRATION_FRAMES:
            self._compute_baseline()
            self._calibrated = True
            logger.info(
                "facial_baseline_calibrated",
                extra={"frames": len(self._feature_history), "baseline": self._baseline},
            )
            return True
        return False

    def _compute_baseline(self):
        """用中位数 (抗异常值) 计算基线"""
        for key in self.FEATURE_KEYS:
            values = sorted(f[key] for f in self._feature_history)
            n = len(values)
            self._baseline[key] = float(values[n // 2])

    def _deviation(self, features: dict[str, float], key: str) -> float:
        """计算特征相对于基线的标准差偏离 (z-score 近似)"""
        if key not in self._baseline:
            return 0.0
        # 使用 MAD (中位数绝对偏差) 做稳健归一化
        values = sorted(f[key] for f in self._feature_history)
        n = len(values)
        med = values[n // 2]
        abs_devs = sorted(abs(v - med) for v in values)
        mad = abs_devs[n // 2] if n > 0 else 0.0

        # 最小 MAD — 防止静止画面导致除以零
        # 使用中位数值的 1% 或绝对最小值作为 floor
        baseline_val = abs(self._baseline[key])
        min_mad = max(baseline_val * 0.01, 0.0001)
        if mad < min_mad:
            mad = min_mad

        return float((features[key] - self._baseline[key]) / mad)

    def classify(self, features: dict[str, float]) -> ExpressionResult:
        """
        基于基线偏离度进行表情分类。
        如果尚未校准完成，使用保守的排序比较法。
        """
        if not self._calibrated:
            return self._classify_uncalibrated(features)

        # 打印特征值 (调试用，每 50 帧打一次)
        if not hasattr(self, '_log_counter'):
            self._log_counter = 0
        self._log_counter += 1
        if self._log_counter % 50 == 0:
            logger.debug(
                "facial_features_sample",
                extra={"features": {k: round(v, 4) for k, v in features.items()}},
            )

        # 提取偏离值
        d = {
            "mar": self._deviation(features, "mar"),
            "mar_inner": self._deviation(features, "mar_inner"),
            "corner_upturn": self._deviation(features, "corner_upturn"),
            "mouth_width": self._deviation(features, "mouth_width"),
            "ear": self._deviation(features, "ear"),
            "eyebrow_pos": self._deviation(features, "eyebrow_pos"),
            "eyebrow_inner": self._deviation(features, "eyebrow_inner"),
            "nose_lip": self._deviation(features, "nose_lip_dist"),
        }

        # ── 表情模板：每个表情定义 (d_特征, 期望方向, 权重) ──
        # 方向: +1 = 高于基线得分, -1 = 低于基线得分
        # 注意图像坐标系 y 向下 → corner_upturn>0=嘴角上扬=开心
        #                    eyebrow_inner<0=内侧眉毛更高=悲伤

        def sigmoid(x, k=1.5):
            """sigmoid 平滑激活: 将偏离值映射到 (0, 1)，防溢出"""
            # 裁剪输入防止 exp 溢出
            x = max(-20.0, min(20.0, k * x))
            return 1.0 / (1.0 + math.exp(-x))

        def _score(deviations, template):
            total = 0.0
            total_weight = 0.0
            for key, direction, weight in template:
                raw = sigmoid(deviations[key] * direction, k=2.0)
                total += raw * weight
                total_weight += weight
            return total / total_weight if total_weight > 0 else 0.0

        templates = {
            "happy": [
                ("corner_upturn", +1, 3.0),   # 嘴角上扬
                ("mouth_width", +1, 1.0),      # 嘴变宽
                ("ear", -1, 1.5),               # 眼睛微眯
                ("eyebrow_pos", -1, 0.5),       # 眉毛略低
            ],
            "sad": [
                ("eyebrow_inner", -1, 2.5),     # 眉毛内侧抬高 (inner y < outer y)
                ("corner_upturn", -1, 2.5),     # 嘴角下垂
                ("mar", -1, 1.0),               # 嘴动作少
                ("ear", -1, 1.0),               # 眼睛微闭
            ],
            "surprised": [
                ("eyebrow_pos", +1, 2.5),       # 眉毛整体抬高
                ("ear", +1, 2.5),               # 眼睛睁大
                ("mar", +1, 2.0),               # 嘴张开
                ("mar_inner", +1, 1.5),         # 内嘴张开
            ],
            "angry": [
                ("eyebrow_pos", -1, 3.0),       # 眉毛压低
                ("ear", -1, 2.5),               # 眼睛眯紧
                ("mar", -1, 1.5),               # 嘴唇紧闭
                ("corner_upturn", -1, 1.0),     # 嘴角不扬
            ],
            "fearful": [
                ("ear", +1, 2.5),               # 眼睛睁大
                ("eyebrow_pos", +1, 2.0),       # 眉毛抬高
                ("mar", +1, 1.5),               # 嘴张开
                ("eyebrow_inner", -1, 1.5),     # 眉毛内侧微抬
                ("mouth_width", +1, 1.0),       # 嘴角外拉
            ],
            "disgusted": [
                ("nose_lip", -1, 3.0),          # 皱鼻 (鼻唇距离缩小)
                ("eyebrow_pos", -1, 1.5),       # 眉毛略压
                ("corner_upturn", -1, 1.0),     # 嘴角不扬
                ("mar", +1, 1.0),               # 可能微张嘴
            ],
        }

        # 计算各表情得分
        scores = {}
        for label, template in templates.items():
            scores[label] = _score(d, template)

        # 中性得分：所有偏离越小越中性
        total_deviation = sum(abs(v) for v in d.values())
        neutral_score = max(0.0, 1.0 - total_deviation / 8.0)  # 8 = 特征数
        scores["neutral"] = float(neutral_score)

        # 找最高分
        best_label = max(scores, key=scores.get)
        confidence = scores[best_label]

        # 如果最高分 < 0.35，说明不够确定，归为 neutral
        if best_label != "neutral" and confidence < 0.35:
            best_label = "neutral"
            confidence = max(scores.get("neutral", 0.3), 0.3)

        # 中文映射
        label_cn_map = {
            "neutral": "平静",
            "happy": "开心",
            "sad": "悲伤",
            "surprised": "惊讶",
            "angry": "愤怒",
            "fearful": "恐惧",
            "disgusted": "厌恶",
        }

        return ExpressionResult(
            label=best_label,
            label_cn=label_cn_map.get(best_label, best_label),
            confidence=round(confidence, 3),
            features=features,
        )

    def _classify_uncalibrated(self, features: dict[str, float]) -> ExpressionResult:
        """
        未校准时的保守分类 — 使用成对特征比较。
        避免硬编码阈值，用特征间的关系判断。
        校准完成前倾向返回 neutral，减少误判。
        """
        mar = features["mar"]
        ear = features["ear"]
        corner_upturn = features["corner_upturn"]
        eyebrow_pos = features["eyebrow_pos"]
        eyebrow_inner = features["eyebrow_inner"]
        nose_lip = features["nose_lip_dist"]
        mouth_width = features["mouth_width"]
        mar_inner = features["mar_inner"]

        # ── 每个表情的匹配度 — 越大越像 ──
        # 用特征的相对值而非绝对阈值
        scores = {}

        # 开心: 嘴角上扬 vs 下垂 → corner_upturn 相对较高
        scores["happy"] = corner_upturn * 3.0 + (mouth_width - 0.4) * 1.5 + (0.3 - ear) * 1.0

        # 悲伤: 眉毛内侧抬高(inner y↑ → eyebrow_inner↓) + 嘴角下垂
        scores["sad"] = -eyebrow_inner * 2.0 - corner_upturn * 2.5 - mar * 0.5 - ear * 0.5

        # 惊讶: 眉毛抬高 + 眼睛睁大 + 嘴张开
        scores["surprised"] = eyebrow_pos * 1.5 + ear * 1.5 + mar * 1.5 + mar_inner * 1.0

        # 愤怒: 眉毛压低 + 眼睛眯 + 嘴紧闭
        scores["angry"] = -eyebrow_pos * 2.0 - ear * 2.0 - mar * 1.0 - corner_upturn * 0.5

        # 恐惧: 眼睛睁大 + 眉毛抬高 + 嘴微张
        scores["fearful"] = ear * 1.5 + eyebrow_pos * 1.0 + mar * 1.0 + mar_inner * 1.0 - eyebrow_inner * 0.5

        # 厌恶: 皱鼻(nose_lip↓) + 眉毛压低
        scores["disgusted"] = -nose_lip * 2.5 - eyebrow_pos * 1.0 + mar * 0.5

        # 中性: 各维度接近 0 (用总分数的方差判断)
        vals = list(scores.values())
        mean_val = sum(vals) / len(vals)
        variance = sum((v - mean_val) ** 2 for v in vals) / len(vals)

        # 如果所有分数接近 (方差小)，说明没有明显情绪 → neutral
        if variance < 0.005:
            return ExpressionResult(
                label="neutral", label_cn="平静", confidence=0.6, features=features,
            )

        # softmax 转概率
        exp_vals = np.exp((np.array(vals) - max(vals)) * 5.0)  # temperature=0.2
        probs = exp_vals / exp_vals.sum()

        labels = list(scores.keys())
        best_idx = int(np.argmax(probs))
        best_label = labels[best_idx]
        confidence = float(probs[best_idx])

        # 高阈值保护 — 不够确定就 neutral
        if confidence < 0.28:
            best_label = "neutral"
            confidence = 0.4

        label_cn_map = {
            "neutral": "平静", "happy": "开心", "sad": "悲伤",
            "surprised": "惊讶", "angry": "愤怒", "fearful": "恐惧", "disgusted": "厌恶",
        }

        return ExpressionResult(
            label=best_label,
            label_cn=label_cn_map.get(best_label, best_label),
            confidence=round(min(confidence, 0.99), 3),
            features=features,
        )


# 全局分类器实例
_classifier = AdaptiveExpressionClassifier()


def classify_expression(features: dict) -> ExpressionResult:
    """表情分类 (委托给自适应分类器，保持向后兼容)"""
    return _classifier.classify(features)


def calibrate_classifier(features: dict) -> bool:
    """喂入一帧用于校准，返回 True 表示校准完成"""
    return _classifier.calibrate(features)


# ═══════════════════════════════════════════════════════════════
# 主接口 — 从图像帧检测表情
# ═══════════════════════════════════════════════════════════════


class FacialExpressionDetector:
    """面部表情检测器 (单例)"""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True

        self._face_mesh = None

    def _ensure_loaded(self):
        """延迟加载 MediaPipe (首次调用时加载) — 使用新版 Tasks API"""
        if self._face_mesh is not None:
            return

        try:
            from mediapipe.tasks.python import BaseOptions
            from mediapipe.tasks.python.vision import (
                FaceLandmarker,
                FaceLandmarkerOptions,
                RunningMode,
            )

            if not os.path.exists(_MODEL_PATH):
                raise RuntimeError(
                    f"MediaPipe 模型文件未找到: {_MODEL_PATH}\n"
                    "请从以下地址下载并放入 models/ 目录:\n"
                    "https://storage.googleapis.com/mediapipe-models/"
                    "face_landmarker/face_landmarker/float16/1/face_landmarker.task"
                )

            options = FaceLandmarkerOptions(
                base_options=BaseOptions(model_asset_path=_MODEL_PATH),
                running_mode=RunningMode.IMAGE,
                num_faces=1,
                min_face_detection_confidence=0.5,
                min_tracking_confidence=0.5,
            )
            self._face_mesh = FaceLandmarker.create_from_options(options)
            logger.info("mediapipe_face_landmarker_loaded (tasks API)")
        except ImportError:
            logger.error("mediapipe_not_installed")
            raise RuntimeError(
                "MediaPipe 未安装。请运行: pip install mediapipe"
            )

    def detect(self, image: np.ndarray) -> Optional[ExpressionResult]:
        """
        从图像帧检测面部表情。

        Args:
            image: BGR 格式图像 (H, W, 3)，来自 cv2.imdecode 或摄像头帧

        Returns:
            ExpressionResult 或 None (未检测到人脸)
        """
        self._ensure_loaded()

        import mediapipe as mp

        # MediaPipe Tasks API 需要 RGB 输入
        rgb = image[:, :, ::-1] if image.shape[-1] == 3 else image

        # 转换为 MediaPipe Image 对象
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        detection_result = self._face_mesh.detect(mp_image)

        if not detection_result.face_landmarks:
            return None

        # 只取第一张人脸
        face = detection_result.face_landmarks[0]

        # 转换为 numpy 数组 (478, 3) — 新版模型有 478 个关键点
        # 前 468 个与旧版兼容，我们的索引常量仍有效
        h, w = image.shape[:2]
        landmarks = np.array(
            [[lm.x, lm.y, lm.z] for lm in face],
            dtype=np.float32,
        )

        # 提取特征
        extractor = FacialFeatureExtractor(landmarks)
        features = extractor.extract_all()

        # 喂入校准器 (前 N 帧用于建立个人基线)
        calibrate_classifier(features)

        # 分类
        return classify_expression(features)

    def detect_from_bytes(self, image_bytes: bytes) -> Optional[ExpressionResult]:
        """从 JPEG/PNG 字节流检测"""
        import cv2
        arr = np.frombuffer(image_bytes, dtype=np.uint8)
        image = cv2.imdecode(arr, cv2.IMREAD_COLOR)
        if image is None:
            logger.warning("failed_to_decode_image")
            return None
        return self.detect(image)


# 全局单例
expression_detector = FacialExpressionDetector()


# ═══════════════════════════════════════════════════════════════
# 当前表情存储 (内存 — 供 Agent 工具读取)
# ═══════════════════════════════════════════════════════════════

# { user_id: ExpressionResult }
_current_expressions: dict[str, ExpressionResult] = {}


def store_current_expression(user_id: str, result: Optional[ExpressionResult]):
    """存储用户当前的表情检测结果"""
    if result is not None:
        _current_expressions[user_id] = result


def get_current_expression(user_id: str) -> Optional[ExpressionResult]:
    """获取用户最近存储的表情检测结果"""
    return _current_expressions.get(user_id)
