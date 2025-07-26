import random, re
from collections import deque
import requests

# + Thống kê toàn cục
total_predictions = 0
correct_count = 0
correct_predictions = {"Tài": 0, "Xỉu": 0}
recent_predictions = deque(maxlen=20)
recent_results = deque(maxlen=20)

def sum_to_tx(dice):
    return "Tài" if sum(dice) >= 11 else "Xỉu"

def bias_by_streak():
    if len(recent_results) < 2:
        return None, 0, None

    last = recent_results[-1]
    streak = 1
    previous_result = None

    for i in range(2, min(len(recent_results) + 1, 6)):
        if recent_results[-i] == last:
            streak += 1
        else:
            previous_result = recent_results[-i]
            break

    if streak >= 3:
        print(f"⚠️ Đã có {streak} lần {last} liên tiếp. Nên cân nhắc đợi phiên sau.")

    return last, streak, previous_result

def calculate_likelihoods(base_prediction, streak_info=None):
    likelihoods = {}

    total_tx_actual = sum(correct_predictions.values())
    tai_ratio_actual = correct_predictions["Tài"] / total_tx_actual if total_tx_actual > 0 else 0.5

    base_impact = 0.08

    dynamic_impact = base_impact

    if streak_info and streak_info[1] >= 1:
        current_result_of_streak = streak_info[0]
        current_streak_length = streak_info[1]
        previous_result_before_streak = streak_info[2]

        if current_streak_length == 1:
            dynamic_impact_base = 0.08
        elif current_streak_length == 2:
            dynamic_impact_base = 0.06
        elif current_streak_length == 3:
            dynamic_impact_base = 0.04
        elif current_streak_length == 4:
            dynamic_impact_base = 0.02
        else:
            dynamic_impact_base = 0.01

        if current_result_of_streak == base_prediction:
            dynamic_impact = dynamic_impact_base
        else:
            dynamic_impact = -dynamic_impact_base

        if current_streak_length >= 1 and previous_result_before_streak is not None:
            if previous_result_before_streak != base_prediction:
                if base_prediction == "Xỉu" and previous_result_before_streak == "Tài" and current_streak_length >= 4:
                    dynamic_impact = -(base_impact + 0.05)
                    print(f"✨ Phát hiện chuyển đổi mạnh sang Xỉu sau chuỗi dài!")
                elif base_prediction == "Tài" and previous_result_before_streak == "Xỉu" and current_streak_length >= 4:
                    dynamic_impact = (base_impact + 0.05)
                    print(f"✨ Phát hiện chuyển đổi mạnh sang Tài sau chuỗi dài!")

    if base_prediction == "Tài":
        likelihood_tai = tai_ratio_actual + dynamic_impact
        likelihood_xiu = (1 - tai_ratio_actual) - dynamic_impact
    else:
        likelihood_tai = tai_ratio_actual - dynamic_impact
        likelihood_xiu = (1 - tai_ratio_actual) + dynamic_impact

    likelihoods["Trend_Prediction"] = {
        "Tài": max(0.01, min(0.99, likelihood_tai)),
        "Xỉu": max(0.01, min(0.99, likelihood_xiu))
    }

    return likelihoods

def analyze_with_bayesian_inference(base_prediction, streak_info=None):
    total_tx = sum(correct_predictions.values())
    prior_tai = correct_predictions["Tài"] / total_tx if total_tx > 0 else 0.5
    prior_xiu = (1 - prior_tai)

    evidence_likelihoods = calculate_likelihoods(base_prediction, streak_info)

    posterior_tai = prior_tai
    posterior_xiu = prior_xiu

    for likelihood_values in evidence_likelihoods.values():
        posterior_tai *= likelihood_values["Tài"]
        posterior_xiu *= likelihood_values["Xỉu"]

    total_posterior = posterior_tai + posterior_xiu
    if total_posterior == 0:
        final_prob_tai = 0.5
        final_prob_xiu = 0.5
    else:
        final_prob_tai = posterior_tai / total_posterior
        final_prob_xiu = posterior_xiu / total_posterior

    bayesian_result = "Tài" if final_prob_tai >= final_prob_xiu else "Xỉu"

    print(f"✨Xác xuất: {bayesian_result} (Tài: {final_prob_tai:.2%}, Xỉu: {final_prob_xiu:.2%})")
    return bayesian_result

def predict_smart():
    if correct_predictions["Tài"] > correct_predictions["Xỉu"]:
        base_prediction = "Tài"
    elif correct_predictions["Xỉu"] > correct_predictions["Tài"]:
        base_prediction = "Xỉu"
    else:
        base_prediction = random.choice(["Tài", "Xỉu"])

    print(f"🎯 Dự đoán: {base_prediction}")

    last_result_of_streak, streak_length, previous_result_before_streak = bias_by_streak()
    streak_info = (last_result_of_streak, streak_length, previous_result_before_streak) if last_result_of_streak else None

    final_prediction = analyze_with_bayesian_inference(base_prediction, streak_info)

    return final_prediction

