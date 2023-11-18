# import cv2
# import os
# import traceback

# read_path = r'C:\HCI\project\dataset\video'
# write_path = r'C:\HCI\project\dataset\pictures'
# frame_jump = 10
# img_name = 0

# video_list = os.listdir(read_path)
# for video_name in video_list:
#     try:
#         video = cv2.VideoCapture(os.path.join(read_path, video_name))
#         if video.isOpened():
#             cnt = 0
#             while video.isOpened():
#                 ret, img = video.read()
#                 if cnt == frame_jump:
#                     cnt = 0
#                     cv2.imwrite(os.path.join(write_path, '{}.jpg'.format(img_name)), img)
#                     cv2.imshow('img', img)
#                     cv2.waitKey(1)
#                     img = 0
#                     img_name += 1
#                 cnt += 1
#             video.release()
#         else:
#             raise Exception('동영상 파일을 열 수 없습니다.')
#     except Exception as e:
#         print('에러 발생:')
#         print(traceback.format_exc())
#         break
#라이브러리 호출
import cv2
import os

print(cv2.__version__)

# Specify the directory containing video files
video_directory = r'C:\HCI\project\dataset\video'

# Check if the directory exists
if not os.path.exists(video_directory):
    print(f"Error: Directory not found - {video_directory}")
    exit(1)

# Construct the full file paths for all video files in the directory
video_files = [os.path.join(video_directory, file) for file in os.listdir(video_directory) if file.endswith('.mp4')]

count = 0
# Loop through each video file
for video_file in video_files:
    video = cv2.VideoCapture(video_file)

    if not video.isOpened():
        print("Could not open:", video_file)
        continue  # Move to the next iteration if the video cannot be opened

    # Get video properties
    length = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = video.get(cv2.CAP_PROP_FPS)

    print(f"\nProcessing video file: {video_file}")
    print("Video length:", length)
    print("Frame width:", width)
    print("Frame height:", height)
    print("Frames per second:", fps)

    # Create a directory to save frames for each video
    output_directory = os.path.join(video_directory, os.path.splitext(os.path.basename(video_file))[0])
    try:
        os.makedirs(output_directory)
    except OSError:
        print(f"Error: Creating directory {output_directory}")

    # Process each frame
    while(video.isOpened()):
        ret, image = video.read()
        if not ret:
            break

        # Save every 1 second of video
        if int(video.get(1)) % int(fps *0.5) == 0:
            frame_filename = f"2_frame{count}.jpg"
            frame_path = os.path.join('C:\HCI\project\dataset\pictures', frame_filename)
            cv2.imwrite(frame_path, image)
            print(f'Saved frame: {frame_path}')
            count += 1

    # Release the video object
    video.release()
    print(f"Frames saved for {video_file}")

print("\nFrames extraction complete.")

