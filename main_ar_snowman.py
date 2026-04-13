"""
Homework #4: Camera Pose Estimation and AR
- 목표: 카메라 캘리브레이션 결과를 활용하여 자세(Pose)를 추정하고 AR 물체 띄우기
- AR 물체: 체스보드 위에서 회전하는 입체 눈사람 (가려짐 효과 적용)
- 특징: 전체 프레임을 먼저 백그라운드에서 렌더링(편집)하여 저장한 후, 최종 결과 영상을 재생합니다.
"""

import cv2
import numpy as np
import math
import os

# ==========================================
# 1. 환경 및 파일 설정
# ==========================================
video_path = "chessVideo.mp4"                  # 입력 비디오 파일
calib_file = "calibration_result.npz"          # Homework #3 캘리브레이션 결과
output_video_path = "ar_snowman_output.mp4"    # 결과물 저장 경로

pattern_size = (9, 6)   # 체스보드 내부 코너 개수 (가로, 세로)
square_size = 3.0       # 체스보드 한 칸의 실제 크기 (cm)

# ==========================================
# 2. 카메라 캘리브레이션 내부 파라미터 로드
# ==========================================
if not os.path.exists(calib_file):
    print(f"[오류] '{calib_file}' 파일을 찾을 수 없습니다.")
    exit()

data = np.load(calib_file)
camera_matrix = data["camera_matrix"]
dist_coeffs = data["dist_coeffs"]
print("[INFO] 카메라 캘리브레이션 데이터 로드 완료")

# ==========================================
# 3. 비디오 입출력 초기화
# ==========================================
cap = cv2.VideoCapture(video_path)
if not cap.isOpened():
    print(f"[오류] '{video_path}' 비디오를 열 수 없습니다.")
    exit()

# 비디오 저장을 위한 포맷 및 해상도 설정
ret, first_frame = cap.read()
h, w = first_frame.shape[:2]
fps = cap.get(cv2.CAP_PROP_FPS)
total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter(output_video_path, fourcc, fps, (w, h))

cap.set(cv2.CAP_PROP_POS_FRAMES, 0) # 첫 프레임으로 되감기

# ==========================================
# 4. 3D 공간 제어 변수 및 월드 좌표계 정의
# ==========================================
# 체스보드 평면(Z=0)의 3D 좌표 (World Coordinate) 생성
objp = np.zeros((pattern_size[0] * pattern_size[1], 3), np.float32)
objp[:, :2] = np.mgrid[0:pattern_size[0], 0:pattern_size[1]].T.reshape(-1, 2)
objp *= square_size

# 눈사람을 체스보드 정중앙에 배치하기 위한 중심점 계산
center_x = (pattern_size[0] * square_size) / 2
center_y = (pattern_size[1] * square_size) / 2

# 애니메이션 상태 관리 변수
angle = 0.0          # 회전 애니메이션용 각도

print(f"\n[INFO] 총 {total_frames} 프레임에 대한 AR 렌더링을 시작합니다.")
print("[INFO] 편집 중입니다. 잠시만 기다려주세요... (창이 나타나지 않습니다)")