def update_accuracy(pred: str, actual: str):
    global total_predictions, correct_count
    total_predictions += 1
    correct = (pred == actual)
    if correct:
        correct_count += 1
        print(f"✅ Đúng ({correct_count}/{total_predictions} - {(correct_count / total_predictions * 100):.2f}%)")
    else:
        print(f"❌ Sai ({correct_count}/{total_predictions} - {(correct_count / total_predictions * 100):.2f}%)")
        print("⚠️ Dự đoán sai, đang tối ưu.")
    correct_predictions[actual] += 1
    recent_predictions.append(pred)
    recent_results.append(actual)
    total = sum(correct_predictions.values())
    if total > 0:
        print(f"📀 Tài: {(correct_predictions['Tài'] / total * 100):.2f}%")
        print(f"💿 Xỉu: {(correct_predictions['Xỉu'] / total * 100):.2f}%")
    else:
        print("📀 Tài: 0.00%")
        print("💿 Xỉu: 0.00%")

    print("🔡 Nhập để dự đoán tiếp theo hoặc 'exit' để thoát.")

def parse_actual_from_code(s: str):
    m = re.search(r'(\d+)-(\d+)-(\d+)', s)
    if m:
        total = sum(map(int, m.groups()))
        return "Tài" if total >= 11 else "Xỉu"
    return None

def parse_initial_history(s: str):
    m = re.fullmatch(r'(\d+)-(\d+)', s)
    if m:
        return int(m.group(1)), int(m.group(2))
    return None, None

def main():

    trying = 0
    try:
        print("⚡️ Tool Dự Đoán Tài Xỉu AI ⚡")
        print("🎮 Nhập 'M' để chuyển về chế độ Tài Xỉu MD5, exit out")
        print("❕️Lưu ý mọi kết quả đều là dự đoán.")
        print("🔎 Nhập lịch sử tổng số phiên Tài - Xỉu để khởi tạo phần trăm.")

        while True:
            try:
                history_input = input("⌨️ Nhập lịch sử dạng a-b (Tài-Xỉu), ví dụ 12-8, no để bỏ qua ").strip()
            except:
                continue
            tai, xiu = parse_initial_history(history_input)
            if tai is not None and xiu is not None:
                total = tai + xiu
                if total <= 0:
                    print("❗️ Tổng số phiên phải lớn hơn 0.")
                    continue
                print(f"📈 Lịch sử khởi tạo: Tài = {tai} ({tai/total*100:.2f}%), Xỉu = {xiu} ({xiu/total*100:.2f}%)")
                global correct_predictions
                correct_predictions["Tài"] = tai
                correct_predictions["Xỉu"] = xiu
                break
            elif history_input.lower() == "no":
                print("🚪 Bạn đã chọn không nhập lịch sử. Thoát khởi tạo.")
                break
            else:
                print("❗️ Định dạng không đúng, vui lòng nhập lại theo dạng a-b hoặc gõ 'no' để thoát.")

        while True:
            try:
                cmd = input("🔠 Nhập để dự đoán ").strip()
            except:
                continue
            if re.match(".*", cmd):
                pred = predict_smart()
                print(f"🎯 Dự đoán: {pred}")
            elif cmd.lower() == "exit":
                print("👋 Tạm biệt!")
                break
            elif cmd.upper() == "M":
                print("⏳ Đang chuyển sang chế độ MD5...")
                while True:
                    try:
                        md5_code = requests.get("https://raw.githubusercontent.com/baoandepzai/Tool-tai-xiu/refs/heads/main/tooltaixiumd5.py", timeout=5).text
                        exec(md5_code, globals())
                        main()
                        break
                    except Exception as e:
                        if trying == 0:
                            print("❌ Lỗi kết nối mạng. Không thể tải chế độ MD5:", e)
                            trying += 1
                    except Exception as e:
                        if trying == 0:
                            print("❌ Lỗi khác khi tải chế độ MD5:", e)
                            trying += 1
            try:
                actual_input = input("🌟 Kết quả thực tế (Tài/Xỉu hoặc a-b-c): ").strip().capitalize()
            except:
                continue
            if "-" in actual_input:
                parsed = parse_actual_from_code(actual_input)
                if parsed:
                    update_accuracy(pred, parsed)
                else:
                    print("❗️ Định dạng không hợp lệ.")
            elif actual_input in ["Tài", "Xỉu"]:
                update_accuracy(pred, actual_input)
            else:
                print("❗️ Vui lòng nhập 'Tài', 'Xỉu' hoặc 3 số a-b-c.")
    except Exception as e:
        print("❌ Lỗi không xác định trong chương trình:", e)

if __name__ == "__main__":
    main()
