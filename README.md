# AR Snowman Project

본 프로젝트는 카메라 캘리브레이션 데이터를 기반으로 체스보드의 자세(Pose)를 추정하고, 그 위에 실시간으로 회전하는 3D 눈사람을 합성하는 증강현실(AR) 프로그램입니다.

---

## 프로젝트 소개 (Description)

이 프로그램은 OpenCV를 이용하여 현실 세계의 체스보드를 마커로 인식하고, 가상의 3D 좌표계를 투영하여 사용자에게 몰입감 있는 AR 경험을 제공합니다. 단순히 좌표축만 표시하는 예제 수준을 넘어, 애니메이션과 물리적 가려짐(Occlusion)이 적용된 캐릭터 모델링을 구현하였습니다.

---

## 주요 기능 및 특징 (Features)

**1. Camera Pose Estimation (PnP)**

   * **PnP (Perspective-n-Point) 알고리즘**: `cv2.solvePnP`를 사용하여 3D 월드 좌표와 2D 이미지 좌표 사이의 회전(Rotation) 및 평행이동(Translation) 행렬을 계산합니다.
   * **정밀한 트래킹**: `cv2.cornerSubPix`를 통한 코너 정밀화로 노이즈가 있는 영상에서도 안정적인 자세 추정이 가능합니다.

**2. 3D AR Visualization (Snowman Model)**

   * **Custom 3D Model**: 단순 도형이 아닌 머리, 몸통, 팔, 코로 구성된 입체 눈사람을 설계했습니다.
   * **3D Point Projection**: 설계된 3D 좌표를 `cv2.projectPoints`를 통해 카메라 렌즈 왜곡이 반영된 2D 평면으로 투영합니다.

**3. Advanced Rendering Techniques**

   * **Occlusion Handling**: 화가 알고리즘(Painter's Algorithm)을 적용하여 눈사람이 회전할 때 카메라와의 거리에 따라 앞부분이 뒷부분을 가리도록 렌더링 순서를 최적화했습니다.
   * **Animation**: 삼각함수를 활용하여 눈사람의 양팔과 코가 부드럽게 회전하는 애니메이션을 구현했습니다.

**4. User Interface & Stability**

   * **Stable Rendering**: 전체 프레임을 선행 렌더링(Pre-rendering)하여 저장함으로써 시스템 사양에 관계없이 끊김 없는 고화질 결과물(mp4)을 생성합니다.
   * **Interactive Control**: 영상 재생 중 SPACE를 이용한 일시정지 및 q를 이용한 종료 기능을 제공합니다.

---

## 데모 영

* Original Video: `chessVideo.mp4`
  
  https://youtu.be/ODB6fhd_y3E

* AR Result Video: `ar_snowman_output.mp4`
  
  https://youtu.be/EJA77B-PG7I

---

## 실행 방법

1. 동일한 폴더 내에 `chessVideo.mp4`와 `calibration_result.npz` 파일이 있는지 확인합니다.
(캘리브레이션 파일 생성은 [이전 프로젝](https://github.com/jayjaewoo/Camera-Calibration-and-Lens-Distortion-Correction-OpenCV-)를 참조하세요)

3. `main_ar_snowman.py`를 실행합니다.

3. 터미널에서 렌더링 진행률을 확인합니다.

4. 렌더링이 완료되면 결과 영상이 자동으로 재생됩니다.

   * `SPACE`: 일시정지 / 재생 토글
   * `q`: 프로그램 종료

---

## 개발 환경

* Python 3.x
* OpenCV (cv2)
* NumPy
