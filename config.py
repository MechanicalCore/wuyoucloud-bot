import json

# 加载配置文件
def load_config():
    with open("config.json", "r") as config_file:
        config = json.load(config_file)
    # 解析群组和管理员ID列表
    config["notification_group_ids"] = config["notification_group_ids"].split(",")
    config["admin_user_ids"] = config["admin_user_ids"].split(",")
    return config
