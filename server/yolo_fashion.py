# fashion_object_detection_with_faiss.py

import torch
from PIL import Image
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import json
import faiss
from transformers import (
    AutoImageProcessor,
    AutoModelForObjectDetection,
    AutoProcessor,
    AutoModelForZeroShotImageClassification,
)

print(faiss.__version__)


# 1. 객체 탐지 모델 (YOLOS)
def load_detection_model(model_name="valentinafeve/yolos-fashionpedia"):
    print("객체 탐지 모델 불러오는 중...")
    processor = AutoImageProcessor.from_pretrained(model_name)
    model = AutoModelForObjectDetection.from_pretrained(model_name)
    return processor, model


# 2. FashionCLIP 모델 (임베딩용)
def load_embedding_model(model_name="patrickjohncyh/fashion-clip"):
    print("FashionCLIP 임베딩 모델 불러오는 중...")
    processor = AutoProcessor.from_pretrained(model_name)
    model = AutoModelForZeroShotImageClassification.from_pretrained(model_name)
    return processor, model


# 3. 이미지 로드
def load_image(image_path):
    print(f"이미지 로드: {image_path}")
    image = Image.open(image_path).convert("RGB")
    return image


# 4. 객체 탐지
def detect_objects(image, processor, model, threshold=0.5):
    print("객체 탐지 중...")
    inputs = processor(images=image, return_tensors="pt")
    with torch.no_grad():
        outputs = model(**inputs)

    target_sizes = torch.tensor([image.size[::-1]])  # (height, width)
    results = processor.post_process_object_detection(
        outputs, target_sizes=target_sizes, threshold=threshold
    )[0]
    return results


# 5. 객체별 임베딩 추출
def get_object_embeddings(image, results, detection_model, embedding_processor, embedding_model):
    print("객체별 임베딩 생성 중...")
    embeddings = {}
    for i, (score, label, box) in enumerate(zip(results["scores"], results["labels"], results["boxes"])):
        xmin, ymin, xmax, ymax = box.tolist()
        obj_crop = image.crop((xmin, ymin, xmax, ymax))  # 객체 영역 자르기
        label_name = detection_model.config.id2label[label.item()]

        # FashionCLIP 임베딩
        inputs = embedding_processor(images=obj_crop, return_tensors="pt")
        with torch.no_grad():
            outputs = embedding_model.get_image_features(**inputs)  # [1, hidden_dim]

        embeddings[f"{label_name}_{i}"] = outputs.squeeze().numpy().astype("float32")

    return embeddings


# 6. 결과 시각화
def visualize_results(image, results, model, save_path="output_with_boxes.png"):
    print(f"탐지 결과 시각화 → {save_path}")
    plt.figure(figsize=(10, 10))
    plt.imshow(image)
    ax = plt.gca()

    for score, label, box in zip(results["scores"], results["labels"], results["boxes"]):
        xmin, ymin, xmax, ymax = box.tolist()
        width, height = xmax - xmin, ymax - ymin
        ax.add_patch(
            patches.Rectangle(
                (xmin, ymin), width, height, linewidth=2, edgecolor="red", facecolor="none"
            )
        )
        label_name = model.config.id2label[label.item()]
        ax.text(
            xmin,
            ymin,
            f"{label_name}: {round(score.item(), 2)}",
            bbox=dict(facecolor="yellow", alpha=0.5),
            fontsize=10,
            color="black",
        )

    plt.axis("off")
    plt.title("Fashion Object Detection")
    plt.savefig(save_path)


# 7. FAISS에 저장
def save_to_faiss(embeddings, prefix="fashion_index"):
    print("FAISS 인덱스 저장 중...")
    vectors = np.array(list(embeddings.values())).astype("float32")
    labels = list(embeddings.keys())

    dim = vectors.shape[1]
    index = faiss.IndexFlatL2(dim)  # L2 거리 기반 인덱스
    index.add(vectors)

    faiss.write_index(index, f"{prefix}.faiss")
    with open(f"{prefix}_labels.json", "w") as f:
        json.dump(labels, f, ensure_ascii=False, indent=2)

    print(f"저장 완료: {prefix}.faiss , {prefix}_labels.json")


# 8. 메인 실행
def main():
    image_path = "C:\\kdt\\front\\images\\cloth.png"

    # 모델 불러오기
    det_processor, det_model = load_detection_model()
    emb_processor, emb_model = load_embedding_model()

    # 이미지 로드 및 객체 탐지
    image = load_image(image_path)
    results = detect_objects(image, det_processor, det_model, threshold=0.5)

    # 탐지 결과 출력
    print("\n 탐지된 객체들:")
    for score, label, box in zip(results["scores"], results["labels"], results["boxes"]):
        label_name = det_model.config.id2label[label.item()]
        print(f"{label_name}: {round(score.item(), 3)} | 박스: {box.tolist()}")

    # 임베딩 생성
    embeddings = get_object_embeddings(image, results, det_model, emb_processor, emb_model)

    print("\n 임베딩 정보:")
    for obj_name, emb in embeddings.items():
        print(f"{obj_name}: shape={emb.shape}")

    # 시각화
    visualize_results(image, results, det_model)

    # FAISS 저장
    save_to_faiss(embeddings, prefix="fashion_objects")


if __name__ == "__main__":
    main()