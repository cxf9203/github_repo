# -- coding: utf-8 --
import socket
import time


def run_client():
    # ================= 配置 =================
    SERVER_IP = "192.168.1.3"   # 👉 如果服务器在其他电脑，改成对应IP
    SERVER_PORT = 8005

    # ================= 创建客户端 =================
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        print("正在连接服务器...")
        client.connect((SERVER_IP, SERVER_PORT))
        print("连接成功！")

        while True:
           
            # ================= 发送请求 =================
            msg = "pic"
            print(f"发送: {msg}")
            client.send(msg.encode())

            # ================= 接收结果 =================
            data = client.recv(1024)
            if not data:
                print("服务器断开连接")
                break

            result = data.decode()
            print(f"收到结果: {result}")

            # ================= 业务逻辑 =================
            if result == "red":
                print("👉 检测结果：红色（OK）")
            elif result == "not":
                print("👉 检测结果：非红色（NG）")
            elif result == "none":
                print("👉 当前没有图像")
            else:
                print("👉 未知返回:", result)

            # ================= 控制频率 =================
            time.sleep(3)   # 每3秒请求一次（可调）

    except ConnectionRefusedError:
        print("❌ 无法连接服务器，请检查IP和端口")
    except Exception as e:
        print("❌ 异常:", str(e))
    finally:
        client.close()
        print("连接关闭")


if __name__ == "__main__":
    run_client()