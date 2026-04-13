# AR Snowman Project (컴퓨터비전 과제 #4)

본 프로젝트는 카메라 캘리브레이션 데이터를 기반으로 체스보드의 자세(Pose)를 추정하고, 그 위에 실시간으로 회전하는 3D 눈사람을 합성하는 증강현실(AR) 프로그램입니다.

---

## 주요 특징 및 기능

* **Camera Pose Estimation**: `cv2.solvePnP` 알고리즘을 사용하여 체스보드 기준 카메라의 6자유도(Rotation, Translation)를 추정합니다.

* **3D AR Visualization**: 단순한 `축(Axis)` 표시를 넘어, 3D 좌표로 설계된 눈사람 모델을 `cv2.projectPoints`로 투영하여 시각화합니다.

* **Occlusion Handling**: `화가 알고리즘(Painter's Algorithm)`과 카메라 좌표계의 `깊이(Depth)` 계산을 통해, 눈사람이 회전할 때 팔과 코가 몸통 뒤로 가려지는 효과를 구현하여 입체감을 높였습니다.

* **Stable Rendering**: 전체 프레임을 백그라운드에서 먼저 렌더링하여 저장한 후 재생하는 방식을 채택하여, 원본 영상 전체에 대해 끊김 없는 고화질 AR 결과물을 보장합니다.

---

## 비디오 예시

* Original Video: `chessVideo.mp4`
https://youtu.be/ODB6fhd_y3E

* AR Result Video: `ar_snowman_output.mp4`
https://youtu.be/EJA77B-PG7I

---

## 실행 방법

1. 동일한 폴더 내에 `chessVideo.mp4`와 `calibration_result.npz` 파일이 있는지 확인합니다.
(해당 파일 생성법에 대해선 [해당 링크](https://github.com/jayjaewoo/Camera-Calibration-and-Lens-Distortion-Correction-OpenCV-)를 참조하세요)

3. main_ar_snowman.py를 실행합니다.

3. 터미널에서 렌더링 진행률을 확인합니다.

4. 렌더링이 완료되면 결과 영상이 자동으로 재생됩니다.

SPACE: 일시정지 / 재생 토글
q: 프로그램 종료

---

## 개발 환경

* Python 3.x
* OpenCV (cv2)
* NumPy
NumPy# AR-Snowman-Project
