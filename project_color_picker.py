from PIL import Image
import numpy as np
from collections import Counter
from sklearn.cluster import KMeans
import base64
from io import BytesIO


def extract_top_colors(file_storage, num_colors=10):
    try:
        img = Image.open(file_storage).convert('RGB')
        img.thumbnail((130, 130))   # 성능 최적화용(너무 작게하면 분산이 부족해지므로 적당히)
        pixels = np.array(img)      # 이미지를 numpy 배열로 변경

        # 비정상 이미지 처리
        if pixels.ndim != 3 or pixels.shape[2] != 3:
            raise ValueError("Image format is not RGB.")

        # 이미지의 총 픽셀(행x열) 계산 후 각 픽셀마다 RGB값 부여 = (100, 200, 3) → (20000, 3)
        pixels = pixels.reshape(-1, 3)

        if pixels.size == 0:
            raise ValueError("No vaild colors could be extracted from the image.")

        # numpy 배열로 바꾼 이미지의
        pixels = np.array(img).reshape(-1, 3)

        # KMeans로 색상 클러스터링
        kmeans = KMeans(n_clusters=num_colors, random_state=42, n_init='auto')  # 랜덤 시드 42로 고정
        labels = kmeans.fit_predict(pixels)             # 각 픽셀이 속하는 그룹(클러스터) 저장
        centers = kmeans.cluster_centers_.astype(int)   # 각 클러스터의 중심 색상

        # 각 클러스터의 픽셀 수와 전체 픽셀 수 계산
        counts = np.bincount(labels)
        total = np.sum(counts)

        # (빈도, 색상 중심값) 튜플 생성 후 빈도 기준으로 내림차순 정렬
        color_info = sorted(zip(counts, centers), reverse=True)

        # HEX 색상 리스트 및 비율 반환
        result = []
        for count, (r, g, b) in color_info:
            hex_color = f'#{r:02x}{g:02x}{b:02x}'
            ratio = round((count / total) * 100, 1)  # 소수점 1자리 %
            result.append((hex_color, ratio))
        return result
    except ValueError:  # 에러 발생시 빈 리스트 반환
        return []

def convert_file_to_data_url(file_storage):
    image_bytes = BytesIO()     # 파일 내용을 디스크에 저장하지 않고 메모리에서 바로 처리하기 위해 빈 바이트 스트림 생성
    file_storage.save(image_bytes)  # 생성한 메모리 버퍼에 FileStorage 객체의 데이터 저장
    encoded_image = base64.b64encode(image_bytes.getvalue()).decode('utf-8')    # bytes→ base64 형식의 bytes로 인코딩 → str로 디코딩(UTF-8 방식)
    return f"data:{file_storage.mimetype};base64,{encoded_image}"   # data URL 형식으로 문자열을 만들어 반환(e.g. data:image/png;base64,iVBORw0KGgoAAAANS...)