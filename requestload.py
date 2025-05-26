import requests
import sys

def main():
    try:
        version = requests.get("https://raw.githubusercontent.com/baoandepzai/Tool-tai-xiu/refs/heads/main/Ver", timeout=5).text
        print("Latest version:", version)
    except requests.exceptions.RequestException:
        print("Không có kết nối mạng! Vui lòng kiểm tra lại internet! ❌")
        sys.exit()

    print("Xin chào bạn đến với tool dự đoán! 🎲")
    print("Bạn muốn dùng tool nào?")
    print("➤ Nhập 'M' để dùng tool DỰ ĐOÁN Tai Xiu MD5")
    print("➤ Nhập 'T' để dùng tool DỰ ĐOÁN Tai Xiu (AI tự đoán)")
    print("⚠️Khi nhập nếu để 1 dòng trống sẽ gây lỗi")
    print("➤ Nhập 'exit' để thoát chương trình")

    while True:
        try:
            choice = input(">>> Nhập lựa chọn của bạn (M/T/exit): ").strip().upper()

            if not choice:
                print("Bạn chưa nhập gì cả! Hãy thử lại! :)")
                continue

            if choice == "EXIT":
                print("Tạm biệt! Hẹn gặp lại lần sau nha! 👋")
                break

            elif choice == "M":
                print("Đang tải tool theo mã MD5...")
                try:
                    response = requests.get("https://raw.githubusercontent.com/baoandepzai/Tool-tai-xiu/refs/heads/main/tooltaixiumd5.py", timeout=5)
                    exec_code(response.text, 'tool_md5')
                except Exception as e:
                    print("Lỗi khi chạy tool M:", e)

            elif choice == "T":
                print("Đang tải tool AI tự đoán...")
                try:
                    response = requests.get("https://raw.githubusercontent.com/baoandepzai/Tool-tai-xiu/refs/heads/main/tooltaixiu.py", timeout=5)
                    exec_code(response.text, 'tool_ai')
                except Exception as e:
                    print("Lỗi khi chạy tool T:", e)

            else:
                print("Lựa chọn không hợp lệ! Vui lòng chỉ nhập 'M', 'T' hoặc 'exit' ! >:(")

        except Exception as e:
            print("Có lỗi xảy ra khi nhập! Hãy thử lại!")
            continue

def exec_code(code_text, namespace_name):
    # Tạo namespace riêng cho tool tải về
    tool_env = {"__name__": "__main__"}
    exec(code_text, tool_env)

if __name__ == "__main__":
    main()
