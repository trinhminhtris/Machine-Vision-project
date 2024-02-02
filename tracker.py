import math

# Khai báo lớp tracker
class Tracker:
    # Hàm khởi tạo lớp tracker, được gọi khi một đối tượng tracker được tạo ra
    def __init__(self):
        # Khởi tạo một từ điển rỗng để lưu tọa độ đặc trưng của các đối tượng
        self.center_points = {}
        # Lưu trữ số lượng đối tượng đã được phát hiện.
        # Biến này sẽ được tăng lên mỗi khi phát hiện một đối tượng mới.
        self.id_count = 0
        
    # Hàm dùng để cập nhật thông tin về đối tượng,
    # nhận một danh sách các hộp giới hạn (objects_rect) chứa thông tin về vị trí và kích thước của các đối tượng.
    def update(self, objects_rect):
        # Khởi tạo một danh sách rỗng để lưu trữ các hộp giới hạn và ID của các đối tượng.
        objects_bbs_ids = [] 
        
        for rect in objects_rect:
            # Gán giá trị từng phần tử trong rect vào x, y, w, h
            x, y, w, h = rect
            # Tính toán thông số xác định đối tượng, thông số này để tính toán tọa độ trọng tâm của đối tượng,
            # nhưng phép toán tính trọng tâm chính xác dễ nhận diện 2 đối tượng gần nhau thành 1 vật thể.
            # Do đó, để đặc trưng hóa các thông số, ta cộng thêm một lần x và một lần y để các thông số trở nên đặc trưng,
            # thuận lợi cho việc xác định có cùng một vật thể hay không. 
            cx = (x + x + w) // 2  # cx = (x + w)//2
            cy = (y + y + h) // 2  # cy = (y + h)//2
            
            # Xác định xem đối tượng đã được phát hiện trước đó chưa
            same_object_detected = False 
            
            # Duyệt qua từng cặp ID và giá trị đặc trưng trong từ điển với self.center_points.
            # Phương thức item() sử dụng trong danh sách để trả về một cặp giá trị (key, value) từ đối tượng.
            for id, pt in self.center_points.items():
                #Uclidean giữa thông số đặc trưng mới (cx, cy) và thông số đặc trưng đã biết (pt[0], pt[1]).
                dist = math.hypot(cx - pt[0], cy - pt[1])
                # Nếu dist < 20 thì được xem là đủ gần và được coi là cùng đối tượng.
                # Ta cập nhật lại giá trị đặc trưng của đối tượng bằng tọa độ mới.
                if dist < 20:
                    self.center_points[id] = (cx, cy)
                    # Thêm thông tin (x, y, w, h, id) vào danh sách objects_bbs_ids để biểu thị hình chữ nhật và ID của đối tượng.
                    objects_bbs_ids.append([x, y, w, h, id])
                    same_object_detected = True
                    break
            
            # Nếu phát hiện đối tượng mới (không tìm thấy đối tượng tương tự đã được phát hiện trước đó)
            if same_object_detected is False:
                # Gắn thông số đặc trưng mới cho đối tượng mới được phát hiện trong self.center_points với key là self.id_count
                self.center_points[self.id_count] = (cx, cy)
                # Thêm thông tin đối tượng mới vào danh sách objects_bbs_ids gồm tọa độ hình chữ nhật (x, y, w, h) cùng 
                # ID của đối tượng (self.id_count)
                objects_bbs_ids.append([x, y, w, h, self.id_count])
                # Tăng ID lên 1 để gán cho đối tượng mới tiếp theo
                self.id_count += 1 
        
        # Làm sạch từ điển self.center_points để loại bỏ các ID không sử dụng nữa.
        # Tạo 1 từ điển rỗng mới để lưu trữ các thông số đặc trưng của các đối tượng đã được phát hiện và được sử dụng.
        new_center_points = {}  
        # Duyệt qua từng phần tử trong danh sách objects_bbs_ids, chứa thông tin về 
        # các hộp giới hạn và ID của các đối tượng đã được phát hiện.
        for obj_bb_id in objects_bbs_ids:
            # Gán giá trị ID của đối tượng cho biến object_id
            _, _, _, _, object_id = obj_bb_id
            # Truy xuất thông số đặc trưng của đối tượng từ từ điển self.center_points dựa trên ID.
            center = self.center_points[object_id]
            # Gán giá trị thông số đặc trưng của đối tượng trong từ điển mới new_center_points, để đảm bảo
            # chỉ thông số đặc trưng của các đối tượng đực phát hiện trong objects_bbs_ids mới nhất được sao chép vào new_center_points.
            new_center_points[object_id] = center
        
        # Cập nhật lại self.center_points để chỉ chứa thông số đặc trưng của các đối tượng đã được phát hiện trong objects_bbs_ids để
        # loại bỏ những id không sử dụng nữa, đảm bảo self.center_points chỉ chứa thông tin về các đối tượng hiện tại và đang được theo dõi.
        self.center_points = new_center_points.copy()
        return objects_bbs_ids      