from datetime import datetime
import re

# 转义特殊字符
def escape_markdown_v2(text):
    return re.sub(r'([_*\[\]()~`>#+\-=|{}.!])', r'\\\1', text)

# 格式化库存信息
def format_inventory_message(inventory_data):
    formatted_message = "📦✨ 当前库存信息 ✨📦\n\n"
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    for item in inventory_data:
        flag_emoji = "🇺🇸" if "US" in item["name"] else "🇨🇳"  # 根据商品名称决定国旗
        link_text = escape_markdown_v2(item["name"])
        url = escape_markdown_v2(item["url"])
        stock = escape_markdown_v2(str(item["stock"]))
        formatted_message += f"{flag_emoji} 商品: *{link_text}* 🔗 [点击下单]({url})\n✅ 库存: {stock}\n⏰ 更新时间: {escape_markdown_v2(current_time)}\n\n"
    return formatted_message

# 格式化任务提交成功通知
def format_task_submitted():
    return "✅ 任务已成功提交！请耐心等待，库存信息即将更新… 😊"

# 格式化任务在队列中通知
def format_task_in_queue():
    return "⏳ 前方已有相同任务在执行，无法重复提交哦！请稍等片刻 🙏"

# 库存变动检测或整点通知被阻塞的通知
def format_inventory_blocked_notification(task_name):
    return f"🚧 {escape_markdown_v2(task_name)} 任务受阻，当前有其他任务在进行中。请稍候，稍后会自动重试 ⏳"

# 格式化新增库存通知
def format_release_notification(new_releases):
    formatted_message = "🎉 新库存已释放！🎉\n\n"
    for item in new_releases:
        flag_emoji = "🇺🇸" if "US" in item["name"] else "🇨🇳"  # 根据商品名加入国旗
        link_text = escape_markdown_v2(item["name"])
        url = escape_markdown_v2(item["url"])
        stock = escape_markdown_v2(str(item["stock"]))
        formatted_message += f"{flag_emoji} 商品: *{link_text}* 🔗 [点击下单]({url})\n✅ 库存: {stock}\n\n"
    formatted_message += "💨 快速下单，库存有限！"
    return formatted_message

# 格式化售罄通知
def format_sold_out_notification(sold_out_items):
    formatted_message = "❌ 已售罄商品 ❌\n\n"
    for item in sold_out_items:
        flag_emoji = "🇺🇸" if "US" in item["name"] else "🇨🇳"
        link_text = escape_markdown_v2(item["name"])
        url = escape_markdown_v2(item["url"])
        formatted_message += f"{flag_emoji} 商品: *{link_text}* 已售罄 🔗 [查看页面]({url})\n\n"
    formatted_message += "📢 持续关注库存更新！"
    return formatted_message

# 通知：任务错误通知给用户
def format_error_notification():
    return "⚠️ 任务执行失败，暂时无法获取库存信息。请稍后再试或联系管理员！🙇‍♂️"

# 通知：管理员任务错误
def format_admin_error_notification(task_name, error):
    return f"🚨 {escape_markdown_v2(task_name)} 任务执行错误！\n错误信息: {escape_markdown_v2(error)}\n请尽快处理。"