# ==========================================
# 5. 메인 AR 렌더링 루프 (백그라운드 처리)
# ==========================================
current_frame_idx = 0
while True:
    ret, frame = cap.read()
    if not ret:
        break

    current_frame_idx += 1
    # 터미널에 진행률 표시 (\r을 사용해 한 줄에 덮어쓰기)
    print(f"\r[INFO] 렌더링 진행률: {current_frame_idx} / {total_frames} 프레임 처리 중...", end="")

    # 코너 검출 정확도를 높이기 위한 그레이스케일 변환
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # 체스보드 코너 찾기
    found, corners = cv2.findChessboardCorners(gray, pattern_size)

    if found:
        # 서브픽셀 정밀도로 코너 위치 보정
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
        corners2 = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)

        # ---------------------------------------------------------
        # [평가 항목 1] Camera Pose Estimation (5점)
        # PnP 알고리즘을 이용해 체스보드 기준 카메라의 회전(rvec)과 평행이동(tvec) 추정
        # ---------------------------------------------------------
        ret_pnp, rvec, tvec = cv2.solvePnP(objp, corners2, camera_matrix, dist_coeffs)

        # 카메라 기준 깊이(Depth, Z값)를 계산하는 함수
        # (용도: AR 물체가 회전할 때 겹치는 부분의 가려짐 효과 구현)
        R, _ = cv2.Rodrigues(rvec)
        def get_depth(pt_3d):
            # 카메라 좌표계로 변환 후 Z축 값만 추출 (값이 클수록 카메라에서 멂)
            return (R @ np.array(pt_3d).reshape(3, 1) + tvec)[2][0]

        # ---------------------------------------------------------
        # [평가 항목 2] AR Object Visualization (15점)
        # 회전하는 3D 눈사람 모델 좌표 정의 및 투영
        # ---------------------------------------------------------
        body_center = [center_x, center_y, -3.0]  # 몸통 중앙
        head_center = [center_x, center_y, -7.0]  # 머리 중앙
        body_edge = [center_x + 3.0, center_y, -3.0] # 몸통 반경 (3.0)
        head_edge = [center_x + 2.0, center_y, -7.0] # 머리 반경 (2.0)

        # 애니메이션 각도(angle)에 맞춰 회전하는 요소(코, 양팔) 좌표 계산
        nose_tip = [center_x + 3.5 * math.cos(angle), center_y + 3.5 * math.sin(angle), -7.0]
        arm1_end = [center_x + 5.0 * math.cos(angle + math.pi/2), center_y + 5.0 * math.sin(angle + math.pi/2), -4.0]
        arm2_end = [center_x + 5.0 * math.cos(angle - math.pi/2), center_y + 5.0 * math.sin(angle - math.pi/2), -4.0]

        # 화가 알고리즘(Painter's Algorithm)을 위한 각 파트 깊이 계산
        depth_body = get_depth(body_center)
        depth_head = get_depth(head_center)
        depth_nose = get_depth(nose_tip)
        depth_arm1 = get_depth(arm1_end)
        depth_arm2 = get_depth(arm2_end)

        # 정의된 3D 점들을 하나의 배열로 묶기
        points_3d = np.array([body_center, head_center, body_edge, head_edge, nose_tip, arm1_end, arm2_end], dtype=np.float32)

        # 3D 월드 좌표 -> 2D 이미지 좌표로 투영 (Projection)
        imgpts, _ = cv2.projectPoints(points_3d, rvec, tvec, camera_matrix, dist_coeffs)
        imgpts = np.int32(imgpts).reshape(-1, 2)

        # 투영된 픽셀 좌표 언패킹
        pt_body, pt_head, pt_body_edge, pt_head_edge, pt_nose, pt_arm1, pt_arm2 = [tuple(pt) for pt in imgpts]

        # 투영된 2D 평면상에서의 원의 픽셀 반지름 계산
        r_body = int(np.linalg.norm(np.array(pt_body) - np.array(pt_body_edge)))
        r_head = int(np.linalg.norm(np.array(pt_head) - np.array(pt_head_edge)))

        brown_color = (19, 69, 139)  # 팔 색상 (BGR)
        orange_color = (0, 140, 255) # 코 색상 (BGR)

        # --- [가려짐(Occlusion)을 고려한 렌더링] ---
        # 1단계: 몸통보다 멀리(뒤) 있는 팔 그리기
        if depth_arm1 > depth_body:
            cv2.line(frame, pt_body, pt_arm1, brown_color, 6)
        if depth_arm2 > depth_body:
            cv2.line(frame, pt_body, pt_arm2, brown_color, 6)

        # 2단계: 머리보다 멀리(뒤) 있는 코 그리기
        if depth_nose > depth_head:
            cv2.line(frame, pt_head, pt_nose, orange_color, 6)

        # 3단계: 기본 몸통 및 머리 렌더링 (흰색 채우기 + 회색 윤곽선)
        cv2.circle(frame, pt_body, r_body, (250, 250, 250), -1)
        cv2.circle(frame, pt_body, r_body, (150, 150, 150), 2)
        cv2.circle(frame, pt_head, r_head, (250, 250, 250), -1)
        cv2.circle(frame, pt_head, r_head, (150, 150, 150), 2)

        # 4단계: 몸통보다 가까이(앞) 있는 팔 그리기
        if depth_arm1 <= depth_body:
            cv2.line(frame, pt_body, pt_arm1, brown_color, 6)
        if depth_arm2 <= depth_body:
            cv2.line(frame, pt_body, pt_arm2, brown_color, 6)

        # 5단계: 머리보다 가까이(앞) 있는 코 그리기
        if depth_nose <= depth_head:
            cv2.line(frame, pt_head, pt_nose, orange_color, 6)

        # 다음 프레임을 위한 회전 각도 증가
        angle += 0.15

    # UI 안내 텍스트 비디오 프레임에 기록 (저장본에 영구 포함됨)
    cv2.putText(frame, "Press 'q' to quit", (30, 80), cv2.FONT_HERSHEY_SIMPLEX, 2.0, (0, 0, 255), 4, cv2.LINE_AA)
    cv2.putText(frame, "Press 'SPACE' to pause", (30, 160), cv2.FONT_HERSHEY_SIMPLEX, 2.0, (0, 255, 0), 4, cv2.LINE_AA)

    # 디스플레이 출력 없이 파일에만 저장
    out.write(frame)

# 렌더링 자원 반환
cap.release()
out.release()
print(f"\n\n[INFO] 성공적으로 렌더링을 마쳤습니다. 결과물: '{output_video_path}'")

# ==========================================
# 6. 완성된 결과 영상 재생 (Playback 루프)
# ==========================================
print("[INFO] 저장된 AR 영상을 재생합니다. (종료: 'q', 일시정지: 'SPACE')")

cap_play = cv2.VideoCapture(output_video_path)
window_name = 'AR Snowman Playback'
cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
cv2.resizeWindow(window_name, int(w * 0.5), int(h * 0.5))

is_paused = False
drawn_frame = None

while True:
    if not is_paused:
        ret, frame = cap_play.read()
        if not ret:
            print("[INFO] 영상 재생이 완료되었습니다.")
            break
        drawn_frame = frame.copy()
    else:
        # 일시정지 상태: 캐시된 프레임을 유지하며 PAUSED 텍스트만 덧씌움
        if drawn_frame is not None:
            frame = drawn_frame.copy()
            cv2.putText(frame, "[PAUSED]", (30, 240), cv2.FONT_HERSHEY_SIMPLEX, 2.0, (0, 255, 255), 4, cv2.LINE_AA)

    cv2.imshow(window_name, frame)

    # ---------------------------------------------------------
    # 재생 시 키보드 및 윈도우 이벤트 처리
    # ---------------------------------------------------------
    key = cv2.waitKey(int(1000/fps)) & 0xFF  # 영상 FPS에 맞추어 재생 속도 조절
    if key == ord('q'):         # q 입력 시 재생 강제 종료
        break
    elif key == ord(' '):       # 스페이스바 입력 시 일시정지 토글
        is_paused = not is_paused

    # 사용자가 창의 'X' 버튼을 눌러 강제 종료했는지 감지
    if cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE) < 1:
        break

# 재생 시스템 자원 반환
cap_play.release()
cv2.destroyAllWindows()