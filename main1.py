#%%
import cv2
import numpy as np
from ultralytics import YOLO
from tracker import*

# Khởi tạo model YOLO với tệp trọng số yolov8s.pt
model = YOLO("weights/yolov8s.pt", "v8")

# Mở video để đọc khung hình
cap = cv2.VideoCapture('ThreePastShop2_60fps.mp4')
# Lấy thông số tốc độ khung hình
fps = cap.get(cv2.CAP_PROP_FPS)

# Đọc dữ liệu từ tệp "coco.txt" chứa danh sách các lớp
my_file = open("coco1.txt", 'r')
# Đọc toàn bộ nội dung của file "coco.txt" và gán nó vào biến data
data = my_file.read()
# Chia chuỗi data thành 1 danh sách các lớp bằng kí tự xuống dòng ("\n")
class_list = data.split("\n")
my_file.close()

# Khởi tạo các biến đếm và lưu trữ vị trí khung hình trước đó
count = 0           # biến đếm khung hình
num_objects = 0     # số vật thể trong khung hình
num_speed_high = 0  # số vật thể chuyển động nhanh
num_speed_low = 0   # số vật thể chuyển động chậm
frame_index = 0     # biến lưu thứ tự khung hình đã lưu
i = 0               # biến đếm

# Khởi tạo bộ lọc kalman
class KalmanFilter:
    def __init__(self, process_variance, measurement_variance):
        self.process_variance = process_variance
        self.measurement_variance = measurement_variance
        self.estimated_state = 57.78 # Khởi tạo giá trị trạng thái ước lượng
        self.estimated_error = 18 # Khởi tạo giá trị lỗi ước lượng

    def predict(self):
        # Dự đoán trạng thái kế tiếp
        self.estimated_state = self.estimated_state
        self.estimated_error = self.estimated_error + self.process_variance

    def update(self, measurement):
        # Cập nhật trạng thái dựa trên đo đạc thực tế
        kalman_gain = self.estimated_error / (self.estimated_error + self.measurement_variance)
        self.estimated_state = self.estimated_state + kalman_gain * (measurement - self.estimated_state)
        self.estimated_error = (1 - kalman_gain) * self.estimated_error

class SlidingAverageFilter:
    def __init__(self, window_size):
        self.window_size = window_size
        self.values = []

    def update(self, value):
        self.values.append(value)
        if len(self.values) > self.window_size:
            self.values = self.values[-self.window_size:]

    def get_average(self):
        if not self.values:
            return 0
        return sum(self.values) / len(self.values)
    
# Khởi tạo bộ lọc trung bình cộng trượt với kích thước cửa sổ là 10 (có thể điều chỉnh)
sliding_average_filter = SlidingAverageFilter(window_size = 5)   

# Định nghĩa tỷ lệ chuyển đổi từ pixel sang mét (tùy thuộc vào kích thước thực của vật thể trong thế giới thực)
pixel_to_meter_ratio = 0.0375  # Ví dụ: 1 pixel = 0.037 mét, sai số tầm 10%

# Hàm chuyển đổi vận tốc từ pixel/s sang m/s
def pixel_per_second_to_meter_per_second(pixel_speed, pixel_to_meter_ratio):
    return pixel_speed * pixel_to_meter_ratio

# Khởi tạo bộ lọc Kalman cho tốc độ
kalman_filter_speed = KalmanFilter(process_variance = 1, measurement_variance = 5)
# Khởi tạo bộ lọc Kalman cho tốc độ x
kalman_filter_speed_x = KalmanFilter(process_variance = 1, measurement_variance = 5)
# Khởi tạo bộ lọc Kalman cho tốc độ y
kalman_filter_speed_y = KalmanFilter(process_variance = 1, measurement_variance = 2)

# Khởi tạo một tracker để theo dõi vật thể trong khung hình
tracker = Tracker()
# Khởi tạo một từ điển trống để lưu trữ thông tin về vật thể trong các khung hình trước
previous_frame = {}
# Biến frame_count để đếm số lượng khung hình đã xử lý
frame_count = 0
# Khai báo biến tính toán tốc độ trung bình cộng:
average_speed_meter_per_second = 0

