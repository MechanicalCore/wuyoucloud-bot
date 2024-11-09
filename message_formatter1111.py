from datetime import datetime
import re

# 转义特殊字符
def escape_markdown_v2(text):
    return re.sub(r'([_*\[\]()~`>#+\-=|{}.!])', r'\\\1', text)


# 通知：库存信息
def format_inventory_message(inventory_data):
    formatted_message = "📦✨ 叮~~当前库存信息 ✨📦\n\n"
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    for item in inventory_data:
        link_text, url = item.split('，')[-2], item.split('，')[-1]
        link_text = escape_markdown_v2(link_text)
        url = escape_markdown_v2(url)
        formatted_message += f"🛒 小鸡: *{link_text}* 🔗 [点击直达下单页面]({url})\n"
        formatted_message += f"⏰ 时间: {escape_markdown_v2(current_time)}\n\n"
    formatted_message += "🔗 更多信息请访问我们的[官网](https://wuyoucloud.club/) 🌐"
    return formatted_message

# 通知：任务已提交
def format_task_submitted():
    return "✅ 小主的任务已成功提交！劳烦小主耐心等待哦~ 😊"

# 通知：任务在队列中
def format_task_in_queue():
    return "⏳ 前方已有相同任务在执行，小主无法重复提交哦！劳烦小主稍等片刻 🙏"

# 通知：库存变动检测或整点通知被阻塞
def format_inventory_blocked_notification(task_name):
    return f"🚧 {escape_markdown_v2(task_name)} 哎呀！(ｷ｀ﾟДﾟ´)!!定时通知任务受阻了呜呜呜┭┮﹏┭┮当前有其他任务在进行中。哼╭(╯^╰)╮，我会在再次重试的 ⏳"

# 通知：释放库存
def format_release_notification(new_releases):
    formatted_message = "🎉 叮~~新库存已释放！🎉\n\n"
    for item in new_releases:
        link_text, url = item.split('，')[-2], item.split('，')[-1]
        link_text = escape_markdown_v2(link_text)
        url = escape_markdown_v2(url)
        formatted_message += f"🆕 小鸡: *{link_text}* 🔗 [点击直达下单页面]({url})\n"
    formatted_message += "\n💨 有需要的小主加快手速下单！库存有限哦~~O(∩_∩)O"
    return formatted_message

# 通知：小鸡售零
def format_sold_out_notification(sold_out_items):
    formatted_message = "❌ 叮~~售罄通知 ❌\n\n"
    for item in sold_out_items:
        link_text, url = item.split('，')[-2], item.split('，')[-1]
        link_text = escape_markdown_v2(link_text)
        url = escape_markdown_v2(url)
        formatted_message += f"💔 小鸡: *{link_text}* 已售罄 🔗 [点击查看页面]({url})\n"
    formatted_message += "\n📢 请各位小主继续关注我们，我们会随时更新库存的O(∩_∩)O "
    return formatted_message

# 通知：任务错误通知给用户
def format_error_notification():
    return "⚠️ 哎呀！(ｷ｀ﾟДﾟ´)!! 任务执行失败了，暂时无法获取库存信息。劳烦小主请稍后再试或联系我的主人！🙇‍♂️"

# 通知：管理员任务错误
def format_admin_error_notification(task_name, error):
    return f"🚨哎呀！(ｷ｀ﾟДﾟ´)!!  {escape_markdown_v2(task_name)} 任务执行错误！\n错误信息: {escape_markdown_v2(error)}\n 劳烦小主请稍后再试或告知联系我的主人！🙇‍♂️"