# Lặp qua từng khung hình trong video:
while True:
    # Đọc 1 khung hình từ video và gắn khung hình vào biến frame
    # Biến ret được sử dụng để xem việc đọc khung hình có thành công hay không
    ret, frame = cap.read()
    
    if not ret:
        break
    
    # Giảm số lượng khung hình cần xét để tăng tốc độ xử lý.
    count += 1
    if count % 8 != 0:
        continue   # bỏ qua phần còn lại của vòng lặp, bắt đầu vòng lặp mới
    
    # Điều chỉnh kích thước khung hình
    #frame = cv2.resize(frame, (1020, 500))
    frame = cv2.resize(frame, (816, 400))
    
    # Sử dụng mô hình YOLO để dự đoán và nhận diện các vật thể trong khung hình.
    # frame là khung hình đang xử lý, conf là ngưỡng tin cậy, classes là lớp đối tượng cần nhận diện, show = True: hiển thị khung hình detect
    results = model.predict(frame, conf = 0.58, classes = 0, show = True)
    # cho num_objects = 0 để reset sau mỗi khung hình
    num_objects = 0
    
    # Lấy danh sách các hộp giới hạn của các vật thể nhận diện.
    # arr là mảng
    #arr = results[0].boxes.boxes
    arr = results[0].numpy()
    #arr = np.array(results[0])
    
    # Tính số vật thể nhận diện được trong frame
    num_objects += len(arr)  # cộng thêm số vật thể trong khung hình này
    
    # Chuyển đổi danh sách hộp giới hạn thành DataFrame để dễ dàng truy cập thông tin.
    # DataFrame cấu trúc 2 chiều dạng bảng
    #px = pd.DataFrame(arr).astype("float")
    # reset các giá trị cho vòng lặp mới
    i = 0
    state = 0     # biến trạng thái đưa ra cảnh báo về tốc độ bất thường
    list = []     # mảng chứa tọa độ hộp giới hạn của các object detect được
    
    # Xử lý từng vật thể nhận diện được trong khung hình.
    # Trong vòng lặp for, với mỗi hàng của px, xác định tọa độ và lớp của vật thể.
    # Nếu lớp là "person", thêm tọa độ vào danh sách list.
    # column chỉ các cột chứa thông tin trong dataframe
    # column 0, 1, 2, 3 chứa tọa độ hộp giới hạn row 4 chứa conf, row 5 chứa class.
    for result in results:
        for j in range(0, num_objects, 1):
            # x1, y1, x2, y2 là tọa độ hộp giới hạn
            x1 = int(result.boxes.xyxy.cpu().detach().numpy()[j][0])
            y1 = int(result.boxes.xyxy.cpu().detach().numpy()[j][1])
            x2 = int(result.boxes.xyxy.cpu().detach().numpy()[j][2])
            y2 = int(result.boxes.xyxy.cpu().detach().numpy()[j][3])
            # d là class của vật thể
            d = int(result.boxes.cls.cpu().detach().numpy()[0])
            c = class_list[d]
            # Nếu truy xuất được đối tượng "person" thì thêm tọa độ hộp giới hạn của đối tượng đó vào list.
            if 'person' in c:
                list.append([x1, y1, x2, y2])
        print(list)
            
    # Cập nhật trạng thái vật thể và vẽ đường tròn, gán nhãn vật thể.
    # Gọi phương thức update của đối tượng Tracker để cập nhật thông tin về vật thể
    # và nhận về danh sách vật thể cùng với ID.
    bbox_id = tracker.update(list) 
    # Với mỗi vật thể và ID tương ứng, tính toán tọa độ trung tâm và vẽ hộp giới hạn lên khung hình.
    for bbox in bbox_id:
        x1, y1, x2, y2, id = bbox
        cx = int(x1 + x2)//2
        cy = int(y1 + y2)//2
        cv2.circle(frame, (cx, cy), 2, (0, 0, 255), 2)
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        
        # Tính toán tốc độ của vật thể và cho biết vật thể đang đứng yên hay chuyển động.
        # Kiểm tra có khung hình trước không, 'previous_frame is not None', và 
        # vật thể hiện tại có trong khung hình trước không, "id in previous_frame"
        if previous_frame is not None and id in previous_frame:
            # Lấy giá trị tọa độ trọng tâm trong khung hình trước
            prev_cx, prev_cy, prev_frame_count = previous_frame[id]
            print("prev", prev_cx, prev_cy, prev_frame_count)
            print("now", cx, cy, frame_count) 
            
            # Tính toán độ dịch theo trục x và y
            dx = abs(cx - prev_cx)
            dy = abs(cy - prev_cy)

            # Tính thời gian giữa 2 khung hình đang xét
            dt = 8/fps
            
            # Tính tốc độ pixel/s theo trục x và y
            speed_x = dx / dt
            speed_y = dy / dt
            
            # Tính toán tốc độ sử dụng bộ lọc Kalman dx
            kalman_filter_speed_x.update(speed_x)
            kalman_filter_speed_x.predict()
            filtered_speed_x = int(kalman_filter_speed_x.estimated_state)
            # Tính toán tốc độ sử dụng bộ lọc Kalman dy
            kalman_filter_speed_y.update(speed_y)
            kalman_filter_speed_x.predict()
            filtered_speed_y = int(kalman_filter_speed_y.estimated_state)

            # Tính tốc độ pixel/s
            speed = int(math.hypot(filtered_speed_x, filtered_speed_y)) 

            # Tính toán tốc độ sử dụng bộ lọc Kalman
            kalman_filter_speed.update(speed)
            kalman_filter_speed.predict()
            filtered_speed = int(kalman_filter_speed.estimated_state)
                        
            # Chuyển đổi tốc độ từ pixel/s sang m/s
            speed_meter_per_second = pixel_per_second_to_meter_per_second(filtered_speed, pixel_to_meter_ratio)
            # Cập nhật giá trị trung bình cộng trượt cho tốc độ
            sliding_average_filter.update(speed_meter_per_second)
            # Lấy giá trị trung bình cộng
            average_speed = sliding_average_filter.get_average()

            if average_speed > 0.4:
                num_speed_high += 1
                cv2.putText(frame, "walking", (cx, cy + 10), cv2.FONT_HERSHEY_COMPLEX, 0.8, (0, 0, 255), 2)
                cv2.putText(frame, f"{average_speed:.2f}", (cx - 10, cy + 33), cv2.FONT_HERSHEY_COMPLEX, 0.8, (0, 0, 255), 2)
            else:
                num_speed_low += 1
                cv2.putText(frame, "standing", (cx, cy + 10), cv2.FONT_HERSHEY_COMPLEX, 0.8, (0, 0, 255), 2)
                cv2.putText(frame, f"{average_speed:.2f}", (cx - 10, cy + 33), cv2.FONT_HERSHEY_COMPLEX, 0.8, (0, 0, 255), 2)

            cv2.putText(frame, f"Num objects: {num_objects}", (550, 30), cv2.FONT_HERSHEY_COMPLEX, 0.8, (0, 0, 255), 2)
                
            # Cập nhật lại tọa độ trọng tâm sau khi tính toán:
            previous_frame[id] = (cx, cy, frame_count)
            
            # frame: khung hình cần vẽ
            # (cx, cy): tọa độ hiển thị
            # cv2.FONT_HERSHEY_COMPLEX: font chữ
            # 0.8: kích thước chữ
            # (0, 0, 255): màu chữ
            # 2: độ dày
            
        # Lưu trữ vị trí hiện tại của vật thể nếu vật thể không có trong khung hình trước
        # áp dụng cho những vật thể mới xuất hiện
        if id not in previous_frame:
            previous_frame[id] = (cx, cy, frame_count)
            
    # Hiển thị số lượng  đối tượng đang đi bộ, đứng im
    cv2.putText(frame, f"Num walking: {num_speed_high}", (550, 60), cv2.FONT_HERSHEY_COMPLEX, 0.8, (0, 0, 255), 2)
    num_speed_high = 0
    cv2.putText(frame, f"Num standing: {num_speed_low}", (550, 90), cv2.FONT_HERSHEY_COMPLEX, 0.8, (0, 0, 255), 2)
    num_speed_low = 0
    
    # Hiển thị khung hình
    cv2.imshow("Video", frame)
    if cv2.waitKey(5) == ord('q'):
        break
    
cap.release()
cv2.destroyAllWindows()

# %%
